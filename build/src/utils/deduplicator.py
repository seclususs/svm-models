"""Skrip utilitas untuk menghapus gambar duplikat dari dataset.

Skrip ini mengiterasi melalui semua folder kelas dalam direktori dataset,
menghitung hash perseptual (average hash) untuk setiap gambar, dan
mengidentifikasi serta menghapus file-file yang memiliki hash yang sama.
"""

import os
from PIL import Image
import imagehash


def find_and_remove_duplicates(dataset_dir):
    """Mencari dan menghapus gambar duplikat dalam direktori dataset.

    Args:
        dataset_dir (str): Path ke direktori utama dataset yang berisi
                           sub-direktori untuk setiap kelas.
    """
    hashes = {}
    duplicates_to_remove = []

    print(f"Memindai duplikat di direktori: {dataset_dir}")

    # Iterasi melalui setiap folder kelas
    for class_folder in os.listdir(dataset_dir):
        class_path = os.path.join(dataset_dir, class_folder)
        if not os.path.isdir(class_path):
            continue

        print(f"\nMemproses folder: {class_folder}")
        # Iterasi melalui setiap file dalam folder kelas
        for filename in os.listdir(class_path):
            filepath = os.path.join(class_path, filename)
            try:
                # Buka gambar dan hitung hash-nya
                with Image.open(filepath) as img:
                    h = imagehash.average_hash(img)

                # Periksa apakah hash sudah ada
                if h in hashes:
                    duplicates_to_remove.append(filepath)
                    print(f"  - Duplikat ditemukan: {filepath} (sama dengan {hashes[h]})")
                else:
                    # Jika belum ada, simpan hash dan path file
                    hashes[h] = filepath
            except Exception as e:
                print(f"  - Error memproses {filepath}: {e}")

    # Hapus semua file duplikat yang telah diidentifikasi
    if duplicates_to_remove:
        print("\n--- Menghapus file duplikat ---")
        for filepath in duplicates_to_remove:
            try:
                os.remove(filepath)
                print(f"Menghapus: {filepath}")
            except Exception as e:
                print(f"Gagal menghapus {filepath}: {e}")
    else:
        print("\nTidak ada file duplikat yang ditemukan.")

    print(f"\nProses selesai. Total duplikat ditemukan dan dihapus: {len(duplicates_to_remove)}")


if __name__ == '__main__':
    # Tentukan direktori dataset utama.
    # Ganti path ini sesuai dengan struktur direktori Anda.
    main_dataset_dir = r"D:\program\python-project\svm-models\build\data\raw"
    find_and_remove_duplicates(main_dataset_dir)
