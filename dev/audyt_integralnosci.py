import os

# Główne foldery projektu, które zawierają pliki kodu
KATALOGI_PROJEKTU = [
    "core",
    "data",
    "patterns",
    "trading",
    "utils"
]

# Pliki, które muszą istnieć i być odwzorowane w stanie projektu
PLIKI_WYMAGANE = {
    "core": ["workflow.py"],
    "data": ["ai_reports.py"],
    "patterns": ["pattern_atm.py", "pattern_mob.py"],
    "trading": ["entry_manager.py", "position_monitor.py", "risk_manager.py"],
    "utils": ["mt5_interface.py"]
}

# Pliki dokumentowane w stanie projektu (do ręcznego porównania)
PLIKI_W_STANIE_PROJEKTU = [
    "workflow.py",
    "ai_reports.py",
    "pattern_atm.py",
    "pattern_mob.py",
    "entry_manager.py",
    "position_monitor.py",
    "risk_manager.py",
    "mt5_interface.py"
]

def sprawdz_integralnosc():
    brakujace = []
    nieudokumentowane = []

    for folder, expected_files in PLIKI_WYMAGANE.items():
        folder_path = os.path.join(os.getcwd(), folder)
        if not os.path.isdir(folder_path):
            print(f"[ERROR] Folder nie istnieje: {folder}")
            continue

        aktualne = os.listdir(folder_path)
        for plik in expected_files:
            if plik not in aktualne:
                brakujace.append(os.path.join(folder, plik))

    # Szukaj plików, które istnieją fizycznie, ale nie są opisane w stanie projektu
    wszystkie_plikikodu = []
    for folder in KATALOGI_PROJEKTU:
        sciezka_folderu = os.path.join(os.getcwd(), folder)
        if os.path.isdir(sciezka_folderu):
            wszystkie_plikikodu += [f for f in os.listdir(sciezka_folderu) if f.endswith(".py")]

    for plik in wszystkie_plikikodu:
        if plik not in PLIKI_W_STANIE_PROJEKTU:
            nieudokumentowane.append(plik)

    # Raport
    if not brakujace and not nieudokumentowane:
        print("✅ Wszystko spójne ze stanem projektu.")
    else:
        print("🔍 WYKRYTO NIEZGODNOŚCI:")
        if brakujace:
            print("❌ Brakujące pliki kodu:")
            for p in brakujace:
                print(f" - {p}")
        if nieudokumentowane:
            print("❗ Pliki istniejące, ale nieopisane w stanie projektu:")
            for p in nieudokumentowane:
                print(f" - {p}")

if __name__ == "__main__":
    sprawdz_integralnosc()