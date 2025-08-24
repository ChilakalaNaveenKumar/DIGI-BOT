"""
Digi Bot Services - Production Ready
Clean Google OAuth + AI Chat with Database History

Features:
- Google OAuth authentication
- Direct AI streaming (no orchestrator overhead)  
- Chat history with database persistence
- File upload support
- All AI providers (Anthropic, OpenAI, Grok)
- Cost-effective, minimal token usage
"""

import logging
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator, Optional

import structlog
import uvicorn
import httpx
import jwt
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, Response
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import init_db, close_db, get_db_session
from app.models.user import User
from app.routers.component_matcher import router as component_matcher_router
from app.services.auth.router.enhanced_auth_router import router as enhanced_auth_router

# Configure clean logging (no spam)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("anthropic").setLevel(logging.WARNING)

logger = structlog.get_logger(__name__)

# Initialize settings
settings = get_settings()


class GoogleAuthRequest(BaseModel):
    """Request model for Google authentication"""
    credential: str


class AuthResponse(BaseModel):
    """Response model for successful authentication"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Digi Bot Services")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # File service removed as requested
        
        logger.info("Digi Bot Services started successfully")
        
    except Exception as e:
        logger.error("Failed to start application", error=str(e))
        sys.exit(1)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Digi Bot Services")
    
    try:
        # File service cleanup removed
        
        # Close database connections
        await close_db()
        logger.info("Database connections closed")
        
        logger.info("Digi Bot Services shutdown complete")
        
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def verify_google_token(credential: str) -> dict:
    """Verify Google ID token and extract user info"""
    try:
        # Use a thread pool to run the sync Google verification in async context
        import asyncio
        import functools
        
        # Run the sync operation in a thread pool
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
    
    try:
        # Try to find existing user
        stmt = select(User).where(User.google_id == google_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            # Update last login
            user.last_login_at = datetime.now(timezone.utc)
            user.verified_email = google_user.get('email_verified', user.verified_email)
            logger.info(f"User login: {user.email}")
        else:
            # Create new user
            user = User(
                google_id=google_id,
                email=google_user.get('email'),
                name=google_user.get('name'),
                picture=google_user.get('picture'),
                verified_email=google_user.get('email_verified', False),
                last_login_at=datetime.now(timezone.utc)
            )
            db.add(user)
            logger.info(f"New user created: {user.email}")
        
        # Flush to get the ID, then commit
        await db.flush()
        await db.commit()
        
        # Refresh the user object to get the latest data and ensure it's loaded
        await db.refresh(user)
        
        return user
        
    except Exception as e:
        logger.error("Error in get_or_create_user", error=str(e), google_id=google_id)
        try:
            await db.rollback()
        except Exception as rollback_error:
            logger.error("Error during rollback", error=str(rollback_error))
        raise


# Create FastAPI app
app = FastAPI(
    title="Digi Bot Services",
    description="Production-ready Google OAuth + AI Chat with Database History",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Health check
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Digi Bot Services",
        "version": "1.0.0",
        "status": "healthy",
        "features": [
            "Google OAuth",
            "AI Chat Streaming", 
            "Chat History",
            "File Uploads",
            "Multi-AI Providers"
        ]
    }


# Google OAuth endpoints
@app.get("/auth/google/url")
async def get_google_auth_url():
    """Get Google OAuth authorization URL"""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500, 
            detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID."
        )
    
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid email profile"
        "&access_type=offline"
        "&prompt=consent"
    )
    
    return {"auth_url": google_auth_url}


@app.post("/auth/google/verify")
async def verify_google_credential(
    auth_request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Verify Google credential and return JWT token"""
    
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured"
        )
    
    # Verify Google token
    try:
        google_user = await verify_google_token(auth_request.credential)
        logger.info("Google authentication successful", user_id=google_user.get('sub'))
    except Exception as e:
        logger.error("Google authentication failed", error=str(e))
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    # Get or create user in database
    try:
        user = await get_or_create_user(google_user, db)
    except Exception as db_error:
        logger.error("Database error in OAuth verification", error=str(db_error))
        raise HTTPException(status_code=500, detail="Database error during authentication")
    
    # Create JWT token
    token_data = {
        "sub": str(user.id),
        "google_id": user.google_id,
        "email": user.email,
        "name": user.name
    }
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=token_data, 
        expires_delta=access_token_expires
    )
    
    # Serialize user data while session is active
    user_dict = user.to_dict()
    
    return AuthResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_dict
    )


