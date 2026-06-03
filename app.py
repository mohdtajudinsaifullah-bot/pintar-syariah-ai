import streamlit as st
import os
import time
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from google import genai
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor
from io import BytesIO

# 1. Buka kunci (.env)
load_dotenv(override=True)
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else os.getenv("GOOGLE_API_KEY")
api_key_google = os.environ["GOOGLE_API_KEY"]

# --- FUNGSI AUTO-RETRY ---
def cuba_jana_ai(prompt_teks):
    client = genai.Client(api_key=api_key_google)
    senarai_model = ["gemini-flash-latest", "gemini-3.5-flash", "gemini-3.1-flash-lite"] 
    max_cuba = 3 
    for cubaan in range(max_cuba):
        for model_ai in senarai_model:
            try:
                respons = client.models.generate_content(model=model_ai, contents=prompt_teks)
                return respons
            except Exception as e:
                ralat = str(e)
                if "503" in ralat or "429" in ralat:
                    time.sleep(5) 
                    continue 
                elif "404" in ralat:
                    continue 
                else:
                    raise e 
    raise Exception("Pelayan Google sesak. Sila cuba lagi.")

# --- FUNGSI BINA FAIL WORD (VERSION PRO) ---
def bina_fail_word(teks_ai, tajuk_dokumen, metadata):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)
    style.paragraph_format.line_spacing = 1.0
    style.paragraph_format.space_after = Pt(12) # Jarak antara perenggan

    # --- 1. KEPALA SURAT (CENTER) ---
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run1 = p1.add_run(f"{metadata['pihak1']}\nlwn\n{metadata['pihak2']}")
    run1.bold = True
    run1.font.size = Pt(12)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Format: [Mahkamah] [Nama Hakim] pada [Tarikh]
    p2.add_run(f"[{metadata['mahkamah']}, {metadata['hakim']}, pada {metadata['tarikh']}]").italic = True

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.add_run(f"[Kes No: {metadata['nokes']}]")

    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p4.add_run(f"[Permohonan: {metadata['jenis_p']}]\n[Peguam: {metadata['peguam']}]")
    
    # --- 2. PEMBINAAN KANDUNGAN & PEMBERSIHAN SIMBOL ---
    # Buang simbol markdown yang user tak nak
    teks_bersih = teks_ai.replace('**', '').replace('##', '').replace('*', '').replace('>', '').replace('[ ', '[').replace(' ]', ']')
    lines = teks_bersih.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # KESAN JADUAL
        if line.startswith('|'):
            table_data = []
            while i < len(lines) and line.startswith('|'):
                cells = [c.strip() for c in lines[i].split('|') if c.strip()]
                if cells: table_data.append(cells)
                i += 1
                if i < len(lines): line = lines[i].strip()
            
            if table_data:
                table = doc.add_table(rows=len(table_data), cols=len(table_data[0]))
                table.style = 'Table Grid'
                for r_idx, row_cells in enumerate(table_data):
                    for c_idx, cell_text in enumerate(row_cells):
                        cell = table.rows[r_idx].cells[c_idx]
                        cell.text = cell_text.replace('<br>', '\n')
            continue 

        # KESAN TAJUK UTAMA (PERMOHONAN, FAKTA KES, KEPUTUSAN dsb)
        seksyen_utama = ["PERMOHONAN", "FAKTA KES", "ULASAN MAHKAMAH", "KEPUTUSAN"]
        if any(s in line.upper() for s in seksyen_utama):
            p = doc.add_paragraph()
            run = p.add_run(line.upper())
            run.bold = True
            run.underline = True # Tambah garis bawah untuk tajuk seksyen
            p.paragraph_format.space_before = Pt(18)
        
        # KESAN NOMBOR (1. 2. 3.1)
        elif any(line.startswith(str(n)+'.') for n in range(1, 30)):
            p = doc.add_paragraph()
            run = p.add_run(line)
            run.bold = True
        
        # TEKS BIASA
        else:
            p = doc.add_paragraph(line)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        i += 1
            
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- UI STREAMLIT ---
st.set_page_config(page_title="Pintar Syariah AI", page_icon="⚖️", layout="wide")
st.title("⚖️ Artificial Intelligence Mahkamah Syariah (AIMS)")
st.divider()

tab_kes, tab_pengurusan = st.tabs(["🏛️ Mod 1: Analisis Kes Syariah (AP)", "📝 Mod 2: Kertas Kerja Pengurusan"])

