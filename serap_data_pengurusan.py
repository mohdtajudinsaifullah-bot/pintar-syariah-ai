import os
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Load API Key
load_dotenv()

def serap_pengurusan():
    print("📂 Memulakan operasi menyedut Data Templat Pengurusan...")
    
    # LALUAN FOLDER PENGURUSAN
    folder_path = r"G:\My Drive\JKSM\BPKR\MyAIGeneratorSistem\Data Templat Pengurusan"
    
    if not os.path.exists(folder_path):
        print(f"❌ Ralat: Folder tidak dijumpai di {folder_path}")
        return

    semua_dokumen = []
    senarai_fail = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    
    print(f"📄 Dijumpai {len(senarai_fail)} fail PDF Pengurusan. Sedang memproses...")

    for indeks, filename in enumerate(senarai_fail):
        path = os.path.join(folder_path, filename)
        try:
            loader = PyPDFLoader(path)
            docs = loader.load()
            
            # PECAHKAN METADATA: JENIS_TOPIK_TAHUN_BAHAGIAN_STATUS.pdf
            bahagian = filename.replace(".pdf", "").split("_")
            
            if len(bahagian) >= 5:
                meta = {
                    "jenis": bahagian[0],      # KertasKerja / KertasKonsep / KertasBajet
                    "topik": bahagian[1],      # BengkelAI / ICT / SekatanTelefon
                    "tahun": bahagian[2],
                    "bahagian": bahagian[3],   # BPKR / JKSM
                    "status": bahagian[4],     # Lulus / Final
                    "sumber": "Pengurusan"     # <--- PENANDA UTAMA MOD 2
                }
            else:
                meta = {"sumber": "Pengurusan", "jenis": "Umum"}
            
            for d in docs:
                d.metadata.update(meta)
            
            semua_dokumen.extend(docs)
            print(f"✅ [{indeks+1}/{len(senarai_fail)}] Hadam: {filename}")
            
        except Exception as e:
            print(f"❌ Gagal: {filename} - {e}")

    # Potong Teks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    ketulan = splitter.split_documents(semua_dokumen)
    
    # Suntik masuk otak AI
    print(f"\n🧠 Menyuntik {len(ketulan)} ketulan data pengurusan ke Otak AI...")
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    db = Chroma(persist_directory="./database_vektor_google", embedding_function=embeddings)
    
    # Teknik Kura-kura Perisai Besi (Auto-Resume) 🐢🛡️
    saiz_batch = 15
    for i in range(0, len(ketulan), saiz_batch):
        batch = ketulan[i : i + saiz_batch]
        print(f"🐢 Batch {i+1} hingga {min(i+saiz_batch, len(ketulan))}...")
        
        try:
            db.add_documents(batch)
        except Exception as e:
            print(f"   ⚠️ Ops! Terlanggar roadblock Google (Ralat 429). Kura-kura rehat extra 60 saat...")
            time.sleep(60) # Kita bagi dia tidur seminit terus supaya Google betul-betul cool down
            db.add_documents(batch) # Cuba tembak sekali lagi
            
        time.sleep(15) # Rehat standard dinaikkan ke 15 saat

    print("\n🎉 SIAP! AI kau sekarang dah pakar dalam bab Kertas Kerja & Bajet!")

if __name__ == "__main__":
    serap_pengurusan()