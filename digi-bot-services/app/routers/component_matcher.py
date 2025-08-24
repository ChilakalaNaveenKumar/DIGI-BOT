"""
Component Matcher API Router
Provides streaming component matching with thinking block format and authentication
"""

from __future__ import annotations
import json
from typing import Dict, Any, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import structlog

from app.services.auth.core.auth_deps import get_current_user_required
from app.services.component_matcher import ComponentMatcherClient, VectorStoreManager

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/component-matcher", tags=["component-matcher"])


class ComponentMatcherRequest(BaseModel):
    query: str


class ComponentMatcherRouter:
    """Router for component matcher with thinking block streaming"""
    
    def __init__(self):
        self.component_matcher = ComponentMatcherClient()
        self.vector_manager = None
    
    async def initialize(self):
        """Initialize component matcher and vector manager"""
        try:
            await self.component_matcher.initialize()
            self.vector_manager = VectorStoreManager()
            await self.vector_manager.initialize()
            logger.info("Component matcher router initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize component matcher router", error=str(e))
            raise


# Global router instance
component_router = ComponentMatcherRouter()


async def convert_to_thinking_blocks(
    query: str, 
    component_matcher: ComponentMatcherClient,
    vector_manager: VectorStoreManager
) -> AsyncGenerator[str, None]:
    """
    Convert OpenAI streaming response to thinking block format
    Only yields data if matches are found
    """
    
    # First check if there are any matches using quick_match
    quick_result = await component_matcher.quick_match(query, vector_manager)
    
    # If no match found, return empty stream
    if not component_matcher.has_match(quick_result):
        logger.info("No component matches found", query=query)
        return
    
    # Start thinking block
    yield f"data: {json.dumps({'type': 'thinking_start'})}\n\n"
    
    # Add initial thinking
    yield f"data: {json.dumps({'type': 'thinking_delta', 'text': 'Analyzing query for component matches...'})}\n\n"
    
    # Stream the actual analysis with thinking deltas
    full_content = ""
    thinking_content = []
    
    async for event in component_matcher.analyze(query, vector_manager):
        if event["type"] == "content":
            content_chunk = event["content"]
            full_content += content_chunk
            
            # Convert content to thinking delta
            thinking_content.append(content_chunk)
            yield f"data: {json.dumps({'type': 'thinking_delta', 'text': content_chunk})}\n\n"
            
        elif event["type"] == "error":
            # End thinking and return error
            yield f"data: {json.dumps({'type': 'thinking_stop'})}\n\n"
            yield f"data: {json.dumps({'type': 'error', 'error': event['error']})}\n\n"
            return
            
        elif event["type"] == "completion":
            # End thinking block
            yield f"data: {json.dumps({'type': 'thinking_stop'})}\n\n"
            
            # Return final content if it's a valid match
            if component_matcher.has_match(full_content):
                yield f"data: {json.dumps({'type': 'content', 'content': full_content.strip()})}\n\n"
            
            # Send completion
            yield f"data: {json.dumps({'type': 'completion', 'finish_reason': 'done'})}\n\n"
            return


@router.post("/analyze")
async def analyze_component_match(
    request: ComponentMatcherRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required),
    http_request: Request = None
):
    """
    Analyze query for component matches with thinking block streaming
    
    Returns streaming response in thinking block format:
    - thinking_start: Begin analysis
    - thinking_delta: Analysis progress 
    - thinking_stop: End analysis
    - content: Matched component format (only if match found)
    - completion: End of stream
    
    If no matches found, returns empty stream.
    """
    
    try:
        # Initialize if needed
        if not component_router.component_matcher._initialized:
            await component_router.initialize()
        
        # Log the request
        logger.info(
            "Component matcher request", 
            user_id=current_user["id"],
            query=request.query[:100] + "..." if len(request.query) > 100 else request.query
        )
        
        # Create streaming response
        return StreamingResponse(
            convert_to_thinking_blocks(
                request.query,
                component_router.component_matcher,
                component_router.vector_manager
            ),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        logger.error(
            "Component matcher error",
            user_id=current_user["id"],
            query=request.query,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Component matching failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for component matcher service"""
    try:
        if not component_router.component_matcher._initialized:
            await component_router.initialize()
        
        return {
            "status": "healthy",
            "service": "component-matcher",
            "initialized": component_router.component_matcher._initialized
        }
    except Exception as e:
        logger.error("Component matcher health check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


# Export the router
__all__ = ["router"]
