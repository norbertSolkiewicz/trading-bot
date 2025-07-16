from apscheduler.schedulers.background import BackgroundScheduler
import time
import MetaTrader5 as mt5

from core.workflow import uruchom_analyze_etapu
from utils.logger import log_trade
from utils.mt5_interface import initialize_mt5, shutdown_mt5


# ✅ Konfiguracja: jakie symbole i interwały obsługujemy
symbol_tf_config = {
    "EURUSD.ecn": ["M15", "H1"],
    "GBPUSD.ecn": ["M15"],
    "USDJPY.ecn": ["H1", "D1"]
}

# ✅ Mapowanie interwałów na cron (co ile minut ma się uruchamiać)
timeframe_cron_map = {
    "M15": "*/15 * * * *",
    "H1": "0 * * * *",
    "D1": "0 9 * * *"  # codziennie o 09:00
}

# Parametry globalne
point = 0.0001 # Przykładowo dla EURUSD
# ✅ Czy uruchamiamy w trybie DRY-RUN (testowym, bez pozycji)
dry_run_mode = True

logger = log_trade("main_scheduler")



def zaplanuj_zadania():
    scheduler = BackgroundScheduler()

    for symbol, timeframes in symbol_tf_config.items():
        for tf in timeframes:
            cron = timeframe_cron_map.get(tf)
            if not cron:
                logger.warning(f"[SKIP] Nieobsługiwany timeframe {tf} dla {symbol}")
                continue

            scheduler.add_job(
                uruchom_analyze_etapu,
                trigger='cron',
                args=[symbol, tf, point, dry_run_mode],
                id=f"{symbol}_{tf}",
                name=f"Analyze {symbol} {tf}",
                **_cron_string_to_kwargs(cron)
            )
            logger.info(f"[SCHEDULE] Zadanie dodane: {symbol} {tf} ({cron})")

    scheduler.start()
    logger.info("[START] Harmonogram APScheduler uruchomiony")


def _cron_string_to_kwargs(cron_str: str) -> dict:
    """Pomocnicza funkcja do konwersji cron stringa na kwargs"""
    fields = cron_str.strip().split()
    return {
        "minute": fields[0],
        "hour": fields[1],
        "day": fields[2],
        "month": fields[3],
        "day_of_week": fields[4]
    }

def aktywuj_symbole(symbol_tf_config: dict):
    """
    Aktywuje wszystkie symbole z konfiguracji symbol_tf_config w Market Watch MT5.
    """
    for symbol in symbol_tf_config.keys():
        if not mt5.symbol_select(symbol, True):
            print(f"[WARNING] Nie udało się aktywować symbolu: {symbol}")
        else:
            print(f"[INIT] Symbol {symbol} został aktywowany w Market Watch.")


if __name__ == "__main__":
    login = 125463824
    password = "H%N7hCyUPWqP"
    server = "TradeQuo-Server"
    if not initialize_mt5(login, password, server):
        logger.error("[ERROR] Nie udało się połączyć z MetaTrader 5.")
        exit()

    aktywuj_symbole(symbol_tf_config)

    zaplanuj_zadania()
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("[STOP] Zatrzymano harmonogram.")
        shutdown_mt5()