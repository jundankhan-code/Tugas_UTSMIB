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


# --- VISUALIZATIONS (OPTIMIZED FOR VARIANCE) ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("📈 Tren Kumulatif Kunjungan Pasien")
    
    # 1. Agregasi data: Hitung jumlah pasien per Tanggal dan Departemen [cite: 861]
    df_counts = df_selection.groupby(['Tanggal', 'Departemen']).size().reset_index(name='Jumlah_Pasien')
    
    # 2. Membuat Stacked Area Chart sesuai gambar yang Anda inginkan
    # Menggunakan px.area untuk memberikan efek warna di bawah garis [cite: 926]
    fig_area = px.area(
        df_counts, 
        x="Tanggal", 
        y="Jumlah_Pasien", 
        color="Departemen", # Warna membedakan departemen [cite: 1029]
        markers=True,
        template="plotly_white",
        labels={"Jumlah_Pasien": "Total Pasien", "Tanggal": "Periode"},
        line_shape="linear"
    )
    
    # 3. Optimasi Hover & Interaktivitas agar data lengkap terlihat saat kursor menempel
    fig_area.update_layout(
        hovermode="x unified", # Menampilkan semua data departemen dalam satu kotak hover
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Memastikan sumbu Y mulai dari 0 untuk validitas data [cite: 1030]
    fig_area.update_yaxes(rangemode="tozero") 
    
    st.plotly_chart(fig_area, use_container_width=True)

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
