"""
Grok Provider Service

Handles xAI Grok API interactions with streaming support.
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, List, Optional, Any

import structlog
import httpx

from app.core.config import get_settings
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)
settings = get_settings()


class GrokProvider:
    """xAI Grok API provider with streaming support."""
    
    def __init__(self):
        self.client = None
        self.name = "grok"
        self.models = {
            # 2025 Latest Grok 3 Model - OFFICIAL API LIMITS
            "grok-3": {
                "name": "Grok 3 (2025)",
                "context_length": 128000,  # Official: 128K context window
                "max_output": 128000,  # Official API limit: 128K output tokens
                "supports_tools": True,
                "supports_vision": True,
                "supports_search": True,
                "supports_reasoning": True,
                "live_search": True,
                "platform": "X/Twitter integrated",
                "capabilities": ["think_mode", "deepsearch", "big_brain_mode"],
                "best_for": "real-time info, reasoning, academic/technical tasks",
                "released": "2025-02-17"
            },
            # Legacy/Future models
            "grok-4": {
                "name": "Grok-4 (Future)",
                "context_length": 256000,
                "max_output": 32000,
                "supports_tools": True,
                "supports_vision": True,
                "supports_search": True,
                "live_search": True,
                "platform": "X/Twitter integrated",
                "best_for": "real-time info, academic/technical tasks",
                "vs_gpt5": "better at academic tasks, weaker at creative/emotional"
            },
            "grok-2-1212": {
                "name": "Grok-2 (Legacy)",
                "context_length": 256000,
                "max_output": 32000,
                "supports_tools": True,
                "supports_vision": True,
                "supports_search": True,
                "best_for": "fallback if newer models unavailable"
            }
        }
    
    async def initialize(self):
        """Initialize the Grok client."""
        try:
            self.client = httpx.AsyncClient(
                base_url="https://api.x.ai/v1",
                headers={
                    "Authorization": f"Bearer {settings.GROK_API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )
            
            # Test the connection
            await self.health_check()
            
            logger.info("Grok provider initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Grok provider", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="GROK_INIT_ERROR",
                message="Failed to initialize Grok provider"
            )
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.client:
            await self.client.aclose()
        logger.info("Grok provider cleaned up")
    
    async def health_check(self) -> bool:
        """Check if the provider is healthy."""
        try:
            if not self.client:
                return False
            
            # Simple test request
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": "grok-beta",
                    "max_tokens": 5,
                    "messages": [{"role": "user", "content": "Hello"}]
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error("Grok health check failed", error=str(e))
            return False
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "grok-4",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None,
        enable_search: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a non-streaming completion."""
        
        if not self.client:
            raise DigiSetuException(
                status_code=500,
                error_code="GROK_NOT_INITIALIZED",
                message="Grok provider not initialized"
            )
        
        try:
            # Validate model
            if model not in self.models:
                model = "grok-4"  # Fallback
            
            # Prepare request parameters
            request_params = {
                "model": "grok-beta",  # Use actual model name
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or self.models[model]["max_output"],
                **kwargs
            }
            
            # Add tools if provided and supported
            if tools and self.models[model]["supports_tools"]:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            # Enable real-time search if supported
            if enable_search and self.models[model]["supports_search"]:
                request_params["stream"] = False  # Search works better without streaming
            
            response = await self.client.post("/chat/completions", json=request_params)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(
                "Grok completion generated",
                model=model,
                tokens_used=result.get("usage", {}).get("total_tokens", 0)
            )
            
            return result
            
        except Exception as e:
            logger.error("Grok completion failed", model=model, error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="GROK_COMPLETION_ERROR",
                message=f"Grok completion failed: {str(e)}"
            )
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "grok-4",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None,
        enable_search: bool = True,
        enable_thinking: bool = False,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate a streaming completion."""
        
        if not self.client:
            raise DigiSetuException(
                status_code=500,
                error_code="GROK_NOT_INITIALIZED",
                message="Grok provider not initialized"
            )
        
        try:
            # Validate model
            if model not in self.models:
                model = "grok-4"  # Fallback
            
            # Prepare request parameters
            request_params = {
                "model": "grok-beta",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or self.models[model]["max_output"],
                "stream": True,
                **kwargs
            }
            
            # Add Think mode for Grok 3 (2025 reasoning feature)
            if enable_thinking and model == "grok-3":
                request_params["think_mode"] = True
            
            # Add tools if provided and supported
            if tools and self.models[model]["supports_tools"]:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            # Start streaming
            async with self.client.stream("POST", "/chat/completions", json=request_params) as response:
                response.raise_for_status()
                
                content_buffer = ""
                tool_calls = {}
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line == "data: [DONE]":
                            break
                            
                        try:
                            data = json.loads(line[6:])
                            
                            if not data.get("choices"):
                                continue
                            
                            choice = data["choices"][0]
                            delta = choice.get("delta", {})
                            
                            # Handle content
                            if delta.get("content"):
                                content_buffer += delta["content"]
                                yield {
                                    "type": "content",
                                    "content": delta["content"],
                                    "provider": self.name,
                                    "model": model
                                }
                            
                            # Handle tool calls
                            if delta.get("tool_calls"):
                                for tool_call in delta["tool_calls"]:
                                    call_id = tool_call.get("id")
                                    if call_id:
                                        if call_id not in tool_calls:
                                            tool_calls[call_id] = {
                                                "id": call_id,
                                                "type": "function",
                                                "function": {
                                                    "name": "",
                                                    "arguments": ""
                                                }
                                            }
                                        
                                        if tool_call.get("function", {}).get("name"):
                                            tool_calls[call_id]["function"]["name"] = tool_call["function"]["name"]
                                        
                                        if tool_call.get("function", {}).get("arguments"):
                                            tool_calls[call_id]["function"]["arguments"] += tool_call["function"]["arguments"]
                            
                            # Handle finish reason
                            if choice.get("finish_reason"):
                                if choice["finish_reason"] == "tool_calls" and tool_calls:
                                    for tool_call in tool_calls.values():
                                        yield {
                                            "type": "tool_call",
                                            "tool_call": tool_call,
                                            "provider": self.name,
                                            "model": model
                                        }
                                
                                yield {
                                    "type": "finish",
                                    "reason": choice["finish_reason"],
                                    "provider": self.name,
                                    "model": model
                                }
                                
                        except json.JSONDecodeError:
                            continue
            
            logger.info(
                "Grok streaming completion finished",
                model=model,
                content_length=len(content_buffer),
                tool_calls_count=len(tool_calls)
            )
            
        except Exception as e:
            logger.error("Grok streaming failed", model=model, error=str(e))
            yield {
                "type": "error",
                "error": str(e),
                "provider": self.name,
                "model": model
            }
    
    async def search_and_respond(
        self,
        query: str,
        messages: List[Dict[str, str]],
        model: str = "grok-4",
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Perform real-time search and generate response."""
        
        # Add search context to the query
        search_enhanced_messages = messages + [{
            "role": "user",
            "content": f"Please search for current information about: {query}. "
                      f"Use real-time data and provide up-to-date information."
        }]
        
        try:
            async for chunk in self.stream_completion(
                messages=search_enhanced_messages,
                model=model,
                enable_search=True,
                **kwargs
            ):
                # Add search indicator for search-enhanced responses
                if chunk.get("type") == "content":
                    chunk["search_enhanced"] = True
                
                yield chunk
                
        except Exception as e:
            logger.error("Grok search and respond failed", error=str(e))
            yield {
                "type": "error",
                "error": str(e),
                "provider": self.name
            }
    
    async def generate_reasoning(
        self,
        messages: List[Dict[str, str]],
        model: str = "grok-4",
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate reasoning process for a request."""
        
        # Add reasoning instruction to messages
        reasoning_messages = messages + [{
            "role": "system",
            "content": (
                "Think step by step about this request. Show your reasoning process "
                "clearly before providing your final answer. Break down your thinking "
                "into logical steps."
            )
        }]
        
        try:
            async for chunk in self.stream_completion(
                messages=reasoning_messages,
                model=model,
                max_tokens=1500,
                temperature=0.3,  # Lower temperature for more consistent reasoning
                **kwargs
            ):
                if chunk.get("type") == "content":
                    content = chunk.get("content", "")
                    
                    # Check if this is reasoning content
                    if any(keyword in content.lower() for keyword in [
                        "step", "first", "next", "then", "therefore", "because", 
                        "reasoning", "analysis", "consider"
                    ]):
                        yield {
                            "type": "reasoning",
                            "content": content,
                            "provider": self.name,
                            "model": model
                        }
                    else:
                        yield chunk
                else:
                    yield chunk
                    
        except Exception as e:
            logger.error("Grok reasoning generation failed", error=str(e))
            yield {
                "type": "error",
                "error": str(e),
                "provider": self.name
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
