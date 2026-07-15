@echo off
echo ===================================================
echo ROBOT MALAM AIMS - KEMAS KINI MEMORI AI
echo ===================================================

:: TUKAR JALUR DI BAWAH IKUT FOLDER PROJEK KAU YANG SEBENAR (Aku anggap kat C:)
cd /d "C:\ai-syariah-backend" 

echo Menghidupkan Virtual Environment...
call venv\Scripts\activate.bat

echo Menjalankan Skrip Penyerapan Google Drive...
python auto_serap_gdrive.py

echo Menghantar Kemas Kini Memori ke Streamlit Cloud (GitHub)...
git add database_vektor_google rekod_fail_diproses.txt
git commit -m "Auto-Update: Memori AI baharu dari Google Drive"
git push origin main

echo Selesai! Mengunci terminal...
exit