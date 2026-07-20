from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import qtawesome as qta


def _shadow():
    s = QGraphicsDropShadowEffect()
    s.setBlurRadius(20)
    s.setXOffset(0)
    s.setYOffset(5)
    s.setColor(QColor(0, 0, 0, 45))
    return s


class HelpView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(20)

        # ── Header ───────────────────────────────────────────────────────────────
        header = QHBoxLayout()
        title = QLabel("Help & Panduan")
        title.setObjectName("HeaderTitle")
        header.addWidget(title)
        header.addStretch()

        version = QLabel("PhysioAnx v1.0")
        version.setStyleSheet(
            "color: #A0AEC0; font-size: 12px; font-weight: 600; "
            "background: transparent; border: none;"
        )
        header.addWidget(version)
        root.addLayout(header)

        # ── Scroll Area ───────────────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: transparent; width: 6px; margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E0; border-radius: 3px; min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 12, 0)
        inner_layout.setSpacing(16)

        # ── Konten bantuan ────────────────────────────────────────────────────────
        sections = [
            {
                "icon":  "fa5s.users",
                "color": "#3182CE",
                "title": "Patients",
                "desc":  "Halaman manajemen data pasien.",
                "items": [
                    ("Registrasi Pasien Baru",
                     "Klik tombol 'Registrasi Pasien Baru' di pojok kanan atas. "
                     "Isi formulir data diri pasien (Nama, No. RM, Tanggal Lahir, "
                     "Jenis Kelamin, Berat, Tinggi Badan), lalu klik Simpan."),
                    ("Cari Pasien",
                     "Ketik nama atau No. RM di kolom pencarian. Gunakan filter "
                     "Jenis Kelamin untuk mempersempit hasil, lalu klik Filter."),
                    ("Edit / Hapus Pasien",
                     "Gunakan tombol Edit atau Hapus pada kolom Aksi di setiap baris tabel."),
                ],
            },
            {
                "icon":  "fa5s.heartbeat",
                "color": "#E53E3E",
                "title": "Sesi Pemeriksaan",
                "desc":  "Halaman untuk memulai dan memantau sesi rekaman sensor secara real-time.",
                "items": [
                    ("Memilih Pasien",
                     "Ketik nama atau No. RM di kolom pencarian, lalu pilih pasien "
                     "dari dropdown. Data identitas pasien akan tampil di kartu sebelah kanan."),
                    ("Memulai Sesi",
                     "Setelah pasien dipilih, tombol 'Mulai' akan aktif. Klik tombol "
                     "tersebut untuk masuk ke halaman monitoring live sensor."),
                    ("Monitoring Sensor",
                     "Grafik Heart Rate (BPM), Skin Conductance (µS), dan Skin Temperature (°C) "
                     "diperbarui secara real-time dari perangkat Bluetooth yang terhubung."),
                    ("Mengakhiri Sesi",
                     "Klik tombol 'Kembali' untuk menghentikan rekaman dan kembali "
                     "ke halaman pemilihan pasien."),
                ],
            },
            {
                "icon":  "fa5s.file-medical-alt",
                "color": "#38A169",
                "title": "Riwayat Sesi",
                "desc":  "Daftar seluruh sesi pemeriksaan yang telah tersimpan.",
                "items": [
                    ("Mencari Riwayat",
                     "Gunakan kolom pencarian untuk mencari berdasarkan ID atau nama pasien. "
                     "Filter 'Kategori' memungkinkan pencarian berdasarkan tingkat kecemasan."),
                    ("Melihat Detail Sesi",
                     "Klik tombol 'Detail' pada kolom Aksi untuk membuka jendela "
                     "detail sesi lengkap beserta replay grafik sensor."),
                    ("Ekspor Laporan",
                     "Gunakan tombol 'PDF' untuk ekspor laporan PDF atau 'Excel' "
                     "untuk ekspor ke format spreadsheet."),
                    ("Tingkat Kecemasan",
                     "Hasil analisis ditampilkan dengan badge berwarna: "
                     "Minimal (hijau), Mild (kuning), Moderate (oranye), Severe (merah)."),
                ],
            },
            {
                "icon":  "fa5s.chart-line",
                "color": "#D69E2E",
                "title": "Detail Sesi & Replay",
                "desc":  "Jendela detail sesi menampilkan identitas pasien dan replay data sensor.",
                "items": [
                    ("Memutar Replay",
                     "Klik tombol 'Play' untuk memulai animasi replay data sensor. "
                     "Klik lagi untuk menjeda."),
                    ("Reset Replay",
                     "Klik tombol 'Reset' untuk mengembalikan grafik ke kondisi awal "
                     "dan memulai replay dari awal."),
                    ("Membaca Grafik",
                     "Sumbu Y menunjukkan nilai sensor, sumbu X menunjukkan waktu (relative). "
                     "Tiga grafik: Heart Rate (merah), Skin Conductance (biru), "
                     "Skin Temperature (kuning)."),
                ],
            },
            {
                "icon":  "fa5s.info-circle",
                "color": "#805AD5",
                "title": "Informasi Sistem",
                "desc":  "Tentang PhysioAnx.",
                "items": [
                    ("Versi Aplikasi", "PhysioAnx v1.0 — Sistem Monitoring Kecemasan Fisiologis."),
                ],
            },
        ]

        for sec in sections:
            inner_layout.addWidget(
                self._build_section(
                    sec["icon"], sec["color"],
                    sec["title"], sec["desc"], sec["items"]
                )
            )

        inner_layout.addStretch()
        scroll.setWidget(inner)
        root.addWidget(scroll, stretch=1)

    # ─────────────────────────────────────────────────────────────────────────────

    def _build_section(self, icon_name, color, title, desc, items):
        card = QFrame()
        card.setGraphicsEffect(_shadow())
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # ── Section header ────────────────────────────────────────────────────────
        hdr = QHBoxLayout()
        hdr.setSpacing(12)

        ic_wrap = QFrame()
        ic_wrap.setFixedSize(40, 40)
        ic_wrap.setStyleSheet(f"""
            background-color: {color}18;
            border-radius: 10px;
            border: none;
        """)
        ic_l = QHBoxLayout(ic_wrap)
        ic_l.setContentsMargins(0, 0, 0, 0)
        ic_lbl = QLabel()
        ic_lbl.setPixmap(qta.icon(icon_name, color=color).pixmap(20, 20))
        ic_lbl.setAlignment(Qt.AlignCenter)
        ic_lbl.setStyleSheet("background: transparent; border: none;")
        ic_l.addWidget(ic_lbl)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            f"color: #1A202C; font-size: 15px; font-weight: 800; "
            f"background: transparent; border: none;"
        )

        lbl_desc = QLabel(desc)
        lbl_desc.setStyleSheet(
            "color: #4A5568; font-size: 12px; "
            "background: transparent; border: none;"
        )

        title_col.addWidget(lbl_title)
        title_col.addWidget(lbl_desc)

        hdr.addWidget(ic_wrap)
        hdr.addLayout(title_col)
        hdr.addStretch()

        layout.addLayout(hdr)

        # ── Separator ─────────────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #EDF2F7; max-height: 1px; border: none;")
        layout.addWidget(sep)

        # ── Items ─────────────────────────────────────────────────────────────────
        for item_title, item_body in items:
            item_row = QHBoxLayout()
            item_row.setSpacing(12)
            item_row.setAlignment(Qt.AlignTop)

            # Dot
            dot = QLabel("●")
            dot.setFixedWidth(14)
            dot.setStyleSheet(
                f"color: {color}; font-size: 10px; "
                "background: transparent; border: none;"
            )
            dot.setAlignment(Qt.AlignTop)

            # Text block
            text_col = QVBoxLayout()
            text_col.setSpacing(2)

            lbl_q = QLabel(item_title)
            lbl_q.setStyleSheet(
                "color: #1A202C; font-size: 13px; font-weight: 700; "
                "background: transparent; border: none;"
            )

            lbl_a = QLabel(item_body)
            lbl_a.setWordWrap(True)
            lbl_a.setStyleSheet(
                "color: #4A5568; font-size: 12px; "
                "background: transparent; border: none;"
            )

            text_col.addWidget(lbl_q)
            text_col.addWidget(lbl_a)

            item_row.addWidget(dot)
            item_row.addLayout(text_col)
            layout.addLayout(item_row)

        return card
