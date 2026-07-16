from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from datetime import datetime
from .database import Base

class SensorRecord(Base):
    __tablename__ = "sensor_records"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    heart_rate = Column(Float, nullable=True)
    spo2 = Column(Float, nullable=True)
    gsr_value = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
