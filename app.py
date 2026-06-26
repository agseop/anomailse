import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection  # Pustaka sakti untuk simpan permanen

# ==============================================================================
# 1. KONFIGURASI HALAMAN UTAMA & SIDEBAR
# ==============================================================================
st.set_page_config(
    page_title="Monitoring Anomali - BPS Pesawaran",
    page_icon="📊",
    layout="wide"
)

# Tautan langsung Google Sheets Anda (Anti-Error 404/400)
URL_SPREADSHEET = "https://docs.google.com/spreadsheets/d/1zsFeCk7jtd4fVOgqlSqgSgvtNVOLq4iqRKdpqTiMhsk"

# Custom CSS untuk mempercantik komponen visual & tata letak (Layout)
st.markdown("""
    <style>
    /* Styling Judul Utama */
    .main-title { font-size: 32px; font-weight: 800; color: #1E3A8A; margin-bottom: 2px; }
    .sub-title { font-size: 16px; color: #6B7280; margin-bottom: 20px; font-weight: 400; }
    
    /* Styling Sub-Header Section Tabel */
    .section-header-belum { font-size: 20px; font-weight: 700; color: #DC2626; border-left: 5px solid #DC2626; padding-left: 10px; margin-bottom: 15px; }
    .section-header-sudah { font-size: 20px; font-weight: 700; color: #16A34A; border-left: 5px solid #16A34A; padding-left: 10px; margin-bottom: 15px; }
    
    /* Box Panduan di Sidebar */
    .sidebar-guide-box { background-color: #F8FAFC; padding: 12px; border-radius: 8px; border: 1px solid #E2E8F0; margin-top: 10px; }
    .sidebar-guide-title { font-weight: bold; color: #0F172A; margin-bottom: 8px; font-size: 14px; }
    .sidebar-step { margin-left: 15px; padding-left: 0px; line-height: 1.5; font-size: 13px; color: #334155; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. STRUKTUR SIDEBAR (PETUNJUK PEMAKAIAN MITRA)
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
            <li><b>Filter Data:</b><br>Pilih Kecamatan, Desa, atau langsung ketik nama Anda pada kolom pencarian petugas.</li>
            <li style="margin-top: 8px;"><b>Periksa Isian:</b><br>Lihat rincian daftar kesalahan data Anda pada tabel berwarna <span style="color:#DC2626; font-weight:bold;">Merah</span>.</li>
            <li style="margin-top: 8px;"><b>Tandai Selesai:</b><br>Jika dokumen sudah clean, <b>beri centang (✔️)</b> pada kolom paling kiri (<b>Cek & Tandai</b>).</li>
            <li style="margin-top: 8px;"><b>Simpan Progress:</b><br>Klik tombol merah <b>"💾 Simpan Perubahan"</b> di bawah tabel untuk memperbarui status pengerjaan Anda di cloud.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.caption("⚙️ **BPS Kabupaten Pesawaran**\nMonitoring Evaluasi Cloud v5.0")

# ==============================================================================
# 3. KONTEN HALAMAN UTAMA (DASHBOARD UTAMA)
# ==============================================================================
st.markdown('<div class="main-title">📊 Web Monitoring & Update Anomali</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Badan Pusat Statistik Kabupaten Pesawaran</div>', unsafe_allow_html=True)

# ==============================================================================
# 4. KONEKSI GOOGLE SHEETS LIVE CLOUD
# ==============================================================================
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data_from_sheets():
    try:
        # Membaca data langsung menggunakan URL pangkalan data utama
        df = conn.read(spreadsheet=URL_SPREADSHEET, worksheet="Sheet1", ttl=0)
        df.columns = df.columns.str.strip()
        
        # Penyeragaman data ID/Kode agar tidak berubah format (.0)
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

# Membaca data secara live di setiap aktivitas web
data_sheets = load_data_from_sheets()
if data_sheets is not None:
    df_kerja = data_sheets
else:
    st.stop()

# --------------------------------------------------------------------------
# 5. DASHBOARD METRIK CAPAIAN (KPI CARDS)
# --------------------------------------------------------------------------
total_kasus = len(df_kerja)
sudah_diperbaiki = len(df_kerja[df_kerja['Status'] == 'Sudah'])
belum_diperbaiki = total_kasus - sudah_diperbaiki
persen_progress = (sudah_diperbaiki / total_kasus * 100) if total_kasus > 0 else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("📌 Total Kasus Anomali", f"{total_kasus} Kasus")
m2.metric("✅ Berhasil Diperbaiki", f"{sudah_diperbaiki} Kasus")
m3.metric("❌ Sisa Belum Diperbaiki", f"{belum_diperbaiki} Kasus")
m4.metric("📈 Progress Penyelesaian", f"{persen_progress:.1f}%")

st.write("---")

# --------------------------------------------------------------------------
# 6. PANEL FILTER DATA SEJAJAR 3 KOLOM
# --------------------------------------------------------------------------
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
        df_filtered_kec = df_kerja.copy()
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

# --------------------------------------------------------------------------
# 7. TABEL 1 - DAFTAR BELUM DIPERBAIKI (RUANG EDIT INTERAKTIF)
# --------------------------------------------------------------------------
st.write("---")
st.markdown('<div class="section-header-belum">🟥 DAFTAR ANOMALI YANG BELUM DIPERBAIKI</div>', unsafe_allow_html=True)

df_belum = df_kerja[df_kerja['Status'] != 'Sudah'].copy()
df_belum_filtered = jalankan_filter(df_belum)

if not df_belum_filtered.empty:
    df_belum_filtered.insert(0, 'Cek & Tandai', False)
    
    # Menyesuaikan daftar kolom disabled agar COCOK PERSIS dengan header Google Sheets Anda
    kolom_ada = df_belum_filtered.columns.tolist()
    kolom_disabled = [c for c in ['No', 'Kecamatan', 'Desa', 'SLS', 'Keluarga atau Usaha', 'Anomali', 'Petugas', 'Pengawas'] if c in kolom_ada]
    
    edited_df = st.data_editor(
        df_belum_filtered,
        column_config={
            "Cek & Tandai": st.column_config.CheckboxColumn(
                "Cek & Tandai",
                help="Centang jika baris data kesalahan ini sudah selesai Anda perbaiki",
                default=False,
            ),
            "Status": None  # Sembunyikan kolom status asli
        },
        disabled=kolom_disabled,
        use_container_width=True,
        key="tabel_editor_cloud"
    )
    
    if st.button("💾 Simpan Perubahan & Pindahkan ke Tabel Bawah", type="primary", use_container_width=True):
        baris_dicentang = edited_df[edited_df['Cek & Tandai'] == True]
        
        if not baris_dicentang.empty:
            # Mengubah status nilai di dalam data master 'df_kerja' berdasarkan kolom 'No'
            for idx, row in baris_dicentang.iterrows():
                id_kasus = row['No']
                df_kerja.loc[df_kerja['No'] == id_kasus, 'Status'] = 'Sudah'
            
            # 🔥 UPDATE LANGSUNG KE GOOGLE SHEETS PUSAT SECARA PERMANEN
            conn.update(spreadsheet=URL_SPREADSHEET, worksheet="Sheet1", data=df_kerja)
            
            st.success("🎉 Berhasil! Perubahan telah dikunci di Google Sheets pusat secara permanen.")
            st.rerun()
        else:
            st.info("💡 Pemberitahuan: Belum ada data yang Anda centang.")
else:
    st.success("✨ Sempurna! Semua data anomali pada filter wilayah ini sudah diselesaikan.")

# --------------------------------------------------------------------------
# 8. TABEL 2 - REKAPAN DATA SELESAI (SUDAH DIPERBAIKI)
# --------------------------------------------------------------------------
st.write("---")
st.markdown('<div class="section-header-sudah">🟩 REKAPAN ANOMALI YANG SUDAH DIPERBAIKI</div>', unsafe_allow_html=True)

df_sudah = df_kerja[df_kerja['Status'] == 'Sudah'].copy()
df_sudah_filtered = jalankan_filter(df_sudah)

if not df_sudah_filtered.empty:
    df_sudah_filtered = df_sudah_filtered.reset_index(drop=True)
    df_sudah_filtered.index = df_sudah_filtered.index + 1
    
    st.dataframe(
        df_sudah_filtered.drop(columns=['Status'], errors='ignore'), 
        use_container_width=True
    )
else:
    st.info("💡 Catatan: Belum ada daftar kasus yang selesai diperbaiki pada kombinasi filter ini.")
