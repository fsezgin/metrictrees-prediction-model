import os


class Config:
    # API Ayarları
    API_BASE_URL = "https://api.metrictrees.yusuf-erdem.com/api/v1"
    TOKEN_ID = 2 # XRP
    INTERVAL = "1m"

    # Model Ayarları
    LOOK_BACK = 60
    STEP_AHEAD = 15
    FEATURES = 21  # Kullandığımız feature sayısı

    # Model Dosya Yolları
    MODEL_PATHS = {
        'lstm': r'C:\Users\lunaf\Desktop\Projects\MetricTrees-AI\MetricTrees-Prediction-Model\models\saved_models\LSTM_best_model.h5',
        'cnn_lstm': r'C:\Users\lunaf\Desktop\Projects\MetricTrees-AI\MetricTrees-Prediction-Model\models\saved_models\CNN-LSTM_best_model.h5',
        'transformer_lstm': r'C:\Users\lunaf\Desktop\Projects\MetricTrees-AI\MetricTrees-Prediction-Model\models\saved_models\Transformer-LSTM_best_model.h5',
        'attention_gru': r'C:\Users\lunaf\Desktop\Projects\MetricTrees-AI\MetricTrees-Prediction-Model\models\saved_models\Attention-GRU_best_model.h5',
        'stacked_lstm': r'C:\Users\lunaf\Desktop\Projects\MetricTrees-AI\MetricTrees-Prediction-Model\models\saved_models\Stacked-LSTM_best_model.h5'
    }

    # Scaler Dosya Yolları
    SCALER_X_PATH = 'data/scalers/scaler_X.pkl'
    SCALER_Y_PATH = 'data/scalers/scaler_y.pkl'

    # Feature Listesi (kullandığınız feature'lar)
    FEATURES_LIST = [
        'low', 'log_ret', 'obv', 'vwap', 'hour_sin', 'hour_cos', 'dow_sin',
        'close_std_60', 'atr_14', 'dow_cos', 'close_std_20', 'close_slope_60',
        'hour_volume', 'macd_signal', 'volumeTo', 'is_weekend', 'close_slope_20',
        'rsi_7', 'cmf_20', 'macd_hist'
    ]

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"