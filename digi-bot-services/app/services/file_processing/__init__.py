"""
File Processing Service Package

This package provides clients for file analysis and vector store management:
- FileAnalyzer: Extract text from various document types with configurable limits
- VectorStoreSaver: Manage files in OpenAI vector stores with automatic expiry
- AnalyzeLimits: Configuration for file processing limits
- AnalyzeResult: Structured results from file analysis

Supported file types:
- Text: .txt, .md, .csv, .tsv, .json, .log
- Documents: .pdf, .docx, .pptx, .xlsx  
- Code: .py, .js, .ts, .html, .css, .java, .c, .cpp, .go, .rs, .sh, .sql, .yaml, .yml, .xml
- Images: .png, .jpg, .jpeg, .webp (with optional OCR)
"""

from .file_analyzer import FileAnalyzer, AnalyzeLimits, AnalyzeResult
from .vector_store_saver import VectorStoreSaver
from .text_vector_saver import TextVectorSaver
from .user_vector_store import UserVectorStoreManager
from .file_aware_chat import FileAwareChatService
from .smart_file_context import SmartFileContextDetector

__all__ = ["FileAnalyzer", "AnalyzeLimits", "AnalyzeResult", "VectorStoreSaver", "TextVectorSaver", "UserVectorStoreManager", "FileAwareChatService", "SmartFileContextDetector"]
