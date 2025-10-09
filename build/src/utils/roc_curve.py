import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize
from itertools import cycle
import os

from src.configs.config import RESULTS_PATH, CLASSES
from src.utils.logger import logger

def plot_roc_curve(y_true, y_pred_proba):
    """
    Menghitung dan memplot Kurva ROC untuk setiap kelas (One-vs-Rest) dan
    menyimpan plot sebagai file gambar.

    Args:
        y_true (array-like): Label kelas yang sebenarnya, dalam bentuk numerik (misal: 0, 1, 2, 3).
        y_pred_proba (array-like): Probabilitas prediksi untuk setiap kelas dari model.
    """
    try:
        # Binarisasi label ground truth
        y_true_bin = label_binarize(y_true, classes=np.arange(len(CLASSES)))
        n_classes = y_true_bin.shape[1]

        # Inisialisasi dictionary untuk menyimpan nilai FPR, TPR, dan AUC
        fpr = dict()
        tpr = dict()
        roc_auc = dict()

        # Hitung kurva ROC dan area AUC untuk setiap kelas
        for i in range(n_classes):
            fpr[i], tpr[i], _ = roc_curve(y_true_bin[:, i], y_pred_proba[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])

        # Hitung micro-average ROC curve dan area AUC
        fpr["micro"], tpr["micro"], _ = roc_curve(y_true_bin.ravel(), y_pred_proba.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

        # Mulai plotting
        plt.figure(figsize=(10, 8))
        
        # Plot kurva ROC micro-average
        plt.plot(fpr["micro"], tpr["micro"],
                 label=f'micro-average ROC curve (area = {roc_auc["micro"]:0.2f})',
                 color='deeppink', linestyle=':', linewidth=4)

        # Plot kurva ROC untuk setiap kelas
        colors = cycle(['aqua', 'darkorange', 'cornflowerblue', 'green'])
        for i, color in zip(range(n_classes), colors):
            plt.plot(fpr[i], tpr[i], color=color, lw=2,
                     label=f'ROC curve of class {CLASSES[i]} (area = {roc_auc[i]:0.2f})')

        # Plot garis diagonal (random guess)
        plt.plot([0, 1], [0, 1], 'k--', lw=2)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC) Curve')
        plt.legend(loc="lower right")
        
        save_path = os.path.join(RESULTS_PATH, 'roc_curve.png')
        os.makedirs(RESULTS_PATH, exist_ok=True)
        plt.savefig(save_path)
        plt.close()
        logger.info(f"ROC curve saved to: {save_path}")

    except Exception as e:
        logger.error(f"Error plotting ROC curve: {e}")
