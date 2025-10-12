"""Modul untuk konfigurasi logging aplikasi.

Menyediakan instance logger tunggal yang dapat diimpor dan digunakan di
seluruh proyek untuk mencatat informasi, peringatan, dan error.
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from src.configs.config import LOGS_PATH


def setup_logger():
    """Mengkonfigurasi dan mengembalikan instance logger.

    Logger ini akan mencatat pesan ke file log (`app.log`) dan juga
    menampilkannya di konsol. Menggunakan `RotatingFileHandler` untuk
    membatasi ukuran file log.

    Returns:
        logging.Logger: Instance logger yang sudah dikonfigurasi.
    """
    # Pastikan direktori logs ada
    os.makedirs(LOGS_PATH, exist_ok=True)

    log_file = os.path.join(LOGS_PATH, 'app.log')

    # Tentukan format pesan log
    log_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    )

    # Dapatkan logger utama untuk aplikasi
    logger = logging.getLogger('KlasifikasiCuaca')
    logger.setLevel(logging.INFO)

    # Mencegah penambahan handler berulang kali jika fungsi dipanggil lagi
    if logger.hasHandlers():
        return logger

    # Handler untuk menulis log ke file, dengan rotasi
    # Ukuran file maksimal 5MB, dengan 3 file backup
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3
    )
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    # Handler untuk menampilkan log di konsol
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    return logger


# Buat instance logger global yang bisa diimpor dari modul lain
logger = setup_logger()
