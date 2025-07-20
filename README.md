[README.md](https://github.com/user-attachments/files/21335562/README.md)# 📈 MT5 Automated Trading Bot

**Automatyczny bot tradingowy dla MetaTrader 5**, który analizuje rynek na wielu symbolach i interwałach, wykrywa predefiniowane patterny (ATM, MOB), zarządza ryzykiem, monitoruje pozycje oraz generuje raporty AI o skuteczności.

---

## ✅ Funkcjonalności Bota

1. **Wykrywanie patternów**:

   * Patterny: ATM (Cash Machine), MOB (Make Or Break).
   * Analiza na wielu symbolach i interwałach.
   * Schodzenie na niższe interwały jeśli pattern nie został znaleziony na wyższych.

2. **Obsługa trendu głównego**:

   * Wykrywanie trendu na najwyższym interwale.
   * Ograniczenie analizy do kierunku trendu.
   * Niższe interwały analizowane od ostatniego znalezionego patternu/overbalancu.

3. **Zarządzanie ryzykiem**:

   * Tryby: `percent`, `fixed_lot`, `max_usd`.
   * Dynamiczne zarządzanie wolumenem pozycji.
   * Obliczanie łącznego ryzyka na otwartych pozycjach.

4. **Monitorowanie pozycji**:

   * Automatyczne zamykanie po osiągnięciu TP/SL.
   * Logowanie zamknięcia pozycji z pełnymi statystykami.
   * Obliczenia pipsów, USD, RR i zysku.

5. **Raporty AI**:

   * Automatyczne generowanie raportów AI na podstawie historii transakcji.
   * Skuteczność patternów, RR, pipsów, częstotliwości.
   * Raporty per symbol, timeframe oraz globalne.

6. **Scheduler**:

   * Automatyczne wywoływanie analiz wg harmonogramu dla każdego symbolu i interwału.
   * Integracja z APScheduler.

7. **Tryb Dry-Run**:

   * Flaga `dry_run=True` umożliwia testowanie bota bez zawierania realnych transakcji.

---

## 📂 Struktura Katalogów

```
mt5_bot/
│
├── ai/                     # Generowanie raportów AI o skuteczności patternów
│    └── ai_report_generator.py
│
├── core/                   # Workflow - główne procesy analityczne
│    └── workflow.py
│
├── data/                   # Dane wygenerowane przez bota (raporty, pamięć patternów)
│    └── ai_reports.py
│
├── patterns/               # Detekcja patternów
│    ├── pattern_atm.py
│    └── pattern_mob.py
│
├── stats/                  # Logika i pliki statystyczne
│    └── pattern_stats_logger.py
│
├── trading/                # Obsługa pozycji, ryzyka
│    ├── entry_manager.py
│    ├── position_monitor.py
│    └── risk_manager.py
│
├── utils/                  # Narzędzia wspierające
│    ├── logger.py
│    ├── fibonacci.py
│    ├── mt5_interface.py
│    ├── pattern_memory.py
│    ├── data_loader.py
│    └── market_initializer.py
│
├── dev/                    # Narzędzia developerskie
│    └── audyt_integralnosci.py
│
├── main.py                 # Główne wejście programu - harmonogram analiz
│
├── requirements.txt        # Lista zależności
└── README.md               # Dokumentacja projektu
```

---

## 🚀 Zasady Rozwoju i Deployu

1. **Zasady rozwoju**

   * Trzymamy się architektury projektu określonej w pliku `📁 stan projektu`.
   * Nie zmieniamy nazw plików ani klas bez aktualizacji dokumentu projektu.
   * Każda funkcjonalność powinna być modularna i łatwa do testowania.
   * Każdy nowy komponent musi być w pełni zintegrowany z systemem logów.
   * Każdy commit powinien zawierać jasny opis zmian oraz wpływ na pozostałe komponenty.

2. **Deploy / Uruchomienie**

   * Wymagany MetaTrader 5 Desktop z poprawnie skonfigurowanym kontem.
   * Plik konfiguracyjny dla loginu, hasła, serwera w `main.py`.
   * Uruchomienie:

     ```
     python main.py
     ```
   * Obsługa harmonogramu przez APScheduler – proces działa w pętli, analizując rynek wg zaplanowanych interwałów.

3. **Środowisko**

   * Python 3.10+
   * Zależności określone w `requirements.txt`.
   * Rekomendowana praca na osobnym środowisku wirtualnym.

---

## 📌 Status

Projekt w wersji produkcyjnej **dla użytku własnego**. Wciąż możliwy dalszy rozwój w zakresie:

* Backtestingu,
* Trailing Stop,
* Dynamicznego dostosowania risk\_mode,
* Dashboardu wyników.

---

## 🤝 Autor

Projekt: Norbert (repozytorium prywatne).

