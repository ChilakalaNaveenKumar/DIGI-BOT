"""
Conversation and message models for chat functionality.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Boolean, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, 
    String, Text, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class MessageRole(str, Enum):
    """Message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessagePartType(str, Enum):
    """Types of message parts."""
    TEXT = "text"
    REASONING = "reasoning"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"


class ContentType(str, Enum):
    """Content types for message parts."""
    TEXT = "text"
    MARKDOWN = "markdown"
    CODE = "code"
    JSON = "json"
    TABLE = "table"
    DIAGRAM = "diagram"
    HTML = "html"


class ConversationStatus(str, Enum):
    """Conversation status."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Conversation(Base):
    """Conversation model for chat sessions."""
    
    __tablename__ = "conversations"
    
    # Basic information
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    
    # Settings
    status: Mapped[ConversationStatus] = mapped_column(
        SQLEnum(ConversationStatus),
        default=ConversationStatus.ACTIVE,
        nullable=False
    )
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # AI Configuration
    ai_provider: Mapped[Optional[str]] = mapped_column(String(50))
    ai_model: Mapped[Optional[str]] = mapped_column(String(100))
    ai_settings: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Metadata
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Statistics
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Foreign keys
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"))
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    
    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, title='{self.title}', user_id={self.user_id})>"
    
    def to_dict(self) -> dict:
        """Convert conversation to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "summary": self.summary,
            "status": self.status.value,
            "is_pinned": self.is_pinned,
            "ai_provider": self.ai_provider,
            "ai_model": self.ai_model,
            "ai_settings": self.ai_settings,
            "tags": self.tags,
            "metadata": self.metadata,
            "message_count": self.message_count,
            "total_tokens": self.total_tokens,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "user_id": self.user_id,
            "project_id": self.project_id,
        }


class Message(Base):
    """Message model for individual chat messages."""
    
    __tablename__ = "messages"
    
    # Basic information
    role: Mapped[MessageRole] = mapped_column(SQLEnum(MessageRole), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)  # Legacy content field
    
    # AI Information
    ai_provider: Mapped[Optional[str]] = mapped_column(String(50))
    ai_model: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Processing information
    processing_time: Mapped[Optional[float]] = mapped_column(Float)
    token_count: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Metadata
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Foreign keys
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), nullable=False)
    parent_message_id: Mapped[Optional[int]] = mapped_column(ForeignKey("messages.id"))
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    parent_message: Mapped[Optional["Message"]] = relationship(
        "Message", 
        remote_side="Message.id",
        back_populates="child_messages"
    )
    child_messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="parent_message",
        cascade="all, delete-orphan"
    )
    parts: Mapped[List["MessagePart"]] = relationship(
        "MessagePart",
        back_populates="message",
        cascade="all, delete-orphan",
        order_by="MessagePart.order"
    )
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"
    
    def to_dict(self) -> dict:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "ai_provider": self.ai_provider,
            "ai_model": self.ai_model,
            "processing_time": self.processing_time,
            "token_count": self.token_count,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "conversation_id": self.conversation_id,
            "parent_message_id": self.parent_message_id,
            "parts": [part.to_dict() for part in self.parts] if self.parts else [],
        }


class MessagePart(Base):
    """Message part model for structured message content."""
    
    __tablename__ = "message_parts"
    
    # Content information
    type: Mapped[MessagePartType] = mapped_column(SQLEnum(MessagePartType), nullable=False)
    content_type: Mapped[Optional[ContentType]] = mapped_column(SQLEnum(ContentType))
    content: Mapped[Optional[str]] = mapped_column(Text)
    
    # Structure
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Tool information (for tool calls/results)
    tool_name: Mapped[Optional[str]] = mapped_column(String(100))
    tool_input: Mapped[Optional[dict]] = mapped_column(JSON)
    tool_output: Mapped[Optional[dict]] = mapped_column(JSON)
    tool_error: Mapped[Optional[str]] = mapped_column(Text)
    
    # File information (for file parts)
    file_id: Mapped[Optional[int]] = mapped_column(ForeignKey("files.id"))
    file_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Metadata
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Foreign keys
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), nullable=False)
    
    # Relationships
    message: Mapped["Message"] = relationship("Message", back_populates="parts")
    file: Mapped[Optional["File"]] = relationship("File")
    
    def __repr__(self) -> str:
        return f"<MessagePart(id={self.id}, type={self.type}, message_id={self.message_id})>"
    
    def to_dict(self) -> dict:
        """Convert message part to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "content_type": self.content_type.value if self.content_type else None,
            "content": self.content,
            "order": self.order,
            "tool_name": self.tool_name,
            "tool_input": self.tool_input,
            "tool_output": self.tool_output,
            "tool_error": self.tool_error,
            "file_id": self.file_id,
            "file_url": self.file_url,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "message_id": self.message_id,
        }
