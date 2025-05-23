import logging
import os
from config.settings import Config


def setup_logger(name, log_file, level=logging.INFO):
    """Logger kurulumu"""
    config = Config()

    # Log dizinini oluştur
    os.makedirs('logs', exist_ok=True)

    # Formatter
    formatter = logging.Formatter(config.LOG_FORMAT)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
