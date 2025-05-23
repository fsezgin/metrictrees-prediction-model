import json
import os
from datetime import datetime

def ensure_directory(path):
    """Dizin yoksa oluştur"""
    os.makedirs(path, exist_ok=True)

def save_json(data, filepath):
    """JSON formatında kaydet"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_json(filepath):
    """JSON dosyasını yükle"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def format_price(price):
    """Fiyatı formatla"""
    return f"{price:.4f}"

def calculate_percentage_change(old_value, new_value):
    """Yüzde değişimi hesapla"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100