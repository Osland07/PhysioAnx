from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QLineEdit, QComboBox, 
                               QTableWidget, QHeaderView)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta
from main_window import create_shadow # We can import this utility or move it later

class PatientView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # --- 1. HEADER (Judul & Tombol Registrasi) ---
        header_layout = QHBoxLayout()
        title = QLabel("Patients")
        title.setObjectName("HeaderTitle")
        
        self.btn_add = QPushButton(" Registrasi Pasien Baru")
        self.btn_add.setIcon(qta.icon('fa5s.user-plus', color='white'))
        self.btn_add.setIconSize(QSize(18, 18))
        self.btn_add.setObjectName("PrimaryButton")
        self.btn_add.setFixedSize(220, 45)
        self.btn_add.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)
        
        # --- 2. FILTER & SEARCH PANEL ---
        filter_panel = QFrame()
        filter_panel.setObjectName("GraphPanel")
        filter_panel.setGraphicsEffect(create_shadow())
        filter_layout = QHBoxLayout(filter_panel)
        filter_layout.setContentsMargins(20, 15, 20, 15)
        filter_layout.setSpacing(15)
        
        self.search_input_pasien = QLineEdit()
        self.search_input_pasien.setObjectName("SearchBar")
        self.search_input_pasien.setPlaceholderText("Cari No. RM atau Nama Pasien...")
        self.search_input_pasien.setMinimumWidth(300)
        
        self.cmb_gender_pasien = QComboBox()
        self.cmb_gender_pasien.addItems(["Semua Jenis Kelamin", "Laki-laki", "Perempuan"])
        self.cmb_gender_pasien.setFixedSize(210, 40)
        
        self.btn_filter = QPushButton(" Filter")
        self.btn_filter.setIcon(qta.icon('fa5s.filter', color='#2D3748'))
        self.btn_filter.setObjectName("SecondaryButton")
        self.btn_filter.setFixedSize(100, 40)
        self.btn_filter.setCursor(Qt.PointingHandCursor)
        
        filter_layout.addWidget(self.search_input_pasien)
        filter_layout.addWidget(self.cmb_gender_pasien)
        filter_layout.addWidget(self.btn_filter)
        filter_layout.addStretch()
        
        # --- 3. TABEL DATA PASIEN ---
        table_panel = QFrame()
        table_panel.setObjectName("GraphPanel")
        table_panel.setGraphicsEffect(create_shadow())
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.setSpacing(15)
        
        self.table_pasien = QTableWidget(0, 5)
        self.table_pasien.setHorizontalHeaderLabels([
            "No. RM", "Nama Pasien", "Umur", "Gender", "Aksi"
        ])
        
        header = self.table_pasien.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.table_pasien.setColumnWidth(0, 130)
        self.table_pasien.setColumnWidth(2, 80)
        self.table_pasien.setColumnWidth(3, 90)
        self.table_pasien.setColumnWidth(4, 260)
        
        self.table_pasien.verticalHeader().setVisible(False)
        self.table_pasien.verticalHeader().setDefaultSectionSize(55)
        self.table_pasien.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_pasien.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_pasien.setSelectionMode(QTableWidget.SingleSelection)
        self.table_pasien.setShowGrid(False)
        
        # --- 4. PAGINATION PANEL ---
        pagination_layout = QHBoxLayout()
        self.lbl_info = QLabel()
        self.lbl_info.setStyleSheet("color: #718096; font-size: 13px;")
        
        self.btn_prev = QPushButton(" Prev")
        self.btn_prev.setIcon(qta.icon('fa5s.chevron-left', color='#2D3748'))
        self.btn_prev.setObjectName("SecondaryButton")
        self.btn_prev.setFixedSize(80, 30)
        
        self.btn_next = QPushButton(" Next")
        self.btn_next.setIcon(qta.icon('fa5s.chevron-right', color='#2D3748'))
        self.btn_next.setLayoutDirection(Qt.RightToLeft)
        self.btn_next.setObjectName("SecondaryButton")
        self.btn_next.setFixedSize(80, 30)
        
        pagination_layout.addWidget(self.lbl_info)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.btn_prev)
        pagination_layout.addWidget(self.btn_next)
        
        table_layout.addWidget(self.table_pasien)
        table_layout.addLayout(pagination_layout)
        
        layout.addLayout(header_layout)
        layout.addWidget(filter_panel)
        layout.addWidget(table_panel, stretch=1)
