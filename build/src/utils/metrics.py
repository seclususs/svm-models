import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from src.configs.config import RESULTS_PATH, CLASSES
from src.utils.logger import logger

def evaluate_model(y_true, y_pred):
    """
    Menghitung dan mencatat metrik evaluasi.
    """
    try:
        accuracy = accuracy_score(y_true, y_pred)
        report = classification_report(y_true, y_pred, target_names=CLASSES)
        
        logger.info(f"\nAkurasi Keseluruhan: {accuracy:.4f}\n")
        logger.info("Laporan Klasifikasi:\n" + report)
        
        report_path = os.path.join(RESULTS_PATH, 'classification_report.txt')
        with open(report_path, 'w') as f:
            f.write(f"Akurasi Keseluruhan: {accuracy:.4f}\n\n")
            f.write("Laporan Klasifikasi:\n")
            f.write(report)
        logger.info(f"Laporan klasifikasi disimpan di: {report_path}")
            
    except Exception as e:
        logger.error(f"Gagal mengevaluasi model: {e}")

def plot_confusion_matrix(y_true, y_pred):
    """
    Membuat plot confusion matrix.
    """
    try:
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=CLASSES, yticklabels=CLASSES)
        plt.title('Confusion Matrix')
        plt.ylabel('Label Sebenarnya')
        plt.xlabel('Label Prediksi')
        
        plot_path = os.path.join(RESULTS_PATH, 'confusion_matrix.png')
        plt.savefig(plot_path)
        logger.info(f"Confusion matrix disimpan di: {plot_path}")
        plt.close()
    except Exception as e:
        logger.error(f"Gagal membuat plot confusion matrix: {e}")
