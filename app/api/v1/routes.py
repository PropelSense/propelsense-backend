"""
API Routes Registry
Centralized list of all API endpoints
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, propulsion

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(propulsion.router, prefix="/propulsion", tags=["Propulsion"])