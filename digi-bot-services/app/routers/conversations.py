"""
Conversations Router - Conversation Management

Handles conversation CRUD operations, title generation, and conversation history.
"""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import structlog

from app.core.enhanced_auth_deps import CurrentUser, AuthenticatedUserWithCSRF
from app.core.database import get_db_session
from app.models.user import User
from app.models.conversation import Conversation, ConversationStatus

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


class ConversationCreate(BaseModel):
    """Request model for creating a conversation."""
    title: str = "Untitled"
    ai_provider: Optional[str] = "anthropic"


class ConversationUpdate(BaseModel):
    """Request model for updating a conversation."""
    title: Optional[str] = None
    status: Optional[ConversationStatus] = None
    is_pinned: Optional[bool] = None


class ConversationResponse(BaseModel):
    """Response model for conversation."""
    id: int
    title: str
    summary: Optional[str]
    status: str
    is_pinned: bool
    message_count: int
    created_at: str
    updated_at: str
    last_message_at: Optional[str]


@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = CurrentUser,
    limit: int = 50,
    offset: int = 0
):
    """Get user's conversations."""
    try:
        # Query conversations for the current user
        query = (
            select(Conversation)
            .where(Conversation.user_id == current_user["id"])
            .where(Conversation.status != ConversationStatus.DELETED)
            .order_by(desc(Conversation.last_message_at), desc(Conversation.updated_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await db.execute(query)
        conversations = result.scalars().all()
        
        return [
            ConversationResponse(
                id=conv.id,
                title=conv.title,
                summary=conv.summary,
                status=conv.status.value,
                is_pinned=conv.is_pinned,
                message_count=conv.message_count,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                last_message_at=conv.last_message_at.isoformat() if conv.last_message_at else None
            )
            for conv in conversations
        ]
    
    except Exception as e:
        logger.error("Error fetching conversations", error=str(e), user_id=current_user["id"])
        raise HTTPException(status_code=500, detail="Failed to fetch conversations")


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: dict = AuthenticatedUserWithCSRF,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new conversation."""
    try:
        conversation = Conversation(
            title=conversation_data.title,
            ai_provider=conversation_data.ai_provider,
            user_id=current_user["id"],
            status=ConversationStatus.ACTIVE
        )
        
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        
        logger.info("Conversation created", conversation_id=conversation.id, user_id=current_user["id"])
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            summary=conversation.summary,
            status=conversation.status.value,
            is_pinned=conversation.is_pinned,
            message_count=conversation.message_count,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            last_message_at=conversation.last_message_at.isoformat() if conversation.last_message_at else None
        )
    
    except Exception as e:
        logger.error("Error creating conversation", error=str(e), user_id=current_user["id"])
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: dict = CurrentUser,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific conversation."""
    try:
        query = (
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == current_user.id)
            .where(Conversation.status != ConversationStatus.DELETED)
        )
        
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            summary=conversation.summary,
            status=conversation.status.value,
            is_pinned=conversation.is_pinned,
            message_count=conversation.message_count,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            last_message_at=conversation.last_message_at.isoformat() if conversation.last_message_at else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching conversation", error=str(e), conversation_id=conversation_id)
        raise HTTPException(status_code=500, detail="Failed to fetch conversation")


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    update_data: ConversationUpdate,
    current_user: dict = AuthenticatedUserWithCSRF,
    db: AsyncSession = Depends(get_db_session)
):
    """Update a conversation."""
    try:
        query = (
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == current_user.id)
            .where(Conversation.status != ConversationStatus.DELETED)
        )
        
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Update fields
        if update_data.title is not None:
            conversation.title = update_data.title
        if update_data.status is not None:
            conversation.status = update_data.status
        if update_data.is_pinned is not None:
            conversation.is_pinned = update_data.is_pinned
        
        await db.commit()
        await db.refresh(conversation)
        
        logger.info("Conversation updated", conversation_id=conversation.id, user_id=current_user["id"])
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            summary=conversation.summary,
            status=conversation.status.value,
            is_pinned=conversation.is_pinned,
            message_count=conversation.message_count,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            last_message_at=conversation.last_message_at.isoformat() if conversation.last_message_at else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating conversation", error=str(e), conversation_id=conversation_id)
        raise HTTPException(status_code=500, detail="Failed to update conversation")


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: dict = AuthenticatedUserWithCSRF,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a conversation (soft delete)."""
    try:
        query = (
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == current_user.id)
            .where(Conversation.status != ConversationStatus.DELETED)
        )
        
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Soft delete
        conversation.status = ConversationStatus.DELETED
        await db.commit()
        
        logger.info("Conversation deleted", conversation_id=conversation.id, user_id=current_user["id"])
        
        return {"message": "Conversation deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting conversation", error=str(e), conversation_id=conversation_id)
        raise HTTPException(status_code=500, detail="Failed to delete conversation")
