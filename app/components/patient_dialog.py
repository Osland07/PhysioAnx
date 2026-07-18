from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QTextEdit, QPushButton, QDateEdit, QFormLayout, QSpinBox, QDoubleSpinBox)
from PySide6.QtCore import Qt, QDate
import qtawesome as qta

class PatientDialog(QDialog):
    def __init__(self, parent=None, patient_data=None):
        super().__init__(parent)
        self.setWindowTitle("Registrasi Pasien Baru" if not patient_data else "Edit Data Pasien")
        self.setFixedSize(450, 500)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                color: #2D3748;
            }
            QLabel {
                color: #4A5568;
                font-weight: bold;
                font-size: 13px;
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
                background-color: #F7FAFC;
                border: 2px solid #E2E8F0;
                border-radius: 6px;
                padding: 8px;
                color: #2D3748;
                font-size: 14px;
            }
            QSpinBox, QDoubleSpinBox {
                padding-right: 25px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #00B4DB;
                background-color: #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #2D3748;
                selection-background-color: #EBF8FA;
                border: 1px solid #E2E8F0;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        lbl_title = QLabel("Formulir Data Pasien" if not patient_data else "Edit Profil Pasien")
        lbl_title.setStyleSheet("color: #2D3748; font-size: 20px; font-weight: 900; margin-bottom: 10px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.inp_rm = QLineEdit()
        self.inp_rm.setReadOnly(True)
        new_rm = self.generate_sequential_rm()
        
        self.inp_rm.setText(new_rm if not patient_data else patient_data.no_rm)
        self.inp_rm.setStyleSheet("background-color: #EDF2F7; color: #A0AEC0; border-color: #E2E8F0;")
        form_layout.addRow("No. Rekam Medis", self.inp_rm)

        self.inp_nama = QLineEdit()
        self.inp_nama.setPlaceholderText("Masukkan nama lengkap pasien")
        if patient_data: self.inp_nama.setText(patient_data.full_name)
        form_layout.addRow("Nama Lengkap", self.inp_nama)

        self.inp_tgl_lahir = QDateEdit()
        self.inp_tgl_lahir.setCalendarPopup(True)
        self.inp_tgl_lahir.setDisplayFormat("dd MMMM yyyy")
        self.inp_tgl_lahir.setDate(QDate.currentDate().addYears(-20))
        if patient_data and patient_data.date_of_birth:
            self.inp_tgl_lahir.setDate(patient_data.date_of_birth)
        form_layout.addRow("Tanggal Lahir", self.inp_tgl_lahir)

        self.inp_jk = QComboBox()
        self.inp_jk.addItems(["Laki-laki", "Perempuan"])
        if patient_data and patient_data.gender == "P":
            self.inp_jk.setCurrentText("Perempuan")
        form_layout.addRow("Jenis Kelamin", self.inp_jk)

        self.inp_bb = QDoubleSpinBox()
        self.inp_bb.setRange(10.0, 300.0)
        self.inp_bb.setSuffix(" kg")
        if patient_data and patient_data.weight:
            self.inp_bb.setValue(patient_data.weight)
        else:
            self.inp_bb.setValue(60.0)
        form_layout.addRow("Berat Badan", self.inp_bb)
            
        self.inp_tb = QSpinBox()
        self.inp_tb.setRange(50, 250)
        self.inp_tb.setSuffix(" cm")
        if patient_data and patient_data.height:
            self.inp_tb.setValue(patient_data.height)
        else:
            self.inp_tb.setValue(165)
        form_layout.addRow("Tinggi Badan", self.inp_tb)

        layout.addLayout(form_layout)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_cancel = QPushButton(" Batal")
        self.btn_cancel.setIcon(qta.icon('fa5s.times', color='#E53E3E'))
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #EDF2F7; color: #E53E3E; font-weight: bold; font-size: 14px; padding: 10px; border-radius: 6px; border: 1px solid #E2E8F0;
            }
            QPushButton:hover { background-color: #E2E8F0; }
        """)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(" Simpan Data")
        self.btn_save.setIcon(qta.icon('fa5s.save', color='white'))
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0083B0, stop:1 #00B4DB); color: white; font-weight: bold; font-size: 14px; padding: 10px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00B4DB, stop:1 #00D2FF); }
        """)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)

    def get_data(self):
        return {
            "no_rm": self.inp_rm.text().strip(),
            "full_name": self.inp_nama.text().strip(),
            "date_of_birth": self.inp_tgl_lahir.date().toPython(), # Returns datetime.date
            "gender": "L" if self.inp_jk.currentText() == "Laki-laki" else "P",
            "weight": self.inp_bb.value(),
            "height": self.inp_tb.value()
        }

    def generate_sequential_rm(self):
        from models.database import SessionLocal
        from models.patient import Patient
        from datetime import datetime
        
        session = SessionLocal()
        latest_patient = session.query(Patient).order_by(Patient.id.desc()).first()
        session.close()
        
        current_yymm = datetime.now().strftime("%y%m")
        
        if latest_patient and latest_patient.no_rm.startswith(f"RM-{current_yymm}-"):
            try:
                last_num = int(latest_patient.no_rm.split("-")[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
            
        return f"RM-{current_yymm}-{new_num:03d}"
