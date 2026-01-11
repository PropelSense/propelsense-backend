"""
Weather Data Model
Store weather conditions for analysis
"""
from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from app.core.database import Base


class WeatherData(Base):
    __tablename__ = "weather_data"
    
    weather_data_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Location
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(String(100))
    
    # Weather conditions
    temperature = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    pressure = Column(Float)
    humidity = Column(Float)
    
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<WeatherData(id={self.weather_data_id}, location={self.location_name})>"
