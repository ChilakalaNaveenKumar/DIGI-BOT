"""
Enhanced Authentication Router with Secure Cookies and Refresh Tokens
HIPAA-compliant authentication system with comprehensive security features
"""

import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Request, Response, Cookie, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db_session
from app.core.security import security_manager
from app.core.enhanced_auth_deps import get_current_user_from_cookie
from app.models.user import User
from app.core.config import get_settings

# We'll define these functions locally to avoid circular imports
import asyncio
import functools
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy import select

logger = structlog.get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/auth", tags=["Enhanced Authentication"])


async def verify_google_token(credential: str) -> dict:
    """Verify Google ID token and extract user info"""
    try:
        # Use a thread pool to run the sync Google verification in async context
        loop = asyncio.get_event_loop()
        idinfo = await loop.run_in_executor(
            None,
            functools.partial(
                id_token.verify_oauth2_token,
                credential,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
        )
        
        # Verify the issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        return idinfo
    except ValueError as e:
        logger.error("Google token verification failed", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid Google token")


async def get_or_create_user(google_user: dict, db: AsyncSession) -> User:
    """Get or create user from Google OAuth data"""
    google_id = google_user.get('sub')
    email = google_user.get('email')
    name = google_user.get('name')
    picture = google_user.get('picture')
    verified_email = google_user.get('email_verified', False)
    
    if not google_id or not email:
        raise HTTPException(status_code=400, detail="Invalid Google user data")
    
    try:
        # Try to find existing user
        result = await db.execute(select(User).where(User.google_id == google_id))
        user = result.scalar_one_or_none()
        
        if user:
            # Update existing user info
            user.email = email
            user.name = name
            user.picture = picture
            user.verified_email = verified_email
            user.last_login_at = datetime.now(timezone.utc)
            
            await db.flush()
            await db.commit()
            return user
        else:
            # Create new user
            user = User(
                google_id=google_id,
                email=email,
                name=name,
                picture=picture,
                verified_email=verified_email,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                last_login_at=datetime.now(timezone.utc)
            )
            
            db.add(user)
            await db.flush()
            await db.commit()
            await db.refresh(user)
            
            logger.info("New user created", user_id=user.id, email=email)
            return user
            
    except Exception as e:
        logger.error("Database error in user creation", error=str(e))
        raise HTTPException(status_code=500, detail="Database error during user creation")


class GoogleAuthRequest(BaseModel):
    """Request model for Google authentication"""
    credential: str


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh"""
    pass  # Token comes from httpOnly cookie


class AuthResponse(BaseModel):
    """Enhanced response model for authentication"""
    success: bool
    message: str
    user: Optional[Dict[str, Any]] = None
    csrf_token: Optional[str] = None
    expires_in: Optional[int] = None


@router.post("/google/verify", response_model=AuthResponse)
async def verify_google_credential_secure(
    auth_request: GoogleAuthRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session)
):
    """Verify Google credential and set secure cookies."""
    
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured"
        )
    
    try:
        # Verify Google token
        google_user = await verify_google_token(auth_request.credential)
        
        # Log authentication attempt
        security_manager.log_security_event(
            "google_auth_attempt",
            request,
            details={"google_id": google_user.get('sub')}
        )
        
        # Get or create user in database
        user = await get_or_create_user(google_user, db)
        
        # Generate secure tokens
        access_token, refresh_token = security_manager.generate_tokens({
            "id": user.id,
            "google_id": user.google_id,
            "email": user.email,
            "name": user.name,
            "verified_email": user.verified_email
        })
        
        # Set secure cookies
        security_manager.set_secure_cookies(
            response,
            access_token,
            refresh_token,
            user.to_dict()
        )
        
        # Log successful authentication
        security_manager.log_security_event(
            "user_login_success",
            request,
            user_id=str(user.id),
            details={"method": "google_oauth"}
        )
        
        return AuthResponse(
            success=True,
            message="Authentication successful",
            user={
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "picture": user.picture,
                "verified_email": user.verified_email
            },
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        # Log authentication failure
        security_manager.log_security_event(
            "authentication_failed",
            request,
            details={"method": "google_oauth", "error": str(e)}
        )
        
        logger.error("Google authentication failed", error=str(e))
        raise HTTPException(status_code=401, detail="Authentication failed")


@router.post("/refresh", response_model=AuthResponse)
async def refresh_access_token(
    request: Request,
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db_session)
):
    """Refresh access token using refresh token from httpOnly cookie."""
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token required")
    
    try:
        # Verify refresh token
        payload = security_manager.verify_refresh_token(refresh_token)
        user_id = int(payload.get("sub"))
        
        # Get user from database
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        
        # Generate new tokens
        new_access_token, new_refresh_token = security_manager.generate_tokens({
            "id": user.id,
            "google_id": user.google_id,
            "email": user.email,
            "name": user.name,
            "verified_email": user.verified_email
        })
        
        # Revoke old refresh token
        old_jti = payload.get("jti")
        if old_jti:
            security_manager.revoke_refresh_token(old_jti)
        
        # Set new secure cookies
        security_manager.set_secure_cookies(
            response,
            new_access_token,
            new_refresh_token,
            user.to_dict()
        )
        
        # Log token refresh
        security_manager.log_security_event(
            "token_refreshed",
            request,
            user_id=str(user.id)
        )
        
        return AuthResponse(
            success=True,
            message="Token refreshed successfully",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(status_code=401, detail="Token refresh failed")


@router.post("/logout")
async def logout_secure(
    request: Request,
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_from_cookie)
):
    """Secure logout with token revocation and cookie cleanup."""
    
    try:
        user_id = None
        
        # Revoke refresh token if present
        if refresh_token:
            try:
                payload = security_manager.verify_refresh_token(refresh_token)
                jti = payload.get("jti")
                if jti:
                    security_manager.revoke_refresh_token(jti)
            except:
                pass  # Token already invalid
        
        # Revoke all user tokens if user is authenticated
        if current_user:
            user_id = str(current_user["id"])
            revoked_count = security_manager.revoke_all_user_tokens(user_id)
            logger.info(f"Revoked {revoked_count} refresh tokens for user {user_id}")
        
        # Clear all authentication cookies
        security_manager.clear_auth_cookies(response)
        
        # Log logout
        security_manager.log_security_event(
            "user_logout",
            request,
            user_id=user_id
        )
        
        return AuthResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except Exception as e:
        logger.error("Logout error", error=str(e))
        return AuthResponse(
            success=True,
            message="Logged out successfully"  # Always return success for security
        )


@router.get("/me")
async def get_current_user_info(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user_from_cookie)
):
    """Get current user information from secure session."""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "user": {
            "id": str(current_user["id"]),
            "email": current_user["email"],
            "name": current_user["name"],
            "verified_email": current_user["verified_email"],
            "is_active": current_user["is_active"]
        },
        "authenticated": True
    }


@router.get("/status")
async def get_auth_status(
    request: Request,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_from_cookie)
):
    """Get authentication status without requiring login."""
    
    # Debug: Log cookies received
    cookies = request.cookies
    access_token_value = cookies.get("access_token", "")
    logger.info("Auth status check", cookies=list(cookies.keys()), has_access_token=bool(access_token_value), access_token_length=len(access_token_value) if access_token_value else 0)
    
    return {
        "authenticated": current_user is not None,
        "user": {
            "id": str(current_user["id"]),
            "email": current_user["email"],
            "name": current_user["name"]
        } if current_user else None
    }


class AuthCodeRequest(BaseModel):
    auth_code: str

@router.post("/exchange-auth-code")
async def exchange_auth_code(
    request: Request,
    response: Response,
    auth_request: AuthCodeRequest
):
    """Exchange one-time auth code for secure cookies."""
    
    try:
        # Consume the auth code
        auth_data = security_manager.consume_auth_code(auth_request.auth_code)
        
        if not auth_data:
            raise HTTPException(status_code=401, detail="Invalid or expired auth code")
        
        # Set secure cookies in parent window
        security_manager.set_secure_cookies(
            response,
            auth_data["access_token"],
            auth_data["refresh_token"],
            auth_data["user_data"]
        )
        
        logger.info("Auth code exchanged for cookies", user_id=auth_data["user_data"]["id"])
        
        return {
            "message": "Authentication successful",
            "user": auth_data["user_data"],
            "authenticated": True
        }
        
    except Exception as e:
        logger.error("Error exchanging auth code", error=str(e))
        raise HTTPException(status_code=500, detail="Authentication exchange failed")


@router.post("/verify-token")
async def verify_token_and_set_cookies(
    request: Request,
    response: Response,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db_session)
):
    """Verify JWT token and set secure cookies for parent window authentication."""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    
    token = authorization.split(" ")[1]
    
    try:
        # Verify the token using the security manager
        payload = security_manager.verify_access_token(token)
        user_id = int(payload.get("sub"))
        
        # Get user from database
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user or not user.is_active:
                raise HTTPException(status_code=401, detail="User not found or inactive")
        except Exception as db_error:
            logger.error("Database error in verify-token", error=str(db_error))
            raise HTTPException(status_code=500, detail="Database error during token verification")
        
        # Generate new secure tokens for the parent window
        user_data = {
            "id": user.id,
            "google_id": user.google_id,
            "email": user.email,
            "name": user.name,
            "verified_email": user.verified_email
        }
        
        new_access_token, new_refresh_token = security_manager.generate_tokens(user_data)
        
        # Set secure cookies in parent window context
        security_manager.set_secure_cookies(
            response,
            new_access_token,
            new_refresh_token,
            user.to_dict()
        )
        
        # Log successful token verification
        security_manager.log_security_event(
            "token_verified_parent_window",
            request,
            user_id=str(user.id)
        )
        
        return AuthResponse(
            success=True,
            message="Token verified and cookies set",
            user={
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "picture": user.picture,
                "verified_email": user.verified_email
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token verification failed", error=str(e))
        raise HTTPException(status_code=401, detail="Token verification failed")


@router.post("/revoke-all-sessions")
async def revoke_all_sessions(
    request: Request,
    response: Response,
    current_user: Dict[str, Any] = Depends(get_current_user_from_cookie)
):
    """Revoke all user sessions (security feature)."""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_id = str(current_user["id"])
    
    # Revoke all refresh tokens for this user
    revoked_count = security_manager.revoke_all_user_tokens(user_id)
    
    # Clear current session cookies
    security_manager.clear_auth_cookies(response)
    
    # Log security action
    security_manager.log_security_event(
        "all_sessions_revoked",
        request,
        user_id=user_id,
        details={"revoked_tokens": revoked_count}
    )
    
    return {
        "success": True,
        "message": f"Revoked {revoked_count} sessions",
        "revoked_sessions": revoked_count
    }
