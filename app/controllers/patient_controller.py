from PySide6.QtWidgets import QTableWidgetItem, QWidget, QHBoxLayout, QPushButton, QMessageBox
from PySide6.QtCore import Qt
import qtawesome as qta
from datetime import date
from models.database import SessionLocal
from models.patient import Patient
from components.patient_dialog import PatientDialog

class PatientController:
    def __init__(self, view, main_window):
        self.view = view
        self.main_window = main_window # Untuk callback seperti start_examination atau refresh combobox
        
        # Sambungkan sinyal dari UI ke fungsi controller
        self.view.btn_add.clicked.connect(self.show_add_patient_dialog)
        self.view.search_input_pasien.textChanged.connect(self.load_patients)
        self.view.cmb_gender_pasien.currentIndexChanged.connect(self.load_patients)
        self.view.btn_filter.clicked.connect(self.load_patients)
        
        # Load data pertama kali
        self.load_patients()

    def load_patients(self):
        session = SessionLocal()
        query = session.query(Patient)
        
        search_text = self.view.search_input_pasien.text().strip()
        if search_text:
            query = query.filter((Patient.full_name.ilike(f"%{search_text}%")) | (Patient.no_rm.ilike(f"%{search_text}%")))
            
        gender_text = self.view.cmb_gender_pasien.currentText()
        if gender_text != "Semua Jenis Kelamin":
            query = query.filter(Patient.gender == gender_text)
            
        patients = query.all()
        
        self.view.table_pasien.setRowCount(len(patients))
        for row, p in enumerate(patients):
            self.view.table_pasien.setItem(row, 0, QTableWidgetItem(p.no_rm))
            self.view.table_pasien.setItem(row, 1, QTableWidgetItem(p.full_name))
            
            # Hitung umur
            umur = ""
            if p.date_of_birth:
                today = date.today()
                age = today.year - p.date_of_birth.year - ((today.month, today.day) < (p.date_of_birth.month, p.date_of_birth.day))
                umur = f"{age} Thn"
            
            item_umur = QTableWidgetItem(umur)
            item_umur.setTextAlignment(Qt.AlignCenter)
            self.view.table_pasien.setItem(row, 2, item_umur)
            
            # Format Gender
            if p.gender in ["L", "Laki-laki"]:
                gender_display = "Laki-laki"
            elif p.gender in ["P", "Perempuan"]:
                gender_display = "Perempuan"
            else:
                gender_display = p.gender
                
            item_jk = QTableWidgetItem(gender_display)
            item_jk.setTextAlignment(Qt.AlignCenter)
            self.view.table_pasien.setItem(row, 3, item_jk)
            
            # Kolom Aksi
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(8)
            
            btn_periksa = QPushButton(" Periksa")
            btn_periksa.setIcon(qta.icon('fa5s.stethoscope', color='white'))
            btn_periksa.setStyleSheet("background-color: #4CAF50; color: white; border: none; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
            btn_periksa.setCursor(Qt.PointingHandCursor)
            btn_periksa.clicked.connect(lambda checked, pat=p, u=umur: self.main_window.start_examination(pat, u))
            
            btn_edit = QPushButton(" Edit")
            btn_edit.setIcon(qta.icon('fa5s.edit', color='white'))
            btn_edit.setStyleSheet("background-color: #FFA000; color: white; border: none; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda checked, pat=p: self.show_edit_patient_dialog(pat))
            
            btn_delete = QPushButton(" Hapus")
            btn_delete.setIcon(qta.icon('fa5s.trash-alt', color='white'))
            btn_delete.setStyleSheet("background-color: #D32F2F; color: white; border: none; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
            btn_delete.setCursor(Qt.PointingHandCursor)
            btn_delete.clicked.connect(lambda checked, rm=p.no_rm, n=p.full_name: self.delete_patient_action(rm, n))
            
            action_layout.addWidget(btn_periksa)
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)
            action_layout.addStretch()
            self.view.table_pasien.setCellWidget(row, 4, action_widget)
            
        self.view.lbl_info.setText(f"Menampilkan 1 hingga {len(patients)} dari {len(patients)} entri")
        session.close()

    def show_add_patient_dialog(self):
        dialog = PatientDialog(self.view)
        if dialog.exec():
            data = dialog.get_data()
            session = SessionLocal()
            new_p = Patient(
                no_rm=data["no_rm"],
                full_name=data["full_name"],
                date_of_birth=data["date_of_birth"],
                gender=data["gender"],
                height=data["height"],
                weight=data["weight"]
            )
            session.add(new_p)
            session.commit()
            session.close()
            self.load_patients()
            if hasattr(self.main_window, 'load_patients_to_combobox'):
                self.main_window.load_patients_to_combobox()

    def show_edit_patient_dialog(self, patient_obj):
        dialog = PatientDialog(self.view, patient_data=patient_obj)
        if dialog.exec():
            data = dialog.get_data()
            session = SessionLocal()
            p = session.query(Patient).filter(Patient.no_rm == patient_obj.no_rm).first()
            if p:
                p.full_name = data["full_name"]
                p.date_of_birth = data["date_of_birth"]
                p.gender = data["gender"]
                p.height = data["height"]
                p.weight = data["weight"]
                session.commit()
            session.close()
            self.load_patients()
            if hasattr(self.main_window, 'load_patients_to_combobox'):
                self.main_window.load_patients_to_combobox()

    def delete_patient_action(self, rm_id, patient_name):
        msg_box = QMessageBox(self.view)
        msg_box.setWindowTitle("Konfirmasi Hapus")
        msg_box.setText(f"Apakah Anda yakin ingin menghapus data pasien '{patient_name}'?")
        msg_box.setInformativeText("Data yang dihapus tidak dapat dikembalikan.")
        msg_box.setIcon(QMessageBox.Warning)
        
        btn_yes = msg_box.addButton("Ya, Hapus", QMessageBox.DestructiveRole)
        btn_no = msg_box.addButton("Batal", QMessageBox.RejectRole)
        msg_box.setDefaultButton(btn_no)
        
        msg_box.exec()
        if msg_box.clickedButton() == btn_yes:
            session = SessionLocal()
            p = session.query(Patient).filter(Patient.no_rm == rm_id).first()
            if p:
                session.delete(p)
                session.commit()
            session.close()
            self.load_patients()
            if hasattr(self.main_window, 'load_patients_to_combobox'):
                self.main_window.load_patients_to_combobox()
