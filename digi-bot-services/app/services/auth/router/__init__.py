"""
Authentication Router Module

Contains FastAPI routers for authentication endpoints including
Google OAuth integration and secure token management.
"""

from .enhanced_auth_router import router as enhanced_auth_router

__all__ = [
    "enhanced_auth_router"
]
