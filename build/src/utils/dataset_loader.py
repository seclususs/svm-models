"""Utilitas untuk memuat dataset gambar.

Modul ini menyediakan fungsi untuk memuat gambar dari struktur direktori
di mana setiap sub-direktori mewakili sebuah kelas.
"""

import os
import cv2
import shutil
from tqdm import tqdm

from src.configs.config import CLASSES, DATA_OUTLIERS_PATH
from src.utils.logger import logger


def load_images_from_folder(folder_path):
    """Memuat semua gambar dari folder, menangani file korup.

    Fungsi ini mengiterasi sub-direktori yang sesuai dengan nama kelas yang
    didefinisikan dalam `config.CLASSES`. Gambar yang gagal dibaca atau korup
    akan dipindahkan ke direktori outliers.

    Args:
        folder_path (str): Path ke direktori utama yang berisi sub-direktori kelas.

    Returns:
        tuple: Sebuah tuple berisi tiga list:
            - images (list): List dari gambar yang dimuat (sebagai array NumPy).
            - labels (list): List dari label integer yang sesuai.
            - filenames (list): List dari nama file gambar yang dimuat.

    Raises:
        FileNotFoundError: Jika `folder_path` yang diberikan tidak ditemukan.
    """
    images = []
    labels = []
    filenames = []

    logger.info(f"Memuat gambar dari '{folder_path}'...")

    if not os.path.isdir(folder_path):
        logger.error(f"Direktori dataset tidak ditemukan di: {folder_path}")
        raise FileNotFoundError(f"Direktori dataset tidak ditemukan di: {folder_path}")

    # Iterasi melalui setiap kelas yang terdaftar di konfigurasi
    for class_label, class_name in enumerate(CLASSES):
        class_path = os.path.join(folder_path, class_name)

        # Penanganan jika nama folder menggunakan huruf kapital (misal 'Cerah' vs 'cerah')
        if not os.path.isdir(class_path):
            fallback_class_path = os.path.join(folder_path, class_name.capitalize())
            if os.path.isdir(fallback_class_path):
                class_path = fallback_class_path
            else:
                logger.warning(f"Direktori untuk kelas '{class_name}' tidak ditemukan, dilewati.")
                continue

        # Gunakan tqdm untuk menampilkan progress bar
        for filename in tqdm(os.listdir(class_path), desc=f"Loading {class_name}"):
            img_path = os.path.join(class_path, filename)
            try:
                # Baca gambar menggunakan OpenCV
                img = cv2.imread(img_path)
                if img is not None:
                    # Jika berhasil, tambahkan gambar, label, dan nama file ke list
                    images.append(img)
                    labels.append(class_label)
                    filenames.append(filename)
                else:
                    # Jika `imread` mengembalikan None, file korup atau bukan gambar
                    os.makedirs(DATA_OUTLIERS_PATH, exist_ok=True)
                    destination_path = os.path.join(DATA_OUTLIERS_PATH, filename)
                    shutil.move(img_path, destination_path)
                    logger.warning(f"Gagal membaca '{filename}'. File dipindahkan ke outliers.")
            except Exception as e:
                logger.error(f"Error saat memproses {img_path}: {e}")

    logger.info(f"Total gambar yang berhasil dimuat: {len(images)}")
    return images, labels, filenames
