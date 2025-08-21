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
            # 2025 Latest Models with Reasoning - OFFICIAL API LIMITS
            "gpt-5": {
                "name": "GPT-5 (2025)",
                "context_length": 400000,  # Official: 400K context window
                "max_output": 128000,  # Official API limit: 128K output tokens
                "supports_tools": True,
                "supports_vision": True,
                "supports_reasoning": True,
                "multimodal": "text+vision+audio",
                "best_for": "coding, agentic tasks, complex reasoning",
                "released": "2025"
            },
            "o3": {
                "name": "o3 Reasoning (2025)",
                "context_length": 200000,  # Official: 200K context window
                "max_output": 100000,  # Official API limit: 100K output tokens
                "supports_tools": False,
                "supports_vision": True,
                "supports_reasoning": True,
                "best_for": "complex reasoning, mathematics, coding",
                "released": "2025-04-16"
            },
            "o3-mini": {
                "name": "o3-mini Reasoning (2025)",
                "context_length": 128000,
                "max_output": 65536,  # Use full API limit - let AI decide
                "supports_tools": False,
                "supports_vision": False,
                "supports_reasoning": True,
                "best_for": "fast reasoning, STEM problems",
                "released": "2025-01-31"
            },
            # Legacy models for fallback
            "gpt-4o": {
                "name": "GPT-4o",
                "context_length": 128000,
                "max_output": 16000,  # Use full API limit - let AI decide
                "supports_tools": True,
                "supports_vision": True,
                "best_for": "general multimodal tasks"
            },
            "o1-preview": {
                "name": "o1-preview Reasoning (Legacy)",
                "context_length": 128000,
                "max_output": 32768,  # Use actual API limit
                "supports_tools": False,
                "supports_vision": False,
                "supports_reasoning": True,
                "best_for": "complex reasoning, mathematics, coding"
            },
            "o1-mini": {
                "name": "o1-mini Reasoning (Legacy)",
                "context_length": 128000,
                "max_output": 65536,  # Use actual API limit
                "supports_tools": False,
                "supports_vision": False,
                "supports_reasoning": True,
                "best_for": "fast reasoning, STEM problems"
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
            
            # GPT-5 uses max_completion_tokens instead of max_tokens (64K max output)
            if model in ["gpt-5", "gpt-5-mini", "gpt-5-nano"]:
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
        reasoning_effort: Optional[str] = None,
        reasoning_summary: Optional[str] = None,
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
            
            # GPT-5 uses max_completion_tokens instead of max_tokens (64K max output)
            if model in ["gpt-5", "gpt-5-mini", "gpt-5-nano"]:
                request_params["max_completion_tokens"] = max_tokens or self.models[model]["max_output"]
            else:
                request_params["max_tokens"] = max_tokens or self.models[model]["max_output"]
            
            # Add reasoning_effort parameter for 2025 reasoning models
            if reasoning_effort and model in ["gpt-5", "o3", "o3-mini", "o1-preview", "o1-mini"]:
                request_params["reasoning_effort"] = reasoning_effort
            
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
                
                # Handle reasoning content (for o1/o3 models)
                if hasattr(delta, 'reasoning') and delta.reasoning:
                    yield {
                        "type": "reasoning",
                        "content": delta.reasoning,
                        "provider": self.name,
                        "model": model
                    }
                
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
    
    async def segment_content_blocks(
        self,
        content: str,
        context: str = "Content analysis"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Use GPT-4o Mini for fast, cheap content block segmentation.
        This is Step 1 of the two-step analysis pipeline.
        """
        import json  # Import at function start to avoid scope issues
        
        if not self.client:
            raise DigiSetuException(
                status_code=500,
                error_code="OPENAI_NOT_INITIALIZED",
                message="OpenAI provider not initialized"
            )
        
        try:
            segmentation_prompt = f"""
Segment this content into logical blocks for data visualization analysis.

CONTENT (length: {len(content)}):
{content}

RULES:
- Create blocks that contain complete thoughts/data sections
- Each block should be 200-800 characters
- Don't split data tables, lists, or paragraphs
- Look for natural boundaries (double newlines, section headers, data blocks)
- Last block must end at position {len(content)}

Return ONLY JSON with position arrays:
{{
  "blocks": [
    [0, 300],
    [300, 600], 
    [600, {len(content)}]
  ]
}}

IMPORTANT: Blocks must be continuous with no gaps. Focus on keeping data together.
"""

            messages = [
                {
                    "role": "system", 
                    "content": "You are a text segmentation tool. Return only JSON with position arrays."
                },
                {
                    "role": "user", 
                    "content": segmentation_prompt
                }
            ]
            
            # Use GPT-4o Mini for fast, cheap segmentation
            response = await self.generate_completion(
                messages=messages,
                model="gpt-4o-mini",
                max_tokens=1000,  # Enough for any content length
                temperature=0,  # Deterministic segmentation
            )
            
            if not response.choices or not response.choices[0].message.content:
                logger.warning("GPT-4o Mini segmentation returned empty response")
                return None
            
            # Parse JSON response
            content_response = response.choices[0].message.content.strip()
            
            # Clean up any markdown formatting
            if content_response.startswith("```json"):
                content_response = content_response.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(content_response)
            position_blocks = result.get("blocks", [])
            
            # Convert [start, end] positions to block objects
            blocks = []
            for i, (start, end) in enumerate(position_blocks):
                if start < len(content) and end <= len(content) and start < end:
                    block_content = content[start:end]
                    blocks.append({
                        "start_position": start,
                        "end_position": end,
                        "content": block_content,
                        "has_enhancement_potential": True  # All blocks are candidates
                    })
            
            logger.info(
                "GPT-4o Mini segmentation completed",
                blocks_found=len(blocks),
                tokens_used=response.usage.total_tokens if response.usage else 0
            )
            
            return blocks
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse GPT-4o Mini segmentation JSON", error=str(e))
            return None
        except Exception as e:
            logger.error("GPT-4o Mini segmentation failed", error=str(e))
            return None