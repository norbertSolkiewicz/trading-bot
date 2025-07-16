

def generate_prompt(stats_file):
    return f"""
    Zanalizuj plik CSV zawierający statystyki transakcji patternów. Znajdź:
    - Najskuteczniejszy pattern (procent skuteczności)
    - Średni zysk w pipsach dla każdego patternu
    - Czy skuteczność zależy od interwału (M1, M5, H1...)
    - Czy pora dnia/tygodnia wpływa na wyniki
    Plik CSV znajduje się pod nazwą: {stats_file}
    """