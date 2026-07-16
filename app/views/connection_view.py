from PySide6.QtWidgets import QWidget

class ConnectionView(QWidget):
    """Halaman untuk melakukan scan dan menyambungkan Bluetooth ESP"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Menampilkan daftar Bluetooth yang tersedia
