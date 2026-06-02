import os
import re
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Buka kunci peti besi (.env)
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

def serap_alasan_penghakiman():
    print("🚀 Memulakan operasi menyedut 300+ Alasan Penghakiman dari Google Drive...")
    
    # LALUAN FOLDER GOOGLE DRIVE
    folder_gdrive = r"G:\My Drive\JKSM\BPKR\MyAIGeneratorSistem\Data Alasan Penghakiman (AP) Kes Lepas"
    
    # Semak kalau folder tu wujud
    if not os.path.exists(folder_gdrive):
        print(f"❌ Ralat: Folder tak dijumpai di {folder_gdrive}")
        return

    semua_dokumen = []
    senarai_fail = [f for f in os.listdir(folder_gdrive) if f.endswith('.pdf')]
    jumlah_fail = len(senarai_fail)
    
    print(f"📂 Dijumpai {jumlah_fail} fail PDF. Sedang memproses...\n")

    # 2. Proses setiap fail satu per satu
    for indeks, filename in enumerate(senarai_fail):
        laluan_fail = os.path.join(folder_gdrive, filename)
        
        try:
            loader = PyPDFLoader(laluan_fail)
            docs = loader.load()
            
            bahagian = filename.replace(".pdf", "").split("_")
            
            if len(bahagian) >= 5:
                metadata_khas = {
                    "kategori": bahagian[0],
                    "isu": bahagian[1],
                    "tahun": bahagian[2],
                    "pihak": bahagian[3],
                    "no_kes": bahagian[4],
                    "sumber": "Alasan Penghakiman"
                }
            else:
                metadata_khas = {"sumber": "Alasan Penghakiman", "isu": "Umum"}
            
            for doc in docs:
                doc.metadata.update(metadata_khas)
            
            semua_dokumen.extend(docs)
            print(f"✅ [{indeks+1}/{jumlah_fail}] Berjaya hadam: {filename}")
            
        except Exception as e:
            print(f"❌ Gagal baca {filename}: {e}")

    # 3. Potong teks
    print("\n✂️ Memotong ribuan muka surat menjadi memori kecil untuk AI...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    ketulan_teks = text_splitter.split_documents(semua_dokumen)
    jumlah_ketulan = len(ketulan_teks)
    print(f"Terhasil {jumlah_ketulan} ketulan memori.")

    # 4. Tukar kepada Vektor secara BERPERINGKAT (Teknik Kura-Kura 🐢)
    print("\n🧠 Sedang menyuntik memori ke dalam Otak AI (Teknik Kura-kura Aktif)...")
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    direktori_db = "./database_vektor_google"
    
    db = Chroma(persist_directory=direktori_db, embedding_function=embeddings)
    
    # Kita hantar sikit-sikit (15 ketul sekali suap)
    saiz_batch = 15
    
    for i in range(0, jumlah_ketulan, saiz_batch):
        batch_ketulan = ketulan_teks[i : i + saiz_batch]
        print(f"🐢 Menyuntik memori {i+1} hingga {min(i+saiz_batch, jumlah_ketulan)} daripada {jumlah_ketulan}...")
        
        # Try-Except supaya kalau Google sekat, skrip tak mati tapi rehat sekejap
        try:
            db.add_documents(batch_ketulan)
        except Exception as e:
            print("   ⚠️ Terlanggar had laju! Kura-kura rehat extra 30 saat...")
            time.sleep(30)
            db.add_documents(batch_ketulan)
        
        # Rehat 12 saat setiap kali suap (Sangat selamat untuk Kuota Percuma)
        if i + saiz_batch < jumlah_ketulan:
            time.sleep(12)
            
    print("\n🎉 SIAP SEPENUHNYA! Kesemua Alasan Penghakiman kini telah menjadi memori kekal AI kau bro!")

if __name__ == "__main__":
    serap_alasan_penghakiman()