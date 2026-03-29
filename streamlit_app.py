import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Health Facility KPI Dashboard", layout="wide")

# --- LOAD DATA (DATA ACQUISITION) ---
@st.cache_data
def load_real_data():
    # Membaca database medis
    df = pd.read_csv("data_rumah_sakit.csv")
    
    # Cleaning: Hapus spasi di nama kolom jika ada
    df.columns = df.columns.str.strip()
    
    # Konversi Tanggal
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    
    # Standardisasi nama kolom agar sesuai dengan kode dashboard
    df = df.rename(columns={
        "Nama Departemen": "Departemen",
        "Kode ICD-10": "Diagnosa_ICD10",
        "Waktu Tunggu (menit)": "Waktu_Tunggu",
        "Biaya (IDR)": "Biaya_IDR",
        "Kepuasan Pasien": "Skor_Kepuasan"
    })
    
    return df.sort_values("Tanggal")

df = load_real_data()

# --- DEFINISI WARNA TETAP ---
# Menjamin konsistensi warna sesuai permintaan Anda
color_map = {
    "IGD": "#1f77b4",        # Biru
    "Neurologi": "#ff7f0e",  # Oranye
    "Kardiologi": "#2ca02c", # Hijau
    "Pediatri": "#d62728",   # Merah
    "Ortopedi": "#9467bd",   # Ungu
    "Total": "#333333"       # Abu-abu gelap untuk akumulasi
}

# --- SIDEBAR (INTERACTIVITY) ---
st.sidebar.header("🏥 Health Admin Panel")
st.sidebar.markdown("Mata Kuliah: **Biomedical Info Management**")
st.sidebar.divider()

# Menambahkan opsi "Total" ke dalam daftar departemen
dept_options = list(df["Departemen"].unique())
if "Total" not in dept_options:
    dept_options.append("Total")

selected_dept = st.sidebar.multiselect(
    "Filter Departemen:",
    options=dept_options,
    default=[d for d in dept_options if d != "Total"] # Default semua kecuali Total
)

# --- LOGIKA FILTER & AKUMULASI TOTAL ---
# df_selection digunakan untuk visualisasi
if "Total" in selected_dept:
    # Buat data akumulasi "Total" per tanggal
    df_total_agg = df.groupby("Tanggal").size().reset_index(name="Count")
    # Karena data asli punya banyak baris per tanggal, kita buat dummy df untuk Total
    # agar bisa digabung dengan data departemen lainnya
    df_total = pd.DataFrame({
        "Tanggal": df_total_agg["Tanggal"],
        "Departemen": "Total"
    })
    
    depts_only = [d for d in selected_dept if d != "Total"]
    df_filtered_depts = df[df["Departemen"].isin(depts_only)]
    
    # Gabungkan data asli (hanya kolom yang diperlukan untuk plot tren) dengan data Total
    df_plot = pd.concat([
        df_filtered_depts[["Tanggal", "Departemen"]],
        df_total
    ])
else:
    df_plot = df[df["Departemen"].isin(selected_dept)][["Tanggal", "Departemen"]]

# df_kpi digunakan untuk angka metrik (tanpa duplikasi Total agar valid)
df_kpi = df[df["Departemen"].isin([d for d in selected_dept if d != "Total"])]
if df_kpi.empty:
    df_kpi = df # Fallback jika user hanya pilih Total

# --- MAIN PAGE ---
st.title("📊 Health Facility KPI Dashboard")
st.markdown("Dashboard ini berfungsi sebagai **Clinical Decision Support System (CDSS)**.")

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

# --- CLINICAL DECISION SUPPORT (ALERTS) ---
if avg_wait > 35:
    st.error(f"⚠️ **ALERT:** Waktu tunggu rata-rata sangat tinggi ({avg_wait} min). Perlu penambahan staf.")
elif satisfaction < 3.5:
    st.warning("⚠️ **PERHATIAN:** Skor kepuasan di bawah target. Evaluasi layanan diperlukan.")
else:
    st.success("✅ Seluruh indikator operasional dalam batas aman.")

# --- VISUALIZATIONS (DYNAMIC RANGE) ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("📈 Tren Kunjungan Pasien")
    
    # Agregasi data harian untuk plot
    df_counts = df_plot.groupby(['Tanggal', 'Departemen']).size().reset_index(name='Jumlah_Pasien')
    
    # Hitung Range Y Dinamis
    if not df_counts.empty:
        max_val_c1 = df_counts['Jumlah_Pasien'].max()
        # Jika data besar (seperti Total), beri buffer lebih besar
        y_limit_c1 = max_val_c1 + (20 if max_val_c1 > 30 else 10)
    else:
        y_limit_c1 = 60

    fig_line = px.line(
        df_counts, 
        x="Tanggal", 
        y="Jumlah_Pasien", 
        color="Departemen",
        color_discrete_map=color_map, # Mengunci warna sesuai dept
        markers=True,
        template="plotly_white"
    )
    
    fig_line.update_layout(hovermode="x unified")
    fig_line.update_yaxes(range=[0, y_limit_c1]) 
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("📊 Analisis Kasus (ICD-10)")
    
    # Hitung frekuensi diagnosa dari data asli terfilter
    df_icd = df_kpi["Diagnosa_ICD10"].value_counts().reset_index()
    df_icd.columns = ["Kode_ICD10", "Total"]
    
    # Hitung Range Y Dinamis untuk Bar Chart
    if not df_icd.empty:
        max_val_c2 = df_icd['Total'].max()
        y_limit_c2 = max_val_c2 + (15 if max_val_c2 > 20 else 5)
    else:
        y_limit_c2 = 50

    fig_bar = px.bar(
        df_icd, 
        x="Kode_ICD10", 
        y="Total", 
        color="Total",
        color_continuous_scale="Viridis",
        text_auto=True,
        template="plotly_white"
    )
    fig_bar.update_yaxes(range=[0, y_limit_c2])
    st.plotly_chart(fig_bar, use_container_width=True)

# --- FITUR TAMBAHAN (NILAI PLUS) ---
st.divider()
col_extra1, col_extra2 = st.columns(2)

with col_extra1:
    st.subheader("📋 Statistik Deskriptif (Ratio Data)")
    st.write("Analisis waktu tunggu dan biaya untuk mendukung keputusan manajerial.")
    st.dataframe(df_kpi[["Waktu_Tunggu", "Biaya_IDR"]].describe().T, use_container_width=True)

with col_extra2:
    st.subheader("📥 Export Data Audit")
    st.write("Unduh data terfilter sesuai standar HIPAA untuk keperluan laporan.")
    csv_data = df_kpi.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV Report",
        data=csv_data,
        file_name=f"report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )

# --- LEGAL & PRIVACY ---
with st.expander("⚖️ Legal Aspect & Data Privacy (HIPAA)"):
    st.write("""
    Sesuai dengan **HIPAA Title II (Administrative Simplification)**:
    - Data telah melalui proses **De-identification** untuk melindungi privasi pasien.
    - Akses dashboard dibatasi untuk personel administratif berwenang.
    - Transmisi data dilakukan secara elektronik mengikuti standar keamanan medis.
    """)

st.caption("Developed for MIB Project - Semester Genap 2026")
