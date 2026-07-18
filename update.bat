@echo off
echo ==============================================
echo  Mengambil update terbaru dari server (Git Pull)
echo ==============================================
echo.

git pull

echo.
echo ==============================================
echo  Menginstal library baru (jika ada)...
echo ==============================================
call .\venv\Scripts\activate.bat
pip install -r requirements.txt
echo.
echo ==============================================
echo  Proses update selesai!
echo ==============================================
pause
