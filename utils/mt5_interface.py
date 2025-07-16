

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import pytz

def initialize_mt5(login: int, password: str, server: str, path: str= "") -> bool:
    if not mt5.initialize(path, login = login, password = password, server=server):
        print(f"[ERROR] MetaTrader5 init failed: {mt5.last_error()}")
        return False
    print("[INFO] MetaTrader5 initialized successfully")
    return True

def shutdown_mt5():
    mt5.shutdown()

TIMEFRAMES = {
    'M1': mt5.TIMEFRAME_M1,
    'M5': mt5.TIMEFRAME_M5,
    'M15': mt5.TIMEFRAME_M15,
    'H1': mt5.TIMEFRAME_H1,
    'D1': mt5.TIMEFRAME_D1
}

def get_ohlc_data(symbol: str, timeframe: str, num_bars: int = 500) -> pd.DataFrame:
    if timeframe not in TIMEFRAMES:
        raise ValueError(f"[ERROR] Nieobsługiwany interwał czasowy: {timeframe}")

    utc_tz = pytz.timezone('Etc/UTC')

    # [DEBUG] Próba pobrania danych OHLC
    print(f"[DEBUG] Pobieranie danych OHLC dla: symbol={symbol}, timeframe={timeframe}, num_bars={num_bars}")

    rates = mt5.copy_rates_from_pos(symbol, TIMEFRAMES[timeframe], 0, num_bars)

    #Jeśli brak danych - spróbuj aktywować symbol
    if rates is None or len(rates) == 0:
        print(f"[WARNING] Brak danych dla {symbol}. Próba aktywacji symbolu w Market Watch...")
        selected = mt5.symbol_select(symbol, True)
        if not selected:
            raise RuntimeError(f"[ERROR] Symbol {symbol} nie mógł zostać aktywowany w Market Watch.")

        # Retry po aktywacji
        rates = mt5.copy_rates_from_pos(symbol, TIMEFRAMES[timeframe], 0, num_bars)
        if rates is None or len(rates) == 0:
            raise RuntimeError(f"[ERROR] Po aktywacji nadal brak danych dla {symbol} ({timeframe}).")

    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Europe/Warsaw')
    df.rename(columns={
        'time': 'datetime',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'tick_volume': 'volume'
    }, inplace=True)

    print(f"[DEBUG] Pobrano {len(df)} rekordów dla {symbol} ({timeframe})")

    return df[['datetime', 'open', 'high', 'low', 'close', 'volume']]

def get_account_info():
    account = mt5.account_info()
    if account is None:
        raise RuntimeError("[ERROR] Nie udało się pobrać informacji o koncie")
    return {
        "balance": account.balance,
        "equity": account.equity,
        "margin": account.margin,
        "free_margin": account.margin_free,
        "currency": account.currency
    }

def get_symbol_info(symbol: str):
    info = mt5.symbol_info(symbol)
    if not info:
        raise RuntimeError(f"[ERROR] Brak informacji o symbolu: {symbol}")
    return {
        "min_lot": info.volume_min,
        "lot_step": info.volume_step,
        "tick_size": info.trade_tick_size,
        "point": info.point,
        "spread": info.spread * info.point
    }

def open_position(symbol: str, direction: str, price: float, sl: float, tp: float, volume: float, comment: str = "",
                      magic: int = 123456):
    """
   Otwiera pozycję na podstawie przekazanych parametrów.

   :param symbol: Symbol instrumentu (np. "EURUSD.ecn")
   :param direction: Kierunek pozycji ("buy" lub "sell")
   :param price: Cena wejścia
   :param sl: Stop loss
   :param tp: Take profit
   :param volume: Wielkość pozycji (loty)
   :param comment: Komentarz do pozycji (np. pattern)
   """
    order_type = mt5.ORDER_TYPE_BUY if direction == "buy" else mt5.ORDER_TYPE_SELL

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": magic,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[ERROR] Zlecenie nie powiodło się: {result.retcode}, {result.comment}")
    else:
        print(f"[INFO] Pozycja otwarta: ticket={result.order}, cena={price}, SL={sl}, TP={tp}")
    return result

def close_position(position_ticket: int):
    position = mt5.positions_get(tikcket=position_ticket)
    if not position or len(position) == 0:
        print(f"[ERROR] Nie znaleziono pozycji o tickerze {position_ticket}")
        return

    pos = position[0]
    order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": pos.symbol,
        "volume": pos.volume,
        "type": order_type,
        "position": position_ticket,
        "price": mt5.symbol_info_tick(pos.symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(
            pos.symbol).ask,
        "deviation": 20,
        "magic": pos.magic,
        "comment": "auto_close"
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[ERROR] Nie udało się zamknąć pozycji: {result.retcode}")
    else:
        print(f"[INFO] Pozycja zamknięta: ticket={position_ticket}")
    return result

def get_open_position(symbol: str = None):
    position = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
    result = []
    for pos in position:
        result.append({
            "ticket": pos.ticket,
            "symbol": pos.symbol,
            "type": "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL",
            "volume": pos.volume,
            "price_open": pos.price_open,
            "sl": pos.sl,
            "tp": pos.tp,
            "profit": pos.profit
        })

    return result