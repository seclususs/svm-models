import re

def sanitize_for_filename(text):
    if not isinstance(text, str):
        return "default"
    
    s = text.lower()

    weather_map = {
        "cerah berawan": "cerah_berawan",
        "berawan dan berkabut": "berawan_berkabut",
        "cerah berkabut": "cerah_berkabut",
        "mendung": "mendung",
        "hujan berkabut": "hujan_berkabut",
        "hujan cerah": "hujan_cerah"
    }
    for key, value in weather_map.items():
        if key in s:
            return value
    
    s = re.split(r'[\s(]', s)[0]
    return s

def get_human_readable_prediction(confidences):
    """
    Menganalisis seluruh distribusi probabilitas untuk menghasilkan kesimpulan
    cuaca yang objektif dan informatif.
    """
    if not confidences:
        return "Tidak Diketahui", "default", "Data probabilitas tidak tersedia."

    top_class, top_prob = confidences[0]
    second_class, second_prob = confidences[1] if len(confidences) > 1 else (None, 0)
    third_class, third_prob = confidences[2] if len(confidences) > 2 else (None, 0)

    prediction_name = top_class
    icon_base_name = top_class
    description = ""

    # POLA 1: SANGAT DOMINAN
    if top_prob >= 75:
        prediction_name = top_class
        icon_base_name = top_class
        description = f"Kondisi cuaca teridentifikasi secara definitif sebagai <strong>{top_class}</strong>. Model memiliki keyakinan tinggi ({top_prob}%) karena sinyal untuk cuaca lain sangat minimal."

    # POLA 2: DUA KUTUB (DUA CUACA BERSAING)
    elif (top_prob - second_prob) < 25 and (top_prob + second_prob) > 70 and third_prob < 15:
        prob_map = dict(confidences)
        top_simple = top_class.split(' ')[0]
        second_simple = second_class.split(' ')[0]

        # Logika kombinasi cuaca
        if {top_simple, second_simple} == {"Cerah", "Berawan"}:
            prediction_name = "Cerah Berawan"
            icon_base_name = "Cerah Berawan"
            description = f"Gambar ini menunjukkan kondisi campuran antara <strong>Cerah</strong> ({prob_map.get('Cerah (Sunrise, Shiny)', 0)}%) dan <strong>Berawan</strong> ({prob_map.get('Berawan (Cloudy)', 0)}%), mengarah pada kesimpulan cuaca cerah berawan."
        
        elif {top_simple, second_simple} == {"Berawan", "Hujan"}:
            prediction_name = "Mendung"
            icon_base_name = "Mendung"
            description = f"Langit yang sangat <strong>Berawan</strong> ({prob_map.get('Berawan (Cloudy)', 0)}%) disertai probabilitas <strong>Hujan</strong> yang signifikan ({prob_map.get('Hujan (Rain)', 0)}%). Ini adalah kondisi mendung dengan potensi hujan."

        elif {top_simple, second_simple} == {"Berawan", "Berkabut"}:
            prediction_name = "Berawan dan Berkabut"
            icon_base_name = "Berawan dan Berkabut"
            description = f"Terdeteksi kombinasi kuat antara kondisi <strong>Berawan</strong> ({prob_map.get('Berawan (Cloudy)', 0)}%) dan <strong>Berkabut</strong> ({prob_map.get('Berkabut (Foggy)', 0)}%), menandakan cuaca mendung disertai kabut."

        elif {top_simple, second_simple} == {"Cerah", "Berkabut"}:
            prediction_name = "Cerah Berkabut"
            icon_base_name = "Cerah Berkabut"
            description = f"Pemandangan menunjukkan adanya sinar matahari yang mencoba menembus lapisan kabut. Probabilitas untuk <strong>Cerah</strong> ({prob_map.get('Cerah (Sunrise, Shiny)', 0)}%) dan <strong>Berkabut</strong> ({prob_map.get('Berkabut (Foggy)', 0)}%) sama-sama tinggi."
        
        elif {top_simple, second_simple} == {"Hujan", "Berkabut"}:
            prediction_name = "Hujan Berkabut"
            icon_base_name = "Hujan Berkabut"
            description = f"Kombinasi antara <strong>Hujan</strong> ({prob_map.get('Hujan (Rain)', 0)}%) dan <strong>Berkabut</strong> ({prob_map.get('Berkabut (Foggy)', 0)}%) terdeteksi, menandakan hujan yang disertai dengan kabut tebal dan jarak pandang rendah."

        elif {top_simple, second_simple} == {"Cerah", "Hujan"}:
            prediction_name = "Hujan Cerah (Sunshower)"
            icon_base_name = "Hujan Cerah"
            description = f"Fenomena unik di mana <strong>Hujan</strong> ({prob_map.get('Hujan (Rain)', 0)}%) turun saat matahari masih <strong>Cerah</strong> ({prob_map.get('Cerah (Sunrise, Shiny)', 0)}%). Kondisi ini sering disebut sebagai 'sunshower'."

        else:
            prediction_name = f"Transisi: {top_simple}/{second_simple}"
            icon_base_name = top_class
            description = f"Model mengidentifikasi dua skenario cuaca yang paling mungkin: <strong>{top_class}</strong> ({top_prob}%) dan <strong>{second_class}</strong> ({second_prob}%). Ini adalah kondisi transisi di antara keduanya."

    # POLA 3: KOMPLEKS / TRANSISI
    elif top_prob < 65 and second_prob > 20 and third_prob > 10:
        prediction_name = f"Cuaca Kompleks ({top_class.split(' ')[0]})"
        icon_base_name = top_class
        description = f"Pemandangan ini memiliki karakteristik dari beberapa jenis cuaca. Kondisi dominan adalah <strong>{top_class}</strong> ({top_prob}%), namun juga terdeteksi adanya elemen <strong>{second_class}</strong> ({second_prob}%)."

    # POLA 4: STANDAR
    else:
        prediction_name = top_class
        icon_base_name = top_class
        secondary_influence = ""
        if second_prob > 15:
            secondary_influence = f", dengan pengaruh sekunder dari kondisi <strong>{second_class}</strong> ({second_prob}%)"
        description = f"Kondisi cuaca utama teridentifikasi sebagai <strong>{top_class}</strong> (probabilitas {top_prob}%){secondary_influence}."

    icon_name = sanitize_for_filename(icon_base_name)

    return prediction_name, icon_name, description
