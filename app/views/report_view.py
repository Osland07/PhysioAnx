from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QLineEdit, QComboBox, 
                               QTableWidget, QHeaderView, QTableWidgetItem)
from PySide6.QtCore import Qt, QSize
import qtawesome as qta
from main_window import create_shadow

class ReportView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # --- 1. HEADER PANEL ---
        header_layout = QHBoxLayout()
        title = QLabel("Riwayat Sesi Pemeriksaan")
        title.setObjectName("HeaderTitle")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # --- 2. FILTER & SEARCH PANEL ---
        filter_panel = QFrame()
        filter_panel.setObjectName("GraphPanel")
        filter_panel.setGraphicsEffect(create_shadow())
        filter_layout = QHBoxLayout(filter_panel)
        filter_layout.setContentsMargins(20, 15, 20, 15)
        filter_layout.setSpacing(15)
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchBar")
        self.search_input.setPlaceholderText("Cari No. RM atau Nama Pasien...")
        self.search_input.setMinimumWidth(300)
        
        self.cmb_anxiety = QComboBox()
        self.cmb_anxiety.addItems(["Semua Tingkat Kecemasan", "Rendah", "Sedang", "Tinggi"])
        self.cmb_anxiety.setFixedSize(220, 40)
        
        self.btn_filter = QPushButton(" Filter")
        self.btn_filter.setIcon(qta.icon('fa5s.filter', color='white'))
        self.btn_filter.setObjectName("SecondaryButton")
        self.btn_filter.setFixedSize(100, 40)
        self.btn_filter.setCursor(Qt.PointingHandCursor)
        
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.cmb_anxiety)
        filter_layout.addWidget(self.btn_filter)
        filter_layout.addStretch()
        
        # --- 3. TABEL RIWAYAT SESI ---
        table_panel = QFrame()
        table_panel.setObjectName("GraphPanel")
        table_panel.setGraphicsEffect(create_shadow())
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.setSpacing(15)
        
        self.table_sesi = QTableWidget(0, 5)
        self.table_sesi.setHorizontalHeaderLabels([
            "Tanggal Sesi", "No. RM - Nama Pasien", "Durasi", "Indikasi", "Aksi"
        ])
        
        header = self.table_sesi.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.table_sesi.setColumnWidth(0, 150)
        self.table_sesi.setColumnWidth(2, 100)
        self.table_sesi.setColumnWidth(3, 150)
        self.table_sesi.setColumnWidth(4, 180)
        
        self.table_sesi.verticalHeader().setVisible(False)
        self.table_sesi.verticalHeader().setDefaultSectionSize(55)
        self.table_sesi.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_sesi.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_sesi.setSelectionMode(QTableWidget.SingleSelection)
        self.table_sesi.setShowGrid(False)
        
        # --- 4. PAGINATION PANEL ---
        pagination_layout = QHBoxLayout()
        self.lbl_info = QLabel("Menampilkan data riwayat sesi")
        self.lbl_info.setStyleSheet("color: #8C9EBA; font-size: 13px;")
        
        self.btn_prev = QPushButton(" Prev")
        self.btn_prev.setIcon(qta.icon('fa5s.chevron-left', color='white'))
        self.btn_prev.setObjectName("SecondaryButton")
        self.btn_prev.setFixedSize(80, 30)
        
        self.btn_next = QPushButton(" Next")
        self.btn_next.setIcon(qta.icon('fa5s.chevron-right', color='white'))
        self.btn_next.setLayoutDirection(Qt.RightToLeft)
        self.btn_next.setObjectName("SecondaryButton")
        self.btn_next.setFixedSize(80, 30)
        
        pagination_layout.addWidget(self.lbl_info)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.btn_prev)
        pagination_layout.addWidget(self.btn_next)
        
        table_layout.addWidget(self.table_sesi)
        table_layout.addLayout(pagination_layout)
        
        layout.addLayout(header_layout)
        layout.addWidget(filter_panel)
        layout.addWidget(table_panel, stretch=1)
