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
        self.setWindowTitle("PhysioAnx")
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
        
        self.btn_pasien = QPushButton(" Patients")
        self.btn_pasien.setIcon(qta.icon('fa5s.users', color='#8C9EBA'))
        self.btn_pasien.setIconSize(QSize(20, 20))
        
        self.btn_session = QPushButton(" Sesi Pemeriksaan")
        self.btn_session.setIcon(qta.icon('fa5s.heartbeat', color='#8C9EBA'))
        self.btn_session.setIconSize(QSize(20, 20))
        
        self.btn_report = QPushButton(" Riwayat Sesi")
        self.btn_report.setIcon(qta.icon('fa5s.file-medical-alt', color='#8C9EBA'))
        self.btn_report.setIconSize(QSize(20, 20))

        self.btn_help = QPushButton(" Help")
        self.btn_help.setIcon(qta.icon('fa5s.question-circle', color='#8C9EBA'))
        self.btn_help.setIconSize(QSize(20, 20))
        
        self.btn_pasien.clicked.connect(lambda: self.switch_page(0))
        self.btn_session.clicked.connect(lambda: self.switch_page(1))
        self.btn_report.clicked.connect(lambda: self.switch_page(2))
        self.btn_help.clicked.connect(lambda: self.switch_page(3))
        
        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(30)
        sidebar_layout.addWidget(self.btn_pasien)
        sidebar_layout.addWidget(self.btn_session)
        sidebar_layout.addWidget(self.btn_report)
        sidebar_layout.addWidget(self.btn_help)
        sidebar_layout.addStretch()

        # Tombol Logout
        btn_logout = QPushButton(" Keluar")
        btn_logout.setIcon(qta.icon('fa5s.sign-out-alt', color='white'))
        btn_logout.setIconSize(QSize(16, 16))
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #FF0000;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                margin: 0 16px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #D50000;
            }
            QPushButton:pressed {
                background-color: #AA0000;
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
        
        from views.patient_view import PatientView
        from controllers.patient_controller import PatientController
        
        self.page_pasien = PatientView()
        self.patient_ctrl = PatientController(self.page_pasien, self)
        
        self.page_live_session = QWidget()
        self.setup_live_session_page()
        
        from views.report_view import ReportView
        from controllers.report_controller import ReportController
        from views.help_view import HelpView
        
        self.page_report = ReportView()
        self.report_ctrl = ReportController(self.page_report, self)

        self.page_help = HelpView()
        
        self.stacked_widget.addWidget(self.page_pasien)       # 0
        self.stacked_widget.addWidget(self.page_live_session) # 1
        self.stacked_widget.addWidget(self.page_report)       # 2
        self.stacked_widget.addWidget(self.page_help)         # 3
        
        self.content_layout.addWidget(self.top_bar)
        self.content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_area)
        
        # Sinkronisasi jam dari internet di thread terpisah agar UI tidak beku
        import threading
        from services.time_service import TimeService
        time_service = TimeService.get_instance()
        threading.Thread(target=time_service.sync_time, daemon=True).start()
        
        self.update_time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        # Memuat data untuk combobox pasien
        self.load_patients_to_combobox()
        
        # Default ke Data Pasien
        self.switch_page(0)


    def update_time(self):
        from services.time_service import TimeService
        current_time = TimeService.get_instance().get_current_time()
        jam = current_time.hour
        if 5 <= jam < 12: sapaan = "Good Morning"
        elif 12 <= jam < 17: sapaan = "Good Afternoon"
        else: sapaan = "Good Evening"
        nama = self.current_user.full_name if self.current_user else "User"
        self.greeting_label.setText(f"{sapaan}, {nama}!")
        self.clock_label.setText(current_time.strftime("%H:%M:%S"))

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
        
        buttons = [self.btn_pasien, self.btn_session, self.btn_report, self.btn_help]
        for btn in buttons:
            btn.setObjectName("MenuButton")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
        if 0 <= index < len(buttons):
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
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0083B0, stop:1 #00B4DB);
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border-radius: 6px;
                    border: none;
                    padding: 0 20px;
                    letter-spacing: 0.5px;
                }
                QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00B4DB, stop:1 #00D2FF); }
            """)
            # Update preview kartu pasien
            self._refresh_patient_preview(text)
        else:
            self.btn_enter_session.setStyleSheet("""
                QPushButton {
                    background-color: #EDF2F7;
                    color: #A0AEC0;
                    font-weight: bold;
                    font-size: 14px;
                    border-radius: 6px;
                    border: 1px solid #E2E8F0;
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
            self.toggle_session_recording()

    def exit_active_session(self):
        self.stop_session_recording()
        self.session_stacked.setCurrentIndex(0)

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



    # ==========================================
    # HALAMAN 3: RIWAYAT SESI
    # ==========================================

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
            QHeaderView, QCompleter, QSplitter, QGridLayout
        )
        from PySide6.QtCore import QDate

        self.page_pre_session = QWidget()
        self.page_pre_session.setObjectName("PreSessionPage")
        self.page_pre_session.setStyleSheet("""
            QWidget#PreSessionPage {
                background-color: transparent;
            }
        """)

        pre_root = QVBoxLayout(self.page_pre_session)
        pre_root.setContentsMargins(0, 0, 0, 0)
        pre_root.setSpacing(20)

        # --- SECTION TITLE ---
        sec_title = QLabel("Persiapan Sesi Pemeriksaan")
        sec_title.setStyleSheet("""
            color: #2D3748;
            font-size: 24px;
            font-weight: 800;
            background: transparent;
        """)
        sec_sub = QLabel("Pilih pasien yang akan diperiksa, periksa data identitas, lalu mulai sesi.")
        sec_sub.setStyleSheet("color: #718096; font-size: 14px; background: transparent;")
        pre_root.addWidget(sec_title)
        pre_root.addWidget(sec_sub)

        # --- PANEL UTAMA: 2 Kolom Seamless ---
        main_layout = QHBoxLayout()
        main_layout.setSpacing(40)
        main_layout.setContentsMargins(0, 10, 0, 0)

        # ==========================================
        # KOLOM KIRI: Pencarian & Pilihan
        # ==========================================
        left_col = QVBoxLayout()
        left_col.setSpacing(24)


        
        # Search Box Area
        search_area = QVBoxLayout()
        search_area.setSpacing(12)
        
        self.cmb_pasien_session = QComboBox()
        self.cmb_pasien_session.setEditable(True)
        self.cmb_pasien_session.setInsertPolicy(QComboBox.NoInsert)
        self.cmb_pasien_session.lineEdit().setPlaceholderText("Ketik nama pasien atau No. RM di sini...")
        self.cmb_pasien_session.setFixedHeight(54)
        self.cmb_pasien_session.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF; border: 2px solid #E2E8F0; border-radius: 12px;
                color: #2D3748; font-size: 15px; padding-left: 16px;
            }
            QComboBox:focus { border: 2px solid #00B4DB; background-color: #FFFFFF; }
            QComboBox::drop-down { width: 40px; border: none; }
            QComboBox::down-arrow { image: none; width: 0; }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF; color: #2D3748; border: 1px solid #E2E8F0; border-radius: 8px;
                selection-background-color: #EBF8FA; selection-color: #00B4DB; font-size: 14px; padding: 6px; outline: none;
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
        
        # Tombol Pasien Baru (di bawah pencarian)
        btn_tambah_ps = QPushButton("  Daftarkan Pasien Baru")
        btn_tambah_ps.setIcon(qta.icon('fa5s.plus', color='#00B4DB'))
        btn_tambah_ps.setFixedHeight(46)
        btn_tambah_ps.setStyleSheet("""
            QPushButton {
                background-color: #F7FAFC; color: #2D3748; font-weight: 700; font-size: 14px;
                border-radius: 8px; border: 1px solid #E2E8F0;
            }
            QPushButton:hover { background-color: #EDF2F7; }
        """)
        btn_tambah_ps.setCursor(Qt.PointingHandCursor)
        btn_tambah_ps.clicked.connect(self.patient_ctrl.show_add_patient_dialog)

        search_area.addWidget(self.cmb_pasien_session)
        search_area.addWidget(btn_tambah_ps)
        

        left_col.addLayout(search_area)
        left_col.addStretch()

        # ==========================================
        # KOLOM KANAN: Identitas & Mulai
        # ==========================================
        right_col = QVBoxLayout()
        right_col.setSpacing(0)
        
        identity_card = QFrame()
        identity_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
            }
        """)
        identity_card.setGraphicsEffect(create_shadow())
        identity_layout = QVBoxLayout(identity_card)
        identity_layout.setContentsMargins(32, 32, 32, 32)
        identity_layout.setSpacing(24)

        # Profile Header (Avatar + Name)
        prof_layout = QHBoxLayout()
        prof_layout.setSpacing(20)
        
        avatar_lbl = QLabel()
        avatar_lbl.setPixmap(qta.icon('fa5s.user-circle', color='#A0AEC0').pixmap(72, 72))
        avatar_lbl.setStyleSheet("background: transparent; border: none;")
        avatar_lbl.setFixedSize(72, 72)
        
        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        self.prev_nama = QLabel("Belum Dipilih")
        self.prev_nama.setStyleSheet("color: #2D3748; font-size: 22px; font-weight: 800; background: transparent; border: none;")
        self.prev_rm = QLabel("Pilih pasien untuk melihat identitas")
        self.prev_rm.setStyleSheet("color: #718096; font-size: 14px; background: transparent; border: none;")
        name_col.addWidget(self.prev_nama)
        name_col.addWidget(self.prev_rm)
        name_col.addStretch()
        
        prof_layout.addWidget(avatar_lbl)
        prof_layout.addLayout(name_col)
        prof_layout.addStretch()
        identity_layout.addLayout(prof_layout)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #E2E8F0; background-color: #E2E8F0; border: none; max-height: 1px;")
        identity_layout.addWidget(sep)

        # Details Grid (2x2)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        def _make_grid_item(icon_name, label, value_attr, row, col):
            wrap = QFrame()
            wrap.setStyleSheet("background-color: #F7FAFC; border-radius: 10px; border: 1px solid #EDF2F7;")
            l = QHBoxLayout(wrap)
            l.setContentsMargins(16, 16, 16, 16)
            l.setSpacing(14)
            
            ic = QLabel()
            ic.setPixmap(qta.icon(icon_name, color='#00B4DB').pixmap(22, 22))
            ic.setStyleSheet("background: transparent; border: none;")
            
            text_col = QVBoxLayout()
            text_col.setSpacing(4)
            lbl_title = QLabel(label)
            lbl_title.setStyleSheet("color: #718096; font-size: 12px; background: transparent; border: none;")
            val = QLabel("-")
            val.setStyleSheet("color: #2D3748; font-size: 16px; font-weight: 700; background: transparent; border: none;")
            setattr(self, value_attr, val)
            
            text_col.addWidget(lbl_title)
            text_col.addWidget(val)
            l.addWidget(ic)
            l.addLayout(text_col)
            l.addStretch()
            
            grid_layout.addWidget(wrap, row, col)

        _make_grid_item('fa5s.venus-mars', 'Jenis Kelamin', 'prev_jk', 0, 0)
        _make_grid_item('fa5s.birthday-cake', 'Usia', 'prev_usia', 0, 1)
        _make_grid_item('fa5s.weight', 'Berat Badan (kg)', 'prev_bb', 1, 0)
        _make_grid_item('fa5s.ruler-vertical', 'Tinggi Badan (cm)', 'prev_tb', 1, 1)
        
        identity_layout.addLayout(grid_layout)
        identity_layout.addSpacing(10)

        # Tombol Mulai
        self.btn_enter_session = QPushButton("  Mulai")
        self.btn_enter_session.setIcon(qta.icon('fa5s.play', color='#90A4AE'))
        self.btn_enter_session.setIconSize(QSize(18, 18))
        self.btn_enter_session.setFixedHeight(56)
        self.btn_enter_session.setCursor(Qt.PointingHandCursor)
        self.btn_enter_session.setStyleSheet("""
            QPushButton {
                background-color: #EDF2F7; color: #A0AEC0; font-weight: bold; font-size: 16px;
                border-radius: 10px; border: 1px solid #E2E8F0;
            }
        """)
        self.btn_enter_session.setEnabled(False)
        self.btn_enter_session.clicked.connect(self.enter_active_session)
        identity_layout.addWidget(self.btn_enter_session)

        right_col.addWidget(identity_card)
        right_col.addStretch()

        main_layout.addLayout(left_col, stretch=4)
        main_layout.addLayout(right_col, stretch=5)
        
        pre_root.addLayout(main_layout)

        # Connect validasi & finalize
        self.cmb_pasien_session.currentTextChanged.connect(self.validate_session_start)
        self._clear_patient_preview()
        self.session_stacked.addWidget(self.page_pre_session)

        # ==========================================
        # SUB-PAGE 1: ACTIVE SESSION (Monitoring)
        # ==========================================

        self.page_active_session = QWidget()
        active_layout = QVBoxLayout(self.page_active_session)
        active_layout.setContentsMargins(15, 8, 15, 8)
        active_layout.setSpacing(6)
        
        # --- 1. KONTROL ATAS (KEMBALI & STATUS) ---
        kontrol_row = QHBoxLayout()
        
        btn_back = QPushButton(" Kembali")
        btn_back.setIcon(qta.icon('fa5s.arrow-left', color='#718096'))
        btn_back.setStyleSheet("""
            QPushButton { 
                background-color: #FFFFFF; 
                color: #718096; 
                font-weight: bold; 
                border: 1px solid #E2E8F0; 
                border-radius: 6px; 
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #F7FAFC; color: #2D3748; }
        """)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.exit_active_session)
        
        self.status_panel = QFrame()
        self.status_panel.setStyleSheet("border: 1px solid #E2E8F0; background-color: #F7FAFC; border-radius: 6px;")
        
        status_layout = QHBoxLayout(self.status_panel)
        status_layout.setContentsMargins(12, 6, 12, 6)
        status_layout.setSpacing(8)
        
        self.lbl_record_dot = QFrame()
        self.lbl_record_dot.setFixedSize(10, 10)
        self.lbl_record_dot.setStyleSheet("background-color: transparent; border-radius: 5px; border: none;")
        
        self.lbl_status_sesi = QLabel("Sesi Belum Dimulai")
        self.lbl_status_sesi.setStyleSheet("color: #718096; font-weight: bold; font-size: 12px; border: none; background: transparent;")
        
        status_layout.addWidget(self.lbl_record_dot)
        status_layout.addWidget(self.lbl_status_sesi)
        
        kontrol_row.addWidget(btn_back)
        kontrol_row.addStretch()
        kontrol_row.addWidget(self.status_panel)
        
        active_layout.addLayout(kontrol_row)
        
        # --- 2. HEADER PANEL & INFO PASIEN ---
        header_row = QHBoxLayout()
        header_row.setSpacing(15)
        
        info_panel = QFrame()
        info_panel.setFixedHeight(85)
        info_panel.setGraphicsEffect(create_shadow())
        info_panel.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0;")
        info_layout = QHBoxLayout(info_panel)
        info_layout.setContentsMargins(20, 10, 20, 10)
        
        icon_patient = QLabel()
        icon_patient.setPixmap(qta.icon('fa5s.user', color='#A0AEC0').pixmap(30, 30))
        icon_patient.setStyleSheet("border: none; background: transparent;")
        
        patient_details = QVBoxLayout()
        patient_details.setSpacing(2)
        
        self.lbl_info_nama = QLabel("Belum ada pasien dipilih")
        self.lbl_info_nama.setStyleSheet("color: #2D3748; font-size: 18px; font-weight: 800; border: none; background: transparent;")
        
        info_sub = QHBoxLayout()
        self.lbl_info_rm = QLabel("RM: -")
        self.lbl_info_usia = QLabel("Usia: -")
        self.lbl_info_gender = QLabel("Gender: -")
        
        for lbl in [self.lbl_info_rm, self.lbl_info_usia, self.lbl_info_gender]:
            lbl.setStyleSheet("color: #718096; font-size: 13px; border: none; background: transparent; padding-right: 15px;")
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
        dev_panel.setFixedHeight(85)
        dev_panel.setGraphicsEffect(create_shadow())
        dev_panel.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0;")
        dev_layout = QHBoxLayout(dev_panel)
        dev_layout.setContentsMargins(20, 10, 20, 10)
        
        self.lbl_bluetooth = QLabel("Belum Terhubung")
        self.lbl_bluetooth.setStyleSheet("color: #A0AEC0; font-weight: bold; font-size: 14px; border: none; background: transparent;")
        self.icon_bluetooth = QLabel()
        self.icon_bluetooth.setPixmap(qta.icon('fa5b.bluetooth', color='#A0AEC0').pixmap(24, 24))
        self.icon_bluetooth.setStyleSheet("border: none; background: transparent;")
        
        self.btn_connect = QPushButton(" Hubungkan")
        self.btn_connect.setIcon(qta.icon('fa5s.link', color='#FFFFFF'))
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #3182CE; 
                color: #FFFFFF; 
                border-radius: 6px; 
                padding: 8px 16px; 
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover { background-color: #2B6CB0; }
        """)
        self.btn_connect.setCursor(Qt.PointingHandCursor)
        
        dev_layout.addWidget(self.icon_bluetooth)
        dev_layout.addWidget(self.lbl_bluetooth)
        dev_layout.addStretch()
        dev_layout.addWidget(self.btn_connect)
        
        header_row.addWidget(info_panel, stretch=2)
        header_row.addWidget(dev_panel, stretch=1)
        
        # --- 3. SENSOR & GRAFIK ROWS ---
        main_content = QVBoxLayout()
        main_content.setSpacing(6)
        
        pg.setConfigOption('background', 'transparent')
        pg.setConfigOption('foreground', '#718096')
        
        import numpy as np
        self.x_data = np.linspace(0, 10, 300)
        self.phase = 0.0
        self.y_data_hr = np.zeros(300)
        self.y_data_gsr = np.zeros(300)
        self.y_data_temp = np.zeros(300)
        
        def create_row_card(title_text, unit_text, color, icon_name, y_data):
            row_frame = QFrame()
            row_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            row_frame.setGraphicsEffect(create_shadow())
            row_frame.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0;")
            
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(15, 2, 15, 2)
            
            plot = pg.PlotWidget()
            plot.getAxis('left').setPen('#CBD5E0')
            plot.getAxis('bottom').setPen('#CBD5E0')
            plot.showGrid(x=True, y=True, alpha=0.15)
            curve = plot.plot(self.x_data, y_data, pen=pg.mkPen(color=color, width=2.5))
            
            val_panel = QFrame()
            val_panel.setStyleSheet("border: none; background: transparent;")
            val_panel.setFixedWidth(160)
            v_layout = QVBoxLayout(val_panel)
            v_layout.setContentsMargins(2, 0, 2, 0)
            v_layout.setAlignment(Qt.AlignCenter)
            
            top_h = QHBoxLayout()
            top_h.setSpacing(4)
            icon_lbl = QLabel()
            icon_lbl.setPixmap(qta.icon(icon_name, color=color).pixmap(24, 24))
            top_h.addWidget(icon_lbl)
            lbl_title = QLabel(title_text)
            lbl_title.setStyleSheet("color: #718096; font-size: 12px; font-weight: bold;")
            top_h.addWidget(lbl_title)
            top_h.addStretch()
            v_layout.addLayout(top_h)
            
            val_lbl = QLabel("--")
            val_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            val_lbl.setStyleSheet(f"color: {color}; font-size: 42px; font-weight: 900;")
            
            unit_lbl = QLabel(unit_text)
            unit_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            unit_lbl.setStyleSheet("color: #A0AEC0; font-size: 14px; font-weight: bold;")
            
            v_layout.addWidget(val_lbl)
            v_layout.addWidget(unit_lbl)
            
            row_layout.addWidget(plot, stretch=4)
            
            sep = QFrame()
            sep.setFrameShape(QFrame.VLine)
            sep.setStyleSheet("color: #E2E8F0;")
            row_layout.addWidget(sep)
            
            row_layout.addWidget(val_panel)
            
            return row_frame, curve, val_lbl
            
        self.row_hr, self.curve_hr, self.lbl_val_hr = create_row_card("HEART RATE", "BPM", "#FF5252", "fa5s.heartbeat", self.y_data_hr)
        self.row_gsr, self.curve_gsr, self.lbl_val_gsr = create_row_card("SKIN CONDUCTANCE", "µS", "#40C4FF", "fa5s.bolt", self.y_data_gsr)
        self.row_temp, self.curve_temp, self.lbl_val_temp = create_row_card("SKIN TEMPERATURE", "°C", "#FFB300", "fa5s.thermometer-half", self.y_data_temp)
        
        main_content.addWidget(self.row_hr, stretch=1)
        main_content.addWidget(self.row_gsr, stretch=1)
        main_content.addWidget(self.row_temp, stretch=1)
        
        active_layout.addLayout(header_row)
        active_layout.addLayout(main_content, stretch=1)
        
        self.session_stacked.addWidget(self.page_active_session)
        self.session_stacked.setCurrentIndex(0)
        
        self.timer_graph = QTimer(self)
        self.timer_graph.timeout.connect(self.update_fake_graph)
        self.is_recording = False



    def toggle_session_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.timer_graph.start(50)
            self.lbl_status_sesi.setText("Recording")
            self.lbl_status_sesi.setStyleSheet("color: #FF0000; font-weight: bold; font-size: 12px; border: none; background: transparent;")
            self.status_panel.setStyleSheet("border: 1px solid #FED7D7; background-color: #FFF5F5; border-radius: 6px;")
            self.is_dot_visible = True
            self.lbl_record_dot.setStyleSheet("background-color: #FF0000; border-radius: 5px; border: none;")
            self.blink_counter = 0
            self.lbl_bluetooth.setText("Alat Terhubung")
            self.lbl_bluetooth.setStyleSheet("color: #00E676; font-weight: bold; font-size: 15px; border: none; background: transparent;")
            self.icon_bluetooth.setPixmap(qta.icon('fa5b.bluetooth', color='#00E676').pixmap(24, 24))
            
            self.btn_connect.setText(" Putuskan")
            self.btn_connect.setIcon(qta.icon('fa5s.unlink', color='#4A5568'))
            self.btn_connect.setStyleSheet("""
                QPushButton {
                    background-color: #E2E8F0; 
                    color: #4A5568; 
                    border-radius: 6px; 
                    padding: 8px 16px; 
                    font-weight: bold;
                    font-size: 13px;
                    border: none;
                }
                QPushButton:hover { background-color: #CBD5E0; }
            """)

    def stop_session_recording(self):
        self.is_recording = False
        self.timer_graph.stop()
        self.lbl_status_sesi.setText("Sesi Selesai")
        self.lbl_status_sesi.setStyleSheet("color: #718096; font-weight: bold; font-size: 12px; border: none; background: transparent;")
        self.status_panel.setStyleSheet("border: 1px solid #E2E8F0; background-color: #F7FAFC; border-radius: 6px;")
        self.lbl_record_dot.setStyleSheet("background-color: transparent; border-radius: 5px; border: none;")
        
        # Reset data for next session
        import numpy as np
        self.y_data_hr = np.zeros(300)
        self.y_data_gsr = np.zeros(300)
        self.y_data_temp = np.zeros(300)
        self.curve_hr.setData(self.x_data, self.y_data_hr)
        self.curve_gsr.setData(self.x_data, self.y_data_gsr)
        self.curve_temp.setData(self.x_data, self.y_data_temp)
        self.lbl_val_hr.setText("--")
        self.lbl_val_gsr.setText("--")
        self.lbl_val_temp.setText("--")
        self.lbl_bluetooth.setText("Belum Terhubung")
        self.lbl_bluetooth.setStyleSheet("color: #A0AEC0; font-weight: bold; font-size: 14px; border: none; background: transparent;")
        self.icon_bluetooth.setPixmap(qta.icon('fa5b.bluetooth', color='#A0AEC0').pixmap(24, 24))
        
        self.btn_connect.setText(" Hubungkan")
        self.btn_connect.setIcon(qta.icon('fa5s.link', color='#FFFFFF'))
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #3182CE; 
                color: #FFFFFF; 
                border-radius: 6px; 
                padding: 8px 16px; 
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover { background-color: #2B6CB0; }
        """)

    def update_fake_graph(self):
        import numpy as np
        
        self.blink_counter += 1
        if self.blink_counter % 10 == 0:
            if getattr(self, 'is_dot_visible', False):
                self.lbl_record_dot.setStyleSheet("background-color: transparent; border-radius: 5px; border: none;")
                self.is_dot_visible = False
            else:
                self.lbl_record_dot.setStyleSheet("background-color: #FF0000; border-radius: 5px; border: none;")
                self.is_dot_visible = True
            
        self.phase += 0.2
        # Geser gelombang agar beranimasi
        self.y_data_hr[:-1] = self.y_data_hr[1:]
        val_hr = np.sin(self.x_data[-1] * 5 + self.phase) * 10 + 80 + np.random.normal(0, 1)
        self.y_data_hr[-1] = val_hr
        
        self.y_data_gsr[:-1] = self.y_data_gsr[1:]
        val_gsr = np.sin(self.x_data[-1] + self.phase) * 5 + 15 + np.random.normal(0, 0.2)
        self.y_data_gsr[-1] = val_gsr
        
        self.y_data_temp[:-1] = self.y_data_temp[1:]
        val_temp = 36.5 + np.random.normal(0, 0.05)
        self.y_data_temp[-1] = val_temp
        
        self.curve_hr.setData(self.x_data, self.y_data_hr)
        self.curve_gsr.setData(self.x_data, self.y_data_gsr)
        self.curve_temp.setData(self.x_data, self.y_data_temp)
        
        # Update Labels
        self.lbl_val_hr.setText(f"{int(val_hr)}")
        self.lbl_val_gsr.setText(f"{val_gsr:.1f}")
        self.lbl_val_temp.setText(f"{val_temp:.1f}")





