import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman
st.set_page_config(page_title="Health Facility KPI Dashboard", layout="wide")

@st.cache_data
def load_real_data():
    df = pd.read_csv("data_rumah_sakit.csv")
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    # Rename kolom agar konsisten dengan kode
    df = df.rename(columns={
        "Nama Departemen": "Departemen",
        "Kode ICD-10": "Diagnosa_ICD10",
        "Waktu Tunggu (menit)": "Waktu_Tunggu",
        "Biaya (IDR)": "Biaya_IDR",
        "Kepuasan Pasien": "Skor_Kepuasan"
    })
    return df.sort_values("Tanggal")

df = load_real_data()

# --- DEFINISI WARNA TETAP (COLOR DISCRETE MAP) ---
# Menjamin IGD tetap biru, Neurologi tetap oranye, dll. sesuai permintaan Anda
color_map = {
    "IGD": "#1f77b4",        # Biru
    "Neurologi": "#ff7f0e",  # Oranye
    "Kardiologi": "#2ca02c", # Hijau
    "Pediatri": "#d62728",   # Merah
    "Ortopedi": "#9467bd",   # Ungu
    "Total": "#333333"       # Abu-abu gelap untuk akumulasi
}

# --- SIDEBAR FILTER ---
st.sidebar.header("🏥 Health Admin Panel")
dept_options = list(df["Departemen"].unique())
dept_options.append("Total") # Menambahkan opsi Total

selected_dept = st.sidebar.multiselect(
    "Filter Departemen:",
    options=dept_options,
    default=dept_options[:-1] # Default semua kecuali Total
)

# --- LOGIKA FILTER DATA ---
if "Total" in selected_dept:
    # Jika Total dipilih, kita buat dataframe bayangan untuk 'Total'
    df_total = df.copy()
    df_total["Departemen"] = "Total"
    
    # Gabungkan data departemen asli yang dipilih dengan data Total
    depts_only = [d for d in selected_dept if d != "Total"]
    df_selection = pd.concat([df[df["Departemen"].isin(depts_only)], df_total])
else:
    df_selection = df[df["Departemen"].isin(selected_dept)]

# --- MAIN PAGE ---
st.title("📊 Health Facility KPI Dashboard")

# --- KPI METRICS ---
col1, col2, col3 = st.columns(3)
# Menggunakan data murni (tanpa duplikasi 'Total') untuk KPI agar angka tidak double
df_kpi = df[df["Departemen"].isin([d for d in selected_dept if d != "Total"])]
if df_kpi.empty: df_kpi = df # Fallback jika hanya pilih Total

with col1:
    st.metric("Rerata Waktu Tunggu", f"{round(df_kpi['Waktu_Tunggu'].mean(), 1)} Min")
with col2:
    st.metric("Total Revenue", f"Rp {df_kpi['Biaya_IDR'].sum():,}")
with col3:
    st.metric("Skor Kepuasan", f"{round(df_kpi['Skor_Kepuasan'].mean(), 1)}/5.0")

st.divider()

# --- VISUALIZATIONS (DYNAMIC RANGE) ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("📈 Tren Kunjungan Pasien")
    
    # Agregasi data harian [cite: 861]
    df_counts = df_selection.groupby(['Tanggal', 'Departemen']).size().reset_index(name='Jumlah_Pasien')
    
    # Hitung nilai max secara dinamis untuk menentukan rentang Y [cite: 1030]
    if not df_counts.empty:
        max_val_c1 = df_counts['Jumlah_Pasien'].max()
        # Logika buffer: jika > 30 tambah 20, jika < 30 tambah 10 (sesuai permintaan Anda)
        y_limit_c1 = max_val_c1 + (20 if max_val_c1 > 30 else 10)
    else:
        y_limit_c1 = 60 # Fallback jika data kosong

    fig_line = px.line(
        df_counts, 
        x="Tanggal", 
        y="Jumlah_Pasien", 
        color="Departemen",
        color_discrete_map=color_map, # Konsistensi warna [cite: 1029]
        markers=True,
        template="plotly_white"
    )
    
    fig_line.update_layout(hovermode="x unified")
    # Terapkan rentang dinamis hasil perhitungan
    fig_line.update_yaxes(range=[0, y_limit_c1]) 
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("📊 Analisis Kasus (ICD-10)")
    
    # Hitung frekuensi diagnosa [cite: 235]
    df_icd = df_kpi["Diagnosa_ICD10"].value_counts().reset_index()
    df_icd.columns = ["Kode_ICD10", "Total"]
    
    # Hitung nilai max dinamis untuk grafik batang
    if not df_icd.empty:
        max_val_c2 = df_icd['Total'].max()
        y_limit_c2 = max_val_c2 + (20 if max_val_c2 > 30 else 10)
    else:
        y_limit_c2 = 60

    fig_bar = px.bar(
        df_icd, x="Kode_ICD10", y="Total", 
        color="Total", color_continuous_scale="Viridis",
        text_auto=True, template="plotly_white"
    )
    
    # Terapkan rentang dinamis pada sumbu Y
    fig_bar.update_yaxes(range=[0, y_limit_c2])
    st.plotly_chart(fig_bar, use_container_width=True)
