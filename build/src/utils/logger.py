import os
import logging
from logging.handlers import RotatingFileHandler

from src.configs.config import LOGS_PATH

def setup_logger():
    """
    Mengkonfigurasi dan mengembalikan instance logger.
    Logger ini akan mencatat ke file dan konsol.
    """
    os.makedirs(LOGS_PATH, exist_ok=True)
    
    log_file = os.path.join(LOGS_PATH, 'app.log')

    # Konfigurasi format log
    log_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    )
    
    logger = logging.getLogger('KlasifikasiCuaca')
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        return logger
    
    # Max 5MB per file, dengan 3 file backup
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3
    )
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()
