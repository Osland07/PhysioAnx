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
            ("19 Jul 2026, 09:15", "2406-001", "Bpk. Budi", "Severe", "45 Tahun", "Laki-laki", "170 cm", "75 kg", "Jl. Merdeka No. 1, Jakarta"),
            ("18 Jul 2026, 14:30", "2406-002", "Ibu Siti", "Moderate", "38 Tahun", "Perempuan", "160 cm", "60 kg", "Jl. Sudirman No. 12, Bandung"),
            ("17 Jul 2026, 10:00", "2406-003", "Sdr. Andi", "Mild", "25 Tahun", "Laki-laki", "175 cm", "68 kg", "Jl. Diponegoro No. 8, Surabaya")
        ]
        
        self.view.table_sesi.setRowCount(len(dummy_sesi))
        for row, data in enumerate(dummy_sesi):
            item_tgl = QTableWidgetItem(data[0])
            item_tgl.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.view.table_sesi.setItem(row, 0, item_tgl)
            
            item_id = QTableWidgetItem(data[1])
            item_id.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.view.table_sesi.setItem(row, 1, item_id)
            
            item_nama = QTableWidgetItem(data[2])
            item_nama.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.view.table_sesi.setItem(row, 2, item_nama)
            
            # Badge Indikasi Kecemasan
            lbl_indikasi = QLabel(data[3])
            lbl_indikasi.setAlignment(Qt.AlignCenter)
            if data[3] == "Severe":
                lbl_indikasi.setStyleSheet("background-color: #E53E3E; color: #FFF; padding: 4px; border-radius: 4px; font-weight: bold;")
            elif data[3] == "Moderate":
                lbl_indikasi.setStyleSheet("background-color: #DD6B20; color: #FFF; padding: 4px; border-radius: 4px; font-weight: bold;")
            else:
                lbl_indikasi.setStyleSheet("background-color: #38A169; color: #FFF; padding: 4px; border-radius: 4px; font-weight: bold;")
                
            ind_widget = QWidget()
            ind_layout = QHBoxLayout(ind_widget)
            ind_layout.setContentsMargins(5, 5, 5, 5)
            ind_layout.addWidget(lbl_indikasi)
            self.view.table_sesi.setCellWidget(row, 3, ind_widget)
            
            # Kolom Aksi
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 5, 5, 5)
            action_layout.setSpacing(8)
            
            btn_detail = QPushButton(" Detail")
            btn_detail.setIcon(qta.icon('fa5s.eye', color='white'))
            btn_detail.setStyleSheet("color: white; font-weight: bold; background: #3182CE; border-radius: 4px; padding: 4px 8px; font-size: 11px;")
            btn_detail.setCursor(Qt.PointingHandCursor)
            
            btn_pdf = QPushButton(" PDF")
            btn_pdf.setIcon(qta.icon('fa5s.file-pdf', color='white'))
            btn_pdf.setStyleSheet("color: white; font-weight: bold; background: #ED2224; border-radius: 4px; padding: 4px 8px; font-size: 11px;")
            btn_pdf.setCursor(Qt.PointingHandCursor)
            
            btn_excel = QPushButton(" Excel")
            btn_excel.setIcon(qta.icon('fa5s.file-excel', color='white'))
            btn_excel.setStyleSheet("color: white; font-weight: bold; background: #107C41; border-radius: 4px; padding: 4px 8px; font-size: 11px;")
            btn_excel.setCursor(Qt.PointingHandCursor)
            
            btn_detail.clicked.connect(lambda checked=False, d=data: self.open_detail_replay(d))
            btn_pdf.clicked.connect(lambda checked=False, d=data: self.export_pdf(d))
            btn_excel.clicked.connect(lambda checked=False, d=data: self.export_excel(d))
            
            action_layout.addWidget(btn_detail)
            action_layout.addWidget(btn_pdf)
            action_layout.addWidget(btn_excel)
            
            self.view.table_sesi.setCellWidget(row, 4, action_widget)
            
        self.view.lbl_info.setText(f"Menampilkan 1 hingga {len(dummy_sesi)} dari {len(dummy_sesi)} riwayat sesi")

    def export_excel(self, data):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import openpyxl
        
        # Bersihkan nama pasien untuk nama file
        safe_name = data[2].replace('.', '').replace(' ', '_')
        filepath, _ = QFileDialog.getSaveFileName(self.view, "Simpan Excel", f"Laporan_{safe_name}.xlsx", "Excel Files (*.xlsx)")
        if filepath:
            try:
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Laporan Sesi"
                
                # Header
                ws.append(["Tanggal Sesi", "ID Pasien", "Nama Pasien", "Indikasi Kecemasan"])
                # Data
                ws.append([data[0], data[1], data[2], data[3]])
                
                # Styling sederhana untuk Header
                from openpyxl.styles import Font
                for cell in ws[1]:
                    cell.font = Font(bold=True)
                    
                wb.save(filepath)
                QMessageBox.information(self.view, "Sukses", f"Data Excel berhasil diekspor ke:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Gagal menyimpan file:\n{str(e)}")

    def export_pdf(self, data):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        from PySide6.QtGui import QTextDocument
        from PySide6.QtPrintSupport import QPrinter
        
        safe_name = data[2].replace('.', '').replace(' ', '_')
        filepath, _ = QFileDialog.getSaveFileName(self.view, "Simpan PDF", f"Laporan_{safe_name}.pdf", "PDF Files (*.pdf)")
        if filepath:
            try:
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(filepath)
                
                doc = QTextDocument()
                html = f"""
                <div style="font-family: Arial, sans-serif; color: #2D3748;">
                    <h1 style='color: #2B6CB0; text-align: center;'>Laporan Analisis Fisiologis & Kecemasan</h1>
                    <hr style="border: 1px solid #E2E8F0;">
                    
                    <h2 style='color: #2D3748;'>1. Informasi Pasien & Sesi</h2>
                    <table width="100%" cellpadding="8" style="border-collapse: collapse; margin-bottom: 20px;">
                        <tr style="background-color: #F7FAFC;">
                            <td width="30%"><b>ID Pasien</b></td>
                            <td width="70%">{data[1]}</td>
                        </tr>
                        <tr>
                            <td><b>Nama Pasien</b></td>
                            <td>{data[2]}</td>
                        </tr>
                        <tr style="background-color: #F7FAFC;">
                            <td><b>Waktu Perekaman</b></td>
                            <td>{data[0]} (Durasi: 15 Menit 45 Detik)</td>
                        </tr>
                        <tr>
                            <td><b>Tingkat Kecemasan</b></td>
                            <td><b>{data[3]}</b></td>
                        </tr>
                    </table>
                    
                    <h2 style='color: #2D3748;'>2. Ringkasan Sinyal Fisiologis</h2>
                    <table border="1" width="100%" cellpadding="10" style="border-collapse: collapse; border-color: #CBD5E0; margin-bottom: 20px;">
                        <tr style="background-color: #EDF2F7; text-align: left;">
                            <th>Parameter Sensor</th>
                            <th>Rata-rata (Avg)</th>
                            <th>Puncak (Peak)</th>
                            <th>Interpretasi Baseline</th>
                        </tr>
                        <tr>
                            <td><b>Heart Rate (BPM)</b></td>
                            <td>84.2 bpm</td>
                            <td>112.5 bpm</td>
                            <td>Reaktivitas kardiovaskular tinggi</td>
                        </tr>
                        <tr>
                            <td><b>Skin Conductance (μS)</b></td>
                            <td>5.8 μS</td>
                            <td>9.1 μS</td>
                            <td>Aktivitas kelenjar keringat aktif</td>
                        </tr>
                        <tr>
                            <td><b>Skin Temperature (°C)</b></td>
                            <td>31.5 °C</td>
                            <td>33.2 °C</td>
                            <td>Sedikit menurun (Vasokonstriksi)</td>
                        </tr>
                    </table>

                    <h2 style='color: #2D3748;'>3. Kesimpulan & Observasi Medis</h2>
                    <p style="line-height: 1.6;">
                        Berdasarkan hasil pembacaan sensor biometrik di atas, terdapat pola fluktuasi yang kuat pada <i>Heart Rate</i> dan lonjakan signifikan pada <i>Galvanic Skin Response</i> (GSR) yang berkorelasi lurus dengan indikasi tingkat kecemasan <b>{data[3]}</b>. Pasien menunjukkan hiperaktivitas pada saraf simpatis selama sesi perekaman berlangsung.
                    </p>
                    
                    <br><br><br>
                    <table width="100%">
                        <tr>
                            <td width="60%"></td>
                            <td width="40%" style="text-align: center;">
                                <p>Mengetahui,</p>
                                <br><br><br>
                                <p><b>( Dokter / Terapis )</b></p>
                            </td>
                        </tr>
                    </table>
                </div>
                """
                doc.setHtml(html)
                doc.print_(printer)
                
                QMessageBox.information(self.view, "Sukses", f"Laporan PDF berhasil diekspor ke:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Gagal menyimpan PDF:\n{str(e)}")

    def open_detail_replay(self, data):
        from components.replay_dialog import ReplayDialog
        dialog = ReplayDialog(data, self.main_window)
        dialog.exec()
