import numpy as np
import cv2
import random
from scipy.stats import skew
from skimage.feature import hog, local_binary_pattern, graycomatrix, graycoprops
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.svm import SVC


# Konfigurasi yang harus sama dengan saat training
IMAGE_SIZE = (128, 128)
HOG_ORIENTATIONS = 9
HOG_PIXELS_PER_CELL = (8, 8)
HOG_CELLS_PER_BLOCK = (2, 2)

# Fungsi helper yang dibutuhkan oleh class
def resize_image(image):
    """Mengubah ukuran gambar ke ukuran standar."""
    return cv2.resize(image, IMAGE_SIZE, interpolation=cv2.INTER_AREA)

def to_grayscale(image):
    """Mengonversi gambar BGR ke grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def normalize_image(image):
    """Menormalisasi nilai piksel gambar ke rentang [0.0, 1.0]."""
    return image.astype('float32') / 255.0

def preprocess_image_for_feature_extraction(image):
    """Pipeline prapemrosesan lengkap untuk satu gambar."""
    resized_color_uint8 = resize_image(image)
    gray_image = to_grayscale(resized_color_uint8)
    normalized_gray = normalize_image(gray_image)
    normalized_color = normalize_image(resized_color_uint8)
    return normalized_gray, normalized_color

def extract_hog_features(gray_image):
    """Mengekstrak fitur HOG."""
    return hog(gray_image, orientations=HOG_ORIENTATIONS, pixels_per_cell=HOG_PIXELS_PER_CELL,
               cells_per_block=HOG_CELLS_PER_BLOCK, block_norm='L2-Hys', visualize=False, transform_sqrt=True)

def extract_color_histogram(color_image):
    """Mengekstrak fitur histogram warna HSV."""
    hsv_image = cv2.cvtColor((color_image * 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
    hist_h = cv2.calcHist([hsv_image], [0], None, [180], [0, 180])
    hist_s = cv2.calcHist([hsv_image], [1], None, [32], [0, 256])
    hist_v = cv2.calcHist([hsv_image], [2], None, [32], [0, 256])
    cv2.normalize(hist_h, hist_h)
    cv2.normalize(hist_s, hist_s)
    cv2.normalize(hist_v, hist_v)
    return np.concatenate((hist_h, hist_s, hist_v)).flatten()

def extract_lbp_features(gray_image):
    """Mengekstrak fitur LBP."""
    gray_image_uint8 = (gray_image * 255).astype(np.uint8)
    radius, n_points = 8, 24
    lbp = local_binary_pattern(gray_image_uint8, n_points, radius, method='uniform')
    (hist, _) = np.histogram(lbp.ravel(), bins=np.arange(0, n_points + 3), range=(0, n_points + 2))
    hist = hist.astype("float")
    hist /= (hist.sum() + 1e-6)
    return hist

def extract_color_moments(color_image):
    """Mengekstrak fitur color moments Lab."""
    lab_image = cv2.cvtColor((color_image * 255).astype(np.uint8), cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(lab_image)
    channels = [l, a, b]
    features = []
    for channel in channels:
        mean = np.mean(channel)
        std = np.std(channel)
        if std > 1e-6:
            skewness = skew(channel.flatten())
        else:
            skewness = 0.0
        features.extend([mean, std, skewness])
    return np.array(features)

def extract_glcm_features(gray_image):
    """Mengekstrak fitur tekstur GLCM."""
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
    """Mengekstrak fitur tekstur Gabor."""
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
    """Mengekstrak fitur tepi Sobel."""
    img_uint8 = (gray_image * 255).astype(np.uint8)
    sobelx = cv2.Sobel(img_uint8, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(img_uint8, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx**2 + sobely**2)
    (hist, _) = np.histogram(magnitude.ravel(), bins=32, range=(0, 256))
    hist = hist.astype("float")
    hist /= (hist.sum() + 1e-6)
    return hist

def extract_features(gray_image, color_image):
    """Menggabungkan semua fitur menjadi satu vektor tunggal."""
    hog_features = extract_hog_features(gray_image)
    color_hist_features = extract_color_histogram(color_image)
    lbp_features = extract_lbp_features(gray_image)
    gabor_features = extract_gabor_features(gray_image)
    sobel_features = extract_sobel_features(gray_image)
    glcm_features = extract_glcm_features(gray_image)
    color_moments = extract_color_moments(color_image)
    all_features = np.hstack([hog_features, color_hist_features, lbp_features, gabor_features, sobel_features, glcm_features, color_moments])
    
    if np.isnan(all_features).any():
        all_features = np.nan_to_num(all_features)
        
    return all_features

class IntegratedClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self, C=1.0, gamma='scale'):
        self.C = C
        self.gamma = gamma
        self.pipeline = make_pipeline(
            StandardScaler(),
            PCA(n_components=0.95, random_state=42),
            SVC(kernel='rbf', C=self.C, gamma=self.gamma, probability=True, random_state=42, class_weight='balanced')
        )
    def _preprocess_and_extract(self, X_raw):
        feature_list = []
        for image in X_raw:
            gray_img, color_img = preprocess_image_for_feature_extraction(image)
            features = extract_features(gray_img, color_img)
            feature_list.append(features)
        return np.array(feature_list)
    def fit(self, X_raw, y):
        X_features = self._preprocess_and_extract(X_raw)
        self.pipeline.fit(X_features, y)
        return self
    def predict(self, X_raw):
        X_features = self._preprocess_and_extract(X_raw)
        return self.pipeline.predict(X_features)
    def predict_proba(self, X_raw):
        X_features = self._preprocess_and_extract(X_raw)
        return self.pipeline.predict_proba(X_features)
