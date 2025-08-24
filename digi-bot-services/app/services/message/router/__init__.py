"""
Message Router Module

Contains FastAPI routers for message endpoints including streaming.
"""

from .stream_router import router as stream_router

__all__ = [
    "stream_router"
]
