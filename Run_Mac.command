#!/bin/bash

# Pindah ke direktori tempat script ini berada (folder project)
cd "$(dirname "$0")"

echo "================================================="
echo "  Menyiapkan Aplikasi PhysioAnx (Mac)..."
echo "================================================="

# Mengecek apakah ada Virtual Environment. Jika ada, aktifkan.
if [ -d "venv" ]; then
    echo "[INFO] Mengaktifkan Virtual Environment..."
    source venv/bin/activate
else
    echo "[INFO] Virtual Environment tidak ditemukan. Menggunakan Python Global."
fi

echo ""
echo "[INFO] Membuka Jendela Utama..."
python3 app/main.py

# Jika terjadi error (misalnya library belum di-install), tahan layar
if [ $? -ne 0 ]; then
    echo ""
    echo "================================================="
    echo "[ERROR] Aplikasi gagal berjalan atau berhenti."
    echo "Pastikan Anda sudah menginstal library dengan menjalankan 'Setup_Mac.command' terlebih dahulu."
    echo "================================================="
    read -n 1 -s -r -p "Tekan tombol apa saja untuk keluar..."
fi
