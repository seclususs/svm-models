import os
import joblib
from flask import Flask

from utils.model_wrapper import IntegratedClassifier
from routes.main import main_bp
from routes.predict import predict_bp
from routes.live import live_bp

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['UPLOAD_FOLDER'] = 'static/uploads/'
    app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        
    try:
        model_path = 'model/svm_model-v1.1.pkl' 
        app.model = joblib.load(model_path)
        print(f"* Model klasifikasi berhasil dimuat dari {model_path}")
    except Exception as e:
        print(f"* GAGAL memuat model klasifikasi: {e}")
        app.model = None

    try:
        anomaly_model_path = 'model/anomaly_detector.pkl'
        app.anomaly_detector = joblib.load(anomaly_model_path)
        print(f"* Model detektor anomali berhasil dimuat dari {anomaly_model_path}")
    except Exception as e:
        print(f"* GAGAL memuat model detektor anomali: {e}")
        app.anomaly_detector = None

    app.CLASSES = ["Berawan", "Hujan", "Cerah", "Berkabut"]
    app.ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    app.register_blueprint(main_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(live_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')
