"""
Digi Setu AI Backend - Main Application

Modern FastAPI application with proper structure, middleware, and error handling.
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
# Middleware imports moved to middleware.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.core.exceptions import DigiSetuException
from app.core.logging import setup_logging
from app.core.middleware import (
    SecurityHeadersMiddleware,
    TimingMiddleware,
    RateLimitMiddleware,
    setup_middleware,
)
from app.routers import ai_chat, vision, audio, tools, search, multimodal_chat, advanced_features, component_analysis

# Initialize settings
settings = get_settings()

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting Digi Setu AI Backend", version=app.version)
    
    try:
        # Initialize database
        await init_db()
        logger.info("✅ Database initialized successfully")
        
        # Initialize AI services
        from app.services.ai_orchestrator import AIOrchestrator
        orchestrator = AIOrchestrator()
        await orchestrator.initialize()
        app.state.ai_orchestrator = orchestrator
        logger.info("✅ AI Orchestrator initialized successfully")
        
        # Initialize file storage
        from app.services.file_service import FileService
        file_service = FileService()
        await file_service.initialize()
        app.state.file_service = file_service
        logger.info("✅ File Service initialized successfully")
        
        logger.info("🎉 Digi Setu AI Backend started successfully")
        
    except Exception as e:
        logger.error("❌ Failed to start application", error=str(e))
        sys.exit(1)
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Digi Setu AI Backend")
    
    try:
        # Cleanup AI services
        if hasattr(app.state, 'ai_orchestrator'):
            await app.state.ai_orchestrator.cleanup()
            logger.info("✅ AI Orchestrator cleaned up")
        
        # Cleanup file service
        if hasattr(app.state, 'file_service'):
            await app.state.file_service.cleanup()
            logger.info("✅ File Service cleaned up")
        
        # Close database connections
        await close_db()
        logger.info("✅ Database connections closed")
        
        logger.info("👋 Digi Setu AI Backend shutdown complete")
        
    except Exception as e:
        logger.error("❌ Error during shutdown", error=str(e))


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Digi Setu AI Backend",
        description=(
            "Advanced AI Assistant Backend with multi-provider orchestration, "
            "reasoning display, activity streaming, and comprehensive content handling."
        ),
        version="2.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )
    
    # Security middleware
    if settings.ENVIRONMENT == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )
    
    # Setup all middleware
    setup_middleware(app)
    
    # Exception handlers
    @app.exception_handler(DigiSetuException)
    async def digi_setu_exception_handler(request: Request, exc: DigiSetuException):
        """Handle custom Digi Setu exceptions."""
        logger.error(
            "Digi Setu exception occurred",
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        logger.warning(
            "HTTP exception occurred",
            status_code=exc.status_code,
            detail=exc.detail,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                }
            },
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        logger.warning(
            "Validation error occurred",
            errors=exc.errors(),
            path=request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": exc.errors(),
                }
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(
            "Unexpected exception occurred",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )
    
    # Include routers
    # TODO: Create these routers as needed
    # app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    # app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    # app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    # app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
    # app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["Conversations"])
    app.include_router(ai_chat.router, prefix="/api/v1/chat", tags=["AI Chat"])
    app.include_router(multimodal_chat.router, prefix="/api/v1", tags=["Multimodal Chat"])
    app.include_router(advanced_features.router, prefix="/api/v1", tags=["Advanced Features"])
    app.include_router(component_analysis.router, prefix="/api/v1/components", tags=["Component Analysis"])
    app.include_router(vision.router, prefix="/api/v1", tags=["Vision"])
    app.include_router(audio.router, prefix="/api/v1", tags=["Audio"])
    app.include_router(tools.router, prefix="/api/v1", tags=["Tools"])
    app.include_router(search.router, prefix="/api/v1", tags=["Search"])
    # app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
    
    # Simple health endpoint
    @app.get("/api/v1/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "digi-setu-ai-backend"}
    
    # Metrics endpoint for monitoring
    if settings.ENABLE_METRICS:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
    
    return app


# Create the application instance
app = create_application()


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with basic information."""
    return {
        "service": "Digi Setu AI Backend",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs" if settings.ENVIRONMENT != "production" else None,
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        server_header=False,
        date_header=False,
    )
