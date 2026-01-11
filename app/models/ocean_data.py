"""
Ocean Data Model
Store ocean/marine conditions
"""
from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from app.core.database import Base


class OceanData(Base):
    __tablename__ = "ocean_data"
    
    ocean_data_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Location
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Ocean conditions
    sea_surface_temperature = Column(Float)
    wave_height = Column(Float)
    wave_period = Column(Float)
    current_speed = Column(Float)
    current_direction = Column(Float)
    
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<OceanData(id={self.ocean_data_id}, wave_height={self.wave_height})>"
