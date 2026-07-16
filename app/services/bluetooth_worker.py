from PySide6.QtCore import QThread, Signal

class BluetoothWorker(QThread):
    """
    Berjalan di latar belakang agar UI tidak freeze.
    Bertugas menerima data dari ESP menggunakan library Bleak secara terus menerus.
    """
    # Sinyal ini akan 'ditembakkan' ke UI setiap kali data baru masuk
    data_received = Signal(str)

    def run(self):
        # Proses Asyncio Bleak berjalan di sini
        pass
