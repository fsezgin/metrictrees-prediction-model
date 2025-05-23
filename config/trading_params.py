class TradingParams:
    # Ensemble Ağırlık Stratejileri
    ENSEMBLE_WEIGHTS = {
        1: {  # Trend Takip Dönemleri
            'lstm': 0.40,
            'cnn_lstm': 0.35,
            'transformer_lstm': 0.25,
            'attention_gru': 0.0,
            'stacked_lstm': 0.0
        },
        2: {  # Sideways Piyasa
            'attention_gru': 0.60,
            'lstm': 0.0,
            'cnn_lstm': 0.0,
            'transformer_lstm': 0.0
        },
        3: {  # Yüksek Volatilite
            'cnn_lstm': 0.55,
            'transformer_lstm': 0.45,
            'lstm': 0.0,
            'attention_gru': 0.0,
            'stacked_lstm': 0.0
        },
        4: {  # Düşük Volatilite
            'lstm': 0.45,
            'stacked_lstm': 0.30,
            'attention_gru': 0.25,
            'cnn_lstm': 0.0,
            'transformer_lstm': 0.0
        }
    }

    # Al/Sat Sinyal Parametreleri
    TOLERANCE = 0.001  # %0.1 tolerans
    MIN_MOVE = 0.002  # Minimum %0.2 hareket
    STOP_LOSS_THRESHOLD = 0.02  # %2 stop loss

    # Pozisyon Yönetimi
    MAX_POSITION_SIZE = 1000  # Maksimum pozisyon büyüklüğü
    MIN_POSITION_SIZE = 10  # Minimum pozisyon büyüklüğü
    RISK_PER_TRADE = 0.02  # Trade başına risk %2

    # Piyasa Durumu Parametreleri
    VOLATILITY_THRESHOLD_HIGH = 0.02  # Yüksek volatilite eşiği
    VOLATILITY_THRESHOLD_LOW = 0.005  # Düşük volatilite eşiği
    TREND_THRESHOLD = 0.001  # Trend eşiği
    SIDEWAYS_THRESHOLD = 0.0005  # Sideways eşiği