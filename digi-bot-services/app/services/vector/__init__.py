"""
Vector Services Package

Provides vector database functionality for semantic search and message embeddings.
"""

from .vector_service import VectorService, VectorServiceManager, get_vector_service

__all__ = ["VectorService", "VectorServiceManager", "get_vector_service"]
