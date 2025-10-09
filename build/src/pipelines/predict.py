import os
import sys
import cv2
import warnings

from src.configs.config import CLASSES
from src.models.svm_classifier import load_model
from src.preprocessing.image_preprocessing import preprocess_image_for_feature_extraction
from src.features.feature_extraction import extract_features
from src.utils.logger import logger

warnings.filterwarnings('ignore', category=UserWarning)
sys.path.append(os.path.dirname(__file__))

def predict_single_image(image_path, model):
    """
    Melakukan prediksi pada satu gambar.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Tidak dapat membaca gambar di {image_path}")
            return None, None

        # Preprocessing (tanpa menyimpan, hanya untuk prediksi)
        # Ambil _ karena kita tidak butuh gambar uint8 di sini
        gray_img, color_img, _ = preprocess_image_for_feature_extraction(image)

        # Ekstraksi Fitur
        features = extract_features(gray_img, color_img)
        features = features.reshape(1, -1)

        # Prediksi
        prediction_idx = model.predict(features)[0]
        predicted_class = CLASSES[prediction_idx]

        # Dapatkan probabilitas
        probabilities = model.predict_proba(features)[0]
        confidence = probabilities[prediction_idx]

        return predicted_class, confidence

    except Exception as e:
        logger.error(f"Error saat memprediksi {image_path}: {e}", exc_info=True)
        return None, None

def main():
    """
    Fungsi utama untuk memuat model dan memproses gambar.
    """
    logger.info("--- Memulai Sesi Prediksi Cuaca ---")

    try:
        model = load_model()
    except FileNotFoundError:
        logger.error("File model 'svm_model.pkl' tidak ditemukan. Pastikan pipeline training (run.py) sudah dijalankan.")
        return

    if len(sys.argv) < 2:
        logger.warning("Penggunaan: python predict.py <path_ke_gambar_atau_folder>")
        return

    input_path = sys.argv[1]

    if os.path.isfile(input_path):
        logger.info(f"Memproses file tunggal: {input_path}")
        predicted_class, confidence = predict_single_image(input_path, model)
        if predicted_class:
            logger.info(f"-> Prediksi: {predicted_class} (Kepercayaan: {confidence:.2%})")

    elif os.path.isdir(input_path):
        logger.info(f"Memproses semua gambar di folder: {input_path}")
        image_files = [f for f in os.listdir(input_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not image_files:
            logger.warning("Tidak ada file gambar yang ditemukan di folder ini.")
            return
            
        for filename in image_files:
            image_path = os.path.join(input_path, filename)
            logger.info(f"--- Memproses: {filename} ---")
            predicted_class, confidence = predict_single_image(image_path, model)
            if predicted_class:
                logger.info(f"-> Prediksi: {predicted_class} (Kepercayaan: {confidence:.2%})")

    else:
        logger.error(f"Path tidak valid: {input_path}")

if __name__ == "__main__":
    main()
