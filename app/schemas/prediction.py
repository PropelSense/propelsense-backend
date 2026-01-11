"""
Pydantic Schemas for Prediction History
Request/Response models for API validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PredictionRequest(BaseModel):
    """Request schema for power prediction"""
    speed_through_water: float = Field(..., description="Speed through water in knots")
    wind_speed: Optional[float] = Field(None, description="Wind speed in m/s")
    draft_fore: Optional[float] = Field(None, description="Draft fore in meters")
    draft_aft: Optional[float] = Field(None, description="Draft aft in meters")
    wave_height: Optional[float] = Field(None, description="Wave height in meters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "speed_through_water": 3245,
                "wind_speed": 523,
                "draft_fore": 523,
                "draft_aft": 234,
                "wave_height": 324
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for power prediction"""
    prediction_history_id: int
    predicted_power: float
    confidence_score: Optional[float]
    efficiency: Optional[float]
    model_version: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class VesselCreate(BaseModel):
    """Request schema for creating a vessel"""
    vessel_name: str = Field(..., min_length=1, max_length=100)
    vessel_type: Optional[str] = Field(None, max_length=50)
    imo_number: Optional[str] = Field(None, max_length=20)


class VesselResponse(BaseModel):
    """Response schema for vessel data"""
    vessel_id: int
    vessel_name: str
    vessel_type: Optional[str]
    imo_number: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
