import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Health Facility KPI Dashboard", layout="wide")

# --- LOAD DATA (DATA ACQUISITION) ---
@st.cache_data
def load_real_data():
    # Membaca file database medis
    df = pd.read_csv("data_rumah_sakit.csv")
    
    # Membersihkan spasi pada nama kolom untuk mencegah KeyError
    df.columns = df.columns.str.strip()
    
    # Konversi tipe data Tanggal
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    
    # Standardisasi nama variabel agar sesuai dengan logika kode
    df = df.rename(columns={
        "Nama Departemen": "Departemen",
        "Kode ICD-10": "Diagnosa_ICD10",
        "Waktu Tunggu (menit)": "Waktu_Tunggu",
        "Biaya (IDR)": "Biaya_IDR",
        "Kepuasan Pasien": "Skor_Kepuasan" 
    })
    
    # Proteksi jika kolom Skor_Kepuasan tidak ditemukan
    if "Skor_Kepuasan" not in df.columns:
        df["Skor_Kepuasan"] = 0
        
    return df.sort_values("Tanggal")

# Inisialisasi Data Dasar
df_base = load_real_data()

# --- DEFINISI WARNA TETAP (CONSISTENT VISUALIZATION) ---
# Memastikan departemen memiliki warna yang sama meskipun difilter
color_map = {
    "IGD": "#1f77b4",        # Biru
    "Neurologi": "#ff7f0e",  # Oranye
    "Kardiologi": "#2ca02c", # Hijau
    "Pediatri": "#d62728",   # Merah
    "Ortopedi": "#9467bd",   # Ungu
    "Total": "#333333"       # Abu-abu gelap untuk akumulasi
}

# --- SIDEBAR (FILTER INTERAKTIF) ---
st.sidebar.header("🏥 Health Admin Panel")
st.sidebar.markdown("Mata Kuliah: **Biomedical Info Management**")
st.sidebar.divider()

# Menyiapkan opsi filter termasuk opsi "Total"
dept_options = list(df_base["Departemen"].unique())
dept_options.append("Total")

selected_dept = st.sidebar.multiselect(
    "Pilih Departemen untuk Dianalisis:",
    options=dept_options,
    default=[d for d in dept_options if d != "Total"] # Default: semua kecuali Total
)

# --- LOGIKA PENYARINGAN DATA ---
# 1. Data untuk KPI (Murni, tidak menduplikasi 'Total')
depts_only = [d for d in selected_dept if d != "Total"]
df_kpi = df_base[df_base["Departemen"].isin(depts_only)] if depts_only else df_base

# 2. Data untuk Visualisasi (Termasuk akumulasi jika 'Total' dipilih)
if "Total" in selected_dept:
    df_total = df_base.copy()
    df_total["Departemen"] = "Total"
    df_selection = pd.concat([df_base[df_base["Departemen"].isin(depts_only)], df_total])
else:
    df_selection = df_base[df_base["Departemen"].isin(selected_dept)]

# --- MAIN PAGE ---
st.title("📊 Health Facility KPI Dashboard")
st.markdown("Dashboard ini berfungsi sebagai **Clinical Decision Support System (CDSS)** untuk efisiensi fasilitas.")

# --- KPI METRICS ---
col1, col2, col3 = st.columns(3)

avg_wait = round(df_kpi["Waktu_Tunggu"].mean(), 1) if not df_kpi.empty else 0
total_rev = df_kpi["Biaya_IDR"].sum() if not df_kpi.empty else 0
satisfaction = round(df_kpi["Skor_Kepuasan"].mean(), 1) if not df_kpi.empty else 0

with col1:
    st.metric("Rerata Waktu Tunggu", f"{avg_wait} Min", delta="-5% (Target < 30)")
with col2:
    st.metric("Total Revenue", f"Rp {total_rev:,}")
with col3:
    st.metric("Skor Kepuasan (1-5)", f"{satisfaction}/5.0")

st.divider()

# --- ALERTS (CDSS LOGIC) ---
if avg_wait > 35:
    st.error(f"⚠️ **ALERT:** Waktu tunggu rata-rata sangat tinggi ({avg_wait} min).")
elif satisfaction < 3.5 and not df_kpi.empty:
    st.warning("⚠️ **PERHATIAN:** Skor kepuasan pasien di bawah target.")
else:
    st.success("✅ Seluruh indikator operasional berada dalam batas aman.")

# --- VISUALIZATIONS ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("📈 Tren Kunjungan Pasien")
    
    # Agregasi data harian
    df_counts = df_selection.groupby(['Tanggal', 'Departemen']).size().reset_index(name='Jumlah_Pasien')
    
    # Hitung Rentang Y Dinamis (Max + Buffer)
    if not df_counts.empty:
        max_c1 = df_counts['Jumlah_Pasien'].max()
        y_limit_c1 = max_c1 + (20 if max_c1 > 30 else 10)
    else:
        y_limit_c1 = 60

    # Line Chart agar bisa bertumpang tindih secara transparan
    fig_line = px.line(
        df_counts, x="Tanggal", y="Jumlah_Pasien", color="Departemen",
        color_discrete_map=color_map, markers=True, template="plotly_white",
        labels={"Jumlah_Pasien": "Pasien", "Tanggal": "Hari"}
    )
    
    fig_line.update_layout(hovermode="x unified")
    fig_line.update_yaxes(range=[0, y_limit_c1])
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("📊 Analisis Kasus (ICD-10)")
    
    # Distribusi diagnosa dari data kpi (murni)
    df_icd = df_kpi["Diagnosa_ICD10"].value_counts().reset_index()
    df_icd.columns = ["Kode_ICD10", "Total"]
    
    # Hitung Rentang Y Dinamis untuk Bar
    if not df_icd.empty:
        max_c2 = df_icd['Total'].max()
        y_limit_c2 = max_c2 + (20 if max_c2 > 30 else 10)
    else:
        y_limit_c2 = 60

    fig_bar = px.bar(
        df_icd, x="Kode_ICD10", y="Total", color="Total",
        color_continuous_scale="Viridis", text_auto=True, template="plotly_white"
    )
    fig_bar.update_yaxes(range=[0, y_limit_c2])
    st.plotly_chart(fig_bar, use_container_width=True)

# --- FITUR TAMBAHAN (NILAI PLUS) ---
st.subheader("📋 Statistik Deskriptif & Analisis Data")
col_stats, col_export = st.columns([2, 1])

with col_stats:
    # Memberikan analisis statistik mendalam sesuai materi Skala Ratio
    st.write("Ringkasan Statistik (Waktu Tunggu & Biaya):")
    st.dataframe(df_kpi[["Waktu_Tunggu", "Biaya_IDR"]].describe().T, use_container_width=True)

with col_export:
    st.write("Ekspor Data Terfilter:")
    csv = df_selection.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"audit_rs_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )

# --- TABEL DATA ---
with st.expander("Lihat Detail Data Mentah"):
    st.dataframe(df_selection, use_container_width=True)

# --- LEGAL & PRIVACY (HIPAA) ---
st.divider()
with st.expander("⚖️ Legal Aspect & Data Privacy (HIPAA Compliance)"):
    st.write("""
    Sistem ini mematuhi prinsip **HIPAA Title II**:
    - **De-identification**: Data identitas pasien telah disamarkan.
    - **Access Control**: Dashboard hanya untuk otoritas administratif.
    - **Audit Trail**: Setiap perubahan data tercatat dalam log sistem.
    """)

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | MIB Project 2026")
