"""
Stream Router - Clean 3-Step Stepper Implementation

Efficient streaming with 3-step approach:
1. Planning + Built-in Research (with full history)
2. Custom Tool Execution (minimal tokens)  
3. Final Analysis (with distilled context)
"""

import json
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import structlog

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.comprehensive_tools import get_conditional_tools, process_comprehensive_tool_calls
from app.services.conversation_service import ConversationService
from app.services.conversation_manager import ConversationManager
from app.models.user import User
from app.core.database import get_db_session
from app.core.config import get_settings
from app.core.auth_deps import get_current_user_required
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/stream", tags=["Stream"])


class StreamRequest(BaseModel):
    """Request model for streaming."""
    messages: List[dict]
    conversation_id: Optional[int] = None
    files: Optional[List[dict]] = None
    user_id: Optional[int] = None
    # Tool enablement flags
    has_audio: bool = False
    has_image: bool = False
    enable_audio_generation: bool = False


async def generate_conversation_title(user_message: str, provider: AnthropicProvider, settings = None) -> str:
    """Generate a simple 4-5 word conversation title from the user's first message."""
    title_prompt = f"""Based on this user message, generate a short conversation title of exactly 4-5 words that captures the main topic or question.

User message: "{user_message}"
Return ONLY the title, nothing else.

Title:"""

    try:
        model = settings.DEFAULT_AI_MODEL if settings else "claude-sonnet-4-20250514"
        
        response = await provider.generate_completion(
            messages=[{"role": "user", "content": title_prompt}]
        )
        
        title = ""
        content_blocks = response.get('content', [])
        for block in content_blocks:
            if block.get('type') == 'text':
                title += block.get('text', '')
        
        # Clean and validate title
        title = title.strip().replace('"', '').replace('\n', ' ')
        words = title.split()
        
        # Ensure 4-5 words
        if len(words) > 5:
            title = ' '.join(words[:5])
        elif len(words) < 3:
            title = f"Chat about {words[0] if words else 'Topic'}"
            
        return title or "New Conversation"
        
    except Exception as e:
        logger.error("Error generating conversation title", error=str(e))
        return "New Conversation"


@router.post("", response_class=StreamingResponse)
async def stream_endpoint(
    request: StreamRequest,
    db: AsyncSession = Depends(get_db_session),
    settings = Depends(get_settings)
):
    """
    Clean 3-step stepper streaming endpoint.
    
    Step 1: Planning + Built-in Research (full history)
    Step 2: Custom Tool Execution (minimal tokens)
    Step 3: Final Analysis (distilled context)
    """
    
    async def generate_response():
        """Generate 3-step stepper response."""
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
            
            logger.info(f"Processing message with 3-step stepper: {user_message[:100]}...")
            
            # Check if this is the first message
            is_first_message = not request.conversation_id
            conversation_id = request.conversation_id
            conversation_title = None
            
            # For first message: Generate title first
            if is_first_message:
                logger.info("First message detected - generating conversation title")
                yield f"data: {json.dumps({'type': 'activity', 'content': 'Creating conversation...'})}\n\n"
                
                provider = AnthropicProvider()
                await provider.initialize()
                conversation_title = await generate_conversation_title(user_message, provider, settings)
                logger.info(f"Generated title: {conversation_title}")
            
            # Initialize managers
            conv_manager = ConversationManager(db)
            
            # Prepare conversation context
            prepared_messages, conversation_summary = await conv_manager.prepare_conversation_context(
                conversation_id=conversation_id,
                new_user_message=user_message,
                existing_summary=None
            )
            
            # Add system message
            system_message = {
                "role": "system", 
                "content": """You are Digi Setu AI, an advanced AI assistant with comprehensive capabilities.

**Important:** Provide well-formatted, helpful responses using markdown when it improves readability.

When providing analysis, create comprehensive responses that naturally integrate visualizations and data throughout your analysis. Use tools as needed to support your insights, and reference the results of charts, tables, and searches directly in your analysis."""
            }
            
            final_messages = [system_message] + prepared_messages
            
            # Initialize provider
            provider = AnthropicProvider()
            await provider.initialize()
            
            # Get available tools
            available_tools = get_conditional_tools(
                has_audio=request.has_audio,
                has_image=request.has_image,
                enable_audio_generation=request.enable_audio_generation
            )
            
            # Log tools and model
            tool_names = [tool.get('name', tool.get('type', 'unknown')) for tool in available_tools]
            logger.info(f"🔧 Available tools: {tool_names}")
            logger.info(f"🤖 Using model: {settings.DEFAULT_AI_MODEL}")
            
            # Execute 3-step stepper
            assistant_content = ""
            
            async for chunk in provider.stream_stepper(
                messages=final_messages,
                tools=available_tools,
                enable_thinking=True,
                complex_reasoning=True
            ):
                # Pass through all chunks to frontend
                yield f"data: {json.dumps(chunk)}\n\n"
                
                # Extract text content for saving
                if chunk.get("type") == "content_block_delta":
                    delta = chunk.get("delta", {})
                    if delta.get("type") == "text_delta":
                        assistant_content += delta.get("text", "")
                elif chunk.get("type") == "completion_finished":
                    final_assistant_message = chunk.get("assistant_message", {})
                    for content_block in final_assistant_message.get("content", []):
                        if content_block.get("type") == "text":
                            assistant_content += content_block.get("text", "")
            
            # Handle conversation saving
            if is_first_message and conversation_title:
                try:
                    logger.info("Creating and saving new conversation")
                    conv_service = ConversationService(db)
                    conversation = await conv_service.create_conversation(
                        user_id=1,  # TODO: Use actual user_id from auth
                        title=conversation_title
                    )
                    conversation_id = conversation.id
                    
                    await conv_manager.save_conversation_turn(
                        conversation_id=conversation_id,
                        user_message=user_message,
                        assistant_response=assistant_content,
                        tool_calls_used=0,  # Will be tracked in stepper
                        summary=conversation_summary
                    )
                    
                    yield f"data: {json.dumps({'type': 'conversation_created', 'conversation_id': conversation_id, 'title': conversation_title})}\n\n"
                    
                except Exception as e:
                    logger.error("Error saving new conversation", error=str(e))
            
            elif conversation_id:
                try:
                    await conv_manager.save_conversation_turn(
                        conversation_id=conversation_id,
                        user_message=user_message,
                        assistant_response=assistant_content,
                        tool_calls_used=0,  # Will be tracked in stepper
                        summary=conversation_summary
                    )
                except Exception as e:
                    logger.error("Error saving conversation turn", error=str(e))
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete', 'content': 'Response completed'})}\n\n"
            
        except Exception as e:
            logger.error("Stream endpoint error", error=str(e))
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


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Stream router is working",
        "timestamp": time.time()
    }

