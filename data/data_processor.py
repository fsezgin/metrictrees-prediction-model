import pandas as pd
import numpy as np
import logging
import pickle
import warnings
from config.settings import Config

# FutureWarning'leri sustur
warnings.filterwarnings('ignore', category=FutureWarning)


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
        price_df['close'] = pd.to_numeric(price_df['close'], errors='coerce')

        # Hedef (tahmin için gerekli değil ama feature hesabında kullanılıyor)
        price_df['target'] = price_df['close'].shift(-step_ahead)

        # Çoklu lag özellikleri
        for lag in [5, 20, 60, look_back]:
            price_df[f'closelag{lag}'] = price_df['close'].shift(lag)

        # Rolling özet istatistikler
        windows = [20, 60, look_back]

        # Slope fonksiyonunu loop dışında tanımla
        def safe_slope(x):
            try:
                if len(x) == 0 or x.isna().all():
                    return np.nan
                clean_x = x.dropna()
                if len(clean_x) < 2:
                    return np.nan
                return np.polyfit(np.arange(len(clean_x)), clean_x.values, 1)[0]
            except:
                return np.nan

        for w in windows:
            # FutureWarning tamamen düzeltildi
            rolling_mean = price_df['close'].rolling(w).mean()
            rolling_std = price_df['close'].rolling(w).std()
            rolling_slope = price_df['close'].rolling(w).apply(safe_slope, raw=False)

            price_df[f'close_mean_{w}'] = rolling_mean
            price_df[f'close_std_{w}'] = rolling_std
            price_df[f'close_slope_{w}'] = rolling_slope

        # ATR - FIXED TRUE RANGE CALCULATION
        high_low = price_df['high'] - price_df['low']
        high_prev_close = (price_df['high'] - price_df['close'].shift(1)).abs()
        low_prev_close = (price_df['low'] - price_df['close'].shift(1)).abs()

        # Debug information (remove after fixing)
        self.logger.debug(f"high_low NaN count: {high_low.isna().sum()}")
        self.logger.debug(f"high_prev_close NaN count: {high_prev_close.isna().sum()}")
        self.logger.debug(f"low_prev_close NaN count: {low_prev_close.isna().sum()}")

        # FIX: Use numeric_only and skipna parameters to handle the ambiguous truth value error
        try:
            tr_df = pd.concat([high_low, high_prev_close, low_prev_close], axis=1)
            tr = tr_df.max(axis=1, skipna=True, numeric_only=True)
        except Exception as e:
            self.logger.warning(f"TR calculation with pandas failed, using numpy: {e}")
            # Fallback to numpy approach
            tr = np.maximum.reduce([
                high_low.fillna(0).values,
                high_prev_close.fillna(0).values,
                low_prev_close.fillna(0).values
            ])
            tr = pd.Series(tr, index=price_df.index)

        price_df['atr_14'] = tr.rolling(14).mean()

        # VWAP
        pv = ((price_df['high'] + price_df['low'] + price_df['close']) / 3) * price_df['volumeTo']
        price_df['vwap'] = pv.cumsum() / price_df['volumeTo'].cumsum()

        # OBV ve CMF - FIXED OBV CALCULATION
        try:
            close_diff = price_df['close'].diff()
            # Handle NaN values and ensure proper comparison
            close_diff_clean = close_diff.fillna(0)
            obv_direction = (close_diff_clean > 0).astype(int) * 2 - 1
            obv = obv_direction * price_df['volumeTo']
            price_df['obv'] = obv.cumsum()
        except Exception as e:
            self.logger.warning(f"OBV calculation failed, using fallback: {e}")
            # Fallback: simple volume-based calculation
            price_df['obv'] = price_df['volumeTo'].cumsum()

        # CMF - FIXED CALCULATION
        try:
            high_low_diff = price_df['high'] - price_df['low']
            # Avoid division by zero
            high_low_diff = high_low_diff.replace(0, 1e-9)

            mfv = ((price_df['close'] - price_df['low']) - (price_df['high'] - price_df['close'])) \
                  / high_low_diff * price_df['volumeTo']

            # Handle potential NaN values
            mfv = mfv.fillna(0)
            volume_sum = price_df['volumeTo'].rolling(20).sum()
            volume_sum = volume_sum.replace(0, 1e-9)  # Avoid division by zero

            price_df['cmf_20'] = mfv.rolling(20).sum() / volume_sum
        except Exception as e:
            self.logger.warning(f"CMF calculation failed, using fallback: {e}")
            # Fallback: set to zero
            price_df['cmf_20'] = 0

        # RSI 7
        delta = price_df['close'].diff()
        delta = pd.to_numeric(delta, errors='coerce')
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

        # Zaman periyodik - Boolean kontrol düzeltildi
        try:
            if hasattr(price_df.index, 'hour'):
                h = price_df.index.hour + price_df.index.minute / 60
                price_df['hour_sin'] = np.sin(2 * np.pi * h / 24)
                price_df['hour_cos'] = np.cos(2 * np.pi * h / 24)
                wd = price_df.index.weekday
                price_df['dow_sin'] = np.sin(2 * np.pi * wd / 7)
                price_df['dow_cos'] = np.cos(2 * np.pi * wd / 7)
                price_df['is_weekend'] = (wd >= 5).astype(int)
                # Zaman-hacim etkileşimi
                price_df['hour_volume'] = price_df['hour_sin'] * price_df['volumeTo']
            else:
                # DateTime index değilse varsayılan değerler
                price_df['hour_sin'] = 0
                price_df['hour_cos'] = 1
                price_df['dow_sin'] = 0
                price_df['dow_cos'] = 1
                price_df['is_weekend'] = 0
                price_df['hour_volume'] = 0
        except Exception as e:
            self.logger.warning(f"Zaman feature'ları hesaplanamadı: {e}")
            # Varsayılan değerler
            price_df['hour_sin'] = 0
            price_df['hour_cos'] = 1
            price_df['dow_sin'] = 0
            price_df['dow_cos'] = 1
            price_df['is_weekend'] = 0
            price_df['hour_volume'] = 0

        # Pivot seviyeleri
        price_df['pivot'] = (price_df['high'].shift(1) + price_df['low'].shift(1) + price_df['close'].shift(1)) / 3
        price_df['support_1'] = 2 * price_df['pivot'] - price_df['high'].shift(1)
        price_df['resistance_1'] = 2 * price_df['pivot'] - price_df['low'].shift(1)

        # NaN'ları temizle
        price_df.dropna(inplace=True)

        last_60_rows = price_df.tail(60)

        return last_60_rows

    def prepare_model_input(self, features_df):
        """Model için giriş verilerini hazırla"""
        try:
            # Sadece kullandığınız feature'ları seç
            selected_features = features_df[self.config.FEATURES_LIST].copy()
            # Tekrar eden satır kaldırıldı
            print("SELECTED FEATURE SHAPE")
            print(selected_features.shape)
            print("FEATURES from config:", self.config.FEATURES)
            print("Actual features in data:", selected_features.shape[1])

            # Son satırı al (en güncel veri)
            latest_features = selected_features.iloc[-self.config.LOOK_BACK:].values
            print("LATEST FEATURES SHAPE")
            print(latest_features.shape)

            # Reshape et
            X = latest_features.reshape(1, self.config.LOOK_BACK, self.config.FEATURES)

            print("X SHAPE")
            print(X.shape)

            # Scale et
            X_2d = X.reshape(-1, self.config.FEATURES)
            print("X 2D")
            print(X_2d.shape)
            X_scaled_2d = self.scaler_X.transform(X_2d)
            print("X SCALED 2D")
            print(X_scaled_2d.shape)
            X_scaled = X_scaled_2d.reshape(X.shape)
            print("X SCALED")
            print(X_scaled.shape)

            return X_scaled

        except Exception as e:
            self.logger.error(f"Model input hazırlama hatası: {e}")
            raise

    def inverse_transform_prediction(self, scaled_prediction):
        """Tahmin değerini orijinal ölçeğe çevir"""
        try:
            original_prediction = self.scaler_y.inverse_transform([[scaled_prediction]])[0][0]
            return original_prediction
        except Exception as e:
            self.logger.error(f"Inverse transform hatası: {e}")
            return scaled_prediction