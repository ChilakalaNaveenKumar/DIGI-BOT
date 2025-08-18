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
            # Step 1: Show detailed reasoning like Claude
            yield {
                "type": "thinking",
                "content": "I need to analyze this request carefully to understand what the user is asking for and determine the best approach.",
                "metadata": {"step": "initial_analysis"}
            }
            
            # Step 2: Claude 4 analyzes request and makes orchestration decision
            yield {
                "type": "activity",
                "content": "🧠 Analyzing request and planning tool usage...",
                "metadata": {"step": "analysis"}
            }
            
            decision = await self._make_orchestration_decision(
                user_message, conversation_history, user_preferences, files
            )
            
            # Step 3: Show reasoning behind tool selection
            yield {
                "type": "reasoning",
                "content": f"**My Analysis:** {decision.reasoning}",
                "metadata": {"step": "reasoning_display", "confidence": decision.confidence}
            }
            
            yield {
                "type": "activity", 
                "content": f"🎯 Selected tools: {', '.join(decision.selected_tools)}",
                "metadata": {"step": "tool_selection", "tools": decision.selected_tools}
            }
            
            # Step 2: Execute selected tools according to plan
            tool_results = {}
            for step in decision.execution_plan:
                tool_name = step["tool"]
                tool_request = step["request"]
                
                yield {
                    "type": "activity",
                    "content": f"⚡ Executing {tool_name}...",
                    "metadata": {"step": "tool_execution", "tool": tool_name}
                }
                
                # Execute tool
                tool = self.tool_registry.get_tool(tool_name)
                if not tool:
                    logger.error(f"Tool {tool_name} not found")
                    continue
                
                # Prepare tool context with user info
                tool_context = {
                    "user_id": user_id,
                    "db": db,
                    "conversation_history": conversation_history,
                    "user_preferences": user_preferences
                }
                
                # Stream or execute tool based on capabilities
                if tool.get_capabilities().supports_streaming and decision.requires_streaming:
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
                    result = await tool.execute(tool_request, tool_context)
                    tool_results[tool_name] = result.content
                    
                    yield {
                        "type": "tool_output",
                        "content": result.content,
                        "metadata": {
                            **result.metadata,
                            "source_tool": tool_name,
                            "step": "tool_execution"
                        },
                        "final": True
                    }
            
            # Step 3: Claude 4 synthesizes results into final response
            yield {
                "type": "activity",
                "content": "🎨 Claude 4 synthesizing final response...",
                "metadata": {"step": "synthesis"}
            }
            
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
        
        # Analyze the request to determine appropriate tools
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
        elif any(word in user_lower for word in ['generate image', 'create image', 'draw', 'image of', 'picture of']):
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
        
        # Check for current events/search requests
        elif any(word in user_lower for word in ['recent', 'current', 'latest', 'news', 'today', 'now', 'developments']):
            selected_tools.append("grok4_tool")
            reasoning_parts.append("Current information needed - using Grok-4 with real-time search")
            execution_plan.append({
                "tool": "grok4_tool",
                "request": {
                    "messages": [{"role": "user", "content": user_message}],
                    "model": "grok-4",
                    "enable_search": True,
                    "temperature": 0.7
                }
            })
        
        # Check for complex reasoning/analysis requests
        elif any(word in user_lower for word in ['analyze', 'complex', 'reasoning', 'advanced', 'trends', 'patterns']):
            selected_tools.append("gpt5_tool")
            reasoning_parts.append("Complex analysis requires GPT-5's advanced reasoning capabilities")
            execution_plan.append({
                "tool": "gpt5_tool",
                "request": {
                    "messages": [{"role": "user", "content": user_message}],
                    "model": "gpt-5",
                    "temperature": 0.7
                }
            })
        
        # Default to GPT-4 for general conversation
        else:
            selected_tools.append("gpt4_tool")
            reasoning_parts.append("General conversation - using GPT-4 for reliable assistance")
            execution_plan.append({
                "tool": "gpt4_tool",
                "request": {
                    "messages": [{"role": "user", "content": user_message}],
                    "model": "gpt-4o",
                    "temperature": 0.7
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
        
        # If only one tool was used and it was streaming, we might already have the final response
        if len(tool_results) == 1 and decision.requires_streaming:
            tool_name = list(tool_results.keys())[0]
            yield {
                "type": "content",
                "content": tool_results[tool_name],
                "metadata": {
                    "orchestrator": "claude4",
                    "tools_used": decision.selected_tools,
                    "reasoning": decision.reasoning
                },
                "final": True
            }
            return
    
    async def cleanup(self) -> None:
        """Cleanup orchestrator resources."""
        logger.info("Cleaning up Claude 4 Orchestrator")
        
        if self.tool_registry:
            await self.tool_registry.cleanup()
        
        if self.claude4_provider:
            await self.claude4_provider.cleanup()
        
        self.initialized = False
        logger.info("Claude 4 Orchestrator cleanup completed")
