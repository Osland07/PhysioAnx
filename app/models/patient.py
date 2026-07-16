from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float
from datetime import datetime
from .database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    no_rm = Column(String(50), unique=True, index=True)
    full_name = Column(String, index=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(1)) # 'L' untuk Laki-laki, 'P' untuk Perempuan
    height = Column(Integer, nullable=True) # cm
    weight = Column(Float, nullable=True) # kg
    address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
