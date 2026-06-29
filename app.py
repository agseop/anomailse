import streamlit as st
import pandas as pd
import os

# Konfigurasi Halaman
st.set_page_config(page_title="Monitoring Anomali - BPS Pesawaran", page_icon="📊", layout="wide")

# CSS Kustom
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: 800; color: #1E3A8A; margin-bottom: 2px; }
    .sub-title { font-size: 16px; color: #6B7280; margin-bottom: 20px; font-weight: 400; }
    .section-header-belum { font-size: 20px; font-weight: 700; color: #DC2626; border-left: 5px solid #DC2626; padding-left: 10px; margin-bottom: 15px; }
    .section-header-sudah { font-size: 20px; font-weight: 700; color: #16A34A; border-left: 5px solid #16A34A; padding-left: 10px; margin-bottom: 15px; }
    .sidebar-guide-box { background-color: #F8FAFC; padding: 12px; border-radius: 8px; border: 1px solid #E2E8F0; margin-top: 10px; }
    .sidebar-guide-title { font-weight: bold; color: #0F172A; margin-bottom: 8px; font-size: 14px; }
    .sidebar-step { margin-left: 15px; padding-left: 0px; line-height: 1.5; font-size: 13px; color: #334155; }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/28/Lambang_Badan_Pusat_Statistik_%28BPS%29_Indonesia.svg", width=70)
    st.markdown("### 📋 Menu Navigasi")
    st.write("---")
   
    
    st.markdown("#### 💡 CARA PENGGUNAAN")
    st.markdown("""
    <div class="sidebar-guide-box">
        <div class="sidebar-guide-title">📢 Langkah Update Progress:</div>
        <ol class="sidebar-step">
            <li><b>Filter Data:</b> Pilih Kecamatan, Desa, atau ketik nama Anda.</li>
            <li><b>Periksa Isian:</b> Lihat daftar kesalahan pada tabel Merah.</li>
            <li><b>Eksekusi Fasih:</b> Perbaiki data di Fasih.</li>
            <li><b>Tandai Selesai:</b> Centang kolom "Cek & Tandai".</li>
            <li><b>Simpan:</b> Klik "💾 Simpan Perubahan".</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.caption("⚙️ **BPS Kabupaten Pesawaran**\nMonitoring Evaluasi Lokal v2.0")

# Manajemen Data
FILE_NAME = "data_anomali.xlsx"
BASELINE_COUNT = 1680

if os.path.exists(FILE_NAME):
    if 'df_anomali' not in st.session_state:
        df = pd.read_excel(FILE_NAME)
        df.columns = df.columns.str.strip()
        if 'Status' not in df.columns: df['Status'] = 'Belum'
        st.session_state.df_anomali = df

    df_kerja = st.session_state.df_anomali
    
    # --------------------------------------------------------------------------
    # 3. KONTEN HALAMAN UTAMA (Header Utama)
    # --------------------------------------------------------------------------
    st.markdown('<div class="main-title">📊 Web Monitoring & Update Anomali</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Badan Pusat Statistik Kabupaten Pesawaran</div>', unsafe_allow_html=True)

    st.write("---")
    
    # --------------------------------------------------------------------------
    # 5. DASHBOARD METRIK (Dengan Persentase)
    # --------------------------------------------------------------------------
    df_awal = df_kerja[df_kerja['Tgl_Tarik'] == 26]
    
    # Tambahan adalah yang Tgl_Tarik bukan 26
    df_tambahan = df_kerja[df_kerja['Tgl_Tarik'] != 26]
    
    # Hitung jumlah tambahan untuk heading
    jumlah_tambahan = len(df_tambahan)
    
    # Hitung Selesai
    selesai_awal = len(df_awal[df_awal['Status'] == 'Sudah']) if not df_awal.empty else 0
    persen_awal = (selesai_awal / len(df_awal) * 100) if len(df_awal) > 0 else 0
    
    selesai_tambahan = len(df_tambahan[df_tambahan['Status'] == 'Sudah']) if not df_tambahan.empty else 0
    persen_tambahan = (selesai_tambahan / len(df_tambahan) * 100) if len(df_tambahan) > 0 else 0

    # Tampilan UI 4 kolom
    st.subheader(f"📌 Beban Awal 26 Juni (1680) | ➕ Tambahan ({jumlah_tambahan})")
    m1, m2, m3, m4 = st.columns(4)
    
    m1.metric("✅ Selesai (26 Juni)", f"{selesai_awal}", f"{persen_awal:.1f}%")
    m2.metric("❌ Sisa (26 Juni)", f"{len(df_awal) - selesai_awal}")
    m3.metric("✅ Selesai (Tmb)", f"{selesai_tambahan}", f"{persen_tambahan:.1f}%")
    m4.metric("❌ Sisa (Tmb)", f"{len(df_tambahan) - selesai_tambahan}")
  
    st.write("---")

    # Filter
    st.markdown("### 🔍 Filter Wilayah & Nama Petugas")
    col_f1, col_f2, col_f3 = st.columns(3)
    pilihan_kec = col_f1.selectbox("📍 Pilih Kecamatan:", ["Semua Kecamatan"] + sorted(df_kerja['Kecamatan'].unique().tolist()))
    pilihan_desa = col_f2.selectbox("🏢 Pilih Desa/Kelurahan:", ["Semua Desa"] + sorted(df_kerja[df_kerja['Kecamatan'] == pilihan_kec]['Desa'].unique().tolist() if pilihan_kec != "Semua Kecamatan" else df_kerja['Desa'].unique().tolist()))
    search_keyword = col_f3.text_input("👤 Cari Nama Petugas / SLS / Kategori:", "")

    def jalankan_filter(df):
        if pilihan_kec != "Semua Kecamatan": df = df[df['Kecamatan'] == pilihan_kec]
        if pilihan_desa != "Semua Desa": df = df[df['Desa'] == pilihan_desa]
        if search_keyword: df = df[df.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False)).any(axis=1)]
        return df

    # Tabel Belum Selesai
    st.markdown('<div class="section-header-belum">🟥 DAFTAR ANOMALI YANG BELUM DIPERBAIKI</div>', unsafe_allow_html=True)
    df_belum = jalankan_filter(df_kerja[df_kerja['Status'] != 'Sudah']).copy()
    df_belum.insert(0, 'Cek & Tandai', False)
    # Gunakan column_config untuk menyembunyikan kolom yang tidak diinginkan
    edited_df = st.data_editor(
        df_belum, 
        column_config={
            "Cek & Tandai": st.column_config.CheckboxColumn(),
            "ID_Assignment": None,  # Sembunyikan ID_Assignment
            "Status": None,         # Sembunyikan Status
            "No": None              # Jika kolom No juga ingin disembunyikan
        }, 
        disabled=['Kecamatan', 'Desa', 'SLS'], # Tambahkan kolom lain di sini yang tidak boleh diedit
        use_container_width=True
    )
  
    if st.button("💾 Simpan Perubahan & Pindahkan ke Tabel Bawah", type="primary"):
        for idx, row in edited_df[edited_df['Cek & Tandai'] == True].iterrows():
            st.session_state.df_anomali.loc[st.session_state.df_anomali['No'] == row['No'], 'Status'] = 'Sudah'
        st.session_state.df_anomali.to_excel(FILE_NAME, index=False)
        st.rerun()

    # --------------------------------------------------------------------------
    # 8. TABEL 2 - REKAPAN DATA SELESAI (SUDAH DIPERBAIKI)
    # --------------------------------------------------------------------------
    st.markdown('<div class="section-header-sudah">🟩 REKAPAN ANOMALI YANG SUDAH DIPERBAIKI</div>', unsafe_allow_html=True)
    
    df_sudah = df_kerja[df_kerja['Status'] == 'Sudah'].copy()
    df_sudah_filtered = jalankan_filter(df_sudah)
    
    if not df_sudah_filtered.empty:
        # Menghapus kolom yang tidak ingin ditampilkan menggunakan .drop()
        kolom_dihapus = ['ID_Assignment', 'Status'] 
        df_tampil = df_sudah_filtered.drop(columns=kolom_dihapus, errors='ignore')
        
        # Reset penomoran tampilan
        df_tampil = df_tampil.reset_index(drop=True)
        df_tampil.index = df_tampil.index + 1
        
        st.dataframe(df_tampil, use_container_width=True)
    else:
        st.info("💡 Catatan: Belum ada daftar kasus yang selesai diperbaiki pada kombinasi filter ini.")
