import os

# PATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_RAW_PATH = os.path.join(BASE_DIR, 'data', 'raw')
DATA_PROCESSED_PATH = os.path.join(BASE_DIR, 'data', 'processed')
DATA_OUTLIERS_PATH = os.path.join(BASE_DIR, 'data', 'outliers')
SAVED_MODEL_PATH = os.path.join(BASE_DIR, 'saved_models', 'svm_model.pkl')
LOGS_PATH = os.path.join(BASE_DIR, 'experiments', 'logs')
RESULTS_PATH = os.path.join(BASE_DIR, 'experiments', 'results')

# IMAGE PREPROCESSING
IMAGE_SIZE = (128, 128) # Ukuran gambar (lebar, tinggi)

# FEATURE EXTRACTION (HOG)
HOG_ORIENTATIONS = 9
HOG_PIXELS_PER_CELL = (8, 8)
HOG_CELLS_PER_BLOCK = (2, 2)

# MODEL TRAINING
TEST_SIZE = 0.2
RANDOM_STATE = 42

# DATASET CLASSES
CLASSES = ["Berawan (Cloudy)", "Hujan (Rain)", "Cerah (Sunrise, Shiny)", "Berkabut (Foggy)"]