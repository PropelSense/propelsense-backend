"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends
from app.core.auth import require_auth

router = APIRouter()


@router.get("/me")
async def get_current_user_info(user: dict = Depends(require_auth)):
    """
    Get current authenticated user information
    
    Returns the user data from the JWT token
    """
    return {
        "user": user,
        "message": "Successfully authenticated"
    }


@router.get("/verify")
async def verify_authentication(user: dict = Depends(require_auth)):
    """
    Verify if the user is authenticated
    
    Simple endpoint to check if token is valid
    """
    return {
        "authenticated": True,
        "user_id": user["id"],
        "email": user["email"]
    }
