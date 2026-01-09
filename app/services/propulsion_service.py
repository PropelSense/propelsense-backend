"""
Propulsion Service - Business Logic Layer
"""
from typing import List
from datetime import datetime, timedelta
import random
from app.schemas.propulsion import PropulsionData, PropulsionResponse
from app.models.propulsion_model import get_model
import logging

logger = logging.getLogger(__name__)


class PropulsionService:
    """Service for handling propulsion data operations"""
    
    def __init__(self):
        """Initialize service with ML model"""
        try:
            self.model = get_model()
            logger.info("ML model loaded successfully in PropulsionService")
        except Exception as e:
            logger.warning(f"Failed to load ML model: {e}. Using fallback methods.")
            self.model = None
    
    async def get_data(self, limit: int = 100) -> List[PropulsionData]:
        """
        Get propulsion sensor data
        
        Args:
            limit: Number of records to return
            
        Returns:
            List of PropulsionData objects
        """
        # TODO: Replace with actual database query
        # This is sample data for demonstration
        data = []
        base_time = datetime.utcnow()
        
        for i in range(limit):
            data.append(PropulsionData(
                id=i + 1,
                timestamp=base_time - timedelta(minutes=i),
                rpm=random.uniform(1500, 3000),
                torque=random.uniform(100, 200),
                temperature=random.uniform(70, 95),
                power=random.uniform(25, 50),
                efficiency=random.uniform(85, 95)
            ))
        
        return data
    
    async def get_stats(self) -> PropulsionResponse:
        """
        Get propulsion statistics
        
        Returns:
            PropulsionResponse with statistics
        """
        # TODO: Replace with actual database aggregation
        # Sample statistics for demonstration
        return PropulsionResponse(
            total_records=1000,
            avg_power=38.5,
            max_power=45.2,
            min_power=20.1,
            avg_efficiency=91.2,
            avg_temperature=82.5
        )
    
    async def predict(self, rpm: float, torque: float, temperature: float) -> dict:
        """
        Predict power output based on input parameters using ML model
        
        Args:
            rpm: Rotations per minute
            torque: Torque value
            temperature: Operating temperature
            
        Returns:
            Prediction dictionary
        """
        try:
            # Use ML model if available
            if self.model and self.model.is_ready():
                # Preprocess input
                input_data = self.model.preprocess_input({
                    "rpm": rpm,
                    "torque": torque,
                    "temperature": temperature
                })
                
                # Get prediction from model
                prediction = self.model.predict(input_data)
                
                # Add input parameters to response
                prediction["inputs"] = {
                    "rpm": rpm,
                    "torque": torque,
                    "temperature": temperature
                }
                
                return prediction
            else:
                # Fallback to simple formula if model not available
                logger.warning("ML model not available, using fallback calculation")
                return self._fallback_prediction(rpm, torque, temperature)
                
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            # Return fallback on error
            return self._fallback_prediction(rpm, torque, temperature)
    
    def _fallback_prediction(self, rpm: float, torque: float, temperature: float) -> dict:
        """
        Fallback prediction method when ML model is unavailable
        
        Args:
            rpm: Rotations per minute
            torque: Torque value
            temperature: Operating temperature
            
        Returns:
            Prediction dictionary
        """
        # Simple formula: Power (kW) = (RPM * Torque) / 9549
        predicted_power = (rpm * torque) / 9549
        
        # Adjust for temperature efficiency
        temp_factor = 1.0 - ((temperature - 75) * 0.002)
        predicted_power *= temp_factor
        
        return {
            "predicted_power": round(predicted_power, 2),
            "confidence": 85.5,
            "model_version": "fallback-v1.0.0",
            "inputs": {
                "rpm": rpm,
                "torque": torque,
                "temperature": temperature
            },
            "note": "Using fallback formula (ML model not loaded)"
        }
