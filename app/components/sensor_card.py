from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

class SensorCard(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setObjectName("SensorCard")
