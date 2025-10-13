"""
Modul untuk logika interpretasi hasil prediksi model.

Fungsi-fungsi dalam modul ini tidak hanya mengambil kelas dengan probabilitas
tertinggi, tetapi juga menganalisis distribusi probabilitas secara keseluruhan
untuk memberikan prediksi yang lebih kontekstual dan informatif. Ini termasuk
penggunaan entropi untuk mengukur ketidakpastian dan aturan berbasis domain
untuk mengidentifikasi kondisi cuaca campuran.
"""

import re
import numpy as np

def sanitize_for_filename(text):
    """
    Membersihkan dan mengubah teks prediksi menjadi nama berkas yang aman.

    Fungsi ini mengubah teks menjadi huruf kecil, mengganti spasi dengan garis bawah,
    dan menggunakan pemetaan khusus untuk kondisi cuaca yang kompleks. Tujuannya
    adalah untuk menghasilkan nama yang dapat digunakan untuk mencocokkan dengan
    nama berkas ikon (misalnya, 'Cerah Berawan' -> 'cerah_berawan.svg').

    Args:
        text (str): Teks prediksi mentah (misalnya, "Cerah Berawan").

    Returns:
        str: Nama berkas yang telah dibersihkan.
    """
    if not isinstance(text, str):
        return "default"
    
    s = text.lower()

    # Pemetaan spesifik untuk mengubah frasa menjadi nama berkas ikon.
    weather_map = {
        "cerah berawan": "cerah_berawan",
        "berawan dan berkabut": "berawan_berkabut",
        "cerah berkabut": "cerah_berkabut",
        "mendung": "mendung",
        "hujan berkabut": "hujan_berkabut",
        "hujan disertai kabut": "hujan_berkabut",
        "hujan cerah": "hujan_cerah",
        "cuaca campuran": "default" # Ikon cadangan untuk kondisi tidak pasti.
    }
    for key, value in weather_map.items():
        if key in s:
            return value
    
    # Jika tidak ada pemetaan yang cocok, gunakan kata pertama dari teks.
    s = re.split(r'[\s(]', s)[0]
    return s

