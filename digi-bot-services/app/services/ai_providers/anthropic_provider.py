"""
Simplified Anthropic Provider Service

Handles Anthropic Claude API interactions with streaming support.
Focused on simple query-response with vector context integration.
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
    """Simplified Anthropic Claude API provider with streaming support."""
    
    def __init__(self):
        self.client = None
        self.name = "anthropic"
        self.models = {
            "claude-opus-4-1-20250805": {
                "name": "Claude Opus 4.1 (Latest)",
                "context_length": 200000,
                "max_output": 32000,
                "supports_tools": True,
                "supports_vision": True,
                "supports_reasoning": True,
                "supports_thinking": True,
                "supports_code_execution": True,
                "released": "2025-08-05",
                "rpm": 1000,
                "input_tpm": 450000,
                "output_tpm": 90000
            },
            "claude-sonnet-4-20250514": {
                "name": "Claude Sonnet 4",
                "context_length": 200000,
                "max_output": 64000,
                "supports_tools": True,
                "supports_vision": True,
                "supports_reasoning": True,
                "supports_thinking": True,
                "supports_code_execution": True,
                "released": "2025-05-14",
                "rpm": 1000,
                "input_tpm": 450000,
                "output_tpm": 90000
            },
            "claude-3-5-sonnet-20241022": {
                "name": "Claude 3.5 Sonnet (Current)",
                "context_length": 200000,
                "max_output": 8000,
                "supports_tools": True,
                "supports_vision": True,
                "supports_reasoning": False,
                "supports_thinking": False,  # Confirmed: does not support thinking
                "released": "2024-10-22",
                "rpm": 1000,
                "input_tpm": 40000,
                "output_tpm": 8000
            }
        }
        self.default_model = "claude-sonnet-4-20250514"
    
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
            
            response = await self.client.post(
                "/messages",
                json={
                    "model": self.default_model,
                    "max_tokens": 5,
                    "messages": [{"role": "user", "content": "Hello"}]
                }
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error("Anthropic health check failed", error=str(e))
            return False
    
    def _prepare_messages(self, messages: List[Dict[str, str]]) -> tuple[Optional[str], List[Dict[str, Any]]]:
        """Convert messages to Anthropic format and extract system message."""
        anthropic_messages = []
        system_message = None
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                # Convert content to proper block format
                content = msg["content"]
                if isinstance(content, str):
                    content = [{"type": "text", "text": content}]
                
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": content
                })
        
        return system_message, anthropic_messages
    
    def _get_web_search_tool(self) -> Dict[str, Any]:
        """Get web search tool configuration."""
        return {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5
        }
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.5,
        enable_thinking: bool = False,
        thinking_budget: int = 5000,
        enable_web_search: bool = True,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate a streaming completion with optional thinking mode and web search."""
        
        if not self.client:
            raise DigiSetuException(
                status_code=500,
                error_code="ANTHROPIC_NOT_INITIALIZED",
                message="Anthropic provider not initialized"
            )
        
        # Use default model if not specified
        if not model or model not in self.models:
            model = self.default_model
        
        try:
            # Prepare messages
            system_message, anthropic_messages = self._prepare_messages(messages)
            
            # Prepare request
            request_data = {
                "model": model,
                "max_tokens": max_tokens or self.models[model]["max_output"],
                "messages": anthropic_messages,
                "stream": True
            }
            
            # Add system message if present
            if system_message:
                request_data["system"] = system_message
            
            # Add web search tool for supported models
            if enable_web_search and ("claude-opus-4" in model or "claude-sonnet-4" in model or "claude-3-7-sonnet" in model):
                request_data["tools"] = [self._get_web_search_tool()]
            
            # Add thinking mode if enabled
            if enable_thinking:
                # Check if model supports thinking mode
                model_info = self.models.get(model, {})
                if not model_info.get("supports_thinking", False):
                    logger.warning(
                        "Model does not support thinking mode, disabling",
                        model=model,
                        supports_thinking=model_info.get("supports_thinking", False)
                    )
                    enable_thinking = False
                    request_data["temperature"] = temperature
                else:
                    # Ensure minimum thinking budget (Anthropic requires >= 1024)
                    min_thinking_budget = 1024
                    if thinking_budget < min_thinking_budget:
                        thinking_budget = min_thinking_budget
                        logger.warning(
                            "Thinking budget too low, using minimum",
                            requested=thinking_budget,
                            minimum=min_thinking_budget
                        )
                
                    # Ensure max_tokens is greater than thinking_budget
                    current_max_tokens = request_data["max_tokens"]
                    if current_max_tokens <= thinking_budget:
                        # Set max_tokens to at least thinking_budget + 1024 for response
                        request_data["max_tokens"] = thinking_budget + 1024
                        logger.warning(
                            "max_tokens too low for thinking mode, increased",
                            original_max_tokens=current_max_tokens,
                            thinking_budget=thinking_budget,
                            new_max_tokens=request_data["max_tokens"]
                        )
                    
                    request_data["thinking"] = {
                        "type": "enabled",
                        "budget_tokens": thinking_budget
                    }
                    # Don't add temperature when using thinking mode
            
            if not enable_thinking:
                request_data["temperature"] = temperature
            
            logger.info(
                "Starting Anthropic stream",
                model=model,
                max_tokens=request_data["max_tokens"],
                thinking_enabled=enable_thinking,
                thinking_budget=thinking_budget if enable_thinking else 0,
                web_search_enabled=enable_web_search
            )
            
            # Debug: Log the full request payload (excluding sensitive data)
            debug_request = request_data.copy()
            if "messages" in debug_request:
                debug_request["messages"] = f"[{len(debug_request['messages'])} messages]"
            logger.info("Anthropic request payload", request_data=debug_request)
            
            # Start streaming - just pass through raw Anthropic response
            async with self.client.stream("POST", "/messages", json=request_data) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            # Just yield the raw Anthropic data
                            yield data
                        except json.JSONDecodeError:
                            continue
            
            logger.info(
                "Anthropic streaming completed",
                model=model
            )
            
        except Exception as e:
            # Get detailed error information for HTTP errors
            error_details = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    # Try to get the response body for more details
                    error_body = await e.response.aread() if hasattr(e.response, 'aread') else e.response.text
                    if isinstance(error_body, bytes):
                        error_body = error_body.decode('utf-8')
                    error_details = f"{str(e)} - Response: {error_body}"
                except:
                    # If we can't read the response, just use the original error
                    pass
            
            logger.error("Anthropic streaming failed", 
                        model=model, 
                        error=error_details,
                        error_type=type(e).__name__)
            yield {
                "type": "error",
                "error": error_details,
                "provider": self.name,
                "model": model
            }
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a non-streaming completion."""
        
        if not self.client:
            raise DigiSetuException(
                status_code=500,
                error_code="ANTHROPIC_NOT_INITIALIZED",
                message="Anthropic provider not initialized"
            )
        
        # Use default model if not specified
        if not model or model not in self.models:
            model = self.default_model
        
        try:
            # Prepare messages
            system_message, anthropic_messages = self._prepare_messages(messages)
            
            # Prepare request
            request_data = {
                "model": model,
                "max_tokens": max_tokens or self.models[model]["max_output"],
                "temperature": temperature,
                "messages": anthropic_messages
            }
            
            if system_message:
                request_data["system"] = system_message
            
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
    
    def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model."""
        return self.models.get(model)
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return list(self.models.keys())
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimation: ~4 characters per token for Claude
        return len(text) // 4