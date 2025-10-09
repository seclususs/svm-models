import os
import cv2
import random
import numpy as np
from tqdm import tqdm
import shutil

from src.configs.config import CLASSES, DATA_OUTLIERS_PATH
from src.utils.logger import logger

def augment_image(image):
    """
    Menerapkan augmentasi pada setiap gambar.
    """
    augmented_images = [image]

    # Flip Horizontal
    flipped_h = cv2.flip(image, 1)
    augmented_images.append(flipped_h)

    # Perubahan Kecerahan
    brighter = np.clip(image * 1.2, 0, 255).astype(np.uint8)
    darker = np.clip(image * 0.8, 0, 255).astype(np.uint8)
    # augmented_images.append(brighter)
    # augmented_images.append(darker)

    # Rotasi Acak antara -15 dan 15 derajat
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    angle = random.uniform(-15, 15)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h))
    augmented_images.append(rotated)

    return augmented_images

def load_images_from_folder(folder_path):
    """
    Memuat semua gambar dan labelnya dari folder, serta memindahkan file yang korup.
    """
    images = []
    labels = []
    filenames = []
    
    logger.info(f"Memuat gambar asli dari '{folder_path}'...")
    
    if not os.path.isdir(folder_path):
        logger.error(f"Direktori dataset tidak ditemukan di: {folder_path}")
        raise FileNotFoundError(f"Direktori dataset tidak ditemukan di: {folder_path}")

    for class_label, class_name in enumerate(CLASSES):
        class_path = os.path.join(folder_path, class_name)
        if not os.path.isdir(class_path):
            fallback_class_path = os.path.join(folder_path, class_name.capitalize())
            if os.path.isdir(fallback_class_path):
                class_path = fallback_class_path
            else:
                logger.warning(f"Direktori untuk kelas '{class_name}' tidak ditemukan, dilewati.")
                continue
            
        for filename in tqdm(os.listdir(class_path), desc=f"Loading {class_name}"):
            img_path = os.path.join(class_path, filename)
            try:
                img = cv2.imread(img_path)
                if img is not None:
                    images.append(img)
                    labels.append(class_label)
                    filenames.append(filename)
                else:
                    destination_path = os.path.join(DATA_OUTLIERS_PATH, filename)
                    shutil.move(img_path, destination_path)
                    logger.warning(f"Gagal membaca gambar '{filename}'. File dipindahkan ke direktori outliers.")
            except Exception as e:
                logger.error(f"Error saat memproses gambar {img_path}: {e}")
                
    logger.info(f"Total gambar asli yang berhasil dimuat: {len(images)}")
    return images, labels, filenames