# ==========================================
# MOD 1: ANALISIS KES (DRAF AP PRO)
# ==========================================
with tab_kes:
    # UBAH SUSUNAN LAJUR: Lajur kiri (1) untuk Meta, Lajur kanan (2) untuk Input
    col_meta, col_input = st.columns([1, 2]) 
    
    with col_meta:
        st.subheader("📋 Maklumat Kes (Metadata)")
        m_negeri = st.selectbox("Bidang Kuasa (Negeri):", ["Selangor", "Wilayah Persekutuan", "Johor", "Perak", "Kedah", "Kelantan", "Terengganu", "Pahang", "Negeri Sembilan", "Melaka", "Pulau Pinang", "Perlis", "Sabah", "Sarawak"])
        m_level = st.selectbox("Hierarki Mahkamah:", ["Mahkamah Rendah Syariah", "Mahkamah Tinggi Syariah", "Mahkamah Rayuan Syariah"])
        m_hakim = st.text_input("Nama Hakim:", placeholder="Cth: YA Tuan Haji...")
        m_tarikh = st.text_input("Tarikh Sidang / Keputusan:", placeholder="Cth: 26 Ramadan 1445H / 6 April 2024")
        m_nokes = st.text_input("No. Kes:", placeholder="Cth: 10000-003-0001-2024")
        m_pihak1 = st.text_area("Pihak 1 (Plaintif/Pemohon):", height=70)
        m_pihak2 = st.text_area("Pihak 2 (Defendan/Responden):", height=70)
        m_jenis = st.text_input("Jenis Permohonan:", placeholder="Cth: Pengesahan Lafaz Cerai")
        m_peguam = st.text_input("Nama Peguam (Jika ada):")

    with col_input:
        st.subheader("📝 Ringkasan Fakta & Seksyen Utama")
        f_permohonan = st.text_area("Butiran PERMOHONAN (Jika ada):", placeholder="Biarkan kosong jika mahu AI drafkan...")
        f_fakta = st.text_area("Butiran FAKTA KES (Wajib isi):", height=150)
        f_ulasan = st.text_area("Butiran ULASAN MAHKAMAH (Jika ada):")
        f_keputusan = st.text_area("Butiran KEPUTUSAN (Jika ada):")

        if st.button("🔍 Jana Draf Alasan Penghakiman (AP)", type="primary"):
            if f_fakta.strip() == "":
                st.warning("⚠️ Sila masukkan Fakta Kes!")
            else:
                with st.spinner("AI sedang merangka AP mengikut format rujukan..."):
                    try:
                        # RAG Retrieval
                        embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
                        db = Chroma(persist_directory="./database_vektor_google", embedding_function=embeddings)
                        retriever = db.as_retriever(search_kwargs={"k": 5})
                        dokumen_relevan = retriever.invoke(f_fakta)
                        konteks = "\n".join([d.page_content for d in dokumen_relevan])

                        # Custom Prompt based on Court Hierarchy & State Law
                        prompt_ap = f"""Anda adalah Penyelidik Undang-Undang Kanan. Tugas anda merangka draf ALASAN PENGHAKIMAN (AP) yang formal.

HIERARKI MAHKAMAH: {m_level}
BIDANG KUASA UNDANG-UNDANG: {m_negeri}
NAMA HAKIM: {m_hakim}
JENIS PERMOHONAN: {m_jenis}

STRUKTUR WAJIB (JANGAN GUNA SIMBOL *, [ ], atau >):
1. PERMOHONAN: (Tulis draf permohonan. Ringkasan user: {f_permohonan})
2. FAKTA KES: (Huraikan fakta kronologi secara naratif. Input user: {f_fakta})
3. ULASAN MAHKAMAH: (Salin PERUNTUKAN UNDANG-UNDANG secara verbatim/asal dari rujukan. Pastikan ia selari dengan undang-undang di negeri {m_negeri}. Beri ulasan undang-undang. Ringkasan user: {f_ulasan})
4. KEPUTUSAN: (Gunakan laras bahasa hierarki {m_level}. JANGAN guna "Saya", guna "Mahkamah". Ringkasan user: {f_keputusan})

ARAHAN KHAS:
- DILARANG guna simbol Markdown (*, >, ##, [ ]).
- Salin seksyen Enakmen/Undang-undang sebiji macam teks asal rujukan.
- Bahagian KEPUTUSAN mesti dimulakan dengan ayat: "SETELAH Mahkamah membaca dan meneliti permohonan..."

RUJUKAN KES LEPAS:
{konteks}
"""
                        respons = cuba_jana_ai(prompt_ap)
                        st.write(respons.text)
                        
                        meta_dict = {
                            'mahkamah': m_level, 'hakim': m_hakim, 'tarikh': m_tarikh, 
                            'nokes': m_nokes, 'pihak1': m_pihak1, 'pihak2': m_pihak2, 
                            'jenis_p': m_jenis, 'peguam': m_peguam
                        }
                        
                        fail_word = bina_fail_word(respons.text, "ALASAN PENGHAKIMAN", meta_dict)
                        st.download_button("📄 Muat Turun AP (Word)", data=fail_word, file_name=f"AP_{m_nokes}.docx")
                    except Exception as e: st.error(f"Ralat: {e}")

