"""
ML Model Service for Power Prediction
Loads XGBoost model from Hugging Face and provides prediction functionality
"""
import os
import numpy as np
import joblib
from typing import Dict, Optional, Tuple
from huggingface_hub import hf_hub_download
import logging

logger = logging.getLogger(__name__)

class MLModelService:
    """Service for loading and using XGBoost model (993 KB, cached locally)"""
    
    def __init__(self, cache_dir: str = "./model_cache"):
        self.cache_dir = cache_dir
        self.repo_id = "hasnaynajmal/vessel-power-prediction"
        self.xgb_model = None
        self.feature_scaler = None
        self.target_scaler = None
        self.feature_names = None
        self.time_feature = None
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
    
    def _download_model(self, filename: str) -> str:
        """Download model from Hugging Face"""
        try:
            logger.info(f"Downloading {filename} from Hugging Face...")
            model_path = hf_hub_download(
                repo_id=self.repo_id,
                filename=filename,
                cache_dir=self.cache_dir
            )
            logger.info(f"✓ Downloaded {filename}")
            return model_path
        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")
            raise
    
    def load_scalers(self):
        """Load feature and target scalers"""
        if self.feature_scaler is not None:
            return
        
        try:
            # Download and load feature scaler
            feature_scaler_path = self._download_model("feature_scaler.joblib")
            scaler_dict = joblib.load(feature_scaler_path)
            
            self.feature_scaler = scaler_dict['scaler']
            self.feature_names = scaler_dict['feature_names']
            self.time_feature = scaler_dict.get('time_feature')
            
            # Download and load target scaler
            target_scaler_path = self._download_model("target_scaler.joblib")
            target_dict = joblib.load(target_scaler_path)
            
            self.target_scaler = target_dict
            
            logger.info("✓ Scalers loaded successfully")
            logger.info(f"  Features: {len(self.feature_names)}")
            logger.info(f"  Time feature: {self.time_feature}")
            
        except Exception as e:
            logger.error(f"Failed to load scalers: {e}")
            raise
    
    def load_model(self):
        """Load XGBoost model (recommended, only 993 KB)"""
        # Load scalers first
        self.load_scalers()
        
        # Check if already loaded
        if self.xgb_model is not None:
            return self.xgb_model
        
        try:
            model_path = self._download_model("xgb_model.joblib")
            self.xgb_model = joblib.load(model_path)
            logger.info("✓ XGBoost model loaded (993 KB)")
            return self.xgb_model
            
        except Exception as e:
            logger.error(f"Failed to load XGBoost model: {e}")
            raise
    
    def _prepare_features(self, features: Dict[str, float]) -> np.ndarray:
        """Prepare and scale features for model input"""
        # Add derived features
        features_complete = features.copy()
        
        # Derived features
        features_complete['stw_cubed'] = features['stw'] ** 3
        features_complete['stw_squared'] = features['stw'] ** 2
        features_complete['mean_draft'] = (
            features['draft_aft_telegram'] + features['draft_fore_telegram']
        ) / 2
        features_complete['trim'] = (
            features['draft_aft_telegram'] - features['draft_fore_telegram']
        )
        features_complete['wind_magnitude'] = np.sqrt(
            features['awind_vcomp_provider']**2 + 
            features['awind_ucomp_provider']**2
        )
        features_complete['wind_angle'] = np.arctan2(
            features['awind_ucomp_provider'],
            features['awind_vcomp_provider']
        )
        features_complete['current_magnitude'] = np.sqrt(
            features['rcurrent_vcomp']**2 + 
            features['rcurrent_ucomp']**2
        )
        features_complete['current_angle'] = np.arctan2(
            features['rcurrent_ucomp'],
            features['rcurrent_vcomp']
        )
        features_complete['speed_wind_interaction'] = (
            features['stw'] * features_complete['wind_magnitude']
        )
        
        # Order features correctly
        feature_array = np.array([
            [features_complete[name] for name in self.feature_names]
        ])
        
        # Scale features (excluding time feature)
        features_to_scale = [f for f in self.feature_names if f != self.time_feature]
        time_idx = self.feature_names.index(self.time_feature)
        
        # Get features for scaling
        feature_values_for_scaling = []
        for name in features_to_scale:
            idx = self.feature_names.index(name)
            feature_values_for_scaling.append(feature_array[0, idx])
        
        # Scale
        scaled_features = self.feature_scaler.transform(
            np.array([feature_values_for_scaling])
        )
        
        # Reinsert time feature at correct position
        X = np.concatenate([
            scaled_features[:, :time_idx],
            feature_array[:, time_idx:time_idx+1],
            scaled_features[:, time_idx:]
        ], axis=1)
        
        return X
    
    def predict(
        self, 
        features: Dict[str, float]
    ) -> Tuple[float, Dict]:
        """
        Make power prediction using XGBoost
        
        Args:
            features: Dictionary with vessel and environmental features
            
        Returns:
            Tuple of (prediction_kw, metadata)
        """
        # Load model if not already loaded
        model = self.load_model()
        
        # Prepare features
        X = self._prepare_features(features)
        
        # Make prediction (scaled)
        prediction_scaled = model.predict(X)[0]
        
        # Unscale prediction
        prediction_kw = (
            prediction_scaled * self.target_scaler['std'] + 
            self.target_scaler['mean']
        )
        
        # Metadata
        metadata = {
            "model_used": "xgboost",
            "n_features": len(self.feature_names),
            "unit": "kW",
            "model_performance": {
                "mae_dev_in_kw": 866,
                "r2_dev_in": 0.978,
                "mae_dev_out_kw": 1435,
                "r2_dev_out": 0.896
            }
        }
        
        return float(prediction_kw), metadata

# Global instance
_ml_service: Optional[MLModelService] = None

def get_ml_service() -> MLModelService:
    """Get or create ML service instance"""
    global _ml_service
    if _ml_service is None:
        _ml_service = MLModelService()
    return _ml_service
