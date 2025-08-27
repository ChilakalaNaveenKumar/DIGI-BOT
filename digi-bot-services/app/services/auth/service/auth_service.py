"""
Authentication Service

Handles user authentication, JWT tokens, and authorization.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import structlog
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.models.user import User

logger = structlog.get_logger(__name__)
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for handling authentication and authorization."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.warning("Authentication failed - user not found", email=email)
                return None
            
            if not user.is_active:
                logger.warning("Authentication failed - user inactive", email=email)
                return None
            
            if not self.verify_password(password, user.password_hash):
                logger.warning("Authentication failed - invalid password", email=email)
                return None
            
            logger.info("User authenticated successfully", user_id=user.id, email=email)
            return user
            
        except Exception as e:
            logger.error("Authentication error", email=email, error=str(e))
            return None
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise AuthenticationError("Token expired")
            
            return payload
            
        except JWTError as e:
            logger.warning("Token verification failed", error=str(e))
            raise AuthenticationError("Invalid token")
    
    async def get_current_user(self, token: str) -> User:
        """Get the current user from a JWT token."""
        
        try:
            payload = self.verify_token(token)
            user_id = payload.get("sub")
            
            if user_id is None:
                raise AuthenticationError("Invalid token payload")
            
            result = await self.db.execute(
                select(User).where(User.id == int(user_id))
            )
            user = result.scalar_one_or_none()
            
            if user is None:
                raise AuthenticationError("User not found")
            
            if not user.is_active:
                raise AuthenticationError("User account is inactive")
            
            return user
            
        except Exception as e:
            logger.error("Get current user failed", error=str(e))
            raise AuthenticationError("Authentication failed")
    
    async def create_user(
        self, 
        email: str, 
        password: str, 
        full_name: str,
        **kwargs
    ) -> User:
        """Create a new user account."""
        
        try:
            # Check if user already exists
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise AuthorizationError("User with this email already exists")
            
            # Create new user
            password_hash = self.get_password_hash(password)
            
            user = User(
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                **kwargs
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info("User created successfully", user_id=user.id, email=email)
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error("User creation failed", email=email, error=str(e))
            raise
    
    async def update_user_password(
        self, 
        user_id: int, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Update a user's password."""
        
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise AuthenticationError("User not found")
            
            if not self.verify_password(current_password, user.password_hash):
                raise AuthenticationError("Current password is incorrect")
            
            user.password_hash = self.get_password_hash(new_password)
            await self.db.commit()
            
            logger.info("Password updated successfully", user_id=user_id)
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Password update failed", user_id=user_id, error=str(e))
            raise
    
    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            user.is_active = False
            await self.db.commit()
            
            logger.info("User deactivated", user_id=user_id)
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("User deactivation failed", user_id=user_id, error=str(e))
            return False
    
    def check_permission(self, user: User, resource: str, action: str) -> bool:
        """Check if user has permission for a specific action on a resource."""
        
        # Simple role-based permission check
        # In a real application, this would be more sophisticated
        
        if user.role == "admin":
            return True
        
        if user.role == "user":
            # Users can perform most actions on their own resources
            if action in ["read", "create", "update"]:
                return True
            
            # Users cannot delete certain resources
            if action == "delete" and resource in ["user", "project"]:
                return False
        
        return False
    
    def require_permission(self, user: User, resource: str, action: str) -> None:
        """Require a specific permission, raise exception if not granted."""
        
        if not self.check_permission(user, resource, action):
            raise AuthorizationError(
                f"Permission denied: {action} on {resource}"
            )


# Dependency function for FastAPI
async def get_current_user(token: str = None) -> User:
    """FastAPI dependency to get current user from token."""
    # For development, get the actual mock user from database
    from app.core.database import async_session_factory
    from app.models.user import User
    
    try:
        async with async_session_factory() as db:
            # Get the first user (should be our mock user)
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()
            
            if user:
                return user
            else:
                # Fallback: create a simple mock user object if no user exists
                class MockUser:
                    def __init__(self):
                        self.id = 1
                        self.email = "dev@digisetu.ai"
                        self.full_name = "Development User"
                        self.is_active = True

                        self.theme_preference = "light"
                        self.language_preference = "en"
                
                return MockUser()
                
    except Exception as e:
        logger.error("Failed to get mock user from database", error=str(e))
        # Fallback: create a simple mock user object
        class MockUser:
            def __init__(self):
                self.id = 1
                self.email = "dev@digisetu.ai"
                self.full_name = "Development User"
                self.is_active = True

                self.theme_preference = "light"
                self.language_preference = "en"
        
        return MockUser()
