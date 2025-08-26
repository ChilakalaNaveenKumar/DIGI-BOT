"""
Anthropic Stream Router

Replaces existing stream routers with Anthropic-based streaming.
Integrates vector search from OpenAI (files).
Supports thinking mode toggle and web search.
"""

import json
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import structlog

from app.services.ai_providers.anthropic_provider import AnthropicProvider

from app.services.component_matcher import VectorStoreManager

from app.models.user import User
from app.models.conversation import Conversation, Message, MessageRole, ConversationStatus
from app.core.database import get_db_session
from app.core.config import get_settings
from app.services.auth.core.auth_deps import get_current_user_required
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/stream", tags=["Stream"])


def count_tokens_in_messages(messages: List[dict]) -> int:
    """Count tokens in message list (rough estimation)."""
    total = 0
    for msg in messages:
        content = msg.get('content', '')
        if content:
            # Rough estimation: 1 token ≈ 0.75 words
            total += len(content.split()) * 1.33
    return int(total)


def trim_messages_to_token_limit(messages: List[dict], limit: int = 150000) -> List[dict]:
    """Keep system message + recent messages under token limit."""
    if not messages:
        return messages
    
    # Separate system messages from user/assistant messages
    system_msgs = [msg for msg in messages if msg.get('role') == 'system']
    user_assistant_msgs = [msg for msg in messages if msg.get('role') in ['user', 'assistant']]
    
    # Start from most recent and work backwards
    trimmed_msgs = []
    current_tokens = count_tokens_in_messages(system_msgs)
    
    # Add messages from most recent backwards until we hit the limit
    for msg in reversed(user_assistant_msgs):
        msg_tokens = count_tokens_in_messages([msg])
        if current_tokens + msg_tokens > limit:
            break
        trimmed_msgs.insert(0, msg)
        current_tokens += msg_tokens
    
    # Return system messages + trimmed history
    return system_msgs + trimmed_msgs


async def create_conversation_for_user(
    db: AsyncSession,
    user_id: int,
    first_message: str
) -> Conversation:
    """Create a new conversation with auto-generated title."""
    try:
        # Generate title from first message (first 50 chars, cleaned up)
        title = first_message[:50].strip()
        if len(title) < 5:
            title = "New Conversation"
        elif len(first_message) > 50:
            title += "..."
        
        # Remove newlines and extra spaces
        title = " ".join(title.split())
        
        conversation = Conversation(
            title=title,
            user_id=user_id,
            status=ConversationStatus.ACTIVE,
            message_count=0
        )
        
        db.add(conversation)
        await db.flush()  # Get the ID
        await db.commit()
        await db.refresh(conversation)
        
        logger.info("Auto-created conversation", conversation_id=conversation.id, title=title, user_id=user_id)
        return conversation
        
    except Exception as e:
        logger.error("Failed to create conversation", error=str(e), user_id=user_id)
        await db.rollback()
        raise


async def save_message_to_db(
    db: AsyncSession,
    conversation_id: int,
    role: str,
    content: str,
    ai_provider: Optional[str] = None,
    ai_model: Optional[str] = None,
    token_count: Optional[int] = None,
    processing_time: Optional[float] = None,
    reasoning_steps: Optional[List[dict]] = None
) -> Message:
    """Save a message to the database."""
    try:
        message = Message(
            conversation_id=conversation_id,
            role=MessageRole(role),
            content=content,
            ai_provider=ai_provider,
            ai_model=ai_model,
            token_count=token_count,
            processing_time=processing_time,
            reasoning_steps={"steps": reasoning_steps} if reasoning_steps else None
        )
        
        db.add(message)
        await db.flush()  # Get the ID without committing
        
        # Update conversation's last_message_at and message_count
        conv_query = select(Conversation).where(Conversation.id == conversation_id)
        conv_result = await db.execute(conv_query)
        conversation = conv_result.scalar_one_or_none()
        
        if conversation:
            conversation.last_message_at = datetime.now(timezone.utc)
            conversation.message_count = conversation.message_count + 1
        
        await db.commit()
        await db.refresh(message)
        
        return message
        
    except Exception as e:
        logger.error("Failed to save message to database", error=str(e))
        await db.rollback()
        raise


class StreamRequest(BaseModel):
    """Request model for streaming with vector context."""
    messages: List[dict]  # Now includes conversation history
    conversation_id: Optional[int] = None  # NEW: For saving messages
    files: Optional[List[dict]] = None
    user_id: Optional[int] = None
    # Vector context
    file_ids: Optional[List[int]] = None
    # AI settings
    model: Optional[str] = "claude-sonnet-4-20250514"
    enable_thinking: bool = False
    thinking_budget: int = 5000
    enable_web_search: bool = True
    temperature: float = 0.7
    # Tool enablement flags (legacy compatibility)
    has_audio: bool = False
    has_image: bool = False
    enable_audio_generation: bool = False


