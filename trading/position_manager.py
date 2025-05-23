import logging
from datetime import datetime
from config.trading_params import TradingParams


class PositionManager:
    def __init__(self):
        self.params = TradingParams()
        self.logger = logging.getLogger('position_manager')
        self.current_position = None
        self.entry_price = None
        self.entry_time = None

    def execute_signal(self, signal, current_price):
        """Sinyali işleme al"""
        try:
            if signal == 'buy' and self.current_position != 'long':
                self._open_long_position(current_price)
            elif signal == 'sell' and self.current_position != 'short':
                self._open_short_position(current_price)
            elif signal == 'hold':
                # Mevcut pozisyonu koru
                pass

        except Exception as e:
            self.logger.error(f"Sinyal işleme hatası: {e}")

    def _open_long_position(self, price):
        """Long pozisyon aç"""
        self._close_current_position(price)

        self.current_position = 'long'
        self.entry_price = price
        self.entry_time = datetime.now()

        self.logger.info(f"LONG pozisyon açıldı: {price:.4f}")

    def _open_short_position(self, price):
        """Short pozisyon aç"""
        self._close_current_position(price)

        self.current_position = 'short'
        self.entry_price = price
        self.entry_time = datetime.now()

        self.logger.info(f"SHORT pozisyon açıldı: {price:.4f}")

    def _close_current_position(self, current_price):
        """Mevcut pozisyonu kapat"""
        if self.current_position and self.entry_price:
            pnl = self._calculate_pnl(current_price)
            self.logger.info(f"{self.current_position.upper()} pozisyon kapatıldı. PnL: {pnl:.4f}")

        self.current_position = None
        self.entry_price = None
        self.entry_time = None

    def _calculate_pnl(self, current_price):
        """Kar/zarar hesapla"""
        if not self.entry_price:
            return 0

        if self.current_position == 'long':
            return current_price - self.entry_price
        elif self.current_position == 'short':
            return self.entry_price - current_price
        else:
            return 0

    def get_position_info(self):
        """Pozisyon bilgilerini döndür"""
        return {
            'position': self.current_position,
            'entry_price': self.entry_price,
            'entry_time': self.entry_time
        }