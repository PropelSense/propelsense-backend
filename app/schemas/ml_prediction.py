"""
Pydantic schemas for ML prediction
"""
from pydantic import BaseModel, Field
from typing import Literal, Dict, Optional

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


class PowerPredictionResponse(BaseModel):
    """Response from power prediction"""
    predicted_power_kw: float = Field(..., description="Predicted power in kilowatts")
    predicted_power_mw: float = Field(..., description="Predicted power in megawatts")
    model_used: str = Field(..., description="Model that was used")
    metadata: Dict = Field(..., description="Additional information about prediction")
    
    class Config:
        json_schema_extra = {
            "example": {
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
                }
            }
        }


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
                    },
                    "random_forest": {
                        "name": "Random Forest",
                        "recommended": False,
                        "size": "17 GB",
                        "warning": "Very large, may cause memory issues"
                    }
                }
            }
        }
