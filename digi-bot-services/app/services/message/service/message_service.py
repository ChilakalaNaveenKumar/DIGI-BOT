"""
Message Service

Handles message CRUD operations for both active and archived messages.
Works with ConversationService to maintain conversation statistics.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

import structlog
from sqlalchemy import desc, func, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Message, MessageRole
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)


class MessageService:
    """Service for managing messages only."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_message(
        self,
        conversation_id: int,
        role: MessageRole,
        content: Optional[str] = None,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
        token_count: Optional[int] = None,
        processing_time: Optional[float] = None
    ) -> Message:
        """Create a new message in a conversation."""
        
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                ai_provider=ai_provider,
                ai_model=ai_model,
                token_count=token_count,
                processing_time=processing_time
            )
            
            self.db.add(message)
            await self.db.flush()  # Get the message ID without committing
            
            # We'll commit after message parts are added (if any)
            logger.info(
                "Message created",
                message_id=message.id,
                conversation_id=conversation_id,
                role=role.value
            )
            
            return message
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create message", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="MESSAGE_CREATE_ERROR",
                message="Failed to create message"
            )
    
    async def get_message(
        self,
        message_id: int
    ) -> Optional[Message]:
        """Get a message by ID with its parts."""
        
        try:
            result = await self.db.execute(
                select(Message)
                .options(selectinload(Message.parts))
                .where(Message.id == message_id)
            )
            
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(
                "Failed to get message",
                message_id=message_id,
                error=str(e)
            )
            return None
    
    async def get_conversation_messages(
        self,
        conversation_id: int,
        limit: int = 100,
        offset: int = 0,
        include_parts: bool = True
    ) -> List[Message]:
        """Get messages for a conversation, ordered by creation time."""
        
        try:
            query = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc())
                .limit(limit)
                .offset(offset)
            )
            
            if include_parts:
                query = query.options(selectinload(Message.parts))
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(
                "Failed to get conversation messages",
                conversation_id=conversation_id,
                error=str(e)
            )
            raise DigiSetuException(
                status_code=500,
                error_code="MESSAGES_FETCH_ERROR",
                message="Failed to get messages"
            )
    
    async def update_message(
        self,
        message_id: int,
        content: Optional[str] = None,
        token_count: Optional[int] = None,
        processing_time: Optional[float] = None
    ) -> Optional[Message]:
        """Update message content or metadata."""
        
        try:
            message = await self.db.get(Message, message_id)
            if not message:
                return None
            
            if content is not None:
                message.content = content
            if token_count is not None:
                message.token_count = token_count
            if processing_time is not None:
                message.processing_time = processing_time
            
            await self.db.commit()
            await self.db.refresh(message)
            
            logger.info("Message updated", message_id=message_id)
            return message
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to update message", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="MESSAGE_UPDATE_ERROR",
                message="Failed to update message"
            )
    
    async def delete_message(
        self,
        message_id: int
    ) -> bool:
        """Delete a message and its parts."""
        
        try:
            message = await self.db.get(Message, message_id)
            if not message:
                return False
            
            conversation_id = message.conversation_id
            
            await self.db.delete(message)
            await self.db.commit()
            
            # Update conversation stats after deletion
            await self._update_conversation_stats(conversation_id)
            
            logger.info("Message deleted", message_id=message_id)
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to delete message", error=str(e))
            return False
    
    async def get_latest_user_message(
        self,
        conversation_id: int
    ) -> Optional[Message]:
        """Get the most recent user message in a conversation."""
        
        try:
            result = await self.db.execute(
                select(Message)
                .where(
                    and_(
                        Message.conversation_id == conversation_id,
                        Message.role == MessageRole.USER
                    )
                )
                .order_by(desc(Message.created_at))
                .limit(1)
            )
            
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(
                "Failed to get latest user message",
                conversation_id=conversation_id,
                error=str(e)
            )
            return None
    
    async def get_conversation_history(
        self,
        conversation_id: int,
        max_messages: int = 20
    ) -> List[Dict[str, Any]]:
        """Get conversation history in AI-friendly format."""
        
        try:
            messages = await self.get_conversation_messages(
                conversation_id=conversation_id,
                limit=max_messages,
                include_parts=False
            )
            
            history = []
            for message in messages:
                if message.content:  # Only include messages with content
                    history.append({
                        "role": message.role.value,
                        "content": message.content
                    })
            
            return history
            
        except Exception as e:
            logger.error(
                "Failed to get conversation history",
                conversation_id=conversation_id,
                error=str(e)
            )
            return []
    
    async def commit_message(self, message: Message):
        """Commit a message to the database and update conversation stats."""
        
        try:
            await self.db.commit()
            await self.db.refresh(message)
            
            # Update conversation statistics
            await self._update_conversation_stats(message.conversation_id)
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to commit message", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="MESSAGE_COMMIT_ERROR",
                message="Failed to save message"
            )
    
    async def _update_conversation_stats(self, conversation_id: int):
        """Update conversation statistics after message changes."""
        
        try:
            # Get message count
            result = await self.db.execute(
                select(func.count(Message.id))
                .where(Message.conversation_id == conversation_id)
            )
            message_count = result.scalar()
            
            # Get last message time
            result = await self.db.execute(
                select(func.max(Message.created_at))
                .where(Message.conversation_id == conversation_id)
            )
            last_message_at = result.scalar()
            
            # Import here to avoid circular imports
            from app.services.conversation import ConversationService
            conv_service = ConversationService(self.db)
            await conv_service.update_conversation_stats(
                conversation_id=conversation_id,
                message_count=message_count,
                last_message_at=last_message_at
            )
            
        except Exception as e:
            logger.error("Failed to update conversation stats", error=str(e))
            # Don't raise exception, just log the error
