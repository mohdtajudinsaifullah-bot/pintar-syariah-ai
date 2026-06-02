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

# 1. Buka kunci peti besi (.env)
load_dotenv(override=True)
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
api_key_google = os.environ["GOOGLE_API_KEY"]

# --- FUNGSI PENYERAP HENTAKAN (AUTO-RETRY) ---
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
                    
    raise Exception("Maaf, Pelayan Google sedang terlampau sesak atau versi model tidak tepat. Sila cuba sebentar lagi.")

# --- FUNGSI BINA FAIL WORD (SUSUNAN PERENGGAN & SPACING DIPERBAIKI) ---
def bina_fail_word(teks_ai, tajuk_dokumen):
    doc = Document()
    
    # TETAPAN KESELURUHAN WORD: Arial, Saiz 11, Single Spacing (1.0)
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)
    style.paragraph_format.line_spacing = 1.0 # Single Spacing
    style.paragraph_format.space_before = Pt(0)
    # Default space_after kita set ke 0 dulu, kita ubah ikut jenis perenggan kat bawah
    style.paragraph_format.space_after = Pt(0) 
    
    tajuk_p = doc.add_paragraph()
    tajuk_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tajuk_p.paragraph_format.space_after = Pt(12) # Jarak 1 baris kosong selepas tajuk utama
    run_tajuk = tajuk_p.add_run(tajuk_dokumen.upper())
    run_tajuk.bold = True
    run_tajuk.font.name = 'Arial'
    run_tajuk.font.size = Pt(12)
    run_tajuk.font.color.rgb = RGBColor(0, 0, 0)
    
    teks_bersih_total = teks_ai.replace('**', '').replace('##', '')
    lines = teks_bersih_total.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 1. KESAN JADUAL
        if line.startswith('|'):
            table_data = []
            while i < len(lines) and (lines[i].strip().startswith('|') or lines[i].strip().startswith('+-')):
                if not all(c in '|- ' for c in lines[i].strip()):
                    cells = [c.strip() for c in lines[i].strip().split('|') if c.strip()]
                    if cells:
                        table_data.append(cells)
                i += 1
            
            if table_data:
                table = doc.add_table(rows=len(table_data), cols=len(table_data[0]))
                table.style = 'Table Grid'
                for r_idx, row_cells in enumerate(table_data):
                    for c_idx, cell_text in enumerate(row_cells):
                        cell = table.rows[r_idx].cells[c_idx]
                        clean_text = cell_text.replace('<br>', '\n').strip()
                        cell.text = clean_text
                        for paragraph in cell.paragraphs:
                            paragraph.paragraph_format.space_after = Pt(0) # Dalam jadual mesti rapat
                            for run in paragraph.runs:
                                run.font.name = 'Arial'
                                run.font.size = Pt(11)
            
            # Tambah 1 baris kosong selepas jadual tamat
            p_space = doc.add_paragraph()
            p_space.paragraph_format.space_after = Pt(12)
            continue 
            
        # 2. KESAN TEKS CENTER (Kepala Surat AP)
        elif line.startswith('<CENTER>'):
            clean_center = line.replace('<CENTER>', '').strip()
            p = doc.add_paragraph(clean_center)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0) # Kepala surat mesti rapat-rapat
            
        # 3. KESAN TAJUK & SUB-TAJUK (Bold)
        elif any(line.startswith(str(n)+'.') for n in range(1, 20)):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12) # Tambah jarak kosong SEBELUM tajuk nombor baru
            p.paragraph_format.space_after = Pt(6)   # Tambah jarak sikit SELEPAS tajuk nombor
            run = p.add_run(line)
            run.bold = True 
            run.font.name = 'Arial'
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(0, 0, 0)
            
        # 4. TEKS BIASA / HURAIAN (Justify & Jarak Antara Perenggan)
        elif line:
            p = doc.add_paragraph(line)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY 
            p.paragraph_format.space_after = Pt(12) # Masukkan 1 baris kosong secara automatik selepas perenggan
            
        i += 1
            
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# 2. Tetapan Paparan Web Streamlit
st.set_page_config(page_title="Pintar Syariah AI", page_icon="⚖️", layout="wide")

st.title("⚖️ Papan Pemuka Pintar Syariah AI")
st.markdown("*Sistem Pintar Rujukan Undang-Undang, Alasan Penghakiman & Penjanaan Kertas Kerja Pengurusan*")
st.divider()

with st.sidebar:
    st.header("⚙️ Tetapan Umum")
    negeri_pilihan = st.selectbox(
        "Bidang Kuasa (Negeri)", 
        ["Selangor", "Wilayah Persekutuan", "Johor", "Perak", "Kedah", "Kelantan", "Terengganu", "Pahang", "Negeri Sembilan", "Melaka", "Pulau Pinang", "Perlis", "Sabah", "Sarawak"]
    )
    st.divider()

tab_kes, tab_pengurusan = st.tabs(["🏛️ Mod 1: Analisis Kes Syariah (AP)", "📝 Mod 2: Penjanaan Kertas Kerja & Konsep"])

