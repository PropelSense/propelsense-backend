"""
API Routes Registry
Centralized list of all API endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, propulsion, auth, sea_trial, ml_prediction, reports

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(propulsion.router, prefix="/propulsion", tags=["Propulsion"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(sea_trial.router, prefix="/sea-trials", tags=["Sea Trials"])
api_router.include_router(ml_prediction.router, prefix="/ml", tags=["ML Predictions"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])