import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                               QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect, QStackedWidget, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem)
from PySide6.QtCore import Qt, QTimer, QTime, QSize
from PySide6.QtGui import QColor, QIcon, QPixmap
import os
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
        
        logo_container = QFrame()
        logo_container.setFixedHeight(80)
        logo_container.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; margin-left: 20px; margin-right: 20px;")
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(5, 2, 5, 2)

        title = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "images", "Logo_Text.jpeg")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Skala gambar dengan tinggi maksimal lebih kecil (65) agar tidak ada ruang kosong berlebih di atas/bawah
            pixmap = pixmap.scaled(200, 65, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            title.setPixmap(pixmap)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background: transparent; border: none; margin: 0px;")
        logo_layout.addWidget(title)
        
        self.btn_dashboard = QPushButton(" Dashboard")
        self.btn_dashboard.setIcon(qta.icon('fa5s.chart-pie', color='#FFFFFF'))
        self.btn_dashboard.setIconSize(QSize(20, 20))
        
        self.btn_pasien = QPushButton(" Patients")
        self.btn_pasien.setIcon(qta.icon('fa5s.users', color='#FFFFFF'))
        self.btn_pasien.setIconSize(QSize(20, 20))
        
        self.btn_session = QPushButton(" New Session")
        self.btn_session.setIcon(qta.icon('fa5s.heartbeat', color='#FFFFFF'))
        self.btn_session.setIconSize(QSize(20, 20))
        
        self.btn_report = QPushButton(" History")
        self.btn_report.setIcon(qta.icon('fa5s.file-medical-alt', color='#FFFFFF'))
        self.btn_report.setIconSize(QSize(20, 20))

        self.btn_help = QPushButton(" Help")
        self.btn_help.setIcon(qta.icon('fa5s.question-circle', color='#FFFFFF'))
        self.btn_help.setIconSize(QSize(20, 20))
        
        self.btn_settings = QPushButton(" Settings")
        self.btn_settings.setIcon(qta.icon('fa5s.cog', color='#FFFFFF'))
        self.btn_settings.setIconSize(QSize(20, 20))
        
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
        self.btn_pasien.clicked.connect(lambda: self.switch_page(1))
        self.btn_session.clicked.connect(lambda: self.switch_page(2))
        self.btn_report.clicked.connect(lambda: self.switch_page(3))
        self.btn_help.clicked.connect(lambda: self.switch_page(4))
        self.btn_settings.clicked.connect(lambda: self.switch_page(5))
        
        sidebar_layout.addWidget(logo_container)
        sidebar_layout.addSpacing(30)
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_pasien)
        sidebar_layout.addWidget(self.btn_session)
        sidebar_layout.addWidget(self.btn_report)
        sidebar_layout.addWidget(self.btn_help)
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addStretch()

        # Tombol Logout
        btn_logout = QPushButton(" Logout")
        btn_logout.setIcon(qta.icon('fa5s.sign-out-alt', color='white'))
        btn_logout.setIconSize(QSize(16, 16))
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                font-weight: bold;
                font-size: 13px;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                padding: 10px 16px;
                margin: 0 16px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
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
        
        from views.dashboard_view import DashboardView
        self.page_dashboard = DashboardView()
        
        from views.patient_view import PatientView
        from controllers.patient_controller import PatientController
        
        self.page_dashboard = DashboardView()
        self.page_pasien = PatientView()
        self.patient_ctrl = PatientController(self.page_pasien, self)
        
        self.page_live_session = QWidget()
        self.setup_live_session_page()
        
        from views.report_view import ReportView
        from controllers.report_controller import ReportController
        from views.help_view import HelpView
        from views.settings_view import SettingsView
        
        self.page_report = ReportView()
        self.report_ctrl = ReportController(self.page_report, self)

        self.page_help = HelpView()
        self.page_settings = SettingsView()
        
        self.stacked_widget.addWidget(self.page_dashboard)    # 0
        self.stacked_widget.addWidget(self.page_pasien)       # 1
        self.stacked_widget.addWidget(self.page_live_session) # 2
        self.stacked_widget.addWidget(self.page_report)       # 3
        self.stacked_widget.addWidget(self.page_help)         # 4
        self.stacked_widget.addWidget(self.page_settings)     # 5
        
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
        
        # Auto-refresh dashboard jika dibuka
        if index == 0 and hasattr(self, 'page_dashboard'):
            self.page_dashboard.refresh_dashboard()
        
        # Tampilkan sidebar dan topbar
        self.sidebar.show()
        self.top_bar.show()
        
        buttons = [self.btn_dashboard, self.btn_pasien, self.btn_session, self.btn_report, self.btn_help, self.btn_settings]
        for btn in buttons:
            btn.setObjectName("MenuButton")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
        if 0 <= index < len(buttons):
            buttons[index].setObjectName("MenuButtonActive")
            buttons[index].style().unpolish(buttons[index])
            buttons[index].style().polish(buttons[index])

    def start_examination(self, patient, umur):
        self.lbl_info_rm.setText(f"ID: {patient.no_rm}")
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

        if is_valid:
            self.btn_enter_session.setIcon(qta.icon('fa5s.play', color='#FFFFFF'))
            self.btn_enter_session.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F97D1, stop:1 #5C9EDA);
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border-radius: 6px;
                    border: none;
                    padding: 0 20px;
                    letter-spacing: 0.5px;
                }
                QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5C9EDA, stop:1 #75B0E1); }
            """)
            # Update preview kartu pasien
            self._refresh_patient_preview(text)
        else:
            self.btn_enter_session.setIcon(qta.icon('fa5s.play', color='#A0AEC0'))
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
            gender_full = "Male" if p.gender in ["L", "M"] else "Female"
            usia_str = "-"
            if p.date_of_birth:
                today = date.today()
                age = today.year - p.date_of_birth.year - (
                    (today.month, today.day) < (p.date_of_birth.month, p.date_of_birth.day)
                )
                usia_str = f"{age} Tahun"

            self.prev_nama.setText(p.full_name)
            self.prev_rm.setText(f"ID: {p.no_rm}")
            self.prev_jk.setText(gender_full)
            self.prev_usia.setText(usia_str)
            bb_str = f"{p.weight} kg" if p.weight else "-"
            tb_str = f"{p.height} cm" if p.height else "-"
            self.prev_bb.setText(bb_str)
            self.prev_tb.setText(tb_str)

    def _clear_patient_preview(self):
        if not hasattr(self, 'prev_nama'):
            return
        self.prev_nama.setText("Not Selected")
        self.prev_rm.setText("ID: -")
        for attr in ['prev_jk', 'prev_usia', 'prev_bb', 'prev_tb']:
            if hasattr(self, attr):
                getattr(self, attr).setText("-")


    def enter_active_session(self):
        teks_pasien = self.cmb_pasien_session.currentText()
        is_valid = " - " in teks_pasien and len(teks_pasien) > 5
        
        if not is_valid:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, 
                "Attention",
                "Please select a patient from the list before starting the session.\n\nIf the patient is not registered yet, click the 'Register Patient' button.",
                QMessageBox.Ok
            )
            return

        rm_pasien = teks_pasien.split(" - ")[0] if " - " in teks_pasien else "-"
        nama_pasien = teks_pasien.split(" - ")[-1] if " - " in teks_pasien else teks_pasien
        usia_pasien = "-"
        gender_pasien = "-"

        if rm_pasien != "-":
            session = SessionLocal()
            p = session.query(Patient).filter(Patient.no_rm == rm_pasien).first()
            if p:
                nama_pasien = p.full_name
                gender_pasien = "Male" if p.gender in ["L", "M"] else "Female"
                if p.date_of_birth:
                    today = date.today()
                    age = today.year - p.date_of_birth.year - (
                        (today.month, today.day) < (p.date_of_birth.month, p.date_of_birth.day)
                    )
                    usia_pasien = f"{age} Tahun"
            session.close()

        self.lbl_info_rm.setText(f"ID: {rm_pasien}")
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
        
        self.cmb_pasien_session.blockSignals(True)
        self.cmb_pasien_session.clear()
        for p in patients:
            self.cmb_pasien_session.addItem(f"{p.no_rm} - {p.full_name}")
            
        if completer:
            completer.setModel(self.cmb_pasien_session.model())
            
        self.cmb_pasien_session.setCurrentIndex(-1)
        self.cmb_pasien_session.lineEdit().clear()
        self.cmb_pasien_session.blockSignals(False)
        
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
        sec_title = QLabel("Session Preparation")
        sec_title.setStyleSheet("""
            color: #002C6F;
            font-size: 24px;
            font-weight: 800;
            background: transparent;
        """)
        sec_sub = QLabel("Select a patient, verify identity data, then start the session.")
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
        self.cmb_pasien_session.lineEdit().setPlaceholderText("Type patient name or ID here...")
        self.cmb_pasien_session.setFixedHeight(54)
        self.cmb_pasien_session.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF; border: 2px solid #E2E8F0; border-radius: 12px;
                color: #002C6F; font-size: 15px; padding-left: 16px;
            }
            QComboBox:focus { border: 2px solid #5C9EDA; background-color: #FFFFFF; }
            QComboBox::drop-down { width: 40px; border: none; }
            QComboBox::down-arrow { image: none; width: 0; }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF; color: #002C6F; border: 1px solid #E2E8F0; border-radius: 8px;
                selection-background-color: #EBF8FA; selection-color: #5C9EDA; font-size: 14px; padding: 6px; outline: none;
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
        btn_tambah_ps = QPushButton("  Register Patient")
        btn_tambah_ps.setIcon(qta.icon('fa5s.plus', color='#5C9EDA'))
        btn_tambah_ps.setFixedHeight(46)
        btn_tambah_ps.setStyleSheet("""
            QPushButton {
                background-color: #F7FAFC; color: #002C6F; font-weight: 700; font-size: 14px;
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
        avatar_lbl.setPixmap(qta.icon('fa5s.user-circle', color='#A0AEC0').pixmap(64, 64))
        avatar_lbl.setStyleSheet("background: transparent; border: none;")
        avatar_lbl.setFixedSize(64, 64)
        
        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        self.prev_nama = QLabel("Not Selected")
        self.prev_nama.setStyleSheet("color: #002C6F; font-size: 20px; font-weight: bold; background: transparent; border: none;")
        self.prev_rm = QLabel("ID: -")
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
        grid_layout.setSpacing(15)

        def _make_grid_item(label, value_attr, row, col):
            wrap = QFrame()
            wrap.setStyleSheet("background-color: #F7FAFC; border: 1px solid #E2E8F0; border-radius: 6px;")
            l = QVBoxLayout(wrap)
            l.setContentsMargins(12, 12, 12, 12)
            l.setSpacing(4)
            
            lbl_title = QLabel(label)
            lbl_title.setStyleSheet("color: #718096; font-size: 12px; font-weight: bold; background: transparent; border: none;")
            val = QLabel("-")
            val.setStyleSheet("color: #002C6F; font-size: 15px; font-weight: normal; background: transparent; border: none;")
            setattr(self, value_attr, val)
            
            l.addWidget(lbl_title)
            l.addWidget(val)
            
            grid_layout.addWidget(wrap, row, col)

        _make_grid_item('Gender', 'prev_jk', 0, 0)
        _make_grid_item('Age', 'prev_usia', 0, 1)
        _make_grid_item('Weight (kg)', 'prev_bb', 1, 0)
        _make_grid_item('Height (cm)', 'prev_tb', 1, 1)
        
        identity_layout.addLayout(grid_layout)
        identity_layout.addSpacing(10)

        # Tombol Mulai
        self.btn_enter_session = QPushButton("  Start")
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
            QPushButton:hover { background-color: #F7FAFC; color: #002C6F; }
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
        self.lbl_info_nama.setStyleSheet("color: #002C6F; font-size: 18px; font-weight: 800; border: none; background: transparent;")
        
        info_sub = QHBoxLayout()
        self.lbl_info_rm = QLabel("ID: -")
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
        dev_layout.setContentsMargins(20, 15, 20, 15)
        dev_layout.setSpacing(15)
        
        self.lbl_bluetooth = QLabel("Not Connected")
        self.lbl_bluetooth.setStyleSheet("color: #1E3F76; font-size: 16px; font-weight: bold; background: transparent; border: none;")
        
        self.btn_connect = QPushButton(" Connect")
        self.btn_connect.setIcon(qta.icon('fa5s.link', color='#FFFFFF'))
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #3182CE; 
                color: #FFFFFF; 
                border-radius: 4px; 
                padding: 8px 16px; 
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover { background-color: #2B6CB0; }
        """)
        self.btn_connect.setCursor(Qt.PointingHandCursor)
        
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
            if not self.is_connected:
                self.is_connected = True
                self.lbl_bluetooth.setText("Connected")
                self.lbl_bluetooth.setStyleSheet("color: #00E676; font-size: 16px; font-weight: bold; background: transparent; border: none;")
                self.btn_connect.setText(" Disconnect")
                self.btn_connect.setIcon(qta.icon('fa5s.unlink', color='#1E3F76'))
                self.btn_connect.setStyleSheet("""
                    QPushButton {
                        background-color: #EDF2F7; 
                        color: #1E3F76; 
                        border-radius: 4px; 
                        padding: 8px 16px; 
                        font-weight: bold;
                        font-size: 13px;
                        border: none;
                    }
                    QPushButton:hover { background-color: #E2E8F0; }
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
        self.lbl_bluetooth.setText("Not Connected")
        self.lbl_bluetooth.setStyleSheet("color: #1E3F76; font-size: 16px; font-weight: bold; background: transparent; border: none;")
        
        self.btn_connect.setText(" Connect")
        self.btn_connect.setIcon(qta.icon('fa5s.link', color='#FFFFFF'))
        self.btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #3182CE; 
                color: #FFFFFF; 
                border-radius: 4px; 
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





