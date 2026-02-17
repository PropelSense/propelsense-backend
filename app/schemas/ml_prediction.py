"""
Pydantic schemas for ML prediction
"""
from pydantic import BaseModel, Field
from typing import Literal, Dict, Optional, List
from datetime import datetime

class VesselFeatures(BaseModel):
    """Input features for vessel power prediction"""
    
    # Vessel features
    draft_aft_telegram: float = Field(..., description="Aft draft in meters", ge=0, le=20)
    draft_fore_telegram: float = Field(..., description="Forward draft in meters", ge=0, le=20)
    stw: float = Field(..., description="Speed through water in knots", ge=0, le=40)
    diff_speed_overground: float = Field(..., description="Speed difference", ge=-10, le=10)
    
    # Wind features
    awind_vcomp_provider: float = Field(..., description="Apparent wind V component (m/s)", ge=-50, le=50)
    awind_ucomp_provider: float = Field(..., description="Apparent wind U component (m/s)", ge=-50, le=50)
    
    # Current features
    rcurrent_vcomp: float = Field(..., description="Current V component (m/s)", ge=-10, le=10)
    rcurrent_ucomp: float = Field(..., description="Current U component (m/s)", ge=-10, le=10)
    
    # Wave features
    comb_wind_swell_wave_height: float = Field(..., description="Combined wave height in meters", ge=0, le=20)
    
    # Operational features
    timeSinceDryDock: float = Field(..., description="Days since last dry dock", ge=0, le=3650)
    
    class Config:
        json_schema_extra = {
            "example": {
                "draft_aft_telegram": 8.75,
                "draft_fore_telegram": 8.55,
                "stw": 18.2,
                "diff_speed_overground": 0.1,
                "awind_vcomp_provider": 5.2,
                "awind_ucomp_provider": 3.1,
                "rcurrent_vcomp": 0.05,
                "rcurrent_ucomp": -0.08,
                "comb_wind_swell_wave_height": 1.2,
                "timeSinceDryDock": 120
            }
        }


class PowerPredictionRequest(BaseModel):
    """Request for power prediction"""
    features: VesselFeatures
    save_to_history: bool = Field(
        default=True,
        description="Save this prediction to user's history"
    )


class PowerPredictionResponse(BaseModel):
    """Response from power prediction"""
    id: Optional[int] = Field(None, description="Prediction history ID (if saved)")
    predicted_power_kw: float = Field(..., description="Predicted power in kilowatts")
    predicted_power_mw: float = Field(..., description="Predicted power in megawatts")
    model_used: str = Field(..., description="Model that was used")
    metadata: Dict = Field(..., description="Additional information about prediction")
    created_at: Optional[datetime] = Field(None, description="Timestamp of prediction")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "predicted_power_kw": 18500.5,
                "predicted_power_mw": 18.5,
                "model_used": "xgboost",
                "metadata": {
                    "model_used": "xgboost",
                    "n_features": 19,
                    "unit": "kW",
                    "model_performance": {
                        "mae_dev_in": 866,
                        "r2_dev_in": 0.978
                    }
                },
                "created_at": "2026-02-17T10:30:00"
            }
        }


class PredictionHistoryResponse(BaseModel):
    """Response schema for prediction history"""
    id: int
    user_id: str
    user_email: Optional[str]
    
    # Input features
    draft_aft_telegram: Optional[float]
    draft_fore_telegram: Optional[float]
    stw: Optional[float]
    diff_speed_overground: Optional[float]
    awind_vcomp_provider: Optional[float]
    awind_ucomp_provider: Optional[float]
    rcurrent_vcomp: Optional[float]
    rcurrent_ucomp: Optional[float]
    comb_wind_swell_wave_height: Optional[float]
    timeSinceDryDock: Optional[float]
    
    # Prediction results
    predicted_power_kw: float
    predicted_power_mw: float
    
    # Model info
    model_used: str
    model_metadata: Optional[Dict]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PredictionHistoryListResponse(BaseModel):
    """Response for list of prediction history"""
    total: int
    predictions: List[PredictionHistoryResponse]
    page: int
    page_size: int


class PredictionStatsResponse(BaseModel):
    """Statistics about user's predictions"""
    total_predictions: int
    avg_power_kw: float
    max_power_kw: float
    min_power_kw: float
    most_recent: Optional[datetime]
    predictions_this_month: int


class AvailableModelsResponse(BaseModel):
    """Available ML models"""
    models: Dict[str, Dict] = Field(..., description="Available models and their info")
    
    class Config:
        json_schema_extra = {
            "example": {
                "models": {
                    "xgboost": {
                        "name": "XGBoost",
                        "recommended": True,
                        "size": "993 KB",
                        "performance": {
                            "mae": 866,
                            "r2": 0.978
                        }
                    }
                }
            }
        }
