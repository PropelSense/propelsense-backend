"""
Sea Trial Schemas - Request/Response Models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TrialStatus(str, Enum):
    """Sea trial status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SeaTrialBase(BaseModel):
    """Base schema for sea trial"""
    trial_name: str = Field(..., min_length=1, max_length=200)
    vessel_name: str = Field(..., min_length=1, max_length=200)
    trial_date: datetime
    status: TrialStatus = TrialStatus.PLANNED
    
    # Environmental conditions
    wind_speed: Optional[float] = Field(None, ge=0)
    wind_direction: Optional[float] = Field(None, ge=0, le=360)
    wave_height: Optional[float] = Field(None, ge=0)
    wave_period: Optional[float] = Field(None, ge=0)
    current_speed: Optional[float] = Field(None, ge=0)
    current_direction: Optional[float] = Field(None, ge=0, le=360)
    water_temperature: Optional[float] = None
    air_temperature: Optional[float] = None
    water_depth: Optional[float] = Field(None, ge=0)
    
    # Vessel condition
    displacement: Optional[float] = Field(None, ge=0)
    draft_fore: Optional[float] = Field(None, ge=0)
    draft_aft: Optional[float] = Field(None, ge=0)
    trim: Optional[float] = None
    
    # Predicted performance
    predicted_speed: Optional[float] = Field(None, ge=0)
    predicted_power: Optional[float] = Field(None, ge=0)
    predicted_fuel_consumption: Optional[float] = Field(None, ge=0)
    predicted_rpm: Optional[float] = Field(None, ge=0)
    
    # Actual performance
    actual_speed: Optional[float] = Field(None, ge=0)
    actual_power: Optional[float] = Field(None, ge=0)
    actual_fuel_consumption: Optional[float] = Field(None, ge=0)
    actual_rpm: Optional[float] = Field(None, ge=0)
    
    # Contract specifications
    contract_speed: Optional[float] = Field(None, ge=0)
    contract_power: Optional[float] = Field(None, ge=0)
    contract_fuel: Optional[float] = Field(None, ge=0)
    
    # Additional data
    notes: Optional[str] = None
    test_location: Optional[str] = Field(None, max_length=200)
    duration_hours: Optional[float] = Field(None, ge=0)


class SeaTrialCreate(SeaTrialBase):
    """Schema for creating a new sea trial"""
    vessel_id: Optional[int] = None


class SeaTrialUpdate(BaseModel):
    """Schema for updating an existing sea trial"""
    trial_name: Optional[str] = Field(None, min_length=1, max_length=200)
    vessel_name: Optional[str] = Field(None, min_length=1, max_length=200)
    trial_date: Optional[datetime] = None
    status: Optional[TrialStatus] = None
    
    # Environmental conditions
    wind_speed: Optional[float] = Field(None, ge=0)
    wind_direction: Optional[float] = Field(None, ge=0, le=360)
    wave_height: Optional[float] = Field(None, ge=0)
    wave_period: Optional[float] = Field(None, ge=0)
    current_speed: Optional[float] = Field(None, ge=0)
    current_direction: Optional[float] = Field(None, ge=0, le=360)
    water_temperature: Optional[float] = None
    air_temperature: Optional[float] = None
    water_depth: Optional[float] = Field(None, ge=0)
    
    # Vessel condition
    displacement: Optional[float] = Field(None, ge=0)
    draft_fore: Optional[float] = Field(None, ge=0)
    draft_aft: Optional[float] = Field(None, ge=0)
    trim: Optional[float] = None
    
    # Predicted performance
    predicted_speed: Optional[float] = Field(None, ge=0)
    predicted_power: Optional[float] = Field(None, ge=0)
    predicted_fuel_consumption: Optional[float] = Field(None, ge=0)
    predicted_rpm: Optional[float] = Field(None, ge=0)
    
    # Actual performance
    actual_speed: Optional[float] = Field(None, ge=0)
    actual_power: Optional[float] = Field(None, ge=0)
    actual_fuel_consumption: Optional[float] = Field(None, ge=0)
    actual_rpm: Optional[float] = Field(None, ge=0)
    
    # Contract specifications
    contract_speed: Optional[float] = Field(None, ge=0)
    contract_power: Optional[float] = Field(None, ge=0)
    contract_fuel: Optional[float] = Field(None, ge=0)
    
    # Additional data
    notes: Optional[str] = None
    test_location: Optional[str] = Field(None, max_length=200)
    duration_hours: Optional[float] = Field(None, ge=0)


class SeaTrialResponse(SeaTrialBase):
    """Schema for sea trial response"""
    sea_trial_id: int
    vessel_id: Optional[int] = None
    
    # Performance analysis (calculated)
    speed_deviation: Optional[float] = None
    power_deviation: Optional[float] = None
    fuel_deviation: Optional[float] = None
    overall_performance_score: Optional[float] = None
    meets_contract: Optional[bool] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PerformanceComparison(BaseModel):
    """Detailed performance comparison"""
    metric: str
    predicted: Optional[float] = None
    actual: Optional[float] = None
    deviation: Optional[float] = None  # percentage
    deviation_absolute: Optional[float] = None
    unit: str
    status: str  # "better", "worse", "within_tolerance", "unknown"


class SeaTrialAnalysis(BaseModel):
    """Comprehensive sea trial analysis"""
    sea_trial_id: int
    trial_name: str
    vessel_name: str
    trial_date: datetime
    status: TrialStatus
    
    # Performance comparisons
    speed_comparison: PerformanceComparison
    power_comparison: PerformanceComparison
    fuel_comparison: PerformanceComparison
    rpm_comparison: PerformanceComparison
    
    # Overall assessment
    overall_performance_score: float
    meets_contract: bool
    summary: str
    recommendations: list[str]


class SeaTrialSummary(BaseModel):
    """Summary statistics for multiple sea trials"""
    total_trials: int
    completed_trials: int
    avg_performance_score: Optional[float] = None
    trials_meeting_contract: int
    avg_speed_deviation: Optional[float] = None
    avg_power_deviation: Optional[float] = None
    avg_fuel_deviation: Optional[float] = None
