import os
from PIL import Image
import imagehash

dataset_dir = r"D:\CODE\python-project\klasifikasi-cuaca-svm\svm\data\raw"
hashes = {}
duplicates_to_remove = []

for class_folder in os.listdir(dataset_dir):
    class_path = os.path.join(dataset_dir, class_folder)
    if not os.path.isdir(class_path):
        continue

    for filename in os.listdir(class_path):
        filepath = os.path.join(class_path, filename)
        try:
            img = Image.open(filepath)
            h = imagehash.average_hash(img)
            if h in hashes:
                duplicates_to_remove.append(filepath)
                print(f"Duplikat ditemukan: {filepath} (sama dengan {hashes[h]})")
            else:
                hashes[h] = filepath
        except Exception as e:
            print(f"Error memproses {filepath}: {e}")

for filepath in duplicates_to_remove:
    os.remove(filepath)
    print(f"Menghapus: {filepath}")

print(f"\nTotal duplikat ditemukan: {len(duplicates_to_remove)}")