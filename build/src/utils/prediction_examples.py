import numpy as np
import matplotlib.pyplot as plt
import random
import os
import cv2

from src.configs.config import RESULTS_PATH, CLASSES
from src.utils.logger import logger

def plot_prediction_examples(X_test_orig, y_test, y_pred, n_examples=5):
    """
    Memplot dan menyimpan contoh prediksi yang benar dan salah.

    Args:
        X_test_orig (array-like): Gambar uji asli (sebelum prapemrosesan, format BGR).
        y_test (array-like): Label kelas yang sebenarnya (numerik).
        y_pred (array-like): Label kelas yang diprediksi (numerik).
        n_examples (int): Jumlah contoh yang akan ditampilkan.
    """
    try:
        correct_indices = np.where(y_pred == y_test)[0]
        incorrect_indices = np.where(y_pred != y_test)[0]

        # Plot contoh prediksi yang benar
        if len(correct_indices) > 0:
            plt.figure(figsize=(15, 5))
            plt.suptitle("Contoh Prediksi yang Benar", fontsize=16)
            random_indices = random.sample(list(correct_indices), min(n_examples, len(correct_indices)))
            
            for i, idx in enumerate(random_indices):
                plt.subplot(1, n_examples, i + 1)
                img_rgb = cv2.cvtColor(X_test_orig[idx], cv2.COLOR_BGR2RGB)
                plt.imshow(img_rgb)
                plt.title(f"Prediksi: {CLASSES[y_pred[idx]]}\nAsli: {CLASSES[y_test[idx]]}")
                plt.axis('off')
            
            save_path = os.path.join(RESULTS_PATH, 'correct_predictions.png')
            os.makedirs(RESULTS_PATH, exist_ok=True)
            plt.tight_layout(rect=[0, 0, 1, 0.95])
            plt.savefig(save_path)
            plt.close()
            logger.info(f"Correct prediction examples saved to: {save_path}")

        # Plot contoh prediksi yang salah
        if len(incorrect_indices) > 0:
            plt.figure(figsize=(15, 5))
            plt.suptitle("Contoh Prediksi yang Salah", fontsize=16)
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
            logger.info(f"Incorrect prediction examples saved to: {save_path}")
        else:
            logger.info("Tidak ada prediksi salah untuk diplot.")
            
    except Exception as e:
        logger.error(f"Error plotting prediction examples: {e}")
