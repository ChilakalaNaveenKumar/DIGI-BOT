"""
Authentication Core Module

Contains core authentication components including security management,
token handling, and authentication dependencies.
"""

from .security import SecurityManager, security_manager
from .auth_deps import (
    get_current_user_from_cookie,
    get_current_user_required
)

__all__ = [
    "SecurityManager",
    "security_manager", 
    "get_current_user_from_cookie",
    "get_current_user_required"
]