def smart_predict(confidences):
    """
    Menganalisis distribusi probabilitas untuk menghasilkan prediksi yang cerdas.

    Fungsi ini menerapkan beberapa lapisan logika:
    1.  Menghitung entropi Shannon untuk mengukur ketidakpastian prediksi. Jika entropi tinggi,
        hasilnya diklasifikasikan sebagai "Cuaca Campuran".
    2.  Jika satu kelas memiliki probabilitas yang sangat dominan (>= 75%), kelas tersebut
        langsung dipilih sebagai hasil akhir.
    3.  Menerapkan serangkaian aturan berbasis domain untuk mengidentifikasi kondisi cuaca
        kompleks seperti "Mendung", "Cerah Berawan", atau "Hujan Cerah" dengan
        menganalisis tiga kelas teratas.
    4.  Jika tidak ada aturan di atas yang terpenuhi, fungsi akan kembali ke prediksi standar
        berdasarkan kelas dengan probabilitas tertinggi.

    Args:
        confidences (list of tuple): Daftar tuple, di mana setiap tuple berisi
                                     nama kelas dan skor kepercayaannya (0-100).
                                     Daftar ini diasumsikan sudah diurutkan dari
                                     kepercayaan tertinggi ke terendah.

    Returns:
        tuple: Sebuah tuple berisi tiga elemen:
               - prediction_name (str): Nama prediksi yang ramah pengguna.
               - icon_base_name (str): Nama dasar untuk berkas ikon.
               - description (str): Deskripsi HTML yang menjelaskan hasil prediksi.
    """
    if not confidences:
        return "Tidak Diketahui", "default", "Data probabilitas tidak tersedia."

    # 1. Kalkulasi Entropi untuk mengukur ketidakpastian
    probs = np.array([p for _, p in confidences]) / 100.0
    probs[probs == 0] = 1e-9  # Menghindari galat log(0) dengan nilai kecil.
    entropy = -np.sum(probs * np.log2(probs))
    
    # Entropi maksimal untuk 4 kelas adalah 2.0. Nilai di atas ambang batas ini
    # dianggap sangat tidak pasti.
    ENTROPY_THRESHOLD = 1.6 

    prob_map = dict(confidences)
    top_class, top_prob = confidences[0]
    second_class, second_prob = confidences[1] if len(confidences) > 1 else (None, 0)
    third_class, third_prob = confidences[2] if len(confidences) > 2 else (None, 0)

    # 2. Kasus Entropi Tinggi / Ketidakpastian Tinggi
    if entropy > ENTROPY_THRESHOLD:
        prediction_name = "Cuaca Campuran"
        icon_base_name = top_class  # Gunakan ikon kelas teratas sebagai cadangan.
        description = (f"Kondisi cuaca sangat tidak pasti dan menunjukkan campuran dari beberapa elemen. "
                       f"Prediksi teratas adalah <strong>{top_class}</strong> ({top_prob}%), "
                       f"namun <strong>{second_class}</strong> ({second_prob}%) juga memiliki probabilitas signifikan. "
                       f"Entropi distribusi ({entropy:.2f}) yang tinggi menandakan ketidakpastian model.")
        return prediction_name, sanitize_for_filename(icon_base_name), description

    # 3. Kasus Prediksi Dominan (keyakinan tinggi pada satu kelas)
    if top_prob >= 75:
        prediction_name = top_class
        icon_base_name = top_class
        description = (f"Kondisi cuaca teridentifikasi secara definitif sebagai <strong>{top_class}</strong>. "
                       f"Model memiliki keyakinan sangat tinggi ({top_prob}%) pada prediksi ini.")
        return prediction_name, sanitize_for_filename(icon_base_name), description

    # 4. Aturan Kompleks berdasarkan 3 Kelas Teratas
    top_three_classes = {c for c, p in confidences[:3]}

    # Aturan: Kondisi Hujan, Berawan, dan Berkabut
    if {"Hujan", "Berawan", "Berkabut"}.issubset(top_three_classes) and (prob_map.get("Hujan", 0) + prob_map.get("Berkabut", 0) + prob_map.get("Berawan", 0)) > 70:
        prediction_name = "Hujan Disertai Kabut"
        icon_base_name = "Hujan Berkabut"
        description = (f"Terdeteksi kondisi cuaca kompleks yang melibatkan <strong>Hujan</strong> ({prob_map.get('Hujan', 0)}%), "
                       f"<strong>Berkabut</strong> ({prob_map.get('Berkabut', 0)}%), dan tutupan awan tebal (<strong>Berawan</strong>, {prob_map.get('Berawan', 0)}%). "
                       f"Ini mengindikasikan hujan dengan jarak pandang rendah.")
        return prediction_name, sanitize_for_filename(icon_base_name), description

    # Aturan: Mendung (kombinasi Berawan + Hujan)
    if {"Berawan", "Hujan"}.issubset(top_three_classes) and (top_class in ["Berawan", "Hujan"]) and (second_class in ["Berawan", "Hujan"]):
        prediction_name = "Mendung"
        icon_base_name = "Mendung"
        description = (f"Langit yang sangat <strong>Berawan</strong> ({prob_map.get('Berawan', 0)}%) disertai probabilitas <strong>Hujan</strong> "
                       f"yang signifikan ({prob_map.get('Hujan', 0)}%). Ini adalah kondisi mendung dengan potensi hujan.")
        return prediction_name, sanitize_for_filename(icon_base_name), description

    # Aturan: Cerah Berawan (kombinasi Cerah + Berawan)
    if {"Cerah", "Berawan"}.issubset(top_three_classes) and (top_class in ["Cerah", "Berawan"]) and (second_class in ["Cerah", "Berawan"]):
        prediction_name = "Cerah Berawan"
        icon_base_name = "Cerah Berawan"
        description = (f"Gambar ini menunjukkan kondisi campuran antara <strong>Cerah</strong> ({prob_map.get('Cerah', 0)}%) "
                       f"dan <strong>Berawan</strong> ({prob_map.get('Berawan', 0)}%), mengarah pada kesimpulan cuaca cerah berawan.")
        return prediction_name, sanitize_for_filename(icon_base_name), description

    # Aturan: Hujan Cerah (Sunshower) dengan pemeriksaan domain
    if {"Hujan", "Cerah"}.issubset(top_three_classes) and third_prob < 15: # Pengetahuan domain: Sunshower jarang memiliki komponen ketiga yang kuat
        prediction_name = "Hujan Cerah (Sunshower)"
        icon_base_name = "Hujan Cerah"
        description = (f"Fenomena unik di mana <strong>Hujan</strong> ({prob_map.get('Hujan', 0)}%) turun saat matahari masih <strong>Cerah</strong> "
                       f"({prob_map.get('Cerah', 0)}%). Kondisi ini sering disebut sebagai 'sunshower'.")
        return prediction_name, sanitize_for_filename(icon_base_name), description

    # 5. Kasus Standar (Fallback jika tidak ada aturan yang cocok)
    prediction_name = top_class
    icon_base_name = top_class
    secondary_influence = ""
    # Menambahkan informasi tentang kelas kedua jika probabilitasnya cukup signifikan.
    if second_prob > 15:
        secondary_influence = f", dengan pengaruh sekunder dari kondisi <strong>{second_class}</strong> ({second_prob}%)"
    description = (f"Kondisi cuaca utama teridentifikasi sebagai <strong>{top_class}</strong> (probabilitas {top_prob}%){secondary_influence}.")

    return prediction_name, sanitize_for_filename(icon_base_name), description
