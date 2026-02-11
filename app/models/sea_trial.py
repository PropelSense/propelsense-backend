"""
Sea Trial Model
Stores sea trial data for performance validation and comparison
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Enum
from datetime import datetime
import enum
from app.core.database import Base


class TrialStatus(str, enum.Enum):
    """Sea trial status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SeaTrial(Base):
    __tablename__ = "sea_trials"
    
    sea_trial_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Trial metadata
    trial_name = Column(String(200), nullable=False)
    vessel_id = Column(Integer)  # Link to vessel if vessel table exists
    vessel_name = Column(String(200), nullable=False)
    trial_date = Column(DateTime, nullable=False)
    status = Column(Enum(TrialStatus), default=TrialStatus.PLANNED, nullable=False)
    
    # Environmental conditions
    wind_speed = Column(Float)  # knots
    wind_direction = Column(Float)  # degrees
    wave_height = Column(Float)  # meters
    wave_period = Column(Float)  # seconds
    current_speed = Column(Float)  # knots
    current_direction = Column(Float)  # degrees
    water_temperature = Column(Float)  # celsius
    air_temperature = Column(Float)  # celsius
    water_depth = Column(Float)  # meters
    
    # Vessel condition
    displacement = Column(Float)  # tonnes
    draft_fore = Column(Float)  # meters
    draft_aft = Column(Float)  # meters
    trim = Column(Float)  # meters (fore - aft)
    
    # Performance metrics - Predicted (from model)
    predicted_speed = Column(Float)  # knots
    predicted_power = Column(Float)  # kW
    predicted_fuel_consumption = Column(Float)  # tonnes/day
    predicted_rpm = Column(Float)
    
    # Performance metrics - Actual (measured during trial)
    actual_speed = Column(Float)  # knots
    actual_power = Column(Float)  # kW
    actual_fuel_consumption = Column(Float)  # tonnes/day
    actual_rpm = Column(Float)
    
    # Performance analysis
    speed_deviation = Column(Float)  # percentage
    power_deviation = Column(Float)  # percentage
    fuel_deviation = Column(Float)  # percentage
    overall_performance_score = Column(Float)  # 0-100
    
    # Contract specifications
    contract_speed = Column(Float)  # knots
    contract_power = Column(Float)  # kW
    contract_fuel = Column(Float)  # tonnes/day
    meets_contract = Column(Integer)  # boolean: 1 = meets, 0 = does not meet
    
    # Additional data
    notes = Column(Text)
    test_location = Column(String(200))
    duration_hours = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<SeaTrial(id={self.sea_trial_id}, vessel={self.vessel_name}, date={self.trial_date})>"
