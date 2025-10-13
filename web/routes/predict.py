"""
Blueprint untuk menangani semua logika terkait prediksi gambar.

Modul ini berisi rute untuk:
1. Menerima unggahan gambar (baik tunggal maupun massal).
2. Memvalidasi dan menyimpan berkas yang diunggah.
3. Memproses gambar melalui model deteksi anomali dan klasifikasi cuaca.
4. Mengarahkan pengguna ke halaman hasil yang sesuai.
5. Menyediakan endpoint API untuk pemrosesan gambar secara asinkron (untuk unggahan massal).
"""

import os
import uuid
import numpy as np
from PIL import Image
from flask import (Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify)
from werkzeug.utils import secure_filename

from utils.model_wrapper import preprocess_image_for_feature_extraction, extract_features
from utils.prediction_logic import smart_predict

# Membuat instance Blueprint.
predict_bp = Blueprint('predict', __name__)

def allowed_file(filename):
    """
    Memeriksa apakah ekstensi berkas diizinkan.

    Args:
        filename (str): Nama berkas yang akan diperiksa.

    Returns:
        bool: True jika ekstensi diizinkan, False jika tidak.
    """
    allowed_extensions = current_app.ALLOWED_EXTENSIONS
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(filename):
    """
    Menghasilkan nama berkas yang unik secara global menggunakan UUID.

    Args:
        filename (str): Nama berkas asli.

    Returns:
        str: Nama berkas baru yang unik.
    """
    ext = filename.rsplit('.', 1)[1].lower()
    unique_name = uuid.uuid4().hex
    return f"{unique_name}.{ext}"

@predict_bp.route('/predict', methods=['POST'])
def predict():
    """
    Titik masuk utama untuk prediksi.

    Fungsi ini menangani permintaan POST dari formulir unggah.
    Ini membedakan antara unggahan berkas tunggal dan ganda, lalu memanggil
    fungsi penangan yang sesuai.
    """
    # Mengambil semua berkas dari permintaan.
    uploaded_files = request.files.getlist('files')
    
    # Validasi: Memastikan setidaknya satu berkas dipilih.
    if not uploaded_files or uploaded_files[0].filename == '':
        flash('Tidak ada file yang dipilih untuk diunggah.')
        return redirect(url_for('main.index'))
    
    # Logika untuk satu berkas (mengarahkan ke halaman hasil tunggal).
    if len(uploaded_files) == 1:
        return handle_single_file(uploaded_files[0])
        
    # Logika untuk banyak berkas (mengarahkan ke halaman hasil massal).
    else:
        return handle_multiple_files(uploaded_files)

def handle_single_file(file):
    """
    Memproses unggahan satu berkas gambar.

    Fungsi ini menyimpan berkas, menjalankan deteksi anomali, melakukan prediksi,
    membuat thumbnail, dan kemudian merender halaman hasil yang detail.

    Args:
        file (FileStorage): Objek berkas yang diunggah.
    """
    # Mengambil konfigurasi dan model dari aplikasi.
    model = current_app.model
    anomaly_detector = current_app.anomaly_detector
    classes = current_app.CLASSES
    upload_folder = current_app.config['UPLOAD_FOLDER']

    if file and allowed_file(file.filename):
        original_filename = generate_unique_filename(file.filename)
        filepath = os.path.join(upload_folder, original_filename)
        file.save(filepath)

        try:
            # Deteksi anomali terlebih dahulu.
            with Image.open(filepath) as img:
                image_np_for_check = np.array(img.convert('RGB'))

            gray_img, color_img = preprocess_image_for_feature_extraction(image_np_for_check)
            features = extract_features(gray_img, color_img)
            is_anomaly = anomaly_detector.predict(features.reshape(1, -1))
            
            # Jika anomali terdeteksi, hapus berkas dan kembali ke halaman utama.
            if is_anomaly[0] == -1:
                os.remove(filepath)
                flash('Gambar yang diunggah tidak terdeteksi. Silakan coba gambar lain.')
                return redirect(url_for('main.index'))
            
            # Jika bukan anomali, buat thumbnail untuk ditampilkan.
            with Image.open(filepath) as img:
                filename_parts = original_filename.rsplit('.', 1)
                thumb_filename = f"{filename_parts[0]}_thumb.{filename_parts[1]}"
                thumb_filepath = os.path.join(upload_folder, thumb_filename)
                img.thumbnail((800, 800))  # Mengubah ukuran gambar.
                img.save(thumb_filepath, optimize=True, quality=85)
                
                # Menghapus berkas thumbnail sebelumnya dari sesi untuk menjaga kebersihan.
                last_filepath = session.get('last_filepath')
                if last_filepath and os.path.exists(last_filepath):
                    os.remove(last_filepath)
                session['last_filepath'] = thumb_filepath
                os.remove(filepath) # Menghapus berkas asli yang berukuran besar.

            # Lakukan prediksi cuaca pada gambar.
            confidence_scores = model.predict_proba([image_np_for_check])[0]
            all_confidences = sorted(
                [(classes[i], round(score * 100, 2)) for i, score in enumerate(confidence_scores)],
                key=lambda item: item[1], reverse=True
            )
            prediction, icon_name, description = smart_predict(all_confidences)
            
            # Tampilkan halaman hasil dengan data prediksi.
            return render_template('result.html', 
                                   filename_thumb=thumb_filename,
                                   prediction=prediction,
                                   icon_name=icon_name,
                                   description=description,
                                   all_confidences=all_confidences)

        except Exception as e:
            # Penanganan kesalahan umum.
            if os.path.exists(filepath):
                os.remove(filepath)
            flash(f'Terjadi kesalahan saat memproses gambar: {e}')
            return redirect(url_for('main.index'))

    else:
        flash('Jenis file yang diizinkan adalah png, jpg, jpeg')
        return redirect(url_for('main.index'))

def handle_multiple_files(uploaded_files):
    """
    Memproses unggahan beberapa berkas gambar.

    Fungsi ini membuat direktori unik untuk batch unggahan, menyimpan semua berkas
    yang valid ke dalamnya, dan kemudian merender halaman hasil massal
    yang akan memproses setiap gambar secara asinkron.

    Args:
        uploaded_files (list of FileStorage): Daftar objek berkas yang diunggah.
    """
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
        
    # Tampilkan halaman hasil massal dengan ID batch dan info berkas.
    return render_template('batch_result.html', batch_id=batch_id, files=files_info)

@predict_bp.route('/api/process_image', methods=['POST'])
def process_image():
    """
    Endpoint API untuk memproses satu gambar dari batch.

    Dipanggil oleh JavaScript dari halaman hasil massal untuk setiap gambar.
    Ini melakukan logika prediksi yang sama dengan `handle_single_file` tetapi
    mengembalikan hasilnya dalam format JSON.
    """
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
        
        # Deteksi anomali.
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

        # Prediksi cuaca.
        confidence_scores = model.predict_proba([image_np])[0]
        all_confidences = sorted(
            [(classes[i], round(score * 100, 2)) for i, score in enumerate(confidence_scores)],
            key=lambda item: item[1], reverse=True
        )
        prediction, icon_name, _ = smart_predict(all_confidences)
        
        # Kembalikan hasil dalam format JSON.
        return jsonify({
            'prediction': prediction,
            'icon_name': icon_name,
            'confidence': all_confidences[0][1],
            'all_confidences': all_confidences
        })
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return jsonify({'error': f'Gagal memproses gambar: {e}'}), 500
