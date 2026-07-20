from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QWidget, QGraphicsDropShadowEffect
from PySide6.QtCore import QTimer, Qt, QSize
from PySide6.QtGui import QColor
import pyqtgraph as pg
import qtawesome as qta
import math
import random


def _shadow():
    s = QGraphicsDropShadowEffect()
    s.setBlurRadius(20)
    s.setXOffset(0)
    s.setYOffset(5)
    s.setColor(QColor(0, 0, 0, 55))
    return s


class ReplayDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        # data = [tanggal, id_pasien, nama, indikasi, usia, gender, tb, bb]
        self.setWindowTitle(f"Session Detail — {data[2]}")
        self.setFixedSize(1000, 750)
        self.setModal(True)
        self.setStyleSheet("background-color: #F7FAFC;")

        self.t = 0
        self.data_hr   = []
        self.data_gsr  = []
        self.data_temp = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(16)

        # ── 1. KARTU IDENTITAS PASIEN ─────────────────────────────────────────────
        main_layout.addWidget(self._build_identity_card(data))

        # ── 2. TOMBOL KONTROL ────────────────────────────────────────────────────
        kontrol_layout = QHBoxLayout()

        self.btn_play = QPushButton(" Play")
        self.btn_play.setIcon(qta.icon('fa5s.play', color='white'))
        self.btn_play.setCursor(Qt.PointingHandCursor)
        self.btn_play.setFixedHeight(38)
        self.btn_play.setStyleSheet("""
            QPushButton {
                background-color: #38A169; color: white;
                padding: 0 20px; font-weight: bold;
                border-radius: 8px; font-size: 13px; border: none;
            }
            QPushButton:hover { background-color: #2F855A; }
        """)
        self.btn_play.clicked.connect(self.toggle_play)

        self.btn_close = QPushButton(" Close")
        self.btn_close.setIcon(qta.icon('fa5s.times', color='#E53E3E'))
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setFixedHeight(38)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #2D3748;
                padding: 0 20px;
                font-weight: bold;
                border-radius: 8px;
                font-size: 13px;
                border: 1.5px solid #E2E8F0;
            }
            QPushButton:hover {
                background-color: #FFF5F5;
                color: #E53E3E;
                border: 1.5px solid #FC8181;
            }
            QPushButton:pressed {
                background-color: #FED7D7;
                border: 1.5px solid #E53E3E;
            }
        """)
        self.btn_close.clicked.connect(self.close)

        kontrol_layout.addWidget(self.btn_play)
        kontrol_layout.addStretch()
        kontrol_layout.addWidget(self.btn_close)
        main_layout.addLayout(kontrol_layout)

        # ── 3. GRAFIK SENSOR ─────────────────────────────────────────────────────
        graphs_layout = QVBoxLayout()
        graphs_layout.setSpacing(12)

        self.val_hr,   self.plot_hr,   self.curve_hr   = self.create_sensor_row("HEART RATE",        "BPM", "#FF5252", "fa5s.heartbeat",       graphs_layout)
        self.val_gsr,  self.plot_gsr,  self.curve_gsr  = self.create_sensor_row("SKIN CONDUCTANCE",  "µS",  "#40C4FF", "fa5s.bolt",             graphs_layout)
        self.val_temp, self.plot_temp, self.curve_temp = self.create_sensor_row("SKIN TEMPERATURE",  "°C",  "#FFB300", "fa5s.thermometer-half", graphs_layout)

        main_layout.addLayout(graphs_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graphs)
        self.is_playing = False

    # ─────────────────────────────────────────────────────────────────────────────

    def _build_identity_card(self, data):
        sev = data[3]
        sev_map = {
            "Severe":   "#E53E3E",
            "Moderate": "#DD6B20",
            "Mild":     "#D69E2E",
            "Minimal":  "#38A169",
        }
        sev_color = sev_map.get(sev, "#718096")

        card = QFrame()
        card.setGraphicsEffect(_shadow())
        card.setObjectName("IdentityCard")
        card.setStyleSheet("""
            QFrame#IdentityCard {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #CBD5E0;
            }
        """)

        outer = QVBoxLayout(card)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        fields = [
            ("Name",    data[2]),
            ("No. RM",  data[1]),
            ("Date",    data[0]),
            ("Age",     data[4]),
            ("Gender",  data[5]),
            ("Weight",  data[7]),
            ("Height",  data[6]),
        ]

        # stretch per kolom: Name lebih lebar, Date medium, sisanya equal
        stretches = [3, 2, 3, 1, 1, 1, 1]

        # ── Header row ────────────────────────────────────────────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(0)
        header_row.setContentsMargins(0, 0, 0, 0)

        for i, (label, _) in enumerate(fields):
            h = QLabel(f"  {label}")
            h.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            h.setFixedHeight(30)
            h.setStyleSheet(
                "background-color: #EDF2F7; color: #1A202C; "
                "font-size: 12px; font-weight: 700; border: none;"
            )
            header_row.addWidget(h, stretch=stretches[i])

        badge_h = QLabel("  Result  ")
        badge_h.setAlignment(Qt.AlignCenter)
        badge_h.setFixedHeight(30)
        badge_h.setStyleSheet(
            "background-color: #EDF2F7; color: #1A202C; "
            "font-size: 12px; font-weight: 700; border: none;"
        )
        header_row.addWidget(badge_h, stretch=1)

        # ── Divider ───────────────────────────────────────────────────────────────
        h_line = QFrame()
        h_line.setFrameShape(QFrame.HLine)
        h_line.setStyleSheet("background-color: #CBD5E0; max-height: 1px; border: none;")

        # ── Value row ─────────────────────────────────────────────────────────────
        value_row = QHBoxLayout()
        value_row.setSpacing(0)
        value_row.setContentsMargins(0, 0, 0, 0)

        for i, (_, value) in enumerate(fields):
            v = QLabel(f"  {str(value) if value else '—'}")
            v.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            v.setFixedHeight(34)
            v.setStyleSheet(
                "background-color: #FFFFFF; color: #1A202C; "
                "font-size: 13px; font-weight: 600; border: none;"
            )
            value_row.addWidget(v, stretch=stretches[i])

        # Nilai severity di baris bawah (sejajar badge header)
        sev_val = QLabel(f"  {sev.upper()}  ")
        sev_val.setAlignment(Qt.AlignCenter)
        sev_val.setFixedHeight(34)
        sev_val.setStyleSheet(f"""
            background-color: {sev_color};
            color: white;
            font-size: 12px;
            font-weight: bold;
            border: none;
        """)
        value_row.addWidget(sev_val, stretch=1)

        outer.addLayout(header_row)
        outer.addWidget(h_line)
        outer.addLayout(value_row)

        return card




    # ─────────────────────────────────────────────────────────────────────────────

    def create_sensor_row(self, title_text, unit_text, color, icon_name, parent_layout):
        row_frame = QFrame()
        row_frame.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0;")

        row_layout = QHBoxLayout(row_frame)
        row_layout.setContentsMargins(15, 2, 15, 2)

        pg.setConfigOption('background', 'transparent')
        pg.setConfigOption('foreground', '#718096')

        plot = pg.PlotWidget()
        plot.getAxis('left').setPen('#CBD5E0')
        plot.getAxis('bottom').setPen('#CBD5E0')
        plot.showGrid(x=True, y=True, alpha=0.15)
        plot.setFixedHeight(120)
        curve = plot.plot(pen=pg.mkPen(color=color, width=2.5))

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

        parent_layout.addWidget(row_frame)
        return val_lbl, plot, curve

    # ─────────────────────────────────────────────────────────────────────────────

    def toggle_play(self):
        if not self.is_playing:
            self.is_playing = True
            self.timer.start(50)
            self.btn_play.setText(" Pause")
            self.btn_play.setIcon(qta.icon('fa5s.pause', color='white'))
            self.btn_play.setStyleSheet("""
                QPushButton { background-color: #D69E2E; color: white; padding: 0 20px; font-weight: bold; border-radius: 8px; font-size: 13px; border: none; }
                QPushButton:hover { background-color: #B7791F; }
            """)
        else:
            self.is_playing = False
            self.timer.stop()
            self.btn_play.setText(" Resume")
            self.btn_play.setIcon(qta.icon('fa5s.play', color='white'))
            self.btn_play.setStyleSheet("""
                QPushButton { background-color: #38A169; color: white; padding: 0 20px; font-weight: bold; border-radius: 8px; font-size: 13px; border: none; }
                QPushButton:hover { background-color: #2F855A; }
            """)

    def update_graphs(self):
        self.t += 1

        hr   = 80  + math.sin(self.t * 0.1)  * 15 + random.uniform(-3,   3)
        gsr  = 5   + math.cos(self.t * 0.05) * 3  + random.uniform(-0.5, 0.5)
        temp = 32  + math.sin(self.t * 0.01) * 1  + random.uniform(-0.1, 0.1)

        self.val_hr.setText(f"{hr:.1f}")
        self.val_gsr.setText(f"{gsr:.2f}")
        self.val_temp.setText(f"{temp:.1f}")

        self.data_hr.append(hr)
        self.data_gsr.append(gsr)
        self.data_temp.append(temp)

        if len(self.data_hr) > 100:
            self.data_hr.pop(0)
            self.data_gsr.pop(0)
            self.data_temp.pop(0)

        self.curve_hr.setData(self.data_hr)
        self.curve_gsr.setData(self.data_gsr)
        self.curve_temp.setData(self.data_temp)
