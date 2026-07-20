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
        title = QLabel("Help Center")
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
                "desc":  "Patient data management page.",
                "items": [
                    ("Register New Patient",
                     "Click the 'Register New Patient' button in the top right corner. "
                     "Fill out the patient identity form (Name, Medical Record No., Date of Birth, "
                     "Gender, Weight, Height), then click Save."),
                    ("Search Patients",
                     "Type a name or Medical Record No. in the search bar. Use the Gender filter "
                     "to narrow down results, then click Filter."),
                    ("Edit / Delete Patient",
                     "Use the Edit or Delete buttons in the Action column of each table row."),
                ],
            },
            {
                "icon":  "fa5s.heartbeat",
                "color": "#E53E3E",
                "title": "Active Session",
                "desc":  "Page to start and monitor real-time sensor recording sessions.",
                "items": [
                    ("Selecting a Patient",
                     "Type a name or Medical Record No. in the search bar, then select a patient "
                     "from the dropdown. Patient identity data will appear on the right card."),
                    ("Starting a Session",
                     "Once a patient is selected, the 'Start' button becomes active. Click the button "
                     "to enter the live sensor monitoring page."),
                    ("Sensor Monitoring",
                     "Heart Rate (BPM), Skin Conductance (µS), and Skin Temperature (°C) graphs "
                     "are updated in real-time from the connected Bluetooth device."),
                    ("Ending a Session",
                     "Click the 'Back' button to stop recording and return "
                     "to the patient selection page."),
                ],
            },
            {
                "icon":  "fa5s.file-medical-alt",
                "color": "#38A169",
                "title": "Session History",
                "desc":  "List of all saved examination sessions.",
                "items": [
                    ("Search History",
                     "Use the search bar to find by patient ID or name. "
                     "The 'Category' filter allows searching by anxiety level."),
                    ("View Session Details",
                     "Click the 'Detail' button in the Action column to open the "
                     "full session details window along with sensor graph replay."),
                    ("Export Reports",
                     "Use the 'PDF' button to export a PDF report or 'Excel' "
                     "to export to a spreadsheet format."),
                    ("Anxiety Levels",
                     "Analysis results are displayed with colored badges: "
                     "Minimal (green), Mild (yellow), Moderate (orange), Severe (red)."),
                ],
            },
            {
                "icon":  "fa5s.chart-line",
                "color": "#D69E2E",
                "title": "Session Details & Replay",
                "desc":  "The session details window shows patient identity and sensor data replay.",
                "items": [
                    ("Play Replay",
                     "Click the 'Play' button to start the sensor data replay animation. "
                     "Click again to pause."),
                    ("Reset Replay",
                     "Click the 'Reset' button to return the graphs to their initial state "
                     "and restart the replay from the beginning."),
                    ("Reading the Graphs",
                     "The Y-axis shows the sensor value, the X-axis shows time (relative). "
                     "Three graphs: Heart Rate (red), Skin Conductance (blue), "
                     "Skin Temperature (yellow)."),
                ],
            },
            {
                "icon":  "fa5s.info-circle",
                "color": "#805AD5",
                "title": "System Information",
                "desc":  "About PhysioAnx.",
                "items": [
                    ("Application Version", "PhysioAnx v1.0 — Physiological Anxiety Monitoring System."),
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
            "color: #1E3F76; font-size: 12px; "
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
                "color: #1E3F76; font-size: 12px; "
                "background: transparent; border: none;"
            )

            text_col.addWidget(lbl_q)
            text_col.addWidget(lbl_a)

            item_row.addWidget(dot)
            item_row.addLayout(text_col)
            layout.addLayout(item_row)

        return card
