"""
Conversation Service

Manages conversation CRUD operations, message handling, and history management.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

import structlog
from sqlalchemy import desc, func, and_, select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, Message, MessagePart, MessageRole, MessagePartType
from app.models.user import User
from app.models.project import Project
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)


class ConversationService:
    """Service for managing conversations and messages."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_conversation(
        self,
        user_id: int,
        title: str,
        project_id: Optional[int] = None,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
        ai_settings: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """Create a new conversation."""
        
        try:
            conversation = Conversation(
                title=title,
                user_id=user_id,
                project_id=project_id,
                ai_provider=ai_provider,
                ai_model=ai_model,
                ai_settings=ai_settings or {}
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
        """Get a conversation by ID for a specific user."""
        
        try:
            result = await self.db.execute(
                select(Conversation)
                .options(
                    selectinload(Conversation.project),
                    selectinload(Conversation.messages).selectinload(Message.parts)
                )
                .where(
                    and_(
                        Conversation.id == conversation_id,
                        Conversation.user_id == user_id
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
        project_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Conversation]:
        """Get conversations for a user."""
        
        try:
            query = (
                select(Conversation)
                .options(selectinload(Conversation.project))
                .where(Conversation.user_id == user_id)
                .order_by(desc(Conversation.updated_at))
                .limit(limit)
                .offset(offset)
            )
            
            if project_id:
                query = query.where(Conversation.project_id == project_id)
            
            result = await self.db.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            logger.error(
                "Failed to get user conversations",
                user_id=user_id,
                project_id=project_id,
                error=str(e)
            )
            return []
    
    async def update_conversation(
        self,
        conversation_id: int,
        user_id: int,
        **updates
    ) -> Optional[Conversation]:
        """Update a conversation."""
        
        try:
            conversation = await self.get_conversation(conversation_id, user_id)
            if not conversation:
                return None
            
            for key, value in updates.items():
                if hasattr(conversation, key):
                    setattr(conversation, key, value)
            
            conversation.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(conversation)
            
            logger.info(
                "Conversation updated",
                conversation_id=conversation_id,
                updates=list(updates.keys())
            )
            
            return conversation
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to update conversation",
                conversation_id=conversation_id,
                error=str(e)
            )
            return None
    
    async def delete_conversation(
        self,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """Delete a conversation."""
        
        try:
            conversation = await self.get_conversation(conversation_id, user_id)
            if not conversation:
                return False
            
            await self.db.delete(conversation)
            await self.db.commit()
            
            logger.info(
                "Conversation deleted",
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to delete conversation",
                conversation_id=conversation_id,
                error=str(e)
            )
            return False
    
    async def add_message(
        self,
        conversation_id: int,
        role: MessageRole,
        content: Optional[str] = None,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
        files: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Add a message to a conversation."""
        
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                ai_provider=ai_provider,
                ai_model=ai_model,
                metadata=metadata or {}
            )
            
            self.db.add(message)
            await self.db.flush()  # Get the message ID
            
            # Add file parts if provided
            if files:
                for i, file_data in enumerate(files):
                    file_part = MessagePart(
                        message_id=message.id,
                        type=MessagePartType.FILE,
                        order=i,
                        file_url=file_data.get('url'),
                        metadata={
                            'filename': file_data.get('name'),
                            'size': file_data.get('size'),
                            'type': file_data.get('type')
                        }
                    )
                    self.db.add(file_part)
            
            await self.db.commit()
            await self.db.refresh(message)
            
            # Update conversation stats
            await self._update_conversation_stats(conversation_id)
            
            logger.info(
                "Message added",
                message_id=message.id,
                conversation_id=conversation_id,
                role=role.value
            )
            
            return message
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to add message",
                conversation_id=conversation_id,
                role=role.value,
                error=str(e)
            )
            raise DigiSetuException(
                status_code=500,
                error_code="MESSAGE_CREATE_ERROR",
                message="Failed to add message"
            )
    
    async def update_message(
        self,
        message_id: int,
        content: Optional[str] = None,
        parts: Optional[List[Dict[str, Any]]] = None,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
        tokens_used: Optional[int] = None
    ) -> Optional[Message]:
        """Update an existing message."""
        try:
            # Get the message
            result = await self.db.execute(
                select(Message).where(Message.id == message_id)
            )
            message = result.scalar_one_or_none()
            
            if not message:
                logger.warning("Message not found for update", message_id=message_id)
                return None
            
            # Update fields
            if content is not None:
                message.content = content
            if parts is not None:
                message.parts = parts
            if ai_provider is not None:
                message.ai_provider = ai_provider
            if ai_model is not None:
                message.ai_model = ai_model
            if tokens_used is not None:
                message.tokens_used = tokens_used
            
            message.updated_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(message)
            
            logger.info("Message updated successfully", message_id=message_id)
            return message
            
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Failed to update message",
                message_id=message_id,
                error=str(e)
            )
            return None
    
    async def get_message(
        self,
        message_id: int,
        user_id: int
    ) -> Optional[Message]:
        """Get a message by ID."""
        
        try:
            result = await self.db.execute(
                select(Message)
                .join(Conversation)
                .options(selectinload(Message.parts))
                .where(
                    and_(
                        Message.id == message_id,
                        Conversation.user_id == user_id
                    )
                )
            )
            
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(
                "Failed to get message",
                message_id=message_id,
                user_id=user_id,
                error=str(e)
            )
            return None
    
    async def get_conversation_history(
        self,
        conversation_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """Get conversation message history."""
        
        try:
            result = await self.db.execute(
                select(Message)
                .options(selectinload(Message.parts))
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
                .limit(limit)
                .offset(offset)
            )
            
            return result.scalars().all()
            
        except Exception as e:
            logger.error(
                "Failed to get conversation history",
                conversation_id=conversation_id,
                error=str(e)
            )
            return []
    
    async def get_previous_user_message(
        self,
        message_id: int
    ) -> Optional[Message]:
        """Get the previous user message before a given message."""
        
        try:
            # Get the current message to find its conversation and timestamp
            current_message = await self.db.execute(
                select(Message)
                .where(Message.id == message_id)
            )
            current = current_message.scalar_one_or_none()
            
            if not current:
                return None
            
            # Find the previous user message
            result = await self.db.execute(
                select(Message)
                .where(
                    and_(
                        Message.conversation_id == current.conversation_id,
                        Message.role == MessageRole.USER,
                        Message.created_at < current.created_at
                    )
                )
                .order_by(desc(Message.created_at))
                .limit(1)
            )
            
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(
                "Failed to get previous user message",
                message_id=message_id,
                error=str(e)
            )
            return None
    
    async def update_conversation_stats(
        self,
        conversation_id: int
    ) -> None:
        """Update conversation statistics."""
        await self._update_conversation_stats(conversation_id)
    
    async def _update_conversation_stats(
        self,
        conversation_id: int
    ) -> None:
        """Internal method to update conversation statistics."""
        
        try:
            # Count messages
            message_count_result = await self.db.execute(
                select(func.count(Message.id))
                .where(Message.conversation_id == conversation_id)
            )
            message_count = message_count_result.scalar() or 0
            
            # Sum tokens
            token_sum_result = await self.db.execute(
                select(func.sum(Message.token_count))
                .where(Message.conversation_id == conversation_id)
            )
            total_tokens = token_sum_result.scalar() or 0
            
            # Get last message timestamp
            last_message_result = await self.db.execute(
                select(Message.created_at)
                .where(Message.conversation_id == conversation_id)
                .order_by(desc(Message.created_at))
                .limit(1)
            )
            last_message_at = last_message_result.scalar()
            
            # Update conversation
            await self.db.execute(
                update(Conversation)
                .where(Conversation.id == conversation_id)
                .values(
                    message_count=message_count,
                    total_tokens=total_tokens,
                    last_message_at=last_message_at,
                    updated_at=datetime.utcnow()
                )
            )
            
            await self.db.commit()
            
        except Exception as e:
            logger.error(
                "Failed to update conversation stats",
                conversation_id=conversation_id,
                error=str(e)
            )
    
    async def search_conversations(
        self,
        user_id: int,
        query: str,
        limit: int = 20
    ) -> List[Conversation]:
        """Search conversations by title and content."""
        
        try:
            result = await self.db.execute(
                select(Conversation)
                .options(selectinload(Conversation.project))
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        or_(
                            Conversation.title.ilike(f"%{query}%"),
                            Conversation.summary.ilike(f"%{query}%")
                        )
                    )
                )
                .order_by(desc(Conversation.updated_at))
                .limit(limit)
            )
            
            return result.scalars().all()
            
        except Exception as e:
            logger.error(
                "Failed to search conversations",
                user_id=user_id,
                query=query,
                error=str(e)
            )
            return []