@app.get("/auth/callback")
async def google_callback(
    response: Response,
    code: str = None, 
    error: str = None,
    db: AsyncSession = Depends(get_db_session)
):
    """Handle Google OAuth callback - exchange code for tokens"""
    if error:
        logger.error("Google OAuth error", error=error)
        return JSONResponse(
            status_code=400,
            content={"error": "Authentication failed", "details": error}
        )
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")
    
    try:
        # Exchange authorization code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                }
            )
            
            if token_response.status_code != 200:
                logger.error("Token exchange failed", response=token_response.text)
                raise HTTPException(status_code=400, detail="Failed to exchange code for tokens")
            
            tokens = token_response.json()
            id_token_str = tokens.get("id_token")
            
            if not id_token_str:
                raise HTTPException(status_code=400, detail="No ID token received")
            
            # Verify the ID token and extract user info
            google_user = await verify_google_token(id_token_str)
            
            # Get or create user in database
            try:
                user = await get_or_create_user(google_user, db)
            except Exception as db_error:
                logger.error("Database error in OAuth callback", error=str(db_error))
                raise HTTPException(status_code=500, detail="Database error during authentication")
            
            # Use enhanced security system to generate tokens and set cookies
            from app.services.auth import security_manager
            
            user_data = {
                "id": user.id,
                "google_id": user.google_id,
                "email": user.email,
                "name": user.name,
                "verified_email": user.verified_email
            }
            
            # Generate secure tokens
            access_token, refresh_token = security_manager.generate_tokens(user_data)
            
            # Debug: Log token generation
            logger.info("Google callback token generation", 
                       access_token_length=len(access_token) if access_token else 0,
                       refresh_token_length=len(refresh_token) if refresh_token else 0,
                       user_id=user.id)
            
            # Generate a one-time auth code for secure parent window exchange
            import secrets
            auth_code = secrets.token_urlsafe(32)
            
            # Store the tokens temporarily with the auth code (5 minutes expiry)
            from datetime import datetime, timedelta
            auth_code_data = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_data": user.to_dict(),
                "expires": datetime.now() + timedelta(minutes=5)
            }
            
            # Store in security manager (we'll add this method)
            security_manager.store_auth_code(auth_code, auth_code_data)
            
            # Log successful authentication
            security_manager.log_security_event(
                "google_oauth_callback_success",
                # We don't have request object here, so create a minimal one
                type('Request', (), {
                    'client': type('Client', (), {'host': 'unknown'})(),
                    'headers': {},
                    'url': type('URL', (), {'path': '/auth/callback'})()
                })(),
                user_id=str(user.id)
            )
            
            # Serialize user data for response
            import json
            user_info_json = json.dumps(user.to_dict())
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Authentication Successful</title>
            </head>
            <body>
                <script>
                    console.log('Auth callback page loaded, sending message to parent...');
                    
                    if (window.opener) {{
                        const message = {{
                            type: 'GOOGLE_AUTH_SUCCESS',
                            auth_code: '{auth_code}',
                            user: {user_info_json}
                        }};
                        
                        console.log('Sending auth success message to parent window');
                        window.opener.postMessage(message, 'http://localhost:3000');
                        
                        setTimeout(() => {{
                            window.close();
                        }}, 100);
                    }} else {{
                        document.body.innerHTML = '<h1>✅ Success! You can close this window.</h1>';
                        setTimeout(() => window.close(), 1000);
                    }}
                </script>
            </body>
            </html>
            """
            
            return HTMLResponse(content=html_content)
            
    except Exception as e:
        logger.error("OAuth callback error", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Authentication failed", "details": str(e)}
        )

# Include routers
app.include_router(enhanced_auth_router)  # Enhanced secure authentication
app.include_router(component_matcher_router)  # Component matcher with thinking blocks


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )