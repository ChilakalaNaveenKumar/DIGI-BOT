"""
Clean implementation of direct chat with natural tool flow
"""
import json
import asyncio
from typing import Dict, List, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings
from app.models.conversation import ConversationRequest
from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.comprehensive_tools import get_conditional_tools, process_comprehensive_tool_calls
from app.services.conversation_manager import ConversationManager
from app.services.conversation_service import ConversationService

import structlog
logger = structlog.get_logger()

router = APIRouter()
settings = get_settings()


async def generate_conversation_title(user_message: str, provider: AnthropicProvider, settings) -> str:
    """Generate a conversation title from the first user message."""
    try:
        title_messages = [
            {
                "role": "system",
                "content": "Generate a short, descriptive title (max 6 words) for this conversation based on the user's message. Respond with only the title, no quotes or extra text."
            },
            {
                "role": "user", 
                "content": user_message
            }
        ]
        
        title_response = await provider.generate_completion(
            messages=title_messages,
            enable_thinking=False
        )
        
        title = title_response.get("content", "New Conversation").strip()
        return title[:50] if len(title) > 50 else title
        
    except Exception as e:
        logger.error("Error generating conversation title", error=str(e))
        return "New Conversation"


@router.post("/stream")
async def stream_chat_response(
    request: ConversationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Stream chat response with natural tool execution flow."""
    
    async def generate():
        try:
            user_message = request.message
            conversation_id = request.conversation_id
            is_first_message = conversation_id is None
            
            logger.info("Processing chat request", 
                       user_message_length=len(user_message),
                       conversation_id=conversation_id,
                       is_first_message=is_first_message)
            
            # Generate title for first message
            conversation_title = None
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
            
            # System message with natural instructions
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
            
            # Get tools based on user input
            available_tools = get_conditional_tools(
                has_audio=request.has_audio,
                has_image=request.has_image,
                enable_audio_generation=request.enable_audio_generation
            )
            
            tool_names = [tool.get('name', tool.get('type', 'unknown')) for tool in available_tools]
            logger.info(f"🔧 Available tools: {tool_names}")
            logger.info(f"🤖 Using AI model: {settings.DEFAULT_AI_MODEL}")
            
            # Natural tool execution loop
            assistant_content = ""
            tool_calls_used = 0
            current_messages = final_messages.copy()
            max_tool_iterations = 10
            tool_iteration = 0
            
            while tool_iteration < max_tool_iterations:
                async for chunk in provider.stream_completion(
                    messages=current_messages,
                    enable_thinking=True,
                    complex_reasoning=True,  # Large budget for comprehensive analysis
                    tools=available_tools
                ):
                    # Stream all chunks to frontend
                    yield f"data: {json.dumps(chunk)}\n\n"
                    
                    # Handle tool execution
                    if chunk.get("type") == "custom_tool_use_required":
                        assistant_message = chunk.get("assistant_message")
                        custom_tools = chunk.get("custom_tools", [])
                        
                        logger.info(f"🔧 Executing tools: {[t['name'] for t in custom_tools]}")
                        
                        # Execute tools
                        tool_results = await process_comprehensive_tool_calls(custom_tools)
                        
                        # Build tool result messages
                        tool_result_content = []
                        for i, tool_result in enumerate(tool_results):
                            tool_id = custom_tools[i]["id"]
                            result_content = tool_result.get("content", "No result")
                            
                            tool_result_content.append({
                                "type": "tool_result",
                                "tool_use_id": tool_id,
                                "content": str(result_content)
                            })
                            
                            # Yield tool output to frontend
                            yield f"data: {json.dumps({'type': 'tool_output', 'content': str(result_content)})}\n\n"
                        
                        # Add to context for continued analysis
                        current_messages.append(assistant_message)
                        current_messages.append({
                            "role": "user",
                            "content": tool_result_content
                        })
                        
                        tool_calls_used += len(custom_tools)
                        tool_iteration += 1
                        break  # Continue with updated context
                        
                    elif chunk.get("type") == "completion_finished":
                        # Natural completion - extract content
                        final_assistant_message = chunk.get("assistant_message", {})
                        for content_block in final_assistant_message.get("content", []):
                            if content_block.get("type") == "text":
                                assistant_content += content_block.get("text", "")
                        
                        # Exit both loops
                        tool_iteration = max_tool_iterations
                        break
                        
                else:
                    # No tool use - natural completion
                    break
            
            # Check for max iterations
            if tool_iteration >= max_tool_iterations:
                logger.warning(f"Reached maximum tool iterations ({max_tool_iterations})")
                yield f"data: {json.dumps({'type': 'warning', 'content': 'Analysis reached maximum tool usage limit'})}\n\n"
            
            # Save conversation
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
                        tool_calls_used=tool_calls_used,
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
                        tool_calls_used=tool_calls_used,
                        summary=conversation_summary
                    )
                except Exception as e:
                    logger.error("Error saving conversation turn", error=str(e))
            
            # Final completion signal
            yield f"data: {json.dumps({'type': 'stream_complete'})}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error("Error in stream_chat_response", error=str(e))
            yield f"data: {json.dumps({'type': 'error', 'content': f'An error occurred: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )
