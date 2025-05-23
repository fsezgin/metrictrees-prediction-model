import requests
import pandas as pd
import logging
from datetime import datetime, timedelta, timezone
from config.settings import Config


class APIClient:
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger('api_client')
        self.base_url = self.config.API_BASE_URL

    def get_historical_data(self, minutes=120):
        """Geçmiş veriyi çek"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(minutes=minutes)

            params = {
                'tokenId': self.config.TOKEN_ID,
                'interval': self.config.INTERVAL,
                'startTime': int(start_time.timestamp()),  # saniye
                'endTime': int(end_time.timestamp())
            }

            response = requests.get(f"{self.base_url}/Prices/getinterval", params=params)
            response.raise_for_status()

            data = response.json()
            df = pd.DataFrame(data["data"])

            # Zaman sütununu datetime'a çevir
            if 'time' in df.columns:
                df['timestamp'] = pd.to_datetime(df['time'], unit='s')
                df.set_index('timestamp', inplace=True)

            return df

        except Exception as e:
            self.logger.error(f"Geçmiş veri çekme hatası: {e}")
            return None

    def get_latest_data(self):
        """En son 1 dakikalık veriyi çek"""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(minutes=1)

            params = {
                'tokenId': self.config.TOKEN_ID,
                'interval': self.config.INTERVAL,
                'startTime': int(start_time.timestamp()),
                'endTime': int(end_time.timestamp())
            }

            response = requests.get(f"{self.base_url}/Prices/getinterval", params=params)
            response.raise_for_status()

            data = response.json()

            if data and len(data) > 0:
                latest = data["data"][-1]
                print(latest['time'])
                print(type(latest['time']))
                df = pd.DataFrame([latest])

                if 'time' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['time'], unit='s')
                    df.set_index('timestamp', inplace=True)
                return df

            return pd.DataFrame()  # Veri yoksa boş DataFrame döndür

        except Exception as e:
            self.logger.error(f"Son veri çekme hatası: {e}")
            return pd.DataFrame()  # Hata durumunda da boş DataFrame döndür

    def send_prediction(self, predicted_price, strategy_type, signal):
        """Tahmin ve sinyali API'ye gönder"""
        try:
            data = {
                'predictedClose': predicted_price,
                'predictionMinute': datetime.now(timezone.utc).isoformat(),
                'strategyType': int(strategy_type),
                'signal': signal  # 'buy', 'sell', 'hold'
            }

            response = requests.post(f"{self.base_url}/Prices/send", json=data)
            response.raise_for_status()

            self.logger.info(f"Tahmin gönderildi: {data}")
            return True

        except Exception as e:
            self.logger.error(f"Tahmin gönderme hatası: {e}")
            return False