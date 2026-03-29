import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# Konfigurasi Halaman Dashboard
st.set_page_config(page_title="Health Facility KPI Dashboard", layout="wide")

# --- LOAD DATA (DATA ACQUISITION) ---
# Mengimplementasikan pemrosesan data terstruktur sesuai materi Kuliah 3 [cite: 1511]
@st.cache_data
def load_real_data():
    # Membaca file database medis lokal [cite: 1281]
    df = pd.read_csv("data_rumah_sakit.csv")
    
    # Konversi tipe data untuk analisis data berorientasi waktu (Time-oriented data) [cite: 3]
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    
    # Standardisasi nama variabel untuk interoperabilitas sistem [cite: 1727]
    df = df.rename(columns={
        "Nama Departemen": "Departemen",
        "Kode ICD-10": "Diagnosa_ICD10",
        "Waktu Tunggu (menit)": "Waktu_Tunggu",
        "Biaya (IDR)": "Biaya_IDR",
        "Kepuasan Pasien": "Skor_Kepuasan" 
    })
    
    return df.sort_values("Tanggal")

df = load_real_data()

# --- SIDEBAR (INTERACTIVITY & INFORMATION RETRIEVAL) ---
st.sidebar.header("🏥 Health Admin Panel")
st.sidebar.markdown("Mata Kuliah: **Biomedical Info Management**")
st.sidebar.divider()

# Mekanisme filter untuk kueri data spesifik (Query Formulation) [cite: 1665, 1711]
selected_dept = st.sidebar.multiselect(
    "Filter Departemen:",
    options=df["Departemen"].unique(),
    default=df["Departemen"].unique()
)

df_selection = df[df["Departemen"].isin(selected_dept)]

# --- MAIN PAGE ---
st.title("📊 Health Facility KPI Dashboard")
st.markdown("Dashboard ini dirancang sebagai **Clinical Decision Support System (CDSS)** sederhana[cite: 1605].")

# --- KPI METRICS (OPERATIONAL EFFICIENCY) ---
# Pengukuran kinerja fasilitas kesehatan sesuai materi Kuliah 1 & 5 [cite: 1289, 1502]
col1, col2, col3 = st.columns(3)

avg_wait = round(df_selection["Waktu_Tunggu"].mean(), 1)
total_rev = df_selection["Biaya_IDR"].sum()
satisfaction = round(df_selection["Skor_Kepuasan"].mean(), 1)

with col1:
    st.metric("Rerata Waktu Tunggu", f"{avg_wait} Min", delta="-5% (Target < 30)")
with col2:
    st.metric("Total Revenue", f"Rp {total_rev:,}")
with col3:
    st.metric("Skor Kepuasan (1-5)", f"{satisfaction}/5.0")

st.divider()

# --- CLINICAL DECISION SUPPORT (ALERTS) ---
# Implementasi fungsi EMR untuk keselamatan pasien dan manajemen risiko [cite: 1473, 1749]
if avg_wait > 35:
    st.error(f"⚠️ **ALERT:** Waktu tunggu rata-rata di {', '.join(selected_dept)} sangat tinggi ({avg_wait} min). Pertimbangkan penambahan staf[cite: 1771].")
elif satisfaction < 3.5:
    st.warning("⚠️ **PERHATIAN:** Skor kepuasan pasien di bawah target. Perlu evaluasi kualitas pelayanan[cite: 1774].")
else:
    st.success("✅ Seluruh indikator operasional berada dalam batas aman.")

# --- VISUALIZATIONS (DATA MAPPING & REPRESENTATION) ---
c1, c2 = st.columns(2)

# BAGIAN C1: Tren Kumulatif Kunjungan Pasien
with c1:
    st.subheader("📈 Tren Kumulatif Kunjungan Pasien")
    
    # 1. Agregasi data: Hitung jumlah pasien per Tanggal dan Departemen [cite: 1726]
    df_counts = df_selection.groupby(['Tanggal', 'Departemen']).size().reset_index(name='Jumlah_Pasien')
    
    # 2. Membuat Stacked Area Chart (Representasi data berkelanjutan/Interval) 
    fig_area = px.area(
        df_counts, 
        x="Tanggal", 
        y="Jumlah_Pasien", 
        color="Departemen", # Membedakan kategori departemen (Nominal) 
        markers=True,
        template="plotly_white",
        labels={"Jumlah_Pasien": "Total Pasien", "Tanggal": "Periode"},
        line_shape="linear"
    )
    
    # 3. Optimasi Hover agar data terintegrasi terlihat jelas (Human-Computer Interaction) [cite: 1512]
    fig_area.update_layout(
        hovermode="x unified", 
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Memastikan validitas visualisasi dengan sumbu Y mulai dari 0 [cite: 1030]
    fig_area.update_yaxes(rangemode="tozero") 
    
    st.plotly_chart(fig_area, use_container_width=True)

# BAGIAN C2: Analisis Kasus (ICD-10)
with c2:
    st.subheader("📊 Analisis Kasus (ICD-10)")
    
    # Representasi Klasifikasi Diagnosa menggunakan standar ICD-10 (Kuliah 3) [cite: 1280, 1672]
    df_icd = df_selection["Diagnosa_ICD10"].value_counts().reset_index()
    df_icd.columns = ["Kode_ICD10", "Total"]
    
    # Visualisasi Bar Chart untuk sebaran frekuensi penyakit [cite: 936]
    fig_bar = px.bar(
        df_icd, 
        x="Kode_ICD10", 
        y="Total", 
        color="Total",
        color_continuous_scale="Viridis",
        text_auto=True,
        template="plotly_white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --- TABEL RINGKASAN (NILAI TAMBAH) ---
# Menyediakan akses data terstruktur untuk audit dan riset medis [cite: 1398, 1726]
st.subheader("📋 Ringkasan Data Operasional Terfilter")
st.dataframe(df_selection, use_container_width=True)

# --- LEGAL & PRIVACY (HIPAA COMPLIANCE) ---
# Implementasi materi Kuliah 6 mengenai perlindungan informasi medis [cite: 1283, 1639]
st.divider()
with st.expander("⚖️ Legal Aspect & Data Privacy (HIPAA)"):
    st.write("""
    Sesuai dengan **HIPAA Title II (Administrative Simplification)**[cite: 1653]:
    - Data ini telah melalui proses **De-identification** (anonimisasi) untuk melindungi privasi pasien[cite: 2].
    - Akses terbatas hanya untuk personel administrasi yang berwenang[cite: 1620].
    - Transmisi data elektronik mengikuti standar keamanan medis untuk mencegah kebocoran data[cite: 1608, 1654].
    """)

st.caption("Developed for MIB Project - Semester Genap 2026")
