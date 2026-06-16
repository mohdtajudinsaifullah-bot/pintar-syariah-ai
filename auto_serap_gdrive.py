import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Buka kunci (.env)
load_dotenv(override=True)

# 2. Senarai Direktori Google Drive Desktop (Drive G:)
BASE_DIR = r"G:\My Drive\JKSM\BPKR\MyAIGeneratorSistem"

FOLDERS = {
    "Data Alasan Penghakiman (AP) Kes Lepas": "Alasan Penghakiman",
    "Data Arahan Amalan JKSM": "Arahan Amalan",
    "Data Nas Syarak (Quran & Hadis)": "Nas Syarak",
    "Data Templat Pengurusan": "Pengurusan",
    "Data Undang-Undang (Enakmen Akta)": "Undang-Undang",
    "Kitab Ulama Muktabar": "Kitab"
}

DB_DIR = "./database_vektor_google"
LOG_FILE = "rekod_fail_diproses.txt"

def dapatkan_rekod():
    if not os.path.exists(LOG_FILE): return set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def simpan_rekod(filename):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(filename + "\n")

def proses_dan_simpan():
    print("🤖 Memulakan Robot Penyerapan X-Ray Google Drive...")
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=300)
    
    rekod_lama = dapatkan_rekod()
    ada_data_baru = False

    for folder_name, kategori in FOLDERS.items():
        folder_path = os.path.join(BASE_DIR, folder_name)
        if not os.path.exists(folder_path):
            print(f"⚠️ Abaikan: Folder '{folder_name}' tidak dijumpai.")
            continue
            
        # Guna os.walk untuk SELAM ke dalam semua sub-folder (cth: Selangor, Perak)
        for root, dirs, files in os.walk(folder_path):
            for fail in files:
                if fail.lower().endswith(".pdf"):
                    fail_path = os.path.join(root, fail)
                    
                    # Semak kalau fail ni dah pernah diserap
                    if fail_path in rekod_lama:
                        continue 
                    
                    print(f"📥 Menyedut fail baharu: {fail} (Kategori: {kategori})")
                    try:
                        loader = PyPDFLoader(fail_path)
                        documents = loader.load()
                        
                        for doc in documents:
                            doc.metadata['sumber'] = kategori
                            
                        chunks = text_splitter.split_documents(documents)
                        db.add_documents(chunks)
                        
                        simpan_rekod(fail_path)
                        ada_data_baru = True
                    except Exception as e:
                        print(f"❌ Gagal membaca {fail}: {e}")

    if ada_data_baru:
        print("\n✅ Pangkalan data vektor berjaya dikemas kini dengan fail baharu!")
    else:
        print("\n💤 Tiada fail PDF baharu dijumpai. Pangkalan data dikekalkan.")

if __name__ == "__main__":
    proses_dan_simpan()