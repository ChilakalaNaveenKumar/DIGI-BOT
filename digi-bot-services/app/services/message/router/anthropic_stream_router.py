"""
Anthropic Stream Router

Replaces existing stream routers with Anthropic-based streaming.
Integrates vector search from both PostgreSQL (conversations) and OpenAI (files).
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
from app.services.vector.vector_service import VectorService
from app.services.component_matcher import VectorStoreManager
from app.services.conversation import ConversationService, ConversationManager
from app.models.user import User
from app.core.database import get_db_session
from app.core.config import get_settings
from app.services.auth.core.auth_deps import get_current_user_required
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/stream", tags=["Stream"])


class StreamRequest(BaseModel):
    """Request model for streaming with vector context."""
    messages: List[dict]
    conversation_id: Optional[int] = None
    files: Optional[List[dict]] = None
    user_id: Optional[int] = None
    # Vector context
    file_ids: Optional[List[int]] = None
    message_vector_ids: Optional[List[str]] = None
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
    """Processes vector context from both conversation and file vectors."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_service = VectorService(db)
        self.vector_store_manager = VectorStoreManager()
        self._initialized = False
    
    async def initialize(self):
        """Initialize vector services."""
        if self._initialized:
            return
        
        await self.vector_service.initialize()
        await self.vector_store_manager.initialize()
        self._initialized = True
        logger.info("Context processor initialized")
    
    async def get_conversation_context(
        self,
        query: str,
        user_id: int,
        conversation_id: Optional[int] = None,
        message_vector_ids: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get relevant conversation context from PostgreSQL vectors."""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Search conversation vectors by query
            conversation_results = await self.vector_service.search_similar_messages(
                query=query,
                user_id=user_id,
                conversation_id=conversation_id,
                limit=limit
            )
            
            # Note: message_vector_ids functionality would need additional method in VectorService
            # For now, we'll just use the search results
            
            return conversation_results
            
        except Exception as e:
            logger.error("Failed to get conversation context", error=str(e))
            return []
    
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
        user_id: int,
        conversation_id: Optional[int] = None,
        file_ids: Optional[List[int]] = None,
        message_vector_ids: Optional[List[str]] = None
    ) -> str:
        """Build comprehensive context message from both vector sources."""
        
        # Get conversation context
        conversation_context = await self.get_conversation_context(
            query=query,
            user_id=user_id,
            conversation_id=conversation_id,
            message_vector_ids=message_vector_ids
        )
        
        # Get file context
        file_context = await self.get_file_context(
            query=query,
            file_ids=file_ids
        )
        
        # Build context message
        context_parts = []
        
        if conversation_context:
            context_parts.append("## Previous Conversation Context:")
            for i, ctx in enumerate(conversation_context[:5], 1):  # Limit to 5 most relevant
                snippet = ctx.get("snippet", "")
                content_summary = ctx.get("content_summary", "")
                context_parts.append(f"**Context {i}:**")
                if snippet:
                    context_parts.append(f"Snippet: {snippet[:200]}...")
                if content_summary:
                    context_parts.append(f"Summary: {content_summary[:200]}...")
                context_parts.append("")
        
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


async def generate_conversation_title(user_message: str, provider: AnthropicProvider) -> str:
    """Generate a conversation title using Anthropic."""
    try:
        title_prompt = f"""Generate a short, descriptive title (4-6 words) for a conversation that starts with this message:

"{user_message}"

Return only the title, nothing else."""

        response = await provider.generate_completion(
            messages=[{"role": "user", "content": title_prompt}],
            max_tokens=20
        )
        
        # Extract title from response
        title = ""
        for block in response.get("content", []):
            if block.get("type") == "text":
                title += block.get("text", "")
        
        # Clean title
        title = title.strip().replace('"', '').replace('\n', ' ')
        words = title.split()
        
        if len(words) > 6:
            title = ' '.join(words[:6])
        elif len(words) < 2:
            title = "New Conversation"
        
        return title or "New Conversation"
        
    except Exception as e:
        logger.error("Failed to generate conversation title", error=str(e))
        return "New Conversation"


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
    - Vector search from PostgreSQL (conversations) and OpenAI (files)
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
            logger.info(
                "Processing Anthropic stream request",
                user_id=user_id,
                model=request.model,
                thinking_enabled=request.enable_thinking,
                web_search_enabled=request.enable_web_search,
                message_preview=user_message[:100]
            )
            
            provider = AnthropicProvider()
            await provider.initialize()
            
            context_processor = ContextProcessor(db)
            await context_processor.initialize()
            
            # Check if this is the first message
            is_first_message = not request.conversation_id
            conversation_id = request.conversation_id
            conversation_title = None
            
            # Generate title for first message
            if is_first_message:
                conversation_title = await generate_conversation_title(user_message, provider)
                logger.info("Generated conversation title", title=conversation_title)
            
            
            context_message = await context_processor.build_context_message(
                query=user_message,
                user_id=user_id,
                conversation_id=conversation_id,
                file_ids=request.file_ids,
                message_vector_ids=request.message_vector_ids
            )
            
            # Prepare conversation context
            conv_manager = ConversationManager(db)
            prepared_messages, conversation_summary = await conv_manager.prepare_conversation_context(
                conversation_id=conversation_id,
                new_user_message=user_message,
                existing_summary=None
            )
            
            # Build system message with context
            system_content = """You are Digi Setu AI, an advanced AI assistant with comprehensive capabilities.

**Important Guidelines:**
- Provide well-formatted, helpful responses using markdown when it improves readability
- Use the provided context information to give more accurate and relevant responses
- If context is provided, reference it naturally in your response
- Be conversational and helpful while maintaining accuracy"""
            
            if context_message:
                system_content += f"\n\n{context_message}"
            
            system_message = {"role": "system", "content": system_content}
            final_messages = [system_message] + prepared_messages
            
            # Start streaming with thinking blocks
            if request.enable_thinking:
                yield f"data: {json.dumps({'type': 'thinking_start'})}\n\n"
            
            assistant_content = ""
            
            async for chunk in provider.stream_completion(
                messages=final_messages,
                model=request.model,
                temperature=request.temperature,
                enable_thinking=request.enable_thinking,
                thinking_budget=request.thinking_budget,
                enable_web_search=request.enable_web_search
            ):
                # Just pass through raw Anthropic data
                yield f"data: {json.dumps(chunk)}\n\n"
                
                # Extract text content for saving conversation
                if chunk.get("type") == "content_block_delta":
                    delta = chunk.get("delta", {})
                    if delta.get("type") == "text_delta":
                        assistant_content += delta.get("text", "")
                elif chunk.get("type") == "message_stop":
                    break
            
            # TODO: Re-enable conversation saving after fixing database issues
            # if is_first_message and conversation_title:
            #     # Create new conversation
            #     conv_service = ConversationService(db)
            #     conversation = await conv_service.create_conversation(
            #         user_id=user_id,
            #         title=conversation_title
            #     )
            #     conversation_id = conversation.id
            #     
            #     # Save conversation turn
            #     await conv_manager.save_conversation_turn(
            #         conversation_id=conversation_id,
            #         user_message=user_message,
            #         assistant_response=assistant_content,
            #         user_id=user_id,
            #         tool_calls_used=1 if request.enable_web_search else 0,
            #         summary=conversation_summary
            #     )
            #     
            #     yield f"data: {json.dumps({'type': 'metadata', 'conversation_id': conversation_id, 'title': conversation_title})}\n\n"
            #     
            # elif conversation_id:
            #     # Update existing conversation
            #     await conv_manager.save_conversation_turn(
            #         conversation_id=conversation_id,
            #         user_message=user_message,
            #         assistant_response=assistant_content,
            #         user_id=user_id,
            #         tool_calls_used=1 if request.enable_web_search else 0,
            #         summary=conversation_summary
            #     )
            #     
            #     yield f"data: {json.dumps({'type': 'metadata', 'conversation_id': conversation_id})}\n\n"
            
            # Send completion
            yield f"data: {json.dumps({'type': 'completion', 'finish_reason': 'stop'})}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error("Anthropic stream endpoint error", error=str(e))
            yield f"data: {json.dumps({'type': 'error', 'content': f'Stream Error: {str(e)}'})}\n\n"
    
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
