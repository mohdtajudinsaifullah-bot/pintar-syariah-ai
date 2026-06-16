from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Buka kunci
load_dotenv(override=True)

print("🔍 Sedang mengimbas otak AI...")

# Sambung ke database
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
db = Chroma(persist_directory="./database_vektor_google", embedding_function=embeddings)

# Kira jumlah vektor (cebisan ayat)
jumlah_memori = db._collection.count()

print("=======================================")
print(f"🧠 JUMLAH MEMORI AI SEKARANG: {jumlah_memori} cebisan data")
print("=======================================")
print("💡 Tip: Kalau nombor ni makin bertambah dari semalam,")
print("maknanya AI dah berjaya hafal fail PDF baru!")