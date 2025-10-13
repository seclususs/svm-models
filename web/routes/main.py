"""
Blueprint untuk rute-rute utama dan statis dari aplikasi.

Modul ini mendefinisikan rute untuk halaman utama (index), halaman
visualisasi performa model, dan halaman deteksi langsung (live).
Tugas utamanya adalah merender templat HTML yang sesuai untuk setiap halaman.
"""

from flask import Blueprint, render_template

# Membuat instance Blueprint untuk rute-rute utama.
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Rute untuk halaman utama (beranda).
    
    Menampilkan halaman di mana pengguna dapat mengunggah satu atau lebih gambar
    untuk dianalisis.

    Returns:
        str: Konten HTML yang dirender dari templat 'index.html'.
    """
    return render_template('index.html')

@main_bp.route('/performance')
def performance():
    """
    Rute untuk halaman performa model.
    
    Menampilkan halaman yang berisi visualisasi data mengenai performa
    model klasifikasi, seperti confusion matrix, kurva ROC, dan metrik lainnya.

    Returns:
        str: Konten HTML yang dirender dari templat 'performance.html'.
    """
    return render_template('performance.html')

@main_bp.route('/live')
def live():
    """
    Rute untuk halaman deteksi langsung.
    
    Menampilkan halaman yang memungkinkan pengguna menggunakan kamera perangkat
    mereka untuk melakukan klasifikasi cuaca secara real-time.

    Returns:
        str: Konten HTML yang dirender dari templat 'live.html'.
    """
    return render_template('live.html')
