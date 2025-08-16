"""
AI Chat Router

Handles AI chat interactions with streaming and non-streaming endpoints.
"""

import json
import time
from typing import Dict, Any

import structlog
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import DigiSetuException
from app.models.conversation import MessageRole
from app.models.user import User
from app.schemas.chat import ChatRequest
from app.services.auth_service import get_current_user
from app.services.conversation_service import ConversationService

logger = structlog.get_logger(__name__)
router = APIRouter(tags=["ai-chat"])


@router.post("/test")
async def test_endpoint():
    """Test endpoint for basic connectivity."""
    return {"message": "AI Chat router is working", "timestamp": time.time()}


@router.post("/send")
async def send_message_simple(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    http_request: Request = None,
):
    """Real chat endpoint using AI orchestrator."""
    try:
        # Get AI orchestrator from app state
        ai_orchestrator = http_request.app.state.ai_orchestrator
        
        # Prepare user preferences
        user_preferences = {
            "preferred_provider": getattr(current_user, 'preferred_ai_provider', 'openai'),
            "theme": getattr(current_user, 'theme_preference', 'light'),
            "language": getattr(current_user, 'language_preference', 'en'),
        }
        
        # Simple conversation history (empty for now)
        conversation_history = []
        
        # Project settings (empty for now)
        project_settings = {}
        
        # Collect response from AI orchestrator
        response_content = ""
        activities = []
        selected_provider = None
        
        async for chunk in ai_orchestrator.process_request(
            user_message=request.message,
            conversation_history=conversation_history,
            user_preferences=user_preferences,
            project_settings=project_settings
        ):
            chunk_type = chunk.get("type")
            chunk_content = chunk.get("content", "")
            
            if chunk_type == "activity":
                activities.append(chunk_content)
            elif chunk_type == "content":
                response_content += chunk_content
                selected_provider = chunk.get("provider")
            elif chunk_type == "error":
                raise Exception(f"AI Error: {chunk_content}")
        
        return {
            "conversation_id": request.conversation_id or 1,
            "message_id": str(int(time.time())),
            "response": {
                "content": response_content or "No response generated",
                "ai_provider": selected_provider or str(request.provider),
                "timestamp": time.time()
            },
            "activities": activities,
            "processing_time": 1.0
        }
        
    except Exception as e:
        logger.error("Error in real chat", error=str(e), exc_info=True)
        return {
            "error": {
                "code": "CHAT_ERROR", 
                "message": f"Chat error: {str(e)}"
            }
        }


@router.post("/stream", response_class=StreamingResponse)
async def stream_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    http_request: Request = None,
):
    """
    Stream AI chat responses with real-time updates.
    
    This endpoint provides:
    - Conversation management with database persistence
    - Real-time activity streaming (thought process)
    - Tool execution with step-by-step updates
    - Multi-modal content support
    """
    
    async def generate_response():
        """Generate streaming response with proper conversation handling."""
        try:
            conversation_service = ConversationService(db)
            ai_orchestrator = http_request.app.state.ai_orchestrator
            
            # Get or create conversation
            if request.conversation_id:
                conversation = await conversation_service.get_conversation(
                    request.conversation_id, current_user.id
                )
                if not conversation:
                    yield f"data: {json.dumps({'type': 'error', 'content': {'code': 'CONVERSATION_NOT_FOUND', 'message': 'Conversation not found'}})}\n\n"
                    return
            else:
                # Create new conversation
                conversation = await conversation_service.create_conversation(
                    user_id=current_user.id,
                    title=request.message[:50] + "..." if len(request.message) > 50 else request.message,
                    project_id=request.project_id,
                    ai_provider=request.provider,
                    ai_settings=request.ai_settings
                )
            
            # Save user message
            user_message = await conversation_service.add_message(
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=request.message,
                files=request.files
            )
            
            # Get conversation history
            conversation_history = await conversation_service.get_conversation_history(
                conversation.id, limit=20
            )
            
            # Prepare user preferences
            user_preferences = {
                "preferred_provider": current_user.preferred_ai_provider,
                "theme": current_user.theme_preference,
                "language": current_user.language_preference,
                "conversation_history_limit": getattr(current_user, 'conversation_history_limit', 20),
            }
            
            # Project settings
            project_settings = {}
            if conversation.project:
                project_settings = {
                    "ai_provider": conversation.project.default_ai_provider,
                    "ai_model": conversation.project.default_ai_model,
                    "ai_settings": conversation.project.ai_settings or {},
                }
            
            # Send initial conversation info
            yield f"data: {json.dumps({'type': 'conversation_id', 'content': conversation.id})}\n\n"
            yield f"data: {json.dumps({'type': 'message_id', 'content': user_message.id})}\n\n"
            
            # Initialize assistant message
            assistant_message = await conversation_service.add_message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                ai_provider=request.provider or user_preferences["preferred_provider"],
                ai_model=request.model
            )
            
            yield f"data: {json.dumps({'type': 'assistant_message_id', 'content': assistant_message.id})}\n\n"
            
            # Stream the AI orchestrator process
            response_content = ""
            async for chunk in ai_orchestrator.process_request(
                user_message=request.message,
                conversation_history=[msg.to_dict() for msg in conversation_history],
                user_preferences=user_preferences,
                project_settings=project_settings
            ):
                chunk_type = chunk.get("type")
                chunk_content = chunk.get("content", "")
                
                if chunk_type == "activity":
                    # Stream thought process steps in real-time
                    yield f"data: {json.dumps({'type': 'activity', 'content': chunk_content})}\n\n"
                elif chunk_type == "content":
                    # Stream response content
                    response_content += chunk_content
                    yield f"data: {json.dumps({'type': 'content', 'content': chunk_content, 'provider': chunk.get('provider', 'openai')})}\n\n"
                elif chunk_type == "tool_result":
                    # Stream tool execution results
                    yield f"data: {json.dumps({'type': 'tool_result', 'tool_name': chunk.get('tool_name'), 'content': chunk_content})}\n\n"
                elif chunk_type == "error":
                    yield f"data: {json.dumps({'type': 'error', 'content': chunk_content})}\n\n"
                    return
            
            # Update assistant message with final content
            await conversation_service.update_message(
                message_id=assistant_message.id,
                content=response_content,
                ai_provider=request.provider or user_preferences["preferred_provider"],
                ai_model=request.model
            )
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation.id, 'message_id': assistant_message.id})}\n\n"
            
        except Exception as e:
            logger.error("Error in streaming chat", error=str(e), exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': f'Streaming error: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Content-Encoding": "identity",  # Prevent compression
        }
    )