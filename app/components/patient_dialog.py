from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QTextEdit, QPushButton, QDateEdit, QFormLayout, QSpinBox, QDoubleSpinBox)
from PySide6.QtCore import Qt, QDate
import qtawesome as qta

class PatientDialog(QDialog):
    def __init__(self, parent=None, patient_data=None):
        super().__init__(parent)
        self.setWindowTitle("Register Patient" if not patient_data else "Edit Patient Data")
        self.setFixedSize(450, 500)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                color: #002C6F;
            }
            QLabel {
                color: #1E3F76;
                font-weight: bold;
                font-size: 13px;
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
                background-color: #F7FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 6px;
                padding: 8px;
                color: #002C6F;
                font-size: 14px;
            }
            QSpinBox, QDoubleSpinBox {
                padding-right: 25px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #5C9EDA;
                background-color: #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #002C6F;
                selection-background-color: #EBF8FA;
                border: 1px solid #E2E8F0;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        lbl_title = QLabel("Patient Data Form" if not patient_data else "Edit Patient Profile")
        lbl_title.setStyleSheet("color: #002C6F; font-size: 20px; font-weight: 900; margin-bottom: 10px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.inp_rm = QLineEdit()
        self.inp_rm.setReadOnly(True)
        new_rm = self.generate_sequential_rm()
        
        self.inp_rm.setText(new_rm if not patient_data else patient_data.no_rm)
        self.inp_rm.setStyleSheet("background-color: #EDF2F7; color: #A0AEC0; border-color: #E2E8F0;")
        form_layout.addRow("Patient ID", self.inp_rm)

        self.inp_nama = QLineEdit()
        self.inp_nama.setPlaceholderText("Enter full name")
        if patient_data: self.inp_nama.setText(patient_data.full_name)
        form_layout.addRow("Full Name", self.inp_nama)

        self.layout_tgl = QHBoxLayout()
        self.layout_tgl.setSpacing(5)
        
        self.inp_tgl_hari = QComboBox()
        self.inp_tgl_hari.addItems([f"{i:02d}" for i in range(1, 32)])
        
        self.inp_tgl_bulan = QComboBox()
        self.inp_tgl_bulan.addItems([
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ])
        
        self.inp_tgl_tahun = QComboBox()
        current_year = QDate.currentDate().year()
        self.inp_tgl_tahun.addItems([str(i) for i in range(current_year, current_year - 120, -1)])
        
        self.layout_tgl.addWidget(self.inp_tgl_hari)
        self.layout_tgl.addWidget(self.inp_tgl_bulan)
        self.layout_tgl.addWidget(self.inp_tgl_tahun)
        
        default_date = QDate.currentDate().addYears(-20)
        if patient_data and patient_data.date_of_birth:
            try:
                # If it's a PySide6 QDate
                default_date = QDate(patient_data.date_of_birth.year(), patient_data.date_of_birth.month(), patient_data.date_of_birth.day())
            except TypeError:
                # If it's a Python datetime.date
                default_date = QDate(patient_data.date_of_birth.year, patient_data.date_of_birth.month, patient_data.date_of_birth.day)
            
        self.inp_tgl_hari.setCurrentText(f"{default_date.day():02d}")
        self.inp_tgl_bulan.setCurrentIndex(default_date.month() - 1)
        self.inp_tgl_tahun.setCurrentText(str(default_date.year()))

        def update_days():
            year = int(self.inp_tgl_tahun.currentText())
            month = self.inp_tgl_bulan.currentIndex() + 1
            days_in_month = QDate(year, month, 1).daysInMonth()
            
            current_day = self.inp_tgl_hari.currentText()
            self.inp_tgl_hari.clear()
            self.inp_tgl_hari.addItems([f"{i:02d}" for i in range(1, days_in_month + 1)])
            
            if int(current_day) <= days_in_month:
                self.inp_tgl_hari.setCurrentText(current_day)
            else:
                self.inp_tgl_hari.setCurrentText(f"{days_in_month:02d}")

        self.inp_tgl_bulan.currentIndexChanged.connect(update_days)
        self.inp_tgl_tahun.currentTextChanged.connect(update_days)
        
        form_layout.addRow("Date of Birth", self.layout_tgl)

        self.inp_jk = QComboBox()
        self.inp_jk.addItems(["Male", "Female"])
        if patient_data and patient_data.gender:
            self.inp_jk.setCurrentText("Male" if patient_data.gender in ["L", "M"] else "Female")
        form_layout.addRow("Gender", self.inp_jk)

        self.inp_bb = QDoubleSpinBox()
        self.inp_bb.setRange(10.0, 300.0)
        self.inp_bb.setSuffix(" kg")
        if patient_data and patient_data.weight:
            self.inp_bb.setValue(patient_data.weight)
        else:
            self.inp_bb.setValue(60.0)
        form_layout.addRow("Weight", self.inp_bb)
            
        self.inp_tb = QSpinBox()
        self.inp_tb.setRange(50, 250)
        self.inp_tb.setSuffix(" cm")
        if patient_data and patient_data.height:
            self.inp_tb.setValue(patient_data.height)
        else:
            self.inp_tb.setValue(165)
        form_layout.addRow("Height", self.inp_tb)

        layout.addLayout(form_layout)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_cancel = QPushButton(" Cancel")
        self.btn_cancel.setIcon(qta.icon('fa5s.times', color='#E53E3E'))
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #EDF2F7; color: #E53E3E; font-weight: bold; font-size: 14px; padding: 10px; border-radius: 6px; border: 1px solid #E2E8F0;
            }
            QPushButton:hover { background-color: #E2E8F0; }
        """)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(" Save Data")
        self.btn_save.setIcon(qta.icon('fa5s.save', color='white'))
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F97D1, stop:1 #5C9EDA); color: white; font-weight: bold; font-size: 14px; padding: 10px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5C9EDA, stop:1 #75B0E1); }
        """)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)

    def get_data(self):
        from datetime import date
        year = int(self.inp_tgl_tahun.currentText())
        month = self.inp_tgl_bulan.currentIndex() + 1
        day = int(self.inp_tgl_hari.currentText())
        
        return {
            "no_rm": self.inp_rm.text().strip(),
            "full_name": self.inp_nama.text().strip(),
            "date_of_birth": date(year, month, day),
            "gender": "M" if self.inp_jk.currentText() == "Male" else "F",
            "weight": self.inp_bb.value(),
            "height": self.inp_tb.value()
        }

    def generate_sequential_rm(self):
        from models.database import SessionLocal
        from models.patient import Patient
        
        session = SessionLocal()
        latest_patient = session.query(Patient).order_by(Patient.id.desc()).first()
        session.close()
        
        if latest_patient and latest_patient.no_rm.startswith("ID"):
            try:
                # Ambil 5 digit setelah tulisan "ID"
                last_num = int(latest_patient.no_rm[2:])
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1
            
        return f"ID{new_num:05d}"
