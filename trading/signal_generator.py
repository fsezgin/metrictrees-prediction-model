import logging
from config.trading_params import TradingParams


class SignalGenerator:
    def __init__(self):
        self.params = TradingParams()
        self.logger = logging.getLogger('signal_generator')

    def generate_signal(self, prediction, features_df, market_condition):
        """Al/sat sinyali üret"""
        try:
            if prediction is None or len(features_df) == 0:
                return 'hold'

            # Mevcut fiyatı al
            current_price = features_df['close'].iloc[-1]

            # Fiyat değişimi yüzdesini hesapla
            price_change = (prediction - current_price) / current_price

            # Temel sinyal mantığı
            signal = self._basic_signal_logic(price_change)

            # Piyasa durumuna göre sinyal filtreleme
            filtered_signal = self._filter_by_market_condition(signal, features_df, market_condition)

            # Teknik indikatör filtreleme
            final_signal = self._technical_filter(filtered_signal, features_df)

            self.logger.info(f"Sinyal üretimi - Değişim: {price_change:.4f}, Temel: {signal}, Final: {final_signal}")

            return final_signal

        except Exception as e:
            self.logger.error(f"Sinyal üretimi hatası: {e}")
            return 'hold'

    def _basic_signal_logic(self, price_change):
        """Temel sinyal mantığı"""
        if price_change > self.params.MIN_MOVE:
            return 'buy'
        elif price_change < -self.params.MIN_MOVE:
            return 'sell'
        else:
            return 'hold'

    def _filter_by_market_condition(self, signal, features_df, market_condition):
        """Piyasa durumuna göre sinyal filtrele"""
        try:
            # Yüksek volatilite dönemlerinde daha temkinli ol
            if market_condition == 3:  # Yüksek volatilite
                if 'atr_14' in features_df.columns:
                    atr = features_df['atr_14'].iloc[-1]
                    if atr > features_df['atr_14'].mean() * 1.5:
                        # Çok yüksek volatilite, bekle
                        return 'hold'

            # Sideways piyasada daha sık işlem
            elif market_condition == 2:  # Sideways
                # RSI ile kontrol
                if 'rsi_7' in features_df.columns:
                    rsi = features_df['rsi_7'].iloc[-1]
                    if signal == 'buy' and rsi > 70:
                        return 'hold'  # Aşırı alım
                    elif signal == 'sell' and rsi < 30:
                        return 'hold'  # Aşırı satım

            return signal

        except Exception as e:
            self.logger.error(f"Market condition filter hatası: {e}")
            return signal

    def _technical_filter(self, signal, features_df):
        """Teknik indikatör filtresi"""
        try:
            # MACD kontrolü
            if 'macd_hist' in features_df.columns:
                macd_hist = features_df['macd_hist'].iloc[-1]

                if signal == 'buy' and macd_hist < 0:
                    # MACD negatif iken al sinyali verme
                    signal = 'hold'
                elif signal == 'sell' and macd_hist > 0:
                    # MACD pozitif iken sat sinyali verme
                    signal = 'hold'

            # Volume kontrolü
            if 'volumeTo' in features_df.columns:
                current_volume = features_df['volumeTo'].iloc[-1]
                avg_volume = features_df['volumeTo'].tail(20).mean()

                # Düşük volume'da işlem yapma
                if current_volume < avg_volume * 0.5:
                    signal = 'hold'

            return signal

        except Exception as e:
            self.logger.error(f"Technical filter hatası: {e}")
            return signal