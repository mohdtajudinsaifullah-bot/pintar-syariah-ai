import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Buka kunci peti besi (.env)
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

def cari_maklumat():
    print("Memuatkan enjin carian Google Gemini...")
    
    # 2. Guna enjin Embedding Google (Mesti sama macam masa kita simpan)
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    
    # 3. Sambungkan ke folder database baru kita
    direktori_db = "./database_vektor_google"
    db = Chroma(persist_directory=direktori_db, embedding_function=embeddings)
    
    # 4. Soalan / Fakta Kes
    fakta_kes = "Suami saya telah ghaib dan hilang lebih daripada satu tahun. Saya nak tuntut cerai."
    print(f"\nFakta Kes Masuk: '{fakta_kes}'")
    print("Mencari peruntukan undang-undang yang relevan...\n")
    
    # 5. Arahkan AI cari 3 bahagian teks yang paling tepat (k=3)
    hasil_carian = db.similarity_search(fakta_kes, k=3)
    
    # 6. Paparkan hasil carian
    for i, hasil in enumerate(hasil_carian):
        print(f"--- JUMPA REKOD KE-{i+1} ---")
        print(hasil.page_content)
        print("-" * 50 + "\n")

if __name__ == "__main__":
    cari_maklumat()