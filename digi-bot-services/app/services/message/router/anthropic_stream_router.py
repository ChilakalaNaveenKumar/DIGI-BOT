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
from app.core.database import get_db_session
from app.core.config import get_settings
from app.services.auth.core.auth_deps import get_current_user_required
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/stream", tags=["Stream"])


class StreamRequest(BaseModel):
    """Request model for streaming with vector context."""
    messages: List[dict]
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
                
                if chunk.get("type") == "message_stop":
                    break
            
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
