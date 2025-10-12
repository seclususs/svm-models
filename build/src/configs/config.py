"""Konfigurasi utama.

File ini berisi semua variabel global dan parameter konfigurasi yang digunakan
di seluruh proyek, seperti path direktori, parameter prapemrosesan gambar,
pengaturan pelatihan model, dan nama kelas dataset.
"""

import os

# =============================================================================
# DEFINISI PATH DIREKTORI
# =============================================================================
# Menentukan path dasar proyek (satu level di atas direktori 'src')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Path untuk data
DATA_RAW_PATH = os.path.join(BASE_DIR, 'data', 'raw')
ANOMALY_DATA_PATH = os.path.join(BASE_DIR, 'data', 'anomaly')
DATA_PROCESSED_PATH = os.path.join(BASE_DIR, 'data', 'processed')
DATA_OUTLIERS_PATH = os.path.join(BASE_DIR, 'data', 'outliers')

# Path untuk model dan hasil eksperimen
SAVED_MODEL_PATH = os.path.join(BASE_DIR, 'saved_models', 'svm_model.pkl')
LOGS_PATH = os.path.join(BASE_DIR, 'experiments', 'logs')
RESULTS_PATH = os.path.join(BASE_DIR, 'experiments', 'results')


# =============================================================================
# PENGATURAN PRAPEMROSESAN GAMBAR
# =============================================================================
IMAGE_SIZE = (128, 128)  # Ukuran gambar standar (lebar, tinggi)


# =============================================================================
# PENGATURAN EKSTRAKSI FITUR (HOG)
# =============================================================================
HOG_ORIENTATIONS = 9          # Jumlah bins orientasi gradien
HOG_PIXELS_PER_CELL = (8, 8)  # Ukuran sel dalam piksel
HOG_CELLS_PER_BLOCK = (2, 2)  # Jumlah sel dalam satu blok


# =============================================================================
# PENGATURAN PELATIHAN MODEL
# =============================================================================
TEST_SIZE = 0.2     # Proporsi dataset yang akan digunakan sebagai data uji
RANDOM_STATE = 42   # Seed untuk reproduktifitas


# =============================================================================
# KELAS DATASET
# =============================================================================
# Daftar nama kelas sesuai dengan urutan label numerik (0, 1, 2, 3)
CLASSES = ["Berawan", "Hujan", "Cerah", "Berkabut"]
