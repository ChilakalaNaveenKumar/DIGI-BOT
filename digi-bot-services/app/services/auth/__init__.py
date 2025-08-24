"""
Authentication Service Module

This module provides comprehensive authentication and authorization services
including JWT token management, Google OAuth integration, and security features.

Structure:
- core/: Core authentication components (security, dependencies)
- service/: Authentication service implementations
- router/: FastAPI routers for authentication endpoints

Components:
- AuthService: Core authentication service with password hashing and user verification
- SecurityManager: Token management, CSRF protection, and security logging
- auth_deps: FastAPI dependencies for authentication
- enhanced_auth_router: FastAPI router with secure authentication endpoints
"""

# Import from subdirectories
from .core import SecurityManager, security_manager, get_current_user_from_cookie, get_current_user_required
from .service import AuthService
from .router import enhanced_auth_router

__all__ = [
    "AuthService",
    "SecurityManager", 
    "security_manager",
    "get_current_user_from_cookie",
    "get_current_user_required",
    "enhanced_auth_router"
]
