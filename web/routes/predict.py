import os
import uuid
import numpy as np
from PIL import Image
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from werkzeug.utils import secure_filename

from utils.model_wrapper import preprocess_image_for_feature_extraction, extract_features
from utils.prediction_logic import smart_predict

predict_bp = Blueprint('predict', __name__)

def allowed_file(filename):
    """Memeriksa ekstensi file."""
    allowed_extensions = current_app.ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(filename):
    """Menghasilkan nama file yang unik."""
    ext = filename.rsplit('.', 1)[1].lower()
    unique_name = uuid.uuid4().hex
    return f"{unique_name}.{ext}"

@predict_bp.route('/predict', methods=['POST'])
def predict():
    """Menangani unggahan satu atau banyak gambar dan mengarahkannya ke halaman hasil yang sesuai."""
    uploaded_files = request.files.getlist('files')
    
    if not uploaded_files or uploaded_files[0].filename == '':
        flash('Tidak ada file yang dipilih untuk diunggah.')
        return redirect(url_for('main.index'))
    
    # Logika untuk satu file (halaman hasil tunggal)
    if len(uploaded_files) == 1:
        return handle_single_file(uploaded_files[0])
        
    # Logika untuk banyak file (halaman hasil massal)
    else:
        return handle_multiple_files(uploaded_files)

def handle_single_file(file):
    """Memproses satu file gambar dan menampilkan halaman hasil detail."""
    model = current_app.model
    anomaly_detector = current_app.anomaly_detector
    classes = current_app.CLASSES
    upload_folder = current_app.config['UPLOAD_FOLDER']

    if file and allowed_file(file.filename):
        original_filename = generate_unique_filename(file.filename)
        filepath = os.path.join(upload_folder, original_filename)
        file.save(filepath)

        try:
            with Image.open(filepath) as img:
                image_np_for_check = np.array(img.convert('RGB'))

            gray_img, color_img = preprocess_image_for_feature_extraction(image_np_for_check)
            features = extract_features(gray_img, color_img)
            is_anomaly = anomaly_detector.predict(features.reshape(1, -1))
            
            if is_anomaly[0] == -1:
                os.remove(filepath)
                flash('Gambar yang diunggah tidak terdeteksi. Silakan coba gambar lain.')
                return redirect(url_for('main.index'))
            
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
                os.remove(filepath)

            confidence_scores = model.predict_proba([image_np_for_check])[0]
            all_confidences = sorted(
                [(classes[i], round(score * 100, 2)) for i, score in enumerate(confidence_scores)],
                key=lambda item: item[1], reverse=True
            )
            prediction, icon_name, description = smart_predict(all_confidences)
            
            return render_template('result.html', 
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

def handle_multiple_files(uploaded_files):
    """Menyimpan banyak file ke direktori batch dan menampilkan halaman hasil massal."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    batch_id = uuid.uuid4().hex
    batch_dir = os.path.join(upload_folder, batch_id)
    os.makedirs(batch_dir)
    
    files_info = []
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = generate_unique_filename(filename)
            filepath = os.path.join(batch_dir, unique_filename)
            file.save(filepath)
            files_info.append({
                'id': f"card-{unique_filename.split('.')[0]}",
                'unique_filename': unique_filename
            })
            
    if not files_info:
        flash('Tidak ada file valid yang diunggah.')
        return redirect(url_for('main.index'))
        
    return render_template('batch_result.html', batch_id=batch_id, files=files_info)

@predict_bp.route('/api/process_image', methods=['POST'])
def process_image():
    """API endpoint untuk memproses satu gambar dari batch secara asynchronous."""
    model = current_app.model
    anomaly_detector = current_app.anomaly_detector
    classes = current_app.CLASSES
    upload_folder = current_app.config['UPLOAD_FOLDER']

    data = request.get_json()
    batch_id = data.get('batch_id')
    filename = data.get('filename')

    if not all([batch_id, filename, model, anomaly_detector]):
        return jsonify({'error': 'Parameter tidak valid atau model tidak dimuat'}), 400
        
    filepath = os.path.join(upload_folder, batch_id, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File tidak ditemukan'}), 404

    try:
        image = Image.open(filepath).convert('RGB')
        image_np = np.array(image)
        
        gray_img, color_img = preprocess_image_for_feature_extraction(image_np)
        features = extract_features(gray_img, color_img)
        is_anomaly = anomaly_detector.predict(features.reshape(1, -1))
        
        if is_anomaly[0] == -1:
            return jsonify({
                'prediction': 'Gambar Ditolak',
                'icon_name': 'default',
                'confidence': 100,
                'all_confidences': [('Bukan citra cuaca', 100)],
                'is_anomaly': True
            })

        confidence_scores = model.predict_proba([image_np])[0]
        all_confidences = sorted(
            [(classes[i], round(score * 100, 2)) for i, score in enumerate(confidence_scores)],
            key=lambda item: item[1], reverse=True
        )
        prediction, icon_name, _ = smart_predict(all_confidences)
        
        return jsonify({
            'prediction': prediction,
            'icon_name': icon_name,
            'confidence': all_confidences[0][1],
            'all_confidences': all_confidences
        })
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return jsonify({'error': f'Gagal memproses gambar: {e}'}), 500
