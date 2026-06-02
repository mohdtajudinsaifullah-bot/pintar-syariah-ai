import os
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Buka kunci peti besi (.env)
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

def bina_database_vektor_google(path_fail):
    print(f"\n[1] Mula membaca fail: {path_fail}...")
    loader = PyMuPDFLoader(path_fail)
    dokumen = loader.load()
    
    pemotong_teks = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = pemotong_teks.split_documents(dokumen)
    print(f"[2] Berjaya potong PDF kepada {len(chunks)} bahagian.")
    
    print("[3] Menghantar teks ke Google Gemini untuk ditukar ke vektor...")
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    
    direktori_db = "./database_vektor_google"
    print("[4] Sedang menyimpan pangkalan data secara berperingkat (Taktik Kura-Kura)...")
    
    # Buat sambungan database
    db = Chroma(persist_directory=direktori_db, embedding_function=embeddings)
    
    # Masukkan data sikit-sikit (50 chunk sekali masuk)
    saiz_batch = 50
    for i in range(0, len(chunks), saiz_batch):
        batch = chunks[i : i + saiz_batch]
        print(f" -> Memproses chunk {i+1} hingga {i+len(batch)}...")
        
        # Tambah ke dalam database
        db.add_documents(batch)
        
        # Suruh sistem rehat 35 saat untuk reset limit 1 Minit Google
        if i + saiz_batch < len(chunks):
            print("    [Rehat 35 saat sambil minum kopi jap...]")
            time.sleep(35)
            
    print(f"\n🚀 BERJAYA! Otak Google sedia digunakan di dalam folder: {direktori_db}")
    return db

if __name__ == "__main__":
    lokasi_fail = "data_ujian/UU_KeluargaIslam_Selangor_2003.pdf"
    database = bina_database_vektor_google(lokasi_fail)