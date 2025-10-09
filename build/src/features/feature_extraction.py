import numpy as np
import cv2
from skimage.feature import hog, local_binary_pattern
from src.configs.config import HOG_ORIENTATIONS, HOG_PIXELS_PER_CELL, HOG_CELLS_PER_BLOCK

def extract_hog_features(gray_image):
    """
    Mengekstrak fitur HOG dari gambar grayscale.
    """
    gray_image = gray_image.astype(np.float32)
    features = hog(
        gray_image,
        orientations=HOG_ORIENTATIONS,
        pixels_per_cell=HOG_PIXELS_PER_CELL,
        cells_per_block=HOG_CELLS_PER_BLOCK,
        block_norm='L2-Hys',
        visualize=False,
        transform_sqrt=True
    )
    return features

def extract_color_histogram(color_image):
    """
    Mengekstrak histogram warna dari gambar berwarna menggunakan ruang warna HSV.
    Gambar diasumsikan sudah dinormalisasi [0, 1] dan BGR.
    """
    # Konversi gambar dari BGR ke HSV
    hsv_image = cv2.cvtColor((color_image * 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
    
    # Menghitung histogram untuk setiap channel
    hist_h = cv2.calcHist([hsv_image], [0], None, [180], [0, 180]) # Hue
    hist_s = cv2.calcHist([hsv_image], [1], None, [32], [0, 256])  # Saturation (32 bins)
    hist_v = cv2.calcHist([hsv_image], [2], None, [32], [0, 256])  # Value (32 bins)
    
    # Normalisasi histogram
    cv2.normalize(hist_h, hist_h)
    cv2.normalize(hist_s, hist_s)
    cv2.normalize(hist_v, hist_v)

    # Menggabungkan histogram dan meratakannya menjadi satu vektor
    hist = np.concatenate((hist_h, hist_s, hist_v)).flatten()
    return hist

def extract_lbp_features(gray_image):
    """
    Mengekstrak fitur tekstur menggunakan Local Binary Patterns (LBP).
    """
    gray_image_uint8 = (gray_image * 255).astype(np.uint8)
    
    # Parameter LBP: 24 tetangga, radius 8. Umum digunakan.
    radius = 8
    n_points = 24 
    lbp = local_binary_pattern(gray_image_uint8, n_points, radius, method='uniform')
    
    # Hitung histogram dari hasil LBP
    # Jumlah bin adalah n_points + 2
    (hist, _) = np.histogram(lbp.ravel(),
                             bins=np.arange(0, n_points + 3),
                             range=(0, n_points + 2))
    
    # Normalisasi histogram
    hist = hist.astype("float")
    hist /= (hist.sum() + 1e-6) # Tambahkan epsilon untuk menghindari pembagian dengan nol
    
    return hist

def extract_gabor_features(gray_image):
    """
    Mengekstrak fitur tekstur menggunakan Gabor Filters.
    """
    img = (gray_image * 255).astype(np.uint8)
    filters = []
    ksize = 31 # Ukuran kernel Gabor
    # Menentukan parameter untuk bank filter Gabor
    for theta in np.arange(0, np.pi, np.pi / 4): # 4 orientasi
        for lambd in np.arange(np.pi / 4, np.pi, np.pi / 4): # 3 panjang gelombang
            for sigma in (1, 3): # 2 standar deviasi
                kernel = cv2.getGaborKernel((ksize, ksize), sigma, theta, lambd, 0.5, 0, ktype=cv2.CV_32F)
                filters.append(kernel)

    features = []
    # Terapkan setiap filter ke gambar
    for kernel in filters:
        filtered_img = cv2.filter2D(img, cv2.CV_8UC3, kernel)
        # Ekstrak statistik (rata-rata dan standar deviasi) sebagai fitur
        features.append(filtered_img.mean())
        features.append(filtered_img.std())
    
    return np.array(features)

def extract_features(gray_image, color_image):
    """
    Menggabungkan fitur.
    """
    hog_features = extract_hog_features(gray_image)
    color_hist_features = extract_color_histogram(color_image)
    lbp_features = extract_lbp_features(gray_image)
    gabor_features = extract_gabor_features(gray_image)
    
    # Menggabungkan semua vektor fitur menjadi satu vektor besar
    combined_features = np.hstack([hog_features, color_hist_features, lbp_features, gabor_features])
    return combined_features
