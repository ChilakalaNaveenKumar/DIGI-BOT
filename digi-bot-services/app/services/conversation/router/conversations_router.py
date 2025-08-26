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

from app.services.auth import get_current_user_required, get_current_user_from_cookie

# Create dependency aliases for backward compatibility
CurrentUser = Depends(get_current_user_required)
AuthenticatedUserWithCSRF = Depends(get_current_user_required)  # Using same for now
from app.core.database import get_db_session
from app.models.user import User
from app.models.conversation import Conversation, ConversationStatus, Message, MessageRole
from datetime import datetime, timezone

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


class ConversationCreate(BaseModel):
    """Request model for creating a conversation."""
    title: str = "Untitled"
    ai_provider: Optional[str] = "anthropic"


class SaveConversationRequest(BaseModel):
    """Request model for saving a complete conversation with messages."""
    title: str
    user_message: str
    assistant_message: str
    reasoning_steps: Optional[List[dict]] = None
    ai_provider: str = "anthropic"
    ai_model: str = "claude-sonnet-4-20250514"
    processing_time: Optional[float] = None


class AddMessageRequest(BaseModel):
    """Request model for adding a message to an existing conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    reasoning_steps: Optional[dict] = None
    token_count: Optional[int] = None
    processing_time: Optional[float] = None


class ConversationUpdate(BaseModel):
    """Request model for updating a conversation."""
    title: Optional[str] = None
    status: Optional[ConversationStatus] = None


class ConversationResponse(BaseModel):
    """Response model for conversation - CLEAN VERSION."""
    id: int
    title: str
    status: str
    message_count: int
    created_at: str
    updated_at: str
    last_message_at: Optional[str]
    storage_type: str = "active"


class MessageResponse(BaseModel):
    """Response model for message."""
    id: int
    role: str
    content: Optional[str]
    ai_provider: Optional[str]
    ai_model: Optional[str]
    token_count: Optional[int]
    processing_time: Optional[float]
    reasoning_steps: Optional[dict]
    created_at: str
    updated_at: str


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
                status=conv.status.value,
                message_count=conv.message_count,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                last_message_at=conv.last_message_at.isoformat() if conv.last_message_at else None,
                storage_type="active"
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
            status=conversation.status.value,
            message_count=conversation.message_count,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            last_message_at=conversation.last_message_at.isoformat() if conversation.last_message_at else None,
            storage_type="active"
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
            status=conversation.status.value,
            message_count=conversation.message_count,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            last_message_at=conversation.last_message_at.isoformat() if conversation.last_message_at else None,
            storage_type="active"
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
        
        await db.commit()
        await db.refresh(conversation)
        
        logger.info("Conversation updated", conversation_id=conversation.id, user_id=current_user["id"])
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            status=conversation.status.value,
            message_count=conversation.message_count,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            last_message_at=conversation.last_message_at.isoformat() if conversation.last_message_at else None,
            storage_type="active"
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


@router.post("/save-complete", response_model=ConversationResponse)
async def save_complete_conversation(
    request: SaveConversationRequest,
    current_user: dict = AuthenticatedUserWithCSRF,
    db: AsyncSession = Depends(get_db_session)
):
    """Save a complete conversation with user and assistant messages."""
    try:
        # Create conversation
        conversation = Conversation(
            title=request.title,
            user_id=current_user["id"],
            status=ConversationStatus.ACTIVE,
            message_count=0
        )
        
        db.add(conversation)
        await db.flush()  # Get the ID
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.user_message,
            token_count=len(request.user_message.split()) * 1.33  # Rough estimate
        )
        db.add(user_message)
        
        # Save assistant message with reasoning steps
        assistant_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=request.assistant_message,
            ai_provider=request.ai_provider,
            ai_model=request.ai_model,
            processing_time=request.processing_time,
            reasoning_steps={"steps": request.reasoning_steps} if request.reasoning_steps else None,
            token_count=len(request.assistant_message.split()) * 1.33  # Rough estimate
        )
        db.add(assistant_message)
        
        # Update conversation stats
        conversation.message_count = 2
        conversation.last_message_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(conversation)
        
        logger.info("Complete conversation saved", 
                   conversation_id=conversation.id, 
                   user_id=current_user["id"],
                   has_reasoning=bool(request.reasoning_steps))
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            status=conversation.status.value,
            message_count=conversation.message_count,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            last_message_at=conversation.last_message_at.isoformat() if conversation.last_message_at else None,
            storage_type="active"
        )
    
    except Exception as e:
        logger.error("Error saving complete conversation", error=str(e), user_id=current_user["id"])
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to save conversation")


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    current_user: dict = CurrentUser,
    db: AsyncSession = Depends(get_db_session),
    limit: int = 100,
    offset: int = 0
):
    """Get all messages for a conversation."""
    try:
        # First verify the conversation belongs to the user
        conv_query = (
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == current_user["id"])
            .where(Conversation.status != ConversationStatus.DELETED)
        )
        
        conv_result = await db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages for the conversation
        messages_query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
            .offset(offset)
        )
        
        messages_result = await db.execute(messages_query)
        messages = messages_result.scalars().all()
        
        return [
            MessageResponse(
                id=msg.id,
                role=msg.role.value,
                content=msg.content,
                ai_provider=msg.ai_provider,
                ai_model=msg.ai_model,
                token_count=msg.token_count,
                processing_time=msg.processing_time,
                reasoning_steps=msg.reasoning_steps,
                created_at=msg.created_at.isoformat(),
                updated_at=msg.updated_at.isoformat()
            )
            for msg in messages
        ]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching conversation messages", error=str(e), conversation_id=conversation_id)
        raise HTTPException(status_code=500, detail="Failed to fetch conversation messages")


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def add_message_to_conversation(
    conversation_id: int,
    request: AddMessageRequest,
    current_user: dict = AuthenticatedUserWithCSRF,
    db: AsyncSession = Depends(get_db_session)
):
    """Add a new message to an existing conversation."""
    try:
        # Verify conversation exists and belongs to user
        conversation = await db.get(Conversation, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.user_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Create new message
        message = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER if request.role.lower() == 'user' else MessageRole.ASSISTANT,
            content=request.content,
            ai_provider=request.ai_provider,
            ai_model=request.ai_model,
            reasoning_steps=request.reasoning_steps,
            token_count=request.token_count,
            processing_time=request.processing_time
        )
        
        db.add(message)
        
        # Update conversation stats
        conversation.message_count += 1
        conversation.last_message_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(message)
        
        logger.info("Message added to conversation", 
                   conversation_id=conversation_id, 
                   message_id=message.id,
                   role=request.role,
                   user_id=current_user["id"])
        
        return MessageResponse(
            id=message.id,
            role=message.role.value,
            content=message.content,
            ai_provider=message.ai_provider,
            ai_model=message.ai_model,
            token_count=message.token_count,
            processing_time=message.processing_time,
            reasoning_steps=message.reasoning_steps,
            created_at=message.created_at.isoformat(),
            updated_at=message.updated_at.isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error adding message to conversation", 
                    error=str(e), 
                    conversation_id=conversation_id,
                    user_id=current_user["id"])
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add message to conversation")
