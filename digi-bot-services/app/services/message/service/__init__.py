"""
Message Service Module

Contains message service implementations for CRUD operations and message parts.
"""

from .message_service import MessageService
from .message_part_service import MessagePartService

__all__ = [
    "MessageService",
    "MessagePartService"
]
