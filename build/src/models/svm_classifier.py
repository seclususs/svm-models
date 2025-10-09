import os
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV
import joblib

from src.utils.logger import logger
from src.configs.config import SAVED_MODEL_PATH


def create_svm_pipeline_with_pca():
    """
    Pipeline yang terdiri dari scaler, PCA untuk reduksi dimensi, dan classifier SVM.
    """
    pipeline = make_pipeline(
        StandardScaler(),
        PCA(n_components=0.95, random_state=42),
        SVC(kernel='rbf', probability=True, random_state=42, class_weight='balanced')
    )
    return pipeline

def tune_and_train_model(X_train, y_train):
    """
    Melakukan tuning hyperparameter menggunakan GridSearchCV dan melatih model.
    """
    pipeline = create_svm_pipeline_with_pca()
    
    param_grid = {
    'C': [0.1, 1, 10, 100],
    'gamma': [0.005, 0.01, 0.05],
    }

    logger.info("="*50)
    logger.info("MEMULAI TUNING HYPERPARAMETER (GRID SEARCH)")
    logger.info(f"Parameter Grid yang Diuji: {param_grid}")
    logger.info("="*50)

    # Tambahkan n_jobs=1 untuk menonaktifkan multiprocessing di Windows
    grid_search = GridSearchCV(pipeline, param_grid, cv=3, verbose=2, n_jobs=1)
    grid_search.fit(X_train, y_train)

    logger.info("\nTuning selesai.")
    logger.info(f"Parameter terbaik ditemukan: {grid_search.best_params_}")
    logger.info(f"Skor cross-validation terbaik: {grid_search.best_score_:.4f}")

    if hasattr(grid_search.best_estimator_.named_steps['pca'], 'n_components_'):
        n_components = grid_search.best_estimator_.named_steps['pca'].n_components_
        logger.info(f"PCA memilih {n_components} komponen.")

    return grid_search.best_estimator_

def save_model(model):
    """
    Menyimpan model yang telah dilatih ke file.
    """
    try:
        joblib.dump(model, SAVED_MODEL_PATH)
        logger.info(f"Model berhasil disimpan di {SAVED_MODEL_PATH}")
    except Exception as e:
        logger.error(f"Gagal menyimpan model: {e}")
        raise

def load_model():
    """
    Memuat model dari file.
    """
    try:
        if os.path.exists(SAVED_MODEL_PATH):
            model = joblib.load(SAVED_MODEL_PATH)
            logger.info(f"Model berhasil dimuat dari {SAVED_MODEL_PATH}")
            return model
        else:
            raise FileNotFoundError(f"File model tidak ditemukan di {SAVED_MODEL_PATH}")
    except Exception as e:
        logger.error(f"Gagal memuat model: {e}")
        raise
