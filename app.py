import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==============================================================================
# 1. KONFIGURASI HALAMAN UTAMA & SIDEBAR
# ==============================================================================
st.set_page_config(
    page_title="Monitoring Anomali - BPS Pesawaran",
    page_icon="📊",
    layout="wide"
)

# Custom CSS untuk mempercantik komponen visual & tata letak
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

# ==============================================================================
# 2. STRUKTUR SIDEBAR
# ==============================================================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/28/Lambang_Badan_Pusat_Statistik_%28BPS%29_Indonesia.svg", width=70)
    st.markdown("### 📋 Menu Navigasi")
    st.write("---")
    st.markdown("#### 💡 CARA PENGGUNAAN")
    st.markdown("""
    <div class="sidebar-guide-box">
        <div class="sidebar-guide-title">📢 Langkah Update Progress:</div>
        <ol class="sidebar-step">
            <li><b>Filter Data:</b> Pilih Kecamatan/Desa Anda.</li>
            <li><b>Tandai Selesai:</b> Beri centang (✔️) pada kolom <b>Cek & Tandai</b>.</li>
            <li><b>Simpan Progress:</b> Klik tombol merah <b>"💾 Simpan Perubahan"</b>.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.caption("⚙️ **BPS Kabupaten Pesawaran**\nMonitoring Evaluasi Cloud v5.0")

st.markdown('<div class="main-title">📊 Web Monitoring & Update Anomali</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Badan Pusat Statistik Kabupaten Pesawaran</div>', unsafe_allow_html=True)

# ==============================================================================
# 3. KONEKSI GOOGLE SHEETS LIVE (DUA ARAH)
# ==============================================================================
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data_from_sheets():
    try:
        # Membaca data menggunakan konfigurasi dari Secrets secara aman
        df = conn.read(worksheet="Sheet1", ttl=0)
        df.columns = df.columns.str.strip()
        
        kolom_teks = ['No', 'Kecamatan', 'Desa', 'SLS']
        for col in kolom_teks:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        if 'Status' not in df.columns:
            df['Status'] = 'Belum'
            
        return df
    except Exception as e:
        st.error(f"⚠️ Gagal memuat data dari Google Sheets! Detail error: {e}")
        return None

df_kerja = load_data_from_sheets()
if df_kerja is None:
    st.stop()

# ==============================================================================
# 4. DASHBOARD METRIK & FILTER
# ==============================================================================
total_kasus = len(df_kerja)
sudah_diperbaiki = len(df_kerja[df_kerja['Status'] == 'Sudah'].copy())
belum_diperbaiki = total_kasus - sudah_diperbaiki
persen_progress = (sudah_diperbaiki / total_kasus * 100) if total_kasus > 0 else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("📌 Total Kasus Anomali", f"{total_kasus} Kasus")
m2.metric("✅ Berhasil Diperbaiki", f"{sudah_diperbaiki} Kasus")
m3.metric("❌ Sisa Belum Diperbaiki", f"{belum_diperbaiki} Kasus")
m4.metric("📈 Progress Penyelesaian", f"{persen_progress:.1f}%")

st.write("---")
st.markdown("### 🔍 Filter Wilayah & Nama Petugas")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    list_kec = ["Semua Kecamatan"] + sorted(df_kerja['Kecamatan'].dropna().unique().tolist())
    pilihan_kec = st.selectbox("📍 Pilih Kecamatan:", list_kec)
    
with col_f2:
    if pilihan_kec != "Semua Kecamatan":
        df_filtered_kec = df_kerja[df_kerja['Kecamatan'] == pilihan_kec]
        list_desa = ["Semua Desa"] + sorted(df_filtered_kec['Desa'].dropna().unique().tolist())
    else:
        list_desa = ["Semua Desa"] + sorted(df_kerja['Desa'].dropna().unique().tolist())
    pilihan_desa = st.selectbox("🏢 Pilih Desa/Kelurahan:", list_desa)

with col_f3:
    search_keyword = st.text_input("👤 Cari Nama Petugas / SLS / Kategori:", "")

def jalankan_filter(df_target):
    if pilihan_kec != "Semua Kecamatan":
        df_target = df_target[df_target['Kecamatan'] == pilihan_kec]
    if pilihan_desa != "Semua Desa":
        df_target = df_target[df_target['Desa'] == pilihan_desa]
    if search_keyword:
        df_target = df_target[df_target.astype(str).apply(lambda x: x.str.contains(search_keyword, case=False)).any(axis=1)]
    return df_target

# ==============================================================================
# 5. TABEL INTERAKTIF & PROSES SIMPAN TULIS BALIK
# ==============================================================================
st.write("---")
st.markdown('<div class="section-header-belum">🟥 DAFTAR ANOMALI YANG BELUM DIPERBAIKI</div>', unsafe_allow_html=True)

df_belum = df_kerja[df_kerja['Status'] != 'Sudah'].copy()
df_belum_filtered = jalankan_filter(df_belum)

if not df_belum_filtered.empty:
    df_belum_filtered.insert(0, 'Cek & Tandai', False)
    
    kolom_ada = df_belum_filtered.columns.tolist()
    kolom_disabled = [c for c in ['No', 'Kecamatan', 'Desa', 'SLS', 'Keluarga atau Usaha', 'Anomali', 'Petugas', 'Pengawas'] if c in kolom_ada]
    
    edited_df = st.data_editor(
        df_belum_filtered,
        column_config={
            "Cek & Tandai": st.column_config.CheckboxColumn(
                "Cek & Tandai",
                help="Centang jika baris data ini sudah selesai diperbaiki",
                default=False,
            ),
            "Status": None
        },
        disabled=kolom_disabled,
        use_container_width=True,
        key="tabel_editor_cloud"
    )
    
    if st.button("💾 Simpan Perubahan & Amankan ke Google Sheets", type="primary", use_container_width=True):
        baris_dicentang = edited_df[edited_df['Cek & Tandai'] == True]
        
        if not baris_dicentang.empty:
            # Update status lokal ke 'Sudah'
            for idx, row in baris_dicentang.iterrows():
                id_kasus = row['No']
                df_kerja.loc[df_kerja['No'] == id_kasus, 'Status'] = 'Sudah'
            
            try:
                # Menuliskan kembali seluruh perubahan ke file Google Sheets pusat
                conn.update(worksheet="Sheet1", data=df_kerja)
                st.success("🎉 Berhasil! Progres pengerjaan Anda telah ditulis balik ke Google Sheets pusat.")
                st.rerun()
            except Exception as ex:
                st.error(f"❌ Gagal menulis balik data ke Google Sheets! Detail error: {ex}")
        else:
            st.info("💡 Pemberitahuan: Belum ada data yang Anda centang.")
else:
    st.success("✨ Sempurna! Semua data anomali pada filter wilayah ini sudah diselesaikan.")

# ==============================================================================
# 6. REKAPAN DATA SELESAI
# ==============================================================================
st.write("---")
st.markdown('<div class="section-header-sudah">🟩 REKAPAN ANOMALI YANG SUDAH DIPERBAIKI</div>', unsafe_allow_html=True)

df_sudah = df_kerja[df_kerja['Status'] == 'Sudah'].copy()
df_sudah_filtered = jalankan_filter(df_sudah)

if not df_sudah_filtered.empty:
    df_sudah_filtered = df_sudah_filtered.reset_index(drop=True)
    df_sudah_filtered.index = df_sudah_filtered.index + 1
    st.dataframe(df_sudah_filtered.drop(columns=['Status'], errors='ignore'), use_container_width=True)
else:
    st.info("💡 Catatan: Belum ada daftar kasus yang selesai diperbaiki pada kombinasi filter ini.")
