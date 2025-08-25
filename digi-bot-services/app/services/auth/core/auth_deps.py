"""
Enhanced Authentication Dependencies with Security Features
Implements secure cookie-based authentication with CSRF protection
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, Request, Depends, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db_session
from .security import security_manager
from app.models.user import User

logger = structlog.get_logger(__name__)


async def get_current_user_from_cookie(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    csrf_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db_session)
) -> Optional[Dict[str, Any]]:
    """Get current user from secure httpOnly cookies (optional)."""
    
    if not access_token:
        return None
    
    try:
        # Verify access token
        payload = security_manager.verify_access_token(access_token)
        
        # Get user from database
        user_id = int(payload.get("sub"))
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            return None
        
        # Log successful authentication
        security_manager.log_security_event(
            "user_authenticated",
            request,
            user_id=str(user.id)
        )
        
        # Return user data without google_id for security
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "verified_email": user.verified_email,
            "is_active": user.is_active
        }
        
    except HTTPException as e:
        if "expired" in str(e.detail).lower():
            # Log token expiration
            security_manager.log_security_event(
                "access_token_expired",
                request,
                details={"reason": str(e.detail)}
            )
        return None
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        return None


async def get_current_user_required(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    csrf_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get current user from secure cookies (required)."""
    
    user = await get_current_user_from_cookie(request, access_token, csrf_token, db)
    
    if not user:
        # Log authentication failure
        security_manager.log_security_event(
            "authentication_failed",
            request,
            details={"reason": "no_valid_token"}
        )
        raise HTTPException(
            status_code=401, 
            detail="Authentication required. Please log in again."
        )
    
    return user


async def verify_csrf_token(
    request: Request,
    csrf_token: Optional[str] = Cookie(None)
) -> bool:
    """Verify CSRF token for state-changing operations."""
    
    # Skip CSRF for GET requests
    if request.method == "GET":
        return True
    
    if not csrf_token:
        security_manager.log_security_event(
            "csrf_token_missing",
            request,
            details={"method": request.method, "path": str(request.url.path)}
        )
        raise HTTPException(status_code=403, detail="CSRF token required")
    
    if not security_manager.validate_csrf_token(csrf_token):
        security_manager.log_security_event(
            "csrf_token_invalid",
            request,
            details={"method": request.method, "path": str(request.url.path)}
        )
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
    
    return True


async def get_authenticated_user_with_csrf(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    csrf_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get authenticated user and verify CSRF for protected operations."""
    
    # Verify CSRF token for state-changing operations
    await verify_csrf_token(request, csrf_token)
    
    # Get authenticated user
    user = await get_current_user_required(request, access_token, csrf_token, db)
    
    return user


# Convenience aliases
CurrentUser = Depends(get_current_user_required)
CurrentUserOptional = Depends(get_current_user_from_cookie)
AuthenticatedUserWithCSRF = Depends(get_authenticated_user_with_csrf)

