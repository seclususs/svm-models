import numpy as np
import base64
import io
from PIL import Image
from flask import Blueprint, jsonify, request, current_app

from utils.model_wrapper import preprocess_image_for_feature_extraction, extract_features
from utils.prediction_logic import smart_predict

live_bp = Blueprint('live', __name__)

@live_bp.route('/predict_frame', methods=['POST'])
def predict_frame():
    """
    Menerima frame gambar dalam format Base64 dari klien,
    melakukan prediksi, dan mengembalikan hasilnya sebagai JSON.
    """
    model = current_app.model
    anomaly_detector = current_app.anomaly_detector
    classes = current_app.CLASSES

    if not model or not anomaly_detector:
        return jsonify({'error': 'Model tidak dimuat'}), 500

    try:
        # Mengambil data gambar dari request JSON
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'Tidak ada data gambar'}), 400

        # Membersihkan header 'data:image/jpeg;base64,' dari string
        header, encoded = image_data.split(',', 1)
        
        # Decode base64 menjadi bytes
        image_bytes = base64.b64decode(encoded)
        
        # Buka gambar menggunakan Pillow dan konversi ke array NumPy
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_np = np.array(image)

        # Deteksi Anomali
        gray_img, color_img = preprocess_image_for_feature_extraction(image_np)
        features = extract_features(gray_img, color_img)
        is_anomaly = anomaly_detector.predict(features.reshape(1, -1))
        
        if is_anomaly[0] == -1:
            return jsonify({
                'prediction': 'Tidak Terdeteksi',
                'confidence': 100,
                'is_anomaly': True
            })

        # Lakukan prediksi cuaca
        confidence_scores = model.predict_proba([image_np])[0]
        all_confidences = sorted(
            [(classes[i], round(score * 100, 2)) for i, score in enumerate(confidence_scores)],
            key=lambda item: item[1],
            reverse=True
        )
        prediction, _, _ = smart_predict(all_confidences)
        
        # Kirim hasil sebagai JSON
        return jsonify({
            'prediction': prediction,
            'confidence': all_confidences[0][1]
        })

    except Exception as e:
        print(f"Error processing frame: {e}")
        return jsonify({'error': str(e)}), 500
