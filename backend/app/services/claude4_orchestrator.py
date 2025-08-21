"""
Claude 4 Orchestrator

Main orchestration service that uses Claude 4 as the decision-making brain
to intelligently select and coordinate other AI models as specialized tools.
"""

import json
import time
from typing import Dict, Any, Optional, List, AsyncGenerator
import structlog
from pydantic import BaseModel

from app.services.tools.tool_registry import ToolRegistry
from app.services.tools.ai_model_tools import GPT5Tool, GPT4Tool, Grok4Tool
from app.services.tools.audio_tools import AudioTranscriptionTool, AudioGenerationTool, RealtimeVoiceTool
from app.services.tools.image_tools import ImageAnalysisTool, ImageGenerationTool, ImageEditingTool
from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)


class OrchestrationDecision(BaseModel):
    """Decision made by Claude 4 about which tools to use."""
    selected_tools: List[str]
    reasoning: str
    execution_plan: List[Dict[str, Any]]
    requires_streaming: bool = True
    confidence: float


class Claude4Orchestrator:
    """
    Claude 4 Orchestrator - The Main Brain
    
    Uses Claude 4's superior reasoning to:
    - Analyze user requests intelligently
    - Select appropriate AI model tools
    - Coordinate multi-tool workflows
    - Synthesize results into coherent responses
    - Handle streaming with component injection
    """
    
    def __init__(self):
        self.claude4_provider = None
        self.tool_registry = None
        self.initialized = False
        
        # Orchestration settings
        self.max_tool_calls_per_request = 5
        self.decision_temperature = 0.3  # Lower for more consistent decisions
        self.synthesis_temperature = 0.7  # Higher for creative synthesis
    
    async def initialize(self) -> None:
        """Initialize Claude 4 orchestrator and all tools."""
        try:
            logger.info("Initializing Claude 4 Orchestrator")
            
            # Initialize Claude 4 provider
            self.claude4_provider = AnthropicProvider()
            await self.claude4_provider.initialize()
            
            # Initialize tool registry
            self.tool_registry = ToolRegistry()
            
            # Register all AI model tools
            self.tool_registry.register_tool(GPT5Tool())
            self.tool_registry.register_tool(GPT4Tool())
            self.tool_registry.register_tool(Grok4Tool())
            
            # Register all multimodal tools
            self.tool_registry.register_tool(AudioTranscriptionTool())
            self.tool_registry.register_tool(AudioGenerationTool())
            self.tool_registry.register_tool(RealtimeVoiceTool())
            self.tool_registry.register_tool(ImageAnalysisTool())
            self.tool_registry.register_tool(ImageGenerationTool())
            self.tool_registry.register_tool(ImageEditingTool())
            
            # Initialize all tools
            await self.tool_registry.initialize()
            
            self.initialized = True
            logger.info("Claude 4 Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Claude 4 Orchestrator", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="CLAUDE4_ORCHESTRATOR_INIT_ERROR",
                message="Failed to initialize Claude 4 orchestrator"
            )
    
    async def process_request(
        self,
        user_message: str,
        conversation_history: List[Dict[str, Any]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        project_settings: Optional[Dict[str, Any]] = None,
        files: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[str] = None,
        db: Optional[Any] = None,
        system_message: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process user request using Claude 4 orchestration.
        
        This is the main entry point where Claude 4 analyzes the request
        and intelligently coordinates other AI models as tools.
        """
        if not self.initialized:
            raise DigiSetuException(
                status_code=500,
                error_code="ORCHESTRATOR_NOT_INITIALIZED",
                message="Claude 4 orchestrator not initialized"
            )
        
        try:
            decision = await self._make_orchestration_decision(
                user_message, conversation_history, user_preferences, files
            )
            
            # Let AI models provide their own natural thinking/reasoning
            
           
            
            # Step 2: Execute selected tools according to plan
            tool_results = {}
            for step in decision.execution_plan:
                logger.info(f"Processing execution step: {step}")
                tool_name = step["tool"]
                tool_request = step.get("request", {})
                logger.info(f"Tool name: {tool_name}, Tool request: {tool_request}")
                
                # Only show execution for complex tasks, hide for simple conversations
                if any(word in user_message.lower() for word in ['generate', 'create', 'analyze', 'chart', 'audio', 'image']):
                    friendly_name = tool_name.replace('_tool', '').replace('_', ' ').title()
        
                
                # Handle Claude direct responses
                if tool_name == "claude_direct":
                    # Claude responds directly without external tools - enable reasoning
                    message = tool_request.get("message", user_message)
                    
                    # Stream Claude direct response with reasoning
                    accumulated_content = ""
                    async for chunk in self._claude_direct_response_stream(
                        message, conversation_history, enable_reasoning=True
                    ):
                        # Only accumulate content chunks, not reasoning chunks
                        if chunk.get("type") == "content":
                            accumulated_content += chunk.get("content", "")
                        yield chunk  # Stream reasoning and content chunks in real-time
                    
                    tool_results[tool_name] = accumulated_content
                    continue
                
                # Execute tool - handle name mapping
                # Map Claude's tool names to actual registered names
                tool_name_mapping = {
                    "gpt5": "gpt5_tool",
                    "gpt4": "gpt4_tool", 
                    "grok4": "grok4_tool",
                    "claude_opus_4_1": "claude_direct",
                    "image_generation": "image_generation_tool",
                    "image_analysis": "image_analysis_tool",
                    "audio_generation": "audio_generation_tool",
                    "audio_transcription": "audio_transcription_tool"
                }
                
                actual_tool_name = tool_name_mapping.get(tool_name, tool_name)
                tool = self.tool_registry.get_tool(actual_tool_name)
                if not tool:
                    logger.error(f"Tool {actual_tool_name} (mapped from {tool_name}) not found")
                    continue
                
                # Prepare tool context with user info
                tool_context = {
                    "user_id": user_id,
                    "db": db,
                    "conversation_history": conversation_history or [],
                    "user_preferences": user_preferences or {}
                }
                
                # Stream or execute tool based on capabilities
                try:
                    logger.info(f"Executing tool {tool_name} with request: {tool_request}")
                    capabilities = tool.get_capabilities()
                    if capabilities and capabilities.supports_streaming and decision.requires_streaming:
                        accumulated_content = ""
                        async for chunk in tool.stream_execute(tool_request, tool_context):
                            # Accumulate content
                            chunk_content = chunk.get("content", "")
                            accumulated_content += chunk_content
                            
                            # Forward tool output with metadata
                            yield {
                                "type": "tool_output",
                                "content": chunk_content,
                                "metadata": {
                                    **chunk.get("metadata", {}),
                                    "source_tool": tool_name,
                                    "step": "tool_streaming"
                                },
                                "final": chunk.get("final", False)
                            }
                            
                            # Store final result for synthesis when streaming is complete
                            if chunk.get("final", False):
                                tool_results[tool_name] = accumulated_content
                        
                        # Ensure we store the result even if no final chunk was sent
                        if tool_name not in tool_results:
                            tool_results[tool_name] = accumulated_content
                    else:
                        logger.info(f"About to execute non-streaming tool {tool_name} with request: {tool_request}")
                        result = await tool.execute(tool_request, tool_context)
                        
                        if result and result.success:
                            tool_results[tool_name] = result.content
                            
                            yield {
                                "type": "tool_output",
                                "content": result.content,
                                "metadata": {
                                    **(result.metadata or {}),
                                    "source_tool": tool_name,
                                    "step": "tool_execution"
                                },
                                "final": True
                            }
                        else:
                            error_msg = result.error if result else "Unknown error"
                            tool_results[tool_name] = f"Tool execution failed: {error_msg}"
                            logger.error(f"Tool {tool_name} execution failed: {error_msg}")
                            
                            yield {
                                "type": "tool_output",
                                "content": f"Tool execution failed: {error_msg}",
                                "metadata": {
                                    "source_tool": tool_name,
                                    "step": "tool_execution",
                                    "error": True
                                },
                                "final": True
                            }
                except Exception as e:
                    logger.error(f"Tool execution failed for {tool_name}: {e}")
                    tool_results[tool_name] = f"Tool execution failed: {str(e)}"
            
            # Step 3: Claude 4 synthesizes results into final response
            # Final response ready
            
            async for chunk in self._synthesize_response(
                user_message, decision, tool_results, conversation_history
            ):
                yield chunk
            
        except Exception as e:
            logger.error("Claude 4 orchestration failed", error=str(e))
            yield {
                "type": "error",
                "content": f"Orchestration failed: {str(e)}",
                "final": True
            }
    
    async def _make_orchestration_decision(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, Any]]],
        user_preferences: Optional[Dict[str, Any]],
        files: Optional[List[Dict[str, Any]]]
    ) -> OrchestrationDecision:
        """Claude 4 analyzes request and decides which tools to use."""
        
        # Actually use Claude 4 to make real decisions
        logger.info(f"Making orchestration decision for: {user_message}")
        if self.claude4_provider:
            try:
                # Build simplified prompt without tool descriptions (tools are passed as parameter)
                simple_prompt = f"""Analyze this user request and decide which tools to use (if any).

User request: "{user_message}"
{f"Files uploaded: {[f.get('name', 'unknown') for f in files]}" if files else ""}

You have access to AI models (GPT-5, GPT-4, Grok) and specialized tools (image, audio, etc).
Use tools only when necessary - you can handle most requests directly.

Respond with tool calls if needed, or answer directly."""
                
                logger.info(f"Simplified prompt built, calling Claude with tools...")
                
                response = await self.claude4_provider.generate_completion(
                    messages=[{"role": "user", "content": simple_prompt}],
                    model="claude-sonnet-4-20250514",
                    max_tokens=16000,  # Higher limit as requested
                    temperature=self.decision_temperature,
                    tools=self._get_available_tools()  # Pass tools as parameter instead of describing in prompt
                )
                
                logger.info(f"Claude response received")
                
                # Claude now handles tool decisions automatically via tools parameter
                # Check if Claude used any tools or responded directly
                content_blocks = response.get('content', [])
                tool_calls = []
                direct_response = ""
                
                for block in content_blocks:
                    if isinstance(block, dict):
                        if block.get('type') == 'tool_use':
                            tool_calls.append({
                                'tool': block.get('name'),
                                'request': block.get('input', {})
                            })
                        elif block.get('type') == 'text':
                            direct_response += block.get('text', '')
                
                # Create decision based on Claude's response
                if tool_calls:
                    selected_tools = [call['tool'] for call in tool_calls]
                    execution_plan = tool_calls
                    reasoning = f"Claude selected tools: {', '.join(selected_tools)}"
                else:
                    selected_tools = ["claude_direct"]
                    execution_plan = [{"tool": "claude_direct", "request": {"response": direct_response}}]
                    reasoning = "Claude handled request directly"
                
                result = OrchestrationDecision(
                    selected_tools=selected_tools,
                    reasoning=reasoning,
                    execution_plan=execution_plan,
                    requires_streaming=True,
                    confidence=0.9
                )
                
                logger.info(f"Final orchestration decision: {result}")
                return result
                
            except Exception as e:
                logger.error(f"Claude decision-making failed: {e}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                # Fallback to simple logic
                pass
        
        # Fallback: Simple direct response if Claude API fails
        return OrchestrationDecision(
            selected_tools=["claude_direct"],
            reasoning="Fallback to direct Claude response due to API issues",
            execution_plan=[{
                "tool": "claude_direct",
                "request": {"message": user_message}
            }],
            requires_streaming=True,
            confidence=0.7
        )
    
    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Get ALL tools in Anthropic API format instead of describing them in prompts."""
        return [
            # AI Model Tools - for when Claude needs backup or specific capabilities
            {
                "name": "gpt5_tool",
                "description": "Use GPT-5 for advanced reasoning, coding, or when user specifically requests GPT-5",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "messages": {
                            "type": "array",
                            "description": "Conversation messages to send to GPT-5"
                        },
                        "model": {
                            "type": "string", 
                            "description": "GPT-5 model variant",
                            "default": "gpt-5"
                        }
                    },
                    "required": ["messages"]
                }
            },
            {
                "name": "gpt4_tool",
                "description": "Use GPT-4o for specific tasks or when user requests GPT-4",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "messages": {
                            "type": "array",
                            "description": "Conversation messages to send to GPT-4"
                        },
                        "model": {
                            "type": "string",
                            "description": "GPT-4 model variant", 
                            "default": "gpt-4o"
                        }
                    },
                    "required": ["messages"]
                }
            },
            {
                "name": "grok4_tool",
                "description": "Use Grok-4 for alternative perspectives or when user requests Grok",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "messages": {
                            "type": "array",
                            "description": "Conversation messages to send to Grok"
                        },
                        "model": {
                            "type": "string",
                            "description": "Grok model variant",
                            "default": "grok-4"
                        }
                    },
                    "required": ["messages"]
                }
            },
            
            # Image Tools
            {
                "name": "image_generation_tool",
                "description": "Generate images from text prompts using DALL-E 3",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The text prompt to generate an image from"
                        }
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "image_analysis_tool",
                "description": "Analyze uploaded images using GPT-4 Vision",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "messages": {
                            "type": "array",
                            "description": "Messages with image content to analyze"
                        }
                    },
                    "required": ["messages"]
                }
            },
            {
                "name": "image_editing_tool", 
                "description": "Edit or modify existing images",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "image_path": {
                            "type": "string",
                            "description": "Path to the image to edit"
                        },
                        "instructions": {
                            "type": "string",
                            "description": "Instructions for how to edit the image"
                        }
                    },
                    "required": ["image_path", "instructions"]
                }
            },
            
            # Audio Tools  
            {
                "name": "audio_generation_tool",
                "description": "Convert text to speech using OpenAI TTS",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to convert to speech"
                        },
                        "voice": {
                            "type": "string",
                            "description": "Voice to use for TTS",
                            "default": "alloy"
                        }
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "audio_transcription_tool",
                "description": "Convert speech to text using Whisper",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "audio_file": {
                            "type": "string",
                            "description": "Path to the audio file to transcribe"
                        }
                    },
                    "required": ["audio_file"]
                }
            },
            {
                "name": "realtime_voice_tool",
                "description": "Handle real-time voice conversations",
                "input_schema": {
                    "type": "object", 
                    "properties": {
                        "action": {
                            "type": "string",
                            "description": "Action to perform (start, stop, process)"
                        },
                        "audio_data": {
                            "type": "string",
                            "description": "Audio data for processing"
                        }
                    },
                    "required": ["action"]
                }
            }
        ]
    
    async def _synthesize_response(
        self,
        user_message: str,
        decision: OrchestrationDecision,
        tool_results: Dict[str, str],
        conversation_history: Optional[List[Dict[str, Any]]]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Claude 4 synthesizes tool results into final coherent response."""
        
        if not tool_results:
            yield {
                "type": "content",
                "content": "I apologize, but I wasn't able to process your request successfully. Please try again.",
                "final": True
            }
            return
        
        # If only one tool was used and it was streaming, content was already streamed
        if len(tool_results) == 1 and decision.requires_streaming:
            # Content was already streamed in real-time, just send completion marker
            yield {
                "type": "complete",
                "content": "Response completed",
                "metadata": {
                    "orchestrator": "claude4",
                    "tools_used": decision.selected_tools
                },
                "final": True
            }
            return
    
    async def _claude_direct_response(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        enable_reasoning: bool = False
    ) -> str:
        """Handle direct Claude responses without external tools."""
        
        # Use the actual Claude 4 provider for real responses
        logger.info(f"Claude provider available: {self.claude4_provider is not None}")
        if self.claude4_provider:
            try:
                # Add system message to encourage markdown formatting
                messages = [
                    {
                        "role": "system", 
                        "content": "You are a helpful AI assistant. Always format your responses in markdown for better readability. Use headers, lists, code blocks, emphasis, and other markdown elements as appropriate."
                    },
                    {"role": "user", "content": message}
                ]
                
                # Add conversation history if available
                if conversation_history:
                    formatted_history = []
                    for msg in conversation_history[-5:]:  # Last 5 messages for context
                        formatted_history.append({
                            "role": msg.get("role", "user"),
                            "content": msg.get("content", "")
                        })
                    # Insert history before the current message
                    messages = [messages[0]] + formatted_history + [messages[1]]
                
                logger.info(f"Calling Claude with messages: {messages}")
                
                # Use streaming with reasoning if enabled
                if enable_reasoning:
                    full_response = ""
                    reasoning_content = ""
                    
                    async for chunk in self.claude4_provider.stream_completion(
                        messages=messages,
                        model="claude-sonnet-4-20250514",  # Use Claude Opus 4.1 with thinking
                        max_tokens=16000,  # Production-ready: 16K max + 4K thinking = 20K total
                        enable_reasoning=True,
                        reasoning_budget=4000  # Larger budget for complex reasoning
                    ):
                        if chunk.get("type") == "reasoning":
                            reasoning_content += chunk.get("content", "")
                        elif chunk.get("type") == "content":
                            full_response += chunk.get("content", "")
                    
                    # Return both reasoning and response
                    if reasoning_content:
                        return f"**Reasoning:**\n{reasoning_content}\n\n**Response:**\n{full_response}"
                    else:
                        return full_response
                else:
                    response = await self.claude4_provider.generate_completion(
                        messages=messages,
                        model="claude-sonnet-4-20250514",  # Use Claude Opus 4.1
                        max_tokens=16000,  # Production-ready limit that works
                        temperature=0.7
                    )
                
                logger.info(f"Claude response: {response}")
                # Handle Anthropic response format (dict with 'content' array)
                if isinstance(response, dict) and 'content' in response:
                    content = response['content']
                    if content and isinstance(content, list) and len(content) > 0:
                        return content[0].get('text', '') if isinstance(content[0], dict) else str(content[0])
                elif hasattr(response, 'content') and response.content:
                    return response.content[0].text if response.content else "I'm here to help! How can I assist you?"
                
                return "I'm here to help! How can I assist you?"
                
            except Exception as e:
                logger.error(f"Claude direct response failed: {e}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                # Fallback to simple responses
                pass
        
        # Fallback if Claude provider completely fails
        return "I'm having trouble connecting to my AI capabilities right now. Please try again in a moment."
    
    async def _claude_direct_response_stream(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, Any]]],
        enable_reasoning: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Get streaming response from Claude 4 with real-time reasoning chunks."""
        
        # Use the actual Claude 4 provider for real responses
        logger.info(f"Claude provider available: {self.claude4_provider is not None}")
        if self.claude4_provider:
            try:
                # Add system message to encourage markdown formatting
                messages = [
                    {
                        "role": "system", 
                        "content": "You are a helpful AI assistant. Always format your responses in markdown for better readability. Use headers, lists, code blocks, emphasis, and other markdown elements as appropriate."
                    },
                    {"role": "user", "content": message}
                ]
                
                # Add conversation history if available
                if conversation_history:
                    formatted_history = []
                    for msg in conversation_history[-5:]:  # Last 5 messages for context
                        formatted_history.append({
                            "role": msg.get("role", "user"),
                            "content": msg.get("content", "")
                        })
                    # Insert history before the current message
                    messages = [messages[0]] + formatted_history + [messages[1]]
                
                logger.info(f"Streaming Claude with reasoning={enable_reasoning}")
                
                if enable_reasoning:
                    # Stream reasoning chunks in real-time, but accumulate content
                    reasoning_started = False
                    response_started = False
                    accumulated_content = ""  # Track accumulated content
                    content_id = f"content_{int(time.time() * 1000)}"  # Unique ID for this content stream
                    
                    async for chunk in self.claude4_provider.stream_completion(
                        messages=messages,
                        model="claude-sonnet-4-20250514",  # Use Claude Opus 4.1 with thinking
                        max_tokens=16000,  # Production-ready: 16K max + 4K thinking = 20K total
                        enable_reasoning=True,
                        reasoning_budget=4000  # Larger budget for complex reasoning
                    ):
                        chunk_type = chunk.get("type")
                        chunk_content = chunk.get("content", "")
                        
                        if chunk_type == "reasoning":
                            # Preserve the actual Anthropic block structure
                            metadata = chunk.get("metadata", {})
                            
                            if metadata.get("block_start") and metadata.get("thinking_block"):
                                # Start of thinking block
                                yield {
                                    "type": "thinking",
                                    "content": "",
                                    "provider": "claude4", 
                                    "model": "claude-sonnet-4-20250514",
                                    "metadata": {"block_start": True}
                                }
                            elif metadata.get("thinking_delta") and chunk_content:
                                # Thinking content chunks
                                yield {
                                    "type": "thinking",
                                    "content": chunk_content,
                                    "provider": "claude4",
                                    "model": "claude-sonnet-4-20250514",
                                    "metadata": {"thinking_delta": True}
                                }
                            elif metadata.get("block_end") and metadata.get("thinking_block"):
                                # End of thinking block - mark as reasoning conclusion
                                yield {
                                    "type": "reasoning",
                                    "content": "",
                                    "provider": "claude4",
                                    "model": "claude-sonnet-4-20250514", 
                                    "metadata": {"block_end": True}
                                }
                            
                        elif chunk_type == "content" and chunk_content:
                            # Accumulate content and stream the full accumulated content with consistent ID
                            accumulated_content += chunk_content
                            yield {
                                "type": "content",
                                "content": accumulated_content,  # Send full accumulated content
                                "id": content_id,  # Same ID for all updates to this content
                                "provider": "claude4",
                                "model": "claude-sonnet-4-20250514"
                            }
                else:
                    # Non-reasoning mode - accumulate content
                    accumulated_content = ""
                    content_id = f"content_{int(time.time() * 1000)}"  # Unique ID for this content stream
                    async for chunk in self.claude4_provider.stream_completion(
                        messages=messages,
                        model="claude-sonnet-4-20250514",  # Use Claude Opus 4.1
                        max_tokens=16000,  # Production-ready limit that works
                        enable_reasoning=False,
                        temperature=0.7
                    ):
                        if chunk.get("type") == "content":
                            accumulated_content += chunk.get("content", "")
                            yield {
                                "type": "content",
                                "content": accumulated_content,  # Send full accumulated content
                                "id": content_id,  # Same ID for all updates to this content
                                "provider": "claude4",
                                "model": "claude-sonnet-4-20250514"
                            }
                
            except Exception as e:
                logger.error(f"Claude direct streaming failed: {str(e)}")
                yield {
                    "type": "content",
                    "content": f"I apologize, but I encountered an error processing your request: {str(e)}",
                    "provider": "claude4",
                    "model": "claude-sonnet-4-20250514"
                }
        else:
            yield {
                "type": "content", 
                "content": "Claude 4 provider not available",
                "provider": "claude4",
                "model": "claude-sonnet-4-20250514"
            }
    

    

    
    async def cleanup(self) -> None:
        """Cleanup orchestrator resources."""
        logger.info("Cleaning up Claude 4 Orchestrator")
        
        if self.tool_registry:
            await self.tool_registry.cleanup()
        
        if self.claude4_provider:
            await self.claude4_provider.cleanup()
        
        self.initialized = False
        logger.info("Claude 4 Orchestrator cleanup completed")
