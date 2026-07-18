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
        
        self.btn_pasien.clicked.connect(lambda: self.switch_page(0))
        self.btn_session.clicked.connect(lambda: self.switch_page(1))
        self.btn_report.clicked.connect(lambda: self.switch_page(2))
        
        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(30)
        sidebar_layout.addWidget(self.btn_pasien)
        sidebar_layout.addWidget(self.btn_session)
        sidebar_layout.addWidget(self.btn_report)
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
        
        self.page_report = ReportView()
        self.report_ctrl = ReportController(self.page_report, self)
        
        self.stacked_widget.addWidget(self.page_pasien)       # 0
        self.stacked_widget.addWidget(self.page_live_session) # 1
        self.stacked_widget.addWidget(self.page_report)       # 2
        
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
        
        buttons = [self.btn_pasien, self.btn_session, self.btn_report]
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
            QHeaderView, QCompleter, QSplitter
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
        pre_root.setSpacing(0)



        # --- KONTEN UTAMA (Scrollable) ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical {
                background: #F7FAFC; width: 8px; border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E0; border-radius: 4px; min-height: 40px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(28, 24, 28, 24)
        scroll_layout.setSpacing(20)

        # --- SECTION TITLE ---
        sec_title = QLabel("Persiapan Sesi Pemeriksaan")
        sec_title.setStyleSheet("""
            color: #2D3748;
            font-size: 22px;
            font-weight: 800;
            background: transparent;
        """)
        sec_sub = QLabel("Pilih pasien yang akan diperiksa, periksa data identitas, lalu mulai sesi pemantauan fisiologis.")
        sec_sub.setStyleSheet("color: #718096; font-size: 13px; background: transparent;")
        scroll_layout.addWidget(sec_title)
        scroll_layout.addWidget(sec_sub)

        # --- PANEL UTAMA: 2 kolom (Kiri: Pencarian, Kanan: Preview) ---
        main_row = QHBoxLayout()
        main_row.setSpacing(20)

        # ---- KOLOM KIRI: Pencarian & Pemilihan Pasien ----
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
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
        lbl_search_icon.setPixmap(qta.icon('fa5s.user-injured', color='#00B4DB').pixmap(20, 20))
        lbl_search_icon.setStyleSheet("background: transparent; border: none;")
        lbl_left_title = QLabel("Pencarian Pasien")
        lbl_left_title.setStyleSheet("color: #2D3748; font-size: 15px; font-weight: 700; background: transparent; border: none;")
        btn_tambah_ps = QPushButton("  + Pasien Baru")
        btn_tambah_ps.setStyleSheet("""
            QPushButton {
                background-color: #F7FAFC;
                color: #2D3748;
                font-weight: 700;
                font-size: 12px;
                border-radius: 5px;
                border: 1.5px solid #E2E8F0;
                padding: 5px 12px;
            }
            QPushButton:hover { background-color: #E2E8F0; }
        """)
        btn_tambah_ps.setCursor(Qt.PointingHandCursor)
        btn_tambah_ps.clicked.connect(self.patient_ctrl.show_add_patient_dialog)
        left_hdr.addWidget(lbl_search_icon)
        left_hdr.addWidget(lbl_left_title)
        left_hdr.addStretch()
        left_hdr.addWidget(btn_tambah_ps)
        left_panel_layout.addLayout(left_hdr)

        # Garis separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("color: #E2E8F0; background-color: #E2E8F0; border: none; max-height: 1px;")
        left_panel_layout.addWidget(sep1)

        # Search bar
        lbl_cari = QLabel("Cari Pasien (Nama / No. Rekam Medis):")
        lbl_cari.setStyleSheet("color: #4A5568; font-size: 12px; font-weight: 600; background: transparent; border: none;")
        left_panel_layout.addWidget(lbl_cari)

        search_row = QHBoxLayout()
        search_row.setSpacing(0)

        search_icon_lbl = QLabel()
        search_icon_lbl.setPixmap(qta.icon('fa5s.search', color='#A0AEC0').pixmap(16, 16))
        search_icon_lbl.setFixedSize(40, 42)
        search_icon_lbl.setAlignment(Qt.AlignCenter)
        search_icon_lbl.setStyleSheet("""
            background-color: #F7FAFC;
            border: 1.5px solid #E2E8F0;
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
                background-color: #F7FAFC;
                border: 1.5px solid #E2E8F0;
                border-left: none;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                color: #2D3748;
                font-size: 13px;
                padding-left: 8px;
            }
            QComboBox:focus {
                border: 1.5px solid #00B4DB;
                border-left: none;
                background-color: #FFFFFF;
            }
            QComboBox::drop-down { width: 30px; border: none; }
            QComboBox::down-arrow { image: none; width: 0; }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #2D3748;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                selection-background-color: #EBF8FA;
                selection-color: #00B4DB;
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
        lbl_hint.setStyleSheet("color: #718096; font-size: 11px; background: transparent; border: none;")
        left_panel_layout.addWidget(lbl_hint)

        left_panel_layout.addStretch()

        # --- INFO STATUS ---
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #EDF2F7;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
            }
        """)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(14, 10, 14, 10)
        lbl_status_icon = QLabel()
        lbl_status_icon.setPixmap(qta.icon('fa5s.info-circle', color='#718096').pixmap(14, 14))
        lbl_status_icon.setStyleSheet("background: transparent; border: none;")
        lbl_status_text = QLabel("Silakan pilih pasien terlebih dahulu sebelum memulai sesi pemeriksaan.")
        lbl_status_text.setStyleSheet("color: #4A5568; font-size: 12px; background: transparent; border: none;")
        status_layout.addWidget(lbl_status_icon)
        status_layout.addSpacing(6)
        status_layout.addWidget(lbl_status_text)
        status_layout.addStretch()
        left_panel_layout.addWidget(status_frame)

        # ---- KOLOM KANAN: Preview Identitas Pasien ----
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
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
        lbl_prev_icon.setPixmap(qta.icon('fa5s.id-card', color='#00B4DB').pixmap(20, 20))
        lbl_prev_icon.setStyleSheet("background: transparent; border: none;")
        lbl_right_title = QLabel("Identitas Pasien")
        lbl_right_title.setStyleSheet("color: #2D3748; font-size: 15px; font-weight: 700; background: transparent; border: none;")
        right_hdr.addWidget(lbl_prev_icon)
        right_hdr.addWidget(lbl_right_title)
        right_hdr.addStretch()
        right_panel_layout.addLayout(right_hdr)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("color: #E2E8F0; background-color: #E2E8F0; border: none; max-height: 1px;")
        right_panel_layout.addWidget(sep2)

        # Kartu avatar + nama pasien
        avatar_row = QHBoxLayout()
        avatar_row.setSpacing(14)
        avatar_lbl = QLabel()
        avatar_lbl.setPixmap(qta.icon('fa5s.user-circle', color='#A0AEC0').pixmap(52, 52))
        avatar_lbl.setStyleSheet("background: transparent; border: none;")
        avatar_lbl.setFixedSize(52, 52)

        name_col = QVBoxLayout()
        name_col.setSpacing(3)
        self.prev_nama = QLabel("Belum Dipilih")
        self.prev_nama.setStyleSheet("color: #2D3748; font-size: 16px; font-weight: 800; background: transparent; border: none;")
        self.prev_rm = QLabel("No. RM: -")
        self.prev_rm.setStyleSheet("color: #718096; font-size: 12px; background: transparent; border: none;")
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
            ic.setPixmap(qta.icon(icon_name, color='#00B4DB').pixmap(14, 14))
            ic.setStyleSheet("background: transparent; border: none;")
            ic.setFixedWidth(20)
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #718096; font-size: 12px; min-width: 100px; background: transparent; border: none;")
            val = QLabel("-")
            val.setStyleSheet("color: #2D3748; font-size: 12px; font-weight: 600; background: transparent; border: none;")
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
        sep3.setStyleSheet("color: #E2E8F0; background-color: #E2E8F0; border: none; max-height: 1px;")
        right_panel_layout.addWidget(sep3)

        # Tombol MULAI SESI
        self.btn_enter_session = QPushButton("  Mulai")
        self.btn_enter_session.setIcon(qta.icon('fa5s.play-circle', color='#90A4AE'))
        self.btn_enter_session.setIconSize(QSize(18, 18))
        self.btn_enter_session.setFixedHeight(46)
        self.btn_enter_session.setCursor(Qt.PointingHandCursor)
        self.btn_enter_session.setToolTip("Pilih pasien terlebih dahulu untuk mengaktifkan tombol ini")
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
        self.btn_enter_session.setEnabled(False)
        self.btn_enter_session.clicked.connect(self.enter_active_session)
        right_panel_layout.addWidget(self.btn_enter_session)

        right_panel_layout.addStretch()

        main_row.addWidget(left_panel, stretch=1)
        main_row.addWidget(right_panel)
        scroll_layout.addLayout(main_row)



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
        self.card_gsr, self.lbl_val_gsr = self.create_sensor_card("SKIN CONDUCTANCE", "--", "µS", "#40C4FF", "fa5s.bolt")
        self.card_temp, self.lbl_val_temp = self.create_sensor_card("SKIN TEMPERATURE", "--", "°C", "#FFB300", "fa5s.thermometer-half")
        
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
        
        btn_back = QPushButton(" Kembali")
        btn_back.setIcon(qta.icon('fa5s.arrow-left', color='#8C9EBA'))
        btn_back.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                color: #8C9EBA; 
                font-weight: bold; 
                border: 1px solid #1C3565; 
                border-radius: 6px; 
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #112A54; color: white; }
        """)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(lambda: self.session_stacked.setCurrentIndex(0))
        
        gl_title = QLabel("Real-time Data Monitor")
        gl_title.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 16px; border: none; background: transparent; margin-left: 10px;")
        
        self.lbl_status_sesi = QLabel(" Sesi Belum Dimulai ")
        self.lbl_status_sesi.setStyleSheet("color: #64748B; font-weight: bold; font-size: 12px; border: none; padding: 6px 12px; background-color: #051024; border-radius: 6px;")
        
        graph_header.addWidget(btn_back)
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
        self.curve_gsr = self.plot.plot(self.x_data, self.y_data_gsr, pen=pg.mkPen(color='#40C4FF', width=2.5), name="Skin Conductance")
        
        gl.addLayout(graph_header)
        gl.addSpacing(10)
        gl.addWidget(self.plot)
        
        main_content.addWidget(graph_panel, stretch=1)
        
        active_layout.addLayout(header_row)
        active_layout.addLayout(cards_layout)
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



