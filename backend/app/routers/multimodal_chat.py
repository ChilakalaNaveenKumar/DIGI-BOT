"""
Multimodal Chat Router

Enhanced chat endpoint that automatically uses multimodal capabilities.
"""

import logging
from typing import List, Optional

import structlog
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.multimodal_orchestrator import MultimodalOrchestrator, MultimodalRequest
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/multimodal", tags=["multimodal-chat"])


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str  # user, assistant, system
    content: str
    metadata: Optional[dict] = None


class MultimodalChatRequest(BaseModel):
    """Request for multimodal chat."""
    message: str
    conversation_history: Optional[List[ChatMessage]] = None
    files: Optional[List[dict]] = None
    preferences: Optional[dict] = None


class MultimodalChatResponse(BaseModel):
    """Response from multimodal chat."""
    message: str
    content_type: str
    metadata: dict
    tool_calls: List[dict] = []
    reasoning: Optional[str] = None


@router.post("/chat", response_model=MultimodalChatResponse)
async def multimodal_chat(request: MultimodalChatRequest):
    """
    Enhanced chat endpoint with automatic multimodal capabilities.
    
    This endpoint automatically detects when to use:
    - Vision analysis for image-related queries
    - Audio processing for audio-related requests
    - Tool execution for calculations, weather, code generation, etc.
    - Web search for information lookup
    
    Args:
        request: Chat request with message and optional files
    
    Returns:
        Enhanced response with appropriate multimodal content
    """
    try:
        logger.info(
            "Processing multimodal chat request",
            message_length=len(request.message),
            has_files=bool(request.files),
            has_history=bool(request.conversation_history)
        )
        
        # Create multimodal request
        multimodal_request = MultimodalRequest(
            user_message=request.message,
            context={
                "conversation_history": request.conversation_history or [],
                "preferences": request.preferences or {}
            },
            files=request.files or []
        )
        
        # Process with multimodal orchestrator
        orchestrator = MultimodalOrchestrator()
        response = await orchestrator.process_request(multimodal_request)
        
        logger.info(
            "Multimodal chat completed",
            content_type=response.content_type,
            tool_calls_count=len(response.tool_calls)
        )
        
        return MultimodalChatResponse(
            message=response.content,
            content_type=response.content_type,
            metadata=response.metadata,
            tool_calls=response.tool_calls,
            reasoning=response.reasoning
        )
        
    except DigiSetuException:
        raise
    except Exception as e:
        logger.error("Multimodal chat failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multimodal chat failed: {str(e)}"
        )


@router.get("/capabilities")
async def get_multimodal_capabilities():
    """
    Get available multimodal capabilities.
    
    Returns:
        List of available capabilities and their descriptions
    """
    try:
        capabilities = {
            "vision": {
                "description": "Analyze and describe images",
                "supported_formats": ["jpg", "jpeg", "png", "gif", "webp"],
                "max_file_size": "20MB",
                "models": ["gpt-4-vision-preview", "claude-3-opus", "claude-3-sonnet"]
            },
            "audio": {
                "description": "Transcribe and analyze audio files",
                "supported_formats": ["mp3", "wav", "m4a", "ogg", "flac", "webm"],
                "max_file_size": "25MB",
                "models": ["whisper-1"]
            },
            "tools": {
                "description": "Execute various tools and functions",
                "available_tools": [
                    "calculate - Perform mathematical calculations",
                    "get_weather - Get weather information for locations",
                    "generate_code - Generate code in various programming languages",
                    "search_database - Search internal databases",
                    "analyze_data - Analyze data and generate insights"
                ]
            },
            "search": {
                "description": "Search the web for information",
                "search_types": ["web", "news", "images"],
                "features": ["suggestions", "trending_topics"]
            },
            "intent_detection": {
                "description": "Automatically detect user intent and use appropriate tools",
                "supported_intents": [
                    "audio_generation",
                    "image_analysis", 
                    "calculation",
                    "weather",
                    "code_generation",
                    "web_search",
                    "data_analysis"
                ]
            }
        }
        
        return {
            "success": True,
            "capabilities": capabilities,
            "total_capabilities": len(capabilities)
        }
        
    except Exception as e:
        logger.error("Failed to get capabilities", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get capabilities: {str(e)}"
        )


@router.post("/test-intent")
async def test_intent_detection(message: str):
    """
    Test intent detection for a message.
    
    Args:
        message: Message to test intent detection on
    
    Returns:
        Detected intent and confidence
    """
    try:
        orchestrator = MultimodalOrchestrator()
        detected_intent = orchestrator._detect_intent(message)
        
        return {
            "success": True,
            "message": message,
            "detected_intent": detected_intent,
            "has_intent": detected_intent is not None
        }
        
    except Exception as e:
        logger.error("Intent detection test failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Intent detection failed: {str(e)}"
        )

