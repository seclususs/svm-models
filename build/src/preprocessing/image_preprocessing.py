"""Modul untuk fungsi-fungsi prapemrosesan gambar dasar.

Menyediakan utilitas untuk mengubah ukuran, mengonversi ke grayscale,
dan menormalisasi gambar.
"""

import cv2
from src.configs.config import IMAGE_SIZE


def resize_image(image):
    """Mengubah ukuran gambar ke ukuran standar yang ditentukan di config.

    Args:
        image (np.ndarray): Gambar input (berwarna atau grayscale).

    Returns:
        np.ndarray: Gambar yang ukurannya telah diubah.
    """
    return cv2.resize(image, IMAGE_SIZE, interpolation=cv2.INTER_AREA)


def to_grayscale(image):
    """Mengonversi gambar berwarna (BGR) menjadi grayscale.

    Args:
        image (np.ndarray): Gambar input berwarna dalam format BGR.

    Returns:
        np.ndarray: Gambar dalam format grayscale.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def normalize_image(image):
    """Menormalisasi nilai piksel gambar ke rentang float [0.0, 1.0].

    Args:
        image (np.ndarray): Gambar input (berwarna atau grayscale).

    Returns:
        np.ndarray: Gambar dengan nilai piksel yang dinormalisasi (tipe float32).
    """
    return image.astype('float32') / 255.0


def preprocess_image_for_feature_extraction(image):
    """Menjalankan pipeline prapemrosesan lengkap untuk satu gambar.

    Langkah-langkahnya meliputi: resize, konversi ke grayscale, dan normalisasi.

    Args:
        image (np.ndarray): Gambar input asli dalam format BGR.

    Returns:
        tuple: Sebuah tuple berisi:
            - normalized_gray (np.ndarray): Gambar grayscale ternormalisasi.
            - normalized_color (np.ndarray): Gambar berwarna ternormalisasi.
            - resized_color_uint8 (np.ndarray): Gambar berwarna setelah resize
                                                (tipe uint8).
    """
    # Resize gambar asli (berwarna)
    resized_color_uint8 = resize_image(image)

    # Konversi ke grayscale
    gray_image = to_grayscale(resized_color_uint8)

    # Normalisasi keduanya untuk ekstraksi fitur
    normalized_gray = normalize_image(gray_image)
    normalized_color = normalize_image(resized_color_uint8)

    # Kembalikan semua versi yang mungkin berguna
    return normalized_gray, normalized_color, resized_color_uint8
