"""
Conversation Service Module

This module provides comprehensive conversation management services
including conversation CRUD operations, conversation management, and routing.

Structure:
- core/: Core conversation components (managers, utilities)
- service/: Conversation service implementations
- router/: FastAPI routers for conversation endpoints

Components:
- ConversationService: Core conversation CRUD operations
- ConversationManager: Advanced conversation management and orchestration
- conversations_router: FastAPI router for conversation endpoints
"""

# Import from subdirectories
from .core.conversation_manager import ConversationManager
from .service.conversation_service import ConversationService
from .router.conversations_router import router as conversations_router

__all__ = [
    "ConversationManager",
    "ConversationService",
    "conversations_router"
]
