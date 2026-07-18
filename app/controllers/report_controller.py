from PySide6.QtWidgets import QTableWidgetItem, QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
import qtawesome as qta

class ReportController:
    def __init__(self, view, main_window):
        self.view = view
        self.main_window = main_window
        
        # Simulasi load data
        self.load_dummy_data()

    def load_dummy_data(self):
        dummy_sesi = [
            ("25 Jun 2026", "RM-2406-001 - Bpk. Budi", "15 Menit", "85 bpm", "Tinggi"),
            ("24 Jun 2026", "RM-2406-002 - Ibu Siti", "20 Menit", "72 bpm", "Sedang"),
            ("20 Jun 2026", "RM-2406-003 - Sdr. Andi", "10 Menit", "65 bpm", "Rendah")
        ]
        
        self.view.table_sesi.setRowCount(len(dummy_sesi))
        for row, data in enumerate(dummy_sesi):
            self.view.table_sesi.setItem(row, 0, QTableWidgetItem(data[0]))
            self.view.table_sesi.setItem(row, 1, QTableWidgetItem(data[1]))
            
            item_durasi = QTableWidgetItem(data[2])
            item_durasi.setTextAlignment(Qt.AlignCenter)
            self.view.table_sesi.setItem(row, 2, item_durasi)
            
            # Badge Indikasi Kecemasan
            lbl_indikasi = QLabel(data[4])
            lbl_indikasi.setAlignment(Qt.AlignCenter)
            if data[4] == "Tinggi":
                lbl_indikasi.setStyleSheet("background-color: #D32F2F; color: #FFF; padding: 4px; border-radius: 4px; font-weight: bold;")
            elif data[4] == "Sedang":
                lbl_indikasi.setStyleSheet("background-color: #F57F17; color: #FFF; padding: 4px; border-radius: 4px; font-weight: bold;")
            else:
                lbl_indikasi.setStyleSheet("background-color: #1B5E20; color: #FFF; padding: 4px; border-radius: 4px; font-weight: bold;")
                
            ind_widget = QWidget()
            ind_layout = QHBoxLayout(ind_widget)
            ind_layout.setContentsMargins(5, 5, 5, 5)
            ind_layout.addWidget(lbl_indikasi)
            self.view.table_sesi.setCellWidget(row, 3, ind_widget)
            
            # Kolom Aksi
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(8)
            
            btn_detail = QPushButton(" Detail")
            btn_detail.setIcon(qta.icon('fa5s.chart-area', color='white'))
            btn_detail.setStyleSheet("background-color: #1976D2; color: white; border: none; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
            btn_detail.setCursor(Qt.PointingHandCursor)
            
            btn_pdf = QPushButton(" PDF")
            btn_pdf.setIcon(qta.icon('fa5s.file-pdf', color='white'))
            btn_pdf.setStyleSheet("background-color: #388E3C; color: white; border: none; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
            btn_pdf.setCursor(Qt.PointingHandCursor)
            
            action_layout.addWidget(btn_detail)
            action_layout.addWidget(btn_pdf)
            action_layout.addStretch()
            self.view.table_sesi.setCellWidget(row, 4, action_widget)
            
        self.view.lbl_info.setText(f"Menampilkan 1 hingga {len(dummy_sesi)} dari {len(dummy_sesi)} riwayat sesi")