class ContextProcessor:
    """Processes vector context from file vectors."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_store_manager = VectorStoreManager()
        self._initialized = False
    
    async def initialize(self):
        """Initialize vector services."""
        if self._initialized:
            return
        
        await self.vector_store_manager.initialize()
        self._initialized = True
        logger.info("Context processor initialized")
    

    
    async def get_file_context(
        self,
        query: str,
        file_ids: Optional[List[int]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get relevant file context from OpenAI vectors."""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Search file vectors by query
            file_results = await self.vector_store_manager.query(query, top_k=limit)
            
            # Filter by specific file IDs if provided
            if file_ids:
                filtered_results = []
                for result in file_results:
                    meta = result.get("meta", {})
                    if meta.get("file_id") in file_ids:
                        filtered_results.append(result)
                file_results = filtered_results
            
            return file_results
            
        except Exception as e:
            logger.error("Failed to get file context", error=str(e))
            return []
    
    async def build_context_message(
        self,
        query: str,
        file_ids: Optional[List[int]] = None
    ) -> str:
        """Build context message from file vectors."""
        
        # Get file context
        file_context = await self.get_file_context(
            query=query,
            file_ids=file_ids
        )
        
        # Build context message
        context_parts = []
        
        if file_context:
            context_parts.append("## Relevant File Content:")
            for i, ctx in enumerate(file_context[:5], 1):  # Limit to 5 most relevant
                text = ctx.get("text", "")
                meta = ctx.get("meta", {})
                filename = meta.get("filename", "Unknown file")
                context_parts.append(f"**File {i} ({filename}):**")
                context_parts.append(text[:300] + "..." if len(text) > 300 else text)
                context_parts.append("")
        
        if not context_parts:
            return ""
        
        context_parts.insert(0, "# Context Information")
        context_parts.insert(1, "The following context may be relevant to your response:")
        context_parts.insert(2, "")
        
        return "\n".join(context_parts)





