#!/bin/bash

# Pindah ke direktori tempat script ini berada (folder project)
cd "$(dirname "$0")"

echo "================================================="
echo "  Mulai Otomatisasi Setup PhysioAnx untuk Mac..."
echo "================================================="

# Cek apakah Python3 tersedia di sistem
if ! command -v python3 &> /dev/null
then
    echo "ERROR: python3 tidak ditemukan di Mac Anda."
    echo "Silakan install Python 3 terlebih dahulu dari https://www.python.org/downloads/"
    read -n 1 -s -r -p "Tekan tombol apa saja untuk keluar..."
    exit 1
fi

echo "[1/4] Membuat Virtual Environment (venv)..."
python3 -m venv venv

echo "[2/4] Mengaktifkan Virtual Environment..."
source venv/bin/activate

echo "[3/4] Menginstal Library Python (bisa memakan waktu beberapa menit)..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo "[4/4] Mem-build Aplikasi macOS (.app)..."
# Membangun aplikasi dengan PyInstaller
pyinstaller --name "PhysioAnx" --windowed --onedir --add-data "app/assets:app/assets" --osx-bundle-identifier "com.physioanx.app" app/main.py

echo "================================================="
echo "  SELESAI!"
echo "  Aplikasi Mac Anda berhasil dibuat di folder 'dist'."
echo "================================================="

# Secara otomatis membuka folder hasil build di Mac
open dist

echo ""
echo "Silakan pindahkan aplikasi PhysioAnx (.app) yang ada di jendela tersebut ke folder Applications Mac Anda."
read -n 1 -s -r -p "Tekan tombol apa saja untuk menutup layar ini..."
