"""Utilitas untuk memvisualisasikan contoh-contoh hasil prediksi.

Modul ini menyediakan fungsi untuk menampilkan gambar-gambar dari set data uji
yang diprediksi dengan benar dan yang salah oleh model.
"""

import os
import random
import numpy as np
import matplotlib.pyplot as plt
import cv2

from src.configs.config import RESULTS_PATH, CLASSES
from src.utils.logger import logger


def plot_prediction_examples(X_test_orig, y_test, y_pred, n_examples=5):
    """Memplot dan menyimpan contoh prediksi yang benar dan salah.

    Args:
        X_test_orig (array-like): Gambar uji asli (sebelum prapemrosesan,
                                    dalam format BGR dari OpenCV).
        y_test (array-like): Label kelas yang sebenarnya (numerik).
        y_pred (array-like): Label kelas yang diprediksi oleh model (numerik).
        n_examples (int): Jumlah contoh yang akan ditampilkan untuk setiap
                          kategori (benar dan salah).
    """
    try:
        # Cari indeks untuk prediksi yang benar dan salah
        correct_indices = np.where(y_pred == y_test)[0]
        incorrect_indices = np.where(y_pred != y_test)[0]

        # Plot contoh prediksi yang BENAR
        if len(correct_indices) > 0:
            plt.figure(figsize=(15, 5))
            plt.suptitle("Contoh Prediksi yang Benar", fontsize=16)
            # Pilih N contoh secara acak dari indeks yang benar
            random_indices = random.sample(list(correct_indices), min(n_examples, len(correct_indices)))

            for i, idx in enumerate(random_indices):
                plt.subplot(1, n_examples, i + 1)
                # Konversi gambar dari BGR ke RGB untuk Matplotlib
                img_rgb = cv2.cvtColor(X_test_orig[idx], cv2.COLOR_BGR2RGB)
                plt.imshow(img_rgb)
                plt.title(f"Prediksi: {CLASSES[y_pred[idx]]}\nAsli: {CLASSES[y_test[idx]]}")
                plt.axis('off')

            save_path = os.path.join(RESULTS_PATH, 'correct_predictions.png')
            os.makedirs(RESULTS_PATH, exist_ok=True)
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            plt.savefig(save_path)
            plt.close()
            logger.info(f"Contoh prediksi benar disimpan di: {save_path}")

        # Plot contoh prediksi yang SALAH
        if len(incorrect_indices) > 0:
            plt.figure(figsize=(15, 5))
            plt.suptitle("Contoh Prediksi yang Salah", fontsize=16)
            # Pilih N contoh secara acak dari indeks yang salah
            random_indices = random.sample(list(incorrect_indices), min(n_examples, len(incorrect_indices)))

            for i, idx in enumerate(random_indices):
                plt.subplot(1, n_examples, i + 1)
                img_rgb = cv2.cvtColor(X_test_orig[idx], cv2.COLOR_BGR2RGB)
                plt.imshow(img_rgb)
                plt.title(f"Prediksi: {CLASSES[y_pred[idx]]}\nAsli: {CLASSES[y_test[idx]]}")
                plt.axis('off')

            save_path = os.path.join(RESULTS_PATH, 'incorrect_predictions.png')
            os.makedirs(RESULTS_PATH, exist_ok=True)
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            plt.savefig(save_path)
            plt.close()
            logger.info(f"Contoh prediksi salah disimpan di: {save_path}")
        else:
            logger.info("Tidak ada prediksi salah untuk diplot.")

    except Exception as e:
        logger.error(f"Error saat membuat plot contoh prediksi: {e}")
