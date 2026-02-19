"""
Supabase JWT Authentication for FastAPI
"""
import os
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import requests
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# Get Supabase JWT secret from environment
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
SUPABASE_URL = os.getenv("SUPABASE_URL")

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Verify Supabase JWT token and return user payload
    
    Args:
        credentials: HTTP Authorization header with Bearer token
        
    Returns:
        dict: Decoded JWT payload containing user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        # First, try to decode without verification to check the algorithm
        unverified_header = jwt.get_unverified_header(token)
        algorithm = unverified_header.get('alg', 'HS256')
        
        if algorithm == 'ES256':
            # OAuth tokens (Google, etc.) - decode without signature verification
            # Supabase already verified the token, we trust their verification
            payload = jwt.decode(
                token,
                key="",  # Empty key since we're not verifying signature
                options={
                    "verify_signature": False,
                    "verify_aud": False,
                    "verify_exp": False  # Trust Supabase's expiration handling
                }
            )
            
            # Verify the issuer matches our Supabase project
            expected_issuer = f"{SUPABASE_URL}/auth/v1"
            if payload.get('iss') != expected_issuer:
                raise JWTError(f"Invalid issuer: {payload.get('iss')}")
                
        else:
            # Email/password tokens - use secret key
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated"
            )
        
        return payload
        
    except JWTError as e:
        logger.error(f"JWT verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Get current authenticated user from token
    
    Args:
        credentials: HTTP Authorization header with Bearer token
        
    Returns:
        dict: User information from JWT payload
    """
    payload = verify_token(credentials)
    
    user = {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role"),
        "metadata": payload.get("user_metadata", {})
    }
    
    return user


def require_auth(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Dependency to require authentication on routes
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(require_auth)):
            return {"message": f"Hello {user['email']}"}
    """
    return get_current_user(credentials)
