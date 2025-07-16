import os
import pandas as pd

def wczytaj_dane_z_csv(symbol: str, interwal: str, ostatnie: int = 300) -> pd.DataFrame:
    """
    Wczytuje dane świecowe z pliku CSV dla danego symbolu i interwału.

    :param symbol: np. "EURUSD.ecn"
    :param interwal: np. "M15", "H1", "D1"
    :param ostatnie: liczba ostatnich świec do zwrócenia
    :return: DataFrame z danymi lub pusty DataFrame jeśli brak danych
    """
    folder = f"data/history/{symbol}"
    filename = f"{interwal}.csv"
    path = os.path.join(folder, filename)

    if not os.path.exists(path):
        print(f"[DATA] Brak pliku: {path}")
        return pd.DataFrame()

    df = pd.read_csv(path)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)
    return df.tail(ostatnie)