from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Menampilkan halaman utama untuk unggah gambar tunggal."""
    return render_template('index.html')

@main_bp.route('/performance')
def performance():
    """Menampilkan halaman visualisasi performa model."""
    return render_template('performance.html')

@main_bp.route('/batch')
def batch():
    """Menampilkan halaman untuk unggah gambar massal (batch)."""
    return render_template('batch.html')