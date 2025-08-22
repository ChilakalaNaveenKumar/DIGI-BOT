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
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import AsyncGenerator, List, Optional

import structlog
import uvicorn
import httpx
import jwt
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.simple_config import get_settings
from app.core.database import init_db, close_db, get_db_session
from app.models.user import User
from app.models.conversation import Conversation
from app.routers import direct_chat, files

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
        
        # Initialize file storage
        from app.services.file_service import FileService
        file_service = FileService()
        await file_service.initialize()
        app.state.file_service = file_service
        logger.info("File Service initialized successfully")
        
        logger.info("Digi Bot Services started successfully")
        
    except Exception as e:
        logger.error("Failed to start application", error=str(e))
        sys.exit(1)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Digi Bot Services")
    
    try:
        # Cleanup file service
        if hasattr(app.state, 'file_service'):
            await app.state.file_service.cleanup()
            logger.info("File Service cleaned up")
        
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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_google_token(credential: str) -> dict:
    """Verify Google ID token and extract user info"""
    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            credential, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID
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
    
    # Try to find existing user
    stmt = select(User).where(User.google_id == google_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        # Update last login
        user.last_login_at = datetime.utcnow()
        user.email = google_user.get('email', user.email)
        user.name = google_user.get('name', user.name)
        user.picture = google_user.get('picture', user.picture)
        user.verified_email = google_user.get('email_verified', user.verified_email)
        await db.commit()
        logger.info(f"User login: {user.email}")
    else:
        # Create new user
        user = User(
            google_id=google_id,
            email=google_user.get('email'),
            name=google_user.get('name'),
            picture=google_user.get('picture'),
            verified_email=google_user.get('email_verified', False),
            last_login_at=datetime.utcnow()
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"New user created: {user.email}")
    
    return user


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
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://testing.digi-setu.com",
        "https://digi-setu.com"
    ],
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
        google_user = verify_google_token(auth_request.credential)
        logger.info("Google authentication successful", user_id=google_user.get('sub'))
    except Exception as e:
        logger.error("Google authentication failed", error=str(e))
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    # Get or create user in database
    user = await get_or_create_user(google_user, db)
    
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
    
    return AuthResponse(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user.to_dict()
    )


@app.get("/auth/callback")
async def google_callback(
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
            google_user = verify_google_token(id_token_str)
            
            # Get or create user in database
            user = await get_or_create_user(google_user, db)
            
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
            
            # Return success page that closes popup
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
                            access_token: '{access_token}',
                            user: {user_info_json}
                        }};
                        
                        console.log('Sending message to parent:', message);
                        window.opener.postMessage(message, '*');
                        
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


@app.get("/auth/me")
async def get_current_user(authorization: str = None):
    """Get current user information from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
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
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/auth/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Logged out successfully"}


# Include routers
app.include_router(direct_chat.router)
app.include_router(files.router, prefix="/api")


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )