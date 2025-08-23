"""
Conversation Service

Handles conversation CRUD operations for both active and archived conversations.
Focused only on conversation-level operations.
"""

from typing import List, Optional
from datetime import datetime

import structlog
from sqlalchemy import desc, func, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, ConversationStatus
from app.models.user import User
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)


class ConversationService:
    """Service for managing conversations only."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_conversation(
        self,
        user_id: int,
        title: str
    ) -> Conversation:
        """Create a new active conversation."""
        
        try:
            conversation = Conversation(
                title=title,
                user_id=user_id,
                status=ConversationStatus.ACTIVE
            )
            
            self.db.add(conversation)
            await self.db.commit()
            await self.db.refresh(conversation)
            
            logger.info(
                "Conversation created",
                conversation_id=conversation.id,
                user_id=user_id,
                title=title
            )
            
            return conversation
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create conversation", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="CONVERSATION_CREATE_ERROR",
                message="Failed to create conversation"
            )
    
    async def get_conversation(
        self, 
        conversation_id: int, 
        user_id: int
    ) -> Optional[Conversation]:
        """Get an active conversation by ID for a specific user."""
        
        try:
            result = await self.db.execute(
                select(Conversation)
                .where(
                    and_(
                        Conversation.id == conversation_id,
                        Conversation.user_id == user_id,
                        Conversation.status == ConversationStatus.ACTIVE
                    )
                )
            )
            
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(
                "Failed to get conversation",
                conversation_id=conversation_id,
                user_id=user_id,
                error=str(e)
            )
            return None
    
    async def get_user_conversations(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        include_deleted: bool = False
    ) -> List[Conversation]:
        """Get active conversations for a user, ordered by last activity."""
        
        try:
            query = (
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(desc(Conversation.last_message_at), desc(Conversation.updated_at))
                .limit(limit)
                .offset(offset)
            )
            
            if not include_deleted:
                query = query.where(Conversation.status == ConversationStatus.ACTIVE)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(
                "Failed to get user conversations",
                user_id=user_id,
                error=str(e)
            )
            raise DigiSetuException(
                status_code=500,
                error_code="CONVERSATIONS_FETCH_ERROR",
                message="Failed to get conversations"
            )
    
    async def update_conversation(
        self,
        conversation_id: int,
        user_id: int,
        title: Optional[str] = None,
        status: Optional[ConversationStatus] = None
    ) -> Optional[Conversation]:
        """Update conversation details."""
        
        try:
            conversation = await self.get_conversation(conversation_id, user_id)
            if not conversation:
                return None
            
            if title is not None:
                conversation.title = title
            if status is not None:
                conversation.status = status
            
            await self.db.commit()
            await self.db.refresh(conversation)
            
            logger.info(
                "Conversation updated",
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            return conversation
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to update conversation", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="CONVERSATION_UPDATE_ERROR",
                message="Failed to update conversation"
            )
    
    async def delete_conversation(
        self,
        conversation_id: int,
        user_id: int,
        soft_delete: bool = True
    ) -> bool:
        """Delete conversation (soft delete by default)."""
        
        try:
            conversation = await self.get_conversation(conversation_id, user_id)
            if not conversation:
                return False
            
            if soft_delete:
                conversation.status = ConversationStatus.DELETED
                await self.db.commit()
            else:
                await self.db.delete(conversation)
                await self.db.commit()
            
            logger.info(
                "Conversation deleted",
                conversation_id=conversation_id,
                user_id=user_id,
                soft_delete=soft_delete
            )
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to delete conversation", error=str(e))
            return False
    
    async def update_conversation_stats(
        self,
        conversation_id: int,
        message_count: Optional[int] = None,
        last_message_at: Optional[datetime] = None
    ):
        """Update conversation statistics (called by MessageService)."""
        
        try:
            conversation = await self.db.get(Conversation, conversation_id)
            if not conversation:
                return
            
            if message_count is not None:
                conversation.message_count = message_count
            if last_message_at is not None:
                conversation.last_message_at = last_message_at
            
            await self.db.commit()
            
        except Exception as e:
            logger.error("Failed to update conversation stats", error=str(e))
            # Don't raise exception, just log the error
    
    async def search_conversations(
        self,
        user_id: int,
        query: str,
        limit: int = 20
    ) -> List[Conversation]:
        """Search conversations by title."""
        
        try:
            result = await self.db.execute(
                select(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.status == ConversationStatus.ACTIVE,
                        Conversation.title.ilike(f"%{query}%")
                    )
                )
                .order_by(desc(Conversation.updated_at))
                .limit(limit)
            )
            
            return result.scalars().all()
            
        except Exception as e:
            logger.error("Failed to search conversations", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="CONVERSATION_SEARCH_ERROR",
                message="Failed to search conversations"
            )