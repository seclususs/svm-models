import os
import cv2
import numpy as np
from tqdm import tqdm
from sklearn.model_selection import train_test_split

from src.configs.config import TEST_SIZE, RANDOM_STATE, DATA_PROCESSED_PATH, CLASSES
from src.utils.dataset_loader import load_images_from_folder, augment_image
from src.preprocessing.image_preprocessing import preprocess_image_for_feature_extraction
from src.features.feature_extraction import extract_features
from src.models.svm_classifier import tune_and_train_model, save_model
from src.utils.metrics import evaluate_model, plot_confusion_matrix
from src.utils.logger import logger

def run_pipeline(data_path):
    """
    Menjalankan seluruh alur kerja dengan urutan:
    1. Load Data Asli
    2. Split Data (Train-Test)
    3. Augmentasi HANYA pada data training
    4. Preprocess & Ekstraksi Fitur
    5. Train & Evaluate Model
    """
    
    logger.info("Langkah 1: Memuat data gambar asli...")
    images, labels, _ = load_images_from_folder(data_path)
    if not images:
        logger.warning("Tidak ada gambar untuk diproses. Pipeline berhenti.")
        return
    
    logger.info("Langkah 2: Membagi data menjadi set training dan test...")
    X_train_img, X_test_img, y_train, y_test = train_test_split(
        images, labels, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=labels
    )

    logger.info(f"Data asli dibagi: {len(X_train_img)} train, {len(X_test_img)} test.")
    logger.info("Langkah 3: Menerapkan augmentasi HANYA pada set training...")
    train_images_aug = []
    train_labels_aug = []
    for img, label in tqdm(zip(X_train_img, y_train), total=len(X_train_img), desc="Augmenting train data"):
        augmented_imgs = augment_image(img)
        for aug_img in augmented_imgs:
            train_images_aug.append(aug_img)
            train_labels_aug.append(label)
    logger.info(f"Ukuran set training setelah augmentasi: {len(train_images_aug)} gambar.")
    logger.info("Langkah 4: Prapemrosesan dan ekstraksi fitur...")
    
    def process_and_extract(image_set, desc):
        """Fungsi helper untuk prapemrosesan dan ekstraksi fitur."""
        feature_list = []
        for image in tqdm(image_set, desc=desc):
            gray_img, color_img, _ = preprocess_image_for_feature_extraction(image)
            features = extract_features(gray_img, color_img)
            feature_list.append(features)
        return np.array(feature_list)
    
    X_train = process_and_extract(train_images_aug, "Processing augmented train data")
    y_train = np.array(train_labels_aug)

    X_test = process_and_extract(X_test_img, "Processing test data")
    y_test = np.array(y_test)
    
    logger.info(f"Ekstraksi fitur selesai. Bentuk matriks fitur: Train {X_train.shape}, Test {X_test.shape}")
    
    logger.info("Langkah 5: Melatih model...")
    model = tune_and_train_model(X_train, y_train)
    
    logger.info("Langkah 6: Menyimpan model...")
    save_model(model)
    
    logger.info("Langkah 7: Mengevaluasi model pada data test...")
    y_pred = model.predict(X_test)
    
    evaluate_model(y_test, y_pred)
    plot_confusion_matrix(y_test, y_pred)