# ==========================================
# MOD 1: ANALISIS KES SYARIAH (AP)
# ==========================================
with tab_kes:
    st.subheader("📝 Fakta Kes & Tuntutan Mahkamah")
    kategori_kes = st.radio("Kategori Kes:", ["Mal (Keluarga / Harta / DLL)", "Jenayah Syariah"], horizontal=True)
    fakta_kes = st.text_area("Masukkan ringkasan fakta kes di sini:", height=150)

    if st.button("🔍 Jana Analisis Kes & AP", type="primary", key="btn_kes"):
        if fakta_kes.strip() == "":
            st.warning("⚠️ Sila masukkan fakta kes terlebih dahulu bro!")
        else:
            with st.spinner("Menyelongkar Alasan Penghakiman kes lepas..."):
                try:
                    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
                    db = Chroma(persist_directory="./database_vektor_google", embedding_function=embeddings)
                    
                    retriever = db.as_retriever(search_kwargs={"k": 7, "filter": {"sumber": "Alasan Penghakiman"}})
                    dokumen_relevan = retriever.invoke(fakta_kes)
                    
                    konteks_teks = ""
                    for idx, doc in enumerate(dokumen_relevan):
                        konteks_teks += f"\n--- RUJUKAN AP {idx+1} ---\n{doc.page_content}\n"

                    # PROMPT ANTI-HALUSINASI & LARAS BAHASA DIPERBAIKI
                    prompt_lengkap = f"""Anda adalah Pembantu Kanan Hakim Syarie. Drafkan ALASAN PENGHAKIMAN (AP) yang rasmi meniru format AP rujukan.

ARAHAN KETAT MAKLUMAT SULIT & TATABAHASA UNDANG-UNDANG:
1. JANGAN SESEKALI menyalin Nama Pihak, No Kad Pengenalan, Nama Hakim, Nama Mahkamah, atau No Kes daripada DOKUMEN RUJUKAN.
2. Anda WAJIB menggunakan "placeholder" kurungan segi empat bagi maklumat pihak-pihak. Contohnya: [NAMA PEMOHON], [NO K/P PEMOHON], [NAMA RESPONDEN], [NAMA HAKIM], [NAMA MAHKAMAH], [DAERAH], [NO KES].
3. Rujukan kes lepas HANYA digunakan untuk meniru struktur format, gaya bahasa, dan menyalin ayat hujah undang-undang yang relevan dengan fakta kes semasa.
4. AMARAN BESAR: Di bahagian KEPUTUSAN / PERINTAH, anda DILARANG SAMA SEKALI menggunakan perkataan "SAYA SABITKAN" atau "SAYA PERINTAHKAN". Anda WAJIB menggantikannya dengan perkataan "MAHKAMAH SABITKAN" dan "MAHKAMAH MEMERINTAHKAN".

ARAHAN FORMAT KEPALA SURAT (CENTER):
Letakkan kod <CENTER> pada awal setiap baris untuk bahagian Kepala Surat.
Contoh Format Wajib Ditiru:
<CENTER>DI DALAM MAHKAMAH [NAMA MAHKAMAH] DI [DAERAH]
<CENTER>DALAM NEGERI {negeri_pilihan}, MALAYSIA
<CENTER>PERMOHONAN NO: [NO KES]
<CENTER>ANTARA
<CENTER>[NAMA PEMOHON] (NO. K/P: [NO K/P PEMOHON]) ... PEMOHON
<CENTER>DENGAN
<CENTER>[NAMA RESPONDEN] (NO. K/P: [NO K/P RESPONDEN]) ... RESPONDEN
<CENTER>DI HADAPAN YANG ARIF [NAMA HAKIM]

Fakta Kes Semasa:
{fakta_kes}

Struktur Wajib Draf:
(Gunakan <CENTER> untuk bahagian Kepala Surat seperti diajar di atas)
1. PENDAHULUAN
2. ISU-ISU YANG PERLU DIPUTUSKAN
3. UNDANG-UNDANG YANG DIPAKAI
4. PENILAIAN KETERANGAN & ALASAN PENGHAKIMAN
5. KEPUTUSAN (Wajib guna terma MAHKAMAH SABITKAN / MAHKAMAH MEMERINTAHKAN)

Rujukan Format dan Hujah Kes Lepas:
{konteks_teks}
"""
                    respons = cuba_jana_ai(prompt_lengkap)
                    
                    st.divider()
                    st.subheader("💡 Draf Alasan Penghakiman")
                    st.write(respons.text)

                    fail_docx = bina_fail_word(respons.text, f"ALASAN PENGHAKIMAN KES {kategori_kes.upper()}")
                    st.download_button("📄 Muat Turun AP (Word)", data=fail_docx, file_name=f"AP_{negeri_pilihan}.docx")

                except Exception as e: st.error(f"❌ Ralat: {e}")

# ==========================================
# MOD 2: PENJANAAN KERTAS KERJA & KONSEP
# ==========================================
with tab_pengurusan:
    st.subheader("📝 Borang Maklumat Kertas Kerja / Kertas Konsep")
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

CONTOH JADUAL YANG BETUL:
| Bil. | Butiran | Jumlah |
|---|---|---|
| 1. | BAYARAN ELAUN PENCERAMAH<br>RM90.00 x 7 jam = RM630.00 | RM630.00 |
| | JUMLAH KESELURUHAN | RM630.00 |

Rujuk gaya bahasa dokumen ini:
{konteks_teks}
"""
                    respons = cuba_jana_ai(prompt_pengurusan)
                    
                    st.divider()
                    st.subheader(f"💡 Hasil Penjanaan Kertas Cadangan AI ({jenis_kertas})")
                    st.write(respons.text)

                    tajuk_rasmi = f"KERTAS PERMOHONAN KELULUSAN BERBELANJA BAGI\n{nama_program}\nJABATAN KEHAKIMAN SYARIAH MALAYSIA"
                    fail_pengurusan_docx = bina_fail_word(respons.text, tajuk_rasmi)
                    
                    st.download_button("📄 Muat Turun Kertas Kerja (Word)", data=fail_pengurusan_docx, file_name=f"Kertas_Kerja.docx")

                except Exception as e: st.error(f"❌ Ralat Sistem: {e}")