"""
Message Part Service

Handles message parts (text, tool calls, tool results, files, images).
Works with MessageService to build complete messages.
"""

from typing import List, Optional, Dict, Any
import structlog
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import MessagePart, MessagePartType, ContentType
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)


class MessagePartService:
    """Service for managing message parts only."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_text_part(
        self,
        message_id: int,
        content: str,
        content_type: ContentType = ContentType.TEXT,
        order_index: int = 0
    ) -> MessagePart:
        """Create a text message part."""
        
        try:
            part = MessagePart(
                message_id=message_id,
                type=MessagePartType.TEXT,
                content_type=content_type,
                content=content,
                order_index=order_index
            )
            
            self.db.add(part)
            await self.db.flush()
            
            logger.info(
                "Text part created",
                part_id=part.id,
                message_id=message_id
            )
            
            return part
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create text part", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="MESSAGE_PART_CREATE_ERROR",
                message="Failed to create message part"
            )
    
    async def create_tool_call_part(
        self,
        message_id: int,
        tool_name: str,
        tool_input: Dict[str, Any],
        order_index: int = 0
    ) -> MessagePart:
        """Create a tool call message part."""
        
        try:
            part = MessagePart(
                message_id=message_id,
                type=MessagePartType.TOOL_CALL,
                tool_name=tool_name,
                tool_input=tool_input,
                order_index=order_index
            )
            
            self.db.add(part)
            await self.db.flush()
            
            logger.info(
                "Tool call part created",
                part_id=part.id,
                message_id=message_id,
                tool_name=tool_name
            )
            
            return part
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create tool call part", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="TOOL_CALL_PART_CREATE_ERROR",
                message="Failed to create tool call part"
            )
    
    async def create_tool_result_part(
        self,
        message_id: int,
        tool_name: str,
        tool_output: Dict[str, Any],
        content: Optional[str] = None,
        order_index: int = 0
    ) -> MessagePart:
        """Create a tool result message part."""
        
        try:
            part = MessagePart(
                message_id=message_id,
                type=MessagePartType.TOOL_RESULT,
                tool_name=tool_name,
                tool_output=tool_output,
                content=content,
                order_index=order_index
            )
            
            self.db.add(part)
            await self.db.flush()
            
            logger.info(
                "Tool result part created",
                part_id=part.id,
                message_id=message_id,
                tool_name=tool_name
            )
            
            return part
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create tool result part", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="TOOL_RESULT_PART_CREATE_ERROR",
                message="Failed to create tool result part"
            )
    
    async def create_file_part(
        self,
        message_id: int,
        file_id: Optional[int] = None,
        file_url: Optional[str] = None,
        content: Optional[str] = None,
        order_index: int = 0
    ) -> MessagePart:
        """Create a file message part."""
        
        try:
            part = MessagePart(
                message_id=message_id,
                type=MessagePartType.FILE,
                file_id=file_id,
                file_url=file_url,
                content=content,
                order_index=order_index
            )
            
            self.db.add(part)
            await self.db.flush()
            
            logger.info(
                "File part created",
                part_id=part.id,
                message_id=message_id,
                file_id=file_id
            )
            
            return part
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create file part", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="FILE_PART_CREATE_ERROR",
                message="Failed to create file part"
            )
    
    async def create_image_part(
        self,
        message_id: int,
        file_id: Optional[int] = None,
        file_url: Optional[str] = None,
        content: Optional[str] = None,
        order_index: int = 0
    ) -> MessagePart:
        """Create an image message part."""
        
        try:
            part = MessagePart(
                message_id=message_id,
                type=MessagePartType.IMAGE,
                file_id=file_id,
                file_url=file_url,
                content=content,
                order_index=order_index
            )
            
            self.db.add(part)
            await self.db.flush()
            
            logger.info(
                "Image part created",
                part_id=part.id,
                message_id=message_id,
                file_id=file_id
            )
            
            return part
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create image part", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="IMAGE_PART_CREATE_ERROR",
                message="Failed to create image part"
            )
    
    async def get_message_parts(
        self,
        message_id: int
    ) -> List[MessagePart]:
        """Get all parts for a message, ordered by index."""
        
        try:
            result = await self.db.execute(
                select(MessagePart)
                .where(MessagePart.message_id == message_id)
                .order_by(MessagePart.order_index)
            )
            
            return result.scalars().all()
            
        except Exception as e:
            logger.error(
                "Failed to get message parts",
                message_id=message_id,
                error=str(e)
            )
            return []
    
    async def get_parts_by_type(
        self,
        message_id: int,
        part_type: MessagePartType
    ) -> List[MessagePart]:
        """Get message parts of a specific type."""
        
        try:
            result = await self.db.execute(
                select(MessagePart)
                .where(
                    and_(
                        MessagePart.message_id == message_id,
                        MessagePart.type == part_type
                    )
                )
                .order_by(MessagePart.order_index)
            )
            
            return result.scalars().all()
            
        except Exception as e:
            logger.error(
                "Failed to get parts by type",
                message_id=message_id,
                part_type=part_type,
                error=str(e)
            )
            return []
    
    async def update_part(
        self,
        part_id: int,
        content: Optional[str] = None,
        tool_output: Optional[Dict[str, Any]] = None
    ) -> Optional[MessagePart]:
        """Update a message part."""
        
        try:
            part = await self.db.get(MessagePart, part_id)
            if not part:
                return None
            
            if content is not None:
                part.content = content
            if tool_output is not None:
                part.tool_output = tool_output
            
            await self.db.commit()
            await self.db.refresh(part)
            
            logger.info("Message part updated", part_id=part_id)
            return part
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to update message part", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="MESSAGE_PART_UPDATE_ERROR",
                message="Failed to update message part"
            )
    
    async def delete_part(
        self,
        part_id: int
    ) -> bool:
        """Delete a message part."""
        
        try:
            part = await self.db.get(MessagePart, part_id)
            if not part:
                return False
            
            await self.db.delete(part)
            await self.db.commit()
            
            logger.info("Message part deleted", part_id=part_id)
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to delete message part", error=str(e))
            return False
    
    async def commit_parts(self):
        """Commit all pending message parts."""
        
        try:
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to commit message parts", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="MESSAGE_PARTS_COMMIT_ERROR",
                message="Failed to save message parts"
            )
