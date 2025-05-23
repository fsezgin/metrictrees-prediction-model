import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Test imports
from data.api_client import APIClient
from data.sliding_window import SlidingWindow
from data.data_processor import DataProcessor
from models.ensemble import EnsemblePredictor
from utils.market_analyzer import MarketAnalyzer
from trading.signal_generator import SignalGenerator


def test_api_client():
    """API Client testi"""
    print("🔌 API Client testi...")
    try:
        client = APIClient()
        # Test için mock data kullan
        print("✓ API Client başarıyla oluşturuldu")
        return True
    except Exception as e:
        print(f"❌ API Client hatası: {e}")
        return False


def test_sliding_window():
    """Sliding Window testi"""
    print("📊 Sliding Window testi...")
    try:
        window = SlidingWindow(window_size=5)

        # Test verisi ekle
        for i in range(7):
            test_data = {
                'timestamp': datetime.now() - timedelta(minutes=7 - i),
                'open': 100 + i,
                'high': 102 + i,
                'low': 98 + i,
                'close': 101 + i,
                'volumeTo': 1000
            }
            window.add_data(test_data)

        df = window.get_window()
        assert len(df) == 5, f"Window size hatası: {len(df)} != 5"
        print("✓ Sliding Window testi başarılı")
        return True
    except Exception as e:
        print(f"❌ Sliding Window hatası: {e}")
        return False


def test_data_processor():
    """Data Processor testi"""
    print("⚙️ Data Processor testi...")
    try:
        # Mock veri oluştur
        dates = pd.date_range(start='2024-01-01', periods=100, freq='T')
        df = pd.DataFrame({
            'timestamp': dates,
            'open': np.random.uniform(100, 110, 100),
            'high': np.random.uniform(105, 115, 100),
            'low': np.random.uniform(95, 105, 100),
            'close': np.random.uniform(100, 110, 100),
            'volumeTo': np.random.uniform(1000, 2000, 100)
        })
        df.set_index('timestamp', inplace=True)

        processor = DataProcessor()
        features_df = processor.calculate_features(df)

        print(f"✓ Feature hesaplama başarılı: {len(features_df)} satır")
        return True
    except Exception as e:
        print(f"❌ Data Processor hatası: {e}")
        return False


def run_all_tests():
    """Tüm testleri çalıştır"""
    print("🧪 Sistem Testleri Başlatılıyor")
    print("=" * 50)

    tests = [
        test_api_client,
        test_sliding_window,
        test_data_processor,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"📈 Test Sonuçları: {passed}/{total} başarılı")

    if passed == total:
        print("✅ Tüm testler başarılı!")
        return True
    else:
        print("❌ Bazı testler başarısız!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)