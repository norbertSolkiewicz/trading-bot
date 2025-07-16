## [2025-06-21] Aktualizacja `main.py` (refaktoryzacja)

### Dodano:
- Zintegrowano `ATMDetector` i `MOBDetector` z `patterns/`
- Obliczanie ryzyka i lotów przy użyciu funkcji z `risk_manager.py`
- Zapis patternów do CSV i JSON przez `PatternStatsLogger`
- Generowanie raportów AI przez `AIReportGenerator`

### Zmieniono:
- Całkowicie usunięto nieuzgodnione funkcje (`get_open_positions`, stare klasy)
- Usunięto aliasy, skróty, stare nazwy plików – pełna zgodność z "Stanem Projektu"
- Zamiast logiki pomocniczej: czyste wywołania zatwierdzonych klas

### Usunięto:
- Wcześniejsze wersje `main.py` zawierające niezatwierdzone klasy i helpery

### Uzasadnienie:
- Utrzymanie pełnej spójności projektu z dokumentem 📁 Stan Projektu
- MVP jako test integracyjny przed wdrożeniem logiki otwierania pozycji