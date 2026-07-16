from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt

class LoginView(QWidget):
    """Halaman pertama kali dibuka untuk Dokter/Psikolog login"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Nanti kita isi dengan form username & password yang rapi
