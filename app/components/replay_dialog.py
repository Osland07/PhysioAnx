from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QWidget
from PySide6.QtCore import QTimer, Qt
import pyqtgraph as pg
import qtawesome as qta
import math
import random

class ReplayDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detail Sesi - {data[2]}")
        self.setFixedSize(1000, 750)
        self.setModal(True)
        self.setStyleSheet("background-color: #F7FAFC;")
        
        self.t = 0
        self.data_hr = []
        self.data_gsr = []
        self.data_temp = []
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # --- 1. CARD IDENTITAS LENGKAP (Native Qt Layout) ---
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #E2E8F0;")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 20, 25, 20)
        
        # --- Bagian Atas: Demografi Pasien ---
        top_info_layout = QHBoxLayout()
        
        # Kolom 1: Nama & ID
        col1_layout = QVBoxLayout()
        col1_layout.setSpacing(4)
        lbl_nama = QLabel(data[2])
        lbl_nama.setStyleSheet("color: #2B6CB0; font-size: 22px; font-weight: bold;")
        lbl_id = QLabel(f"ID Pasien: <b>{data[1]}</b>")
        lbl_id.setStyleSheet("color: #4A5568; font-size: 14px;")
        col1_layout.addWidget(lbl_nama)
        col1_layout.addWidget(lbl_id)
        col1_layout.addStretch()
        
        # Kolom 2: Usia & Gender
        col2_layout = QVBoxLayout()
        col2_layout.setSpacing(6)
        lbl_usia = QLabel(f"<span style='color:#718096;'>Usia:</span> <span style='color:#2D3748; font-weight:600;'>{data[4]}</span>")
        lbl_gender = QLabel(f"<span style='color:#718096;'>Gender:</span> <span style='color:#2D3748; font-weight:600;'>{data[5]}</span>")
        lbl_usia.setStyleSheet("font-size: 14px;")
        lbl_gender.setStyleSheet("font-size: 14px;")
        col2_layout.addWidget(lbl_usia)
        col2_layout.addWidget(lbl_gender)
        col2_layout.addStretch()
        
        # Kolom 3: Fisik
        col3_layout = QVBoxLayout()
        col3_layout.setSpacing(6)
        lbl_tb = QLabel(f"<span style='color:#718096;'>Tinggi:</span> <span style='color:#2D3748; font-weight:600;'>{data[6]}</span>")
        lbl_bb = QLabel(f"<span style='color:#718096;'>Berat:</span> <span style='color:#2D3748; font-weight:600;'>{data[7]}</span>")
        lbl_tb.setStyleSheet("font-size: 14px;")
        lbl_bb.setStyleSheet("font-size: 14px;")
        col3_layout.addWidget(lbl_tb)
        col3_layout.addWidget(lbl_bb)
        col3_layout.addStretch()
        
        top_info_layout.addLayout(col1_layout, stretch=4)
        top_info_layout.addLayout(col2_layout, stretch=3)
        top_info_layout.addLayout(col3_layout, stretch=3)
        
        # --- Garis Pemisah (Separator) ---
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #E2E8F0; margin-top: 10px; margin-bottom: 10px;")
        
        # --- Bagian Bawah: Meta Sesi & Diagnosis ---
        bottom_info_layout = QHBoxLayout()
        
        # Waktu Rekaman
        waktu_layout = QVBoxLayout()
        waktu_layout.setSpacing(4)
        lbl_waktu_title = QLabel("WAKTU REKAMAN SESI")
        lbl_waktu_title.setStyleSheet("color: #A0AEC0; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        lbl_waktu_val = QLabel(data[0])
        lbl_waktu_val.setStyleSheet("color: #2D3748; font-size: 15px; font-weight: 600;")
        waktu_layout.addWidget(lbl_waktu_title)
        waktu_layout.addWidget(lbl_waktu_val)
        
        # Badge Indikasi
        indikasi_color = "#E53E3E" if data[3] == "Severe" else "#DD6B20" if data[3] == "Moderate" else "#38A169"
        indikasi_layout = QVBoxLayout()
        indikasi_layout.setSpacing(4)
        lbl_indikasi_title = QLabel("TINGKAT KECEMASAN")
        lbl_indikasi_title.setStyleSheet("color: #A0AEC0; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        
        lbl_indikasi_val = QLabel(data[3].upper())
        lbl_indikasi_val.setStyleSheet(f"color: white; background-color: {indikasi_color}; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: bold;")
        lbl_indikasi_val.setAlignment(Qt.AlignCenter)
        
        indikasi_layout.addWidget(lbl_indikasi_title, alignment=Qt.AlignRight)
        indikasi_layout.addWidget(lbl_indikasi_val, alignment=Qt.AlignRight)
        
        bottom_info_layout.addLayout(waktu_layout)
        bottom_info_layout.addStretch()
        bottom_info_layout.addLayout(indikasi_layout)
        
        # --- Rakit Header ---
        header_layout.addLayout(top_info_layout)
        header_layout.addWidget(separator)
        header_layout.addLayout(bottom_info_layout)
        main_layout.addWidget(header_frame)
        
        # --- 2. KONTROL PLAY & STOP ---
        kontrol_layout = QHBoxLayout()
        self.btn_play = QPushButton(" Putar Replay")
        self.btn_play.setIcon(qta.icon('fa5s.play', color='white'))
        self.btn_play.setCursor(Qt.PointingHandCursor)
        self.btn_play.setStyleSheet("""
            QPushButton { background-color: #38A169; color: white; padding: 10px 20px; font-weight: bold; border-radius: 6px; font-size: 13px; }
            QPushButton:hover { background-color: #2F855A; }
        """)
        self.btn_play.clicked.connect(self.toggle_play)
        
        kontrol_layout.addWidget(self.btn_play)
        kontrol_layout.addStretch()
        
        self.btn_close = QPushButton(" Tutup Layar")
        self.btn_close.setIcon(qta.icon('fa5s.times', color='white'))
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton { background-color: #E2E8F0; color: #4A5568; padding: 10px 20px; font-weight: bold; border-radius: 6px; font-size: 13px; }
            QPushButton:hover { background-color: #CBD5E0; }
        """)
        self.btn_close.clicked.connect(self.close)
        kontrol_layout.addWidget(self.btn_close)
        
        main_layout.addLayout(kontrol_layout)
        
        # --- 3. GRAFIK & ANGKA ---
        graphs_layout = QVBoxLayout()
        graphs_layout.setSpacing(15)
        
        self.val_hr, self.plot_hr, self.curve_hr = self.create_sensor_row("HEART RATE", "BPM", "#FF5252", "fa5s.heartbeat", graphs_layout)
        self.val_gsr, self.plot_gsr, self.curve_gsr = self.create_sensor_row("SKIN CONDUCTANCE", "µS", "#40C4FF", "fa5s.bolt", graphs_layout)
        self.val_temp, self.plot_temp, self.curve_temp = self.create_sensor_row("SKIN TEMPERATURE", "°C", "#FFB300", "fa5s.thermometer-half", graphs_layout)
        
        main_layout.addLayout(graphs_layout)
        
        # Timer (TIDAK LANGSUNG JALAN)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_graphs)
        self.is_playing = False
        
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
        
    def toggle_play(self):
        if not self.is_playing:
            self.is_playing = True
            self.timer.start(50)
            self.btn_play.setText(" Jeda Replay")
            self.btn_play.setIcon(qta.icon('fa5s.pause', color='white'))
            self.btn_play.setStyleSheet("""
                QPushButton { background-color: #D69E2E; color: white; padding: 10px 20px; font-weight: bold; border-radius: 6px; font-size: 13px; }
                QPushButton:hover { background-color: #B7791F; }
            """)
        else:
            self.is_playing = False
            self.timer.stop()
            self.btn_play.setText(" Lanjutkan Replay")
            self.btn_play.setIcon(qta.icon('fa5s.play', color='white'))
            self.btn_play.setStyleSheet("""
                QPushButton { background-color: #38A169; color: white; padding: 10px 20px; font-weight: bold; border-radius: 6px; font-size: 13px; }
                QPushButton:hover { background-color: #2F855A; }
            """)
            
    def update_graphs(self):
        self.t += 1
        
        hr = 80 + math.sin(self.t * 0.1) * 15 + random.uniform(-3, 3)
        gsr = 5 + math.cos(self.t * 0.05) * 3 + random.uniform(-0.5, 0.5)
        temp = 32 + math.sin(self.t * 0.01) * 1 + random.uniform(-0.1, 0.1)
        
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
