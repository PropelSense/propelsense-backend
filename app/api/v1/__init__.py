"""
API v1 Router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, propulsion

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(propulsion.router, prefix="/propulsion", tags=["propulsion"])
