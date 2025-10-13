"""
Blueprint untuk fungsionalitas deteksi cuaca secara langsung (live).

Modul ini mendefinisikan rute API yang menerima frame gambar dari klien
(misalnya, dari kamera web), memprosesnya, dan mengembalikan hasil prediksi
secara real-time.
"""

import numpy as np
import base64
import io
from PIL import Image
from flask import Blueprint, jsonify, request, current_app

from utils.model_wrapper import preprocess_image_for_feature_extraction, extract_features
from utils.prediction_logic import smart_predict

# Membuat instance Blueprint untuk rute terkait deteksi langsung.
live_bp = Blueprint('live', __name__)

@live_bp.route('/predict_frame', methods=['POST'])
def predict_frame():
    """
    Endpoint API untuk memprediksi frame gambar tunggal.

    Menerima data gambar dalam format Base64 dari permintaan JSON.
    Gambar tersebut kemudian di-decode, diproses untuk deteksi anomali,
    dan jika valid, diprediksi kondisi cuacanya.

    Returns:
        Response: Objek JSON yang berisi hasil prediksi atau pesan kesalahan.
    """
    # Mengambil model dan konfigurasi dari konteks aplikasi saat ini.
    model = current_app.model
    anomaly_detector = current_app.anomaly_detector
    classes = current_app.CLASSES

    # Memeriksa apakah model telah berhasil dimuat.
    if not model or not anomaly_detector:
        return jsonify({'error': 'Model tidak dimuat'}), 500

    try:
        # Mengambil data gambar dari badan permintaan JSON.
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'Tidak ada data gambar'}), 400

        # Memisahkan header dari data Base64.
        # Contoh header: 'data:image/jpeg;base64,'
        header, encoded = image_data.split(',', 1)
        
        # Mendekode string Base64 menjadi byte.
        image_bytes = base64.b64decode(encoded)
        
        # Membuka byte gambar menggunakan Pillow dan mengubahnya menjadi array NumPy.
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        image_np = np.array(image)

        # Langkah 1: Deteksi Anomali
        # Gambar diproses untuk mengekstrak fitur yang relevan.
        gray_img, color_img = preprocess_image_for_feature_extraction(image_np)
        features = extract_features(gray_img, color_img)
        # Model detektor anomali memprediksi apakah gambar tersebut merupakan anomali.
        is_anomaly = anomaly_detector.predict(features.reshape(1, -1))
        
        # Jika gambar terdeteksi sebagai anomali (nilai prediksi -1), kembalikan respons anomali.
        if is_anomaly[0] == -1:
            return jsonify({
                'prediction': 'Tidak Terdeteksi',
                'confidence': 100,
                'is_anomaly': True
            })

        # Langkah 2: Prediksi Cuaca (jika bukan anomali)
        # Model klasifikasi memprediksi probabilitas untuk setiap kelas cuaca.
        confidence_scores = model.predict_proba([image_np])[0]
        # Mengurutkan hasil kepercayaan dari yang tertinggi ke terendah.
        all_confidences = sorted(
            [(classes[i], round(score * 100, 2)) for i, score in enumerate(confidence_scores)],
            key=lambda item: item[1],
            reverse=True
        )
        # Menggunakan logika cerdas untuk mendapatkan prediksi akhir.
        prediction, _, _ = smart_predict(all_confidences)
        
        # Mengirimkan hasil prediksi dalam format JSON.
        return jsonify({
            'prediction': prediction,
            'confidence': all_confidences[0][1]
        })

    except Exception as e:
        # Menangani kesalahan yang mungkin terjadi selama proses.
        print(f"Error processing frame: {e}")
        return jsonify({'error': str(e)}), 500
