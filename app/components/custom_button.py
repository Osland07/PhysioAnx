from PySide6.QtWidgets import QPushButton

class CustomButton(QPushButton):
    """Komponen tombol yang sudah disesuaikan warnanya (Emas/Biru)"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        # Nanti kita bisa tambah animasi atau efek suara di sini
