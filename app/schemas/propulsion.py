"""
Propulsion Data Schemas (Pydantic Models)
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PropulsionData(BaseModel):
    """Schema for propulsion sensor data"""
    
    id: Optional[int] = None
    timestamp: datetime
    rpm: float = Field(..., description="Rotations per minute")
    torque: float = Field(..., description="Torque in Nm")
    temperature: float = Field(..., description="Temperature in Celsius")
    power: float = Field(..., description="Power output in kW")
    efficiency: float = Field(..., ge=0, le=100, description="Efficiency percentage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "timestamp": "2026-01-09T12:00:00",
                "rpm": 2500.0,
                "torque": 150.5,
                "temperature": 85.2,
                "power": 39.8,
                "efficiency": 92.5
            }
        }


class PropulsionResponse(BaseModel):
    """Schema for propulsion statistics response"""
    
    total_records: int
    avg_power: float
    max_power: float
    min_power: float
    avg_efficiency: float
    avg_temperature: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_records": 1000,
                "avg_power": 38.5,
                "max_power": 45.2,
                "min_power": 20.1,
                "avg_efficiency": 91.2,
                "avg_temperature": 82.5
            }
        }


class PredictionRequest(BaseModel):
    """Schema for power prediction request"""
    
    rpm: float = Field(..., gt=0, description="Rotations per minute")
    torque: float = Field(..., gt=0, description="Torque in Nm")
    temperature: float = Field(..., description="Temperature in Celsius")


class PredictionResponse(BaseModel):
    """Schema for power prediction response"""
    
    predicted_power: float
    confidence: float = Field(..., ge=0, le=100)
    model_version: str
