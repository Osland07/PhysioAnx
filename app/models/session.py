from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String
from datetime import datetime
from .database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    psychologist_notes = Column(Text, nullable=True)
    anxiety_level = Column(String(50), nullable=True)
