"""
Health Check Endpoints
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "PropelSense API",
    }


@router.get("/detailed")
async def detailed_health():
    """
    Detailed health check
    
    Returns:
        dict: Detailed health information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "PropelSense API",
        "version": "1.0.0",
        "dependencies": {
            "database": "not_configured",
            "cache": "not_configured",
        }
    }
