from ai.ai_report_generator import AIReportGenerator

def main():
    #Względne ścieżki do danych testowych
    stats_csv_path = "./data/synthetic_stats.csv"
    stats_json_path = "./data/synthetic_stats.json"
    raport_output_dir = "./data/ai_reports"

    # Inicjalizacja bez modelu AI (tryb offline – statystyki tylko jako tekst)
    ai = AIReportGenerator(
        stats_path_csv=stats_csv_path,
        stats_path_json=stats_json_path,
        output_dir=raport_output_dir,
        model=None #lub np. model = gpt4o jeśli kiedyś podłączysz API
    )

    #Generowanie raportu
    ai.generuj_raport()
    print("[INFO] Raport AI został wygenerowany i zapisany w katalogu:", raport_output_dir)

if __name__ == "__main__":
    main()