@router.post("", response_class=StreamingResponse)
async def stream_endpoint(
    request: StreamRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: Dict[str, Any] = Depends(get_current_user_required),
    settings = Depends(get_settings)
):
    """
    Anthropic streaming endpoint with vector context integration.
    
    Features:
    - Vector search from OpenAI (files)
    - Thinking mode toggle
    - Web search with max 5 tries
    - Thinking block format output
    """
    
    async def generate_response():
        """Generate response using Anthropic with vector context."""
        try:
            # Validate request
            if not request.messages:
                yield f"data: {json.dumps({'type': 'error', 'content': 'No messages provided'})}\n\n"
                return
            
            # Extract user message
            last_message = request.messages[-1]
            user_message = last_message.get('content', '')
            
            if not user_message:
                yield f"data: {json.dumps({'type': 'error', 'content': 'No user message found'})}\n\n"
                return
            
            user_id = current_user.get("id", 1)
            
            # NEW: Token counting and limiting
            total_tokens = count_tokens_in_messages(request.messages)
            logger.info(
                "Processing Anthropic stream request",
                user_id=user_id,
                model=request.model,
                thinking_enabled=request.enable_thinking,
                web_search_enabled=request.enable_web_search,
                message_preview=user_message[:100],
                total_tokens=total_tokens,
                conversation_id=request.conversation_id
            )
            
            # NEW: Apply token limit (150k tokens)
            if total_tokens > 150000:
                logger.info("Token limit exceeded, trimming messages", total_tokens=total_tokens)
                request.messages = trim_messages_to_token_limit(request.messages, 150000)
                total_tokens = count_tokens_in_messages(request.messages)
                logger.info("Messages trimmed", new_total_tokens=total_tokens)
            
            # NOTE: No auto-saving here - frontend will handle conversation saving
            
            provider = AnthropicProvider()
            await provider.initialize()
            
            # Build system message (NO vector context)
            system_content = """You are Digi Setu AI, an advanced AI assistant with comprehensive capabilities.

**Important Guidelines:**
- Provide well-formatted, helpful responses using markdown when it improves readability
- Be conversational and helpful while maintaining accuracy
- Focus on providing clear, informative responses to user questions"""
            
            system_message = {"role": "system", "content": system_content}
            final_messages = [system_message] + request.messages
            
            # Start streaming with thinking blocks
            if request.enable_thinking:
                yield f"data: {json.dumps({'type': 'thinking_start'})}\n\n"
            
            # NEW: Collect assistant response and reasoning steps for database saving
            assistant_response_parts = []
            reasoning_steps = []
            current_step = None
            start_time = datetime.now(timezone.utc)
            
            async for chunk in provider.stream_completion(
                messages=final_messages,
                model=request.model,
                temperature=request.temperature,
                enable_thinking=request.enable_thinking,
                thinking_budget=request.thinking_budget,
                enable_web_search=request.enable_web_search
            ):
                chunk_type = chunk.get("type")
                
                # Handle different content block types
                if chunk_type == "content_block_start":
                    content_block = chunk.get("content_block", {})
                    block_type = content_block.get("type")
                    
                    if block_type == "thinking":
                        # Start a new thinking step
                        current_step = {
                            "id": f"thinking-{len(reasoning_steps)}",
                            "type": "thinking",
                            "content": "",
                            "status": "active",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        }
                    
                    elif block_type == "server_tool_use":
                        # Start a new tool call step
                        tool_name = content_block.get("name", "unknown_tool")
                        current_step = {
                            "id": f"tool-{content_block.get('id', len(reasoning_steps))}",
                            "type": "tool_call",
                            "content": f"Using {tool_name}...",
                            "tool_name": tool_name,
                            "status": "active",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "inputJson": ""
                        }
                
                elif chunk_type == "content_block_delta":
                    delta = chunk.get("delta", {})
                    delta_type = delta.get("type")
                    
                    if delta_type == "text_delta":
                        text = delta.get("text", "")
                        
                        # Check if this is for current step (thinking content)
                        if current_step and current_step["type"] == "thinking" and current_step["status"] == "active":
                            current_step["content"] += text
                        else:
                            # Regular assistant response
                            assistant_response_parts.append(text)
                    
                    elif delta_type == "input_json_delta":
                        # Tool input streaming
                        if current_step and current_step["type"] == "tool_call" and current_step["status"] == "active":
                            current_step["inputJson"] += delta.get("partial_json", "")
                            
                            # Update content for web search with query
                            if current_step["tool_name"] == "web_search":
                                try:
                                    parsed = json.loads(current_step["inputJson"])
                                    if parsed.get("query"):
                                        current_step["content"] = f"Searching: {parsed['query']}"
                                except json.JSONDecodeError:
                                    pass  # Still parsing, ignore errors
                
                elif chunk_type == "content_block_stop":
                    # Complete the current step
                    if current_step and current_step["status"] == "active":
                        current_step["status"] = "completed"
                        reasoning_steps.append(current_step)
                        current_step = None
                
                # Handle tool results
                elif chunk_type == "content_block_start" and chunk.get("content_block", {}).get("type") == "web_search_tool_result":
                    content_block = chunk.get("content_block", {})
                    tool_use_id = content_block.get("tool_use_id")
                    
                    # Find the corresponding tool step and add result
                    for step in reasoning_steps:
                        if step.get("id") == f"tool-{tool_use_id}":
                            step["result"] = content_block.get("content", [])
                            step["status"] = "completed"
                            break
                
                # Pass through raw Anthropic data
                yield f"data: {json.dumps(chunk)}\n\n"
                
                if chunk.get("type") == "message_stop":
                    break
            
            # NOTE: No auto-saving here - frontend will handle conversation saving after component processing
            
            # Send completion
            yield f"data: {json.dumps({'type': 'completion', 'finish_reason': 'stop'})}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            # Log detailed error information
            error_details = {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'model': request.model,
                'user_id': current_user.get("id", "unknown"),
                'conversation_id': request.conversation_id
            }
            
            # Add HTTP response details if available
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details['status_code'] = getattr(e.response, 'status_code', 'unknown')
                    error_details['response_headers'] = dict(getattr(e.response, 'headers', {}))
                    if hasattr(e.response, 'text'):
                        error_details['response_body'] = e.response.text
                except:
                    pass
            
            logger.error("Anthropic stream endpoint error", **error_details)
            yield f"data: {json.dumps({'type': 'error', 'content': f'Stream Error: {str(e)}', 'details': error_details})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


@router.get("/health")
async def health_check():
    """Health check endpoint for Anthropic stream service."""
    try:
        provider = AnthropicProvider()
        await provider.initialize()
        
        is_healthy = await provider.health_check()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "anthropic-stream",
            "models": provider.get_available_models(),
            "default_model": provider.default_model
        }
        
    except Exception as e:
        logger.error("Anthropic stream health check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


# Export the router
__all__ = ["router"]
