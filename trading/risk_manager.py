import logging
from config.trading_params import TradingParams


class RiskManager:
    def __init__(self):
        self.params = TradingParams()
        self.logger = logging.getLogger('risk_manager')
        self.last_positions = []  # Son pozisyonları takip et

    def apply_risk_controls(self, signal, features_df):
        """Risk kontrolleri uygula"""
        try:
            if signal == 'hold':
                return signal

            # Stop loss kontrolü
            controlled_signal = self._stop_loss_control(signal, features_df)

            # Pozisyon büyüklüğü kontrolü
            final_signal = self._position_size_control(controlled_signal, features_df)

            # Aşırı işlem kontrolü
            final_signal = self._overtrading_control(final_signal)

            return final_signal

        except Exception as e:
            self.logger.error(f"Risk kontrol hatası: {e}")
            return 'hold'

    def _stop_loss_control(self, signal, features_df):
        """Stop loss kontrolü"""
        try:
            # ATR bazlı stop loss
            if 'atr_14' in features_df.columns:
                atr = features_df['atr_14'].iloc[-1]
                current_price = features_df['close'].iloc[-1]

                # ATR'nin %200'ü kadar stop loss
                stop_distance = atr * 2
                stop_percentage = stop_distance / current_price

                if stop_percentage > self.params.STOP_LOSS_THRESHOLD:
                    self.logger.warning(f"Yüksek risk: {stop_percentage:.3f} > {self.params.STOP_LOSS_THRESHOLD}")
                    return 'hold'

            return signal

        except Exception as e:
            self.logger.error(f"Stop loss kontrol hatası: {e}")
            return signal

    def _position_size_control(self, signal, features_df):
        """Pozisyon büyüklüğü kontrolü"""
        # Bu örnek implementasyonda sadece sinyali döndürüyoruz
        # Gerçek uygulamada pozisyon büyüklüğü hesaplanabilir
        return signal

    def _overtrading_control(self, signal):
        """Aşırı işlem kontrolü"""
        # Son 5 sinyali kontrol et
        self.last_positions.append(signal)
        if len(self.last_positions) > 5:
            self.last_positions.pop(0)

        # Son 5 işlemde 4'ü aynı yönde ise dur
        if len(self.last_positions) >= 4:
            recent_signals = self.last_positions[-4:]
            if recent_signals.count('buy') >= 3 and signal == 'buy':
                self.logger.warning("Aşırı alım, sinyal iptal edildi")
                return 'hold'
            elif recent_signals.count('sell') >= 3 and signal == 'sell':
                self.logger.warning("Aşırı satım, sinyal iptal edildi")
                return 'hold'

        return signal