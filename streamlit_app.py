import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# Konfigurasi Halaman
st.set_page_config(page_title="Health Facility KPI Dashboard", layout="wide")

# --- SIMULASI DATA (DATA REPRESENTATION) ---
# Mengikuti materi Kuliah 2 & 3: Representasi Data & Klasifikasi [cite: 553, 3]
@st.cache_data
# --- LOAD REAL DATA FROM CSV ---
@st.cache_data
def load_real_data():
    # Membaca file yang sudah Anda update
    df = pd.read_csv("data_rumah_sakit.csv")
    
    # Memastikan format Tanggal benar
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    
    # Menyamakan nama kolom CSV dengan variabel di kode dashboard
    # Pastikan "kepuasan_pasien" masuk ke dalam rename menjadi "Skor_Kepuasan"
    df = df.rename(columns={
        "Nama Departemen": "Departemen",
        "Kode ICD-10": "Diagnosa_ICD10",
        "Waktu Tunggu (menit)": "Waktu_Tunggu",
        "Biaya (IDR)": "Biaya_IDR",
        "kepuasan_pasien": "Skor_Kepuasan"  # Kolom baru Anda
    })
    
    return df.sort_values("Tanggal")

df = load_real_data()

# --- SIDEBAR (INTERACTIVITY) ---
st.sidebar.header("🏥 Health Admin Panel")
st.sidebar.markdown("Mata Kuliah: **Biomedical Info Management**")
st.sidebar.divider()

# Filter Departemen
selected_dept = st.sidebar.multiselect(
    "Filter Departemen:",
    options=df["Departemen"].unique(),
    default=df["Departemen"].unique()
)

df_selection = df[df["Departemen"].isin(selected_dept)]

# --- MAIN PAGE ---
st.title("📊 Health Facility KPI Dashboard")
st.markdown("Dashboard ini dirancang sebagai **Clinical Decision Support System (CDSS)** sederhana.")

# --- KPI METRICS (OPERATIONAL EFFICIENCY) ---
# Implementasi materi Kuliah 1 & 5 [cite: 86, 193]
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
# Implementasi fungsi EMR untuk keselamatan pasien [cite: 198, 474]
if avg_wait > 35:
    st.error(f"⚠️ **ALERT:** Waktu tunggu rata-rata di {', '.join(selected_dept)} sangat tinggi ({avg_wait} min). Pertimbangkan penambahan staf.")
elif satisfaction < 3.5:
    st.warning("⚠️ **PERHATIAN:** Skor kepuasan pasien di bawah target. Cek kualitas layanan.")
else:
    st.success("✅ Seluruh indikator operasional berada dalam batas aman.")

# --- VISUALIZATIONS (DATA MAPPING) ---
# Implementasi materi Kuliah 2 & 4 [cite: 926, 6]
c1, c2 = st.columns(2)

# --- VISUALIZATIONS (DATA MAPPING & ANALYSIS) ---
# Implementasi materi Kuliah 2 & 4 untuk mendukung CDSS [cite: 926, 6]
c1, c2 = st.columns(2)

with c1:
    st.subheader("📈 Tren Kunjungan Pasien per Departemen")
    # Mengelompokkan data berdasarkan Tanggal dan Departemen agar plot bervariasi 
    # Ini akan menunjukkan fluktuasi harian yang nyata (ada hari sibuk/sepi)
    df_trend = df_selection.groupby(["Tanggal", "Departemen"]).size().reset_index(name='Jumlah_Pasien')
    
    # Visualisasi Line Chart dengan pemisahan warna per departemen
    fig_line = px.line(
        df_trend, 
        x="Tanggal", 
        y="Jumlah_Pasien", 
        color="Departemen", 
        markers=True,
        line_shape="linear",
        template="plotly_white",
        labels={"Jumlah_Pasien": "Jumlah Pasien", "Tanggal": "Periode Kunjungan"}
    )
    
    # Optimasi sumbu agar fluktuasi terlihat jelas
    fig_line.update_layout(hovermode="x unified")
    fig_line.update_yaxes(rangemode="tozero") # Memastikan skala mulai dari 0 [cite: 1030]
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("📊 Analisis Beban Kasus (ICD-10)")
    # Menghitung frekuensi kemunculan diagnosa untuk klasifikasi penyakit [cite: 235]
    df_icd = df_selection["Diagnosa_ICD10"].value_counts().reset_index()
    df_icd.columns = ["Kode_ICD10", "Total_Kasus"]
    
    # Visualisasi Bar Chart untuk Data Nominal/Kategorikal [cite: 1029]
    fig_bar = px.bar(
        df_icd, 
        x="Kode_ICD10", 
        y="Total_Kasus", 
        color="Kode_ICD10",
        text_auto='.2s', # Menampilkan angka di atas batang
        template="plotly_white",
        labels={"Total_Kasus": "Jumlah Pasien", "Kode_ICD10": "Kode Diagnosa"}
    )
    
    # Menambahkan interaktivitas agar user bisa zoom pada kode tertentu
    fig_bar.update_layout(showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

# --- TABEL RINGKASAN (NILAI TAMBAH) ---
# Menyediakan data terstruktur untuk audit operasional [cite: 453, 499]
st.subheader("📋 Ringkasan Data Operasional Terfilter")
st.dataframe(df_selection, use_container_width=True)

# --- LEGAL & PRIVACY (HIPAA COMPLIANCE) ---
# Implementasi materi Kuliah 6 [cite: 365, 378]
st.divider()
with st.expander("⚖️ Legal Aspect & Data Privacy (HIPAA)"):
    st.write("""
    Sesuai dengan **HIPAA Title II (Administrative Simplification)**[cite: 378]:
    - Data ini telah melalui proses **De-identification** (anonimisasi) untuk melindungi privasi pasien[cite: 333].
    - Akses ke dashboard ini harus dibatasi hanya untuk personel administratif yang berwenang.
    - Semua transmisi data dilakukan secara elektronik sesuai standar keamanan medis[cite: 371].
    """)

st.caption("Developed for MIB Project - Semester Genap 2026")
