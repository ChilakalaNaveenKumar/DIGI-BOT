"""
Efficient Conversation Manager

Handles conversation context, token management, and summarization.
Implements best practices for Claude API conversation management.
Includes vector database integration for semantic search and memory.
"""

import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.message import MessageService
from app.services.vector import get_vector_service
from ..service.conversation_service import ConversationService
from app.models.conversation import MessageRole

logger = structlog.get_logger(__name__)


class ConversationManager:
    """Manages conversation context and token efficiency."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.MAX_CONTEXT_TOKENS = 60000  # Conservative limit for Claude
        self.KEEP_RECENT_RATIO = 0.3  # Keep 30% of tokens for recent context
        self.msg_service = MessageService(db)
        self.conv_service = ConversationService(db)
        
    def estimate_tokens(self, messages: List[Dict]) -> int:
        """
        Estimate token count for messages.
        Uses rough estimation: 4 characters ≈ 1 token
        """
        try:
            text = json.dumps(messages)
            estimated_tokens = len(text) // 4
            logger.debug(f"Estimated tokens: {estimated_tokens}")
            return estimated_tokens
        except Exception as e:
            logger.error("Error estimating tokens", error=str(e))
            return 0
    
    async def summarize_old_context(self, old_messages: List[Dict]) -> str:
        """
        Summarize older conversation context using Claude Haiku (cheaper).
        """
        try:
            context_text = "\n".join([
                f"{msg['role']}: {self._extract_text_content(msg['content'])}" 
                for msg in old_messages
            ])
            
            # Use cheaper model for summarization
            provider = AnthropicProvider()
            await provider.initialize()
            
            response = await provider.generate_completion(
                messages=[{
                    "role": "user", 
                    "content": f"Summarize this conversation concisely, keeping key context and important details:\n\n{context_text}"
                }]
            )
            
            summary = ""
            content_blocks = response.get('content', [])
            for block in content_blocks:
                if block.get('type') == 'text':
                    summary += block.get('text', '')
            
            logger.info(f"Generated summary: {len(summary)} characters")
            return summary.strip()
            
        except Exception as e:
            logger.error("Error generating summary", error=str(e))
            return "Previous conversation context available but could not be summarized."
    
    def _extract_text_content(self, content) -> str:
        """Extract text from various content types."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                    elif item.get('type') == 'tool_use':
                        text_parts.append(f"[Used tool: {item.get('name', 'unknown')}]")
                elif isinstance(item, str):
                    text_parts.append(item)
            return ' '.join(text_parts)
        return str(content)
    
    async def prepare_conversation_context(
        self, 
        conversation_id: Optional[int], 
        new_user_message: str,
        existing_summary: Optional[str] = None
    ) -> Tuple[List[Dict], Optional[str]]:
        """
        MAIN TRIGGER POINT: Called when user sends new message.
        Prepares efficient conversation context with summarization if needed.
        
        Returns: (prepared_messages, new_summary_if_created)
        """
        try:
            # For new conversations
            if not conversation_id:
                messages = [{"role": "user", "content": new_user_message}]
                logger.info("New conversation - no context needed")
                return messages, None
            
            # Load conversation history from database
            conversation_history = await self.msg_service.get_conversation_history(
                conversation_id=conversation_id,
                max_messages=100  # Load more for analysis
            )
            
            # Add new user message
            conversation_history.append({"role": "user", "content": new_user_message})
            
            current_tokens = self.estimate_tokens(conversation_history)
            logger.info(f"Current context: {current_tokens} tokens for conversation {conversation_id}")
            
            new_summary = existing_summary
            
            # TRIGGER: When approaching token limit
            if current_tokens > self.MAX_CONTEXT_TOKENS:
                logger.info("🔄 Triggering conversation summarization...")
                
                # Calculate how many recent messages to keep
                keep_tokens = int(self.MAX_CONTEXT_TOKENS * self.KEEP_RECENT_RATIO)
                recent_messages = []
                token_count = 0
                
                # Work backwards to keep recent context
                for msg in reversed(conversation_history):
                    msg_tokens = self.estimate_tokens([msg])
                    if token_count + msg_tokens <= keep_tokens:
                        recent_messages.insert(0, msg)
                        token_count += msg_tokens
                    else:
                        break
                
                # Summarize the older context
                older_messages = conversation_history[:-len(recent_messages)]
                if older_messages:
                    old_summary = await self.summarize_old_context(older_messages)
                    
                    # Combine with existing summary
                    if existing_summary:
                        new_summary = f"{existing_summary}\n\nRecent context: {old_summary}"
                    else:
                        new_summary = old_summary
                
                # Create new context with summary + recent messages
                prepared_messages = []
                if new_summary:
                    prepared_messages.append({
                        "role": "user",
                        "content": f"[Previous conversation summary: {new_summary}]"
                    })
                prepared_messages.extend(recent_messages)
                
                final_tokens = self.estimate_tokens(prepared_messages)
                logger.info(f"✅ Context optimized: {current_tokens} → {final_tokens} tokens")
                
                # Update conversation summary in database
                if new_summary != existing_summary:
                    await self.conv_service.update_conversation(
                        conversation_id=conversation_id,
                        user_id=1,  # TODO: Get from auth
                        title=None  # Don't change title
                    )
                
            else:
                prepared_messages = conversation_history
                logger.info(f"Context within limits: {current_tokens} tokens")
            
            return prepared_messages, new_summary
            
        except Exception as e:
            logger.error("Error preparing conversation context", error=str(e))
            # Fallback: just use the new message
            return [{"role": "user", "content": new_user_message}], None
    
    async def save_conversation_turn(
        self,
        conversation_id: int,
        user_message: str,
        assistant_response: str,
        user_id: int = 1,  # TODO: Get from auth context
        tool_calls_used: int = 0,
        summary: Optional[str] = None
    ):
        """Save a complete conversation turn to database and create vector embedding."""
        try:
            # Save user message
            user_msg = await self.msg_service.create_message(
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content=user_message
            )
            
            # Save assistant response
            assistant_msg = await self.msg_service.create_message(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=assistant_response,
                ai_provider="anthropic",
                ai_model="claude-sonnet-4-20250514"
            )
            
            # Commit both messages
            await self.msg_service.commit_message(assistant_msg)
            
            # Get turn index (count of message pairs in conversation)
            turn_index = await self._get_conversation_turn_count(conversation_id)
            
            # Create vector embedding asynchronously (don't block the response)
            asyncio.create_task(self._create_message_vector(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message=user_message,
                assistant_response=assistant_response,
                turn_index=turn_index,
                user_message_id=user_msg.id,
                assistant_message_id=assistant_msg.id
            ))
            
            logger.info(
                "Conversation turn saved",
                conversation_id=conversation_id,
                turn_index=turn_index,
                tool_calls_used=tool_calls_used,
                vector_creation="scheduled"
            )
            
        except Exception as e:
            logger.error("Error saving conversation turn", error=str(e))
            raise
    
    async def _get_conversation_turn_count(self, conversation_id: int) -> int:
        """Get the current turn count for a conversation."""
        try:
            # Count user messages (each represents a turn)
            user_message_count = await self.msg_service.count_messages_by_role(
                conversation_id=conversation_id,
                role=MessageRole.USER
            )
            return user_message_count
        except Exception as e:
            logger.error("Error getting turn count", error=str(e))
            return 1  # Default to 1 if we can't count
    
    async def _create_message_vector(
        self,
        user_id: int,
        conversation_id: int,
        user_message: str,
        assistant_response: str,
        turn_index: int,
        user_message_id: Optional[int] = None,
        assistant_message_id: Optional[int] = None
    ):
        """Create vector embedding for message pair (async background task)."""
        try:
            vector_service = await get_vector_service(self.db)
            
            vector_id = await vector_service.save_message_vector(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message=user_message,
                assistant_response=assistant_response,
                turn_index=turn_index,
                user_message_id=user_message_id,
                assistant_message_id=assistant_message_id,
                expires_in_days=7  # 7-day expiry as planned
            )
            
            logger.info(
                "Message vector created",
                vector_id=vector_id,
                conversation_id=conversation_id,
                turn_index=turn_index
            )
            
        except Exception as e:
            # Don't fail the main conversation save if vector creation fails
            logger.error(
                "Failed to create message vector (non-blocking)",
                error=str(e),
                conversation_id=conversation_id,
                turn_index=turn_index
            )
