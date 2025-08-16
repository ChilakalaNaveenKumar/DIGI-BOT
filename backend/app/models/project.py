"""
Project models for organizing conversations and collaboration.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ProjectRole(str, Enum):
    """Project member roles."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class ProjectVisibility(str, Enum):
    """Project visibility levels."""
    PRIVATE = "private"
    TEAM = "team"
    PUBLIC = "public"


class Project(Base):
    """Project model for organizing conversations and collaboration."""
    
    __tablename__ = "projects"
    
    # Basic information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    
    # Settings
    visibility: Mapped[ProjectVisibility] = mapped_column(
        SQLEnum(ProjectVisibility),
        default=ProjectVisibility.PRIVATE,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # AI Configuration
    default_ai_provider: Mapped[Optional[str]] = mapped_column(String(50))
    ai_settings: Mapped[Optional[str]] = mapped_column(Text)  # JSON string
    
    # Metadata
    color: Mapped[Optional[str]] = mapped_column(String(7))  # Hex color
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    
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
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    members: Mapped[List["ProjectMember"]] = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', slug='{self.slug}')>"
    
    @property
    def conversation_count(self) -> int:
        """Get number of conversations in this project."""
        return len(self.conversations) if self.conversations else 0
    
    @property
    def member_count(self) -> int:
        """Get number of members in this project."""
        return len(self.members) if self.members else 0
    
    def to_dict(self) -> dict:
        """Convert project to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "slug": self.slug,
            "visibility": self.visibility.value,
            "is_active": self.is_active,
            "default_ai_provider": self.default_ai_provider,
            "color": self.color,
            "icon": self.icon,
            "conversation_count": self.conversation_count,
            "member_count": self.member_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "owner_id": self.owner_id,
        }


class ProjectMember(Base):
    """Project membership model for collaboration."""
    
    __tablename__ = "project_members"
    
    # Role and permissions
    role: Mapped[ProjectRole] = mapped_column(
        SQLEnum(ProjectRole),
        default=ProjectRole.MEMBER,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    joined_at: Mapped[datetime] = mapped_column(
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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="project_memberships")
    project: Mapped["Project"] = relationship("Project", back_populates="members")
    
    def __repr__(self) -> str:
        return f"<ProjectMember(user_id={self.user_id}, project_id={self.project_id}, role={self.role})>"
    
    def to_dict(self) -> dict:
        """Convert project member to dictionary."""
        return {
            "id": self.id,
            "role": self.role.value,
            "is_active": self.is_active,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
            "project_id": self.project_id,
        }
