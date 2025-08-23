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
from app.services.comprehensive_tools import process_comprehensive_tool_calls

# Anthropic API Event Types - Constants to avoid hardcoding
class AnthropicEvents:
    MESSAGE_START = "message_start"
    CONTENT_BLOCK_START = "content_block_start"
    CONTENT_BLOCK_DELTA = "content_block_delta"
    CONTENT_BLOCK_STOP = "content_block_stop"
    MESSAGE_DELTA = "message_delta"
    MESSAGE_STOP = "message_stop"

# Content Block Types
class ContentBlockTypes:
    TEXT = "text"
    TOOL_USE = "tool_use"
    THINKING = "thinking"

# Delta Types
class DeltaTypes:
    TEXT_DELTA = "text_delta"
    INPUT_JSON_DELTA = "input_json_delta"
    THINKING_DELTA = "thinking_delta"
    SIGNATURE_DELTA = "signature_delta"

# Stop Reasons
class StopReasons:
    END_TURN = "end_turn"
    MAX_TOKENS = "max_tokens"
    TOOL_USE = "tool_use"
    PAUSE_TURN = "pause_turn"

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
            
            # Skip health check - it's unnecessary and causes delays
            # Health will be verified on first actual API call
            
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
            
            # Simple test request - use default model from config
            response = await self.client.post(
                "/messages",
                json={
                    "model": settings.DEFAULT_AI_MODEL,  # Use config default
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
            # Use config values directly
            model = settings.DEFAULT_AI_MODEL
            max_tokens = settings.MAX_TOKENS
            temperature = settings.TEMPERATURE
            
            # Validate model
            if model not in self.models:
                model = settings.DEFAULT_AI_MODEL
            
            # Extract system message and prepare messages in one pass
            system_message = None
            anthropic_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append(msg)
            
            # Prepare request with full token limit
            model_max = self.models[model]["max_output"]
            safe_max_tokens = max_tokens or model_max
            
            request_data = {
                "model": model,
                "max_tokens": safe_max_tokens,
                "temperature": temperature,
                "messages": anthropic_messages
            }
            
            # Add system message if present
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
    
    async def stream_stepper(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        enable_thinking: bool = False,
        complex_reasoning: bool = False,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        3-Step Stepper for efficient token usage:
        Step 1: Planning + Built-in Research (full history)
        Step 2: Custom Tool Execution (minimal tokens)
        Step 3: Final Analysis (distilled context)
        """
        
        if not self.client:
            raise DigiSetuException(
                status_code=500,
                error_code="ANTHROPIC_NOT_INITIALIZED",
                message="Anthropic provider not initialized"
            )
        
        try:
            # STEP 1: Planning + Built-in Research
            logger.info("🔄 Step 1: Planning + Built-in Research")
            
            # Modify system message for planning mode (no custom tool info to avoid confusion)
            planning_messages = messages.copy()
            for i, msg in enumerate(planning_messages):
                if msg["role"] == "system":
                    planning_messages[i] = {
                        "role": "system",
                        "content": msg["content"] + "\n\nYou are in planning mode. Think, analyze, and use web_search as needed. If you think charts or tables would be helpful for your analysis, mention this in your response."
                    }
                    break
            
            step1_assistant_message = None
            custom_tools_needed = []
            
            # Only include web_search as built-in tool
            builtin_tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}]
            
            async for chunk in self._stream_anthropic_request(
                messages=planning_messages,
                tools=builtin_tools,  # Only built-in tools
                enable_thinking=enable_thinking,
                complex_reasoning=complex_reasoning
            ):
                # Pass through all chunks to frontend
                yield chunk
                
                # Look for completion to parse text for custom tool mentions
                if chunk.get("type") == "completion_finished":
                    step1_assistant_message = chunk.get("assistant_message")
                    
                    # Extract text content to check if custom tools are mentioned
                    step1_text = ""
                    for content_block in step1_assistant_message.get("content", []):
                        if content_block.get("type") == "text":
                            step1_text += content_block.get("text", "")
                    
                    # Parse text for custom tool mentions
                    if "chartjs_tool" in step1_text.lower() or "chart" in step1_text.lower():
                        logger.info("🎯 Chart tool mentioned in Step 1 text")
                        custom_tools_needed.append({
                            "name": "chartjs_tool",
                            "id": "text_chart_001",
                            "input": {"chart_type": "bar", "title": "AI Analysis Chart", "data": []}
                        })
                    
                    if "data_table_tool" in step1_text.lower() or "table" in step1_text.lower():
                        logger.info("🎯 Table tool mentioned in Step 1 text")
                        custom_tools_needed.append({
                            "name": "data_table_tool", 
                            "id": "text_table_001",
                            "input": {"title": "AI Analysis Table", "data": []}
                        })
                    
                    if not custom_tools_needed:
                        logger.info("✅ Step 1 completed - no custom tools needed")
                        # No custom tools needed - return final result
                        return
                    break
            
            # STEP 2: Custom Tool Execution
            if custom_tools_needed:
                logger.info(f"🔄 Step 2: Executing {len(custom_tools_needed)} custom tools")
                
                # Execute all custom tools
                tool_results = await process_comprehensive_tool_calls(custom_tools_needed)
                
                # Build tool result content for Step 3
                tool_result_content = []
                for i, tool_result in enumerate(tool_results):
                    tool_id = custom_tools_needed[i]["id"]
                    result_content = tool_result.get("content", "No result")
                    
                    tool_result_content.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": str(result_content)
                    })
                    
                    # Yield tool output to frontend
                    yield {
                        "type": "tool_output", 
                        "content": str(result_content),
                        "tool_name": custom_tools_needed[i]["name"]
                    }
                
                # STEP 3: Final Analysis (no tools, distilled context)
                logger.info("🔄 Step 3: Final Analysis")
                
                # Create distilled context for Step 3
                original_user_message = messages[-1] if messages else {"role": "user", "content": ""}
                
                # Clean the assistant message for Step 3 (include thinking blocks for context)
                clean_content = []
                for block in step1_assistant_message.get("content", []):
                    # Include thinking, text and tool_use blocks for full context
                    if block.get("type") in ["thinking", "text", "tool_use"]:
                        clean_content.append(block)
                
                clean_assistant_message = {
                    "role": "assistant",
                    "content": clean_content
                }
                
                distilled_messages = [
                    {
                        "role": "system",
                        "content": "You are completing a comprehensive analysis. You have research results and tool outputs (charts, tables). Write your final analysis integrating all information. Think deeply about the insights and provide comprehensive analysis."
                    },
                    original_user_message,
                    clean_assistant_message,
                    {
                        "role": "user",
                        "content": tool_result_content
                    }
                ]
                
                # Stream final analysis (no tools, but enable thinking for deep analysis)
                async for chunk in self._stream_anthropic_request(
                    messages=distilled_messages,
                    tools=None,  # No tools in Step 3
                    enable_thinking=True,  # Enable thinking for comprehensive analysis
                    complex_reasoning=True  # Enable complex reasoning for final step
                ):
                    yield chunk
            
        except Exception as e:
            logger.error("Stepper streaming failed", error=str(e))
            yield {
                "type": "error",
                "error": str(e),
                "provider": self.name
            }
    
    async def _stream_anthropic_request(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        enable_thinking: bool = False,
        complex_reasoning: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Internal method to handle single Anthropic streaming request."""
        
        # Use config values directly
        model = settings.DEFAULT_AI_MODEL
        temperature = settings.TEMPERATURE
        
        # Token allocation
        model_max_output = self.models[model]["max_output"]
        
        if complex_reasoning:
            reasoning_budget = 32000
            max_output_tokens = min(32000, model_max_output - reasoning_budget)
            total_max_tokens = reasoning_budget + max_output_tokens
        else:
            reasoning_budget = settings.REASONING_BUDGET or 16000
            max_output_tokens = settings.MAX_TOKENS or 8000
            if enable_thinking:
                total_max_tokens = min(reasoning_budget + max_output_tokens, model_max_output)
            else:
                total_max_tokens = min(max_output_tokens, model_max_output)
        
        # Validate model
        if model not in self.models:
            model = settings.DEFAULT_AI_MODEL
        
        # Extract system message and prepare messages
        system_message = None
        anthropic_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append(msg)
        
        # Prepare request
        request_data = {
            "model": model,
            "max_tokens": total_max_tokens,
            "messages": anthropic_messages,
            "stream": True
        }
        
        # Add system message if present
        if system_message:
            request_data["system"] = system_message
        
        # Configure thinking mode
        if enable_thinking:
            request_data["thinking"] = {
                "type": "enabled",
                "budget_tokens": reasoning_budget
            }
            request_data["top_p"] = 0.98
            
            # Add interleaved thinking for complex reasoning
            if complex_reasoning and settings.ENABLE_INTERLEAVED_THINKING:
                if not hasattr(self.client, '_interleaved_thinking_enabled'):
                    self.client.headers["anthropic-beta"] = "interleaved-thinking-2025-05-14"
                    self.client._interleaved_thinking_enabled = True
        else:
            request_data["temperature"] = temperature
        
        if tools and self.models[model]["supports_tools"]:
            request_data["tools"] = tools
        
        # Start streaming
        async with self.client.stream("POST", "/messages", json=request_data) as response:
            if response.status_code != 200:
                try:
                    error_body = await response.aread()
                    logger.error(
                        "Anthropic API error",
                        status=response.status_code,
                        body=error_body.decode('utf-8') if error_body else "No body"
                    )
                except Exception as e:
                    logger.error(f"Failed to read error response: {e}")
                response.raise_for_status()
            
            # Build complete assistant message as we stream
            assistant_message = {"role": "assistant", "content": []}
            current_block = None
            custom_tools_detected = []
            has_custom_tool_use = False
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        
                        # Pass through raw data for frontend
                        yield data
                        
                        # Build complete message according to Anthropic format
                        if data.get("type") == AnthropicEvents.MESSAGE_START:
                            message = data.get("message", {})
                            assistant_message.update({
                                "id": message.get("id"),
                                "role": message.get("role", "assistant"),
                                "model": message.get("model"),
                                "content": []
                            })
                        
                        elif data.get("type") == AnthropicEvents.CONTENT_BLOCK_START:
                            block = data.get("content_block", {})
                            
                            if block.get("type") == ContentBlockTypes.TEXT:
                                current_block = {"type": "text", "text": ""}
                            elif block.get("type") == ContentBlockTypes.THINKING:
                                current_block = {"type": "thinking", "thinking": "", "signature": ""}
                            elif block.get("type") == ContentBlockTypes.TOOL_USE:
                                tool_name = block.get("name")
                                
                                # Skip built-in tools (handled by Anthropic servers)
                                if tool_name == "web_search":
                                    logger.info(f"🌐 Built-in tool detected: {tool_name}")
                                    current_block = None
                                else:
                                    # Custom tool - needs continuation
                                    has_custom_tool_use = True
                                    current_block = {
                                        "type": "tool_use",
                                        "id": block.get("id"),
                                        "name": tool_name,
                                        "input": {},
                                        "partial_input": ""
                                    }
                                    logger.info(f"🔧 Custom tool detected: {tool_name}")
                            
                            # Add to content array
                            if current_block:
                                assistant_message["content"].append(current_block)
                        
                        elif data.get("type") == AnthropicEvents.CONTENT_BLOCK_DELTA:
                            delta = data.get("delta", {})
                            
                            if delta.get("type") == DeltaTypes.TEXT_DELTA and current_block:
                                current_block["text"] += delta.get("text", "")
                            elif delta.get("type") == DeltaTypes.THINKING_DELTA and current_block:
                                if current_block.get("type") == "thinking":
                                    current_block["thinking"] += delta.get("thinking", "")
                            elif delta.get("type") == DeltaTypes.SIGNATURE_DELTA and current_block:
                                if current_block.get("type") == "thinking":
                                    current_block["signature"] += delta.get("signature", "")
                            elif delta.get("type") == DeltaTypes.INPUT_JSON_DELTA and current_block:
                                if current_block.get("type") == "tool_use":
                                    partial_json = delta.get("partial_json", "")
                                    current_block["partial_input"] += partial_json
                        
                        elif data.get("type") == AnthropicEvents.CONTENT_BLOCK_STOP:
                            if current_block and current_block.get("type") == "tool_use":
                                if "partial_input" in current_block:
                                    try:
                                        current_block["input"] = json.loads(current_block["partial_input"])
                                        del current_block["partial_input"]
                                        
                                        custom_tools_detected.append({
                                            "name": current_block["name"],
                                            "id": current_block["id"],
                                            "input": current_block["input"]
                                        })
                                        logger.info(f"✅ Custom tool ready: {current_block['name']}")
                                    except json.JSONDecodeError:
                                        logger.warning(f"❌ Failed to parse tool input JSON")
                            current_block = None
                        
                        elif data.get("type") == AnthropicEvents.MESSAGE_DELTA:
                            delta = data.get("delta", {})
                            stop_reason = delta.get("stop_reason")
                            usage = data.get("usage", {})
                            
                            if stop_reason:
                                assistant_message["stop_reason"] = stop_reason
                            if usage:
                                assistant_message["usage"] = usage
                        
                        elif data.get("type") == AnthropicEvents.MESSAGE_STOP:
                            stop_reason = assistant_message.get("stop_reason")
                            usage = assistant_message.get("usage", {})
                            
                            if stop_reason == StopReasons.TOOL_USE and has_custom_tool_use:
                                # Custom tools detected
                                yield {
                                    "type": "custom_tool_use_required",
                                    "assistant_message": assistant_message,
                                    "custom_tools": custom_tools_detected,
                                    "stop_reason": stop_reason,
                                    "usage": usage
                                }
                            else:
                                # Normal completion
                                yield {
                                    "type": "completion_finished",
                                    "assistant_message": assistant_message,
                                    "stop_reason": stop_reason,
                                    "usage": usage
                                }
                            
                    except json.JSONDecodeError:
                        continue
    

    
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
