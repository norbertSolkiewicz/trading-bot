import MetaTrader5 as mt5


class RiskManager:
    """
    Klasa odpowiadająca za zarządzanie ryzykiem – oblicza wielkość pozycji
    na podstawie poziomu SL, salda konta i ustalonego procentu ryzyka.
    """
    def __init__(self, risk_mode: str= "percent"):
        self.risk_mode = risk_mode #Dostępne: percent, fixed_lot, max_usd

    def oblicz_wolumen(self, entry_price: float, sl_price: float, balance: float, symbol: str ,
                       risk_percent: float = 1.0, fixed_lot: float = 0.1, max_usd: float = 100.0) -> float:
        """
        Oblicza wolumen pozycji (lotów), tak aby maksymalna strata wynosiła określony procent salda konta.

        :param max_usd:
        :param symbol:
        :param fixed_lot:
        :param entry_price: Cena wejścia w pozycję
        :param sl_price: Cena Stop Loss
        :param balance: Saldo konta w USD
        :param risk_percent: Procent salda, które może zostać zaryzykowane (np. 1.0 = 1%)
        :return: Obliczony wolumen pozycji w lotach
        """
        if self.risk_mode == "percent":
            return self._wolumen_percent(balance, entry_price, sl_price, symbol, risk_percent)
        elif self.risk_mode == "fixed_lot":
            return fixed_lot
        elif self.risk_mode == "max_usd":
            return self._wolumen_max_usd(entry_price, sl_price, symbol, max_usd)
        else:
            raise ValueError(f"Nieobsługiwany tryb ryzyka: {self.risk_mode}")



    def _get_symbol_data(self, entry_price: float, sl_price: float, symbol: str):
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None or not symbol_info.trade_contract_size:
            print(f"[RISK] Brak informacji o symbolu {symbol}, domyślny wolumen 0.1")
            return None, None, None, 0.1

        contract_size = symbol_info.trade_contract_size
        point = symbol_info.point
        stop_loss_pips = abs(entry_price - sl_price) / point
        if stop_loss_pips == 0:
            return None, None, None, 0.1

        return contract_size, point, stop_loss_pips, None

    def _wolumen_percent(self, balance: float, entry_price: float, sl_price: float, symbol: str, risk_percent: float) -> float:
        contract_size, point, stop_loss_pips, fallback = self._get_symbol_data(entry_price, sl_price, symbol)
        if fallback is not None:
            return fallback

        risk_amount_usd = balance * (risk_percent / 100.0)
        lot_size = risk_amount_usd / (stop_loss_pips * contract_size * point)
        return round(lot_size, 2)

    def _wolumen_max_usd(self, entry_price: float, sl_price: float, symbol: str, max_usd: float) -> float:
        contract_size, point, stop_loss_pips, fallback = self._get_symbol_data(entry_price, sl_price, symbol)
        if fallback is not None:
            return fallback

        lot_size = max_usd / (stop_loss_pips * contract_size * point)
        return round(lot_size, 2)

    def oblicz_total_risk(self, positions: list[dict]) -> float:
        total_risk = 0.0
        for pos in positions:
            sl = pos.get("sl")
            entry = pos.get("price_open")
            volume = pos.get("volume")
            symbol = pos.get("symbol")

            if sl is None or entry is None or volume is None or symbol is None:
                continue

            contract_size, point, stop_loss_pips, fallback = self._get_symbol_data(entry, sl, symbol)
            if fallback is not None:
                continue

            risk_usd = stop_loss_pips * volume * contract_size * point
            total_risk += risk_usd

        return round(total_risk, 2)