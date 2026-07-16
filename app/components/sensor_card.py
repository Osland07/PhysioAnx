from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

class SensorCard(QFrame):
    """Komponen kartu (kotak) kecil untuk menampilkan angka Heart Rate atau Suhu"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("SensorCard")
        # Layout kartu
