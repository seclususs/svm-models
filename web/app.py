"""
Berkas utama aplikasi Flask.

Berkas ini bertanggung jawab untuk menginisialisasi aplikasi Flask,
memuat model machine learning, mengkonfigurasi pengaturan aplikasi,
dan mendaftarkan semua blueprint (rute) yang diperlukan.
"""

import os
import joblib
from flask import Flask

from utils.model_wrapper import IntegratedClassifier
from routes.main import main_bp
from routes.predict import predict_bp
from routes.live import live_bp

def create_app():
    """
    Fungsi pabrik (factory function) untuk membuat dan mengkonfigurasi instance aplikasi Flask.

    Fungsi ini melakukan hal-hal berikut:
    1. Membuat instance Flask.
    2. Mengatur konfigurasi dasar seperti secret key dan folder unggahan.
    3. Memastikan direktori untuk unggahan ada.
    4. Memuat model klasifikasi cuaca dan model deteksi anomali.
    5. Mendefinisikan variabel global aplikasi seperti daftar kelas dan ekstensi yang diizinkan.
    6. Mendaftarkan blueprint untuk setiap bagian dari fungsionalitas aplikasi.

    Returns:
        Flask.app: Instance aplikasi Flask yang telah dikonfigurasi.
    """
    app = Flask(__name__)
    
    # Konfigurasi aplikasi
    app.config['SECRET_KEY'] = 'supersecretkey'  # Kunci rahasia untuk sesi dan keamanan.
    app.config['UPLOAD_FOLDER'] = 'static/uploads/'  # Direktori penyimpanan berkas unggahan.
    app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  # Batas ukuran berkas unggahan (30 MB).
    
    # Membuat direktori unggahan jika belum ada.
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        
    # Memuat model klasifikasi cuaca.
    try:
        model_path = 'model/svm_model-v1.1.pkl' 
        app.model = joblib.load(model_path)
        print(f"* Model klasifikasi berhasil dimuat dari {model_path}")
    except Exception as e:
        print(f"* GAGAL memuat model klasifikasi: {e}")
        app.model = None

    # Memuat model deteksi anomali.
    try:
        anomaly_model_path = 'model/anomaly_detector.pkl'
        app.anomaly_detector = joblib.load(anomaly_model_path)
        print(f"* Model detektor anomali berhasil dimuat dari {anomaly_model_path}")
    except Exception as e:
        print(f"* GAGAL memuat model detektor anomali: {e}")
        app.anomaly_detector = None

    # Mendefinisikan variabel konfigurasi yang dapat diakses di seluruh aplikasi.
    app.CLASSES = ["Berawan", "Hujan", "Cerah", "Berkabut"]  # Daftar kelas target.
    app.ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # Ekstensi berkas yang diizinkan.
    
    # Mendaftarkan blueprint untuk mengatur rute.
    app.register_blueprint(main_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(live_bp)

    return app

# Titik masuk eksekusi skrip.
if __name__ == '__main__':
    # Membuat aplikasi menggunakan fungsi pabrik.
    app = create_app()
    # Menjalankan server pengembangan Flask dengan dukungan SSL ad-hoc.
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')
