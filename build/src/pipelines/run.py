import os
import sys
from datetime import datetime

from pipeline import run_pipeline
from src.utils.logger import setup_logger
from src.configs.config import (
    DATA_RAW_PATH, SAVED_MODEL_PATH, RESULTS_PATH, LOGS_PATH,
    DATA_PROCESSED_PATH, DATA_OUTLIERS_PATH
)

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
logger = setup_logger()

def main(data_path=DATA_RAW_PATH):
    """
    Fungsi utama untuk menjalankan pipeline end-to-end.
    """
    start_time = datetime.now()
    logger.info("="*50)
    logger.info("MEMULAI PIPELINE KLASIFIKASI CUACA")
    logger.info("="*50)
    
    paths_to_create = [
        os.path.dirname(SAVED_MODEL_PATH),
        RESULTS_PATH,
        DATA_PROCESSED_PATH,
        LOGS_PATH,
        DATA_OUTLIERS_PATH
    ]
    for path in paths_to_create:
        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"Direktori '{path}' sudah siap.")
        except OSError as e:
            logger.error(f"Gagal membuat direktori '{path}': {e}")
            return

    try:
        run_pipeline(data_path=data_path)
        logger.info("="*50)
        logger.info("PIPELINE SELESAI DENGAN SUKSES")
        logger.info(f"Model tersimpan di: {SAVED_MODEL_PATH}")
        logger.info(f"Gambar yang diproses tersimpan di: {DATA_PROCESSED_PATH}")
        logger.info(f"Hasil evaluasi tersimpan di: {RESULTS_PATH}")
        logger.info(f"File outliers tersimpan di: {DATA_OUTLIERS_PATH}")
        logger.info("="*50)

    except Exception as e:
        logger.error(f"Terjadi kesalahan fatal saat menjalankan pipeline: {e}", exc_info=True)

    end_time = datetime.now()
    logger.info(f"Total waktu eksekusi: {end_time - start_time}")

if __name__ == "__main__":
    main()