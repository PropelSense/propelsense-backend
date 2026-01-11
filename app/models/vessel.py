"""
Vessel Model
Basic ship/vessel information
"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.database import Base


class Vessel(Base):
    __tablename__ = "vessels"
    
    vessel_id = Column(Integer, primary_key=True, autoincrement=True)
    vessel_name = Column(String(100), nullable=False)
    vessel_type = Column(String(50))
    imo_number = Column(String(20), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Vessel(vessel_id={self.vessel_id}, name={self.vessel_name})>"
