import sys
import os
from PySide6.QtWidgets import QApplication
from main_window import MainWindow

def load_stylesheet(app):
    """Membaca file theme.qss untuk memberikan warna biru dan emas pada aplikasi"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    qss_path = os.path.join(current_dir, 'assets', 'styles', 'theme.qss')
    
    try:
        with open(qss_path, 'r') as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Peringatan: File theme.qss tidak ditemukan. Aplikasi akan memakai warna standar abu-abu.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load tema warna (Rasio 60-30-10)
    load_stylesheet(app)
    
    # Tampilkan jendela utama
    window = MainWindow()
    window.show()
    
    # Jalankan aplikasi (Event Loop)
    sys.exit(app.exec())
