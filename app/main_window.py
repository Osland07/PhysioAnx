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
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
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
        sidebar_layout.addSpacing(30)
        sidebar_layout.addWidget(self.btn_pasien)
        sidebar_layout.addWidget(self.btn_session)
        sidebar_layout.addWidget(self.btn_report)
        sidebar_layout.addWidget(self.btn_setting)
        sidebar_layout.addStretch()

        # Tombol Logout
        btn_logout = QPushButton("  Keluar")
        btn_logout.setIcon(qta.icon('fa5s.sign-out-alt', color='#FF5252'))
        btn_logout.setIconSize(QSize(16, 16))
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #FF5252;
                font-weight: 600;
                font-size: 13px;
                border: 1px solid rgba(255,82,82,0.3);
                border-radius: 6px;
                padding: 8px 16px;
                margin: 0 16px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: rgba(255,82,82,0.1);
                border: 1px solid rgba(255,82,82,0.6);
            }
        """)
        btn_logout.clicked.connect(self._do_logout)
        sidebar_layout.addWidget(btn_logout)
        sidebar_layout.addSpacing(10)

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
        
        # Memuat data untuk combobox pasien
        self.load_patients_to_combobox()
        
        # Default ke Data Pasien
        self.switch_page(0)


    def update_time(self):
        current_time = QTime.currentTime()
        jam = current_time.hour()
        if 5 <= jam < 11: sapaan = "Selamat Pagi"
        elif 11 <= jam < 15: sapaan = "Selamat Siang"
        elif 15 <= jam < 18: sapaan = "Selamat Sore"
        else: sapaan = "Selamat Malam"
        nama = self.current_user.full_name if self.current_user else "Pengguna"
        self.greeting_label.setText(f"{sapaan}, {nama}!")
        self.clock_label.setText(current_time.toString("HH:mm:ss"))

    def _do_logout(self):
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Konfirmasi Keluar",
            "Apakah Anda yakin ingin keluar dari sistem?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from login_window import LoginWindow
            self.login_window = LoginWindow()
            def _back_to_main():
                user = self.login_window.get_logged_in_user()
                self.login_window.close()
                new_win = MainWindow(current_user=user)
                new_win.show()
            self.login_window.accept_login = _back_to_main
            self.login_window.show()
            self.close()


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

    def start_examination(self, patient, umur):
        self.lbl_info_rm.setText(f"RM: {patient.no_rm}")
        self.lbl_info_nama.setText(patient.full_name)
        self.lbl_info_usia.setText(f"Usia: {umur}")
        self.lbl_info_gender.setText(f"Gender: {patient.gender}")
        
        # Pindah ke halaman Live Session dan langsung ke Active Session
        self.switch_page(1)
        if hasattr(self, 'session_stacked'):
            self.session_stacked.setCurrentIndex(1)
            
    def validate_session_start(self, text):
        if not hasattr(self, 'btn_enter_session'):
            return

        is_valid = " - " in text and len(text) > 5
        self.btn_enter_session.setEnabled(is_valid)

        if is_valid:
            self.btn_enter_session.setStyleSheet("""
                QPushButton {
                    background-color: #1565C0;
                    color: #FFFFFF;
                    font-weight: bold;
                    font-size: 14px;
                    border-radius: 6px;
                    border: none;
                    padding: 0 20px;
                    letter-spacing: 0.5px;
                }
                QPushButton:hover { background-color: #1976D2; }
                QPushButton:pressed { background-color: #0D47A1; }
            """)
            # Update preview kartu pasien
            self._refresh_patient_preview(text)
        else:
            self.btn_enter_session.setStyleSheet("""
                QPushButton {
                    background-color: #CFD8DC;
                    color: #90A4AE;
                    font-weight: bold;
                    font-size: 14px;
                    border-radius: 6px;
                    border: none;
                    padding: 0 20px;
                }
            """)
            self._clear_patient_preview()

    def _refresh_patient_preview(self, text):
        if not hasattr(self, 'prev_nama'):
            return
        rm = text.split(" - ")[0] if " - " in text else ""
        if not rm:
            self._clear_patient_preview()
            return

        session = SessionLocal()
        p = session.query(Patient).filter(Patient.no_rm == rm).first()
        session.close()

        if p:
            gender_full = "Laki-laki" if p.gender == "L" else "Perempuan"
            usia_str = "-"
            if p.date_of_birth:
                today = date.today()
                age = today.year - p.date_of_birth.year - (
                    (today.month, today.day) < (p.date_of_birth.month, p.date_of_birth.day)
                )
                usia_str = f"{age} Tahun"

            self.prev_nama.setText(p.full_name)
            self.prev_rm.setText(f"No. RM: {p.no_rm}")
            self.prev_jk.setText(gender_full)
            self.prev_usia.setText(usia_str)
            bb_str = f"{p.weight} kg" if p.weight else "-"
            tb_str = f"{p.height} cm" if p.height else "-"
            self.prev_bb.setText(bb_str)
            self.prev_tb.setText(tb_str)

    def _clear_patient_preview(self):
        if not hasattr(self, 'prev_nama'):
            return
        self.prev_nama.setText("Belum Dipilih")
        self.prev_rm.setText("No. RM: -")
        for attr in ['prev_jk', 'prev_usia', 'prev_bb', 'prev_tb']:
            if hasattr(self, attr):
                getattr(self, attr).setText("-")


    def enter_active_session(self):
        teks_pasien = self.cmb_pasien_session.currentText()
        rm_pasien = teks_pasien.split(" - ")[0] if " - " in teks_pasien else "-"
        nama_pasien = teks_pasien.split(" - ")[-1] if " - " in teks_pasien else teks_pasien
        usia_pasien = "-"
        gender_pasien = "-"

        if rm_pasien != "-":
            session = SessionLocal()
            p = session.query(Patient).filter(Patient.no_rm == rm_pasien).first()
            if p:
                nama_pasien = p.full_name
                gender_pasien = "Laki-laki" if p.gender == "L" else "Perempuan"
                if p.date_of_birth:
                    today = date.today()
                    age = today.year - p.date_of_birth.year - (
                        (today.month, today.day) < (p.date_of_birth.month, p.date_of_birth.day)
                    )
                    usia_pasien = f"{age} Tahun"
            session.close()

        self.lbl_info_rm.setText(f"RM: {rm_pasien}")
        self.lbl_info_nama.setText(nama_pasien)
        self.lbl_info_usia.setText(f"Usia: {usia_pasien}")
        self.lbl_info_gender.setText(f"Jenis Kelamin: {gender_pasien}")

        if hasattr(self, 'session_stacked'):
            self.session_stacked.setCurrentIndex(1)


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
        
        self.search_input_pasien = QLineEdit()
        self.search_input_pasien.setObjectName("SearchBar")
        self.search_input_pasien.setPlaceholderText("Cari No. RM atau Nama Pasien...")
        self.search_input_pasien.setMinimumWidth(300)
        self.search_input_pasien.textChanged.connect(self.load_patients_to_table)
        
        self.cmb_gender_pasien = QComboBox()
        self.cmb_gender_pasien.addItems(["Semua Jenis Kelamin", "Laki-laki", "Perempuan"])
        self.cmb_gender_pasien.setFixedSize(210, 40)
        self.cmb_gender_pasien.currentIndexChanged.connect(self.load_patients_to_table)
        
        btn_filter = QPushButton(" Filter")
        btn_filter.setIcon(qta.icon('fa5s.filter', color='white'))
        btn_filter.setObjectName("SecondaryButton")
        btn_filter.setFixedSize(100, 40)
        btn_filter.setCursor(Qt.PointingHandCursor)
        btn_filter.clicked.connect(self.load_patients_to_table)
        
        filter_layout.addWidget(self.search_input_pasien)
        filter_layout.addWidget(self.cmb_gender_pasien)
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
        self.table_pasien.setColumnWidth(4, 260) # Aksi (Periksa, Edit, Hapus)
        
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
        query = session.query(Patient)
        
        # Terapkan filter jika UI search sudah tersedia
        if hasattr(self, 'search_input_pasien'):
            search_text = self.search_input_pasien.text().strip()
            if search_text:
                query = query.filter((Patient.full_name.ilike(f"%{search_text}%")) | (Patient.no_rm.ilike(f"%{search_text}%")))
                
        if hasattr(self, 'cmb_gender_pasien'):
            gender_text = self.cmb_gender_pasien.currentText()
            if gender_text != "Semua Jenis Kelamin":
                query = query.filter(Patient.gender == gender_text)
                
        patients = query.all()
        
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
            
            btn_periksa = QPushButton(" Periksa")
            btn_periksa.setIcon(qta.icon('fa5s.stethoscope', color='white'))
            btn_periksa.setStyleSheet("background-color: #4CAF50; color: white; border: none; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
            btn_periksa.setCursor(Qt.PointingHandCursor)
            btn_periksa.clicked.connect(lambda checked, pat=p, u=umur: self.start_examination(pat, u))
            
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
            action_layout.addWidget(btn_periksa)
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)
            action_layout.addStretch()
            self.table_pasien.setCellWidget(row, 4, action_widget)
            
        self.lbl_info.setText(f"Menampilkan 1 hingga {len(patients)} dari {len(patients)} entri")
        session.close()

    def load_patients_to_combobox(self):
        if not hasattr(self, 'cmb_pasien_session'):
            return
            
        session = SessionLocal()
        patients = session.query(Patient).all()
        
        # Simpan status QCompleter untuk di-reapply agar list ter-update di model
        completer = self.cmb_pasien_session.completer()
        
        self.cmb_pasien_session.clear()
        for p in patients:
            self.cmb_pasien_session.addItem(f"{p.no_rm} - {p.full_name}")
            
        if completer:
            completer.setModel(self.cmb_pasien_session.model())
            
        session.close()
        # Juga perbarui tabel daftar pasien di halaman pre-session
        self._load_session_patient_table()


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
            self.load_patients_to_combobox()

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
            self.load_patients_to_combobox()

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
            self.load_patients_to_combobox()

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
        
        self.table_sesi = QTableWidget(0, 5)
        self.table_sesi.setHorizontalHeaderLabels([
            "Tanggal Sesi", "No. RM - Nama Pasien", "Durasi", "Indikasi", "Aksi"
        ])
        
        # Konfigurasi Header Tabel
        from PySide6.QtWidgets import QHeaderView
        header = self.table_sesi.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Stretch) # Kolom Nama memanjang
        
        self.table_sesi.setColumnWidth(0, 150) # Tanggal
        self.table_sesi.setColumnWidth(2, 100) # Durasi
        self.table_sesi.setColumnWidth(3, 150) # Indikasi
        self.table_sesi.setColumnWidth(4, 180) # Aksi
        
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
            self.table_sesi.setCellWidget(row, 3, ind_widget)
            
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
            self.table_sesi.setCellWidget(row, 4, action_widget)
            
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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.session_stacked = QStackedWidget()
        layout.addWidget(self.session_stacked)

        # ================================================================
        # SUB-PAGE 0: PRE-SESSION — Pilih Pasien (Standar SIMRS)
        # ================================================================
        from PySide6.QtWidgets import (
            QScrollArea, QSizePolicy, QTableWidget, QTableWidgetItem,
            QHeaderView, QCompleter, QSplitter
        )
        from PySide6.QtCore import QDate

        self.page_pre_session = QWidget()
        self.page_pre_session.setObjectName("PreSessionPage")
        self.page_pre_session.setStyleSheet("""
            QWidget#PreSessionPage {
                background-color: #081B3B;
            }
        """)

        pre_root = QVBoxLayout(self.page_pre_session)
        pre_root.setContentsMargins(0, 0, 0, 0)
        pre_root.setSpacing(0)

        # --- BREADCRUMB / HEADER BAR ---
        header_bar = QFrame()
        header_bar.setFixedHeight(56)
        header_bar.setStyleSheet("""
            QFrame {
                background-color: #0A1F40;
                border-bottom: 2px solid #1C3565;
            }
        """)
        header_bar_layout = QHBoxLayout(header_bar)
        header_bar_layout.setContentsMargins(28, 0, 28, 0)
        header_bar_layout.setSpacing(8)

        # Breadcrumb icons + text
        lbl_bc_icon = QLabel()
        lbl_bc_icon.setPixmap(qta.icon('fa5s.heartbeat', color='#40C4FF').pixmap(18, 18))
        lbl_bc_icon.setStyleSheet("background: transparent; border: none;")
        lbl_bc1 = QLabel("Sesi Pemeriksaan")
        lbl_bc1.setStyleSheet("color: #5C7AAA; font-size: 13px; font-weight: 600; background: transparent; border: none;")
        lbl_bc_sep = QLabel("/")
        lbl_bc_sep.setStyleSheet("color: #1C3565; font-size: 13px; background: transparent; border: none;")
        lbl_bc2 = QLabel("Mulai Sesi Baru")
        lbl_bc2.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: 700; background: transparent; border: none;")

        header_bar_layout.addWidget(lbl_bc_icon)
        header_bar_layout.addWidget(lbl_bc1)
        header_bar_layout.addWidget(lbl_bc_sep)
        header_bar_layout.addWidget(lbl_bc2)
        header_bar_layout.addStretch()

        # Tanggal di kanan
        from datetime import datetime
        lbl_date = QLabel(datetime.now().strftime("%d %B %Y"))
        lbl_date.setStyleSheet("color: #8C9EBA; font-size: 12px; font-weight: 600; background: transparent; border: none;")
        header_bar_layout.addWidget(lbl_date)
        pre_root.addWidget(header_bar)

        # --- KONTEN UTAMA (Scrollable) ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: #081B3B; }
            QScrollBar:vertical {
                background: #0A1F40; width: 8px; border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #1C3565; border-radius: 4px; min-height: 40px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #081B3B;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(28, 24, 28, 24)
        scroll_layout.setSpacing(20)

        # --- SECTION TITLE ---
        sec_title = QLabel("Mulai Sesi Pemeriksaan Baru")
        sec_title.setStyleSheet("""
            color: #FFFFFF;
            font-size: 22px;
            font-weight: 800;
            background: transparent;
        """)
        sec_sub = QLabel("Pilih pasien yang akan diperiksa, periksa data identitas, lalu mulai sesi pemantauan fisiologis.")
        sec_sub.setStyleSheet("color: #8C9EBA; font-size: 13px; background: transparent;")
        scroll_layout.addWidget(sec_title)
        scroll_layout.addWidget(sec_sub)

        # --- PANEL UTAMA: 2 kolom (Kiri: Pencarian, Kanan: Preview) ---
        main_row = QHBoxLayout()
        main_row.setSpacing(20)

        # ---- KOLOM KIRI: Pencarian & Pemilihan Pasien ----
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #0F2040;
                border: 1px solid #1C3565;
                border-radius: 10px;
            }
        """)
        left_panel.setGraphicsEffect(create_shadow())
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(20, 20, 20, 20)
        left_panel_layout.setSpacing(14)

        # Sub-header kiri
        left_hdr = QHBoxLayout()
        lbl_search_icon = QLabel()
        lbl_search_icon.setPixmap(qta.icon('fa5s.user-injured', color='#40C4FF').pixmap(20, 20))
        lbl_search_icon.setStyleSheet("background: transparent; border: none;")
        lbl_left_title = QLabel("Pencarian Pasien")
        lbl_left_title.setStyleSheet("color: #FFFFFF; font-size: 15px; font-weight: 700; background: transparent; border: none;")
        btn_tambah_ps = QPushButton("  + Pasien Baru")
        btn_tambah_ps.setStyleSheet("""
            QPushButton {
                background-color: #112A54;
                color: #40C4FF;
                font-weight: 700;
                font-size: 12px;
                border-radius: 5px;
                border: 1.5px solid #1C3565;
                padding: 5px 12px;
            }
            QPushButton:hover { background-color: #1A3A70; }
        """)
        btn_tambah_ps.setCursor(Qt.PointingHandCursor)
        btn_tambah_ps.clicked.connect(self.show_add_patient_dialog)
        left_hdr.addWidget(lbl_search_icon)
        left_hdr.addWidget(lbl_left_title)
        left_hdr.addStretch()
        left_hdr.addWidget(btn_tambah_ps)
        left_panel_layout.addLayout(left_hdr)

        # Garis separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("color: #1C3565; background-color: #1C3565; border: none; max-height: 1px;")
        left_panel_layout.addWidget(sep1)

        # Search bar
        lbl_cari = QLabel("Cari Pasien (Nama / No. Rekam Medis):")
        lbl_cari.setStyleSheet("color: #8C9EBA; font-size: 12px; font-weight: 600; background: transparent; border: none;")
        left_panel_layout.addWidget(lbl_cari)

        search_row = QHBoxLayout()
        search_row.setSpacing(0)

        search_icon_lbl = QLabel()
        search_icon_lbl.setPixmap(qta.icon('fa5s.search', color='#94A3B8').pixmap(16, 16))
        search_icon_lbl.setFixedSize(40, 42)
        search_icon_lbl.setAlignment(Qt.AlignCenter)
        search_icon_lbl.setStyleSheet("""
            background-color: #071733;
            border: 1.5px solid #1C3565;
            border-right: none;
            border-top-left-radius: 6px;
            border-bottom-left-radius: 6px;
        """)

        self.cmb_pasien_session = QComboBox()
        self.cmb_pasien_session.setEditable(True)
        self.cmb_pasien_session.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_pasien_session.lineEdit().setPlaceholderText("Ketik nama pasien atau No. RM...")
        self.cmb_pasien_session.setFixedHeight(42)
        self.cmb_pasien_session.setStyleSheet("""
            QComboBox {
                background-color: #071733;
                border: 1.5px solid #1C3565;
                border-left: none;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                color: #FFFFFF;
                font-size: 13px;
                padding-left: 8px;
            }
            QComboBox:focus {
                border: 1.5px solid #40C4FF;
                border-left: none;
            }
            QComboBox::drop-down { width: 30px; border: none; }
            QComboBox::down-arrow { image: none; width: 0; }
            QComboBox QAbstractItemView {
                background-color: #0F2040;
                color: #FFFFFF;
                border: 1px solid #1C3565;
                border-radius: 6px;
                selection-background-color: #1A3A70;
                selection-color: #40C4FF;
                outline: none;
                font-size: 13px;
                padding: 4px;
            }
        """)

        completer = QCompleter(self.cmb_pasien_session.model(), self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self.cmb_pasien_session.setCompleter(completer)

        original_mouse_press = self.cmb_pasien_session.lineEdit().mousePressEvent
        def _show_popup(event):
            self.cmb_pasien_session.showPopup()
            original_mouse_press(event)
        self.cmb_pasien_session.lineEdit().mousePressEvent = _show_popup

        search_row.addWidget(search_icon_lbl)
        search_row.addWidget(self.cmb_pasien_session, stretch=1)
        left_panel_layout.addLayout(search_row)

        # Hint text
        lbl_hint = QLabel("💡  Pilih dari dropdown atau ketik untuk pencarian cepat.")
        lbl_hint.setStyleSheet("color: #5C7AAA; font-size: 11px; background: transparent; border: none;")
        left_panel_layout.addWidget(lbl_hint)

        left_panel_layout.addStretch()

        # --- INFO STATUS ---
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #071733;
                border: 1px solid #1C3565;
                border-radius: 6px;
            }
        """)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(14, 10, 14, 10)
        lbl_status_icon = QLabel()
        lbl_status_icon.setPixmap(qta.icon('fa5s.info-circle', color='#94A3B8').pixmap(14, 14))
        lbl_status_icon.setStyleSheet("background: transparent; border: none;")
        lbl_status_text = QLabel("Silakan pilih pasien terlebih dahulu sebelum memulai sesi pemeriksaan.")
        lbl_status_text.setStyleSheet("color: #8C9EBA; font-size: 12px; background: transparent; border: none;")
        status_layout.addWidget(lbl_status_icon)
        status_layout.addSpacing(6)
        status_layout.addWidget(lbl_status_text)
        status_layout.addStretch()
        left_panel_layout.addWidget(status_frame)

        # ---- KOLOM KANAN: Preview Identitas Pasien ----
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #0F2040;
                border: 1px solid #1C3565;
                border-radius: 10px;
            }
        """)
        right_panel.setGraphicsEffect(create_shadow())
        right_panel.setMinimumWidth(320)
        right_panel.setMaximumWidth(380)
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(20, 20, 20, 20)
        right_panel_layout.setSpacing(14)

        # Sub-header kanan
        right_hdr = QHBoxLayout()
        lbl_prev_icon = QLabel()
        lbl_prev_icon.setPixmap(qta.icon('fa5s.id-card', color='#40C4FF').pixmap(20, 20))
        lbl_prev_icon.setStyleSheet("background: transparent; border: none;")
        lbl_right_title = QLabel("Identitas Pasien")
        lbl_right_title.setStyleSheet("color: #FFFFFF; font-size: 15px; font-weight: 700; background: transparent; border: none;")
        right_hdr.addWidget(lbl_prev_icon)
        right_hdr.addWidget(lbl_right_title)
        right_hdr.addStretch()
        right_panel_layout.addLayout(right_hdr)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color: #1C3565; background-color: #1C3565; border: none; max-height: 1px;")
        right_panel_layout.addWidget(sep2)

        # Kartu avatar + nama pasien
        avatar_row = QHBoxLayout()
        avatar_row.setSpacing(14)
        avatar_lbl = QLabel()
        avatar_lbl.setPixmap(qta.icon('fa5s.user-circle', color='#94A3B8').pixmap(52, 52))
        avatar_lbl.setStyleSheet("background: transparent; border: none;")
        avatar_lbl.setFixedSize(52, 52)

        name_col = QVBoxLayout()
        name_col.setSpacing(3)
        self.prev_nama = QLabel("Belum Dipilih")
        self.prev_nama.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: 800; background: transparent; border: none;")
        self.prev_rm = QLabel("No. RM: -")
        self.prev_rm.setStyleSheet("color: #8C9EBA; font-size: 12px; background: transparent; border: none;")
        name_col.addWidget(self.prev_nama)
        name_col.addWidget(self.prev_rm)

        avatar_row.addWidget(avatar_lbl)
        avatar_row.addLayout(name_col)
        avatar_row.addStretch()
        right_panel_layout.addLayout(avatar_row)

        # Grid detail identitas
        def _make_detail_row(icon_name, label, value_attr):
            row = QHBoxLayout()
            row.setSpacing(10)
            ic = QLabel()
            ic.setPixmap(qta.icon(icon_name, color='#5C7AAA').pixmap(14, 14))
            ic.setStyleSheet("background: transparent; border: none;")
            ic.setFixedWidth(20)
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #5C7AAA; font-size: 12px; min-width: 100px; background: transparent; border: none;")
            val = QLabel("-")
            val.setStyleSheet("color: #E2E8F0; font-size: 12px; font-weight: 600; background: transparent; border: none;")
            setattr(self, value_attr, val)
            row.addWidget(ic)
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            return row

        right_panel_layout.addLayout(_make_detail_row('fa5s.venus-mars', 'Jenis Kelamin', 'prev_jk'))
        right_panel_layout.addLayout(_make_detail_row('fa5s.birthday-cake', 'Usia', 'prev_usia'))
        right_panel_layout.addLayout(_make_detail_row('fa5s.weight', 'Berat Badan', 'prev_bb'))
        right_panel_layout.addLayout(_make_detail_row('fa5s.ruler-vertical', 'Tinggi Badan', 'prev_tb'))

        sep3 = QFrame()
        sep3.setFrameShape(QFrame.HLine)
        sep3.setStyleSheet("color: #1C3565; background-color: #1C3565; border: none; max-height: 1px;")
        right_panel_layout.addWidget(sep3)

        # Tombol MULAI SESI
        self.btn_enter_session = QPushButton("  Mulai Sesi Pemeriksaan")
        self.btn_enter_session.setIcon(qta.icon('fa5s.play-circle', color='#90A4AE'))
        self.btn_enter_session.setIconSize(QSize(18, 18))
        self.btn_enter_session.setFixedHeight(46)
        self.btn_enter_session.setCursor(Qt.PointingHandCursor)
        self.btn_enter_session.setToolTip("Pilih pasien terlebih dahulu untuk mengaktifkan tombol ini")
        self.btn_enter_session.setStyleSheet("""
            QPushButton {
                background-color: #112A54;
                color: #5C7AAA;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
                border: 1px solid #1C3565;
                padding: 0 20px;
            }
        """)
        self.btn_enter_session.setEnabled(False)
        self.btn_enter_session.clicked.connect(self.enter_active_session)
        right_panel_layout.addWidget(self.btn_enter_session)

        right_panel_layout.addStretch()

        main_row.addWidget(left_panel, stretch=1)
        main_row.addWidget(right_panel)
        scroll_layout.addLayout(main_row)

        # --- TABEL DAFTAR PASIEN TERDAFTAR ---
        tbl_outer = QFrame()
        tbl_outer.setStyleSheet("""
            QFrame {
                background-color: #0F2040;
                border: 1px solid #1C3565;
                border-radius: 10px;
            }
        """)
        tbl_outer.setGraphicsEffect(create_shadow())
        tbl_outer_layout = QVBoxLayout(tbl_outer)
        tbl_outer_layout.setContentsMargins(20, 18, 20, 18)
        tbl_outer_layout.setSpacing(14)

        tbl_hdr = QHBoxLayout()
        lbl_tbl_icon = QLabel()
        lbl_tbl_icon.setPixmap(qta.icon('fa5s.list-alt', color='#40C4FF').pixmap(18, 18))
        lbl_tbl_icon.setStyleSheet("background: transparent; border: none;")
        lbl_tbl_title = QLabel("Daftar Pasien Terdaftar")
        lbl_tbl_title.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 700; background: transparent; border: none;")
        lbl_tbl_sub = QLabel("(Klik baris untuk memilih pasien)")
        lbl_tbl_sub.setStyleSheet("color: #5C7AAA; font-size: 12px; background: transparent; border: none;")
        tbl_hdr.addWidget(lbl_tbl_icon)
        tbl_hdr.addWidget(lbl_tbl_title)
        tbl_hdr.addSpacing(6)
        tbl_hdr.addWidget(lbl_tbl_sub)
        tbl_hdr.addStretch()
        tbl_outer_layout.addLayout(tbl_hdr)

        sep_tbl = QFrame()
        sep_tbl.setFrameShape(QFrame.HLine)
        sep_tbl.setStyleSheet("color: #1C3565; background-color: #1C3565; border: none; max-height: 1px;")
        tbl_outer_layout.addWidget(sep_tbl)

        self.tbl_session_pasien = QTableWidget(0, 4)
        self.tbl_session_pasien.setHorizontalHeaderLabels(["No. RM", "Nama Pasien", "Usia", "Jenis Kelamin"])
        self.tbl_session_pasien.setStyleSheet("""
            QTableWidget {
                background-color: #0F2040;
                border: none;
                gridline-color: #112A54;
                color: #E2E8F0;
                font-size: 13px;
                outline: none;
            }
            QTableWidget::item {
                padding: 10px 12px;
                border-bottom: 1px solid #112A54;
            }
            QTableWidget::item:selected {
                background-color: #1A3A70;
                color: #40C4FF;
            }
            QHeaderView::section {
                background-color: #071733;
                color: #8C9EBA;
                font-weight: 700;
                font-size: 12px;
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid #1C3565;
            }
        """)
        self.tbl_session_pasien.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_session_pasien.setSelectionBehavior(QTableWidget.SelectRows)
        self.tbl_session_pasien.setSelectionMode(QTableWidget.SingleSelection)
        self.tbl_session_pasien.setShowGrid(False)
        self.tbl_session_pasien.verticalHeader().setVisible(False)
        self.tbl_session_pasien.verticalHeader().setDefaultSectionSize(48)
        self.tbl_session_pasien.setFixedHeight(220)

        hdr_tbl = self.tbl_session_pasien.horizontalHeader()
        hdr_tbl.setSectionResizeMode(0, QHeaderView.Fixed)
        hdr_tbl.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr_tbl.setSectionResizeMode(2, QHeaderView.Fixed)
        hdr_tbl.setSectionResizeMode(3, QHeaderView.Fixed)
        self.tbl_session_pasien.setColumnWidth(0, 130)
        self.tbl_session_pasien.setColumnWidth(2, 80)
        self.tbl_session_pasien.setColumnWidth(3, 130)

        def _on_tbl_row_clicked(row, col):
            rm_item = self.tbl_session_pasien.item(row, 0)
            nm_item = self.tbl_session_pasien.item(row, 1)
            if rm_item and nm_item:
                self.cmb_pasien_session.setCurrentText(f"{rm_item.text()} - {nm_item.text()}")
        self.tbl_session_pasien.cellClicked.connect(_on_tbl_row_clicked)

        tbl_outer_layout.addWidget(self.tbl_session_pasien)
        scroll_layout.addWidget(tbl_outer)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        pre_root.addWidget(scroll)

        # Connect validasi & finalize
        self.cmb_pasien_session.currentTextChanged.connect(self.validate_session_start)
        self._clear_patient_preview()
        self.session_stacked.addWidget(self.page_pre_session)

        # ==========================================
        # SUB-PAGE 1: ACTIVE SESSION (Monitoring)
        # ==========================================

        self.page_active_session = QWidget()
        active_layout = QVBoxLayout(self.page_active_session)
        active_layout.setContentsMargins(15, 15, 15, 15)
        active_layout.setSpacing(20)
        
        # --- 1. HEADER PANEL & INFO PASIEN ---
        header_row = QHBoxLayout()
        header_row.setSpacing(20)
        
        # Patient Info Card
        info_panel = QFrame()
        info_panel.setGraphicsEffect(create_shadow())
        info_panel.setStyleSheet("background-color: #0F2040; border-radius: 12px; border: 1px solid #1C3565;")
        info_layout = QHBoxLayout(info_panel)
        info_layout.setContentsMargins(20, 15, 20, 15)
        
        icon_patient = QLabel()
        icon_patient.setPixmap(qta.icon('fa5s.user', color='#64748B').pixmap(30, 30))
        icon_patient.setStyleSheet("border: none; background: transparent;")
        
        patient_details = QVBoxLayout()
        patient_details.setSpacing(2)
        
        self.lbl_info_nama = QLabel("Belum ada pasien dipilih")
        self.lbl_info_nama.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: 800; border: none; background: transparent;")
        
        info_sub = QHBoxLayout()
        self.lbl_info_rm = QLabel("RM: -")
        self.lbl_info_usia = QLabel("Usia: -")
        self.lbl_info_gender = QLabel("Gender: -")
        
        for lbl in [self.lbl_info_rm, self.lbl_info_usia, self.lbl_info_gender]:
            lbl.setStyleSheet("color: #8C9EBA; font-size: 13px; border: none; background: transparent; padding-right: 15px;")
            info_sub.addWidget(lbl)
        info_sub.addStretch()
        
        patient_details.addWidget(self.lbl_info_nama)
        patient_details.addLayout(info_sub)
        
        info_layout.addWidget(icon_patient)
        info_layout.addSpacing(15)
        info_layout.addLayout(patient_details)
        info_layout.addStretch()
        
        # Device Connection Card
        dev_panel = QFrame()
        dev_panel.setGraphicsEffect(create_shadow())
        dev_panel.setStyleSheet("background-color: #0F2040; border-radius: 12px; border: 1px solid #1C3565;")
        dev_layout = QHBoxLayout(dev_panel)
        dev_layout.setContentsMargins(20, 15, 20, 15)
        
        self.lbl_bluetooth = QLabel("Alat Disconnected")
        self.lbl_bluetooth.setStyleSheet("color: #FF5252; font-weight: bold; font-size: 15px; border: none; background: transparent;")
        self.icon_bluetooth = QLabel()
        self.icon_bluetooth.setPixmap(qta.icon('fa5b.bluetooth', color='#FF5252').pixmap(24, 24))
        self.icon_bluetooth.setStyleSheet("border: none; background: transparent;")
        
        btn_connect = QPushButton(" Hubungkan")
        btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #112A54; 
                color: white; 
                border-radius: 6px; 
                padding: 10px 20px; 
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #1A3A70; }
        """)
        btn_connect.setCursor(Qt.PointingHandCursor)
        
        dev_layout.addWidget(self.icon_bluetooth)
        dev_layout.addWidget(self.lbl_bluetooth)
        dev_layout.addStretch()
        dev_layout.addWidget(btn_connect)
        
        header_row.addWidget(info_panel, stretch=2)
        header_row.addWidget(dev_panel, stretch=1)
        
        # --- 2. SENSOR CARDS ---
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        self.card_hr, self.lbl_val_hr = self.create_sensor_card("HEART RATE", "--", "BPM", "#FF5252", "fa5s.heartbeat")
        self.card_gsr, self.lbl_val_gsr = self.create_sensor_card("GSR", "--", "µS", "#40C4FF", "fa5s.bolt")
        self.card_temp, self.lbl_val_temp = self.create_sensor_card("TEMPERATURE", "--", "°C", "#FFB300", "fa5s.thermometer-half")
        
        cards_layout.addWidget(self.card_hr)
        cards_layout.addWidget(self.card_gsr)
        cards_layout.addWidget(self.card_temp)
        
        # --- 3. GRAFIK & KONTROL SESI ---
        main_content = QHBoxLayout()
        main_content.setSpacing(20)
        
        # Grafik
        graph_panel = QFrame()
        graph_panel.setGraphicsEffect(create_shadow())
        graph_panel.setStyleSheet("background-color: #0F2040; border-radius: 12px; border: 1px solid #1C3565;")
        gl = QVBoxLayout(graph_panel)
        gl.setContentsMargins(20, 20, 20, 20)
        
        graph_header = QHBoxLayout()
        gl_title = QLabel("Real-time Data Monitor")
        gl_title.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 16px; border: none; background: transparent;")
        
        self.lbl_status_sesi = QLabel(" Sesi Belum Dimulai ")
        self.lbl_status_sesi.setStyleSheet("color: #64748B; font-weight: bold; font-size: 12px; border: none; padding: 6px 12px; background-color: #051024; border-radius: 6px;")
        
        graph_header.addWidget(gl_title)
        graph_header.addStretch()
        graph_header.addWidget(self.lbl_status_sesi)
        
        pg.setConfigOption('background', 'transparent')
        pg.setConfigOption('foreground', '#64748B')
        self.plot = pg.PlotWidget()
        self.plot.getAxis('left').setPen('#64748B')
        self.plot.getAxis('bottom').setPen('#64748B')
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        
        import numpy as np
        self.x_data = np.linspace(0, 10, 300)
        self.phase = 0.0
        self.y_data_hr = np.zeros(300)
        self.y_data_gsr = np.zeros(300)
        
        self.curve_hr = self.plot.plot(self.x_data, self.y_data_hr, pen=pg.mkPen(color='#FF5252', width=2.5), name="Heart Rate")
        self.curve_gsr = self.plot.plot(self.x_data, self.y_data_gsr, pen=pg.mkPen(color='#40C4FF', width=2.5), name="GSR")
        
        gl.addLayout(graph_header)
        gl.addSpacing(10)
        gl.addWidget(self.plot)
        
        # Panel Kontrol Kanan
        control_panel = QFrame()
        control_panel.setFixedWidth(280)
        control_panel.setGraphicsEffect(create_shadow())
        control_panel.setStyleSheet("background-color: #0F2040; border-radius: 12px; border: 1px solid #1C3565;")
        cp_layout = QVBoxLayout(control_panel)
        cp_layout.setContentsMargins(25, 25, 25, 25)
        cp_layout.setSpacing(20)
        
        cp_title = QLabel("Kontrol Sesi")
        cp_title.setAlignment(Qt.AlignCenter)
        cp_title.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 16px; border: none; background: transparent; margin-bottom: 10px;")
        
        self.btn_start = QPushButton("  MULAI REKAM")
        self.btn_start.setIcon(qta.icon('fa5s.play', color='white'))
        self.btn_start.setStyleSheet("""
            QPushButton { 
                background-color: #00C853; 
                color: white; 
                font-weight: 900; 
                font-size: 14px; 
                border-radius: 8px; 
                padding: 16px;
            }
            QPushButton:hover { background-color: #00E676; }
        """)
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.clicked.connect(self.toggle_session_recording)
        
        self.btn_stop = QPushButton("  SELESAI")
        self.btn_stop.setIcon(qta.icon('fa5s.stop', color='white'))
        self.btn_stop.setStyleSheet("""
            QPushButton { 
                background-color: #D32F2F; 
                color: white; 
                font-weight: 900; 
                font-size: 14px; 
                border-radius: 8px; 
                padding: 16px;
            }
            QPushButton:hover { background-color: #F44336; }
        """)
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_session_recording)
        
        btn_back = QPushButton(" Kembali")
        btn_back.setIcon(qta.icon('fa5s.arrow-left', color='#8C9EBA'))
        btn_back.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                color: #8C9EBA; 
                font-weight: bold; 
                border: 1px solid #1C3565; 
                border-radius: 8px; 
                padding: 12px;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #112A54; color: white; }
        """)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(lambda: self.session_stacked.setCurrentIndex(0))
        
        cp_layout.addWidget(cp_title)
        cp_layout.addWidget(self.btn_start)
        cp_layout.addWidget(self.btn_stop)
        cp_layout.addStretch()
        cp_layout.addWidget(btn_back)
        
        main_content.addWidget(graph_panel, stretch=1)
        main_content.addWidget(control_panel)
        
        active_layout.addLayout(header_row)
        active_layout.addLayout(cards_layout)
        active_layout.addLayout(main_content, stretch=1)
        
        self.session_stacked.addWidget(self.page_active_session)
        self.session_stacked.setCurrentIndex(0)
        
        self.timer_graph = QTimer(self)
        self.timer_graph.timeout.connect(self.update_fake_graph)
        self.is_recording = False

    def _load_session_patient_table(self):
        if not hasattr(self, 'tbl_session_pasien'):
            return
        session = SessionLocal()
        patients = session.query(Patient).order_by(Patient.full_name).all()
        session.close()

        self.tbl_session_pasien.setRowCount(len(patients))
        for row, p in enumerate(patients):
            item_rm = QTableWidgetItem(p.no_rm)
            item_rm.setFlags(item_rm.flags() & ~Qt.ItemIsEditable)
            self.tbl_session_pasien.setItem(row, 0, item_rm)

            item_nm = QTableWidgetItem(p.full_name)
            item_nm.setFlags(item_nm.flags() & ~Qt.ItemIsEditable)
            self.tbl_session_pasien.setItem(row, 1, item_nm)

            usia_str = "-"
            if p.date_of_birth:
                today = date.today()
                age = today.year - p.date_of_birth.year - (
                    (today.month, today.day) < (p.date_of_birth.month, p.date_of_birth.day)
                )
                usia_str = f"{age} Thn"
            item_usia = QTableWidgetItem(usia_str)
            item_usia.setTextAlignment(Qt.AlignCenter)
            item_usia.setFlags(item_usia.flags() & ~Qt.ItemIsEditable)
            self.tbl_session_pasien.setItem(row, 2, item_usia)

            jk_str = "Laki-laki" if p.gender == "L" else "Perempuan"
            item_jk = QTableWidgetItem(jk_str)
            item_jk.setTextAlignment(Qt.AlignCenter)
            item_jk.setFlags(item_jk.flags() & ~Qt.ItemIsEditable)
            self.tbl_session_pasien.setItem(row, 3, item_jk)

    def toggle_session_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.timer_graph.start(50)
            self.btn_start.setEnabled(False)
            self.btn_start.setStyleSheet("""
                QPushButton { 
                    background-color: #2E7D32; 
                    color: white; 
                    font-weight: 900; 
                    font-size: 14px; 
                    border-radius: 8px; 
                    padding: 16px;
                }
            """)
            self.btn_start.setText("  MEREKAM...")
            self.btn_stop.setEnabled(True)
            self.lbl_status_sesi.setText(" Merekam Data... ")
            self.lbl_status_sesi.setStyleSheet("color: #00E676; font-weight: bold; font-size: 12px; border: none; padding: 6px 12px; background-color: #051024; border-radius: 6px;")
            self.lbl_bluetooth.setText("Alat Terhubung")
            self.lbl_bluetooth.setStyleSheet("color: #00E676; font-weight: bold; font-size: 15px; border: none; background: transparent;")
            self.icon_bluetooth.setPixmap(qta.icon('fa5b.bluetooth', color='#00E676').pixmap(24, 24))

    def stop_session_recording(self):
        self.is_recording = False
        self.timer_graph.stop()
        self.btn_start.setEnabled(True)
        self.btn_start.setStyleSheet("""
            QPushButton { 
                background-color: #00C853; 
                color: white; 
                font-weight: 900; 
                font-size: 14px; 
                border-radius: 8px; 
                padding: 16px;
            }
            QPushButton:hover { background-color: #00E676; }
        """)
        self.btn_start.setText("  MULAI REKAM")
        self.btn_stop.setEnabled(False)
        self.lbl_status_sesi.setText(" Sesi Selesai ")
        self.lbl_status_sesi.setStyleSheet("color: #FF5252; font-weight: bold; font-size: 12px; border: none; padding: 6px 12px; background-color: #051024; border-radius: 6px;")
        
        # Reset data for next session
        import numpy as np
        self.y_data_hr = np.zeros(300)
        self.y_data_gsr = np.zeros(300)
        self.curve_hr.setData(self.x_data, self.y_data_hr)
        self.curve_gsr.setData(self.x_data, self.y_data_gsr)
        self.lbl_val_hr.setText("--")
        self.lbl_val_gsr.setText("--")
        self.lbl_val_temp.setText("--")
        self.lbl_bluetooth.setText("Alat Disconnected")
        self.lbl_bluetooth.setStyleSheet("color: #FF5252; font-weight: bold; font-size: 15px; border: none; background: transparent;")
        self.icon_bluetooth.setPixmap(qta.icon('fa5b.bluetooth', color='#FF5252').pixmap(24, 24))

    def update_fake_graph(self):
        import numpy as np
        self.phase += 0.2
        # Geser gelombang agar beranimasi
        self.y_data_hr[:-1] = self.y_data_hr[1:]
        val_hr = np.sin(self.x_data[-1] * 5 + self.phase) * 10 + 80 + np.random.normal(0, 1)
        self.y_data_hr[-1] = val_hr
        
        self.y_data_gsr[:-1] = self.y_data_gsr[1:]
        val_gsr = np.sin(self.x_data[-1] + self.phase) * 5 + 15 + np.random.normal(0, 0.2)
        self.y_data_gsr[-1] = val_gsr
        
        val_temp = 36.5 + np.random.normal(0, 0.05)
        
        self.curve_hr.setData(self.x_data, self.y_data_hr)
        self.curve_gsr.setData(self.x_data, self.y_data_gsr)
        
        # Update Labels
        self.lbl_val_hr.setText(f"{int(val_hr)}")
        self.lbl_val_gsr.setText(f"{val_gsr:.1f}")
        self.lbl_val_temp.setText(f"{val_temp:.1f}")

    def create_sensor_card(self, title_text, value_text, unit_text, color, icon_name=None):
        card = QFrame()
        card.setGraphicsEffect(create_shadow())
        card.setFixedHeight(110)
        card.setStyleSheet("background-color: #0F2040; border-radius: 12px; border: 1px solid #1C3565;")
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Kiri: Icon + Title + Unit
        left_layout = QVBoxLayout()
        top_left = QHBoxLayout()
        if icon_name:
            icon_lbl = QLabel()
            icon_lbl.setPixmap(qta.icon(icon_name, color=color).pixmap(18, 18))
            icon_lbl.setStyleSheet("border: none; background: transparent;")
            top_left.addWidget(icon_lbl)
            
        title = QLabel(title_text)
        title.setStyleSheet("color: #8C9EBA; font-size: 14px; font-weight: bold; border: none; background: transparent;")
        top_left.addWidget(title)
        top_left.addStretch()
        
        unit = QLabel(unit_text)
        unit.setStyleSheet("color: #64748B; font-size: 13px; font-weight: bold; border: none; background: transparent;")
        
        left_layout.addLayout(top_left)
        left_layout.addStretch()
        left_layout.addWidget(unit)
        
        # Kanan: Value
        val = QLabel(value_text)
        val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        val.setStyleSheet(f"color: {color}; font-size: 42px; font-weight: 900; border: none; background: transparent;")
        
        layout.addLayout(left_layout)
        layout.addStretch()
        layout.addWidget(val)
        
        return card, val

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
        
        group_style = "QGroupBox { color: #69F0AE; font-size: 16px; font-weight: bold; border: 1px solid #112A54; border-radius: 8px; margin-top: 15px; padding-top: 25px; background-color: #081B3B; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; left: 10px; } QLabel { color: #B0BEC5; font-size: 14px; } QLineEdit { background-color: #051024; color: white; border: 1px solid #112A54; border-radius: 4px; padding: 10px; }"
        
        # 1. KONEKSI BLUETOOTH
        group_dev = QGroupBox(" Koneksi Bluetooth (ESP32)")
        group_dev.setStyleSheet(group_style)
        
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
        
        btn_scan.clicked.connect(lambda: QMessageBox.information(self, "Bluetooth", "Memindai perangkat..."))
        btn_reset.clicked.connect(lambda: QMessageBox.information(self, "Reset", "Perangkat berhasil di-reset dan dilepaskan dari memori."))
        
        box_btn = QHBoxLayout()
        box_btn.addWidget(btn_scan)
        box_btn.addWidget(btn_reset)
        box_btn.addStretch()
        form_dev.addRow(QLabel("Aksi:"), box_btn)
        
        # 2. PENYIMPANAN LAPORAN
        group_store = QGroupBox(" Penyimpanan Ekspor & Laporan")
        group_store.setStyleSheet(group_style)
        form_store = QFormLayout(group_store)
        form_store.setContentsMargins(25, 25, 25, 25)
        form_store.setSpacing(15)
        
        from PySide6.QtCore import QStandardPaths
        import os
        docs_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        default_dir = os.path.join(docs_path, "PhysioAnx_Reports").replace("\\", "/")
        self.input_dir = QLineEdit(default_dir)
        btn_browse = QPushButton("Pilih Folder")
        btn_browse.setStyleSheet(btn_style)
        btn_browse.clicked.connect(self.browse_folder)
        
        box_dir = QHBoxLayout()
        box_dir.addWidget(self.input_dir)
        box_dir.addWidget(btn_browse)
        form_store.addRow(QLabel("Folder Output Laporan:"), box_dir)
        
        # 3. TEMA TAMPILAN (UI)
        group_theme = QGroupBox(" Tampilan UI (Mode)")
        group_theme.setStyleSheet(group_style)
        form_theme = QFormLayout(group_theme)
        form_theme.setContentsMargins(25, 25, 25, 25)
        form_theme.setSpacing(15)
        
        btn_dark = QPushButton("Mode Gelap (Aktif)")
        btn_light = QPushButton("Mode Terang")
        
        btn_dark.setStyleSheet("QPushButton { background-color: #1976D2; color: white; border-radius: 4px; padding: 10px 15px; font-weight: bold; }")
        btn_light.setStyleSheet("QPushButton { background-color: #112A54; color: #8C9EBA; border-radius: 4px; padding: 10px 15px; font-weight: bold; border: 1px solid #1C3565; } QPushButton:hover { background-color: #1A3A70; color: white; }")
        
        btn_dark.setCursor(Qt.PointingHandCursor)
        btn_light.setCursor(Qt.PointingHandCursor)
        
        btn_dark.clicked.connect(lambda: QMessageBox.information(self, "Tampilan", "Mode Gelap saat ini sudah aktif."))
        btn_light.clicked.connect(lambda: QMessageBox.information(self, "Tampilan", "Mode Terang akan segera hadir di pembaruan selanjutnya!"))
        
        box_theme = QHBoxLayout()
        box_theme.addWidget(btn_dark)
        box_theme.addWidget(btn_light)
        box_theme.addStretch()
        form_theme.addRow(QLabel("Pilih Tema Aplikasi:"), box_theme)
        
        scroll_layout.addWidget(group_dev)
        scroll_layout.addWidget(group_store)
        scroll_layout.addWidget(group_theme)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        btn_save = QPushButton("Simpan")
        btn_save.setFixedSize(250, 45)
        btn_save.setStyleSheet("background-color: #2E7D32; color: white; border-radius: 4px; font-weight: bold; font-size: 14px;")
        btn_save.clicked.connect(lambda: QMessageBox.information(self, "Tersimpan", "Semua pengaturan berhasil disimpan ke dalam sistem."))
        
        layout.addWidget(btn_save, alignment=Qt.AlignRight)

    def browse_folder(self):
        from PySide6.QtWidgets import QFileDialog
        from PySide6.QtCore import QStandardPaths
        
        default_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Penyimpanan", default_path)
        if folder:
            self.input_dir.setText(folder)

