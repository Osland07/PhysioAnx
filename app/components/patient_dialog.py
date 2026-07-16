from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QTextEdit, QPushButton, QDateEdit, QFormLayout, QSpinBox, QDoubleSpinBox)
from PySide6.QtCore import Qt, QDate
import qtawesome as qta

class PatientDialog(QDialog):
    def __init__(self, parent=None, patient_data=None):
        super().__init__(parent)
        self.setWindowTitle("Registrasi Pasien Baru" if not patient_data else "Edit Data Pasien")
        self.setFixedSize(450, 500)
        
        # Tema dialog agar serasi dengan aplikasi
        self.setStyleSheet("""
            QDialog {
                background-color: #081B3B;
                color: #FFFFFF;
            }
            QLabel {
                color: #8C9EBA;
                font-weight: bold;
                font-size: 13px;
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
                background-color: #071733;
                border: 2px solid #112A54;
                border-radius: 6px;
                padding: 8px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QSpinBox, QDoubleSpinBox {
                padding-right: 25px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #FFD54F;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #071733;
                color: #FFFFFF;
                selection-background-color: #1565C0;
                border: 1px solid #112A54;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Header Title
        lbl_title = QLabel("Formulir Data Pasien" if not patient_data else "Edit Profil Pasien")
        lbl_title.setStyleSheet("color: #FFD54F; font-size: 20px; font-weight: 900; margin-bottom: 10px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Field: No. Rekam Medis
        self.inp_rm = QLineEdit()
        self.inp_rm.setReadOnly(True)
        # Generator RM berurutan berdasarkan database
        new_rm = self.generate_sequential_rm()
        
        self.inp_rm.setText(new_rm if not patient_data else patient_data.no_rm)
        self.inp_rm.setStyleSheet("background-color: #041024; color: #64748B; border-color: #041024;")
        form_layout.addRow("No. Rekam Medis", self.inp_rm)

        # Field: Nama Lengkap
        self.inp_nama = QLineEdit()
        self.inp_nama.setPlaceholderText("Masukkan nama lengkap pasien")
        if patient_data: self.inp_nama.setText(patient_data.full_name)
        form_layout.addRow("Nama Lengkap", self.inp_nama)

        # Field: Tanggal Lahir
        self.inp_tgl_lahir = QDateEdit()
        self.inp_tgl_lahir.setCalendarPopup(True)
        self.inp_tgl_lahir.setDisplayFormat("dd MMMM yyyy")
        self.inp_tgl_lahir.setDate(QDate.currentDate().addYears(-20))
        if patient_data and patient_data.date_of_birth:
            self.inp_tgl_lahir.setDate(patient_data.date_of_birth)
        form_layout.addRow("Tanggal Lahir", self.inp_tgl_lahir)

        # Field: Jenis Kelamin
        self.inp_jk = QComboBox()
        self.inp_jk.addItems(["Laki-laki", "Perempuan"])
        if patient_data and patient_data.gender == "P":
            self.inp_jk.setCurrentText("Perempuan")
        form_layout.addRow("Jenis Kelamin", self.inp_jk)

        # Field: Berat Badan
        self.inp_bb = QDoubleSpinBox()
        self.inp_bb.setRange(10.0, 300.0)
        self.inp_bb.setSuffix(" kg")
        if patient_data and patient_data.weight:
            self.inp_bb.setValue(patient_data.weight)
        else:
            self.inp_bb.setValue(60.0)
        form_layout.addRow("Berat Badan", self.inp_bb)
            
        # Field: Tinggi Badan
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

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_cancel = QPushButton(" Batal")
        self.btn_cancel.setIcon(qta.icon('fa5s.times', color='white'))
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #FF5252; color: white; font-weight: bold; font-size: 14px; padding: 10px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #D32F2F; }
        """)
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton(" Simpan Data")
        self.btn_save.setIcon(qta.icon('fa5s.save', color='#1A1A1A'))
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #FFD54F; color: #1A1A1A; font-weight: bold; font-size: 14px; padding: 10px; border-radius: 6px; border: none;
            }
            QPushButton:hover { background-color: #FFC107; }
        """)
        self.btn_save.setCursor(Qt.PointingHandCursor)
        self.btn_save.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)

    def get_data(self):
        """Mengembalikan dictionary berisi data yang diinputkan."""
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
        # Ambil pasien terakhir berdasarkan ID
        latest_patient = session.query(Patient).order_by(Patient.id.desc()).first()
        session.close()
        
        # Format: RM-YYMM-XXX (contoh: RM-2406-001)
        current_yymm = datetime.now().strftime("%y%m")
        
        if latest_patient and latest_patient.no_rm.startswith(f"RM-{current_yymm}-"):
            try:
                # Ambil 3 digit terakhir dan tambah 1
                last_num = int(latest_patient.no_rm.split("-")[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            # Jika bulan/tahun berbeda atau belum ada data
            new_num = 1
            
        return f"RM-{current_yymm}-{new_num:03d}"
