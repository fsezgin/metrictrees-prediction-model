import tensorflow as tf
import logging
from config.settings import Config


class ModelLoader:
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger('model_loader')
        self.models = {}

    def load_all_models(self):
        """Tüm modelleri yükle"""
        for model_name, model_path in self.config.MODEL_PATHS.items():
            try:
                model = tf.keras.models.load_model(model_path)
                self.models[model_name] = model
                self.logger.info(f"{model_name} modeli yüklendi: {model_path}")
            except Exception as e:
                self.logger.error(f"{model_name} modeli yüklenemedi: {e}")

        return len(self.models) == len(self.config.MODEL_PATHS)

    def get_model(self, model_name):
        """Belirli bir modeli döndür"""
        return self.models.get(model_name)

    def get_all_models(self):
        """Tüm modelleri döndür"""
        return self.models