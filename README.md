# Klasifikasi Cuaca Berbasis Gambar

Model untuk mengklasifikasikan gambar ke dalam empat kategori cuaca:

- **Berawan (Cloudy)**
- **Hujan (Rain)**
- **Cerah (Shine & Sunrise)**
- **Berkabut (Foggy)**

**Sumber Dataset:** 
- [multiclass-weather-dataset](https://www.kaggle.com/datasets/pratik2901/multiclass-weather-dataset)
- [weather-detection-image-dataset](https://www.kaggle.com/datasets/tamimresearch/weather-detection-image-dataset)
- [weather-dataset](https://www.kaggle.com/datasets/jehanbhathena/weather-dataset)

---

## Laporan Klasifikasi Detail

| Kelas                 | Precision | Recall | F1-Score | Support |
|------------------------|------------|---------|-----------|----------|
| Berawan (Cloudy)       | 0.84       | 0.90    | 0.87      | 60       |
| Hujan (Rain)           | 0.84       | 0.98    | 0.91      | 60       |
| Cerah (Sunrise, Shiny) | 0.92       | 0.78    | 0.85      | 60       |
| Berkabut (Foggy)       | 0.98       | 0.90    | 0.94      | 60       |
| **Total / Accuracy**   | —          | —       | **0.89**  | 240      |
| **Macro Avg**          | 0.90       | 0.89    | 0.89      | 240      |
| **Weighted Avg**       | 0.90       | 0.89    | 0.89      | 240      |

---

## Confusion Matrix
![Confusion Matrix](build/experiments/results/confusion_matrix.png)

---

## Precision Recall Curve
![Precision Recall Curve](build/experiments/results/precision_recall_curve.png)

---

## ROC Curve
![ROC Curve](build/experiments/results/roc_curve.png)

---

## Ringkasan

**Metode**
- **Ekstraksi Fitur:** Kombinasi HOG (bentuk), Color Histogram (warna), LBP (tekstur lokal), dan Filter Gabor (tekstur multi-skala).
- **Reduksi Dimensi:** PCA untuk mengatasi *curse of dimensionality* dan overfitting.
- **Klasifikasi:** Support Vector Machine (SVM) dengan kernel RBF.
- **Dataset:** Kaggle — 4 kelas, ~1200 gambar.
- **Hasil Akhir:** Akurasi **89.17%** pada set data pengujian.

---

## Panduan

### Prasyarat
- Python 3.8+
- Git

### Instalasi

```bash
git clone https://github.com/seclususs/svm-models.git
cd svm-models
```

Buat dan aktifkan lingkungan virtual:

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

Instal dependensi:

```bash
pip install -r requirements.txt
```

---

## Cara Menjalankan Pelatihan

### 1. Pelatihan Model
Jalankan Jupyter Notebook untuk visibilitas proses:

```bash
jupyter notebook
```

Buka `build/notebooks/training.ipynb` dan jalankan semua sel. Model akan disimpan di `build/saved_models/`.

### 2. Melakukan Prediksi
Siapkan gambar baru di `build/data/new_images/`.  
Buka `build/notebooks/prediction.ipynb` dan jalankan setelah menyesuaikan nama file gambar.

---

# Panduan Aplikasi Web

## Prasyarat

- **Lingkungan sudah terinstal**  
  Pastikan Anda sudah mengikuti langkah-langkah instalasi, termasuk menjalankan:
  ```bash
  pip install -r requirements.txt
  ```

- **Model tersedia**  
  Pastikan file model `*.pkl` berada di:
  ```
  web/model/
  ```

- **Unduh Model:** [Release](https://github.com/seclususs/svm-models/releases)

---

## Langkah-langkah Menjalankan

### Pindah ke folder aplikasi (web)
Dari direktori root proyek, jalankan:
```bash
cd web
```

### Jalankan aplikasi Flask
```bash
python app.py
```

Aplikasi akan berjalan pada `http://127.0.0.1:5000` secara default (atau alamat yang ditampilkan di terminal).

### Akses aplikasi
Buka browser dan kunjungi:
```
http://127.0.0.1:5000
```

---

## Troubleshooting

- Jika muncul error `ModuleNotFoundError`, pastikan `venv` aktif dan dependensi sudah terpasang.  
- Jika model tidak ditemukan, periksa lokasi `web/model/svm_model_integrated.pkl`.  
- Jika port 5000 sudah dipakai, jalankan Flask pada port lain:

  ```bash
  python app.py --port 5001
  ```

---