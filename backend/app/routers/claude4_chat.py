"""
Claude 4 Chat Router

New chat API that uses Claude 4 as the main orchestrator with other AI models as tools.
Supports streaming responses with component injection capability.
"""

import json
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.dev_auth import get_current_user
from app.core.database import get_db_session
from app.models.user import User
from app.models.conversation import MessageRole
from app.services.conversation_service import ConversationService
from app.services.streaming_analysis_wrapper import StreamingAnalysisWrapper
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Claude 4 Chat"])


class ChatRequest(BaseModel):
    """Request model for Claude 4 chat."""
    message: str
    conversation_id: Optional[str] = None
    project_id: Optional[str] = None
    files: Optional[List[dict]] = None
    ai_settings: Optional[dict] = None
    user_preferences: Optional[dict] = None
    system_message: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for non-streaming chat."""
    message: str
    conversation_id: str
    metadata: dict
    tools_used: List[str]


@router.post("/test")
async def test_endpoint():
    """Test endpoint to verify Claude 4 chat router is working."""
    return {
        "message": "Claude 4 Chat router is working",
        "timestamp": time.time(),
        "service": "claude4-chat",
        "orchestrator": "claude-4"
    }


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    http_request: Request = None,
):
    """
    Send a message using Claude 4 orchestrator (non-streaming).
    
    For simple requests that don't require real-time streaming.
    """
    try:
        # Get Claude 4 orchestrator from app state
        if not hasattr(http_request.app.state, 'claude4_orchestrator'):
            raise DigiSetuException(
                status_code=500,
                error_code="ORCHESTRATOR_NOT_AVAILABLE",
                message="Claude 4 orchestrator not initialized"
            )
        
        orchestrator = http_request.app.state.claude4_orchestrator
        conversation_service = ConversationService(db)
        
        # Get or create conversation
        if request.conversation_id:
            conversation = await conversation_service.get_conversation(
                request.conversation_id, current_user.id
            )
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            # Create new conversation
            conversation = await conversation_service.create_conversation(
                user_id=current_user.id,
                title=request.message[:50] + "..." if len(request.message) > 50 else request.message,
                project_id=request.project_id,
                ai_provider="claude4_orchestrator",
                ai_settings=request.ai_settings
            )
        
        # Save user message
        await conversation_service.add_message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request.message,
            files=request.files
        )
        
        # Get conversation history
        conversation_history = await conversation_service.get_conversation_history(
            conversation.id, limit=20
        )
        
        # Convert to format expected by orchestrator
        history = [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in conversation_history
        ]
        
        # Collect response from Claude 4 orchestrator
        response_content = ""
        tools_used = []
        metadata = {}
        
        async for chunk in orchestrator.process_request(
            user_message=request.message,
            conversation_history=history,
            user_preferences=request.user_preferences,
            files=request.files,
            user_id=current_user.id,
            db=db,
            system_message=request.system_message
        ):
            chunk_type = chunk.get("type")
            chunk_content = chunk.get("content", "")
            chunk_metadata = chunk.get("metadata", {})
            
            if chunk_type == "content":
                response_content += chunk_content
                metadata.update(chunk_metadata)
                
                # Track tools used
                if "tools_used" in chunk_metadata:
                    tools_used.extend(chunk_metadata["tools_used"])
            
            elif chunk_type == "error":
                raise DigiSetuException(
                    status_code=500,
                    error_code="ORCHESTRATION_ERROR",
                    message=f"Claude 4 orchestration error: {chunk_content}"
                )
        
        # Save assistant response
        await conversation_service.add_message(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=response_content,
            metadata={
                **metadata,
                "tools_used": list(set(tools_used)),
                "orchestrator": "claude4"
            }
        )
        
        return ChatResponse(
            message=response_content,
            conversation_id=str(conversation.id),
            metadata=metadata,
            tools_used=list(set(tools_used))
        )
        
    except DigiSetuException:
        raise
    except Exception as e:
        logger.error("Claude 4 chat error", error=str(e))
        raise DigiSetuException(
            status_code=500,
            error_code="CHAT_ERROR",
            message=f"Chat error: {str(e)}"
        )


@router.post("/stream", response_class=StreamingResponse)
async def stream_chat_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    http_request: Request = None,
):
    """
    Stream AI chat responses using Claude 4 orchestrator.
    
    This endpoint provides:
    - Real-time streaming from Claude 4 orchestrator
    - Tool execution with step-by-step updates
    - Component analysis integration (frontend calls /analyze during streaming)
    - Conversation management with database persistence
    """
    
    async def generate_response():
        """Generate streaming response with Claude 4 orchestration and analysis wrapper."""
        try:
            # Get services
            if not hasattr(http_request.app.state, 'claude4_orchestrator'):
                yield f"data: {json.dumps({'type': 'error', 'content': 'Claude 4 orchestrator not initialized'})}\n\n"
                return
            
            orchestrator = http_request.app.state.claude4_orchestrator
            conversation_service = ConversationService(db)
            
            # Initialize streaming analysis wrapper
            wrapper = StreamingAnalysisWrapper()
            await wrapper.initialize()
            
            # Get or create conversation
            if request.conversation_id:
                conversation = await conversation_service.get_conversation(
                    request.conversation_id, current_user.id
                )
                if not conversation:
                    yield f"data: {json.dumps({'type': 'error', 'content': 'Conversation not found'})}\n\n"
                    return
            else:
                # Create new conversation
                conversation = await conversation_service.create_conversation(
                    user_id=current_user.id,
                    title=request.message[:50] + "..." if len(request.message) > 50 else request.message,
                    project_id=request.project_id,
                    ai_provider="claude4_orchestrator",
                    ai_settings=request.ai_settings
                )
                
                # Send conversation ID to frontend
                yield f"data: {json.dumps({'type': 'conversation_id', 'content': str(conversation.id)})}\n\n"
            
            # Get conversation history BEFORE saving current message
            conversation_history = await conversation_service.get_conversation_history(
                conversation.id, limit=20
            )
            
            # Save user message
            await conversation_service.add_message(
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=request.message,
                files=request.files
            )
            
            # Convert to format expected by orchestrator
            history = [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in conversation_history
            ]
            
            # Stream response through analysis wrapper
            response_content = ""
            tools_used = []
            final_metadata = {}
            
            # Get original stream from orchestrator
            original_stream = orchestrator.process_request(
                user_message=request.message,
                conversation_history=history,
                user_preferences=request.user_preferences,
                files=request.files,
                user_id=current_user.id,
                db=db,
                system_message=request.system_message
            )
            
            # Wrap stream with analysis capabilities
            wrapped_stream = wrapper.wrap_stream(
                original_stream=original_stream,
                user_preferences=request.user_preferences
            )
            
            # Process wrapped stream
            async for chunk in wrapped_stream:
                chunk_type = chunk.get("type")
                chunk_content = chunk.get("content", "")
                chunk_metadata = chunk.get("metadata", {})
                is_final = chunk.get("final", False)
                
                # Forward chunk to frontend (includes placeholders and components)
                yield f"data: {json.dumps(chunk)}\n\n"
                
                # Collect content for database storage (only original content)
                if chunk_type == "content":
                    response_content += chunk_content
                    final_metadata.update(chunk_metadata)
                    
                    # Track tools used
                    if "tools_used" in chunk_metadata:
                        tools_used.extend(chunk_metadata["tools_used"])
                
                elif chunk_type == "error":
                    # Error already sent to frontend, log and break
                    logger.error("Claude 4 orchestration error", error=chunk_content)
                    await wrapper.cleanup()
                    return
            
            # Cleanup wrapper
            await wrapper.cleanup()
            
            # Save assistant response to database
            if response_content:
                await conversation_service.add_message(
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=response_content,
                    metadata={
                        **final_metadata,
                        "tools_used": list(set(tools_used)),
                        "orchestrator": "claude4"
                    }
                )
            
            # Send final completion signal
            yield f"data: {json.dumps({'type': 'complete', 'content': 'Response completed'})}\n\n"
            
        except Exception as e:
            logger.error("Claude 4 streaming error", error=str(e))
            yield f"data: {json.dumps({'type': 'error', 'content': f'Streaming error: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


@router.get("/conversations")
async def get_user_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    limit: int = 50,
    offset: int = 0
):
    """Get user's conversations."""
    try:
        conversation_service = ConversationService(db)
        conversations = await conversation_service.get_user_conversations(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return {
            "conversations": [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                    "ai_provider": conv.ai_provider,
                    "message_count": len(conv.messages) if conv.messages else 0
                }
                for conv in conversations
            ],
            "total": len(conversations)
        }
        
    except Exception as e:
        logger.error("Failed to get conversations", error=str(e))
        raise DigiSetuException(
            status_code=500,
            error_code="CONVERSATION_FETCH_ERROR",
            message="Failed to fetch conversations"
        )


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get a specific conversation with its messages."""
    try:
        conversation_service = ConversationService(db)
        conversation = await conversation_service.get_conversation(
            conversation_id, current_user.id
        )
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = await conversation_service.get_conversation_history(conversation_id)
        
        return {
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
                "ai_provider": conversation.ai_provider,
            },
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                    "metadata": msg.metadata,
                    "files": msg.files
                }
                for msg in messages
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get conversation", error=str(e))
        raise DigiSetuException(
            status_code=500,
            error_code="CONVERSATION_FETCH_ERROR",
            message="Failed to fetch conversation"
        )
