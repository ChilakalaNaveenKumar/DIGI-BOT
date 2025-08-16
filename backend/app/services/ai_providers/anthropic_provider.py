"""
Anthropic Provider Service

Handles Anthropic Claude API interactions with streaming support.
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


class AnthropicProvider:
    """Anthropic Claude API provider with streaming support."""
    
    def __init__(self):
        self.client = None
        self.name = "anthropic"
        self.models = {
            "claude-4": {
                "name": "Claude-4",
                "context_length": 200000,
                "max_output": 64000,
                "supports_tools": True,
                "supports_vision": True
            },
            "claude-3.5-sonnet": {
                "name": "Claude-3.5 Sonnet",
                "context_length": 200000,
                "max_output": 8000,
                "supports_tools": True,
                "supports_vision": True
            },
            "claude-3.7-sonnet": {
                "name": "Claude-3.7 Sonnet",
                "context_length": 200000,
                "max_output": 8000,
                "supports_tools": True,
                "supports_vision": True
            }
        }
    
    async def initialize(self):
        """Initialize the Anthropic client."""
        try:
            self.client = httpx.AsyncClient(
                base_url="https://api.anthropic.com/v1",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                timeout=60.0
            )
            
            # Test the connection
            await self.health_check()
            
            logger.info("Anthropic provider initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Anthropic provider", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="ANTHROPIC_INIT_ERROR",
                message="Failed to initialize Anthropic provider"
            )
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.client:
            await self.client.aclose()
        logger.info("Anthropic provider cleaned up")
    
    async def health_check(self) -> bool:
        """Check if the provider is healthy."""
        try:
            if not self.client:
                return False
            
            # Simple test request
            response = await self.client.post(
                "/messages",
                json={
                    "model": "claude-3.5-sonnet-20241022",
                    "max_tokens": 5,
                    "messages": [{"role": "user", "content": "Hello"}]
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error("Anthropic health check failed", error=str(e))
            return False
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3.5-sonnet",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a non-streaming completion."""
        
        if not self.client:
            raise DigiSetuException(
                status_code=500,
                error_code="ANTHROPIC_NOT_INITIALIZED",
                message="Anthropic provider not initialized"
            )
        
        try:
            # Validate model
            if model not in self.models:
                model = "claude-3.5-sonnet"  # Fallback
            
            # Convert to Anthropic format
            anthropic_messages = []
            system_message = None
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Prepare request
            request_data = {
                "model": "claude-3-5-sonnet-20241022",  # Use actual model name
                "max_tokens": max_tokens or self.models[model]["max_output"],
                "temperature": temperature,
                "messages": anthropic_messages
            }
            
            if system_message:
                request_data["system"] = system_message
            
            if tools and self.models[model]["supports_tools"]:
                request_data["tools"] = tools
            
            response = await self.client.post("/messages", json=request_data)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(
                "Anthropic completion generated",
                model=model,
                tokens_used=result.get("usage", {}).get("output_tokens", 0)
            )
            
            return result
            
        except Exception as e:
            logger.error("Anthropic completion failed", model=model, error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="ANTHROPIC_COMPLETION_ERROR",
                message=f"Anthropic completion failed: {str(e)}"
            )
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3.5-sonnet",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate a streaming completion."""
        
        if not self.client:
            raise DigiSetuException(
                status_code=500,
                error_code="ANTHROPIC_NOT_INITIALIZED",
                message="Anthropic provider not initialized"
            )
        
        try:
            # Validate model
            if model not in self.models:
                model = "claude-3.5-sonnet"  # Fallback
            
            # Convert to Anthropic format
            anthropic_messages = []
            system_message = None
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Prepare request
            request_data = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": max_tokens or self.models[model]["max_output"],
                "temperature": temperature,
                "messages": anthropic_messages,
                "stream": True
            }
            
            if system_message:
                request_data["system"] = system_message
            
            if tools and self.models[model]["supports_tools"]:
                request_data["tools"] = tools
            
            # Start streaming
            async with self.client.stream("POST", "/messages", json=request_data) as response:
                response.raise_for_status()
                
                content_buffer = ""
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            
                            if data.get("type") == "content_block_delta":
                                delta = data.get("delta", {})
                                if delta.get("text"):
                                    content_buffer += delta["text"]
                                    yield {
                                        "type": "content",
                                        "content": delta["text"],
                                        "provider": self.name,
                                        "model": model
                                    }
                            
                            elif data.get("type") == "message_stop":
                                yield {
                                    "type": "finish",
                                    "reason": "stop",
                                    "provider": self.name,
                                    "model": model
                                }
                                
                        except json.JSONDecodeError:
                            continue
            
            logger.info(
                "Anthropic streaming completion finished",
                model=model,
                content_length=len(content_buffer)
            )
            
        except Exception as e:
            logger.error("Anthropic streaming failed", model=model, error=str(e))
            yield {
                "type": "error",
                "error": str(e),
                "provider": self.name,
                "model": model
            }
    
    async def generate_reasoning(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3.5-sonnet",
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate reasoning process for a request."""
        
        # Add reasoning instruction to messages
        reasoning_messages = messages + [{
            "role": "user",
            "content": (
                "Before providing your main response, please think through this step by step. "
                "Show your reasoning process clearly. Use <thinking> tags to wrap your "
                "step-by-step analysis before giving your final answer."
            )
        }]
        
        try:
            async for chunk in self.stream_completion(
                messages=reasoning_messages,
                model=model,
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for more consistent reasoning
                **kwargs
            ):
                if chunk.get("type") == "content":
                    content = chunk.get("content", "")
                    
                    # Check if this is reasoning content (inside thinking tags)
                    if "<thinking>" in content or "</thinking>" in content:
                        yield {
                            "type": "reasoning",
                            "content": content.replace("<thinking>", "").replace("</thinking>", "").strip(),
                            "provider": self.name,
                            "model": model
                        }
                    else:
                        yield chunk
                else:
                    yield chunk
                    
        except Exception as e:
            logger.error("Anthropic reasoning generation failed", error=str(e))
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
        # Rough estimation: ~3.5 characters per token for Claude
        return len(text) // 4
