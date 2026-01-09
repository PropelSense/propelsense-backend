"""
Propulsion Data Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.propulsion import PropulsionData, PropulsionResponse
from app.services.propulsion_service import PropulsionService

router = APIRouter()
service = PropulsionService()


@router.get("/data", response_model=List[PropulsionData])
async def get_propulsion_data(limit: int = 100):
    """
    Get propulsion sensor data
    
    Args:
        limit: Number of records to return
        
    Returns:
        List of propulsion data points
    """
    try:
        data = await service.get_data(limit=limit)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=PropulsionResponse)
async def get_propulsion_stats():
    """
    Get propulsion statistics
    
    Returns:
        Propulsion statistics and metrics
    """
    try:
        stats = await service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predict")
async def predict_power(
    rpm: float,
    torque: float,
    temperature: float,
):
    """
    Predict propulsion power based on input parameters
    
    Args:
        rpm: Rotations per minute
        torque: Torque value
        temperature: Operating temperature
        
    Returns:
        Predicted power output
    """
    try:
        prediction = await service.predict(rpm, torque, temperature)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
