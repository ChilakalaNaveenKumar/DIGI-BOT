"""
Anthropic Provider Service

Handles Anthropic Claude API interactions with streaming support.
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, List, Optional, Any

import structlog
import httpx

from app.core.simple_config import get_settings
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)
settings = get_settings()


class AnthropicProvider:
    """Anthropic Claude API provider with streaming support."""
    
    def __init__(self):
        self.client = None
        self.name = "anthropic"
        self.models = {
            # Claude 4 Models with Extended Thinking - OFFICIAL API LIMITS
            "claude-opus-4-1-20250805": {
                "name": "Claude Opus 4.1 (Latest)",
                "context_length": 200000,  # 200K context (from API docs)
                "max_output": 80000,  # Safe limit: 80K + buffer for thinking budget
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
                "context_length": 200000,  # 200K context (from API docs)
                "max_output": 80000,  # Safe limit: 80K + buffer for thinking budget
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
            # Claude 3.7 with Extended Thinking - OFFICIAL API LIMITS
            "claude-3-7-sonnet-20250219": {
                "name": "Claude 3.7 Sonnet (2025)",
                "context_length": 200000,  # 200K context
                "max_output": 16000,  # Official API limit: 16K output tokens
                "supports_tools": True,
                "supports_vision": True,
                "supports_reasoning": True,
                "supports_thinking": True,
                "released": "2025-02-19",
                "rpm": 1000,
                "input_tpm": 40000,
                "output_tpm": 16000
            },
            # Legacy models for fallback
            "claude-3.5-sonnet": {
                "name": "Claude 3.5 Sonnet",
                "context_length": 200000,
                "max_output": 8000,
                "supports_tools": True,
                "supports_vision": True
            },
            "claude-3-5-sonnet-20241022": {
                "name": "Claude 3.5 Sonnet (Legacy)",
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
                    "model": "claude-sonnet-4-20250514",
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
                    # Convert content to proper block format (required by Anthropic)
                    content = msg["content"]
                    if isinstance(content, str):
                        content = [{"type": "text", "text": content}]
                    
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": content
                    })
            
            # Prepare request with full token limit
            model_max = self.models[model]["max_output"]
            # Use full max_tokens limit (removed artificial 8K cap)
            safe_max_tokens = max_tokens or model_max
            
            request_data = {
                "model": model,  # Use actual model parameter
                "max_tokens": safe_max_tokens,
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
        enable_reasoning: bool = False,
        reasoning_budget: int = 2000,
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
                    # Convert content to proper block format (required by Anthropic)
                    content = msg["content"]
                    if isinstance(content, str):
                        content = [{"type": "text", "text": content}]
                    
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": content
                    })
            
            # Prepare request
            request_data = {
                "model": model,  # Use actual model parameter, not hardcoded!
                "max_tokens": max_tokens or self.models[model]["max_output"],
                "messages": anthropic_messages,
                "stream": True
            }
            
            # Add web search tool for Claude 4 models
            if "claude-opus-4" in model or "claude-sonnet-4" in model or "claude-3-7-sonnet" in model:
                request_data["tools"] = [
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": 5
                    }
                ]
            
            # Add temperature only if NOT using thinking (thinking doesn't like extra params)
            if not enable_reasoning:
                request_data["temperature"] = temperature
            
            # Add extended thinking/reasoning if enabled (disabled by default)
            # Note: This is "thinking mode" - different from actual reasoning content
            if enable_reasoning:
                # Calculate optimal reasoning budget (your theory confirmed!)
                total_tokens = max_tokens or self.models.get(model, {}).get("max_output", 2000)
                
                # Use the reasoning budget directly without complex calculations
                # The API handles the token allocation internally
                reasoning_budget_calculated = min(reasoning_budget, total_tokens // 4)  # Max 25% for thinking
                
                logger.info(f"Token allocation - Total: {total_tokens}, Reasoning: {reasoning_budget_calculated}")
                
                request_data["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": reasoning_budget_calculated  # Correct format
                }
            
            if system_message:
                request_data["system"] = system_message
            
            if tools and self.models[model]["supports_tools"]:
                # Merge with existing tools (like web search) instead of overriding
                existing_tools = request_data.get("tools", [])
                request_data["tools"] = existing_tools + tools
            
            # Log the actual request for debugging
            logger.info(f"Anthropic request - Model: {model}, Max tokens: {request_data.get('max_tokens')}, Thinking: {request_data.get('thinking', {}).get('budget_tokens', 'disabled')}")
            
            # Start streaming
            async with self.client.stream("POST", "/messages", json=request_data) as response:
                response.raise_for_status()
                
                content_buffer = ""
                tool_calls_detected = []
                assistant_content_blocks = []
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            
                            # Handle thinking/reasoning content blocks (Claude 4 extended thinking)
                            if data.get("type") == "content_block_start":
                                block = data.get("content_block", {})
                                if block.get("type") == "thinking":
                                    yield {
                                        "type": "reasoning",
                                        "content": "",
                                        "provider": self.name,
                                        "model": model,
                                        "metadata": {"block_start": True, "thinking_block": True}
                                    }
                                elif block.get("type") == "server_tool_use":
                                    tool_name = block.get("name", "unknown")
                                    yield {
                                        "type": "activity",
                                        "content": f"Using {tool_name} tool...",
                                        "provider": self.name,
                                        "model": model,
                                        "metadata": {"tool": tool_name, "tool_start": True}
                                    }
                                elif block.get("type") == "tool_use":
                                    # Client-side tool call (like chart tools) - just store for now
                                    tool_name = block.get("name", "unknown")
                                    tool_id = block.get("id", "unknown")
                                    tool_input = block.get("input", {})
                                    
                                    # Store partial tool call - input might be completed later
                                    tool_calls_detected.append({
                                        "name": tool_name,
                                        "id": tool_id,
                                        "input": tool_input
                                    })
                                    
                                    logger.info(f"Tool call started: {tool_name} (ID: {tool_id}) with input: {tool_input}")
                                    
                                    # Yield tool call info but don't trigger workflow yet
                                    yield {
                                        "type": "tool_call",
                                        "tool_name": tool_name,
                                        "tool_id": tool_id,
                                        "tool_input": tool_input,
                                        "provider": self.name,
                                        "model": model,
                                        "metadata": {"tool_call_start": True}
                                    }
                            
                            elif data.get("type") == "content_block_stop":
                                # Content block finished - check if it was a tool_use block
                                block = data.get("content_block", {})
                                if block.get("type") == "tool_use" and tool_calls_detected:
                                    # Update the tool call with final input
                                    final_input = block.get("input", {})
                                    if tool_calls_detected:
                                        tool_calls_detected[-1]["input"] = final_input
                                        logger.info(f"Tool call completed with final input: {final_input}")
                                    
                                    # Now trigger the tool use workflow
                                    # Add text content if any exists
                                    if content_buffer.strip():
                                        assistant_content_blocks.append({
                                            "type": "text",
                                            "text": content_buffer
                                        })
                                    
                                    # Add tool calls to content blocks
                                    for tc in tool_calls_detected:
                                        assistant_content_blocks.append({
                                            "type": "tool_use",
                                            "id": tc["id"],
                                            "name": tc["name"],
                                            "input": tc["input"]
                                        })
                                    
                                    # Trigger tool use workflow
                                    yield {
                                        "type": "tool_use_required",
                                        "reason": "tool_use",
                                        "provider": self.name,
                                        "model": model,
                                        "tool_calls": tool_calls_detected,
                                        "assistant_content": assistant_content_blocks
                                    }
                                    return  # Exit streaming loop to let router handle tool processing
                            
                            elif data.get("type") == "content_block_delta":
                                delta = data.get("delta", {})
                                
                                # Handle thinking_delta events (Claude 4 extended thinking)
                                if delta.get("type") == "thinking_delta":
                                    thinking_content = delta.get("thinking", "")
                                    if thinking_content:
                                        yield {
                                            "type": "reasoning",
                                            "content": thinking_content,
                                            "provider": self.name,
                                            "model": model,
                                            "metadata": {"thinking_delta": True}
                                        }
                                
                                # Handle signature_delta events (thinking encryption)
                                elif delta.get("type") == "signature_delta":
                                    # Store signature but don't yield (used for verification)
                                    pass
                                
                                # Handle tool input delta events
                                elif delta.get("type") == "input_json_delta":
                                    # Tool input is being streamed - we need to wait for content_block_stop
                                    logger.info(f"Tool input delta received: {delta}")
                                    pass
                                
                                # Handle regular text_delta events
                                elif delta.get("type") == "text_delta":
                                    text_content = delta.get("text", "")
                                    if text_content:
                                        content_buffer += text_content
                                        yield {
                                            "type": "content",
                                            "content": text_content,
                                            "provider": self.name,
                                            "model": model
                                        }
                                
                                # Handle server tool use results
                                elif delta.get("type") == "server_tool_use_delta":
                                    if "result" in delta:
                                        tool_result = delta.get("result", "")
                                        if tool_result:
                                            yield {
                                                "type": "tool_output",
                                                "content": tool_result,
                                                "provider": self.name,
                                                "model": model,
                                                "metadata": {"tool_result": True}
                                            }
                                
                                # Fallback for legacy delta format
                                elif delta.get("text"):
                                    content_buffer += delta["text"]
                                    yield {
                                        "type": "content",
                                        "content": delta["text"],
                                        "provider": self.name,
                                        "model": model
                                    }
                            
                            elif data.get("type") == "message_stop":
                                # Log why the message stopped
                                stop_reason = data.get("stop_reason", "unknown")
                                usage = data.get("usage", {})
                                logger.info(f"Message stopped - Reason: {stop_reason}, Content length: {len(content_buffer)}, Usage: {usage}, Full data: {json.dumps(data)}")
                                
                                # Handle different stop reasons according to 2025 Anthropic docs
                                # If we detected tool calls during streaming, treat as tool_use regardless of stop_reason
                                if stop_reason == "tool_use" or len(content_buffer) == 0:
                                    logger.info("AI made tool call - need to process and continue")
                                    yield {
                                        "type": "tool_use_required",
                                        "reason": "tool_use",
                                        "provider": self.name,
                                        "model": model,
                                        "usage": usage
                                    }
                                elif stop_reason == "max_tokens":
                                    logger.warning("Response truncated due to token limit")
                                    yield {
                                        "type": "truncated",
                                        "reason": stop_reason,
                                        "provider": self.name,
                                        "model": model,
                                        "usage": usage
                                    }
                                else:
                                    # end_turn, pause_turn, etc.
                                    yield {
                                        "type": "finish",
                                        "reason": stop_reason,
                                        "provider": self.name,
                                        "model": model,
                                        "usage": usage
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
                max_tokens=reasoning_budget,  # Use the actual reasoning budget
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
