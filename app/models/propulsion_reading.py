"""
Propulsion Reading Model
Actual sensor data from vessel propulsion systems
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from datetime import datetime
from app.core.database import Base


class PropulsionReading(Base):
    __tablename__ = "propulsion_readings"
    
    propulsion_reading_id = Column(Integer, primary_key=True, autoincrement=True)
    vessel_id = Column(Integer, ForeignKey('vessels.vessel_id'))
    
    # Sensor readings
    rpm = Column(Float, nullable=False)
    torque = Column(Float)
    temperature = Column(Float)
    power_output = Column(Float, nullable=False)
    fuel_consumption = Column(Float)
    
    reading_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<PropulsionReading(id={self.propulsion_reading_id}, power={self.power_output})>"
