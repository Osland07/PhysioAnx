import sys
import hashlib
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect, QApplication
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QSize
from PySide6.QtGui import QColor, QFont, QPixmap, QIcon
import qtawesome as qta


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_shadow(blur=25, opacity=80, offset_y=6):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setColor(QColor(0, 0, 0, opacity))
    shadow.setOffset(0, offset_y)
    return shadow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PhysioAnx — Login")
        self.setMinimumSize(1000, 600)
        self.resize(1100, 660)
        self._logged_in_user = None
        self._build_ui()
        self._ensure_default_user()

    def _ensure_default_user(self):
        """Buat user admin default jika belum ada."""
        from models.database import SessionLocal
        from models.user import User
        session = SessionLocal()
        if not session.query(User).first():
            default = User(
                username="admin",
                password_hash=_hash_password("admin123"),
                full_name="Administrator",
                role="admin"
            )
            session.add(default)
            session.commit()
        session.close()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── KIRI: Banner / Branding ──────────────────────────────────
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #051024,
                    stop:1 #0A1F40
                );
            }
        """)
        left_panel.setFixedWidth(420)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(50, 60, 50, 60)
        left_layout.setSpacing(0)
        left_layout.setAlignment(Qt.AlignCenter)

        # Logo / ikon utama
        lbl_logo_icon = QLabel()
        lbl_logo_icon.setPixmap(qta.icon('fa5s.heartbeat', color='#40C4FF').pixmap(64, 64))
        lbl_logo_icon.setAlignment(Qt.AlignCenter)
        lbl_logo_icon.setStyleSheet("background: transparent; border: none;")

        lbl_app_name = QLabel("PhysioAnx")
        lbl_app_name.setAlignment(Qt.AlignCenter)
        lbl_app_name.setStyleSheet("""
            color: #FFFFFF;
            font-size: 36px;
            font-weight: 900;
            background: transparent;
            letter-spacing: 2px;
        """)

        lbl_tagline = QLabel("Sistem Pemantauan Fisiologis\nTingkat Kecemasan Pasien")
        lbl_tagline.setAlignment(Qt.AlignCenter)
        lbl_tagline.setWordWrap(True)
        lbl_tagline.setStyleSheet("""
            color: #8C9EBA;
            font-size: 14px;
            background: transparent;
            line-height: 1.6;
        """)

        # Divider dekoratif
        divider = QFrame()
        divider.setFixedSize(60, 3)
        divider.setStyleSheet("background-color: #40C4FF; border-radius: 2px;")
        divider_row = QHBoxLayout()
        divider_row.setAlignment(Qt.AlignCenter)
        divider_row.addWidget(divider)

        # Info card kecil di bawah
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255,255,255,0.04);
                border: 1px solid #1C3565;
                border-radius: 10px;
            }
        """)
        info_card_layout = QVBoxLayout(info_card)
        info_card_layout.setContentsMargins(20, 16, 20, 16)
        info_card_layout.setSpacing(10)

        def _feature_row(icon, text):
            row = QHBoxLayout()
            ic = QLabel()
            ic.setPixmap(qta.icon(icon, color='#40C4FF').pixmap(16, 16))
            ic.setStyleSheet("background: transparent; border: none;")
            ic.setFixedWidth(24)
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #8C9EBA; font-size: 12px; background: transparent; border: none;")
            row.addWidget(ic)
            row.addWidget(lbl)
            row.addStretch()
            return row

        info_card_layout.addLayout(_feature_row('fa5s.chart-line', 'Pemantauan sinyal GSR & BVP real-time'))
        info_card_layout.addLayout(_feature_row('fa5s.user-injured', 'Manajemen data rekam medis pasien'))
        info_card_layout.addLayout(_feature_row('fa5s.file-medical-alt', 'Ekspor laporan PDF otomatis'))

        lbl_version = QLabel("v1.0.0 — Prototype")
        lbl_version.setAlignment(Qt.AlignCenter)
        lbl_version.setStyleSheet("color: #2A4A7A; font-size: 11px; background: transparent;")

        left_layout.addStretch()
        left_layout.addWidget(lbl_logo_icon)
        left_layout.addSpacing(16)
        left_layout.addWidget(lbl_app_name)
        left_layout.addSpacing(12)
        left_layout.addLayout(divider_row)
        left_layout.addSpacing(16)
        left_layout.addWidget(lbl_tagline)
        left_layout.addSpacing(32)
        left_layout.addWidget(info_card)
        left_layout.addStretch()
        left_layout.addWidget(lbl_version)

        # ── KANAN: Form Login ────────────────────────────────────────
        right_panel = QFrame()
        right_panel.setStyleSheet("QFrame { background-color: #081B3B; }")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(70, 0, 70, 0)
        right_layout.setSpacing(0)
        right_layout.setAlignment(Qt.AlignCenter)

        # Card login
        card = QFrame()
        card.setFixedWidth(380)
        card.setStyleSheet("""
            QFrame {
                background-color: #0F2040;
                border: 1px solid #1C3565;
                border-radius: 16px;
            }
        """)
        card.setGraphicsEffect(create_shadow(blur=40, opacity=100, offset_y=10))
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(20)

        # Header form
        lbl_welcome = QLabel("Selamat Datang")
        lbl_welcome.setStyleSheet("""
            color: #FFFFFF;
            font-size: 24px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)
        lbl_sub = QLabel("Masuk ke sistem untuk melanjutkan")
        lbl_sub.setStyleSheet("color: #5C7AAA; font-size: 13px; background: transparent; border: none;")

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #1C3565; border: none; max-height: 1px;")

        # Input Username
        lbl_user = QLabel("Username")
        lbl_user.setStyleSheet("color: #8C9EBA; font-size: 12px; font-weight: 600; background: transparent; border: none;")

        user_row = QHBoxLayout()
        user_row.setSpacing(0)
        user_icon = QLabel()
        user_icon.setPixmap(qta.icon('fa5s.user', color='#5C7AAA').pixmap(15, 15))
        user_icon.setFixedSize(42, 44)
        user_icon.setAlignment(Qt.AlignCenter)
        user_icon.setStyleSheet("""
            background-color: #071733;
            border: 1.5px solid #1C3565;
            border-right: none;
            border-top-left-radius: 7px;
            border-bottom-left-radius: 7px;
        """)

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Masukkan username...")
        self.input_username.setFixedHeight(44)
        self.input_username.setStyleSheet("""
            QLineEdit {
                background-color: #071733;
                border: 1.5px solid #1C3565;
                border-left: none;
                border-top-right-radius: 7px;
                border-bottom-right-radius: 7px;
                color: #FFFFFF;
                font-size: 13px;
                padding: 0 12px;
            }
            QLineEdit:focus {
                border: 1.5px solid #40C4FF;
                border-left: none;
            }
        """)
        user_row.addWidget(user_icon)
        user_row.addWidget(self.input_username)

        # Input Password
        lbl_pass = QLabel("Password")
        lbl_pass.setStyleSheet("color: #8C9EBA; font-size: 12px; font-weight: 600; background: transparent; border: none;")

        pass_row = QHBoxLayout()
        pass_row.setSpacing(0)
        pass_icon = QLabel()
        pass_icon.setPixmap(qta.icon('fa5s.lock', color='#5C7AAA').pixmap(15, 15))
        pass_icon.setFixedSize(42, 44)
        pass_icon.setAlignment(Qt.AlignCenter)
        pass_icon.setStyleSheet("""
            background-color: #071733;
            border: 1.5px solid #1C3565;
            border-right: none;
            border-top-left-radius: 7px;
            border-bottom-left-radius: 7px;
        """)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Masukkan password...")
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setFixedHeight(44)
        self.input_password.setStyleSheet("""
            QLineEdit {
                background-color: #071733;
                border: 1.5px solid #1C3565;
                border-left: none;
                border-top-right-radius: 7px;
                border-bottom-right-radius: 7px;
                color: #FFFFFF;
                font-size: 13px;
                padding: 0 12px;
            }
            QLineEdit:focus {
                border: 1.5px solid #40C4FF;
                border-left: none;
            }
        """)
        # Toggle show/hide password
        self.btn_toggle_pass = QPushButton()
        self.btn_toggle_pass.setIcon(qta.icon('fa5s.eye', color='#5C7AAA'))
        self.btn_toggle_pass.setFixedSize(42, 44)
        self.btn_toggle_pass.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_pass.setCheckable(True)
        self.btn_toggle_pass.setStyleSheet("""
            QPushButton {
                background-color: #071733;
                border: 1.5px solid #1C3565;
                border-left: none;
                border-top-right-radius: 7px;
                border-bottom-right-radius: 7px;
            }
            QPushButton:checked { background-color: #0A1F40; }
        """)
        self.btn_toggle_pass.toggled.connect(self._toggle_password_visibility)
        # Re-style password row: icon | input | toggle
        self.input_password.setStyleSheet("""
            QLineEdit {
                background-color: #071733;
                border: 1.5px solid #1C3565;
                border-left: none;
                border-right: none;
                border-radius: 0px;
                color: #FFFFFF;
                font-size: 13px;
                padding: 0 12px;
            }
            QLineEdit:focus {
                border: 1.5px solid #40C4FF;
                border-left: none;
                border-right: none;
            }
        """)
        pass_row.addWidget(pass_icon)
        pass_row.addWidget(self.input_password)
        pass_row.addWidget(self.btn_toggle_pass)

        # Label error
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setFixedHeight(32)
        self.lbl_error.setStyleSheet("""
            QLabel {
                color: #FF5252;
                font-size: 12px;
                background-color: rgba(255,82,82,0.1);
                border: 1px solid rgba(255,82,82,0.3);
                border-radius: 5px;
                padding: 4px 8px;
            }
        """)
        self.lbl_error.hide()

        # Tombol Login
        self.btn_login = QPushButton("  Masuk")
        self.btn_login.setIcon(qta.icon('fa5s.sign-in-alt', color='white'))
        self.btn_login.setIconSize(QSize(16, 16))
        self.btn_login.setFixedHeight(48)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1565C0,
                    stop:1 #1976D2
                );
                color: #FFFFFF;
                font-weight: bold;
                font-size: 15px;
                border-radius: 8px;
                border: none;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1976D2,
                    stop:1 #2196F3
                );
            }
            QPushButton:pressed { background-color: #0D47A1; }
        """)
        self.btn_login.clicked.connect(self._do_login)

        # Info default user
        lbl_hint = QLabel("Default: admin / admin123")
        lbl_hint.setAlignment(Qt.AlignCenter)
        lbl_hint.setStyleSheet("color: #2A4A7A; font-size: 11px; background: transparent; border: none;")

        card_layout.addWidget(lbl_welcome)
        card_layout.addWidget(lbl_sub)
        card_layout.addWidget(sep)
        card_layout.addWidget(lbl_user)
        card_layout.addLayout(user_row)
        card_layout.addWidget(lbl_pass)
        card_layout.addLayout(pass_row)
        card_layout.addWidget(self.lbl_error)
        card_layout.addWidget(self.btn_login)
        card_layout.addWidget(lbl_hint)

        right_layout.addWidget(card, alignment=Qt.AlignCenter)

        # Pasang Enter key untuk login
        self.input_username.returnPressed.connect(self._do_login)
        self.input_password.returnPressed.connect(self._do_login)

        root.addWidget(left_panel)
        root.addWidget(right_panel, stretch=1)

    def _toggle_password_visibility(self, checked: bool):
        if checked:
            self.input_password.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_pass.setIcon(qta.icon('fa5s.eye-slash', color='#40C4FF'))
        else:
            self.input_password.setEchoMode(QLineEdit.Password)
            self.btn_toggle_pass.setIcon(qta.icon('fa5s.eye', color='#5C7AAA'))

    def _do_login(self):
        from models.database import SessionLocal
        from models.user import User

        username = self.input_username.text().strip()
        password = self.input_password.text()

        if not username or not password:
            self._show_error("Username dan password tidak boleh kosong.")
            return

        session = SessionLocal()
        user = session.query(User).filter(User.username == username).first()
        session.close()

        if user and user.password_hash == _hash_password(password):
            self._logged_in_user = user
            self.lbl_error.hide()
            self.accept_login()
        else:
            self._shake_card()
            self._show_error("Username atau password salah. Silakan coba lagi.")
            self.input_password.clear()

    def _show_error(self, msg: str):
        self.lbl_error.setText(msg)
        self.lbl_error.show()

    def _shake_card(self):
        """Efek getar ringan saat login gagal."""
        card = self.findChild(QFrame)
        if not card:
            return
        original = card.geometry()
        anim = QPropertyAnimation(card, b"geometry", self)
        anim.setDuration(300)
        anim.setEasingCurve(QEasingCurve.OutElastic)
        dx = 8
        anim.setKeyValueAt(0,    QRect(original.x(),      original.y(), original.width(), original.height()))
        anim.setKeyValueAt(0.15, QRect(original.x() - dx, original.y(), original.width(), original.height()))
        anim.setKeyValueAt(0.3,  QRect(original.x() + dx, original.y(), original.width(), original.height()))
        anim.setKeyValueAt(0.45, QRect(original.x() - dx, original.y(), original.width(), original.height()))
        anim.setKeyValueAt(0.6,  QRect(original.x() + dx, original.y(), original.width(), original.height()))
        anim.setKeyValueAt(1.0,  QRect(original.x(),      original.y(), original.width(), original.height()))
        anim.start()

    def accept_login(self):
        """Dipanggil main.py setelah login berhasil."""
        pass  # Di-override di main.py

    def get_logged_in_user(self):
        return self._logged_in_user
