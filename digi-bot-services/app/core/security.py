"""
Enhanced Security Configuration for HIPAA Compliance
Implements secure token management, CSRF protection, and session security
"""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
import jwt
from jwt import PyJWTError
import structlog

from app.core.simple_config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

class SecurityManager:
    """Manages all security-related operations including tokens, sessions, and CSRF protection."""
    
    def __init__(self):
        self.csrf_tokens: Dict[str, datetime] = {}
        self.refresh_tokens: Dict[str, Dict[str, Any]] = {}
        self.auth_codes: Dict[str, Dict[str, Any]] = {}  # One-time auth codes
        
    def generate_csrf_token(self) -> str:
        """Generate a secure CSRF token."""
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[token] = datetime.now(timezone.utc) + timedelta(hours=1)
        return token
    
    def validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token and clean up expired ones."""
        now = datetime.now(timezone.utc)
        
        # Clean up expired tokens
        expired_tokens = [t for t, exp in self.csrf_tokens.items() if exp < now]
        for expired in expired_tokens:
            del self.csrf_tokens[expired]
        
        # Validate token
        if token in self.csrf_tokens and self.csrf_tokens[token] > now:
            del self.csrf_tokens[token]  # Single use
            return True
        
        return False
    
    def generate_tokens(self, user_data: Dict[str, Any]) -> Tuple[str, str]:
        """Generate access and refresh tokens."""
        
        # Access token (short-lived, 15 minutes)
        access_payload = {
            "sub": str(user_data["id"]),
            "google_id": user_data.get("google_id"),
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "type": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
            "iat": datetime.now(timezone.utc),
            "jti": secrets.token_urlsafe(16)  # JWT ID for tracking
        }
        
        access_token = jwt.encode(
            access_payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        # Refresh token (long-lived, 7 days)
        refresh_payload = {
            "sub": str(user_data["id"]),
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
            "iat": datetime.now(timezone.utc),
            "jti": secrets.token_urlsafe(16)
        }
        
        refresh_token = jwt.encode(
            refresh_payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        # Store refresh token metadata
        self.refresh_tokens[refresh_payload["jti"]] = {
            "user_id": user_data["id"],
            "expires": refresh_payload["exp"],
            "created": refresh_payload["iat"]
        }
        
        # Debug: Log token generation
        logger.info("Token generation complete", 
                   access_token_length=len(access_token),
                   refresh_token_length=len(refresh_token),
                   user_id=user_data["id"])
        
        return access_token, refresh_token
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify access token and return payload."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Access token expired")
        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid access token")
    
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """Verify refresh token and return payload."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            jti = payload.get("jti")
            if not jti or jti not in self.refresh_tokens:
                raise HTTPException(status_code=401, detail="Refresh token revoked")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            # Clean up expired refresh token
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                    options={"verify_exp": False}
                )
                jti = payload.get("jti")
                if jti and jti in self.refresh_tokens:
                    del self.refresh_tokens[jti]
            except:
                pass
            
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    def revoke_refresh_token(self, jti: str) -> bool:
        """Revoke a specific refresh token."""
        if jti in self.refresh_tokens:
            del self.refresh_tokens[jti]
            return True
        return False
    
    def revoke_all_user_tokens(self, user_id: str) -> int:
        """Revoke all refresh tokens for a specific user."""
        revoked_count = 0
        tokens_to_remove = []
        
        for jti, token_data in self.refresh_tokens.items():
            if token_data["user_id"] == user_id:
                tokens_to_remove.append(jti)
        
        for jti in tokens_to_remove:
            del self.refresh_tokens[jti]
            revoked_count += 1
        
        return revoked_count
    
    def store_auth_code(self, auth_code: str, auth_data: Dict[str, Any]) -> None:
        """Store a one-time auth code with associated token data."""
        self.auth_codes[auth_code] = auth_data
        logger.info("Auth code stored", code_length=len(auth_code))
    
    def consume_auth_code(self, auth_code: str) -> Optional[Dict[str, Any]]:
        """Consume (retrieve and delete) a one-time auth code."""
        from datetime import datetime
        
        auth_data = self.auth_codes.get(auth_code)
        if not auth_data:
            return None
        
        # Check if expired
        if auth_data["expires"] < datetime.now():
            del self.auth_codes[auth_code]
            return None
        
        # Remove the code (one-time use)
        del self.auth_codes[auth_code]
        
        logger.info("Auth code consumed", code_length=len(auth_code))
        return auth_data
    
    def set_secure_cookies(
        self, 
        response: Response, 
        access_token: str, 
        refresh_token: str,
        user_data: Dict[str, Any]
    ) -> None:
        """Set secure httpOnly cookies for tokens and user data."""
        
        # Access token cookie (httpOnly, secure, short-lived)
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=15 * 60,  # 15 minutes
            httponly=True,
            secure=settings.COOKIE_SECURE,  # True in production
            samesite="lax",
            domain=None,  # Don't set domain for localhost
            path="/"
        )
        
        # Refresh token cookie (httpOnly, secure, long-lived)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
            domain=None,  # Don't set domain for localhost
            path="/"  # Make accessible to all endpoints
        )
        
        # User data cookie (secure but not httpOnly for frontend access)
        import json
        user_cookie_data = {
            "id": user_data.get("id"),
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "picture": user_data.get("picture"),
            "verified_email": user_data.get("verified_email", False)
        }
        
        response.set_cookie(
            key="user_data",
            value=json.dumps(user_cookie_data),
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=False,  # Frontend needs access
            secure=settings.COOKIE_SECURE,
            samesite="lax",
            domain=None,  # Don't set domain for localhost
            path="/"
        )
        
        # CSRF token cookie (not httpOnly, frontend needs access)
        csrf_token = self.generate_csrf_token()
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            max_age=60 * 60,  # 1 hour
            httponly=False,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
            domain=None,  # Don't set domain for localhost
            path="/"
        )
    
    def clear_auth_cookies(self, response: Response) -> None:
        """Clear all authentication cookies."""
        cookies_to_clear = ["access_token", "refresh_token", "user_data", "csrf_token"]
        
        for cookie_name in cookies_to_clear:
            response.delete_cookie(
                key=cookie_name,
                domain=settings.COOKIE_DOMAIN,
                path="/" if cookie_name != "refresh_token" else "/auth"
            )
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address for security logging."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def log_security_event(
        self, 
        event_type: str, 
        request: Request, 
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log security events for audit trail."""
        
        log_data = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "client_ip": self.get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", "unknown"),
            "user_id": user_id,
            "details": details or {}
        }
        
        logger.info("Security event", **log_data)

# Global security manager instance
security_manager = SecurityManager()
