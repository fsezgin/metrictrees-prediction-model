import numpy as np
import logging
from models.model_loader import ModelLoader
from data.data_processor import DataProcessor
from config.settings import Config
from config.trading_params import TradingParams


class EnsemblePredictor:
    def __init__(self):
        self.config = Config()
        self.trading_params = TradingParams()
        self.logger = logging.getLogger('ensemble_predictor')

        # Model loader'ı başlat
        self.model_loader = ModelLoader()
        self.data_processor = DataProcessor()

        # Modelleri yükle
        if not self.model_loader.load_all_models():
            raise Exception("Modeller yüklenemedi!")

        self.models = self.model_loader.get_all_models()
        self.logger.info(f"Ensemble başlatıldı: {list(self.models.keys())}")

    def predict(self, features_df, market_condition):
        """Ensemble tahmin yap"""
        try:
            # Model giriş verilerini hazırla
            model_input = self.data_processor.prepare_model_input(features_df)
            if model_input is None:
                return None

            # Her modelden tahmin al
            predictions = {}
            for model_name, model in self.models.items():
                try:
                    pred = model.predict(model_input, verbose=0)[0][0]
                    predictions[model_name] = pred
                    self.logger.debug(f"{model_name} tahmini: {pred}")
                except Exception as e:
                    self.logger.error(f"{model_name} tahmin hatası: {e}")
                    predictions[model_name] = 0

            # Piyasa durumuna göre ağırlıkları al
            weights = self.trading_params.ENSEMBLE_WEIGHTS[market_condition]

            # Ağırlıklı ortalama hesapla
            weighted_prediction = 0
            total_weight = 0

            for model_name, weight in weights.items():
                if model_name in predictions and weight > 0:
                    weighted_prediction += predictions[model_name] * weight
                    total_weight += weight

            if total_weight > 0:
                final_prediction = weighted_prediction / total_weight
            else:
                # Fallback: tüm tahminlerin ortalaması
                final_prediction = np.mean(list(predictions.values()))

            # Scale'i geri çevir
            original_prediction = self.data_processor.inverse_transform_prediction(final_prediction)

            self.logger.info(f"Ensemble tahmin - Market: {market_condition}, Sonuç: {original_prediction:.4f}")

            return original_prediction

        except Exception as e:
            self.logger.error(f"Ensemble tahmin hatası: {e}")
            return None