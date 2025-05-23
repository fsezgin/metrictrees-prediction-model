import numpy as np
import logging
from config.trading_params import TradingParams


class MarketAnalyzer:
    def __init__(self):
        self.params = TradingParams()
        self.logger = logging.getLogger('market_analyzer')

    def analyze_market(self, features_df):
        """Piyasa durumunu analiz et ve strateji tipini döndür"""
        try:
            if len(features_df) < 20:
                return 1  # Default: trend following

            # Volatilite hesapla (son 20 periyot)
            volatility = self._calculate_volatility(features_df)

            # Trend analizi
            trend_strength = self._analyze_trend(features_df)

            # Piyasa durumunu belirle
            market_condition = self._determine_market_condition(volatility, trend_strength)

            self.logger.info(
                f"Piyasa analizi - Volatilite: {volatility:.4f}, Trend: {trend_strength:.4f}, Durum: {market_condition}")

            return market_condition

        except Exception as e:
            self.logger.error(f"Piyasa analizi hatası: {e}")
            return 1  # Default

    def _calculate_volatility(self, features_df):
        """Volatilite hesapla"""
        if 'log_ret' in features_df.columns:
            returns = features_df['log_ret'].tail(20)
            volatility = returns.std()
        else:
            # Fallback: close fiyat değişimi
            close_changes = features_df['close'].pct_change().tail(20)
            volatility = close_changes.std()

        return volatility if not np.isnan(volatility) else 0.01

    def _analyze_trend(self, features_df):
        """Trend gücünü analiz et"""
        try:
            # Slope değerlerini kullan
            if 'close_slope_60' in features_df.columns:
                slope = features_df['close_slope_60'].iloc[-1]
            else:
                # Fallback: basit slope hesapla
                close_prices = features_df['close'].tail(20)
                x = np.arange(len(close_prices))
                slope = np.polyfit(x, close_prices.values, 1)[0]

            return abs(slope) if not np.isnan(slope) else 0

        except Exception as e:
            self.logger.error(f"Trend analizi hatası: {e}")
            return 0

    def _determine_market_condition(self, volatility, trend_strength):
        """Piyasa durumunu belirle"""
        # Yüksek volatilite
        if volatility > self.params.VOLATILITY_THRESHOLD_HIGH:
            return 3  # Yüksek volatilite stratejisi

        # Düşük volatilite
        elif volatility < self.params.VOLATILITY_THRESHOLD_LOW:
            return 4  # Düşük volatilite stratejisi

        # Güçlü trend
        elif trend_strength > self.params.TREND_THRESHOLD:
            return 1  # Trend takip stratejisi

        # Sideways piyasa
        else:
            return 2  # Sideways strateji