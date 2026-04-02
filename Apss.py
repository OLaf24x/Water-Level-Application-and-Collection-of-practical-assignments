import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.signal import butter, filtfilt

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="OceanData Hub | Yolivia",
    page_icon="🌊",
    layout="wide"
)

# --- 2. FUNGSI ANALISIS OSEANOGRAFI ---
def low_pass_filter(data, cutoff=0.01, fs=1.0, order=2):
    """Fungsi untuk membuang noise frekuensi tinggi (gelombang pendek/angin)"""
    try:
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        y = filtfilt(b, a, data)
        return y
    except:
        return data # Jika gagal, kembalikan data asli

# --- 3. SIDEBAR NAVIGASI ---
with st.sidebar:
    st.title("🌊 Oceanography Hub")
    st.write("Institut Teknologi Bandung")
    
    selected = option_menu(
        menu_title="Menu Utama",
        options=["Dashboard", "Water Level Analysis", "Pengumpulan Tugas"],
        icons=["house", "graph-up", "folder2-open"],
        menu_icon="cast",
        default_index=1, # Default langsung ke analisis agar cepat cek data
        styles={
            "container": {"padding": "5!important", "background-color": "#0e1117"},
            "icon": {"color": "#00d4ff", "font-size": "20px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#262730"},
            "nav-link-selected": {"background-color": "#1e3a8a"},
        }
    )
    
    st.markdown("---")
    st.caption("User: Yolivia (Semester 6)")
    st.caption("GPA: - | SKS: - ")

# --- 4. LOGIKA HALAMAN ---

if selected == "Dashboard":
    st.title("👋 Halo, Yolivia!")
    st.subheader("Selamat datang di platform Oseanografimu.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Target Semester Ini", "Naikkan GPA")
    col2.metric("Mata Kuliah Aktif", "11 Matkul")
    col3.metric("Prioritas Utama", "UTS")

    st.markdown("---")
    st.info("**Reminder:** Segera selesaikan analisis SVP menggunakan Wilson Formula untuk tugas pekan depan!")

elif selected == "Water Level Analysis":
    st.title("📊 Water Level Analysis")
    st.write("Analisis komponen Raw, Low-pass (Trend), dan Average (MSL).")

    uploaded_file = st.file_uploader("Unggah File CSV Data Pasut", type=["csv"])

    if uploaded_file is not None:
        try:
            # Membaca file
            df = pd.read_csv(uploaded_file)
            
            # --- FITUR PERBAIKAN: PEMILIH KOLOM ---
            st.success("File Berhasil Dibaca! Silakan sesuaikan kolom di bawah:")
            
            c_select1, c_select2 = st.columns(2)
            with c_select1:
                col_waktu = st.selectbox("Pilih Kolom Waktu (Timestamp):", df.columns, index=0)
            with c_select2:
                col_elevasi = st.selectbox("Pilih Kolom Elevasi (Water Level):", df.columns, index=1)

            # Konversi Waktu (errors='coerce' agar tidak crash jika ada teks sampah)
            df[col_waktu] = pd.to_datetime(df[col_waktu], errors='coerce')
            
            # Hapus baris yang gagal dikonversi menjadi tanggal atau datanya kosong
            df = df.dropna(subset=[col_waktu, col_elevasi])
            
            # Sortir berdasarkan waktu agar grafik tidak berantakan
            df = df.sort_values(by=col_waktu)

            # Ekstrak Nilai
            raw_data = pd.to_numeric(df[col_elevasi], errors='coerce').values
            avg_val = np.nanmean(raw_data)
            
            # Low-pass Filtering
            # Cutoff 0.01 biasanya cukup untuk melihat tren harian/mingguan
            low_data = low_pass_filter(raw_data, cutoff=0.01)

            # --- VISUALISASI PLOTLY ---
            fig = go.Figure()

            # 1. Raw Data
            fig.add_trace(go.Scatter(
                x=df[col_waktu], y=raw_data,
                name="Raw Data (Original)",
                line=dict(color='rgba(150, 150, 150, 0.4)', width=1)
            ))

            # 2. Low-pass Filtered
            fig.add_trace(go.Scatter(
                x=df[col_waktu], y=low_data,
                name="Low-pass (Trend/Surge)",
                line=dict(color='#00d4ff', width=3)
            ))

            # 3. Average Line
            fig.add_trace(go.Scatter(
                x=df[col_waktu], y=[avg_val] * len(df),
                name=f"MSL ({avg_val:.2f}m)",
                line=dict(color='#ff4b4b', width=2, dash='dash')
            ))

            fig.update_layout(
                title=f"Grafik Analisis: {uploaded_file.name}",
                xaxis_title="Waktu",
                yaxis_title="Elevasi (m)",
                hovermode="x unified",
                template="plotly_dark",
                height=600
            )

            st.plotly_chart(fig, use_container_width=True)

            # Statistik
            st.write("### Statistik Deskriptif")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Maximum", f"{np.nanmax(raw_data):.2f} m")
            s2.metric("Minimum", f"{np.nanmin(raw_data):.2f} m")
            s3.metric("Range", f"{(np.nanmax(raw_data)-np.nanmin(raw_data)):.2f} m")
            s4.metric("Mean (MSL)", f"{avg_val:.2f} m")

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data: {e}")
            st.info("Pastikan kolom yang kamu pilih benar-benar berisi angka.")
    else:
        st.info("💡 **Tips:** Silakan drag-and-drop file CSV data pengamatanmu ke sini.")

elif selected == "Pengumpulan Tugas":
    st.title("📚 Repositori Tugas Kuliah")
    st.write("Tempat mengumpulkan file tugas agar rapi dan mudah dicari.")
    
    matkul_list = [
        "Analisis Data Oseanografi", 
        "Pasang Surut", 
        "Energi Terbarukan Laut",
        "Oseanografi Dinamis",
        "Pemodelan Oseanografi"
    ]
    
    for matkul in matkul_list:
        with st.expander(f"Mata Kuliah: {matkul}"):
            st.file_uploader(f"Upload laporan {matkul}", key=matkul)
            if st.button(f"Simpan {matkul}"):
                st.toast("Berhasil disimpan!")

# --- FOOTER ---
st.markdown("---")
st.caption("Created for Yolivia | Oceanography ITB | 2026")