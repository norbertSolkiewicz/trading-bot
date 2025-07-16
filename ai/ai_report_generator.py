import json
import os
import pandas as pd
from datetime import datetime
from typing import Optional


class AIReportGenerator:
    def __init__(self,
                 stats_path_csv: str,
                 stats_path_json: str,
                 output_dir: str,
                 model: Optional[object] = None,
                 symbol: Optional[str] = None,
                 timeframe: Optional[str] = None
        ):
        self.stats_path_csv = stats_path_csv
        self.stats_path_json = stats_path_json
        self.output_dir = output_dir
        self.model = model  # Placeholder na przyszłość (np. GPT)
        self.symbol = symbol
        self.timeframe = timeframe

        os.makedirs(self.output_dir, exist_ok=True)

    def _filtruj_dane(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filtrowanie danych po symbolu i interwale, jeśli podano."""
        if self.symbol:
            df = df[df["symbol"] == self.symbol]
        if self.timeframe:
            df = df[df["timeframe"] == self.timeframe]
        return df

    def _stworz_nazwe_pliku(self, extension: str = "json") -> str:
        """Generuje nazwę pliku raportu na podstawie symbolu i interwału."""
        sym = self.symbol if self.symbol else "ALL"
        tf = self.timeframe if self.timeframe else "ALL"
        filename = f"raport_{sym}_{tf}.{extension}"
        return os.path.join(self.output_dir, filename)

    def generuj_raport(self):
        """Generuje raport AI na podstawie statystyk."""
        try:
            df = pd.read_csv(self.stats_path_csv)
        except Exception as e:
            print(f"[AI REPORT] Błąd wczytywania danych CSV: {e}")
            return

        df = self._filtruj_dane(df)
        if df.empty:
            print(f"[AI REPORT] Brak danych dla symbol={self.symbol} i timeframe={self.timeframe}")
            return

        raport = {
            "symbol": self.symbol or "ALL",
            "timeframe": self.timeframe or "ALL",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "liczba_sygnalow": len(df),
            "patterny": df["pattern"].value_counts().to_dict(),
            "sredni_zysk_usd": round(df["zysk_usd"].mean(), 2),
            "sredni_rr": round(df["rr"].mean(), 2),
            "trafnosc_%": round((df["zysk_usd"] > 0).sum() / len(df) * 100, 2),
        }

        output_path = self._stworz_nazwe_pliku("json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(raport, f, indent=4, ensure_ascii=False)

        print(f"[AI REPORT] Zapisano raport: {output_path}")