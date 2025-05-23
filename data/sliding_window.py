import pandas as pd
import logging


class SlidingWindow:
    def __init__(self, window_size=120):
        self.window_size = window_size
        self.data = pd.DataFrame()
        self.logger = logging.getLogger('sliding_window')

    def add_data(self, data_point):
        if not isinstance(data_point, pd.DataFrame):
            if isinstance(data_point, dict):
                df_point = pd.DataFrame([data_point])
            else:
                df_point = pd.DataFrame(data_point)
        else:
            df_point = data_point

        if 'time' in df_point.columns:
            df_point['timestamp'] = pd.to_datetime(df_point['time'], unit='s')  # saniye cinsinden Unix zamanı ise
            df_point.set_index('timestamp', inplace=True)

        self.data = pd.concat([self.data, df_point])
        self.data = self.data[~self.data.index.duplicated(keep='last')]
        self.data.sort_index(inplace=True)

        if len(self.data) > self.window_size:
            self.data = self.data.iloc[-self.window_size:]

        self.logger.debug(f"Yeni veri eklendi. Toplam: {len(self.data)}")

    def get_window(self):
        if len(self.data) == 0:
            return pd.DataFrame()
        return self.data.copy()

    def is_full(self):
        return len(self.data) == self.window_size

    def get_latest_price(self):
        if len(self.data) > 0:
            return self.data.iloc[-1].get('close', 0)
        return 0

    def clear(self):
        self.data = pd.DataFrame()

    def size(self):
        return len(self.data)
