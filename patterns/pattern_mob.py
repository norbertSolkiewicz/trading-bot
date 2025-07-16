

import pandas as pd
from typing import Optional, Dict

class MOBDetector:
    def __init__(self, symbol: str, point: float):
        self.symbol = symbol
        self.point = point  # np. 0.0001 dla EURUSD

    def _calculate_fibo_level(self, start: float, end: float, level: float) -> float:
        """Oblicza poziom Fibo na podstawie poziomu procentowego"""
        diff = end - start
        return start + diff * (level / 100.0)

    def _measure_pips(self, price1: float, price2: float) -> float:
        """Zwraca odległość w pipsach"""
        return abs(price1 - price2) / self.point

    def _is_trend_up(self, df: pd.DataFrame) -> bool:
        """Prosty trend: wzrost ceny close"""
        return df['close'].iloc[-1] > df['close'].iloc[0]

    def detect(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Detekcja patternu MOB – jak ATM, ale drugi impuls jest mniejszy niż pierwszy.
        Zwraca sygnał wejścia lub None.
        """
        trend_up = self._is_trend_up(df)
        candles = df.reset_index(drop=True)

        for i in range(50, len(candles) - 10):
            # Impuls 1 (główny ruch)
            impulse1_start = candles.loc[i - 3, 'close']
            impulse1_end = candles.loc[i, 'close']
            impulse1_dir_up = impulse1_end > impulse1_start

            if impulse1_dir_up != trend_up:
                continue

            impulse1_pips = self._measure_pips(impulse1_start, impulse1_end)

            # Korekta 1
            correction1_start = impulse1_end
            correction1_end = candles.loc[i + 2, 'close']
            correction1_pips = self._measure_pips(correction1_start, correction1_end)

            fib_38 = self._calculate_fibo_level(impulse1_start, impulse1_end, 38.2)
            if correction1_pips < 100 or \
               (trend_up and correction1_end > fib_38) or \
               (not trend_up and correction1_end < fib_38):
                continue

            # Impuls 2 – musi być w tym samym kierunku, ale KRÓTSZY niż impuls 1
            impulse2_start = correction1_end
            impulse2_end = candles.loc[i + 4, 'close']
            impulse2_pips = self._measure_pips(impulse2_start, impulse2_end)

            if (trend_up and impulse2_end <= impulse2_start) or \
               (not trend_up and impulse2_end >= impulse2_start):
                continue  # nie kontynuuje trendu

            if impulse2_pips >= impulse1_pips:
                continue  # dla MOB: impuls 2 musi być mniejszy niż impuls 1

            # Korekta 2 – powrót do poziomu 100% Fibo z 1. korekty
            correction2_start = impulse2_end
            correction2_end = candles.loc[i + 6, 'close']
            correction2_pips = self._measure_pips(correction2_start, correction2_end)

            fib_100 = self._calculate_fibo_level(impulse1_start, impulse1_end, 100)

            if correction2_pips < 100:
                continue

            if (trend_up and correction2_end < fib_100) or \
               (not trend_up and correction2_end > fib_100):
                continue  # nie dotknięto poziomu 100% Fibo

            # ZNALEZIONO pattern MOB
            entry_price = fib_100
            sl_price = self._calculate_fibo_level(impulse1_start, impulse1_end, 141.4)
            tp_distance = correction1_pips * self.point * 0.15

            return {
                "symbol": self.symbol,
                "entry_time": candles.loc[i + 6, 'datetime'],
                "entry_price": round(entry_price, 5),
                "sl_price": round(sl_price, 5),
                "tp_distance": round(tp_distance, 5),
                "direction": "buy" if trend_up else "sell",
                "pattern": "MOB"
            }

        return None