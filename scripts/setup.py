import os
import sys


def create_directories():
    """Gerekli dizinleri oluştur"""
    directories = [
        'config',
        'models/saved_models',
        'data/scalers',
        'trading',
        'utils',
        'logs',
        'scripts'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ {directory} dizini oluşturuldu")

    # __init__.py dosyalarını oluştur
    init_dirs = ['config', 'models', 'data', 'trading', 'utils']
    for directory in init_dirs:
        init_file = os.path.join(directory, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# -*- coding: utf-8 -*-\n')
            print(f"✓ {init_file} oluşturuldu")


def check_requirements():
    """Gerekli dosyaların varlığını kontrol et"""
    required_files = [
        'models/saved_models/lstm_model.h5',
        'models/saved_models/cnn_lstm_model.h5',
        'models/saved_models/transformer_lstm_model.h5',
        'models/saved_models/attention_gru_model.h5',
        'models/saved_models/stacked_lstm_model.h5',
        'data/scalers/scaler_X.pkl',
        'data/scalers/scaler_y.pkl'
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print("\n⚠️  Eksik dosyalar:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\nLütfen bu dosyaları ilgili dizinlere yerleştirin.")
        return False
    else:
        print("\n✓ Tüm gerekli dosyalar mevcut")
        return True


if __name__ == "__main__":
    print("🚀 Crypto Trading Bot Kurulumu")
    print("=" * 50)

    create_directories()

    print("\n📋 Dosya kontrolü:")
    all_files_present = check_requirements()

    if all_files_present:
        print("\n✅ Kurulum tamamlandı!")
        print("Sistemi başlatmak için: python main.py")
    else:
        print("\n❌ Kurulum tamamlanamadı. Eksik dosyaları yerleştirin.")
        sys.exit(1)