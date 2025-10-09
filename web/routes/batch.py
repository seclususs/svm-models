import os
import uuid
import numpy as np
from PIL import Image
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename
from utils.prediction_logic import get_human_readable_prediction

batch_bp = Blueprint('batch', __name__)

def allowed_file(filename):
    """Memeriksa ekstensi file."""
    allowed_extensions = current_app.ALLOWED_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(filename):
    """Menghasilkan nama file yang unik."""
    ext = filename.rsplit('.', 1)[1].lower()
    unique_name = uuid.uuid4().hex
    return f"{unique_name}.{ext}"

@batch_bp.route('/upload_batch', methods=['POST'])
def upload_batch():
    """Menerima unggahan file massal, menyimpannya, dan mengarahkan ke halaman hasil."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    uploaded_files = request.files.getlist('files')
    
    if not uploaded_files or uploaded_files[0].filename == '':
        flash('Tidak ada file yang dipilih untuk diunggah.')
        return redirect(url_for('main.batch'))
    
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
        return redirect(url_for('main.batch'))
        
    return render_template('batch_result.html', batch_id=batch_id, files=files_info)

@batch_bp.route('/api/process_image', methods=['POST'])
def process_image():
    """API endpoint untuk memproses satu gambar dari batch secara asynchronous."""
    model = current_app.model
    classes = current_app.CLASSES
    upload_folder = current_app.config['UPLOAD_FOLDER']

    data = request.get_json()
    batch_id = data.get('batch_id')
    filename = data.get('filename')

    if not all([batch_id, filename, model]):
        return jsonify({'error': 'Parameter tidak valid atau model tidak dimuat'}), 400
        
    filepath = os.path.join(upload_folder, batch_id, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File tidak ditemukan'}), 404

    try:
        image = Image.open(filepath).convert('RGB')
        image_np = np.array(image)
        
        confidence_scores = model.predict_proba([image_np])[0]
        all_confidences = sorted(
            [(classes[i], round(score * 100, 2)) for i, score in enumerate(confidence_scores)],
            key=lambda item: item[1],
            reverse=True
        )
        prediction, icon_name, _ = get_human_readable_prediction(all_confidences)
        
        return jsonify({
            'prediction': prediction,
            'icon_name': icon_name,
            'confidence': all_confidences[0][1],
            'all_confidences': all_confidences
        })
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return jsonify({'error': f'Gagal memproses gambar: {e}'}), 500
