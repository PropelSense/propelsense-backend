"""
ML Prediction endpoints
"""
from fastapi import APIRouter, HTTPException, status
from app.schemas.ml_prediction import (
    PowerPredictionRequest,
    PowerPredictionResponse,
    AvailableModelsResponse
)
from app.services.ml_service import get_ml_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/predict/power", 
             response_model=PowerPredictionResponse,
             summary="Predict vessel propulsion power",
             description="Predict required propulsion power using XGBoost model")
async def predict_power(request: PowerPredictionRequest):
    """
    Predict vessel propulsion power consumption using XGBoost
    
    - **features**: Vessel and environmental input features
    
    Returns predicted power in kW and MW with metadata.
    Model is downloaded once from Hugging Face Hub and cached locally (993 KB).
    """
    try:
        ml_service = get_ml_service()
        
        # Convert Pydantic model to dict
        features_dict = request.features.dict()
        
        # Make prediction
        logger.info("Making prediction with XGBoost model")
        prediction_kw, metadata = ml_service.predict(features_dict)
        
        # Convert to MW
        prediction_mw = round(prediction_kw / 1000, 2)
        
        return PowerPredictionResponse(
            predicted_power_kw=round(prediction_kw, 2),
            predicted_power_mw=prediction_mw,
            model_used="xgboost",
            metadata=metadata
        )
        
    except MemoryError as e:
        logger.error(f"Memory error during prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            detail="Insufficient memory to load model."
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid input features: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.get("/models/available",
            response_model=AvailableModelsResponse,
            summary="Get available ML models",
            description="Get information about the XGBoost model")
async def get_available_models():
    """
    Get information about the XGBoost model
    
    Returns model name, performance metrics, and info.
    """
    models_info = {
        "xgboost": {
            "name": "XGBoost",
            "recommended": True,
            "size": "993 KB",
            "description": "Fast gradient boosting model with excellent performance",
            "performance": {
                "mae_dev_in_kw": 866,
                "mae_dev_out_kw": 1435,
                "r2_dev_in": 0.978,
                "r2_dev_out": 0.906
            },
            "memory_usage": "Low",
            "load_time": "Fast (<1s)",
            "status": "Production ready"
        }
    }
    
    return AvailableModelsResponse(models=models_info)


@router.get("/models/status",
            summary="Check ML model status",
            description="Check which models are currently loaded in memory")
async def get_model_status():
    """
    Get status of loaded models
    
    Returns which models are currently loaded in memory.
    """
    ml_service = get_ml_service()
    
    status_info = {
        "xgboost_loaded": ml_service.xgb_model is not None,
        "feature_scaler_loaded": ml_service.feature_scaler is not None,
        "cache_directory": ml_service.cache_dir,
        "model_source": "Hugging Face Hub",
        "repo_id": ml_service.repo_id
    }
    
    return status_info
