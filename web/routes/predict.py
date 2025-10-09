import os
import uuid
import numpy as np
from PIL import Image
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from utils.prediction_logic import get_human_readable_prediction

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
            with Image.open(filepath) as img:
                filename_parts = original_filename.rsplit('.', 1)
                thumb_filename = f"{filename_parts[0]}_thumb.{filename_parts[1]}"
                thumb_filepath = os.path.join(upload_folder, thumb_filename)

                img.thumbnail((800, 800))
                img.save(thumb_filepath, optimize=True, quality=85)
                
                # Hapus file lama jika ada dan simpan path file baru (thumb)
                last_filepath = session.get('last_filepath')
                if last_filepath and os.path.exists(last_filepath):
                    os.remove(last_filepath)
                session['last_filepath'] = thumb_filepath
                os.remove(filepath)
                
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            thumb_filename = original_filename
        
        try:
            image_to_predict_path = os.path.join(upload_folder, thumb_filename)
            image = Image.open(image_to_predict_path).convert('RGB')
            image_np = np.array(image)
            
            if not model:
                flash("Model tidak dapat dimuat. Prediksi tidak tersedia.")
                return redirect(url_for('main.index'))
            
            confidence_scores = model.predict_proba([image_np])[0]
            all_confidences = sorted(
                [(classes[i], round(score * 100, 2)) for i, score in enumerate(confidence_scores)],
                key=lambda item: item[1],
                reverse=True
            )
            prediction, icon_name, description = get_human_readable_prediction(all_confidences)
            
            return render_template('result.html', 
                                   filename=original_filename, # Nama file asli untuk referensi jika perlu
                                   filename_thumb=thumb_filename, # Nama file thumbnail untuk ditampilkan
                                   prediction=prediction,
                                   icon_name=icon_name,
                                   description=description,
                                   all_confidences=all_confidences)
        except Exception as e:
            flash(f'Terjadi kesalahan saat memproses gambar: {e}')
            return redirect(url_for('main.index'))
    else:
        flash('Jenis file yang diizinkan adalah png, jpg, jpeg')
        return redirect(url_for('main.index'))
    