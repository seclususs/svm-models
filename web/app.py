import os
import joblib
from flask import Flask

from utils.model_wrapper import IntegratedClassifier
from routes.main import main_bp
from routes.predict import predict_bp
from routes.batch import batch_bp

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['UPLOAD_FOLDER'] = 'static/uploads/'
    app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    try:
        model_path = 'model/svm_model-v0.5.pkl' 
        app.model = joblib.load(model_path)
        print(f"* Model terintegrasi berhasil dimuat dari {model_path}")
    except Exception as e:
        print(f"* GAGAL memuat model: {e}")
        app.model = None

    app.CLASSES = ["Berawan (Cloudy)", "Hujan (Rain)", "Cerah (Sunrise, Shiny)", "Berkabut (Foggy)"]
    app.ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    app.register_blueprint(main_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(batch_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=False)
