import os

BASE_DIR = r"D:\CODE\python-project\klasifikasi-cuaca-svm\svm\data\raw"
TARGET_COUNT = 300
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

subfolders = [
    os.path.join(BASE_DIR, d)
    for d in os.listdir(BASE_DIR)
    if os.path.isdir(os.path.join(BASE_DIR, d))
]

print(f"Ditemukan {len(subfolders)} folder di dalam '{BASE_DIR}'")

for folder in subfolders:
    print(f"\nMemproses folder: {folder}")

    all_files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if os.path.splitext(f.lower())[1] in IMAGE_EXTENSIONS
    ]

    count = len(all_files)
    print(f"  Jumlah file ditemukan: {count}")

    if count > TARGET_COUNT:
        all_files.sort(key=lambda f: os.path.getsize(f))
        files_to_delete = all_files[:count - TARGET_COUNT]
        print(f"  Menghapus {len(files_to_delete)}")

        for file_path in files_to_delete:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"    Gagal {file_path}: {e}")

        print(f"Selesai! Sekarang folder berisi {TARGET_COUNT} file.")
    elif count < TARGET_COUNT:
        print(f"Hanya ada {count} file, tidak ada yang dihapus.")
    else:
        print("Sudah pas, tidak ada tindakan.")
