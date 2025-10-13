from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Menampilkan halaman utama untuk unggah gambar tunggal atau lebih."""
    return render_template('index.html')

@main_bp.route('/performance')
def performance():
    """Menampilkan halaman visualisasi performa model."""
    return render_template('performance.html')

@main_bp.route('/live')
def live():
    """Menampilkan halaman deteksi langsung dari kamera."""
    return render_template('live.html')
