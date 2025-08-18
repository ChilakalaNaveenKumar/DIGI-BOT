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
                    async for chunk in tool.stream_execute(tool_request, tool_context):
                        # Forward tool output with metadata
                        yield {
                            "type": "tool_output",
                            "content": chunk.get("content", ""),
                            "metadata": {
                                **chunk.get("metadata", {}),
                                "source_tool": tool_name,
                                "step": "tool_streaming"
                            },
                            "final": chunk.get("final", False)
                        }
                        
                        # Store final result for synthesis
                        if chunk.get("final", False):
                            tool_results[tool_name] = chunk.get("content", "")
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
        
        # Get available tools info
        all_capabilities = self.tool_registry.get_all_capabilities()
        tools_info = self._format_tools_for_decision(all_capabilities)
        
        # Build decision prompt
        decision_prompt = self._build_decision_prompt(
            user_message, tools_info, conversation_history, user_preferences, files
        )
        
        # Get Claude 4's decision
        messages = [{"role": "user", "content": decision_prompt}]
        
        response = await self.claude4_provider.generate_completion(
            messages=messages,
            model="claude-4",
            temperature=self.decision_temperature,
            max_tokens=2000
        )
        
        # Parse decision from Claude 4
        decision_text = response.choices[0].message.content
        return self._parse_orchestration_decision(decision_text)
    
    def _build_decision_prompt(
        self,
        user_message: str,
        tools_info: str,
        conversation_history: Optional[List[Dict[str, Any]]],
        user_preferences: Optional[Dict[str, Any]],
        files: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build prompt for Claude 4 to make orchestration decisions."""
        
        context_info = []
        if conversation_history:
            context_info.append(f"Conversation history: {len(conversation_history)} previous messages")
        if files:
            file_types = [f.get('type', 'unknown') for f in files]
            context_info.append(f"Files provided: {', '.join(file_types)}")
        if user_preferences:
            context_info.append(f"User preferences: {json.dumps(user_preferences)}")
        
        context_str = "\n".join(context_info) if context_info else "No additional context"
        
        return f"""You are Claude 4, the main orchestrator for an AI system. Your job is to analyze user requests and intelligently select which AI model tools to use.

AVAILABLE TOOLS:
{tools_info}

USER REQUEST: "{user_message}"

CONTEXT:
{context_str}

DECISION GUIDELINES:
- GPT-5: Use for complex reasoning, advanced analysis, latest knowledge, creative tasks
- GPT-4: Use for coding, general intelligence, structured tasks, reliable problem-solving
- Grok-4: Use for real-time information, current events, search-enhanced responses, up-to-date knowledge
- Audio tools: Use when audio processing is needed (transcription, generation, real-time voice)
- Image tools: Use when image processing is needed (analysis, generation, editing)
- Component Analysis: Will be called automatically by frontend when data visualization is detected

ANALYSIS PROCESS:
1. First, understand what the user is asking for
2. Identify the type of task (reasoning, coding, search, creative, technical, etc.)
3. Consider if multiple tools are needed or if one can handle everything
4. Think about the best model for this specific request
5. Consider user context and preferences

Analyze this request and provide your decision in this JSON format:
{{
    "selected_tools": ["tool1", "tool2"],
    "reasoning": "Detailed explanation of your thinking process: What is the user asking for? What type of task is this? Why did you choose these specific tools? What makes them the best choice for this request?",
    "execution_plan": [
        {{"tool": "tool1", "request": {{"messages": [{{"role": "user", "content": "adapted request for this tool"}}], "model": "appropriate-model", "temperature": 0.7}}}},
        {{"tool": "tool2", "request": {{...}}}}
    ],
    "requires_streaming": true,
    "confidence": 0.9
}}

IMPORTANT: 
- Provide detailed reasoning that shows your thinking process
- Be strategic - select the BEST tool for each aspect of the request
- Don't use multiple tools if one can handle everything efficiently
- Consider the user's likely intent beyond just the literal request
- Adapt the request appropriately for each selected tool"""
    
    def _format_tools_for_decision(self, capabilities: Dict[str, Any]) -> str:
        """Format tool capabilities for Claude 4's decision making."""
        tools_list = []
        for tool_name, caps in capabilities.items():
            tools_list.append(
                f"- {caps.name}: {caps.description} "
                f"(Category: {caps.category}, Streaming: {caps.supports_streaming})"
            )
        return "\n".join(tools_list)
    
    def _parse_orchestration_decision(self, decision_text: str) -> OrchestrationDecision:
        """Parse Claude 4's decision response."""
        try:
            # Extract JSON from response
            start = decision_text.find('{')
            end = decision_text.rfind('}') + 1
            json_str = decision_text[start:end]
            
            decision_data = json.loads(json_str)
            
            return OrchestrationDecision(
                selected_tools=decision_data.get("selected_tools", []),
                reasoning=decision_data.get("reasoning", ""),
                execution_plan=decision_data.get("execution_plan", []),
                requires_streaming=decision_data.get("requires_streaming", True),
                confidence=decision_data.get("confidence", 0.5)
            )
            
        except Exception as e:
            logger.error("Failed to parse orchestration decision", error=str(e))
            # Fallback to GPT-4 for general queries
            return OrchestrationDecision(
                selected_tools=["gpt4_tool"],
                reasoning="Failed to parse decision, using GPT-4 fallback",
                execution_plan=[{
                    "tool": "gpt4_tool",
                    "request": {
                        "messages": [{"role": "user", "content": "Please help with this request"}],
                        "model": "gpt-4o"
                    }
                }],
                requires_streaming=True,
                confidence=0.3
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
        
        # Multi-tool synthesis
        synthesis_prompt = f"""You are Claude 4, synthesizing results from multiple AI tools into a coherent response.

ORIGINAL USER REQUEST: "{user_message}"

ORCHESTRATION DECISION: {decision.reasoning}

TOOL RESULTS:
{json.dumps(tool_results, indent=2)}

Synthesize these results into a single, coherent, helpful response for the user. 
Be natural and conversational. Don't mention the internal tool orchestration unless relevant.
Focus on directly answering the user's question using the tool results."""

        messages = [{"role": "user", "content": synthesis_prompt}]
        
        # Stream the synthesis
        async for chunk in self.claude4_provider.stream_completion(
            messages=messages,
            model="claude-4",
            temperature=self.synthesis_temperature,
            max_tokens=4000
        ):
            yield {
                "type": "content",
                "content": chunk.get("content", ""),
                "metadata": {
                    "orchestrator": "claude4",
                    "tools_used": decision.selected_tools,
                    "reasoning": decision.reasoning,
                    "synthesis": True
                },
                "final": chunk.get("final", False)
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
