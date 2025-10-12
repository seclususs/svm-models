"""Utilitas untuk evaluasi kinerja model.

Modul ini menyediakan fungsi untuk menghitung metrik klasifikasi standar
dan untuk memvisualisasikan confusion matrix.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from src.configs.config import RESULTS_PATH, CLASSES
from src.utils.logger import logger


def evaluate_model(y_true, y_pred):
    """Menghitung, mencatat, dan menyimpan metrik evaluasi model.

    Fungsi ini menghasilkan laporan klasifikasi (precision, recall, f1-score)
    dan akurasi, lalu menyimpannya ke file teks.

    Args:
        y_true (array-like): Label kelas yang sebenarnya (ground truth).
        y_pred (array-like): Label kelas yang diprediksi oleh model.
    """
    try:
        # Hitung akurasi dan laporan klasifikasi
        accuracy = accuracy_score(y_true, y_pred)
        report = classification_report(y_true, y_pred, target_names=CLASSES)

        # Catat metrik ke logger
        logger.info(f"\nAkurasi Keseluruhan: {accuracy:.4f}\n")
        logger.info("Laporan Klasifikasi:\n" + report)

        # Simpan laporan ke file
        report_path = os.path.join(RESULTS_PATH, 'classification_report.txt')
        os.makedirs(RESULTS_PATH, exist_ok=True)
        with open(report_path, 'w') as f:
            f.write(f"Akurasi Keseluruhan: {accuracy:.4f}\n\n")
            f.write("Laporan Klasifikasi:\n")
            f.write(report)
        logger.info(f"Laporan klasifikasi disimpan di: {report_path}")

    except Exception as e:
        logger.error(f"Gagal mengevaluasi model: {e}")


def plot_confusion_matrix(y_true, y_pred):
    """Membuat dan menyimpan plot confusion matrix.

    Args:
        y_true (array-like): Label kelas yang sebenarnya (ground truth).
        y_pred (array-like): Label kelas yang diprediksi oleh model.
    """
    try:
        # Hitung confusion matrix
        cm = confusion_matrix(y_true, y_pred)

        # Buat plot menggunakan Matplotlib dan Seaborn
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=CLASSES, yticklabels=CLASSES)
        plt.title('Confusion Matrix')
        plt.ylabel('Label Sebenarnya')
        plt.xlabel('Label Prediksi')

        # Simpan plot sebagai file gambar
        plot_path = os.path.join(RESULTS_PATH, 'confusion_matrix.png')
        os.makedirs(RESULTS_PATH, exist_ok=True)
        plt.savefig(plot_path)
        logger.info(f"Confusion matrix disimpan di: {plot_path}")
        plt.close()  # Tutup plot agar tidak ditampilkan di notebook/konsol

    except Exception as e:
        logger.error(f"Gagal membuat plot confusion matrix: {e}")
