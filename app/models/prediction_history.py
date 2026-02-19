"""
Prediction History Model
Stores user inputs and ML prediction results
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, JSON
from datetime import datetime
from app.core.database import Base


class PredictionHistory(Base):
    __tablename__ = "prediction_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # User association
    user_id = Column(String(255), nullable=False, index=True)  # Supabase user ID
    user_email = Column(String(255), nullable=True)
    
    # Input features (stored as JSON for flexibility)
    input_features = Column(JSON, nullable=False)
    
    # Individual input fields for easy que rying
    draft_aft_telegram = Column(Float)
    draft_fore_telegram = Column(Float)
    stw = Column(Float)
    diff_speed_overground = Column(Float)
    awind_vcomp_provider = Column(Float)
    awind_ucomp_provider = Column(Float)
    rcurrent_vcomp = Column(Float)
    rcurrent_ucomp = Column(Float)
    comb_wind_swell_wave_height = Column(Float)
    time_since_dry_dock = Column(Float)
    
    # Prediction results
    predicted_power_kw = Column(Float, nullable=False)
    predicted_power_mw = Column(Float, nullable=False)
    
    # Model metadata
    model_used = Column(String(50), nullable=False, default="xgboost")
    model_metadata = Column(JSON)  # Stores performance metrics, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<PredictionHistory(id={self.id}, user={self.user_email}, power={self.predicted_power_kw} kW)>"
