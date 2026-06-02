import os
import re

def tukar_nama_pukal():
    # Pastikan kau letak fail-fail PDF tu dalam folder ni
    folder_path = "./AP_Raw" 
    
    print("Memulakan operasi menukar nama berdasarkan Tahun dari No. Kes...")
    
    berjaya = 0
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            try:
                # 1. Tangkap No Kes (Corak: 10000-003-0141-2019)
                # Kita letak kurungan pada 4 digit terakhir tu supaya Python tangkap dia sebagai 'Tahun'
                no_kes_match = re.search(r'(\d{5}-\d{3}-\d{4}-(\d{4}))', filename)
                
                if no_kes_match:
                    no_kes = no_kes_match.group(1) # Cth: 10000-003-0141-2019
                    tahun = no_kes_match.group(2)  # Cth: 2019 (Ngam-ngam ambil hujung je)
                else:
                    no_kes = "NOKES"
                    tahun = "TAHUN"
                
                # 2. Tangkap Nama Pihak (Cari ayat dalam kurungan)
                pihak_match = re.search(r'\((.*?)\)', filename)
                if pihak_match:
                    # Tukar "vs" jadi "_lwn_" dan buang jarak (space)
                    pihak = pihak_match.group(1).replace(" vs ", "_lwn_").replace(" ", "")
                else:
                    pihak = "PIHAK"
                
                # 3. Cantumkan jadi format standard Gred Industri
                nama_baru = f"KATEGORI_ISU_{tahun}_{pihak}_{no_kes}.pdf"
                
                # 4. Laksanakan pertukaran nama
                path_lama = os.path.join(folder_path, filename)
                path_baru = os.path.join(folder_path, nama_baru)
                
                os.rename(path_lama, path_baru)
                print(f"✅ {nama_baru}")
                berjaya += 1
                
            except Exception as e:
                print(f"❌ Gagal proses: {filename} | Ralat: {e}")
                
    print(f"\n🚀 SELESAI! {berjaya} fail telah berjaya ditukar nama.")

if __name__ == "__main__":
    tukar_nama_pukal()