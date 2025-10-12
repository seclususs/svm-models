"""Modul untuk ekstraksi fitur dari gambar.

Berisi kumpulan fungsi untuk mengekstrak berbagai jenis fitur visual,
seperti HOG, histogram warna, LBP, GLCM, Gabor, Sobel, dan color moments.
"""

import numpy as np
import cv2
from skimage.feature import hog, local_binary_pattern, graycomatrix, graycoprops
from scipy.stats import skew

from src.configs.config import HOG_ORIENTATIONS, HOG_PIXELS_PER_CELL, HOG_CELLS_PER_BLOCK


def extract_hog_features(gray_image):
    """Mengekstrak fitur Histogram of Oriented Gradients (HOG).

    Args:
        gray_image (np.ndarray): Gambar input dalam format grayscale dan tipe float.

    Returns:
        np.ndarray: Vektor fitur HOG 1D.
    """
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
    """Mengekstrak histogram warna dari ruang warna HSV.

    Args:
        color_image (np.ndarray): Gambar input berwarna (BGR) yang sudah
                                  dinormalisasi ke rentang [0, 1].

    Returns:
        np.ndarray: Vektor fitur histogram warna 1D.
    """
    hsv_image = cv2.cvtColor((color_image * 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
    hist_h = cv2.calcHist([hsv_image], [0], None, [180], [0, 180])
    hist_s = cv2.calcHist([hsv_image], [1], None, [32], [0, 256])
    hist_v = cv2.calcHist([hsv_image], [2], None, [32], [0, 256])
    cv2.normalize(hist_h, hist_h)
    cv2.normalize(hist_s, hist_s)
    cv2.normalize(hist_v, hist_v)
    return np.concatenate((hist_h, hist_s, hist_v)).flatten()


def extract_lbp_features(gray_image):
    """Mengekstrak fitur tekstur Local Binary Patterns (LBP).

    Args:
        gray_image (np.ndarray): Gambar input grayscale yang sudah
                                  dinormalisasi ke rentang [0, 1].

    Returns:
        np.ndarray: Vektor fitur histogram LBP 1D.
    """
    gray_image_uint8 = (gray_image * 255).astype(np.uint8)
    radius = 8
    n_points = 24
    lbp = local_binary_pattern(gray_image_uint8, n_points, radius, method='uniform')
    (hist, _) = np.histogram(lbp.ravel(),
                             bins=np.arange(0, n_points + 3),
                             range=(0, n_points + 2))
    hist = hist.astype("float")
    hist /= (hist.sum() + 1e-6)
    return hist


def extract_color_moments(color_image):
    """Mengekstrak color moments (mean, std, skewness) dari ruang warna Lab.

    Args:
        color_image (np.ndarray): Gambar input berwarna (BGR) yang sudah
                                  dinormalisasi ke rentang [0, 1].

    Returns:
        np.ndarray: Vektor fitur color moments 1D (9 nilai).
    """
    lab_image = cv2.cvtColor((color_image * 255).astype(np.uint8), cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(lab_image)
    features = []
    for channel in [l, a, b]:
        mean = np.mean(channel)
        std = np.std(channel)
        skewness = skew(channel.flatten())
        features.extend([mean, std, skewness])
    return np.array(features)


def extract_glcm_features(gray_image):
    """Mengekstrak fitur tekstur dari Gray-Level Co-occurrence Matrix (GLCM).

    Args:
        gray_image (np.ndarray): Gambar input grayscale yang sudah
                                  dinormalisasi ke rentang [0, 1].

    Returns:
        np.ndarray: Vektor fitur properti GLCM 1D.
    """
    gray_image_uint8 = (gray_image * 255).astype(np.uint8)
    distances = [1, 3, 5]
    angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
    glcm = graycomatrix(gray_image_uint8, distances=distances, angles=angles, symmetric=True, normed=True)
    features = []
    props = ['contrast', 'dissimilarity', 'homogeneity', 'energy', 'correlation', 'ASM']
    for prop in props:
        features.append(graycoprops(glcm, prop).ravel())
    return np.concatenate(features)


def extract_gabor_features(gray_image):
    """Mengekstrak fitur tekstur menggunakan bank filter Gabor.

    Args:
        gray_image (np.ndarray): Gambar input grayscale yang sudah
                                  dinormalisasi ke rentang [0, 1].

    Returns:
        np.ndarray: Vektor fitur Gabor 1D (mean dan std dari respons filter).
    """
    img = (gray_image * 255).astype(np.uint8)
    filters = []
    ksize = 31
    for theta in np.arange(0, np.pi, np.pi / 4):
        for lambd in np.arange(np.pi / 4, np.pi, np.pi / 4):
            for sigma in (1, 3):
                kernel = cv2.getGaborKernel((ksize, ksize), sigma, theta, lambd, 0.5, 0, ktype=cv2.CV_32F)
                filters.append(kernel)
    features = []
    for kernel in filters:
        filtered_img = cv2.filter2D(img, cv2.CV_8UC3, kernel)
        features.append(filtered_img.mean())
        features.append(filtered_img.std())
    return np.array(features)


def extract_sobel_features(gray_image):
    """Mengekstrak fitur tepi berdasarkan histogram magnitudo Sobel.

    Args:
        gray_image (np.ndarray): Gambar input grayscale yang sudah
                                  dinormalisasi ke rentang [0, 1].

    Returns:
        np.ndarray: Vektor fitur histogram magnitudo Sobel 1D.
    """
    img_uint8 = (gray_image * 255).astype(np.uint8)
    sobelx = cv2.Sobel(img_uint8, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(img_uint8, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx**2 + sobely**2)
    (hist, _) = np.histogram(magnitude.ravel(), bins=32, range=(0, 256))
    hist = hist.astype("float")
    hist /= (hist.sum() + 1e-6)
    return hist


def extract_features(gray_image, color_image):
    """Mengekstrak dan menggabungkan semua fitur menjadi satu vektor.

    Args:
        gray_image (np.ndarray): Gambar input grayscale ternormalisasi.
        color_image (np.ndarray): Gambar input berwarna (BGR) ternormalisasi.

    Returns:
        np.ndarray: Vektor fitur gabungan 1D yang komprehensif.
    """
    hog_features = extract_hog_features(gray_image)
    color_hist_features = extract_color_histogram(color_image)
    lbp_features = extract_lbp_features(gray_image)
    gabor_features = extract_gabor_features(gray_image)
    sobel_features = extract_sobel_features(gray_image)
    glcm_features = extract_glcm_features(gray_image)
    color_moments = extract_color_moments(color_image)

    # Menggabungkan semua vektor fitur menjadi satu
    combined_features = np.hstack([
        hog_features, color_hist_features, lbp_features, gabor_features,
        sobel_features, glcm_features, color_moments
    ])
    return combined_features
