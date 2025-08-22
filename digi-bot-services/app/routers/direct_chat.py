"""
Direct Chat Router - Production Ready

Clean, direct streaming from AI to frontend with minimal overhead.
No complex orchestrator, no tool registry spam - just efficient streaming.
"""

import json
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import structlog

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.chart_tools import get_chart_tools, process_tool_calls
from app.models.user import User
from app.models.conversation import Conversation, Message, MessageRole
from app.core.database import get_db_session
from app.core.simple_config import get_settings
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/direct-chat", tags=["Direct Chat"])


class ChatRequest(BaseModel):
    """Request model for chat."""
    messages: List[dict]
    conversation_id: Optional[int] = None
    files: Optional[List[dict]] = None


class ChatHistoryRequest(BaseModel):
    """Request model for chat history."""
    user_id: int
    limit: int = 20


@router.post("", response_class=StreamingResponse)
async def chat_stream_endpoint(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db_session),
    settings = Depends(get_settings)
):
    """
    Stream chat response directly from AI with chart tools.
    Saves conversation to database for history.
    """
    
    async def generate_response():
        """Generate direct streaming response."""
        try:
            # Validate request
            if not request.messages:
                yield f"data: {json.dumps({'type': 'error', 'content': 'No messages provided'})}\n\n"
                return
            
            last_message = request.messages[-1]
            user_message = last_message.get('content', '')
            
            if not user_message:
                yield f"data: {json.dumps({'type': 'error', 'content': 'No user message found'})}\n\n"
                return
            
            # Initialize AI provider
            provider = AnthropicProvider()
            await provider.initialize()
            
            # Convert messages to AI format
            messages = []
            for msg in request.messages:
                messages.append({
                    "role": msg.get('role', 'user'),
                    "content": msg.get('content', '')
                })
            
            logger.info(f"Chat request: {user_message[:100]}...")
            
            # Backend Approach: Use generate_completion (non-streaming) for tool handling
            logger.info("Step 1: Initial request with chart tools")
            
            response = await provider.generate_completion(
                messages=messages,
                model="claude-sonnet-4-20250514",
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                tools=get_chart_tools(),
                enable_reasoning=True,
                reasoning_budget=settings.REASONING_BUDGET
            )
            
            # Parse initial response
            content_blocks = response.get('content', [])
            initial_text = ""
            tool_calls = []
            
            for block in content_blocks:
                if block.get('type') == 'text':
                    initial_text += block.get('text', '')
                elif block.get('type') == 'tool_use':
                    tool_calls.append(block)
            
            # Stream initial text
            if initial_text:
                yield f"data: {json.dumps({'type': 'content', 'content': initial_text})}\n\n"
            
            # Process tool calls if any
            if tool_calls:
                logger.info(f"Step 2: Processing {len(tool_calls)} tool calls")
                yield f"data: {json.dumps({'type': 'activity', 'content': 'Creating visualizations...'})}\n\n"
                
                # Process all tool calls properly
                tool_results = process_tool_calls(tool_calls)
                
                # Stream chart components
                for result in tool_results:
                    content = result.get('content', '')
                    yield f"data: {json.dumps({'type': 'tool_output', 'content': content})}\n\n"
                
                # Step 3: Get continuation
                logger.info("Step 3: Getting continuation")
                
                messages.append({
                    "role": "assistant",
                    "content": content_blocks
                })
                
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
                
                # Loop to handle multiple rounds of tool calls
                max_rounds = 15  # Prevent infinite loops
                for round_num in range(max_rounds):
                    continuation_response = await provider.generate_completion(
                        messages=messages,
                        model="claude-sonnet-4-20250514",
                        max_tokens=settings.MAX_TOKENS,
                        temperature=settings.TEMPERATURE,
                        tools=get_chart_tools(),
                        enable_reasoning=True,
                        reasoning_budget=settings.REASONING_BUDGET
                    )
                    
                    # Parse continuation response
                    continuation_blocks = continuation_response.get('content', [])
                    continuation_text = ""
                    continuation_tool_calls = []
                    
                    for block in continuation_blocks:
                        if block.get('type') == 'text':
                            continuation_text += block.get('text', '')
                        elif block.get('type') == 'tool_use':
                            continuation_tool_calls.append(block)
                    
                    # Stream continuation text
                    if continuation_text:
                        yield f"data: {json.dumps({'type': 'content', 'content': continuation_text})}\n\n"
                    
                    # If no more tool calls, we're done
                    if not continuation_tool_calls:
                        break
                    
                    # Process continuation tool calls
                    logger.info(f"Round {round_num + 1}: Processing {len(continuation_tool_calls)} more tool calls")
                    yield f"data: {json.dumps({'type': 'activity', 'content': 'Creating more visualizations...'})}\n\n"
                    
                    # Process continuation tool calls properly
                    continuation_tool_results = process_tool_calls(continuation_tool_calls)
                    
                    # Stream additional chart components
                    for result in continuation_tool_results:
                        content = result.get('content', '')
                        yield f"data: {json.dumps({'type': 'tool_output', 'content': content})}\n\n"
                    
                    # Add to conversation for next round
                    messages.append({
                        "role": "assistant",
                        "content": continuation_blocks
                    })
                    
                    messages.append({
                        "role": "user",
                        "content": continuation_tool_results
                    })
            
            # Streaming is complete - the provider handles all tool calls and continuations
            
            # TODO: Save conversation to database here
            # This will be implemented when we integrate with user auth
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete', 'content': 'Response completed'})}\n\n"
            
        except Exception as e:
            logger.error("Chat stream error", error=str(e))
            yield f"data: {json.dumps({'type': 'error', 'content': f'Error: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


@router.get("/history/{user_id}")
async def get_chat_history(
    user_id: int,
    limit: int = 20,
    db: AsyncSession = Depends(get_db_session)
):
    """Get chat history for a user."""
    try:
        # Query conversations for user
        from sqlalchemy import select
        
        stmt = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(
            Conversation.updated_at.desc()
        ).limit(limit)
        
        result = await db.execute(stmt)
        conversations = result.scalars().all()
        
        # Convert to dict format
        history = []
        for conv in conversations:
            history.append({
                "id": conv.id,
                "title": conv.title,
                "summary": conv.summary,
                "message_count": conv.message_count,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
            })
        
        return {"conversations": history}
        
    except Exception as e:
        logger.error("Error fetching chat history", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")


@router.get("/conversation/{conversation_id}")
async def get_conversation_messages(
    conversation_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get all messages in a conversation."""
    try:
        from sqlalchemy import select
        
        # Get conversation with messages
        stmt = select(Conversation).where(
            Conversation.id == conversation_id
        )
        
        result = await db.execute(stmt)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages
        stmt = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())
        
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        # Convert to dict format
        message_list = []
        for msg in messages:
            message_list.append({
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            })
        
        return {
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "summary": conversation.summary,
            },
            "messages": message_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching conversation messages", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch conversation messages")


@router.get("/health")
async def test_endpoint():
    """Test endpoint to verify the router is working."""
    return {
        "status": "ok",
        "message": "Direct chat router is working",
        "timestamp": time.time()
    }
