from utils.mt5_interface import (
    get_ohlc_data,
    get_account_info,
    get_open_position,
    get_symbol_info
)
from trading.entry_manager import RiskManager, handle_entry
from trading.risk_manager import RiskManager
from trading.position_monitor import monitor_positions
from patterns.pattern_atm import ATMDetector
from patterns.pattern_mob import MOBDetector
from stats.pattern_stats_logger import PatternStatsLogger
from ai.ai_report_generator import AIReportGenerator

def uruchom_analyze_etapu(symbol: str, timeframe: str, point: float, data_points: int = 300, risk_mode: str = "percent"):
    print(f"[START] Analiza {symbol} / {timeframe}")
    """
    Główna funkcja workflow – wykonuje analizę patternów i otwiera pozycję.
    Może być wywoływana cyklicznie przez harmonogram.
    """
    candles = get_ohlc_data(symbol, timeframe, data_points)
    if candles is None or candles.empty:
        print(f"[DATA] Brak danych dla {symbol} / {timeframe}")
        return

    account_info = get_account_info()
    if account_info is None:
        print("[ERROR] Brak danych konta")
        return
    balance = account_info["balance"]

    symbol_info = get_symbol_info(symbol)
    if symbol_info is None:
        print(f"[ERROR] Brak informacji o symbolu {symbol}")
        return

    #Wykrycie patternów
    atm = ATMDetector(symbol, point)
    mob = MOBDetector(symbol, point)

    atm_signal = atm.detect(candles)
    mob_signal = mob.detect(candles)

    entry = atm_signal or mob_signal
    if not entry:
        print(f"[PATTERN] Brak sygnału ATM/MOB dla {symbol} / {timeframe}")
        return

    print(f"[PATTERN] Wykryto: {entry['pattern']} | Symbol: {symbol} | TF: {timeframe}")

    #Sprawdzenie ryzyka
    risk_manager = RiskManager(risk_mode=risk_mode)
    open_positions = get_open_position(symbol)
    total_risk_usd = risk_manager.oblicz_total_risk(open_positions)
    max_risk_usd = balance * 0.03

    if total_risk_usd >= max_risk_usd:
        print(f"[RISK] Limit ryzyka przekroczony: {total_risk_usd:.2f} / {max_risk_usd:.2f} USD – pomijam wejście.")
        return

    handle_entry(
        signal=entry,
        symbol=symbol,
        balance=balance,
        risk_percent=3.0,
        risk_mode=risk_mode
    )

    #Logowanie
    csv_path = f"data/pattern_stats_{symbol}_{timeframe}.csv"
    json_path = f"data/pattern_stats_{symbol}_{timeframe}.json"
    raport_output_dir = "data/raporty_ai"

    logger = PatternStatsLogger(csv_path=csv_path, json_path=json_path)
    logger.log(entry, timeframe)

    ai = AIReportGenerator(
        stats_path_csv=csv_path,
        stats_path_json=json_path,
        output_dir=raport_output_dir,
        model=None
    )

    ai.generuj_raport()

    monitor_positions()

    print(f"[DONE] Zakończono analizę {symbol} / {timeframe}")