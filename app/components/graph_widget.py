from PySide6.QtWidgets import QWidget

class GraphWidget(QWidget):
    """Komponen untuk membungkus PyQtGraph agar mudah dipanggil di halaman mana saja"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Setup PyQtGraph akan dilakukan di sini
