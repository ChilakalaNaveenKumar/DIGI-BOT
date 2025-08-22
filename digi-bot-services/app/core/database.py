"""
Database configuration and session management for Digi Setu AI Backend

Uses SQLAlchemy 2.0 with async support and proper connection pooling.
"""

import asyncio
from typing import AsyncGenerator, Optional

import structlog
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import text

from app.core.simple_config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# Global variables for database components
async_engine = None
async_session_factory = None


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    # Common columns for all models
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"


async def init_db() -> None:
    """Initialize database connection and create tables."""
    global async_engine, async_session_factory
    
    try:
        # Create async engine for PostgreSQL
        async_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,  # 1 hour
            connect_args={
                "server_settings": {
                    "application_name": "digi_setu_ai_backend",
                },
                "command_timeout": 60,
            }
        )
        
        # Create session factory with proper async configuration
        async_session_factory = async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,  # Disable autoflush to prevent sync operations
            autocommit=False
        )
        
        # Test connection
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        logger.info("Database connection established successfully")
        
        # Create tables (in production, use Alembic migrations)
        if settings.ENVIRONMENT == "development":
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            
            # Create mock user for development
            await _create_mock_user()
            logger.info("Development mock user created")
        
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise


async def _create_mock_user() -> None:
    """Create a mock user for development."""
    try:
        from app.models.user import User
        
        async with async_session_factory() as db:
            # Check if any user already exists
            from sqlalchemy import select
            result = await db.execute(select(User).limit(1))
            existing_user = result.scalar_one_or_none()
            if existing_user:
                logger.info("Mock user already exists")
                return
            
            # Create mock user (let SQLAlchemy assign the ID automatically)
            mock_user = User(
                google_id="dev_google_id_123",
                email="dev@digisetu.ai",
                name="Development User",
                picture="https://via.placeholder.com/150",
                is_active=True,
                verified_email=True,
                preferred_ai_provider="anthropic",
                theme_preference="light"
            )
            
            db.add(mock_user)
            await db.commit()
            logger.info("Mock user created successfully")
            
    except Exception as e:
        logger.error("Failed to create mock user", error=str(e))
        # Don't raise - this is not critical for basic functionality


async def close_db() -> None:
    """Close database connections."""
    global async_engine
    
    if async_engine:
        await async_engine.dispose()
        logger.info("Database connections closed")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    
    Yields:
        AsyncSession: Database session
    """
    if not async_session_factory:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with async_session_factory() as session:
        try:
            # Ensure the session is properly bound to the async context
            yield session
        except Exception as e:
            logger.error("Database session error", error=str(e))
            await session.rollback()
            raise
        finally:
            try:
                await session.close()
            except Exception as close_error:
                logger.warning("Error closing database session", error=str(close_error))


class DatabaseHealthCheck:
    """Database health check utilities."""
    
    @staticmethod
    async def check_connection() -> bool:
        """Check if database connection is healthy."""
        try:
            if not async_engine:
                return False
            
            async with async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False
    
    @staticmethod
    async def get_connection_info() -> dict:
        """Get database connection information."""
        if not async_engine:
            return {"status": "not_initialized"}
        
        try:
            pool_info = async_engine.pool
            return {
                "status": "connected",
                "pool_size": pool_info.size(),
                "checked_in": pool_info.checkedin(),
                "checked_out": pool_info.checkedout(),
                "overflow": pool_info.overflow(),
                "invalid": pool_info.invalid(),
            }
        except Exception as e:
            logger.error("Failed to get connection info", error=str(e))
            return {"status": "error", "error": str(e)}


# PostgreSQL connection configuration is handled in the engine setup


# Query logging is handled by SQLAlchemy's echo parameter
# Event listeners removed to avoid initialization issues
