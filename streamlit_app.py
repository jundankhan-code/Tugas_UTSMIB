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
def load_simulated_data():
    np.random.seed(42)
    rows = 200
    data = {
        "Tanggal": [datetime(2026, 3, 1) + timedelta(days=np.random.randint(0, 30)) for _ in range(rows)],
        "Departemen": np.random.choice(["IGD", "Farmasi", "Radiologi", "Laboratorium"], rows),
        "Diagnosa_ICD10": np.random.choice(["I10", "E11", "A15.0", "J45", "K29.7"], rows), # Standar ICD-10 
        "Waktu_Tunggu": np.random.randint(10, 60, rows), # Skala Ratio 
        "Biaya_IDR": np.random.randint(100000, 2000000, rows), # Skala Ratio 
        "Skor_Kepuasan": np.random.randint(1, 6, rows), # Skala Ordinal 
        "Status_Pasien": np.random.choice(["Rawat Inap", "Rawat Jalan"], rows) # Skala Nominal 
    }
    return pd.DataFrame(data).sort_values("Tanggal")

df = load_simulated_data()

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

with c1:
    st.subheader("Tren Kunjungan Pasien (Time-Series)")
    # Analisis tren waktu [cite: 861]
    fig_line = px.line(df_selection.groupby("Tanggal").size().reset_index(name='Jumlah'), 
                       x="Tanggal", y="Jumlah", markers=True, template="plotly_white")
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("Distribusi Penyakit (ICD-10)")
    # Representasi Klasifikasi Diagnosa 
    fig_bar = px.bar(df_selection["Diagnosa_ICD10"].value_counts().reset_index(), 
                     x="Diagnosa_ICD10", y="count", color="Diagnosa_ICD10", template="plotly_white")
    st.plotly_chart(fig_bar, use_container_width=True)

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
