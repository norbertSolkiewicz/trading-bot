import MetaTrader5 as mt5
import json
import os
from utils.logger import log_trade
from utils.mt5_interface import get_open_position, close_position
from  stats.pattern_stats_logger import PatternStatsLogger


def monitor_positions():
    """
    Monitoruje wszystkie otwarte pozycje na koncie MT5 i automatycznie zamyka je,
    jeśli aktualna cena osiągnie poziom Take Profit (TP) lub Stop Loss (SL).

    Obsługuje long i short, sprawdza TP i SL, zamyka pozycję zgodnie z logiką MT5.
    Wbudowane logowanie zamkniętych pozycji w formacie JSON/CSV za pomocą PatternStatsLogger.
    W przyszłości można rozszerzyć o trailing stop i AI-based closure.
    """
    memory_path = "data/pattern_memory.json"
    if not os.path.exists(memory_path):
        log_trade("[MONITOR] Brak pliku pamięci patternów.")
        return

    with open(memory_path, "r") as f:
        pattern_memory = json.load(f)

    if not pattern_memory:
        log_trade("[MONITOR] Brak aktywnych patternów w pamięci.")
        return

    # Pobierz wszystkie otwarte pozycje
    open_position = get_open_position()

    #Inicjalizuj logger
    logger = PatternStatsLogger()

    for pos in open_position:
        symbol = pos["symbol"]
        open_price = pos["price_open"]
        ticket = str(pos["ticket"])

        # Dopasuj z pamięci po symbolu i numerze ticketu
        matching_entry = None
        for pattern in pattern_memory.values():
            if (
                pattern["symbol"] == symbol and
                str(pattern["ticket"]) == ticket
            ):
                matching_entry = pattern
                break

        if not matching_entry:
            continue

        direction = matching_entry["direction"]
        tp_distance = matching_entry["tp_distance"]
        sl_price = matching_entry["sl_price"]
        entry_price = matching_entry["entry_price"]
        timeframe = matching_entry.get("timeframe", "UNKNOWN")

        current_price = pos['price_current']
        profit = pos['profit']

        #Oblicz pipsy i RR
        pips = abs(current_price - entry_price)
        rr = abs(current_price - entry_price) / (abs(sl_price - entry_price) + 1e-6)

        # Sprawdzenie TP
        if (
                direction == "buy" and current_price >= entry_price + tp_distance
        ) or (
                direction == "sell" and current_price <= entry_price - tp_distance
        ):
            close_position(pos)
            log_trade(f"[TP HIT] Zamknięto pozycję {ticket} z zyskiem.")
            logger.log({
                "symbol": symbol,
                "timeframe": timeframe,
                "entry_time": matching_entry["entry_time"],
                "exit_time": pos['time'],  # zakładamy, że MT5 zwraca czas
                "entry_price": entry_price,
                "exit_price": current_price,
                "direction": direction,
                "pattern": matching_entry["pattern"],
                "result": "TP",
                "profit_usd": round(profit, 2),
                "pips": round(pips, 2),
                "rr": round(rr, 2)
            })
            continue

        # Sprawdzenie SL
        if (
                direction == "buy" and current_price <= sl_price
        ) or (
                direction == "sell" and current_price >= sl_price
        ):
            close_position(pos)
            log_trade(f"[SL HIT] Zamknięto pozycję {ticket} ze stratą.")
            logger.log({
                "symbol": symbol,
                "timeframe": timeframe,
                "entry_time": matching_entry["entry_time"],
                "exit_time": pos['time'],
                "entry_price": entry_price,
                "exit_price": current_price,
                "direction": direction,
                "pattern": matching_entry["pattern"],
                "result": "SL",
                "profit_usd": round(profit, 2),
                "pips": round(pips, 2),
                "rr": round(rr, 2)
            })
            continue

    log_trade("[MONITOR] Monitoring pozycji zakończony.")
