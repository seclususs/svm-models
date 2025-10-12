"""Utilitas untuk membuat plot Kurva ROC (Receiver Operating Characteristic).

Modul ini menyediakan fungsi untuk memvisualisasikan trade-off antara
True Positive Rate (TPR) dan False Positive Rate (FPR) untuk setiap kelas.
"""

import os
from itertools import cycle
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize

from src.configs.config import RESULTS_PATH, CLASSES
from src.utils.logger import logger


def plot_roc_curve(y_true, y_pred_proba):
    """Menghitung, memplot, dan menyimpan Kurva ROC untuk multi-kelas.

    Fungsi ini menggunakan pendekatan One-vs-Rest (OvR) untuk setiap kelas
    dan juga menghitung serta memplot kurva micro-average.

    Args:
        y_true (array-like): Label kelas yang sebenarnya, dalam bentuk numerik.
        y_pred_proba (array-like): Probabilitas prediksi untuk setiap kelas
                                  dari model (misal, dari `predict_proba`).
    """
    try:
        # Binarisasi label untuk pendekatan One-vs-Rest
        y_true_bin = label_binarize(y_true, classes=np.arange(len(CLASSES)))
        n_classes = y_true_bin.shape[1]

        fpr = dict()
        tpr = dict()
        roc_auc = dict()

        # Hitung kurva ROC dan area AUC untuk setiap kelas
        for i in range(n_classes):
            fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_pred_proba[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])

        # Hitung micro-average ROC dan AUC
        fpr["micro"], tpr["micro"], _ = roc_curve(y_true_bin.ravel(), y_pred_proba.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

        # Membuat plot
        plt.figure(figsize=(10, 8))
        plt.plot(fpr["micro"], tpr["micro"],
                 label=f'micro-average ROC curve (area = {roc_auc["micro"]:0.2f})',
                 color='deeppink', linestyle=':', linewidth=4)

        colors = cycle(['aqua', 'darkorange', 'cornflowerblue', 'green'])
        for i, color in zip(range(n_classes), colors):
            plt.plot(fpr[i], tpr[i], color=color, lw=2,
                     label=f'ROC curve of class {CLASSES[i]} (area = {roc_auc[i]:0.2f})')

        # Garis referensi untuk tebakan acak
        plt.plot([0, 1], [0, 1], 'k--', lw=2)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Multi-class Receiver Operating Characteristic (ROC) Curve')
        plt.legend(loc="lower right")

        # Simpan plot ke file
        save_path = os.path.join(RESULTS_PATH, 'roc_curve.png')
        os.makedirs(RESULTS_PATH, exist_ok=True)
        plt.savefig(save_path)
        plt.close()
        logger.info(f"Kurva ROC disimpan di: {save_path}")

    except Exception as e:
        logger.error(f"Error saat membuat plot Kurva ROC: {e}")
