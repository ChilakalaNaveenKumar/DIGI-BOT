"""
OpenAI Provider Service

Handles OpenAI API interactions with streaming support and error handling.
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, List, Optional, Any

import structlog
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from app.core.config import get_settings
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)
settings = get_settings()


class OpenAIProvider:
    """OpenAI API provider with streaming support."""
    
    def __init__(self):
        self.client = None
        self.name = "openai"
        self.models = {
            "gpt-5": {
                "name": "GPT-5",
                "context_length": 1000000,
                "max_output": 64000,
                "supports_tools": True,
                "supports_vision": True
            },
            "gpt-4o": {
                "name": "GPT-4o",
                "context_length": 128000,
                "max_output": 16000,
                "supports_tools": True,
                "supports_vision": True
            },
            "gpt-4o-mini": {
                "name": "GPT-4o Mini",
                "context_length": 128000,
                "max_output": 16000,
                "supports_tools": True,
                "supports_vision": False
            }
        }
    
    async def initialize(self):
        """Initialize the OpenAI client."""
        try:
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=60.0,
                max_retries=3
            )
            
            # Test the connection
            await self.health_check()
            
            logger.info("OpenAI provider initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize OpenAI provider", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="OPENAI_INIT_ERROR",
                message="Failed to initialize OpenAI provider"
            )
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.client:
            await self.client.close()
        logger.info("OpenAI provider cleaned up")
    
    async def health_check(self) -> bool:
        """Check if the provider is healthy."""
        try:
            if not self.client:
                return False
            
            # Simple test request
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return bool(response.choices)
            
        except Exception as e:
            logger.error("OpenAI health check failed", error=str(e))
            return False
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> ChatCompletion:
        """Generate a non-streaming completion."""
        
        if not self.client:
            raise DigiSetuException(
                status_code=500,
                error_code="OPENAI_NOT_INITIALIZED",
                message="OpenAI provider not initialized"
            )
        
        try:
            # Validate model
            if model not in self.models:
                model = "gpt-4o"  # Fallback
            
            # Prepare request parameters
            request_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                **kwargs
            }
            
            # GPT-5 uses max_completion_tokens instead of max_tokens
            if model == "gpt-5":
                request_params["max_completion_tokens"] = max_tokens or self.models[model]["max_output"]
            else:
                request_params["max_tokens"] = max_tokens or self.models[model]["max_output"]
            
            # Add tools if provided and supported
            if tools and self.models[model]["supports_tools"]:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            response = await self.client.chat.completions.create(**request_params)
            
            logger.info(
                "OpenAI completion generated",
                model=model,
                tokens_used=response.usage.total_tokens if response.usage else 0
            )
            
            return response
            
        except Exception as e:
            logger.error("OpenAI completion failed", model=model, error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="OPENAI_COMPLETION_ERROR",
                message=f"OpenAI completion failed: {str(e)}"
            )
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate a streaming completion."""
        
        if not self.client:
            raise DigiSetuException(
                status_code=500,
                error_code="OPENAI_NOT_INITIALIZED",
                message="OpenAI provider not initialized"
            )
        
        try:
            # Validate model
            if model not in self.models:
                model = "gpt-4o"  # Fallback
            
            # Prepare request parameters
            request_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": True,
                **kwargs
            }
            
            # GPT-5 uses max_completion_tokens instead of max_tokens
            if model == "gpt-5":
                request_params["max_completion_tokens"] = max_tokens or self.models[model]["max_output"]
            else:
                request_params["max_tokens"] = max_tokens or self.models[model]["max_output"]
            
            # Add tools if provided and supported
            if tools and self.models[model]["supports_tools"]:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            stream = await self.client.chat.completions.create(**request_params)
            
            # Process streaming chunks
            tool_calls = {}
            content_buffer = ""
            
            async for chunk in stream:
                if not chunk.choices:
                    continue
                
                choice = chunk.choices[0]
                delta = choice.delta
                
                # Handle content
                if delta.content:
                    content_buffer += delta.content
                    yield {
                        "type": "content",
                        "content": delta.content,
                        "provider": self.name,
                        "model": model
                    }
                
                # Handle tool calls
                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        call_id = tool_call.id
                        
                        if call_id not in tool_calls:
                            tool_calls[call_id] = {
                                "id": call_id,
                                "type": "function",
                                "function": {
                                    "name": "",
                                    "arguments": ""
                                }
                            }
                        
                        if tool_call.function.name:
                            tool_calls[call_id]["function"]["name"] = tool_call.function.name
                        
                        if tool_call.function.arguments:
                            tool_calls[call_id]["function"]["arguments"] += tool_call.function.arguments
                
                # Handle finish reason
                if choice.finish_reason:
                    if choice.finish_reason == "tool_calls" and tool_calls:
                        for tool_call in tool_calls.values():
                            yield {
                                "type": "tool_call",
                                "tool_call": tool_call,
                                "provider": self.name,
                                "model": model
                            }
                    
                    yield {
                        "type": "finish",
                        "reason": choice.finish_reason,
                        "provider": self.name,
                        "model": model
                    }
            
            logger.info(
                "OpenAI streaming completion finished",
                model=model,
                content_length=len(content_buffer),
                tool_calls_count=len(tool_calls)
            )
            
        except Exception as e:
            logger.error("OpenAI streaming failed", model=model, error=str(e))
            yield {
                "type": "error",
                "error": str(e),
                "provider": self.name,
                "model": model
            }
    
    async def generate_reasoning(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate reasoning process for a request."""
        
        # Add reasoning instruction to messages
        reasoning_messages = messages + [{
            "role": "system",
            "content": (
                "Before providing your main response, show your reasoning process. "
                "Think step by step about how to approach this request. "
                "Structure your thinking clearly with numbered steps. "
                "Start each reasoning step with 'REASONING:' followed by the step content."
            )
        }]
        
        try:
            async for chunk in self.stream_completion(
                messages=reasoning_messages,
                model=model,
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for more consistent reasoning
                **kwargs
            ):
                if chunk.get("type") == "content":
                    content = chunk.get("content", "")
                    
                    # Check if this is reasoning content
                    if "REASONING:" in content or any(
                        keyword in content.lower() 
                        for keyword in ["step", "first", "next", "then", "therefore", "because"]
                    ):
                        yield {
                            "type": "reasoning",
                            "content": content.replace("REASONING:", "").strip(),
                            "provider": self.name,
                            "model": model
                        }
                    else:
                        yield chunk
                else:
                    yield chunk
                    
        except Exception as e:
            logger.error("OpenAI reasoning generation failed", error=str(e))
            yield {
                "type": "error",
                "error": str(e),
                "provider": self.name
            }
    
    async def execute_tool_call(
        self,
        tool_call: Dict[str, Any],
        context_messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Execute a tool call and return the result."""
        
        try:
            function_name = tool_call["function"]["name"]
            function_args = json.loads(tool_call["function"]["arguments"])
            
            # Tool execution logic would go here
            # For now, return a mock result
            result = {
                "tool_call_id": tool_call["id"],
                "output": f"Mock result for {function_name} with args: {function_args}",
                "success": True
            }
            
            logger.info(
                "Tool call executed",
                function_name=function_name,
                tool_call_id=tool_call["id"]
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Tool call execution failed",
                tool_call_id=tool_call.get("id"),
                error=str(e)
            )
            return {
                "tool_call_id": tool_call.get("id"),
                "output": f"Error executing tool: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        return self.models.get(model)
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return list(self.models.keys())
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimation: ~4 characters per token
        return len(text) // 4
