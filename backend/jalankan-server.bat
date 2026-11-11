@echo off
REM Menyalakan backend Kostopia (FastAPI) di port 8000.
REM Bisa diakses dari HP di Wi-Fi yang sama lewat http://<IP-laptop>:8000
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [!] Folder .venv belum ada. Jalankan dulu:
  echo     py -3.12 -m venv .venv
  echo     .venv\Scripts\pip install -r requirements.txt
  pause
  exit /b 1
)
if not exist ".env" (
  echo [!] File .env belum ada. Salin .env.example menjadi .env lalu isi DATABASE_URL.
  pause
  exit /b 1
)
echo Menyalakan server Kostopia di http://localhost:8000  (dokumentasi API: /docs)
echo Tekan Ctrl+C untuk berhenti.
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
