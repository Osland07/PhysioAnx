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

        # ================= KIRI (BRANDING) =================
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00B4DB,
                    stop:1 #0083B0
                );
            }
        """)
        left_panel.setFixedWidth(420)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(50, 60, 50, 60)
        left_layout.setSpacing(0)
        left_layout.setAlignment(Qt.AlignCenter)

        lbl_logo_icon = QLabel()
        lbl_logo_icon.setPixmap(qta.icon('fa5s.heartbeat', color='#FFFFFF').pixmap(64, 64))
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

        lbl_tagline = QLabel("Sistem Pemantauan Tingkat Kecemasan")
        lbl_tagline.setAlignment(Qt.AlignCenter)
        lbl_tagline.setWordWrap(True)
        lbl_tagline.setStyleSheet("""
            color: #E0F2F1;
            font-size: 15px;
            font-weight: 500;
            background: transparent;
            line-height: 1.6;
        """)

        divider = QFrame()
        divider.setFixedSize(60, 3)
        divider.setStyleSheet("background-color: #FFFFFF; border-radius: 2px; opacity: 0.5;")
        divider_row = QHBoxLayout()
        divider_row.setAlignment(Qt.AlignCenter)
        divider_row.addWidget(divider)

        lbl_version = QLabel("v1.0.0")
        lbl_version.setAlignment(Qt.AlignCenter)
        lbl_version.setStyleSheet("color: #B2EBF2; font-size: 11px; background: transparent;")

        left_layout.addStretch()
        left_layout.addWidget(lbl_logo_icon)
        left_layout.addSpacing(16)
        left_layout.addWidget(lbl_app_name)
        left_layout.addSpacing(12)
        left_layout.addLayout(divider_row)
        left_layout.addSpacing(16)
        left_layout.addWidget(lbl_tagline)
        left_layout.addStretch()
        left_layout.addWidget(lbl_version)

        # ================= KANAN (FORM LOGIN) =================
        right_panel = QFrame()
        right_panel.setStyleSheet("QFrame { background-color: #F4F7F9; }")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(70, 0, 70, 0)
        right_layout.setSpacing(0)
        right_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedWidth(380)
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 16px;
            }
        """)
        # Shadow lebih lembut untuk mode terang
        card.setGraphicsEffect(create_shadow(blur=30, opacity=15, offset_y=8))
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(20)

        lbl_welcome = QLabel("Welcome")
        lbl_welcome.setStyleSheet("""
            color: #2D3748;
            font-size: 24px;
            font-weight: 800;
            background: transparent;
            border: none;
        """)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #E2E8F0; border: none; max-height: 1px;")

        # === USERNAME ===
        lbl_user = QLabel("Username")
        lbl_user.setStyleSheet("color: #4A5568; font-size: 12px; font-weight: 700; background: transparent; border: none;")

        user_frame = QFrame()
        user_frame.setFixedHeight(44)
        user_frame.setStyleSheet("""
            QFrame {
                background-color: #F7FAFC;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
            }
        """)
        user_row = QHBoxLayout(user_frame)
        user_row.setContentsMargins(12, 0, 12, 0)
        user_row.setSpacing(10)
        
        user_icon = QLabel()
        user_icon.setPixmap(qta.icon('fa5s.user', color='#A0AEC0').pixmap(15, 15))
        user_icon.setStyleSheet("border: none; background: transparent;")

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Masukkan username...")
        self.input_username.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #2D3748;
                font-size: 14px;
            }
        """)
        user_row.addWidget(user_icon)
        user_row.addWidget(self.input_username)

        # === PASSWORD ===
        lbl_pass = QLabel("Password")
        lbl_pass.setStyleSheet("color: #4A5568; font-size: 12px; font-weight: 700; background: transparent; border: none;")

        pass_frame = QFrame()
        pass_frame.setFixedHeight(44)
        pass_frame.setStyleSheet("""
            QFrame {
                background-color: #F7FAFC;
                border: 1.5px solid #E2E8F0;
                border-radius: 8px;
            }
        """)
        pass_row = QHBoxLayout(pass_frame)
        pass_row.setContentsMargins(12, 0, 12, 0)
        pass_row.setSpacing(10)
        
        pass_icon = QLabel()
        pass_icon.setPixmap(qta.icon('fa5s.lock', color='#A0AEC0').pixmap(15, 15))
        pass_icon.setStyleSheet("border: none; background: transparent;")

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Masukkan password...")
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #2D3748;
                font-size: 14px;
            }
        """)
        
        self.btn_toggle_pass = QPushButton()
        self.btn_toggle_pass.setIcon(qta.icon('fa5s.eye', color='#A0AEC0'))
        self.btn_toggle_pass.setFixedSize(24, 24)
        self.btn_toggle_pass.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_pass.setCheckable(True)
        self.btn_toggle_pass.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
            QPushButton:hover { background-color: #E2E8F0; border-radius: 4px; }
        """)
        self.btn_toggle_pass.toggled.connect(self._toggle_password_visibility)
        
        pass_row.addWidget(pass_icon)
        pass_row.addWidget(self.input_password)
        pass_row.addWidget(self.btn_toggle_pass)

        # === PESAN ERROR ===
        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setFixedHeight(32)
        self.lbl_error.setStyleSheet("""
            QLabel {
                color: #C53030;
                font-size: 13px;
                font-weight: bold;
                background-color: #FED7D7;
                border: 1px solid #FEB2B2;
                border-radius: 5px;
                padding: 4px 8px;
            }
        """)
        self.lbl_error.hide()

        # === TOMBOL LOGIN ===
        self.btn_login = QPushButton("  Login")
        self.btn_login.setIcon(qta.icon('fa5s.sign-in-alt', color='white'))
        self.btn_login.setIconSize(QSize(16, 16))
        self.btn_login.setFixedHeight(48)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0083B0,
                    stop:1 #00B4DB
                );
                color: #FFFFFF;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                border: none;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00B4DB,
                    stop:1 #00D2FF
                );
            }
            QPushButton:pressed { background-color: #007299; }
        """)
        self.btn_login.clicked.connect(self._do_login)

        lbl_hint = QLabel("Username : admin\nPassword : admin123")
        lbl_hint.setAlignment(Qt.AlignCenter)
        lbl_hint.setStyleSheet("color: #A0AEC0; font-size: 12px; background: transparent; border: none;")

        card_layout.addWidget(lbl_welcome)
        card_layout.addWidget(sep)
        card_layout.addWidget(lbl_user)
        card_layout.addWidget(user_frame)
        card_layout.addWidget(lbl_pass)
        card_layout.addWidget(pass_frame)
        card_layout.addWidget(self.lbl_error)
        card_layout.addWidget(self.btn_login)
        card_layout.addWidget(lbl_hint)

        right_layout.addWidget(card, alignment=Qt.AlignCenter)

        self.input_username.returnPressed.connect(self._do_login)
        self.input_password.returnPressed.connect(self._do_login)

        root.addWidget(left_panel)
        root.addWidget(right_panel, stretch=1)

    def _toggle_password_visibility(self, checked: bool):
        if checked:
            self.input_password.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_pass.setIcon(qta.icon('fa5s.eye-slash', color='#3182CE'))
        else:
            self.input_password.setEchoMode(QLineEdit.Password)
            self.btn_toggle_pass.setIcon(qta.icon('fa5s.eye', color='#A0AEC0'))

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
            self._show_error("Username atau password salah.")
            self.input_password.clear()

    def _show_error(self, msg: str):
        self.lbl_error.setText(msg)
        self.lbl_error.show()

    def _shake_card(self):
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
        pass  # Di-override di main.py

    def get_logged_in_user(self):
        return self._logged_in_user