# ==========================================
# MOD 2: KERTAS KERJA PENGURUSAN
# ==========================================
with tab_pengurusan:
    st.info("Gunakan format jadual 3 kolum seperti yang telah ditetapkan sebelum ini.")
    jenis_kertas = st.selectbox("Jenis Dokumen:", ["Kertas Kerja Bengkel / Program", "Kertas Konsep Arahan Amalan", "Kertas Kerja Bajet"])
    bahagian_unit = st.text_input("1. Bahagian / Unit Penyedia:")
    nama_program = st.text_input("2. Nama Program / Aktiviti:")
    tarikh_masa = st.text_input("3. Tarikh, Masa & Tempoh:")
    tempat_program = st.text_input("4. Tempat / Lokasi Program:")
    
    col1, col2 = st.columns(2)
    with col1:
        maklumat_peserta = st.text_area("5. Maklumat & Bilangan Peserta:", height=150)
        maklumat_penceramah = st.text_area("6. Maklumat Penceramah:", height=150)
    with col2:
        kos_makan_minum = st.text_area("7. Anggaran Kos Kewangan:", height=150)
        objektif_tambahan = st.text_area("8. Objektif & Latar Belakang Tambahan:", height=150)

    if st.button("🚀 Jana Kertas Cadangan Lengkap", type="primary", key="btn_pengurusan"):
        if nama_program.strip() == "" or bahagian_unit.strip() == "":
            st.warning("⚠️ Sila isi Bahagian/Unit dan Nama Program terlebih dahulu bro!")
        else:
            with st.spinner("Menyusun format Gred Kerajaan & mengira bajet..."):
                try:
                    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
                    db = Chroma(persist_directory="./database_vektor_google", embedding_function=embeddings)
                    
                    retriever = db.as_retriever(search_kwargs={"k": 5, "filter": {"sumber": "Pengurusan"}})
                    dokumen_relevan = retriever.invoke(jenis_kertas)
                    
                    konteks_teks = ""
                    for idx, doc in enumerate(dokumen_relevan):
                        konteks_teks += f"\n--- CONTOH TEMPLAT {idx+1} ---\n{doc.page_content}\n"

                    prompt_pengurusan = f"""Anda adalah Pegawai Tadbir Kanan di JKSM. Jana draf {jenis_kertas} yang rasmi.

PANDUAN STRUKTUR TEKS:
- DILARANG menggunakan simbol bintang (**) untuk tulisan Bold.
- JANGAN tulis tajuk utama. Terus mula dengan nombor 1 di bawah:

1. BAHAGIAN/UNIT 
{bahagian_unit}
2. TUJUAN 
3. LATAR BELAKANG ({objektif_tambahan})
4. OBJEKTIF PROGRAM 
5. BUTIR-BUTIR PROGRAM
(Tarikh: {tarikh_masa}, Tempat: {tempat_program})
(Peserta: {maklumat_peserta})
(Penceramah: {maklumat_penceramah})
6. ANGGARAN PERBELANJAAN
7. KESIMPULAN / PENUTUP

INPUT DATA KEWANGAN:
{kos_makan_minum}

ARAHAN KRITIKAL PEMBINAAN JADUAL (AMARAN KERAS):
1. Anda MESTI membina SATU JADUAL SAHAJA di bawah bahagian 6. ANGGARAN PERBELANJAAN.
2. Jadual tersebut WAJIB mempunyai TEPAT 3 KOLUM.
3. Nama 3 kolum tersebut WAJIB: | Bil. | Butiran | Jumlah |
4. JANGAN sesekali membina kolum bernama "Perkara", "Kadar", "Kuantiti", atau "Pengiraan". JIKA ANDA MEMBINA LEBIH DARI 3 KOLUM, ANDA GAGAL.
5. Masukkan SEMUA butiran pengiraan (cth: 30 orang x RM30) ke dalam kolum "Butiran". Gunakan <br> untuk baris baharu di dalam sel.
6. Baris terakhir jadual mesti bernama JUMLAH KESELURUHAN.

Rujuk gaya bahasa dokumen ini:
{konteks_teks}
"""
                    respons = cuba_jana_ai(prompt_pengurusan)
                    
                    st.divider()
                    st.subheader(f"💡 Hasil Penjanaan Kertas Cadangan AI ({jenis_kertas})")
                    st.write(respons.text)

                    # Dummy meta untuk elak ralat fungsi bina_fail_word
                    meta_dummy = {'mahkamah':'', 'hakim':'', 'tarikh':'', 'nokes':'', 'pihak1':'', 'pihak2':'', 'jenis_p':'', 'peguam':''}
                    
                    tajuk_rasmi = f"KERTAS PERMOHONAN KELULUSAN BERBELANJA BAGI\n{nama_program}\nJABATAN KEHAKIMAN SYARIAH MALAYSIA"
                    fail_pengurusan_docx = bina_fail_word(respons.text, tajuk_rasmi, meta_dummy)
                    
                    st.download_button("📄 Muat Turun Kertas Kerja (Word)", data=fail_pengurusan_docx, file_name=f"Kertas_Kerja.docx")

                except Exception as e: st.error(f"❌ Ralat Sistem: {e}")