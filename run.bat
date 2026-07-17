@echo off
title Launcher PhysioAnx
echo ==============================================
echo Menyiapkan Aplikasi PhysioAnx...
echo ==============================================

cd /d "%~dp0"

IF EXIST "venv\Scripts\activate.bat" (
    echo [INFO] Mengaktifkan Virtual Environment...
    call venv\Scripts\activate.bat
) ELSE (
    echo [INFO] Virtual Environment tidak ditemukan. Menggunakan Python Global.
)

echo.
echo [INFO] Membuka Jendela Utama...
python app\main.py

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==============================================
    echo [ERROR] Aplikasi gagal berjalan atau berhenti.
    echo Pastikan Anda sudah menginstall library dengan perintah:
    echo pip install -r requirements.txt
    echo ==============================================
    pause
)
