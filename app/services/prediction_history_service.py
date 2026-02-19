"""
Prediction History Service
CRUD operations for ML prediction history
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract
from datetime import datetime, timedelta
import logging

from app.models.prediction_history import PredictionHistory
from app.schemas.ml_prediction import (
    PredictionHistoryResponse,
    PredictionHistoryListResponse,
    PredictionStatsResponse
)

logger = logging.getLogger(__name__)


class PredictionHistoryService:
    """Service for managing prediction history"""
    
    def __init__(self, db: Session):
        """Initialize service with database session"""
        self.db = db
    
    def create_prediction(
        self,
        user_id: str,
        user_email: Optional[str],
        input_features: dict,
        predicted_power_kw: float,
        predicted_power_mw: float,
        model_used: str,
        model_metadata: dict
    ) -> PredictionHistory:
        """
        Create a new prediction history entry
        
        Args:
            user_id: User's Supabase ID
            user_email: User's email
            input_features: Dict of input features
            predicted_power_kw: Predicted power in kW
            predicted_power_mw: Predicted power in MW
            model_used: Model name used
            model_metadata: Additional model info
            
        Returns:
            Created PredictionHistory object
        """
        prediction = PredictionHistory(
            user_id=user_id,
            user_email=user_email,
            input_features=input_features,
            # Individual fields for querying
            draft_aft_telegram=input_features.get("draft_aft_telegram"),
            draft_fore_telegram=input_features.get("draft_fore_telegram"),
            stw=input_features.get("stw"),
            diff_speed_overground=input_features.get("diff_speed_overground"),
            awind_vcomp_provider=input_features.get("awind_vcomp_provider"),
            awind_ucomp_provider=input_features.get("awind_ucomp_provider"),
            rcurrent_vcomp=input_features.get("rcurrent_vcomp"),
            rcurrent_ucomp=input_features.get("rcurrent_ucomp"),
            comb_wind_swell_wave_height=input_features.get("comb_wind_swell_wave_height"),
            time_since_dry_dock=input_features.get("timeSinceDryDock"),
            # Predictions
            predicted_power_kw=predicted_power_kw,
            predicted_power_mw=predicted_power_mw,
            model_used=model_used,
            model_metadata=model_metadata
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        logger.info(f"Created prediction history {prediction.id} for user {user_id}")
        return prediction
    
    def get_user_predictions(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> PredictionHistoryListResponse:
        """
        Get paginated prediction history for a user
        
        Args:
            user_id: User's ID
            page: Page number (1-indexed)
            page_size: Number of items per page
            sort_by: Field to sort by
            sort_desc: Sort descending if True
            
        Returns:
            PredictionHistoryListResponse with predictions and pagination info
        """
        # Base query
        query = self.db.query(PredictionHistory).filter(
            PredictionHistory.user_id == user_id
        )
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(PredictionHistory, sort_by, PredictionHistory.created_at)
        if sort_desc:
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
        
        # Apply pagination
        offset = (page - 1) * page_size
        predictions = query.offset(offset).limit(page_size).all()
        
        return PredictionHistoryListResponse(
            total=total,
            predictions=[PredictionHistoryResponse.model_validate(p) for p in predictions],
            page=page,
            page_size=page_size
        )
    
    def get_prediction_by_id(
        self,
        prediction_id: int,
        user_id: str
    ) -> Optional[PredictionHistory]:
        """
        Get a specific prediction by ID (user must own it)
        
        Args:
            prediction_id: Prediction ID
            user_id: User's ID (for authorization)
            
        Returns:
            PredictionHistory object or None
        """
        return self.db.query(PredictionHistory).filter(
            PredictionHistory.id == prediction_id,
            PredictionHistory.user_id == user_id
        ).first()
    
    def delete_prediction(
        self,
        prediction_id: int,
        user_id: str
    ) -> bool:
        """
        Delete a prediction (user must own it)
        
        Args:
            prediction_id: Prediction ID
            user_id: User's ID (for authorization)
            
        Returns:
            True if deleted, False if not found
        """
        prediction = self.get_prediction_by_id(prediction_id, user_id)
        if not prediction:
            return False
        
        self.db.delete(prediction)
        self.db.commit()
        logger.info(f"Deleted prediction {prediction_id} for user {user_id}")
        return True
    
    def get_user_stats(self, user_id: str) -> PredictionStatsResponse:
        """
        Get statistics about user's predictions
        
        Args:
            user_id: User's ID
            
        Returns:
            PredictionStatsResponse with statistics
        """
        # Get all predictions for user
        predictions = self.db.query(PredictionHistory).filter(
            PredictionHistory.user_id == user_id
        ).all()
        
        if not predictions:
            return PredictionStatsResponse(
                total_predictions=0,
                avg_power_kw=0.0,
                max_power_kw=0.0,
                min_power_kw=0.0,
                most_recent=None,
                predictions_this_month=0
            )
        
        # Calculate statistics
        power_values = [p.predicted_power_kw for p in predictions]
        
        # Get predictions from this month
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        predictions_this_month = self.db.query(func.count(PredictionHistory.id)).filter(
            PredictionHistory.user_id == user_id,
            PredictionHistory.created_at >= month_start
        ).scalar()
        
        return PredictionStatsResponse(
            total_predictions=len(predictions),
            avg_power_kw=round(sum(power_values) / len(power_values), 2),
            max_power_kw=round(max(power_values), 2),
            min_power_kw=round(min(power_values), 2),
            most_recent=predictions[0].created_at if predictions else None,
            predictions_this_month=predictions_this_month or 0
        )
    
    def get_recent_predictions(
        self,
        user_id: str,
        limit: int = 5
    ) -> List[PredictionHistory]:
        """
        Get most recent predictions for a user
        
        Args:
            user_id: User's ID
            limit: Number of predictions to return
            
        Returns:
            List of PredictionHistory objects
        """
        return self.db.query(PredictionHistory).filter(
            PredictionHistory.user_id == user_id
        ).order_by(desc(PredictionHistory.created_at)).limit(limit).all()
    
    def delete_all_user_predictions(self, user_id: str) -> int:
        """
        Delete all predictions for a user
        
        Args:
            user_id: User's ID
            
        Returns:
            Number of predictions deleted
        """
        count = self.db.query(PredictionHistory).filter(
            PredictionHistory.user_id == user_id
        ).delete()
        self.db.commit()
        logger.info(f"Deleted {count} predictions for user {user_id}")
        return count
