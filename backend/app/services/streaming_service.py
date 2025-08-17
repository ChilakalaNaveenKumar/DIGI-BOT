"""
Streaming Service - Real-time Response Streaming

Implements advanced streaming capabilities for real-time AI responses.
"""

import asyncio
import json
import time
from typing import Any, AsyncGenerator, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

import structlog
from pydantic import BaseModel

from app.core.config import get_settings
from app.services.ai_providers.openai_provider import OpenAIProvider
from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.reasoning_service import ReasoningService
from app.services.tool_service import ToolService

logger = structlog.get_logger(__name__)
settings = get_settings()


class StreamChunkType(str, Enum):
    """Types of streaming chunks."""
    REASONING = "reasoning"
    CONTENT = "content"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    AUDIO = "audio"
    IMAGE = "image"
    ERROR = "error"
    COMPLETE = "complete"
    METADATA = "metadata"


class StreamChunk(BaseModel):
    """Individual streaming chunk."""
    type: StreamChunkType
    delta: Optional[str] = None
    content: Optional[str] = None
    reasoning: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    multimodal_content: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    timestamp: datetime = datetime.now()


class StreamingRequest(BaseModel):
    """Request for streaming response."""
    prompt: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    include_reasoning: bool = False
    enable_tools: bool = False
    stream_audio: bool = False
    stream_images: bool = False


