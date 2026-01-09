"""
Base Model Interface

All ML models should inherit from this base class to ensure
consistent interface across different model implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """
    Abstract base class for all ML models
    
    This provides a consistent interface for model loading,
    prediction, and metadata management.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the model
        
        Args:
            model_path: Path to the saved model file (optional)
        """
        self.model_path = model_path
        self.model = None
        self.is_loaded = False
        self.metadata = {
            "version": "1.0.0",
            "type": "base",
            "framework": "unknown"
        }
    
    @abstractmethod
    def load(self) -> None:
        """
        Load the model from file or initialize it
        
        This method should be implemented by each model subclass
        to load their specific model type (scikit-learn, PyTorch, TensorFlow, etc.)
        """
        pass
    
    @abstractmethod
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make predictions using the loaded model
        
        Args:
            input_data: Dictionary containing input features
            
        Returns:
            Dictionary containing prediction results
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get model metadata
        
        Returns:
            Dictionary with model information
        """
        return self.metadata
    
    def is_ready(self) -> bool:
        """
        Check if model is loaded and ready for predictions
        
        Returns:
            True if model is ready, False otherwise
        """
        return self.is_loaded and self.model is not None
