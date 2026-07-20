from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QProgressBar, QPushButton
)
from PySide6.QtCore import Qt
import qtawesome as qta
import pyqtgraph as pg
from main_window import create_shadow
from models.database import SessionLocal
from models.patient import Patient
from models.session import Session as SessionModel

class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.load_data()
        self.setup_ui()

    def load_data(self):
        db = SessionLocal()
        try:
            self.total_patients = db.query(Patient).count()
            sessions = db.query(SessionModel).all()
            self.total_sessions = len(sessions)
            
            self.anx_counts = {"Minimal": 0, "Mild": 0, "Moderate": 0, "Severe": 0}
            
            for s in sessions:
                lvl = s.anxiety_level
                if lvl in self.anx_counts:
                    self.anx_counts[lvl] += 1
        finally:
            db.close()

    def setup_ui(self):
        root = self.layout()
        if not root:
            root = QVBoxLayout(self)
            root.setContentsMargins(0, 0, 0, 0)
            root.setSpacing(24)

        # ── Header ───────────────────────────────────────────────────────────────
        header = QHBoxLayout()
        title = QLabel("Dashboard Overview")
        title.setObjectName("HeaderTitle")
        header.addWidget(title)
        
        header.addStretch()
        root.addLayout(header)

        # ── Stats Cards ──────────────────────────────────────────────────────────
        grid = QGridLayout()
        grid.setSpacing(24)

        self.card1 = self._build_stat_card("Total Patients", str(self.total_patients), "fa5s.users", "#3182CE")
        self.card2 = self._build_stat_card("Total Sessions", str(self.total_sessions), "fa5s.heartbeat", "#38A169")
        
        severe_cnt = self.anx_counts["Severe"]
        self.card3 = self._build_stat_card("Severe Cases", str(severe_cnt), "fa5s.exclamation-triangle", "#E53E3E")
        
        grid.addWidget(self.card1, 0, 0)
        grid.addWidget(self.card2, 0, 1)
        grid.addWidget(self.card3, 0, 2)
        root.addLayout(grid)

        # ── Content Split (Chart & Progress Bars) ──────────────────────────────
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)

        # 1. Chart Section
        chart_frame = QFrame()
        chart_frame.setGraphicsEffect(create_shadow())
        chart_frame.setStyleSheet("QFrame { background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; }")
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(24, 24, 24, 24)
        
        chart_title = QLabel("Weekly Sessions Trend")
        chart_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #1A202C; border: none;")
        chart_layout.addWidget(chart_title)

        pg.setConfigOption('background', 'transparent')
        pg.setConfigOption('foreground', '#4A5568')
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setStyleSheet("border: none;")
        self.plot_widget.showGrid(x=False, y=True, alpha=0.3)
        
        x = [1, 2, 3, 4, 5, 6, 7]
        y = [2, 5, 3, 6, 4, 8, self.total_sessions if self.total_sessions > 0 else 1] # Mock dynamic
        pen = pg.mkPen(color='#3182CE', width=3)
        self.plot_widget.plot(x, y, pen=pen, symbol='o', symbolSize=8, symbolBrush='#FFFFFF', symbolPen=pg.mkPen('#3182CE', width=2))
        
        chart_layout.addWidget(self.plot_widget)
        content_layout.addWidget(chart_frame, stretch=2)

        # 2. Progress Bar Section
        prog_frame = QFrame()
        prog_frame.setGraphicsEffect(create_shadow())
        prog_frame.setStyleSheet("QFrame { background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; }")
        prog_layout = QVBoxLayout(prog_frame)
        prog_layout.setContentsMargins(24, 24, 24, 24)
        prog_layout.setSpacing(32)
        
        prog_title = QLabel("Anxiety Level Distribution")
        prog_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #1A202C; border: none;")
        prog_layout.addWidget(prog_title)
        
        total = self.total_sessions if self.total_sessions > 0 else 1
        
        prog_layout.addWidget(self._build_progress_bar("Minimal", self.anx_counts["Minimal"], total, "#38A169"))
        prog_layout.addWidget(self._build_progress_bar("Mild", self.anx_counts["Mild"], total, "#D69E2E"))
        prog_layout.addWidget(self._build_progress_bar("Moderate", self.anx_counts["Moderate"], total, "#DD6B20"))
        prog_layout.addWidget(self._build_progress_bar("Severe", self.anx_counts["Severe"], total, "#E53E3E"))
        
        prog_layout.addStretch()
        content_layout.addWidget(prog_frame, stretch=1)

        root.addLayout(content_layout, stretch=1)

    def _build_progress_bar(self, label_text, count, total, color):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        top_layout = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #4A5568;")
        
        pct = int((count / total) * 100)
        val = QLabel(f"{count} ({pct}%)")
        val.setStyleSheet("font-size: 14px; font-weight: bold; color: #1A202C;")
        
        top_layout.addWidget(lbl)
        top_layout.addStretch()
        top_layout.addWidget(val)
        
        bar = QProgressBar()
        bar.setFixedHeight(12)
        bar.setTextVisible(False)
        bar.setValue(pct)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #EDF2F7;
                border-radius: 6px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 6px;
            }}
        """)
        
        layout.addLayout(top_layout)
        layout.addWidget(bar)
        return widget

    def _build_stat_card(self, title, value, icon_name, color):
        from PySide6.QtWidgets import QHBoxLayout
        card = QFrame()
        card.setGraphicsEffect(create_shadow())
        card.setStyleSheet("QFrame { background-color: #FFFFFF; border-radius: 12px; border: 1px solid #E2E8F0; }")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 13px; color: #718096; font-weight: 700; border: none;")
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("font-size: 26px; color: #1A202C; font-weight: 800; border: none;")
        text_col.addWidget(lbl_title)
        text_col.addWidget(lbl_value)
        text_col.addStretch()
        
        icon_wrap = QFrame()
        icon_wrap.setFixedSize(56, 56)
        icon_wrap.setStyleSheet(f"background-color: {color}18; border-radius: 14px; border: none;")
        icon_layout = QHBoxLayout(icon_wrap)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_icon = QLabel()
        lbl_icon.setPixmap(qta.icon(icon_name, color=color).pixmap(26, 26))
        lbl_icon.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(lbl_icon)
        
        layout.addLayout(text_col)
        layout.addStretch()
        layout.addWidget(icon_wrap)
        
        return card

    def refresh_dashboard(self):
        # Clears current layout and rebuilds
        while self.layout().count():
            item = self.layout().takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clear_layout(item.layout())
        
        self.load_data()
        self.setup_ui()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())
