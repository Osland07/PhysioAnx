from PySide6.QtWidgets import QWidget

class PatientView(QWidget):
    """Halaman untuk melihat daftar pasien dan menambah pasien baru"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Nanti berisi tabel daftar pasien dan tombol tambah
