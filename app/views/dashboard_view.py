from PySide6.QtWidgets import QWidget

class DashboardView(QWidget):
    """Halaman utama tempat Psikolog memantau grafik sensor pasien secara live"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Rakit GraphWidget dan SensorCard di halaman ini
