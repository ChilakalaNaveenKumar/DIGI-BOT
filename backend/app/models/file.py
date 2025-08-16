"""
File Model

Database model for file storage and metadata.
"""

from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class File(Base):
    """File model for storing file metadata."""
    
    __tablename__ = "files"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # File identification
    file_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    original_filename = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)  # Stored filename
    
    # File properties
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    content_type = Column(String(100), nullable=False)
    
    # File metadata
    extra_data = Column(JSON, default=dict)  # Additional file-specific metadata
    
    # Processing status
    status = Column(String(20), default="uploaded")  # uploaded, processing, ready, error
    processing_error = Column(Text, nullable=True)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="files")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<File(id={self.id}, filename='{self.filename}', size={self.file_size})>"
    
    @property
    def url(self) -> str:
        """Get the public URL for this file."""
        return f"/api/v1/files/{self.file_id}"
    
    @property
    def is_image(self) -> bool:
        """Check if this file is an image."""
        return self.content_type.startswith('image/')
    
    @property
    def is_document(self) -> bool:
        """Check if this file is a document."""
        document_types = [
            'application/pdf',
            'text/plain',
            'text/markdown',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        return self.content_type in document_types
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get a metadata value."""
        return self.extra_data.get(key, default) if self.extra_data else default
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set a metadata value."""
        if not self.extra_data:
            self.extra_data = {}
        self.extra_data[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "file_id": self.file_id,
            "original_filename": self.original_filename,
            "filename": self.filename,
            "file_size": self.file_size,
            "content_type": self.content_type,
            "metadata": self.extra_data,
            "status": self.status,
            "url": self.url,
            "is_image": self.is_image,
            "is_document": self.is_document,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
