@echo off
echo ==============================================
echo  PhysioAnx - Instalasi Dependencies
echo ==============================================
echo.

:: Cek apakah Python terinstal
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan. Pastikan Python sudah terinstal dan ditambahkan ke PATH.
    pause
    exit /b
)

:: Buat virtual environment jika belum ada
if not exist "venv" (
    echo [INFO] Membuat Virtual Environment (venv)...
    python -m venv venv
) else (
    echo [INFO] Virtual Environment sudah ditemukan.
)

:: Aktifkan virtual environment dan install requirement
echo [INFO] Menginstal / Memperbarui dependensi dari requirements.txt...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ==============================================
echo  Instalasi selesai tanpa masalah!
echo  Silakan jalankan file "run.bat" untuk membuka aplikasi.
echo ==============================================
pause
