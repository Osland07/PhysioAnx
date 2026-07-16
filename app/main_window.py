import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                               QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect, QStackedWidget, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem)
from PySide6.QtCore import Qt, QTimer, QTime, QSize
from PySide6.QtGui import QColor, QIcon
import pyqtgraph as pg
import qtawesome as qta
from models.database import init_db, SessionLocal
from models.patient import Patient
from datetime import date

def create_shadow():
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(25)
    shadow.setXOffset(0)
    shadow.setYOffset(8)
    shadow.setColor(QColor(0, 0, 0, 90))
    return shadow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        init_db()
        self.setWindowTitle("PhysioAnx - Secure Medical Dashboard")
        self.setMinimumSize(1200, 750)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ==========================================
        # 1. SIDEBAR KIRI
        # ==========================================
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(260)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 40, 0, 30) 
        sidebar_layout.setSpacing(5)
        
        title = QLabel("PHYSIOANX")
        title.setObjectName("AppTitle")
        title.setAlignment(Qt.AlignCenter)
        
        self.btn_pasien = QPushButton(" Data Pasien")
        self.btn_pasien.setIcon(qta.icon('fa5s.users', color='#8C9EBA'))
        self.btn_pasien.setIconSize(QSize(20, 20))
        
        self.btn_session = QPushButton(" Sesi Pemeriksaan")
        self.btn_session.setIcon(qta.icon('fa5s.heartbeat', color='#8C9EBA'))
        self.btn_session.setIconSize(QSize(20, 20))
        
        self.btn_report = QPushButton(" Riwayat Sesi")
        self.btn_report.setIcon(qta.icon('fa5s.file-medical-alt', color='#8C9EBA'))
        self.btn_report.setIconSize(QSize(20, 20))
        
        self.btn_setting = QPushButton(" Pengaturan")
        self.btn_setting.setIcon(qta.icon('fa5s.cog', color='#8C9EBA'))
        self.btn_setting.setIconSize(QSize(20, 20))
        
        self.btn_pasien.clicked.connect(lambda: self.switch_page(0))
        self.btn_session.clicked.connect(lambda: self.switch_page(1))
        self.btn_report.clicked.connect(lambda: self.switch_page(2))
        self.btn_setting.clicked.connect(lambda: self.switch_page(3))
        
        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(50)
        sidebar_layout.addWidget(self.btn_pasien)
        sidebar_layout.addWidget(self.btn_session)
        sidebar_layout.addWidget(self.btn_report)
        sidebar_layout.addWidget(self.btn_setting)
        sidebar_layout.addStretch()
        
        footer_label = QLabel("PhysioAnx v1.0")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet("color: #475569; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        sidebar_layout.addWidget(footer_label)
        
        # ==========================================
        # 2. KONTEN UTAMA (KANAN)
        # ==========================================
        content_area = QWidget()
        content_area.setObjectName("ContentArea")
        self.content_layout = QVBoxLayout(content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        self.top_bar = QFrame()
        self.top_bar.setObjectName("TopBar")
        self.top_bar.setFixedHeight(80)
        top_bar_layout = QHBoxLayout(self.top_bar)
        top_bar_layout.setContentsMargins(40, 0, 40, 0)
        
        self.greeting_label = QLabel()
        self.greeting_label.setObjectName("TopBarGreeting")
        
        self.clock_label = QLabel()
        self.clock_label.setObjectName("TopBarClock")
        
        top_bar_layout.addWidget(self.greeting_label)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.clock_label)
        
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setContentsMargins(40, 30, 40, 40)
        
        self.page_pasien = QWidget()
        self.setup_pasien_page()
        
        self.page_live_session = QWidget()
        self.setup_live_session_page()
        
        self.page_report = QWidget()
        self.setup_report_page()
        
        self.page_setting = QWidget()
        self.setup_setting_page()
        
        self.stacked_widget.addWidget(self.page_pasien)       # 0
        self.stacked_widget.addWidget(self.page_live_session) # 1
        self.stacked_widget.addWidget(self.page_report)       # 2
        self.stacked_widget.addWidget(self.page_setting)      # 3
        
        self.content_layout.addWidget(self.top_bar)
        self.content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_area)
        
        self.update_time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        # Default ke Data Pasien
        self.switch_page(0)


    def update_time(self):
        current_time = QTime.currentTime()
        jam = current_time.hour()
        if 5 <= jam < 11: sapaan = "Selamat Pagi!"
        elif 11 <= jam < 15: sapaan = "Selamat Siang!"
        elif 15 <= jam < 18: sapaan = "Selamat Sore!"
        else: sapaan = "Selamat Malam!"
        self.greeting_label.setText(f"{sapaan}")
        self.clock_label.setText(current_time.toString("HH:mm:ss"))

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        # Tampilkan sidebar dan topbar
        self.sidebar.show()
        self.top_bar.show()
        
        buttons = [self.btn_pasien, self.btn_session, self.btn_report, self.btn_setting]
        for btn in buttons:
            btn.setObjectName("MenuButton")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
        if 0 <= index < 4:
            buttons[index].setObjectName("MenuButtonActive")
            buttons[index].style().unpolish(buttons[index])
            buttons[index].style().polish(buttons[index])

    def setup_pasien_page(self):
        from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QSpacerItem, QSizePolicy

        layout = QVBoxLayout(self.page_pasien)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # --- 1. HEADER (Judul & Tombol Registrasi) ---
        header_layout = QHBoxLayout()
        title = QLabel("Data Pasien (Rekam Medis)")
        title.setObjectName("HeaderTitle")
        
        btn_add = QPushButton(" Registrasi Pasien Baru")
        btn_add.setIcon(qta.icon('fa5s.user-plus', color='#1A1A1A'))
        btn_add.setIconSize(QSize(18, 18))
        btn_add.setObjectName("PrimaryButton")
        btn_add.setFixedSize(220, 45)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self.show_add_patient_dialog)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(btn_add)
        
        # --- 2. FILTER & SEARCH PANEL ---
        filter_panel = QFrame()
        filter_panel.setObjectName("GraphPanel")
        filter_panel.setGraphicsEffect(create_shadow())
        filter_layout = QHBoxLayout(filter_panel)
        filter_layout.setContentsMargins(20, 15, 20, 15)
        filter_layout.setSpacing(15)
        
        search_input = QLineEdit()
        search_input.setObjectName("SearchBar")
        search_input.setPlaceholderText("Cari No. RM, NIK, atau Nama Pasien...")
        search_input.setMinimumWidth(300)
        
        cmb_gender = QComboBox()
        cmb_gender.addItems(["Semua Jenis Kelamin", "Laki-laki", "Perempuan"])
        cmb_gender.setFixedSize(210, 40)
        
        btn_filter = QPushButton(" Filter")
        btn_filter.setIcon(qta.icon('fa5s.filter', color='white'))
        btn_filter.setObjectName("SecondaryButton")
        btn_filter.setFixedSize(100, 40)
        btn_filter.setCursor(Qt.PointingHandCursor)
        
        filter_layout.addWidget(search_input)
        filter_layout.addWidget(cmb_gender)
        filter_layout.addWidget(btn_filter)
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
            "No. RM", "Nama Pasien", "Umur", "L/P", "Aksi"
        ])
        
        # Konfigurasi Header Tabel
        header = self.table_pasien.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive) # Agar kolom tidak otomatis terlalu kecil
        header.setSectionResizeMode(1, QHeaderView.Stretch) # Kolom Nama memanjang
        
        self.table_pasien.setColumnWidth(0, 130) # No RM
        self.table_pasien.setColumnWidth(2, 80)  # Umur
        self.table_pasien.setColumnWidth(3, 50)  # L/P
        self.table_pasien.setColumnWidth(4, 200) # Aksi (Edit, Hapus)
        
        self.table_pasien.verticalHeader().setVisible(False)
        self.table_pasien.verticalHeader().setDefaultSectionSize(55) # Tambah tinggi baris agar tombol tidak terpotong
        self.table_pasien.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_pasien.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_pasien.setSelectionMode(QTableWidget.SingleSelection)
        self.table_pasien.setShowGrid(False)
        
        # --- 4. PAGINATION PANEL ---
        pagination_layout = QHBoxLayout()
        self.lbl_info = QLabel()
        self.lbl_info.setStyleSheet("color: #8C9EBA; font-size: 13px;")
        
        # Memuat data dari database
        self.load_patients_to_table()
        
        btn_prev = QPushButton(" Prev")
        btn_prev.setIcon(qta.icon('fa5s.chevron-left', color='white'))
        btn_prev.setObjectName("SecondaryButton")
        btn_prev.setFixedSize(80, 30)
        
        btn_next = QPushButton(" Next")
        btn_next.setIcon(qta.icon('fa5s.chevron-right', color='white'))
        btn_next.setLayoutDirection(Qt.RightToLeft)
        btn_next.setObjectName("SecondaryButton")
        btn_next.setFixedSize(80, 30)
        
        pagination_layout.addWidget(self.lbl_info)
        pagination_layout.addStretch()
        pagination_layout.addWidget(btn_prev)
        pagination_layout.addWidget(btn_next)
        
        # Compile Table Panel
        table_layout.addWidget(self.table_pasien)
        table_layout.addLayout(pagination_layout)
        
        # Compile All
        layout.addLayout(header_layout)
        layout.addWidget(filter_panel)
        layout.addWidget(table_panel, stretch=1)

    def load_patients_to_table(self):
        session = SessionLocal()
        patients = session.query(Patient).all()
        
        self.table_pasien.setRowCount(len(patients))
        for row, p in enumerate(patients):
            self.table_pasien.setItem(row, 0, QTableWidgetItem(p.no_rm))
            self.table_pasien.setItem(row, 1, QTableWidgetItem(p.full_name))
            
            # Hitung umur
            umur = ""
            if p.date_of_birth:
                today = date.today()
                age = today.year - p.date_of_birth.year - ((today.month, today.day) < (p.date_of_birth.month, p.date_of_birth.day))
                umur = f"{age} Thn"
            
            item_umur = QTableWidgetItem(umur)
            item_umur.setTextAlignment(Qt.AlignCenter)
            self.table_pasien.setItem(row, 2, item_umur)
            
            item_jk = QTableWidgetItem(p.gender)
            item_jk.setTextAlignment(Qt.AlignCenter)
            self.table_pasien.setItem(row, 3, item_jk)
            
            # Kolom Aksi
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(8)
            
            btn_edit = QPushButton(" Edit")
            btn_edit.setIcon(qta.icon('fa5s.edit', color='white'))
            btn_edit.setStyleSheet("background-color: #FFA000; color: white; border: none; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda checked, pat=p: self.show_edit_patient_dialog(pat))
            
            btn_delete = QPushButton(" Hapus")
            btn_delete.setIcon(qta.icon('fa5s.trash-alt', color='white'))
            btn_delete.setStyleSheet("background-color: #D32F2F; color: white; border: none; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
            btn_delete.setCursor(Qt.PointingHandCursor)
            btn_delete.clicked.connect(lambda checked, rm=p.no_rm, n=p.full_name: self.delete_patient_action(rm, n))
            
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)
            action_layout.addStretch()
            self.table_pasien.setCellWidget(row, 4, action_widget)
            
        self.lbl_info.setText(f"Menampilkan 1 hingga {len(patients)} dari {len(patients)} entri")
        session.close()

    def show_add_patient_dialog(self):
        from components.patient_dialog import PatientDialog
        dialog = PatientDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            session = SessionLocal()
            new_p = Patient(
                no_rm=data["no_rm"],
                full_name=data["full_name"],
                date_of_birth=data["date_of_birth"],
                gender=data["gender"],
                height=data["height"],
                weight=data["weight"]
            )
            session.add(new_p)
            session.commit()
            session.close()
            self.load_patients_to_table()

    def show_edit_patient_dialog(self, patient_obj):
        from components.patient_dialog import PatientDialog
        dialog = PatientDialog(self, patient_data=patient_obj)
        if dialog.exec():
            data = dialog.get_data()
            session = SessionLocal()
            p = session.query(Patient).filter(Patient.no_rm == patient_obj.no_rm).first()
            if p:
                p.full_name = data["full_name"]
                p.date_of_birth = data["date_of_birth"]
                p.gender = data["gender"]
                p.height = data["height"]
                p.weight = data["weight"]
                session.commit()
            session.close()
            self.load_patients_to_table()

    def delete_patient_action(self, rm_id, patient_name):
        from PySide6.QtWidgets import QMessageBox
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Konfirmasi Hapus")
        msg_box.setText(f"Apakah Anda yakin ingin menghapus data pasien '{patient_name}'?")
        msg_box.setInformativeText("Data yang dihapus tidak dapat dikembalikan.")
        msg_box.setIcon(QMessageBox.Warning)
        
        btn_yes = msg_box.addButton("Ya, Hapus", QMessageBox.DestructiveRole)
        btn_no = msg_box.addButton("Batal", QMessageBox.RejectRole)
        msg_box.setDefaultButton(btn_no)
        
        # Styling agar mirip dengan tema aplikasi
        msg_box.setStyleSheet("""
            QMessageBox { background-color: #081B3B; }
            QLabel { color: #FFFFFF; font-size: 14px; }
            QPushButton { background-color: #112A54; color: white; padding: 6px 15px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #1A3A70; }
        """)
        btn_yes.setStyleSheet("background-color: #D32F2F; color: white; padding: 6px 15px; border-radius: 4px; font-weight: bold;")
        
        msg_box.exec()
        
        if msg_box.clickedButton() == btn_yes:
            session = SessionLocal()
            p = session.query(Patient).filter(Patient.no_rm == rm_id).first()
            if p:
                session.delete(p)
                session.commit()
            session.close()
            self.load_patients_to_table()

    # ==========================================
    # HALAMAN 3: RIWAYAT SESI
    # ==========================================
    def setup_report_page(self):
        layout = QVBoxLayout(self.page_report)
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
        
        search_input = QLineEdit()
        search_input.setObjectName("SearchBar")
        search_input.setPlaceholderText("Cari No. RM atau Nama Pasien...")
        search_input.setMinimumWidth(300)
        
        cmb_anxiety = QComboBox()
        cmb_anxiety.addItems(["Semua Tingkat Kecemasan", "Rendah", "Sedang", "Tinggi"])
        cmb_anxiety.setFixedSize(220, 40)
        
        btn_filter = QPushButton(" Filter")
        btn_filter.setIcon(qta.icon('fa5s.filter', color='white'))
        btn_filter.setObjectName("SecondaryButton")
        btn_filter.setFixedSize(100, 40)
        btn_filter.setCursor(Qt.PointingHandCursor)
        
        filter_layout.addWidget(search_input)
        filter_layout.addWidget(cmb_anxiety)
        filter_layout.addWidget(btn_filter)
        filter_layout.addStretch()
        
        # --- 3. TABEL RIWAYAT SESI ---
        table_panel = QFrame()
        table_panel.setObjectName("GraphPanel")
        table_panel.setGraphicsEffect(create_shadow())
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.setSpacing(15)
        
        self.table_sesi = QTableWidget(0, 6)
        self.table_sesi.setHorizontalHeaderLabels([
            "Tanggal Sesi", "No. RM - Nama Pasien", "Durasi", "Avg HR", "Indikasi", "Aksi"
        ])
        
        # Konfigurasi Header Tabel
        from PySide6.QtWidgets import QHeaderView
        header = self.table_sesi.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch) # Kolom Nama memanjang
        
        self.table_sesi.setColumnWidth(0, 150) # Tanggal
        self.table_sesi.setColumnWidth(2, 100) # Durasi
        self.table_sesi.setColumnWidth(3, 100) # HR
        self.table_sesi.setColumnWidth(4, 150) # Indikasi
        self.table_sesi.setColumnWidth(5, 180) # Aksi
        
        self.table_sesi.verticalHeader().setVisible(False)
        self.table_sesi.verticalHeader().setDefaultSectionSize(55)
        self.table_sesi.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_sesi.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_sesi.setSelectionMode(QTableWidget.SingleSelection)
        self.table_sesi.setShowGrid(False)
        
        # Dummy Data untuk Tampilan Sesi
        dummy_sesi = [
            ("25 Jun 2026", "RM-2406-001 - Bpk. Budi", "15 Menit", "85 bpm", "Tinggi"),
            ("24 Jun 2026", "RM-2406-002 - Ibu Siti", "20 Menit", "72 bpm", "Sedang"),
            ("20 Jun 2026", "RM-2406-003 - Sdr. Andi", "10 Menit", "65 bpm", "Rendah")
        ]
        
        self.table_sesi.setRowCount(len(dummy_sesi))
        for row, data in enumerate(dummy_sesi):
            self.table_sesi.setItem(row, 0, QTableWidgetItem(data[0]))
            self.table_sesi.setItem(row, 1, QTableWidgetItem(data[1]))
            
            item_durasi = QTableWidgetItem(data[2])
            item_durasi.setTextAlignment(Qt.AlignCenter)
            self.table_sesi.setItem(row, 2, item_durasi)
            
            item_hr = QTableWidgetItem(data[3])
            item_hr.setTextAlignment(Qt.AlignCenter)
            self.table_sesi.setItem(row, 3, item_hr)
            
            # Badge Indikasi Kecemasan
            lbl_indikasi = QLabel(data[4])
            lbl_indikasi.setAlignment(Qt.AlignCenter)
            if data[4] == "Tinggi":
                lbl_indikasi.setStyleSheet("background-color: #D32F2F; color: #FFF; padding: 4px; border-radius: 4px; font-weight: bold;")
            elif data[4] == "Sedang":
                lbl_indikasi.setStyleSheet("background-color: #F57F17; color: #FFF; padding: 4px; border-radius: 4px; font-weight: bold;")
            else:
                lbl_indikasi.setStyleSheet("background-color: #1B5E20; color: #FFF; padding: 4px; border-radius: 4px; font-weight: bold;")
                
            ind_widget = QWidget()
            ind_layout = QHBoxLayout(ind_widget)
            ind_layout.setContentsMargins(5, 5, 5, 5)
            ind_layout.addWidget(lbl_indikasi)
            self.table_sesi.setCellWidget(row, 4, ind_widget)
            
            # Kolom Aksi
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(8)
            
            btn_detail = QPushButton(" Detail")
            btn_detail.setIcon(qta.icon('fa5s.chart-area', color='white'))
            btn_detail.setStyleSheet("background-color: #1976D2; color: white; border: none; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
            btn_detail.setCursor(Qt.PointingHandCursor)
            
            btn_pdf = QPushButton(" PDF")
            btn_pdf.setIcon(qta.icon('fa5s.file-pdf', color='white'))
            btn_pdf.setStyleSheet("background-color: #388E3C; color: white; border: none; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
            btn_pdf.setCursor(Qt.PointingHandCursor)
            
            action_layout.addWidget(btn_detail)
            action_layout.addWidget(btn_pdf)
            action_layout.addStretch()
            self.table_sesi.setCellWidget(row, 5, action_widget)
            
        # --- 4. PAGINATION PANEL ---
        pagination_layout = QHBoxLayout()
        lbl_info = QLabel(f"Menampilkan 1 hingga {len(dummy_sesi)} dari {len(dummy_sesi)} riwayat sesi")
        lbl_info.setStyleSheet("color: #8C9EBA; font-size: 13px;")
        
        btn_prev = QPushButton(" Prev")
        btn_prev.setIcon(qta.icon('fa5s.chevron-left', color='white'))
        btn_prev.setObjectName("SecondaryButton")
        btn_prev.setFixedSize(80, 30)
        
        btn_next = QPushButton(" Next")
        btn_next.setIcon(qta.icon('fa5s.chevron-right', color='white'))
        btn_next.setLayoutDirection(Qt.RightToLeft)
        btn_next.setObjectName("SecondaryButton")
        btn_next.setFixedSize(80, 30)
        
        pagination_layout.addWidget(lbl_info)
        pagination_layout.addStretch()
        pagination_layout.addWidget(btn_prev)
        pagination_layout.addWidget(btn_next)
        
        # Compile Table Panel
        table_layout.addWidget(self.table_sesi)
        table_layout.addLayout(pagination_layout)
        
        # Compile All
        layout.addLayout(header_layout)
        layout.addWidget(filter_panel)
        layout.addWidget(table_panel, stretch=1)

    # ==========================================
    # HALAMAN 5: RUANG SESI LIVE GRAPH
    # ==========================================
    def setup_live_session_page(self):
        layout = QVBoxLayout(self.page_live_session)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        # --- 1. PANEL PERSIAPAN (Atas) ---
        prep_panel = QFrame()
        prep_panel.setGraphicsEffect(create_shadow())
        prep_panel.setStyleSheet("background-color: #081B3B; border-radius: 8px; border: 1px solid #112A54;")
        prep_layout = QHBoxLayout(prep_panel)
        prep_layout.setContentsMargins(20, 15, 20, 15)
        prep_layout.setSpacing(15)
        
        lbl_pilih = QLabel("Pilih Pasien:")
        lbl_pilih.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 14px; border: none;")
        
        cmb_pasien = QComboBox()
        cmb_pasien.addItem("RM-2406-001 - Bpk. Budi Santoso")
        cmb_pasien.addItem("RM-2406-002 - Ibu Siti Aminah")
        cmb_pasien.addItem("RM-2406-003 - Sdr. Andi Pratama")
        cmb_pasien.setMinimumWidth(300)
        cmb_pasien.setFixedHeight(40)
        
        lbl_bluetooth = QLabel("⚫ Alat Disconnected")
        lbl_bluetooth.setStyleSheet("color: #FF5252; font-weight: bold; font-size: 14px; border: none; margin-left: 20px;")
        
        btn_connect = QPushButton(" Hubungkan Alat")
        btn_connect.setIcon(qta.icon('fa5b.bluetooth', color='white'))
        btn_connect.setObjectName("SecondaryButton")
        btn_connect.setFixedSize(160, 40)
        btn_connect.setCursor(Qt.PointingHandCursor)
        
        prep_layout.addWidget(lbl_pilih)
        prep_layout.addWidget(cmb_pasien)
        prep_layout.addWidget(lbl_bluetooth)
        prep_layout.addWidget(btn_connect)
        prep_layout.addStretch()
        
        # --- 2. KONTROL SESI & INDIKATOR VITAL ---
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        
        # Tombol Mulai/Selesai
        action_panel = QVBoxLayout()
        btn_start = QPushButton("  MULAI REKAM SESI")
        btn_start.setIcon(qta.icon('fa5s.play', color='white'))
        btn_start.setStyleSheet("""
            QPushButton { background-color: #00E676; color: #081B3B; font-weight: 900; font-size: 15px; border-radius: 8px; border: none; }
            QPushButton:hover { background-color: #69F0AE; }
        """)
        btn_start.setFixedSize(250, 50)
        btn_start.setCursor(Qt.PointingHandCursor)
        
        btn_stop = QPushButton("  SELESAIKAN SESI")
        btn_stop.setIcon(qta.icon('fa5s.stop', color='white'))
        btn_stop.setStyleSheet("background-color: #D32F2F; color: white; font-weight: bold; font-size: 14px; border-radius: 8px;")
        btn_stop.setFixedSize(250, 50)
        btn_stop.setCursor(Qt.PointingHandCursor)
        btn_stop.setEnabled(False) # Dimatikan sampai sesi mulai
        
        action_panel.addWidget(btn_start)
        action_panel.addWidget(btn_stop)
        action_panel.addStretch()
        
        # Indikator Vital
        card_hr = self.create_sensor_card("HEART RATE (BPM)", "82", "BPM", "#FF5252", "fa5s.heartbeat")
        card_gsr = self.create_sensor_card("GSR (µS)", "14.2", "µS", "#40C4FF", "fa5s.bolt")
        card_status = self.create_sensor_card("STATUS KECEMASAN", "-", "-", "#69F0AE", "fa5s.smile")
        
        control_layout.addLayout(action_panel)
        control_layout.addWidget(card_hr)
        control_layout.addWidget(card_gsr)
        control_layout.addWidget(card_status)
        
        # --- 3. GRAFIK REAL-TIME ---
        graph_panel = QFrame()
        graph_panel.setObjectName("GraphPanel")
        graph_panel.setGraphicsEffect(create_shadow())
        graph_panel.setStyleSheet("background-color: #081B3B; border-radius: 8px; border: 1px solid #112A54;")
        gl = QVBoxLayout(graph_panel)
        gl.setContentsMargins(20, 20, 20, 20)
        
        gl_title = QLabel("Data Pasien")
        gl_title.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 16px; border: none;")
        
        pg.setConfigOption('background', 'transparent')
        pg.setConfigOption('foreground', '#64748B')
        self.plot = pg.PlotWidget()
        self.plot.getAxis('left').setPen('#64748B')
        self.plot.getAxis('bottom').setPen('#64748B')
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        
        # Fake ECG/GSR Data for UI Showcase
        import numpy as np
        self.x_data = np.linspace(0, 10, 300)
        self.phase = 0.0
        self.y_data_hr = np.sin(self.x_data * 5 + self.phase) * 10 + 80 + np.random.normal(0, 1, 300)
        self.y_data_gsr = np.sin(self.x_data + self.phase) * 5 + 15 + np.random.normal(0, 0.2, 300)
        
        pen_hr = pg.mkPen(color='#FF5252', width=3)
        pen_gsr = pg.mkPen(color='#40C4FF', width=3)
        
        self.curve_hr = self.plot.plot(self.x_data, self.y_data_hr, pen=pen_hr, name="Heart Rate")
        self.curve_gsr = self.plot.plot(self.x_data, self.y_data_gsr, pen=pen_gsr, name="GSR")
        
        self.timer_graph = QTimer(self)
        self.timer_graph.timeout.connect(self.update_fake_graph)
        self.timer_graph.start(50)
        
        gl.addWidget(gl_title)
        gl.addWidget(self.plot)
        
        # Rangkai Semua
        layout.addWidget(prep_panel)
        layout.addLayout(control_layout)
        layout.addWidget(graph_panel, stretch=1)

    def update_fake_graph(self):
        import numpy as np
        self.phase += 0.2
        # Geser gelombang agar beranimasi
        self.y_data_hr[:-1] = self.y_data_hr[1:]
        self.y_data_hr[-1] = np.sin(self.x_data[-1] * 5 + self.phase) * 10 + 80 + np.random.normal(0, 1)
        
        self.y_data_gsr[:-1] = self.y_data_gsr[1:]
        self.y_data_gsr[-1] = np.sin(self.x_data[-1] + self.phase) * 5 + 15 + np.random.normal(0, 0.2)
        
        self.curve_hr.setData(self.x_data, self.y_data_hr)
        self.curve_gsr.setData(self.x_data, self.y_data_gsr)

    def create_sensor_card(self, title_text, value_text, unit_text, color, icon_name=None):
        card = QFrame()
        card.setGraphicsEffect(create_shadow())
        card.setFixedHeight(120)
        card.setStyleSheet("background-color: #081B3B; border-radius: 8px; border: 1px solid #112A54;")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        # Title Row with Icon
        top_layout = QHBoxLayout()
        title = QLabel(title_text)
        title.setStyleSheet("color: #8C9EBA; font-size: 13px; font-weight: 800; border: none; letter-spacing: 1px;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        if icon_name:
            icon_lbl = QLabel()
            icon_lbl.setPixmap(qta.icon(icon_name, color=color).pixmap(20, 20))
            icon_lbl.setStyleSheet("border: none;")
            top_layout.addWidget(icon_lbl)
            
        # Value & Unit Row
        v_lay = QHBoxLayout()
        val = QLabel(value_text)
        val.setStyleSheet(f"color: {color}; font-size: 42px; font-weight: 900; border: none;")
        
        unit = QLabel(unit_text)
        unit.setStyleSheet("color: #64748B; font-size: 14px; border: none; font-weight: bold; margin-bottom: 8px;")
        
        v_lay.addWidget(val)
        v_lay.addWidget(unit)
        v_lay.addStretch()
        v_lay.setAlignment(Qt.AlignBottom)
        layout.addWidget(title)
        layout.addLayout(v_lay)
        return card

    def setup_setting_page(self):
        from PySide6.QtWidgets import QFormLayout, QGroupBox, QFileDialog, QScrollArea, QMessageBox
        
        layout = QVBoxLayout(self.page_setting)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        header_label = QLabel("Pengaturan Sistem")
        header_label.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        layout.addWidget(header_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; } QScrollBar:vertical { width: 10px; background: #051024; } QScrollBar::handle:vertical { background: #112A54; border-radius: 5px; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(30)
        scroll_layout.setContentsMargins(0, 0, 20, 0)
        
        # 1. KONEKSI BLUETOOTH
        group_dev = QGroupBox(" Koneksi Bluetooth (ESP32)")
        group_dev.setStyleSheet("QGroupBox { color: #69F0AE; font-size: 16px; font-weight: bold; border: 1px solid #112A54; border-radius: 8px; margin-top: 15px; padding-top: 25px; background-color: #081B3B; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 10px; } QLabel { color: #B0BEC5; font-size: 14px; } QLineEdit { background-color: #051024; color: white; border: 1px solid #112A54; border-radius: 4px; padding: 10px; }")
        
        form_dev = QFormLayout(group_dev)
        form_dev.setContentsMargins(25, 25, 25, 25)
        form_dev.setSpacing(15)
        
        self.input_dev_name = QLineEdit("PhysioAnx-ESP32")
        self.input_mac = QLineEdit()
        self.input_mac.setPlaceholderText("Dikosongkan jika ingin mode pencarian otomatis")
        
        form_dev.addRow(QLabel("Nama Perangkat Target:"), self.input_dev_name)
        form_dev.addRow(QLabel("MAC Address (Opsional):"), self.input_mac)
        
        btn_scan = QPushButton("Cari Perangkat Sekarang")
        btn_reset = QPushButton("Reset Perangkat")
        
        btn_style = "QPushButton { background-color: #112A54; color: white; border-radius: 4px; padding: 10px 15px; font-weight: bold; } QPushButton:hover { background-color: #1A3A70; }"
        btn_scan.setStyleSheet(btn_style)
        btn_reset.setStyleSheet("QPushButton { background-color: #D32F2F; color: white; border-radius: 4px; padding: 10px 15px; font-weight: bold; } QPushButton:hover { background-color: #B71C1C; }")
        
        btn_scan.clicked.connect(lambda: QMessageBox.information(self, "Bluetooth", "Memindai perangkat...\\n(Simulasi: Perangkat ditemukan!)"))
        btn_reset.clicked.connect(lambda: QMessageBox.information(self, "Reset", "Perangkat berhasil di-reset dan dilepaskan dari memori."))
        
        box_btn = QHBoxLayout()
        box_btn.addWidget(btn_scan)
        box_btn.addWidget(btn_reset)
        box_btn.addStretch()
        form_dev.addRow(QLabel("Aksi:"), box_btn)
        
        # 2. PENYIMPANAN LAPORAN
        group_store = QGroupBox(" Penyimpanan Ekspor & Laporan")
        group_store.setStyleSheet(group_dev.styleSheet())
        form_store = QFormLayout(group_store)
        form_store.setContentsMargins(25, 25, 25, 25)
        form_store.setSpacing(15)
        
        self.input_dir = QLineEdit("C:/Users/oslan/Documents/PhysioAnx_Reports")
        btn_browse = QPushButton("Pilih Folder")
        btn_browse.setStyleSheet(btn_style)
        btn_browse.clicked.connect(self.browse_folder)
        
        box_dir = QHBoxLayout()
        box_dir.addWidget(self.input_dir)
        box_dir.addWidget(btn_browse)
        form_store.addRow(QLabel("Folder Output Laporan:"), box_dir)
        
        # 3. KALIBRASI / THRESHOLD
        group_cal = QGroupBox(" Kalibrasi Sensor (Default Baseline)")
        group_cal.setStyleSheet(group_dev.styleSheet())
        form_cal = QFormLayout(group_cal)
        form_cal.setContentsMargins(25, 25, 25, 25)
        form_cal.setSpacing(15)
        
        form_cal.addRow(QLabel("Ambang Batas Heart Rate (BPM):"), QLineEdit("100"))
        form_cal.addRow(QLabel("Ambang Batas Cemas GSR (µS):"), QLineEdit("20.5"))
        
        scroll_layout.addWidget(group_dev)
        scroll_layout.addWidget(group_store)
        scroll_layout.addWidget(group_cal)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        btn_save = QPushButton("SIMPAN SEMUA PENGATURAN")
        btn_save.setFixedSize(250, 45)
        btn_save.setStyleSheet("background-color: #2E7D32; color: white; border-radius: 4px; font-weight: bold; font-size: 14px;")
        btn_save.clicked.connect(lambda: QMessageBox.information(self, "Tersimpan", "Semua pengaturan berhasil disimpan ke dalam sistem."))
        
        layout.addWidget(btn_save, alignment=Qt.AlignRight)

    def browse_folder(self):
        from PySide6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Penyimpanan")
        if folder:
            self.input_dir.setText(folder)

