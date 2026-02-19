"""
Mock baseline_models module to load the trained models
"""
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb


class XGBModel:
    """Wrapper for XGBoost model"""
    def __init__(self, model=None, **kwargs):
        if model is None:
            object.__setattr__(self, 'model', xgb.XGBRegressor(**kwargs))
        else:
            object.__setattr__(self, 'model', model)
    
    def fit(self, X, y):
        return self.model.fit(X, y)
    
    def predict(self, X):
        return self.model.predict(X)
    
    def __getattr__(self, name):
        # Delegate to the wrapped model
        try:
            return getattr(object.__getattribute__(self, 'model'), name)
        except AttributeError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
