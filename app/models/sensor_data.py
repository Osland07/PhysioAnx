from sqlalchemy import Column, Integer, Float, DateTime, String
from datetime import datetime
from .database import Base

class SensorData(Base):
    __tablename__ = "sensor_data"

    # Kolom ID utama (Otomatis bertambah: 1, 2, 3...)
    id = Column(Integer, primary_key=True, index=True)
    
    # Kolom waktu otomatis tercatat saat data masuk
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # --- CONTOH STRUKTUR DATA ---
    # (Kita bisa ubah ini sesuai sensor ESP Anda)
    heart_rate = Column(Float, nullable=True)  # Contoh: Detak Jantung
    gsr_value = Column(Float, nullable=True)   # Contoh: Galvanic Skin Response (Sensor Kecemasan)
    temperature = Column(Float, nullable=True) # Contoh: Suhu Tubuh
    status = Column(String, nullable=True)     # Contoh: "Normal", "Cemas", dll
