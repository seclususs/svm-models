"""Utilitas untuk membuat plot Kurva Precision-Recall.

Modul ini menyediakan fungsi untuk memvisualisasikan kinerja model
dalam hal presisi dan recall untuk setiap kelas (multi-kelas, One-vs-Rest).
"""

import os
from itertools import cycle
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, average_precision_score
from sklearn.preprocessing import label_binarize

from src.configs.config import RESULTS_PATH, CLASSES
from src.utils.logger import logger


def plot_precision_recall_curve(y_true, y_pred_proba):
    """Menghitung, memplot, dan menyimpan Kurva Precision-Recall.

    Memvisualisasikan kurva untuk setiap kelas secara individual dan juga
    kurva micro-average untuk keseluruhan kinerja.

    Args:
        y_true (array-like): Label kelas yang sebenarnya, dalam bentuk numerik.
        y_pred_proba (array-like): Probabilitas prediksi untuk setiap kelas
                                  yang dihasilkan oleh model (misal, dari
                                  `predict_proba`).
    """
    try:
        # Binarisasi label untuk pendekatan One-vs-Rest
        y_true_bin = label_binarize(y_true, classes=np.arange(len(CLASSES)))
        n_classes = y_true_bin.shape[1]

        precision = dict()
        recall = dict()
        average_precision = dict()

        # Hitung kurva dan Average Precision (AP) untuk setiap kelas
        for i in range(n_classes):
            precision[i], recall[i], _ = precision_recall_curve(y_true_bin[:, i], y_pred_proba[:, i])
            average_precision[i] = average_precision_score(y_true_bin[:, i], y_pred_proba[:, i])

        # Hitung micro-average
        precision["micro"], recall["micro"], _ = precision_recall_curve(y_true_bin.ravel(), y_pred_proba.ravel())
        average_precision["micro"] = average_precision_score(y_true_bin, y_pred_proba, average="micro")

        # Membuat plot
        plt.figure(figsize=(10, 8))
        plt.plot(recall["micro"], precision["micro"],
                 label=f'micro-average Precision-recall (AP = {average_precision["micro"]:0.2f})',
                 color='navy', linestyle=':', linewidth=4)

        colors = cycle(['aqua', 'darkorange', 'cornflowerblue', 'green'])
        for i, color in zip(range(n_classes), colors):
            plt.plot(recall[i], precision[i], color=color, lw=2,
                     label=f'Precision-recall for class {CLASSES[i]} (AP = {average_precision[i]:0.2f})')

        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Multi-class Precision-Recall Curve')
        plt.legend(loc="best")

        # Simpan plot ke file
        save_path = os.path.join(RESULTS_PATH, 'precision_recall_curve.png')
        os.makedirs(RESULTS_PATH, exist_ok=True)
        plt.savefig(save_path)
        plt.close()
        logger.info(f"Kurva Precision-Recall disimpan di: {save_path}")

    except Exception as e:
        logger.error(f"Error saat membuat plot Kurva Precision-Recall: {e}")