class StreamingService:
    """Service for real-time streaming responses."""
    
    def __init__(self):
        """Initialize streaming service."""
        self.openai_provider = OpenAIProvider()
        self.anthropic_provider = AnthropicProvider()
        self.reasoning_service = ReasoningService()
        self.tool_service = ToolService()
    
    async def stream_response(
        self,
        request: StreamingRequest
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Stream AI response in real-time chunks.
        
        Args:
            request: Streaming request configuration
            
        Yields:
            Stream chunks as they're generated
        """
        try:
            logger.info(
                "Starting streaming response",
                prompt_length=len(request.prompt),
                model=request.model,
                include_reasoning=request.include_reasoning,
                enable_tools=request.enable_tools
            )
            
            # Send initial metadata
            yield StreamChunk(
                type=StreamChunkType.METADATA,
                metadata={
                    "model": request.model,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "features": {
                        "reasoning": request.include_reasoning,
                        "tools": request.enable_tools,
                        "audio": request.stream_audio,
                        "images": request.stream_images
                    }
                }
            )
            
            # Stream reasoning if requested
            if request.include_reasoning:
                async for reasoning_chunk in self._stream_reasoning(request):
                    yield reasoning_chunk
            
            # Stream main content
            if request.model.startswith('gpt'):
                async for content_chunk in self._stream_openai_response(request):
                    yield content_chunk
            elif request.model.startswith('claude'):
                async for content_chunk in self._stream_anthropic_response(request):
                    yield content_chunk
            else:
                # Default to OpenAI
                async for content_chunk in self._stream_openai_response(request):
                    yield content_chunk
            
            # Send completion signal
            yield StreamChunk(
                type=StreamChunkType.COMPLETE,
                metadata={"completed_at": datetime.now().isoformat()}
            )
            
        except Exception as e:
            logger.error("Streaming response failed", error=str(e), exc_info=True)
            yield StreamChunk(
                type=StreamChunkType.ERROR,
                content=f"Streaming failed: {str(e)}",
                metadata={"error_type": type(e).__name__}
            )
    
    async def _stream_reasoning(
        self,
        request: StreamingRequest
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream reasoning process."""
        
        try:
            async for reasoning_data in self.reasoning_service.stream_reasoning_chain(
                request.prompt,
                reasoning_effort="medium",
                model=request.model
            ):
                if reasoning_data["type"] == "reasoning_step":
                    yield StreamChunk(
                        type=StreamChunkType.REASONING,
                        reasoning=json.dumps(reasoning_data["step"]),
                        metadata={"step_number": reasoning_data["step"]["step_number"]}
                    )
                elif reasoning_data["type"] == "reasoning_complete":
                    yield StreamChunk(
                        type=StreamChunkType.REASONING,
                        reasoning=reasoning_data["final_answer"],
                        metadata={
                            "reasoning_complete": True,
                            "total_confidence": reasoning_data["total_confidence"],
                            "reasoning_time": reasoning_data["reasoning_time"]
                        }
                    )
                    
        except Exception as e:
            logger.error("Reasoning streaming failed", error=str(e))
            yield StreamChunk(
                type=StreamChunkType.ERROR,
                content=f"Reasoning failed: {str(e)}"
            )
    
    async def _stream_openai_response(
        self,
        request: StreamingRequest
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream OpenAI response with tool calls."""
        
        try:
            messages = [
                {"role": "user", "content": request.prompt}
            ]
            
            # Add tools if enabled
            tools = None
            if request.enable_tools:
                tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": "calculate",
                            "description": "Perform mathematical calculations",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "expression": {"type": "string", "description": "Mathematical expression"}
                                },
                                "required": ["expression"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "description": "Get weather information",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {"type": "string", "description": "Location name"}
                                },
                                "required": ["location"]
                            }
                        }
                    }
                ]
            
            # Stream response
            stream = await self.openai_provider.client.chat.completions.create(
                model=request.model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                tools=tools,
                stream=True
            )
            
            accumulated_content = ""
            tool_calls = []
            
            async for chunk in stream:
                if chunk.choices:
                    choice = chunk.choices[0]
                    
                    # Handle content delta
                    if choice.delta.content:
                        delta_content = choice.delta.content
                        accumulated_content += delta_content
                        
                        yield StreamChunk(
                            type=StreamChunkType.CONTENT,
                            delta=delta_content,
                            content=accumulated_content
                        )
                    
                    # Handle tool calls
                    if choice.delta.tool_calls:
                        for tool_call in choice.delta.tool_calls:
                            if tool_call.function:
                                tool_calls.append({
                                    "id": tool_call.id,
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                })
                                
                                yield StreamChunk(
                                    type=StreamChunkType.TOOL_CALL,
                                    tool_calls=[{
                                        "id": tool_call.id,
                                        "name": tool_call.function.name,
                                        "arguments": tool_call.function.arguments
                                    }]
                                )
                    
                    # Handle finish reason
                    if choice.finish_reason:
                        # Execute tool calls if any
                        if tool_calls and request.enable_tools:
                            for tool_call in tool_calls:
                                try:
                                    if tool_call["name"] == "calculate":
                                        args = json.loads(tool_call["arguments"])
                                        result = await self.tool_service.execute(
                                            "calculate", args
                                        )
                                        
                                        yield StreamChunk(
                                            type=StreamChunkType.TOOL_RESULT,
                                            tool_results=[{
                                                "tool_call_id": tool_call["id"],
                                                "result": result
                                            }]
                                        )
                                        
                                except Exception as e:
                                    logger.error("Tool execution failed", error=str(e))
                                    yield StreamChunk(
                                        type=StreamChunkType.ERROR,
                                        content=f"Tool execution failed: {str(e)}"
                                    )
                        
                        yield StreamChunk(
                            type=StreamChunkType.COMPLETE,
                            finish_reason=choice.finish_reason,
                            metadata={"total_content_length": len(accumulated_content)}
                        )
                        break
                        
        except Exception as e:
            logger.error("OpenAI streaming failed", error=str(e))
            yield StreamChunk(
                type=StreamChunkType.ERROR,
                content=f"OpenAI streaming failed: {str(e)}"
            )
    
    async def _stream_anthropic_response(
        self,
        request: StreamingRequest
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream Anthropic response with tool calls."""
        
        try:
            messages = [
                {"role": "user", "content": request.prompt}
            ]
            
            # Add tools if enabled
            tools = None
            if request.enable_tools:
                tools = [
                    {
                        "name": "calculate",
                        "description": "Perform mathematical calculations",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "expression": {"type": "string", "description": "Mathematical expression"}
                            },
                            "required": ["expression"]
                        }
                    },
                    {
                        "name": "get_weather",
                        "description": "Get weather information",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "location": {"type": "string", "description": "Location name"}
                            },
                            "required": ["location"]
                        }
                    }
                ]
            
            # Stream response
            stream = await self.anthropic_provider.client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=messages,
                tools=tools,
                stream=True
            )
            
            accumulated_content = ""
            
            async for chunk in stream:
                if chunk.type == "content_block_start":
                    if chunk.content_block.type == "text":
                        # Text content starting
                        pass
                    elif chunk.content_block.type == "tool_use":
                        # Tool use starting
                        yield StreamChunk(
                            type=StreamChunkType.TOOL_CALL,
                            tool_calls=[{
                                "id": chunk.content_block.id,
                                "name": chunk.content_block.name,
                                "arguments": chunk.content_block.input
                            }]
                        )
                
                elif chunk.type == "content_block_delta":
                    if chunk.delta.type == "text_delta":
                        delta_content = chunk.delta.text
                        accumulated_content += delta_content
                        
                        yield StreamChunk(
                            type=StreamChunkType.CONTENT,
                            delta=delta_content,
                            content=accumulated_content
                        )
                
                elif chunk.type == "message_stop":
                    yield StreamChunk(
                        type=StreamChunkType.COMPLETE,
                        finish_reason="stop",
                        metadata={"total_content_length": len(accumulated_content)}
                    )
                    break
                    
        except Exception as e:
            logger.error("Anthropic streaming failed", error=str(e))
            yield StreamChunk(
                type=StreamChunkType.ERROR,
                content=f"Anthropic streaming failed: {str(e)}"
            )
    
    async def stream_multimodal_response(
        self,
        prompt: str,
        files: List[Dict[str, Any]] = None,
        model: str = "gpt-4-vision-preview"
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream multimodal response with images and audio."""
        
        try:
            yield StreamChunk(
                type=StreamChunkType.METADATA,
                metadata={
                    "multimodal": True,
                    "files_count": len(files) if files else 0,
                    "model": model
                }
            )
            
            # Process files if provided
            if files:
                for i, file_info in enumerate(files):
                    file_type = file_info.get("type", "").lower()
                    
                    if file_type.startswith("image/"):
                        yield StreamChunk(
                            type=StreamChunkType.IMAGE,
                            metadata={
                                "file_index": i,
                                "file_name": file_info.get("name"),
                                "processing": "analyzing_image"
                            }
                        )
                        
                        # Simulate image processing
                        await asyncio.sleep(1)
                        
                        yield StreamChunk(
                            type=StreamChunkType.CONTENT,
                            content=f"Image {i+1} analysis: This appears to be {file_info.get('name', 'an image')} with visual content that would be analyzed by the vision model."
                        )
                    
                    elif file_type.startswith("audio/"):
                        yield StreamChunk(
                            type=StreamChunkType.AUDIO,
                            metadata={
                                "file_index": i,
                                "file_name": file_info.get("name"),
                                "processing": "transcribing_audio"
                            }
                        )
                        
                        # Simulate audio processing
                        await asyncio.sleep(2)
                        
                        yield StreamChunk(
                            type=StreamChunkType.CONTENT,
                            content=f"Audio {i+1} transcription: This would contain the transcribed text from {file_info.get('name', 'the audio file')}."
                        )
            
            # Stream text response
            request = StreamingRequest(
                prompt=prompt,
                model=model,
                include_reasoning=False,
                enable_tools=True
            )
            
            async for chunk in self._stream_openai_response(request):
                yield chunk
                
        except Exception as e:
            logger.error("Multimodal streaming failed", error=str(e))
            yield StreamChunk(
                type=StreamChunkType.ERROR,
                content=f"Multimodal streaming failed: {str(e)}"
            )
    
    def format_stream_for_sse(self, chunk: StreamChunk) -> str:
        """Format stream chunk for Server-Sent Events."""
        
        data = {
            "type": chunk.type,
            "timestamp": chunk.timestamp.isoformat()
        }
        
        if chunk.delta:
            data["delta"] = chunk.delta
        if chunk.content:
            data["content"] = chunk.content
        if chunk.reasoning:
            data["reasoning"] = chunk.reasoning
        if chunk.tool_calls:
            data["tool_calls"] = chunk.tool_calls
        if chunk.tool_results:
            data["tool_results"] = chunk.tool_results
        if chunk.multimodal_content:
            data["multimodal_content"] = chunk.multimodal_content
        if chunk.metadata:
            data["metadata"] = chunk.metadata
        if chunk.finish_reason:
            data["finish_reason"] = chunk.finish_reason
        
        return f"data: {json.dumps(data)}\n\n"

