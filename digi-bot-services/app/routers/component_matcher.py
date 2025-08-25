"""
Component Matcher API Router
Provides streaming component matching using OpenAI Assistant Client with direct API calls
"""

from __future__ import annotations
import json
from typing import Dict, Any, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import structlog

from app.services.auth.core.auth_deps import get_current_user_required
from app.services.component_matcher.openai_assistant_client import OpenAIAssistantClient

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/component-matcher", tags=["component-matcher"])


class ComponentMatcherRequest(BaseModel):
    query: str


class ComponentMatcherRouter:
    """Router for component matcher using OpenAI Assistant Client with direct API calls"""
    
    def __init__(self):
        # Initialize OpenAI Assistant Client - no complex vector management needed
        self.component_matcher = OpenAIAssistantClient()
        self._initialized = False
    
    async def initialize(self):
        """Initialize component matcher - simple setup without connection test"""
        try:
            # Just mark as initialized - no need for connection test
            self._initialized = True
            logger.info("Component matcher router initialized successfully", 
                       prompt_id=self.component_matcher.prompt_id,
                       vector_store_id=self.component_matcher.vector_store_id)
        except Exception as e:
            logger.error("Failed to initialize component matcher router", error=str(e))
            raise


# Global router instance
component_router = ComponentMatcherRouter()


async def convert_to_thinking_blocks(
    query: str, 
    component_matcher: OpenAIAssistantClient
) -> AsyncGenerator[str, None]:
    """
    Convert OpenAI Assistant streaming response to thinking block format
    Streams JSON responses directly from OpenAI Assistant API
    """
    
    # Start thinking block
    yield f"data: {json.dumps({'type': 'thinking_start'})}\n\n"
    
    # Add initial thinking
    yield f"data: {json.dumps({'type': 'thinking_delta', 'text': 'Analyzing query for component matches using OpenAI Assistant...'})}\n\n"
    
    # Stream the actual analysis using OpenAI Assistant Client
    full_content = ""
    
    try:
        async for event in component_matcher.query_components_streaming(query):
            if event["type"] == "delta":
                # Convert delta to thinking delta
                yield f"data: {json.dumps({'type': 'thinking_delta', 'text': event['delta']})}\n\n"
                full_content += event["delta"]
                
            elif event["type"] == "error":
                # End thinking and return error
                yield f"data: {json.dumps({'type': 'thinking_stop'})}\n\n"
                yield f"data: {json.dumps({'type': 'error', 'error': event['error']})}\n\n"
                return
                
            elif event["type"] == "completed":
                # End thinking block
                yield f"data: {json.dumps({'type': 'thinking_stop'})}\n\n"
                
                # Return the structured data as JSON
                if event.get("data"):
                    yield f"data: {json.dumps({'type': 'content', 'content': event['raw_content']})}\n\n"
                
                # Send completion with usage info
                completion_data = {
                    'type': 'completion', 
                    'finish_reason': 'done'
                }
                if event.get("usage"):
                    completion_data["usage"] = {
                        "total_tokens": getattr(event["usage"], 'total_tokens', None),
                        "input_tokens": getattr(event["usage"], 'prompt_tokens', None),
                        "output_tokens": getattr(event["usage"], 'completion_tokens', None)
                    }
                
                yield f"data: {json.dumps(completion_data)}\n\n"
                return
                
    except Exception as e:
        # Handle any streaming errors
        yield f"data: {json.dumps({'type': 'thinking_stop'})}\n\n"
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"


@router.post("/analyze")
async def analyze_component_match(
    request: ComponentMatcherRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required),
    http_request: Request = None
):
    """
    Analyze query for component matches with thinking block streaming
    
    Uses OpenAI Assistant Client for direct API calls without local vector stores.
    
    Returns streaming response in thinking block format:
    - thinking_start: Begin analysis
    - thinking_delta: Analysis progress 
    - thinking_stop: End analysis
    - content: Matched component format as JSON
    - completion: End of stream with usage info
    """
    
    try:
        # Initialize if needed
        if not component_router._initialized:
            await component_router.initialize()
        
        # Log the request
        logger.info(
            "OpenAI Assistant component matcher request", 
            user_id=current_user["id"],
            prompt_id=component_router.component_matcher.prompt_id,
            vector_store_id=component_router.component_matcher.vector_store_id,
            query=request.query[:100] + "..." if len(request.query) > 100 else request.query
        )
        
        # Create streaming response using OpenAI Assistant Client
        return StreamingResponse(
            convert_to_thinking_blocks(
                request.query,
                component_router.component_matcher
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


@router.post("/analyze-simple")
async def analyze_component_match_simple(
    request: ComponentMatcherRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Simple non-streaming component matcher endpoint using OpenAI Assistant Client
    Returns JSON response with component matches or empty result
    """
    
    try:
        # Initialize if needed
        if not component_router._initialized:
            await component_router.initialize()
        
        # Log the request
        logger.info(
            "Simple OpenAI Assistant component matcher request", 
            user_id=current_user["id"],
            prompt_id=component_router.component_matcher.prompt_id,
            query=request.query[:100] + "..." if len(request.query) > 100 else request.query
        )
        
        # Get result using OpenAI Assistant Client
        result = await component_router.component_matcher.query_components(request.query)
        
        logger.info("Component matcher result", 
                   success=result["success"],
                   has_data=bool(result.get("data")))
        
        # Check if there's a successful match
        if result["success"] and result.get("data"):
            # Return the structured response
            response_data = {
                "success": True,
                "has_matches": True,
                "data": result["data"],
                "raw_content": result.get("raw_content", ""),
                "response_id": result.get("response_id")
            }
            
            # Add usage info if available
            if result.get("usage"):
                response_data["usage"] = {
                    "total_tokens": getattr(result["usage"], 'total_tokens', None),
                    "input_tokens": getattr(result["usage"], 'prompt_tokens', None),
                    "output_tokens": getattr(result["usage"], 'completion_tokens', None)
                }
            
            return response_data
        else:
            return {
                "success": False,
                "has_matches": False,
                "message": result.get("error", "No component matches found"),
                "data": None
            }
        
    except Exception as e:
        logger.error(
            "Simple component matcher error",
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
    """Health check endpoint for component matcher service using OpenAI Assistant Client"""
    try:
        if not component_router._initialized:
            await component_router.initialize()
        
        return {
            "status": "healthy",
            "service": "component-matcher",
            "client_type": "OpenAI Assistant Client",
            "initialized": component_router._initialized,
            "prompt_id": component_router.component_matcher.prompt_id,
            "vector_store_id": component_router.component_matcher.vector_store_id
        }
    except Exception as e:
        logger.error("Component matcher health check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


# Export the router
__all__ = ["router"]
