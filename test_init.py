import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow

app = QApplication(sys.argv)
try:
    print("Mencoba inisialisasi MainWindow...")
    window = MainWindow()
    print("Berhasil!")
except Exception as e:
    import traceback
    traceback.print_exc()
