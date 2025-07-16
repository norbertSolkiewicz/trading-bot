import json
import os
from typing import Dict, Any


class PatternMemory:
    def __init__(self, file_path: str = "data/pattern_memory.json"):
        self.file_path = file_path
        self.memory: Dict[str, Any] = self._wczytaj_z_pliku()

    def _wczytaj_z_pliku(self) -> Dict[str, Any]:
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _zapisz_do_pliku(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)

    def czy_juz_istnieje(self, symbol: str, timeframe: str, ticket: str) -> bool:
        """
        Sprawdza, czy pattern o danym kluczu już istnieje w pamięci.
        Klucz: "symbol_timeframe_ticket"
        """
        klucz = f"{symbol}_{timeframe}_{ticket}"
        return klucz in self.memory

    def zapisz_pattern(self, symbol: str, timeframe: str, ticket: str, dane: Dict[str, Any]) -> None:
        """
        Zapisuje nowy pattern do pamięci z kluczem symbol_timeframe_ticket
        """
        klucz = f"{symbol}_{timeframe}_{ticket}"
        self.memory[klucz] = dane
        self._zapisz_do_pliku()

    def usun_pattern(self, symbol: str, timeframe: str, ticket: str) -> None:
        klucz = f"{symbol}_{timeframe}_{ticket}"
        if klucz in self.memory:
            del self.memory[klucz]
            self._zapisz_do_pliku()

    def pobierz_pattern(self, symbol: str, timeframe: str, ticket: str) -> Dict[str, Any]:
        klucz = f"{symbol}_{timeframe}_{ticket}"
        return self.memory.get(klucz, {})

    def wyczysc_pamiec(self) -> None:
        """Czyści całą pamięć patternów"""
        self.memory = {}
        self._zapisz_do_pliku()