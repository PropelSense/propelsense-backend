"""
Prediction History Model
Stores user inputs and ML prediction results
"""
from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from app.core.database import Base


class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    
    prediction_history_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Input parameters from user
    speed_through_water = Column(Float, nullable=False)
    wind_speed = Column(Float)
    draft_fore = Column(Float)
    draft_aft = Column(Float)
    wave_height = Column(Float)
    
    # Prediction results
    predicted_power = Column(Float, nullable=False)
    confidence_score = Column(Float)
    efficiency = Column(Float)
    
    # Metadata
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<PredictionHistory(id={self.prediction_history_id}, power={self.predicted_power})>"
