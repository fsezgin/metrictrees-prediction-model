import pandas as pd
import numpy as np
import logging
import pickle
from config.settings import Config


class DataProcessor:
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger('data_processor')

        # Scaler'ları yükle
        self.load_scalers()

    def load_scalers(self):
        """Scaler'ları yükle"""
        try:
            with open(self.config.SCALER_X_PATH, 'rb') as f:
                self.scaler_X = pickle.load(f)

            with open(self.config.SCALER_Y_PATH, 'rb') as f:
                self.scaler_y = pickle.load(f)

            self.logger.info("Scaler'lar başarıyla yüklendi")

        except Exception as e:
            self.logger.error(f"Scaler yükleme hatası: {e}")
            raise

    def calculate_features(self, df, look_back=60, step_ahead=15):
        """Feature'ları hesapla (sizin kodunuzdan)"""
        # Kopyala
        price_df = df[['open', 'high', 'low', 'close', 'volumeTo']].copy()

        # Hedef (tahmin için gerekli değil ama feature hesabında kullanılıyor)
        price_df['target'] = price_df['close'].shift(-step_ahead)

        # Çoklu lag özellikleri
        for lag in [5, 20, 60, look_back]:
            price_df[f'closelag{lag}'] = price_df['close'].shift(lag)

        # Rolling özet istatistikler
        windows = [20, 60, look_back]
        for w in windows:
            price_df[f'close_mean_{w}'] = price_df['close'].rolling(w).mean()
            price_df[f'close_std_{w}'] = price_df['close'].rolling(w).std()

            # Slope hesaplama
            def slope(x):
                if x.isnull().any():
                    return np.nan
                return np.polyfit(np.arange(len(x)), x.to_numpy(), 1)[0]

            price_df[f'close_slope_{w}'] = price_df['close'].rolling(w).apply(slope, raw=False)

        # ATR
        high_low = price_df['high'] - price_df['low']
        high_prev_close = (price_df['high'] - price_df['close'].shift(1)).abs()
        low_prev_close = (price_df['low'] - price_df['close'].shift(1)).abs()
        tr = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)
        price_df['atr_14'] = tr.rolling(14).mean()

        # VWAP
        pv = ((price_df['high'] + price_df['low'] + price_df['close']) / 3) * price_df['volumeTo']
        price_df['vwap'] = pv.cumsum() / price_df['volumeTo'].cumsum()

        # OBV ve CMF
        obv = ((price_df['close'].diff() > 0).astype(int) * 2 - 1) * price_df['volumeTo']
        price_df['obv'] = obv.cumsum()

        mfv = ((price_df['close'] - price_df['low']) - (price_df['high'] - price_df['close'])) \
              / (price_df['high'] - price_df['low'] + 1e-9) * price_df['volumeTo']
        price_df['cmf_20'] = mfv.rolling(20).sum() / price_df['volumeTo'].rolling(20).sum()

        # RSI 7
        delta = price_df['close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(7).mean()
        avg_loss = loss.rolling(7).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        price_df['rsi_7'] = 100 - 100 / (1 + rs)

        # RSI bayrakları
        price_df['rsi_overbought'] = (price_df['rsi_7'] > 70).astype(int)
        price_df['rsi_oversold'] = (price_df['rsi_7'] < 30).astype(int)

        # MACD
        ema_fast = price_df['close'].ewm(span=8, adjust=False).mean()
        ema_slow = price_df['close'].ewm(span=17, adjust=False).mean()
        macd = ema_fast - ema_slow
        price_df['macd'] = macd
        price_df['macd_signal'] = macd.ewm(span=9, adjust=False).mean()
        price_df['macd_hist'] = price_df['macd'] - price_df['macd_signal']

        # Bollinger Band
        ma20 = price_df['close'].rolling(20).mean()
        std20 = price_df['close'].rolling(20).std()
        price_df['bb_pos'] = (price_df['close'] - (ma20 - 2 * std20)) / (4 * std20)

        # Log getiri
        price_df['log_ret'] = np.log(price_df['close'] / price_df['close'].shift(1) + 1e-9)

        # Zaman periyodik
        if isinstance(price_df.index, pd.DatetimeIndex):
            h = price_df.index.hour + price_df.index.minute / 60
            price_df['hour_sin'] = np.sin(2 * np.pi * h / 24)
            price_df['hour_cos'] = np.cos(2 * np.pi * h / 24)
            wd = price_df.index.weekday
            price_df['dow_sin'] = np.sin(2 * np.pi * wd / 7)
            price_df['dow_cos'] = np.cos(2 * np.pi * wd / 7)
            price_df['is_weekend'] = (wd >= 5).astype(int)
            # Zaman-hacim etkileşimi
            price_df['hour_volume'] = price_df['hour_sin'] * price_df['volumeTo']

        # Pivot seviyeleri
        price_df['pivot'] = (price_df['high'].shift(1) + price_df['low'].shift(1) + price_df['close'].shift(1)) / 3
        price_df['support_1'] = 2 * price_df['pivot'] - price_df['high'].shift(1)
        price_df['resistance_1'] = 2 * price_df['pivot'] - price_df['low'].shift(1)

        # NaN'ları temizle
        price_df.dropna(inplace=True)

        return price_df

    def prepare_model_input(self, features_df):
        """Model için giriş verilerini hazırla"""
        # Sadece kullandığınız feature'ları seç
        selected_features = features_df[self.config.FEATURES_LIST].copy()
        selected_features = features_df[self.config.FEATURES_LIST].copy()
        print(selected_features)

        # Son satırı al (en güncel veri)
        latest_features = selected_features.iloc[-self.config.LOOK_BACK:].values
        print(latest_features.shape)

        # Reshape et
        X = latest_features.reshape(1, self.config.LOOK_BACK, self.config.FEATURES)

        # Scale et
        X_2d = X.reshape(-1, self.config.FEATURES)
        X_scaled_2d = self.scaler_X.transform(X_2d)
        X_scaled = X_scaled_2d.reshape(X.shape)

        return X_scaled

    def inverse_transform_prediction(self, scaled_prediction):
        """Tahmin değerini orijinal ölçeğe çevir"""
        try:
            original_prediction = self.scaler_y.inverse_transform([[scaled_prediction]])[0][0]
            return original_prediction
        except Exception\
                as e:
            self.logger.error(f"Inverse transform hatası: {e}")
            return scaled_prediction