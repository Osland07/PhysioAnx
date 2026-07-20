import qtawesome as qta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QComboBox, QFrame, QScrollArea, QGridLayout,
    QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, QSize
from utils.helpers import create_shadow

class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #F7FAFC;")
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 28px; font-weight: 900; color: #002C6F;")
        
        desc = QLabel("Configure application preferences, user details, and device connections.")
        desc.setStyleSheet("font-size: 14px; color: #1E3F76;")
        
        header_vbox = QVBoxLayout()
        header_vbox.addWidget(title)
        header_vbox.addWidget(desc)
        header_layout.addLayout(header_vbox)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Scrollable Area for Settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(25)
        scroll_layout.setContentsMargins(0, 0, 20, 0)
        
        # --- 1. GENERAL SETTINGS ---
        gen_group = self._create_card_group("fa5s.user-md", "General Settings")
        gen_form = QFormLayout()
        gen_form.setVerticalSpacing(15)
        
        self.inp_doctor = QLineEdit()
        self.inp_doctor.setPlaceholderText("e.g. Dr. Jane Doe")
        self.inp_doctor.setText("Dr. Andi")
        self.inp_doctor.setMinimumHeight(40)
        self.inp_doctor.setStyleSheet("padding: 5px 15px; border: 1px solid #CBD5E0; border-radius: 6px; color: #002C6F; background: white;")
        
        self.cmb_language = QComboBox()
        self.cmb_language.addItems(["English", "Bahasa Indonesia"])
        self.cmb_language.setMinimumHeight(40)
        self.cmb_language.setStyleSheet("padding: 5px 15px; border: 1px solid #CBD5E0; border-radius: 6px; color: #002C6F; background: white;")
        
        self.cmb_theme = QComboBox()
        self.cmb_theme.addItems(["Light Mode", "Dark Mode"])
        self.cmb_theme.setMinimumHeight(40)
        self.cmb_theme.setStyleSheet("padding: 5px 15px; border: 1px solid #CBD5E0; border-radius: 6px; color: #002C6F; background: white;")
        
        lbl_style = "color: #1E3F76; font-weight: bold; font-size: 14px; padding-right: 20px;"
        lbl_doc = QLabel("Physician Name:")
        lbl_doc.setStyleSheet(lbl_style)
        lbl_lang = QLabel("Language:")
        lbl_lang.setStyleSheet(lbl_style)
        lbl_theme = QLabel("Appearance:")
        lbl_theme.setStyleSheet(lbl_style)
        
        gen_form.addRow(lbl_doc, self.inp_doctor)
        gen_form.addRow(lbl_lang, self.cmb_language)
        gen_form.addRow(lbl_theme, self.cmb_theme)
        
        gen_group.layout().addLayout(gen_form)
        scroll_layout.addWidget(gen_group)
        
        # --- 2. DEVICE CONNECTION SETTINGS ---
        dev_group = self._create_card_group("fa5s.bluetooth", "Device Configuration")
        dev_form = QFormLayout()
        dev_form.setVerticalSpacing(15)
        
        # Port Selection Row
        port_row = QHBoxLayout()
        self.cmb_port = QComboBox()
        self.cmb_port.addItems(["COM1", "COM3", "COM4", "COM5 (Bluetooth)"])
        self.cmb_port.setMinimumHeight(40)
        self.cmb_port.setStyleSheet("padding: 5px 15px; border: 1px solid #CBD5E0; border-radius: 6px; color: #002C6F; background: white;")
        
        self.btn_refresh = QPushButton()
        self.btn_refresh.setIcon(qta.icon('fa5s.sync-alt', color='#1E3F76'))
        self.btn_refresh.setFixedSize(40, 40)
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setStyleSheet("QPushButton { background-color: #EDF2F7; border-radius: 6px; border: 1px solid #CBD5E0; } QPushButton:hover { background-color: #E2E8F0; }")
        
        port_row.addWidget(self.cmb_port, stretch=1)
        port_row.addWidget(self.btn_refresh)
        
        self.cmb_baud = QComboBox()
        self.cmb_baud.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.cmb_baud.setCurrentText("115200")
        self.cmb_baud.setMinimumHeight(40)
        self.cmb_baud.setStyleSheet("padding: 5px 15px; border: 1px solid #CBD5E0; border-radius: 6px; color: #002C6F; background: white;")
        
        lbl_port = QLabel("Serial Port:")
        lbl_port.setStyleSheet(lbl_style)
        lbl_baud = QLabel("Baud Rate:")
        lbl_baud.setStyleSheet(lbl_style)
        
        dev_form.addRow(lbl_port, port_row)
        dev_form.addRow(lbl_baud, self.cmb_baud)
        
        dev_group.layout().addLayout(dev_form)
        scroll_layout.addWidget(dev_group)
        
        # --- 3. DATA MANAGEMENT ---
        data_group = self._create_card_group("fa5s.database", "Data Management")
        data_layout = QHBoxLayout()
        
        self.btn_backup = QPushButton(" Backup Database")
        self.btn_backup.setIcon(qta.icon('fa5s.save', color='white'))
        self.btn_backup.setFixedHeight(45)
        self.btn_backup.setCursor(Qt.PointingHandCursor)
        self.btn_backup.setStyleSheet("QPushButton { background-color: #5C9EDA; color: white; font-weight: bold; font-size: 14px; border-radius: 6px; border: none; padding: 0 20px;} QPushButton:hover { background-color: #4F97D1; }")
        
        self.btn_export = QPushButton(" Export All Records (CSV)")
        self.btn_export.setIcon(qta.icon('fa5s.file-export', color='white'))
        self.btn_export.setFixedHeight(45)
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.setStyleSheet("QPushButton { background-color: #48BB78; color: white; font-weight: bold; font-size: 14px; border-radius: 6px; border: none; padding: 0 20px;} QPushButton:hover { background-color: #38A169; }")
        
        data_layout.addWidget(self.btn_backup)
        data_layout.addWidget(self.btn_export)
        data_layout.addStretch()
        
        data_group.layout().addLayout(data_layout)
        scroll_layout.addWidget(data_group)
        
        # Bottom Save Action
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        self.btn_save = QPushButton(" Save Settings")
        self.btn_save.setIcon(qta.icon('fa5s.check', color='white'))
        self.btn_save.setFixedHeight(50)
        self.btn_save.setMinimumWidth(200)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.setStyleSheet("QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F97D1, stop:1 #5C9EDA); color: white; font-weight: bold; font-size: 16px; border-radius: 8px; border: none; padding: 0 30px;} QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5C9EDA, stop:1 #75B0E1); }")
        
        scroll_layout.addStretch()
        scroll_layout.addLayout(save_layout)
        scroll_layout.addWidget(self.btn_save, alignment=Qt.AlignRight)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def _create_card_group(self, icon_name, title_text):
        card = QFrame()
        card.setGraphicsEffect(create_shadow())
        card.setStyleSheet("QFrame { background-color: white; border-radius: 12px; border: 1px solid #E2E8F0; }")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header of card
        header = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(qta.icon(icon_name, color='#5C9EDA').pixmap(24, 24))
        icon.setStyleSheet("background: transparent; border: none;")
        
        title = QLabel(title_text)
        title.setStyleSheet("color: #002C6F; font-size: 18px; font-weight: 800; background: transparent; border: none;")
        
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        
        layout.addLayout(header)
        
        # Add a subtle separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #EDF2F7; border: none; min-height: 1px; max-height: 1px;")
        layout.addWidget(line)
        
        return card
