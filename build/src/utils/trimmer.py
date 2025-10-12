"""Skrip utilitas untuk menyeimbangkan jumlah gambar per kelas.

Skrip ini akan memangkas jumlah gambar di setiap sub-direktori kelas
ke jumlah target yang ditentukan. Skrip ini akan menghapus file-file
dengan ukuran terkecil terlebih dahulu untuk mencapai jumlah target.
"""

import os

# --- KONFIGURASI ---
# Ganti dengan path ke direktori data 'raw' Anda.
BASE_DIR = r"D:\program\python-project\svm-models\build\data\raw"
# Tentukan jumlah gambar yang diinginkan di setiap folder kelas.
TARGET_COUNT = 300
# Ekstensi file gambar yang akan diproses.
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}


def trim_image_folders(base_dir, target_count):
    """Memangkas jumlah gambar di setiap subfolder ke jumlah target.

    Args:
        base_dir (str): Path ke direktori utama yang berisi subfolder kelas.
        target_count (int): Jumlah file yang diinginkan di setiap subfolder.
    """
    # Dapatkan daftar semua subfolder dalam direktori dasar
    subfolders = [
        os.path.join(base_dir, d)
        for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
    ]

    print(f"Ditemukan {len(subfolders)} folder di dalam '{base_dir}'")
    print(f"Target jumlah gambar per folder: {target_count}")

    # Iterasi melalui setiap folder kelas
    for folder in subfolders:
        print(f"\nMemproses folder: {os.path.basename(folder)}")

        # Dapatkan semua file gambar dalam folder
        all_files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if os.path.splitext(f.lower())[1] in IMAGE_EXTENSIONS
        ]

        count = len(all_files)
        print(f"  Jumlah file ditemukan: {count}")

        # Jika jumlah file melebihi target, lakukan pemangkasan
        if count > target_count:
            # Urutkan file berdasarkan ukuran (dari terkecil ke terbesar)
            all_files.sort(key=lambda f: os.path.getsize(f))

            # Tentukan file mana yang akan dihapus
            files_to_delete = all_files[:count - target_count]
            print(f"Kelebihan {len(files_to_delete)} file. Memulai penghapusan...")

            # Hapus file yang telah ditentukan
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Gagal menghapus {os.path.basename(file_path)}: {e}")

            remaining_count = len(os.listdir(folder))
            print(f"Selesai! Folder sekarang berisi {remaining_count} file.")
        elif count < target_count:
            print(f"Jumlah file lebih sedikit dari target. Tidak ada tindakan.")
        else:
            print("Jumlah file sudah sesuai target. Tidak ada tindakan.")


if __name__ == '__main__':
    # Jalankan fungsi utama
    trim_image_folders(BASE_DIR, TARGET_COUNT)
