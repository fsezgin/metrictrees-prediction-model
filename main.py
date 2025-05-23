import time
import logging
from datetime import datetime, timezone
import asyncio
from threading import Thread
import traceback
import warnings

from config.settings import Config
from data.api_client import APIClient
from data.sliding_window import SlidingWindow
from data.data_processor import DataProcessor
from models.ensemble import EnsemblePredictor
from trading.signal_generator import SignalGenerator
from trading.risk_manager import RiskManager
from utils.logger import setup_logger
from utils.market_analyzer import MarketAnalyzer

# FutureWarning'leri sustur
warnings.filterwarnings('ignore', category=FutureWarning)


class TradingBot:
    def __init__(self):
        self.config = Config()
        self.logger = setup_logger('trading', 'logs/trading.log')

        # Bileşenleri başlat
        self.api_client = APIClient()
        self.sliding_window = SlidingWindow(window_size=60)
        self.data_processor = DataProcessor()
        self.ensemble_predictor = EnsemblePredictor()
        self.signal_generator = SignalGenerator()
        self.risk_manager = RiskManager()
        self.market_analyzer = MarketAnalyzer()

        self.is_running = False

    def start(self):
        """Trading bot'u başlat"""
        self.logger.info("Trading Bot başlatılıyor...")
        self.is_running = True

        # İlk veri setini yükle
        self._initialize_data()

        # Ana döngüyü başlat
        self._main_loop()

    def stop(self):
        """Trading bot'u durdur"""
        self.is_running = False
        self.logger.info("Trading Bot durduruluyor...")

    def _initialize_data(self):
        """İlk 60 dakikalık veriyi yükle"""
        self.logger.info("İlk veri seti yükleniyor...")

        try:
            # Son 60 dakikalık veriyi çek
            initial_data = self.api_client.get_historical_data(minutes=60)

            # Sliding window'u doldur
            for _, row in initial_data.iterrows():
                self.sliding_window.add_data(row.to_dict())

            self.logger.info(f"İlk veri seti yüklendi: {len(initial_data)} dakika")

        except Exception as e:
            self.logger.error(f"İlk veri yükleme hatası: {e}")
            raise

    def _main_loop(self):
        """Ana işlem döngüsü"""
        while self.is_running:
            try:
                current_time = datetime.now(timezone.utc)

                # Her dakikanın 59. saniyesinde çalış
                if current_time.second >= 59:
                    self._process_minute()
                    time.sleep(60 - current_time.second + 1)  # Bir sonraki dakikaya kadar bekle
                else:
                    time.sleep(1)

            except KeyboardInterrupt:
                self.logger.info("Kullanıcı tarafından durduruldu")
                break
            except Exception as e:
                self.logger.error(f"Ana döngü hatası: {e}")
                print(f"ANA DÖNGÜ HATASI: {e}")
                traceback.print_exc()
                time.sleep(5)  # Hata durumunda kısa bir bekleme

    def _process_minute(self):
        """Her dakika çalışan ana işlem"""
        try:
            print("=== ADIM 1: Yeni veri çekiliyor ===")
            # 1. Yeni veriyi çek
            new_data = self.api_client.get_latest_data()

            if new_data is None:
                self.logger.warning("Yeni veri alınamadı")
                return

            print("=== ADIM 2: Sliding window güncelleniyor ===")
            # 2. Sliding window'u güncelle
            self.sliding_window.add_data(new_data)

            print("=== ADIM 3: Window data alınıyor ===")
            # 3. 60 dakikalık pencereyi al
            window_data = self.sliding_window.get_window()

            if len(window_data) < 60:
                self.logger.warning(f"Yetersiz veri: {len(window_data)} dakika")
                return

            print("=== ADIM 4: Feature'lar hesaplanıyor ===")
            # 4. Feature'ları hesapla
            try:
                features_df = self.data_processor.calculate_features(window_data)
                print("Feature hesaplama başarılı")
            except Exception as e:
                print(f"FEATURE HESAPLAMA HATASI: {e}")
                traceback.print_exc()
                raise

            print("***********FEATURESDF***************")
            print(features_df)
            print("**************************")

            print("=== ADIM 5: Market analizi yapılıyor ===")
            # 5. Piyasa durumunu analiz et
            try:
                market_condition = self.market_analyzer.analyze_market(features_df)
                print(f"Market analizi başarılı: {market_condition}")
            except Exception as e:
                print(f"MARKET ANALİZİ HATASI: {e}")
                traceback.print_exc()
                raise

            print("=== ADIM 6: Ensemble tahmin yapılıyor ===")
            # 6. Ensemble tahmin yap
            try:
                prediction = self.ensemble_predictor.predict(features_df, market_condition)
                print(f"Ensemble tahmin başarılı: {prediction}")
            except Exception as e:
                print(f"ENSEMBLE TAHMİN HATASI: {e}")
                traceback.print_exc()
                raise

            print("=== ADIM 7: Sinyal üretiliyor ===")
            # 7. Al/sat sinyali üret
            try:
                signal = self.signal_generator.generate_signal(prediction, features_df, market_condition)
                print(f"Sinyal üretimi başarılı: {signal}")
            except Exception as e:
                print(f"SİNYAL ÜRETİMİ HATASI: {e}")
                traceback.print_exc()
                raise

            print("=== ADIM 8: Risk kontrolü uygulanıyor ===")
            # 8. Risk kontrolü
            try:
                final_signal = self.risk_manager.apply_risk_controls(signal, features_df)
                print(f"Risk kontrolü başarılı: {final_signal}")
            except Exception as e:
                print(f"RİSK KONTROLÜ HATASI: {e}")
                traceback.print_exc()
                raise

            print("=== ADIM 9: Sonuçlar loglanıyor ===")
            # 9. Sonuçları logla
            try:
                self._log_results(prediction, signal, final_signal, market_condition)
                print("Loglama başarılı")
            except Exception as e:
                print(f"LOGLAMA HATASI: {e}")
                traceback.print_exc()
                raise

            print("=== ADIM 10: API'ye gönderiliyor ===")
            # 10. API'ye tahmin ve sinyali gönder
            try:
                self.api_client.send_prediction(prediction, market_condition, final_signal)
                print("API gönderimi başarılı")
            except Exception as e:
                print(f"API GÖNDERİMİ HATASI: {e}")
                traceback.print_exc()
                raise

        except Exception as e:
            self.logger.error(f"Dakikalık işlem hatası: {e}")
            print(f"GENEL HATA: {e}")
            print("STACK TRACE:")
            traceback.print_exc()
            print("-" * 50)

    def _log_results(self, prediction, signal, final_signal, market_condition):
        """Sonuçları logla"""
        try:
            current_price = self.sliding_window.get_latest_price()

            log_msg = f"""
            === TAHMIN SONUÇLARI ===
            Zaman: {datetime.now()}
            Mevcut Fiyat: {current_price:.4f}
            Tahmin Edilen Fiyat: {prediction:.4f}
            Piyasa Durumu: {market_condition}
            İlk Sinyal: {signal}
            Final Sinyal: {final_signal}
            """

            self.logger.info(log_msg)
            print(log_msg)  # Terminal çıktısı
        except Exception as e:
            print(f"LOG RESULTS HATASI: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    bot = TradingBot()
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.stop()
    except Exception as e:
        logging.error(f"Bot başlatma hatası: {e}")
        print(f"BOT BAŞLATMA HATASI: {e}")
        traceback.print_exc()