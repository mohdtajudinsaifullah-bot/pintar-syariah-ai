import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate

# 1. Buka kunci peti besi (.env)
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

def draf_keputusan_hakim():
    print("Memuatkan Otak AI (Mencari Data & Berfikir)...")
    
    # --- BAHAGIAN 1: PENCARIAN (RETRIEVAL) ---
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    direktori_db = "./database_vektor_google"
    db = Chroma(persist_directory=direktori_db, embedding_function=embeddings)
    
    fakta_kes = "Suami saya telah ghaib dan hilang lebih daripada satu tahun. Saya nak tuntut cerai."
    print(f"\nFakta Kes: '{fakta_kes}'")
    
    # Cari 3 rekod terbaik
    hasil_carian = db.similarity_search(fakta_kes, k=3)
    
    # Gabungkan teks akta yang dijumpai jadi satu rujukan panjang
    teks_rujukan = "\n\n".join([doc.page_content for doc in hasil_carian])
    
    # --- BAHAGIAN 2: PENJANAAN (GENERATION) ---
    # Kita guna model LLM Gemini 1.5 Flash yang sangat laju dan bijak
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
    
    # Ini adalah "Prompt Engineering" untuk ajar AI peranan dia
    templat_arahan = """
    Anda adalah seorang Pembantu Hakim Syarie di Malaysia yang sangat pakar dalam undang-undang keluarga Islam.
    Tugas anda adalah untuk menyediakan satu draf ringkas ulasan perundangan berdasarkan FAKTA KES dan PERUNTUKAN UNDANG-UNDANG yang diberikan SAHAJA.
    
    FAKTA KES:
    {fakta}
    
    PERUNTUKAN UNDANG-UNDANG (RUJUKAN):
    {rujukan}
    
    Sila hasilkan draf ulasan perundangan yang merangkumi susunan berikut:
    1. Isu Utama.
    2. Pemakaian Undang-Undang (Sebutkan seksyen yang relevan berdasarkan rujukan).
    3. Syor Tindakan/Keputusan.
    
    Gunakan Bahasa Melayu laras undang-undang mahkamah yang profesional, kemas dan meyakinkan.
    """
    
    prompt = PromptTemplate(
        input_variables=["fakta", "rujukan"],
        template=templat_arahan
    )
    
    # Gabungkan Prompt dan LLM
    print("\nSedang menganalisis akta dan menulis draf ulasan... (Sila tunggu sekejap)\n")
    chain = prompt | llm
    
    # Arahkan AI mulakan kerja
    jawapan_ai = chain.invoke({"fakta": fakta_kes, "rujukan": teks_rujukan})
    
    # Paparkan hasil
    print("="*70)
    print("DRAF ULASAN PERUNDANGAN AI (ALASAN PENGHAKIMAN)")
    print("="*70)
    print(jawapan_ai.content)
    print("="*70)

if __name__ == "__main__":
    draf_keputusan_hakim()