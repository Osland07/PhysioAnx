@echo off
title PhysioAnx - Installer
chcp 65001 >nul
echo.
echo  ============================================================
echo   PhysioAnx ^| Setup dan Instalasi Dependensi
echo  ============================================================
echo.

cd /d "%~dp0"


echo [1/4] Mengecek instalasi Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Python tidak ditemukan!
    echo.
    echo  Solusi:
    echo    1. Download Python dari https://www.python.org/downloads/
    echo    2. Saat instalasi, CENTANG "Add Python to PATH"
    echo    3. Restart laptop, lalu jalankan install.bat lagi
    echo.
    pause
    exit /b 1
)
python --version
echo  [OK] Python ditemukan.
echo.


echo [2/4] Menyiapkan Virtual Environment (venv)...
if not exist "venv\Scripts\activate.bat" (
    echo  Membuat venv baru...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo.
        echo  [ERROR] Gagal membuat virtual environment.
        echo  Coba jalankan sebagai Administrator atau cek apakah Python lengkap ter-install.
        echo.
        pause
        exit /b 1
    )
    echo  [OK] Virtual environment berhasil dibuat.
) else (
    echo  [OK] Virtual environment sudah ada, digunakan kembali.
)
echo.


echo [3/4] Mengaktifkan Virtual Environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Gagal mengaktifkan venv.
    echo  Coba hapus folder "venv" dan jalankan install.bat lagi.
    echo.
    pause
    exit /b 1
)
echo  [OK] Virtual environment aktif.
echo.


echo [4/4] Menginstal semua library (mungkin memerlukan beberapa menit)...
echo  Sedang mengupgrade pip...
python -m pip install --upgrade pip --quiet
echo  Sedang menginstall requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Gagal menginstall library!
    echo.
    echo  Kemungkinan penyebab:
    echo    - Tidak ada koneksi internet
    echo    - Versi Python terlalu lama (butuh Python 3.10+)
    echo    - requirements.txt tidak ditemukan
    echo.
    echo  Coba jalankan perintah ini secara manual di Command Prompt:
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo.


echo  ============================================================
echo   [SUKSES] Instalasi selesai tanpa error!
echo  ============================================================
echo.
echo   Cara menjalankan aplikasi:
echo     Klik dua kali file "run.bat"
echo   atau jalankan perintah:
echo     python app\main.py
echo.
pause
