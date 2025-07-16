import csv
import json
import os
from typing import Dict, List

class PatternStatsLogger:
    def __init__(self, base_dir: str = "data/pattern_stats"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_file_paths(self, symbol: str, timeframe: str) -> tuple[str, str]:
        """
        Generuje unikalne ścieżki plików CSV i JSON dla danej pary symbol+timeframe.
        """
        base_name = f"{symbol.replace('.', '_')}_{timeframe}"
        csv_path = os.path.join(self.base_dir, f"{base_name}_stats.csv")
        json_path = os.path.join(self.base_dir, f"{base_name}_stats.json")
        return csv_path, json_path

    def log(self, entry: Dict, timeframe: str) -> None:
        """
        Zapisuje sygnał patternu do pliku CSV i JSON – osobno dla każdego symbolu i interwału.
        """

        symbol = entry.get("symbol")
        if not symbol or not timeframe:
            print("[LOGGER] Brak symbolu lub interwału – pomijam zapis statystyk.")
            return

        csv_path, json_path = self._get_file_paths(symbol, timeframe)

        row = {
            "datetime": str(entry.get("entry_time")),
            "symbol": symbol,
            "timeframe": timeframe,
            "pattern": entry.get("pattern"),
            "direction": entry.get("direction"),
            "entry_price": entry.get("entry_price"),
            "sl_price": entry.get("sl_price"),
            "tp_distance": entry.get("tp_distance"),
        }

        #CSV
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

        #JSON
        stats_data = []
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                try:
                    stats_data = json.load(f)
                except json.JSONDecodeError:
                    stats_data = []

        stats_data.append(row)

        with open(json_path, "w") as f:
            json.dump(stats_data, f, indent=4)

        print(f"[LOGGER] Zapisano statystyki dla {symbol} {timeframe}")