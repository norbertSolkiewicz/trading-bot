import json
import os
from trading.risk_manager import RiskManager
from utils.mt5_interface import open_position


def handle_entry(signal: dict, symbol: str, balance: float, risk_percent: float = 3.0,
                  risk_mode: str = "percent", dry_run: bool = False):
    """
    Obsługuje wejście w pozycję na podstawie sygnału patternu.

    :param signal: słownik zawierający dane patternu (entry_price, sl_price, tp_distance, direction itd.)
    :param symbol: symbol instrumentu (np. "EURUSD.ecn")
    :param balance: saldo konta w USD (pobrane wcześniej z mt5.account_info().balance)
    :param risk_percent: maksymalny procent ryzyka kapitału dla jednej pozycji
    :param risk_mode: tryb zarządzania ryzykiem ("percent", "fixed_lot", "max_usd")
    :param dry_run: jeżeli True, symuluje otwarcie pozycji bez rzeczywistego wykonania
    """
    if not signal or not signal.get("entry_price") or not signal.get("sl_price"):
        print("[WARNING] Brak danych wejściowych – pomijam entry.")
        return

    entry_price = signal["entry_price"]
    sl_price = signal["sl_price"]
    direction = signal["direction"]
    tp_distance = signal.get("tp_distance", 0.0)
    pattern_name = signal.get("pattern", "UNKNOWN")

    risk_manager = RiskManager(risk_mode=risk_mode)

    try:
        volume = risk_manager.oblicz_wolumen(
            entry_price=entry_price,
            sl_price=sl_price,
            balance=balance,
            symbol=symbol,
            risk_percent=risk_percent
        )
    except ValueError as e:
        print(f"[ERROR] Nie można obliczyć wolumenu: {e}")
        return

    tp_price = entry_price + tp_distance if direction == "buy" else entry_price - tp_distance

    if dry_run:
        print(f"[DRY-RUN] Wykryto sygnał {direction.upper()} na {symbol} – pozycja NIE została otwarta (tryb testowy).\n"
              f"Entry: {entry_price}, SL: {sl_price}, TP: {tp_price}, Volume: {volume}, Pattern: {pattern_name}")
        return

    # Otwórz pozycję z komentarzem zawierającym nazwę patternu
    result = open_position(
        symbol=symbol,
        direction=direction,
        price=entry_price,
        sl=sl_price,
        tp=tp_price,
        volume=volume,
        comment=f"pattern={pattern_name}"
    )

    # Zapisz dane patternu do pliku tymczasowego po otwarciu
    if result and hasattr(result, "order") and result.order > 0:
        pattern_memory_path = "data/pattern_memory.json"
        memory = {}

        if os.path.exists(pattern_memory_path):
            with open(pattern_memory_path, "r", encoding="utf-8") as f:
                try:
                    memory = json.load(f)
                except json.JSONDecodeError:
                    print("[WARNING] Błąd odczytu pattern_memory.json – tworzę nowy plik.")

        memory[str(result.order)] = signal

        with open(pattern_memory_path, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)

        print(f"[INFO] Zapisano dane patternu dla pozycji {result.order} do pattern_memory.json")