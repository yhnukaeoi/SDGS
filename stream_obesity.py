import streamlit as st
import pandas as pd
import pickle
import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

# CSS untuk mempercantik tampilan
st.markdown("""
    <style>
        .main {
            background-color: #f7f9fc;
            padding: 20px;
            border-radius: 8px;
        }
        h1 {
            color: #4CAF50;
            text-align: center;
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
        .info-card {
            background-color: #ffffff;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Fungsi untuk memuat model
def load_model_pickle(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)

# Fungsi untuk prediksi
def predict(data, model, label_encoders, scaler, target_encoder):
    categorical_cols = ['Gender', 'CALC', 'FAVC', 'SMOKE', 'family_history_with_overweight', 'CAEC', 'MTRANS']
    numerical_cols = ['Age', 'Height', 'Weight', 'FCVC', 'NCP', 'CH2O', 'FAF', 'TUE']

    # Encode kategori
    for col in categorical_cols:
        data[col] = label_encoders[col].transform(data[col])

    # Standardisasi numerik
    data[numerical_cols] = scaler.transform(data[numerical_cols])

    # Prediksi
    prediction = model.predict(data)
    return target_encoder.inverse_transform(prediction)

# Fungsi untuk memberikan rekomendasi berdasarkan tingkat obesitas
def get_recommendations(prediction):
    recommendations = {
        "Insufficient_Weight": {
            "lifestyle": textwrap.fill("Tingkatkan asupan kalori Anda dan konsultasikan dengan ahli gizi untuk memastikan Anda mendapatkan nutrisi yang cukup.",
                                       width=50),
            "diet": textwrap.fill("Konsumsi makanan kaya nutrisi seperti kacang-kacangan, biji-bijian, susu penuh lemak, daging tanpa lemak, dan buah-buahan. Hindari makanan cepat saji meskipun berkalori tinggi.",
                             width=50)
        },
        "Normal_Weight": {
            "lifestyle":textwrap.fill( "Pertahankan pola makan seimbang dan rutin berolahraga untuk menjaga berat badan tetap stabil.",
                                 width=75),
            "diet": textwrap.fill("Konsumsilah biji-bijian utuh, protein tanpa lemak, sayuran, dan buah-buahan. Hindari makanan olahan.",
            width=80)

        },
        "Overweight_Level_I": {
            "lifestyle":textwrap.fill( "Tingkatkan aktivitas fisik seperti jalan cepat selama 30-45 menit setiap hari.",
                                      width=75),
            "diet": textwrap.fill( "Kurangi konsumsi makanan manis dan berlemak tinggi. Tambahkan lebih banyak sayuran, protein tanpa lemak, dan lemak sehat seperti kacang-kacangan."
                                  , width=80)
        },
        "Overweight_Level_II": {
            "lifestyle": "Pertimbangkan untuk bergabung dengan program kebugaran yang terstruktur dan kurangi kebiasaan duduk terlalu lama.",
            "diet": "Fokus pada pengendalian porsi. Tambahkan makanan tinggi serat, produk susu rendah lemak, dan batasi makanan yang digoreng."
        },
        "Obesity_Type_I": {
            "lifestyle":textwrap.fill( "Tingkatkan aktivitas aerobik dan konsultasikan dengan pelatih kebugaran untuk rutinitas latihan yang dipersonalisasi.",
                                      width=75),
            "diet":textwrap.fill( "Adopsi pola makan dengan defisit kalori. Tambahkan lebih banyak protein nabati dan batasi lemak jenuh."
                                 , width=80)
                                        
        },
        "Obesity_Type_II": {
            "lifestyle": "Dapatkan saran dari ahli gizi atau ahli diet untuk rencana yang dipersonalisasi dan fokus pada latihan kekuatan.",
            "diet": "Ikuti pola makan rendah karbohidrat dan tinggi protein. Hindari minuman manis dan pantau asupan kalori."
        }
    }
    return recommendations.get(prediction, {
        "lifestyle": "Tidak ada rekomendasi khusus.",
        "diet": "Tidak ada rekomendasi khusus."
    })

# Fungsi untuk menyisipkan data ke template gambar
def insert_data_to_image(template_path, output_path, user_data):
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", size=24)
    except:
        font = ImageFont.load_default()

    coordinates = {
        "Nama": (400, 295),
        "Tanggal": (400, 350),
        "Usia": (610, 630),
        "Tinggi": (610, 690),
        "Berat": (610, 740),
        "Sayur": (610, 790),
        "Makan": (610, 850),
        "Minum": (610, 900),
        "Fisik": (610, 950),
        "Teknologi": (610, 1010),
        "Gender": (610, 1070),
        "Alkohol": (610, 1120),
        "Kalori": (610, 1170),
        "Merokok": (610, 1220),
        "Keluarga_Obesitas": (610, 1280),
        "Ngemil": (610, 1330),
        "Transportasi": (610, 1390),
        "Prediksi": (150, 1480),
        "Rekomendasi": (150, 1550),
    }

    draw.text(coordinates["Nama"], f"{user_data['name']}", font=font, fill="black")
    draw.text(coordinates["Tanggal"], f"{user_data['date']}", font=font, fill="black")
    draw.text(coordinates["Usia"], f"{user_data['Age']} tahun", font=font, fill="black")
    draw.text(coordinates["Tinggi"], f"{user_data['Height']} cm", font=font, fill="black")
    draw.text(coordinates["Berat"], f"{user_data['Weight']} kg", font=font, fill="black")
    draw.text(coordinates["Sayur"], f"{user_data['FCVC']}", font=font, fill="black")
    draw.text(coordinates["Makan"], f"{user_data['NCP']} kali/hari", font=font, fill="black")
    draw.text(coordinates["Minum"], f"{user_data['CH2O']} liter", font=font, fill="black")
    draw.text(coordinates["Fisik"], f"{user_data['FAF']} jam", font=font, fill="black")
    draw.text(coordinates["Teknologi"], f"{user_data['TUE']} jam/hari", font=font, fill="black")
    draw.text(coordinates["Gender"], f"{user_data['Gender']}", font=font, fill="black")
    draw.text(coordinates["Alkohol"], f"{user_data['CALC']}", font=font, fill="black")
    draw.text(coordinates["Kalori"], f"{user_data['FAVC']}", font=font, fill="black")
    draw.text(coordinates["Merokok"], f"{user_data['SMOKE']}", font=font, fill="black")
    draw.text(coordinates["Alkohol"], f"{user_data['CALC']}", font=font, fill="black")
    draw.text(coordinates["Keluarga_Obesitas"], f"{user_data['family_history_with_overweight']}", font=font, fill="black")
    draw.text(coordinates["Ngemil"], f"{user_data['CAEC']}", font=font, fill="black")
    draw.text(coordinates["Transportasi"], f"{user_data['MTRANS']}", font=font, fill="black")
    draw.text(coordinates["Prediksi"], f"{user_data['prediction']}", font=font, fill="black")
    draw.text((coordinates["Rekomendasi"][0], coordinates["Rekomendasi"][1] + 30),
            f"Gaya Hidup: {recommendations['lifestyle']}", font=font, fill="black")
    draw.text((coordinates["Rekomendasi"][0], coordinates["Rekomendasi"][1] + 100),
            f"Pola Makan: {recommendations['diet']}", font=font, fill="black")

    img.save(output_path)
    return output_path

# Fungsi untuk mengonversi gambar ke PDF
def convert_image_to_pdf(image_path):
    img = Image.open(image_path)
    pdf_bytes = BytesIO()
    img.save(pdf_bytes, format='PDF')
    pdf_bytes.seek(0)
    return pdf_bytes

# Header
st.markdown("<h1>Prediksi Tingkat Obesitas</h1>", unsafe_allow_html=True)
st.markdown("<div class='info-card'>Masukkan informasi pribadi Anda di bawah untuk memprediksi tingkat obesitas Anda dan mendapatkan rekomendasi.</div>", unsafe_allow_html=True)

# Input pengguna
name = st.text_input("Nama Lengkap")
exam_date = st.date_input("Tanggal Pemeriksaan")
Age = st.number_input("Usia", min_value=1, max_value=100, value=30)
Height = st.number_input("Tinggi Badan (cm)", min_value=50, max_value=250, value=170)
Weight = st.number_input("Berat Badan (kg)", min_value=20, max_value=200, value=60)
FCVC = st.slider("Frekuensi konsumsi sayur (0-3)", min_value=0, max_value=3, value=2)
NCP = st.slider("Jumlah makanan per hari", min_value=1, max_value=5, value=3)
CH2O = st.slider("Asupan air harian (liter)", min_value=1, max_value=5, value=2)
FAF = st.slider("Aktivitas fisik mingguan (jam)", min_value=0, max_value=20, value=5)
TUE = st.slider("Waktu menggunakan teknologi (jam/hari)", min_value=0, max_value=24, value=2)

Gender = st.selectbox("Jenis Kelamin", ["Male", "Female"])
CALC = st.selectbox("Konsumsi alkohol", ["no", "sometimes", "frequently", "always"])
FAVC = st.selectbox("Konsumsi Makanan Tinggi Kalori", ["no", "yes"])
SMOKE = st.selectbox("Kebiasaan merokok", ["no", "yes"])
family_history_with_overweight = st.selectbox("Riwayat keluarga obesitas", ["no", "yes"])
CAEC = st.selectbox("Kebiasaan Ngemil", ["no", "Sometimes", "Frequently", "Always"])
MTRANS = st.selectbox("Transportasi utama", ["Walking", "Bike", "Motorbike", "Public Transportation", "Automobile"])

# Simpan input dalam DataFrame
user_input = pd.DataFrame({
    'Age': [Age],
    'Height': [Height],
    'Weight': [Weight],
    'FCVC': [FCVC],
    'NCP': [NCP],
    'CH2O': [CH2O],
    'FAF': [FAF],
    'TUE': [TUE],
    'Gender': [Gender],
    'CALC': [CALC],
    'FAVC': [FAVC],
    'SMOKE': [SMOKE],
    'family_history_with_overweight': [family_history_with_overweight],
    'CAEC': [CAEC],
    'MTRANS': [MTRANS]
})

# Load model
model_data = load_model_pickle('obesity_model.pkl')
model = model_data['model']
label_encoders = model_data['label_encoders']
scaler = model_data['scaler']
target_encoder = model_data['target_encoder']

# Prediksi
# Prediksi
if st.button('Prediksi Tingkat Obesitas'):
    prediction = predict(user_input, model, label_encoders, scaler, target_encoder)
    st.markdown("<h2>Hasil Prediksi</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='info-card'><strong>Tingkat Obesitas:</strong> {prediction[0]}</div>", unsafe_allow_html=True)

    recommendations = get_recommendations(prediction[0])
    st.markdown("<h2>Rekomendasi</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='info-card'><strong>Gaya Hidup:</strong> {recommendations['lifestyle']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='info-card'><strong>Pola Makan:</strong> {recommendations['diet']}</div>", unsafe_allow_html=True)

    # Sisipkan data ke template
    template_path = "Hasil.jpg"  # Ganti dengan path template Anda
    output_image_path = "Hasil_Updated.jpg"
    user_data = {
        "name": name,
        "date": exam_date,
        "Age": Age,
        "Height": Height,
        "Weight": Weight,
        "FCVC": FCVC,
        "NCP": NCP,
        "CH2O": CH2O,
        "FAF": FAF,
        "TUE": TUE,
        "Gender": Gender,
        "CALC": CALC,
        "FAVC": FAVC,
        "SMOKE": SMOKE,
        "family_history_with_overweight": family_history_with_overweight,
        "CAEC": CAEC,
        "MTRANS": MTRANS,
        "prediction": prediction[0],
       "recommendation": f"Gaya Hidup: {recommendations['lifestyle']}<br>Pola Makan: {recommendations['diet']}"

    }

    image_path = insert_data_to_image(template_path, output_image_path, user_data)
    st.image(image_path, caption="Hasil Template")

    # Konversi ke PDF dan unduh
    pdf_bytes = convert_image_to_pdf(image_path)
    st.download_button(
        label="Unduh PDF",
        data=pdf_bytes,
        file_name="Hasil_Prediksi_Obesitas.pdf",
        mime="application/pdf"
    )
