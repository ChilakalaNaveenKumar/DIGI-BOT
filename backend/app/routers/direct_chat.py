"""
Direct Chat Router

Simple, direct streaming from AI to frontend with Chart.js components.
No complex orchestrator, no analysis overhead - just pure streaming.
"""

import json
import time
from typing import List, Optional
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import structlog

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.chart_tools import get_chart_tools, execute_chart_tool
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/direct-chat", tags=["Direct Chat"])


class DirectChatRequest(BaseModel):
    """Request model for direct chat."""
    messages: List[dict]
    files: Optional[List[dict]] = None


@router.post("", response_class=StreamingResponse)
async def direct_chat_endpoint(
    request: DirectChatRequest,
    http_request: Request = None,
):
    """
    Direct chat endpoint - streams directly from AI with chart tools.
    No orchestrator overhead, no complex analysis.
    """
    
    async def generate_response():
        """Generate direct streaming response."""
        try:
            # Get the last user message
            if not request.messages:
                yield f"data: {json.dumps({'type': 'error', 'content': 'No messages provided'})}\n\n"
                return
            
            last_message = request.messages[-1]
            user_message = last_message.get('content', '')
            
            if not user_message:
                yield f"data: {json.dumps({'type': 'error', 'content': 'No user message found'})}\n\n"
                return
            
            # Initialize Anthropic provider
            provider = AnthropicProvider()
            await provider.initialize()
            
            # Convert messages to Anthropic format
            messages = []
            for msg in request.messages:
                messages.append({
                    "role": msg.get('role', 'user'),
                    "content": msg.get('content', '')
                })
            
            logger.info(f"Direct chat request: {user_message[:100]}...")
            
            # Step 1: Initial request with chart tools
            yield f"data: {json.dumps({'type': 'status', 'content': 'Thinking...'})}\n\n"
            
            response = await provider.generate_completion(
                messages=messages,
                model="claude-sonnet-4-20250514",
                max_tokens=16000,
                temperature=0.7,
                tools=get_chart_tools()
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
            
            # Step 2: Process tool calls if any
            if tool_calls:
                yield f"data: {json.dumps({'type': 'status', 'content': 'Creating visualization...'})}\n\n"
                
                tool_results = []
                for tool_call in tool_calls:
                    result = execute_chart_tool(tool_call)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_call.get('id'),
                        "content": result
                    })
                
                # Stream chart components
                for result in tool_results:
                    content = result.get('content', '')
                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                
                # Step 3: Get continuation
                yield f"data: {json.dumps({'type': 'status', 'content': 'Analyzing...'})}\n\n"
                
                messages.append({
                    "role": "assistant",
                    "content": content_blocks
                })
                
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
                
                continuation_response = await provider.generate_completion(
                    messages=messages,
                    model="claude-sonnet-4-20250514",
                    max_tokens=16000,
                    temperature=0.7,
                    tools=get_chart_tools()
                )
                
                # Parse and stream continuation
                continuation_blocks = continuation_response.get('content', [])
                for block in continuation_blocks:
                    if block.get('type') == 'text':
                        continuation_text = block.get('text', '')
                        if continuation_text:
                            yield f"data: {json.dumps({'type': 'content', 'content': continuation_text})}\n\n"
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete', 'content': 'Response completed'})}\n\n"
            
        except Exception as e:
            logger.error("Direct chat error", error=str(e))
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


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify the router is working."""
    return {
        "status": "ok",
        "message": "Direct chat router is working",
        "timestamp": time.time()
    }
