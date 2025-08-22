"""
Simple authentication dependencies for Digi Bot Services
"""

from typing import Optional
from fastapi import HTTPException, Header
import jwt
from app.core.simple_config import get_settings

settings = get_settings()


async def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """Get current user from JWT token (optional)."""
    if not authorization:
        return None
    
    try:
        # Extract token from "Bearer <token>"
        token = authorization.split(" ")[1] if authorization.startswith("Bearer ") else authorization
        
        # Decode JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        return {
            "id": payload.get("sub"),
            "google_id": payload.get("google_id"),
            "email": payload.get("email"),
            "name": payload.get("name")
        }
    except (jwt.ExpiredSignatureError, jwt.JWTError, IndexError):
        return None


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Get current user from JWT token (required)."""
    user = await get_current_user_optional(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

