import os
import uuid
import numpy as np
from PIL import Image
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app

from utils.model_wrapper import preprocess_image_for_feature_extraction, extract_features
from utils.prediction_logic import smart_predict

predict_bp = Blueprint('predict', __name__)

def allowed_file(filename):
    allowed_extensions = current_app.ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    unique_name = uuid.uuid4().hex
    return f"{unique_name}.{ext}"

@predict_bp.route('/predict', methods=['POST'])
def predict():
    model = current_app.model
    anomaly_detector = current_app.anomaly_detector
    classes = current_app.CLASSES
    upload_folder = current_app.config['UPLOAD_FOLDER']

    if 'file' not in request.files:
        flash('Tidak ada bagian file')
        return redirect(url_for('main.index'))
        
    file = request.files['file']
    if file.filename == '':
        flash('Tidak ada gambar yang dipilih untuk diunggah')
        return redirect(url_for('main.index'))

    if file and allowed_file(file.filename):
        original_filename = generate_unique_filename(file.filename)
        filepath = os.path.join(upload_folder, original_filename)
        file.save(filepath)

        try:
            # Buka gambar dan konversi ke array NumPy
            with Image.open(filepath) as img:
                image_np_for_check = np.array(img.convert('RGB'))

            if not model or not anomaly_detector:
                flash("Satu atau lebih model gagal dimuat. Fungsi prediksi tidak tersedia.")
                os.remove(filepath)
                return redirect(url_for('main.index'))

            # Ekstrak fitur dari gambar yang diunggah
            gray_img, color_img = preprocess_image_for_feature_extraction(image_np_for_check)
            features = extract_features(gray_img, color_img)
            
            # Lakukan prediksi anomali
            is_anomaly = anomaly_detector.predict(features.reshape(1, -1))
            
            # Jika anomali (-1), tolak gambar, hapus file, dan beri pesan
            if is_anomaly[0] == -1:
                os.remove(filepath)
                flash('Gambar yang diunggah tidak terdeteksi sebagai citra cuaca. Silakan coba gambar lain.')
                return redirect(url_for('main.index'))
            
            # Jika lolos, lanjutkan membuat thumbnail
            with Image.open(filepath) as img:
                filename_parts = original_filename.rsplit('.', 1)
                thumb_filename = f"{filename_parts[0]}_thumb.{filename_parts[1]}"
                thumb_filepath = os.path.join(upload_folder, thumb_filename)
                img.thumbnail((800, 800))
                img.save(thumb_filepath, optimize=True, quality=85)
                
                last_filepath = session.get('last_filepath')
                if last_filepath and os.path.exists(last_filepath):
                    os.remove(last_filepath)
                session['last_filepath'] = thumb_filepath
                os.remove(filepath) # Hapus file asli setelah thumbnail dibuat

            # Lanjutkan dengan prediksi cuaca
            confidence_scores = model.predict_proba([image_np_for_check])[0]
            all_confidences = sorted(
                [(classes[i], round(score * 100, 2)) for i, score in enumerate(confidence_scores)],
                key=lambda item: item[1],
                reverse=True
            )
            prediction, icon_name, description = smart_predict(all_confidences)
            
            return render_template('result.html', 
                                   filename=original_filename,
                                   filename_thumb=thumb_filename,
                                   prediction=prediction,
                                   icon_name=icon_name,
                                   description=description,
                                   all_confidences=all_confidences)

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            flash(f'Terjadi kesalahan saat memproses gambar: {e}')
            return redirect(url_for('main.index'))
    else:
        flash('Jenis file yang diizinkan adalah png, jpg, jpeg')
        return redirect(url_for('main.index'))
