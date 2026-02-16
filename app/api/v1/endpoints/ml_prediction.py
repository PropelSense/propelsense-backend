"""
ML Prediction endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.schemas.ml_prediction import (
    PowerPredictionRequest,
    PowerPredictionResponse,
    PredictionHistoryResponse,
    PredictionHistoryListResponse,
    PredictionStatsResponse,
    AvailableModelsResponse
)
from app.services.ml_service import get_ml_service
from app.services.prediction_history_service import PredictionHistoryService
from app.core.database import get_db
from app.core.auth import require_auth
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/predict/power", 
             response_model=PowerPredictionResponse,
             summary="Predict vessel propulsion power",
             description="Predict required propulsion power using XGBoost model")
async def predict_power(
    request: PowerPredictionRequest,
    user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Predict vessel propulsion power consumption using XGBoost
    
    - **features**: Vessel and environmental input features
    - **save_to_history**: Whether to save prediction to user's history (default: true)
    
    Returns predicted power in kW and MW with metadata.
    Model is downloaded once from Hugging Face Hub and cached locally (993 KB).
    """
    try:
        ml_service = get_ml_service()
        
        # Convert Pydantic model to dict
        features_dict = request.features.dict()
        
        # Make prediction
        logger.info(f"Making prediction with XGBoost model for user {user['email']}")
        prediction_kw, metadata = ml_service.predict(features_dict)
        
        # Convert to MW
        prediction_mw = round(prediction_kw / 1000, 2)
        
        # Save to history if requested
        prediction_id = None
        created_at = None
        
        if request.save_to_history:
            try:
                history_service = PredictionHistoryService(db)
                prediction_record = history_service.create_prediction(
                    user_id=user['id'],
                    user_email=user['email'],
                    input_features=features_dict,
                    predicted_power_kw=round(prediction_kw, 2),
                    predicted_power_mw=prediction_mw,
                    model_used="xgboost",
                    model_metadata=metadata
                )
                prediction_id = prediction_record.id
                created_at = prediction_record.created_at
                logger.info(f"Saved prediction {prediction_id} to history")
            except Exception as e:
                logger.error(f"Failed to save prediction to history: {str(e)}")
                # Don't fail the request if history save fails
        
        return PowerPredictionResponse(
            id=prediction_id,
            predicted_power_kw=round(prediction_kw, 2),
            predicted_power_mw=prediction_mw,
            model_used="xgboost",
            metadata=metadata,
            created_at=created_at
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


# ==================== Prediction History Endpoints ====================

@router.get("/history",
            response_model=PredictionHistoryListResponse,
            summary="Get prediction history",
            description="Get user's prediction history with pagination")
async def get_prediction_history(
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_desc: bool = True,
    user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Get paginated prediction history for the authenticated user
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **sort_by**: Field to sort by (default: created_at)
    - **sort_desc**: Sort descending (default: true)
    """
    try:
        # Validate page_size
        if page_size > 100:
            page_size = 100
        
        history_service = PredictionHistoryService(db)
        return history_service.get_user_predictions(
            user_id=user['id'],
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
    except Exception as e:
        logger.error(f"Error fetching prediction history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch prediction history: {str(e)}"
        )


@router.get("/history/{prediction_id}",
            response_model=PredictionHistoryResponse,
            summary="Get specific prediction",
            description="Get a specific prediction by ID")
async def get_prediction(
    prediction_id: int,
    user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Get a specific prediction by ID (user must own it)
    """
    try:
        history_service = PredictionHistoryService(db)
        prediction = history_service.get_prediction_by_id(prediction_id, user['id'])
        
        if not prediction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prediction {prediction_id} not found"
            )
        
        return PredictionHistoryResponse.model_validate(prediction)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prediction {prediction_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch prediction: {str(e)}"
        )


@router.delete("/history/{prediction_id}",
               summary="Delete prediction",
               description="Delete a specific prediction from history")
async def delete_prediction(
    prediction_id: int,
    user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Delete a specific prediction (user must own it)
    """
    try:
        history_service = PredictionHistoryService(db)
        deleted = history_service.delete_prediction(prediction_id, user['id'])
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Prediction {prediction_id} not found"
            )
        
        return {"message": f"Prediction {prediction_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prediction {prediction_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete prediction: {str(e)}"
        )


@router.get("/history/stats/summary",
            response_model=PredictionStatsResponse,
            summary="Get prediction statistics",
            description="Get statistics about user's predictions")
async def get_prediction_stats(
    user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Get statistics about the authenticated user's predictions
    
    Returns:
    - Total predictions
    - Average, max, min power
    - Most recent prediction timestamp
    - Predictions this month
    """
    try:
        history_service = PredictionHistoryService(db)
        return history_service.get_user_stats(user['id'])
    except Exception as e:
        logger.error(f"Error fetching prediction stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch prediction stats: {str(e)}"
        )


@router.delete("/history",
               summary="Delete all predictions",
               description="Delete all predictions for the authenticated user")
async def delete_all_predictions(
    user: dict = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Delete all prediction history for the authenticated user
    
    ⚠️ Warning: This action cannot be undone!
    """
    try:
        history_service = PredictionHistoryService(db)
        count = history_service.delete_all_user_predictions(user['id'])
        
        return {
            "message": f"Deleted {count} predictions",
            "count": count
        }
    except Exception as e:
        logger.error(f"Error deleting all predictions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete predictions: {str(e)}"
        )
