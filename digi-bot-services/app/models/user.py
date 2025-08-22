"""
User model for Google OAuth authentication.
Simplified version for digi-bot-services.
"""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.file import File


class User(Base):
    """User model for Google OAuth authentication."""
    
    __tablename__ = "users"
    
    # Google OAuth information
    google_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    picture: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    verified_email: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Preferences
    preferred_ai_provider: Mapped[str] = mapped_column(String(50), default="anthropic")
    theme_preference: Mapped[str] = mapped_column(String(20), default="system")
    conversation_history_limit: Mapped[int] = mapped_column(Integer, default=20)
    
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
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Conversation.updated_at.desc()"
    )
    files: Mapped[List["File"]] = relationship(
        "File",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
    
    @property
    def display_name(self) -> str:
        """Get display name."""
        return self.name
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding sensitive data)."""
        # Use getattr with defaults to avoid lazy loading issues
        return {
            "id": getattr(self, 'id', None),
            "google_id": getattr(self, 'google_id', ''),
            "email": getattr(self, 'email', ''),
            "name": getattr(self, 'name', ''),
            "display_name": getattr(self, 'name', ''),  # display_name is a property
            "picture": getattr(self, 'picture', None),
            "is_active": getattr(self, 'is_active', True),
            "verified_email": getattr(self, 'verified_email', False),
            "preferred_ai_provider": getattr(self, 'preferred_ai_provider', 'anthropic'),
            "theme_preference": getattr(self, 'theme_preference', 'system'),
            "conversation_history_limit": getattr(self, 'conversation_history_limit', 20),
            "created_at": self.created_at.isoformat() if getattr(self, 'created_at', None) else None,
            "updated_at": self.updated_at.isoformat() if getattr(self, 'updated_at', None) else None,
            "last_login_at": self.last_login_at.isoformat() if getattr(self, 'last_login_at', None) else None,
        }
