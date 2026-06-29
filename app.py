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
    </style>
""", unsafe_allow_html=True)

# 1. SIDEBAR (Tetap Ada)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/28/Lambang_Badan_Pusat_Statistik_%28BPS%29_Indonesia.svg", width=70)
    st.markdown("### 📋 Menu Navigasi")
    st.write("---")
    st.markdown("#### 💡 CARA PENGGUNAAN")
    st.markdown("""
    <div style="font-size: 13px;">
    1. Filter Data di tab Anomali.<br>
    2. Periksa isian pada tabel merah.<br>
    3. Isi kolom 'Catatan Lapangan'.<br>
    4. Centang 'Cek & Tandai'.<br>
    5. Klik <b>💾 Simpan Perubahan</b>.
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.caption("⚙️ BPS Kabupaten Pesawaran")

# 2. MANAJEMEN DATA
FILE_NAME = "data_anomali.xlsx"
if os.path.exists(FILE_NAME):
    if 'df_anomali' not in st.session_state:
        df = pd.read_excel(FILE_NAME)
        df.columns = df.columns.str.strip()
        if 'Status' not in df.columns: df['Status'] = 'Belum'
        if 'Catatan_Petugas' not in df.columns: df['Catatan_Petugas'] = ""
        st.session_state.df_anomali = df

    df_kerja = st.session_state.df_anomali
    
    # 3. KONTEN UTAMA
    st.markdown('<div class="main-title">📊 Web Monitoring & Update Anomali</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Badan Pusat Statistik Kabupaten Pesawaran</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📊 Anomali", "🔍 Missing Value"])

    with tab1:
        # Dashboard Metrik
        df_awal = df_kerja[df_kerja['Tgl_Tarik'] == 26]
        df_tambahan = df_kerja[df_kerja['Tgl_Tarik'] != 26]
        
        selesai_awal = len(df_awal[df_awal['Status'] == 'Sudah'])
        selesai_tambahan = len(df_tambahan[df_tambahan['Status'] == 'Sudah'])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("✅ Selesai (26 Juni)", f"{selesai_awal}")
        m2.metric("❌ Sisa (26 Juni)", f"{len(df_awal) - selesai_awal}")
        m3.metric("✅ Selesai (Tmb)", f"{selesai_tambahan}")
        m4.metric("❌ Sisa (Tmb)", f"{len(df_tambahan) - selesai_tambahan}")
        st.write("---")

        # Filter
        col_f1, col_f2, col_f3 = st.columns(3)
        pilihan_kec = col_f1.selectbox("📍 Pilih Kecamatan:", ["Semua Kecamatan"] + sorted(df_kerja['Kecamatan'].unique().tolist()))
        pilihan_desa = col_f2.selectbox("🏢 Pilih Desa/Kelurahan:", ["Semua Desa"] + sorted(df_kerja[df_kerja['Kecamatan'] == pilihan_kec]['Desa'].unique().tolist() if pilihan_kec != "Semua Kecamatan" else df_kerja['Desa'].unique().tolist()))
        search_keyword = col_f3.text_input("👤 Cari Nama Petugas / SLS / Kategori:", "")

        def jalankan_filter(df):
            if pilihan_kec != "Semua Kecamatan": df = df[df['Kecamatan'] == pilihan_kec]
            if pilihan_desa != "Semua Desa": df = df[df['Desa'] == pilihan_desa]
            if search_keyword: df = df[df.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False)).any(axis=1)]
            return df

        # Tabel Edit
        st.markdown('<div class="section-header-belum">🟥 DAFTAR ANOMALI YANG BELUM DIPERBAIKI</div>', unsafe_allow_html=True)
        df_belum = jalankan_filter(df_kerja[df_kerja['Status'] != 'Sudah']).copy()
        df_belum.insert(0, 'Cek & Tandai', False)
        
        edited_df = st.data_editor(
            df_belum, 
            column_config={
                "Cek & Tandai": st.column_config.CheckboxColumn(),
                "Catatan_Petugas": st.column_config.TextColumn("Catatan Lapangan", default=""),
                "ID_Assignment": None, "Status": None, "No": None
            }, 
            disabled=['Kecamatan', 'Desa', 'SLS'], use_container_width=True
        )

        if st.button("💾 Simpan Perubahan & Catatan", type="primary"):
            for idx, row in edited_df.iterrows():
                if row['Cek & Tandai'] == True:
                    st.session_state.df_anomali.loc[st.session_state.df_anomali['No'] == row['No'], 'Status'] = 'Sudah'
                st.session_state.df_anomali.loc[st.session_state.df_anomali['No'] == row['No'], 'Catatan_Petugas'] = row['Catatan_Petugas']
            st.session_state.df_anomali.to_excel(FILE_NAME, index=False)
            st.rerun()

        # Tabel Selesai
        st.markdown('<div class="section-header-sudah">🟩 REKAPAN ANOMALI YANG SUDAH DIPERBAIKI</div>', unsafe_allow_html=True)
        df_sudah = df_kerja[df_kerja['Status'] == 'Sudah'].copy()
        df_tampil = jalankan_filter(df_sudah).drop(columns=['ID_Assignment', 'Status'], errors='ignore')
        st.dataframe(df_tampil, use_container_width=True)

    with tab2:
        st.subheader("🔍 Monitoring Data Missing Value")
        st.info("Tab ini aktif dan siap dihubungkan ke sumber data Anda.")

else:
    st.error("File data_anomali.xlsx tidak ditemukan!")
