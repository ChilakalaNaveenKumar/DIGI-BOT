"""
Development Authentication

Creates a test user automatically for development without requiring login.
"""

from typing import Optional
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db_session
from app.models.user import User
from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# Test user configuration
TEST_USER_CONFIG = {
    "email": "test@digibot.dev",
    "username": "testuser",
    "full_name": "Test User",
    "is_active": True,
    "is_superuser": False,
}


async def get_or_create_test_user(db: AsyncSession) -> User:
    """
    Get or create the test user for development.
    
    Args:
        db: Database session
        
    Returns:
        User: Test user object
    """
    try:
        # Check if test user already exists
        result = await db.execute(
            select(User).where(User.email == TEST_USER_CONFIG["email"])
        )
        user = result.scalar_one_or_none()
        
        if user:
            logger.debug("Test user found", user_id=user.id)
            return user
        
        # Create test user (let database auto-generate ID)
        user = User(
            email=TEST_USER_CONFIG["email"],
            username=TEST_USER_CONFIG["username"],
            full_name=TEST_USER_CONFIG["full_name"],
            hashed_password="test-password-hash",  # Not used in dev mode
            is_active=TEST_USER_CONFIG["is_active"],
            is_superuser=TEST_USER_CONFIG["is_superuser"]
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info("Test user created for development", user_id=user.id, email=user.email)
        return user
        
    except Exception as e:
        logger.error("Failed to create test user", error=str(e))
        await db.rollback()
        raise


async def get_current_user_dev(
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Development version of get_current_user that automatically uses test user.
    
    Args:
        db: Database session
        
    Returns:
        User: Test user for development
    """
    return await get_or_create_test_user(db)


# Export the appropriate function based on environment
if settings.ENVIRONMENT == "development":
    get_current_user = get_current_user_dev
    logger.info("Using development authentication (test user)")
else:
    from app.core.auth import get_current_user
    logger.info("Using production authentication")
