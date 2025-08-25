"""
Message Service Module

This module provides comprehensive message management services
including message CRUD operations, message parts handling, and streaming.

Structure:
- core/: Core message components (utilities, helpers)
- service/: Message service implementations
- router/: FastAPI routers for message endpoints

Components:
- MessageService: Core message CRUD operations
- MessagePartService: Message parts handling
- stream_router: FastAPI router for message streaming endpoints
"""

# Import from subdirectories
from .service.message_service import MessageService
from .service.message_part_service import MessagePartService
from .router.anthropic_stream_router import router as stream_router

__all__ = [
    "MessageService",
    "MessagePartService", 
    "stream_router"
]
