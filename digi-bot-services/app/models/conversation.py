"""
CLEAN CONVERSATION MODELS - PERFORMANCE OPTIMIZED
================================================

Removes all unused fields and implements conversation archiving.
Only essential fields for maximum performance.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import (
    Boolean, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, 
    String, Text, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.file import File


class MessageRole(str, Enum):
    """Message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessagePartType(str, Enum):
    """Types of message parts - essential only."""
    TEXT = "text"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    IMAGE = "image"
    FILE = "file"


class ContentType(str, Enum):
    """Content types for message parts."""
    TEXT = "text"
    MARKDOWN = "markdown"
    CODE = "code"
    JSON = "json"


class ConversationStatus(str, Enum):
    """Conversation status - simplified."""
    ACTIVE = "active"
    DELETED = "deleted"  # Soft delete only


class Conversation(Base):
    """Active conversation model - last 50 conversations per user."""
    
    __tablename__ = "conversations"
    
    # Basic information - CLEAN & MINIMAL
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    
    # Status - simplified
    status: Mapped[ConversationStatus] = mapped_column(
        SQLEnum(ConversationStatus),
        default=ConversationStatus.ACTIVE,
        nullable=False
    )
    
    # Performance fields (cached)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps for sorting
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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
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
            "status": self.status.value,
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "user_id": self.user_id,
            "storage_type": "active"
        }


class Message(Base):
    """Active message model."""
    
    __tablename__ = "messages"
    
    # Message content
    role: Mapped[MessageRole] = mapped_column(SQLEnum(MessageRole), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    
    # AI Information - ONLY HERE (where it's actually used)
    ai_provider: Mapped[Optional[str]] = mapped_column(String(50))  # anthropic, openai, grok
    ai_model: Mapped[Optional[str]] = mapped_column(String(100))    # claude-3-sonnet, gpt-4, etc
    
    # Performance metrics
    token_count: Mapped[Optional[int]] = mapped_column(Integer)
    processing_time: Mapped[Optional[float]] = mapped_column(Float)
    
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
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    parts: Mapped[List["MessagePart"]] = relationship(
        "MessagePart",
        back_populates="message",
        cascade="all, delete-orphan",
        order_by="MessagePart.order_index"
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
            "token_count": self.token_count,
            "processing_time": self.processing_time,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "conversation_id": self.conversation_id,
            "parts": [part.to_dict() for part in self.parts] if self.parts else [],
        }


class MessagePart(Base):
    """Active message part model."""
    
    __tablename__ = "message_parts"
    
    # Content information
    type: Mapped[MessagePartType] = mapped_column(SQLEnum(MessagePartType), nullable=False)
    content_type: Mapped[Optional[ContentType]] = mapped_column(SQLEnum(ContentType))
    content: Mapped[Optional[str]] = mapped_column(Text)
    
    # Structure
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Tool information (for tool calls/results)
    tool_name: Mapped[Optional[str]] = mapped_column(String(100))
    tool_input: Mapped[Optional[dict]] = mapped_column(JSON)
    tool_output: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # File information
    file_id: Mapped[Optional[int]] = mapped_column(ForeignKey("files.id", ondelete="SET NULL"))
    file_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Foreign keys
    message_id: Mapped[int] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), 
        nullable=False
    )
    
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
            "order": self.order_index,
            "tool_name": self.tool_name,
            "tool_input": self.tool_input,
            "tool_output": self.tool_output,
            "file_id": self.file_id,
            "file_url": self.file_url,
            "created_at": self.created_at.isoformat(),
            "message_id": self.message_id,
        }
