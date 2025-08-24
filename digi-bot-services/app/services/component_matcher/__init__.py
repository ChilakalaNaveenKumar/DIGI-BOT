"""
Component Matcher with o1-preview and Vector Store Management

This package provides intelligent component format matching using OpenAI's models
and vector store management for component documentation.

Components:
- ComponentMatcherClient: Intelligent format matching for component queries
- VectorStoreManager: Document management for component format templates
- Examples: Comprehensive usage examples and integration patterns
"""

from .client import ComponentMatcherClient
from .vector_manager import VectorStoreManager

__all__ = ['ComponentMatcherClient', 'VectorStoreManager']