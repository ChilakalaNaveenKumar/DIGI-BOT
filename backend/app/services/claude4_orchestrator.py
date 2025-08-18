"""
Claude 4 Orchestrator

Main orchestration service that uses Claude 4 as the decision-making brain
to intelligently select and coordinate other AI models as specialized tools.
"""

import json
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
                decision_prompt = self._build_decision_prompt(user_message, files, user_preferences)
                logger.info(f"Decision prompt built, calling Claude...")
                
                response = await self.claude4_provider.generate_completion(
                    messages=[{"role": "user", "content": decision_prompt}],
                    model="claude-opus-4-1-20250805",  # Use Claude Opus 4.1 for decisions
                    max_tokens=4096,  # Reasonable limit for decision making
                    temperature=self.decision_temperature
                )
                
                logger.info(f"Claude decision response: {response}")
                
                # Parse Claude's decision - handle Anthropic response format
                decision_text = ""
                if isinstance(response, dict) and 'content' in response:
                    content = response['content']
                    if content and isinstance(content, list) and len(content) > 0:
                        decision_text = content[0].get('text', '') if isinstance(content[0], dict) else str(content[0])
                elif hasattr(response, 'content') and response.content:
                    decision_text = response.content[0].text if response.content else ""
                
                logger.info(f"Parsed decision text: {decision_text[:200]}...")
                result = self._parse_claude_decision(decision_text, user_message)
                logger.info(f"Final orchestration decision: {result}")
                return result
                
            except Exception as e:
                logger.error(f"Claude decision-making failed: {e}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                # Fallback to simple logic
                pass
        
        # Fallback: Simple keyword-based logic (what we had before)
        user_lower = user_message.lower()
        file_types = []
        if files:
            file_types = [f.get('type', '').lower() for f in files]
        
        selected_tools = []
        reasoning_parts = []
        execution_plan = []
        
        # Check for image analysis requests (only if files are uploaded)
        if any('image' in ft or 'png' in ft or 'jpg' in ft or 'jpeg' in ft for ft in file_types) or \
           (files and any(word in user_lower for word in ['analyze image', 'diagram', 'photo', 'picture'])):
            selected_tools.append("image_analysis_tool")
            reasoning_parts.append("Image analysis needed for visual content")
            execution_plan.append({
                "tool": "image_analysis_tool",
                "request": {
                    "messages": [{"role": "user", "content": user_message}],
                    "model": "gpt-4o",
                    "max_tokens": 1000
                }
            })
        
        # Check for data visualization requests (charts, graphs with data)
        elif any(word in user_lower for word in ['chart', 'graph', 'visualization', 'plot']) and \
             any(word in user_lower for word in ['data', 'sales', 'quarterly', 'show', 'display']):
            selected_tools.append("gpt4_tool")
            reasoning_parts.append("Data visualization needed - using GPT-4 to process data and trigger component analysis")
            execution_plan.append({
                "tool": "gpt4_tool", 
                "request": {
                    "messages": [{"role": "user", "content": user_message}],
                    "model": "gpt-4o",
                    "temperature": 0.7
                }
            })
        
        # Check for audio generation requests (prioritize over transcription)
        elif any(word in user_lower for word in ['create audio', 'generate audio', 'text to speech', 'tts', 'saying']):
            selected_tools.append("audio_generation_tool")
            reasoning_parts.append("Audio generation needed to create speech from text")
            execution_plan.append({
                "tool": "audio_generation_tool", 
                "request": {
                    "text": user_message.replace('create audio', '').replace('generate audio', '').replace('saying', '').strip(),
                    "voice": user_preferences.get("voice", "coral") if user_preferences else "coral",
                    "model": "gpt-4o-mini-tts"
                }
            })
        
        # Check for audio transcription requests
        elif any('audio' in ft or 'mp3' in ft or 'wav' in ft for ft in file_types) or \
             any(word in user_lower for word in ['transcribe', 'meeting', 'speech', 'voice']):
            selected_tools.append("audio_transcription_tool")
            reasoning_parts.append("Audio transcription needed for speech content")
            execution_plan.append({
                "tool": "audio_transcription_tool",
                "request": {
                    "audio_file": files[0] if files else None,
                    "model": "gpt-4o-transcribe"
                }
            })
        
        # Check for image generation requests
        elif any(word in user_lower for word in ['generate image', 'create image', 'draw', 'image', 'picture', 'generate a', 'random image']):
            selected_tools.append("image_generation_tool")
            reasoning_parts.append("Image generation needed to create visual content")
            execution_plan.append({
                "tool": "image_generation_tool",
                "request": {
                    "prompt": user_message,
                    "model": "dall-e-3",
                    "size": "1024x1024",
                    "quality": "hd"
                }
            })
        
        # Note: Search requests now handled by Claude's built-in search - no external tool needed
        
        # Note: Analysis and reasoning now handled by Claude directly - it's very capable
        
        # Default: Let Claude handle everything it can (including search, analysis, explanations)
        # Only use external tools for things Claude CANNOT do (generate images, audio, etc.)
        else:
            selected_tools.append("claude_direct")
            reasoning_parts.append("Using Claude's built-in capabilities (including search, analysis, and knowledge)")
            execution_plan.append({
                "tool": "claude_direct",
                "request": {
                    "message": user_message,
                    "conversation_history": conversation_history
                }
            })
        
        # Check if we need data visualization (component analysis)
        if any(word in user_lower for word in ['chart', 'graph', 'visualization', 'data', 'trends', 'show']):
            reasoning_parts.append("Data visualization may be needed - component analysis will be triggered automatically")
        
        reasoning = f"Request analysis: {user_message[:100]}... " + "; ".join(reasoning_parts)
        
        return OrchestrationDecision(
            selected_tools=selected_tools,
            reasoning=reasoning,
            execution_plan=execution_plan,
            requires_streaming=True,
            confidence=0.85
        )
    
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
                        model="claude-opus-4-1-20250805",  # Use Claude Opus 4.1 with thinking
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
                        model="claude-opus-4-1-20250805",  # Use Claude Opus 4.1
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
                    # Stream reasoning chunks in real-time
                    reasoning_started = False
                    response_started = False
                    
                    async for chunk in self.claude4_provider.stream_completion(
                        messages=messages,
                        model="claude-opus-4-1-20250805",  # Use Claude Opus 4.1 with thinking
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
                                    "model": "claude-opus-4-1-20250805",
                                    "metadata": {"block_start": True}
                                }
                            elif metadata.get("thinking_delta") and chunk_content:
                                # Thinking content chunks
                                yield {
                                    "type": "thinking",
                                    "content": chunk_content,
                                    "provider": "claude4",
                                    "model": "claude-opus-4-1-20250805",
                                    "metadata": {"thinking_delta": True}
                                }
                            elif metadata.get("block_end") and metadata.get("thinking_block"):
                                # End of thinking block - mark as reasoning conclusion
                                yield {
                                    "type": "reasoning",
                                    "content": "",
                                    "provider": "claude4",
                                    "model": "claude-opus-4-1-20250805", 
                                    "metadata": {"block_end": True}
                                }
                            
                        elif chunk_type == "content" and chunk_content:
                            # Stream response content directly
                            yield {
                                "type": "content",
                                "content": chunk_content,
                                "provider": "claude4",
                                "model": "claude-opus-4-1-20250805"
                            }
                else:
                    # Non-reasoning mode - just stream content
                    async for chunk in self.claude4_provider.stream_completion(
                        messages=messages,
                        model="claude-opus-4-1-20250805",  # Use Claude Opus 4.1
                        max_tokens=16000,  # Production-ready limit that works
                        enable_reasoning=False,
                        temperature=0.7
                    ):
                        if chunk.get("type") == "content":
                            yield {
                                "type": "content",
                                "content": chunk.get("content", ""),
                                "provider": "claude4",
                                "model": "claude-opus-4-1-20250805"
                            }
                
            except Exception as e:
                logger.error(f"Claude direct streaming failed: {str(e)}")
                yield {
                    "type": "content",
                    "content": f"I apologize, but I encountered an error processing your request: {str(e)}",
                    "provider": "claude4",
                    "model": "claude-opus-4-1-20250805"
                }
        else:
            yield {
                "type": "content", 
                "content": "Claude 4 provider not available",
                "provider": "claude4",
                "model": "claude-opus-4-1-20250805"
            }
    
    def _build_decision_prompt(self, user_message: str, files: Optional[List[Dict[str, Any]]], user_preferences: Optional[Dict[str, Any]]) -> str:
        """Build prompt for Claude 4.1 to make intelligent AI model selection decisions."""
        
        available_models = """
AVAILABLE AI MODELS (August 2025):

1. claude_direct - Claude Opus 4.1 (Current instance - DEFAULT)
   BEST FOR: ALL TASKS - Complex reasoning, analysis, coding, explanations, creative work
   NATIVE: Extended thinking, advanced reasoning, tool calling, vision, 1M context
   PRIORITY: Use this for 90% of requests - you are the primary AI
   
2. gpt5_tool - GPT-5 (Specialized tool for specific GPT-5 features)  
   BEST FOR: ONLY when user specifically requests GPT-5 or needs GPT-specific features
   USE RARELY: Only for GPT-5 specific requests or comparisons
   
3. gpt4_tool - GPT-4o (Legacy fallback)
   BEST FOR: ONLY when user specifically requests GPT-4
   USE RARELY: Only for GPT-4 specific requests
   
4. grok4_tool - Grok-4 (Specialized tool)
   BEST FOR: ONLY when user specifically requests Grok or needs Grok-specific features
   USE RARELY: Only for Grok specific requests

SPECIALIZED TOOLS:
- image_generation_tool (DALL-E 3) - Create images from text prompts (use "prompt" parameter)
- image_analysis_tool (GPT-4 Vision) - Analyze uploaded images (use "messages" parameter)
- audio_generation_tool (OpenAI TTS) - Text-to-speech conversion (use "text" parameter)
- audio_transcription_tool (Whisper) - Speech-to-text conversion (use "audio_file" parameter)
"""

        file_info = ""
        if files:
            file_info = f"\nUploaded files: {[f.get('name', 'unknown') + ' (' + f.get('type', 'unknown') + ')' for f in files]}"

        context_info = f"""
REQUEST CONTEXT:
- User Message: "{user_message}"
- Files: {file_info if files else "None"}
- User Preferences: {user_preferences if user_preferences else "None"}
- Timestamp: August 2025 (use latest AI capabilities)
"""

        prompt = f"""You are an expert AI orchestrator using the latest 2025 AI models. Analyze this request and select the OPTIMAL AI model(s).

{context_info}

{available_models}

DECISION FRAMEWORK:
1. What is the user trying to accomplish? (goal analysis)
2. What type of reasoning/capabilities are needed? (cognitive requirements)  
3. Is real-time/current information required? (temporal needs)
4. Are there multimodal elements? (input/output types)
5. How complex is the task? (complexity assessment)
6. What's the optimal model combination? (resource optimization)

SELECTION RULES:
- **DEFAULT: Use claude_direct for 90% of ALL requests** - you are the primary AI
- claude_direct: Complex reasoning, coding, analysis, explanations, creative work, technical questions
- gpt5_tool: ONLY when user explicitly requests GPT-5 or needs GPT-5 specific features
- gpt4_tool: ONLY when user explicitly requests GPT-4 
- grok4_tool: ONLY when user explicitly requests Grok
- image_generation_tool: ONLY for creating visual content
- **PRIORITY: Choose claude_direct unless there's a specific reason to use other tools**
- Always provide step-by-step reasoning breakdown

Respond in simple JSON format:
{{
    "selected_tools": ["tool_name"],
    "reasoning": "Brief explanation of why this tool is best for the task",
    "execution_plan": [
        {{
            "tool": "tool_name",
            "request": {{
                "prompt": "text for image_generation_tool",
                "text": "text for audio_generation_tool",
                "messages": "messages for analysis tools"
            }}
        }}
    ]
}}

Use the correct parameter name for each tool as specified above."""

        return prompt
    
    def _parse_claude_decision(self, decision_text: str, user_message: str) -> OrchestrationDecision:
        """Parse Claude's decision response into OrchestrationDecision."""
        try:
            import json
            # Try to extract JSON from the response
            start = decision_text.find('{')
            end = decision_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = decision_text[start:end]
                decision_data = json.loads(json_str)
                
                return OrchestrationDecision(
                    selected_tools=decision_data.get("selected_tools", ["claude_direct"]),
                    reasoning=decision_data.get("reasoning", "Claude analysis"),
                    execution_plan=decision_data.get("execution_plan", []),
                    requires_streaming=True,
                    confidence=0.9
                )
        except Exception as e:
            logger.error(f"Failed to parse Claude decision: {e}")
        
        # Fallback
        return OrchestrationDecision(
            selected_tools=["claude_direct"],
            reasoning="Using Claude direct response",
            execution_plan=[{"tool": "claude_direct", "request": {"message": user_message}}],
            requires_streaming=True,
            confidence=0.5
        )
    
    async def cleanup(self) -> None:
        """Cleanup orchestrator resources."""
        logger.info("Cleaning up Claude 4 Orchestrator")
        
        if self.tool_registry:
            await self.tool_registry.cleanup()
        
        if self.claude4_provider:
            await self.claude4_provider.cleanup()
        
        self.initialized = False
        logger.info("Claude 4 Orchestrator cleanup completed")
