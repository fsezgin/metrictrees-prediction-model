from collections import deque
import pandas as pd
import logging


class SlidingWindow:
    def __init__(self, window_size=60):
        self.window_size = window_size
        self.data = deque(maxlen=window_size)
        self.logger = logging.getLogger('sliding_window')

    def add_data(self, data_point):
        """Yeni veri noktası ekle"""
        self.data.append(data_point)
        self.logger.debug(f"Yeni veri eklendi. Toplam: {len(self.data)}")

    def get_window(self):
        """Mevcut pencereyi DataFrame olarak döndür"""
        if len(self.data) == 0:
            return pd.DataFrame()

        df = pd.DataFrame(list(self.data))

        return df

    def is_full(self):
        """Pencere dolu mu?"""
        return len(self.data) == self.window_size

    def get_latest_price(self):
        """En son fiyatı döndür"""
        if len(self.data) > 0:
            return self.data[-1].get('close', 0)
        return 0

    def clear(self):
        """Pencereyi temizle"""
        self.data.clear()

    def size(self):
        """Mevcut veri sayısı"""
        return len(self.data)