"""
AI Orchestrator Service

Advanced AI orchestration system where GPT-5 acts as a "conductor" to select
and delegate tasks to specialized AI models based on request analysis.
"""

import asyncio
import json
import time
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

import structlog
from pydantic import BaseModel

from app.core.config import get_settings
from app.services.ai_providers.openai_provider import OpenAIProvider
from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.ai_providers.grok_provider import GrokProvider
from app.services.activity_streamer import ActivityStreamer
from app.services.reasoning_processor import ReasoningProcessor
from app.services.tool_executor import ToolExecutor
from app.services.adaptive_workflow_engine import AdaptiveWorkflowEngine

logger = structlog.get_logger(__name__)
settings = get_settings()


class TaskType(BaseModel):
    """Task type classification."""
    category: str  # analysis, creative, coding, search, image, etc.
    complexity: str  # simple, medium, complex
    requires_reasoning: bool
    requires_tools: bool
    estimated_tokens: int
    recommended_provider: str
    confidence: float


class OrchestrationPlan(BaseModel):
    """Orchestration execution plan."""
    primary_provider: str
    secondary_providers: List[str]
    task_breakdown: List[Dict[str, Any]]
    reasoning_required: bool
    tools_required: List[str]
    estimated_time: float
    confidence: float


class AIOrchestrator:
    """
    Advanced AI Orchestration System
    
    Features:
    - Intelligent task analysis and provider selection
    - Multi-model workflow coordination
    - Reasoning display and activity streaming
    - Tool execution management
    - Cost optimization and performance monitoring
    """
    
    def __init__(self):
        self.providers = {}
        self.activity_streamer = ActivityStreamer()
        self.reasoning_processor = ReasoningProcessor()
        self.tool_executor = ToolExecutor()
        self.adaptive_workflow_engine = None  # Will be initialized after providers
        self.performance_metrics = {}
        self.use_adaptive_workflow = False  # Feature flag for adaptive workflow - disabled for now
        
    async def initialize(self):
        """Initialize AI providers and services."""
        try:
            # Initialize AI providers
            self.providers = {
                "openai": OpenAIProvider(),
                "anthropic": AnthropicProvider(),
                "grok": GrokProvider(),
            }
            
            # Initialize each provider
            for name, provider in self.providers.items():
                await provider.initialize()
                logger.info(f"✅ {name.title()} provider initialized")
            
            # Initialize supporting services
            await self.activity_streamer.initialize()
            await self.reasoning_processor.initialize()
            await self.tool_executor.initialize()
            
            # Initialize adaptive workflow engine
            if self.use_adaptive_workflow:
                self.adaptive_workflow_engine = AdaptiveWorkflowEngine(self.providers)
                await self.adaptive_workflow_engine.initialize()
                logger.info("🚀 Adaptive Workflow Engine initialized")
            
            logger.info("🎭 AI Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize AI Orchestrator", error=str(e))
            raise
    
    async def cleanup(self):
        """Cleanup resources."""
        for provider in self.providers.values():
            await provider.cleanup()
        
        await self.activity_streamer.cleanup()
        await self.reasoning_processor.cleanup()
        await self.tool_executor.cleanup()
        
        if self.adaptive_workflow_engine:
            await self.adaptive_workflow_engine.cleanup()
        
        logger.info("AI Orchestrator cleaned up")
    
    async def process_request(
        self,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None,
        project_settings: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process user request with intelligent orchestration.
        
        Args:
            user_message: User's input message
            conversation_history: Previous conversation context
            user_preferences: User's AI preferences
            project_settings: Project-specific settings
            
        Yields:
            Streaming response chunks with activity updates
        """
        start_time = time.time()
        
        try:
            # Use adaptive workflow engine if enabled
            if self.use_adaptive_workflow and self.adaptive_workflow_engine:
                async for chunk in self.adaptive_workflow_engine.execute_adaptive_workflow(
                    user_message,
                    conversation_history,
                    user_preferences,
                    project_settings
                ):
                    yield chunk
                return
            
            # Fallback to legacy orchestration
            logger.info("Using legacy orchestration workflow")
            
            # Step 1: Analyze the request and create orchestration plan (silently)
            task_analysis = await self._analyze_task(
                user_message, conversation_history, user_preferences
            )
            
            orchestration_plan = await self._create_orchestration_plan(
                task_analysis, user_preferences, project_settings
            )
            
            # Step 1.5: Generate real AI reasoning for beautiful thinking process
            logger.info(f"Task analysis: requires_reasoning={task_analysis.requires_reasoning}, category={task_analysis.category}")
            
            # Always generate reasoning for thinking process
            logger.info("Generating reasoning for thinking process...")
            provider = self.providers[orchestration_plan.primary_provider]
            
            # Create a simple reasoning prompt
            reasoning_prompt = f"""Think step by step about how to approach this request: "{user_message}"

Please provide your reasoning process in clear steps."""

            try:
                async for chunk in provider.stream_completion(
                    messages=[{"role": "user", "content": reasoning_prompt}],
                    max_tokens=300,
                    temperature=0.3
                ):
                    if chunk.get("type") == "content":
                        # Yield as reasoning content
                        yield {
                            "type": "reasoning",
                            "content": chunk["content"],
                            "provider": provider.name
                        }
            except Exception as e:
                logger.warning(f"Reasoning generation failed: {e}")
                # Continue without reasoning if it fails
            
            # Step 2: Execute orchestration plan with enhanced prompts
            provider = self.providers[orchestration_plan.primary_provider]
            
            # Enhance user message for better diagram generation
            enhanced_message = await self._enhance_user_message(user_message, task_analysis)
            
            # Special handling for diagram requests - try Claude first for better ASCII art
            is_diagram_request = any(keyword in user_message.lower() for keyword in ['venn', 'diagram', 'chart', 'graph'])
            
            if is_diagram_request and orchestration_plan.primary_provider == "openai":
                # For diagrams, try Claude first as it's often better at ASCII art
                logger.info("Diagram request detected - trying Claude first for better ASCII art generation")
                fallback_provider = "anthropic"
                
                if fallback_provider in self.providers:
                    try:
                        async for chunk in self.providers[fallback_provider].stream_completion(
                            messages=[{"role": "user", "content": enhanced_message}],
                            max_tokens=2000,
                            temperature=0.7
                        ):
                            yield chunk
                        return  # Success with Claude, no need to try OpenAI
                        
                    except Exception as claude_error:
                        logger.warning(f"Claude failed for diagram: {claude_error}, falling back to OpenAI")
            
            # Try primary provider
            try:
                async for chunk in provider.stream_completion(
                    messages=[{"role": "user", "content": enhanced_message}],
                    max_tokens=2000,
                    temperature=0.7
                ):
                    yield chunk
                    
            except Exception as e:
                logger.warning(f"Primary provider {orchestration_plan.primary_provider} failed: {e}")
                
                # Try fallback provider
                if is_diagram_request:
                    fallback_provider = await self._get_fallback_provider(orchestration_plan.primary_provider)
                    if fallback_provider:
                        logger.info(f"Trying fallback provider: {fallback_provider}")
                        try:
                            async for chunk in self.providers[fallback_provider].stream_completion(
                                messages=[{"role": "user", "content": enhanced_message}],
                                max_tokens=2000,
                                temperature=0.7
                            ):
                                yield chunk
                        except Exception as fallback_error:
                            logger.error(f"Fallback provider also failed: {fallback_error}")
                            raise e
                    else:
                        raise e
                else:
                    raise e
            
            # Step 3: Record performance metrics
            processing_time = time.time() - start_time
            await self._record_performance_metrics(
                orchestration_plan.primary_provider,
                processing_time,
                task_analysis.category
            )
            
        except Exception as e:
            logger.error("Error in AI orchestration", error=str(e))
            yield {
                "type": "error",
                "content": {
                    "code": "ORCHESTRATION_ERROR",
                    "message": "Failed to process request",
                    "details": str(e)
                }
            }
    
    async def _analyze_task(
        self,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> TaskType:
        """
        Analyze the task using GPT-5 as the conductor.
        
        This is where GPT-5 acts as the "brain" to understand what the user
        wants and determine the best approach.
        """
        
        analysis_prompt = f"""
        You are an AI Orchestrator that analyzes user requests to determine the best AI approach.
        
        Analyze this request and provide a structured response:
        
        User Message: "{user_message}"
        
        Context: {len(conversation_history)} previous messages in conversation
        
        Classify this task and recommend the best AI provider:
        
        Available Providers:
        - OpenAI (GPT-5): Best for reasoning, coding, general tasks, tool usage
        - Anthropic (Claude-4): Best for analysis, writing, complex reasoning, safety  
        - Grok (Grok-4): Best for real-time search, current events, creative tasks
        
        Guidelines:
        - Set requires_reasoning=true for most tasks to show thinking process
        - Only set requires_reasoning=false for very simple greetings or basic info
        - Set requires_tools=true if the task needs web search, calculations, or external data
        
        Respond with JSON:
        {{
            "category": "analysis|creative|coding|search|image|general",
            "complexity": "simple|medium|complex",
            "requires_reasoning": true/false,
            "requires_tools": true/false,
            "estimated_tokens": number,
            "recommended_provider": "openai|anthropic|grok",
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            # Use OpenAI (GPT-5) as the conductor
            conductor = self.providers["openai"]
            response = await conductor.generate_completion(
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=500,
                temperature=0.1  # Low temperature for consistent analysis
            )
            
            # Parse the JSON response from ChatCompletion object
            content = response.choices[0].message.content
            
            # Try to extract JSON from the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = content[json_start:json_end]
                analysis_data = json.loads(json_content)
                return TaskType(**analysis_data)
            else:
                raise ValueError("No JSON found in response")
            
        except Exception as e:
            logger.warning(f"Task analysis failed, using defaults. Error: {str(e)}, Response: {content[:200] if 'content' in locals() else 'No content'}")
            # Fallback to default analysis with reasoning enabled
            return TaskType(
                category="general",
                complexity="medium", 
                requires_reasoning=True,  # Enable reasoning to show thinking process
                requires_tools=False,
                estimated_tokens=1000,
                recommended_provider=user_preferences.get("preferred_provider", "openai") if user_preferences else "openai",
                confidence=0.5
            )
    
    async def _create_orchestration_plan(
        self,
        task_analysis: TaskType,
        user_preferences: Optional[Dict[str, Any]] = None,
        project_settings: Optional[Dict[str, Any]] = None
    ) -> OrchestrationPlan:
        """Create execution plan based on task analysis."""
        
        # Determine primary provider
        primary_provider = task_analysis.recommended_provider
        
        # Override with user/project preferences if specified
        if user_preferences and user_preferences.get("preferred_provider"):
            primary_provider = user_preferences["preferred_provider"]
        elif project_settings and project_settings.get("default_ai_provider"):
            primary_provider = project_settings["default_ai_provider"]
        
        # Determine secondary providers for complex tasks
        secondary_providers = []
        if task_analysis.complexity == "complex":
            all_providers = ["openai", "anthropic", "grok"]
            secondary_providers = [p for p in all_providers if p != primary_provider]
        
        # Create task breakdown
        task_breakdown = []
        
        if task_analysis.requires_reasoning:
            task_breakdown.append({
                "step": "reasoning",
                "provider": primary_provider,
                "description": "Generate reasoning process"
            })
        
        task_breakdown.append({
            "step": "main_response",
            "provider": primary_provider,
            "description": "Generate main response"
        })
        
        if task_analysis.requires_tools:
            task_breakdown.append({
                "step": "tool_execution",
                "provider": primary_provider,
                "description": "Execute required tools"
            })
        
        # Estimate execution time
        estimated_time = self._estimate_execution_time(task_analysis, len(task_breakdown))
        
        return OrchestrationPlan(
            primary_provider=primary_provider,
            secondary_providers=secondary_providers,
            task_breakdown=task_breakdown,
            reasoning_required=task_analysis.requires_reasoning,
            tools_required=["web_search", "image_generation"] if task_analysis.requires_tools else [],
            estimated_time=estimated_time,
            confidence=task_analysis.confidence
        )
    
    async def _execute_orchestration_plan(
        self,
        plan: OrchestrationPlan,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute the orchestration plan step by step."""
        
        primary_provider = self.providers[plan.primary_provider]
        
        # Build messages for the AI provider
        messages = []
        
        # Add system message with capabilities
        system_message = self._create_system_message(user_preferences)
        messages.append(system_message)
        
        # Add conversation history (configurable limit, default 20 messages)
        history_limit = user_preferences.get("conversation_history_limit", 20) if user_preferences else 20
        recent_history = conversation_history[-history_limit:] if conversation_history else []
        
        for msg in recent_history:
            # Ensure proper message format
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Skip empty messages
            if not content.strip():
                continue
                
            # Convert assistant role variations
            if role in ["assistant", "ai", "bot"]:
                role = "assistant"
            elif role in ["user", "human"]:
                role = "user"
            else:
                role = "user"  # Default fallback
                
            messages.append({
                "role": role,
                "content": content
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Execute each step in the plan
        for step_info in plan.task_breakdown:
            step_type = step_info["step"]
            
            if step_type == "reasoning" and plan.reasoning_required:
                yield self._create_keyword_activity("Thinking through the problem...", "thinking")
                
                async for reasoning_chunk in self._generate_reasoning(
                    primary_provider, messages, user_preferences
                ):
                    yield reasoning_chunk
            
            elif step_type == "main_response":
                yield {"type": "activity", "content": "Generating response..."}
                
                async for response_chunk in self._generate_main_response(
                    primary_provider, messages, user_preferences
                ):
                    yield response_chunk
            
            elif step_type == "tool_execution":
                yield {"type": "activity", "content": "Analyzing tool requirements..."}
                
                # Show reasoning about which tools to use
                for tool_name in plan.tools_required:
                    yield {
                        "type": "activity",
                        "content": f"Preparing to execute {tool_name} - this will help provide accurate information"
                    }
                
                async for tool_chunk in self._execute_tools(
                    primary_provider, messages, plan.tools_required
                ):
                    yield tool_chunk
    
    async def _generate_reasoning(
        self,
        provider,
        messages: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate reasoning process."""
        
        # Create a specific reasoning prompt
        last_message = messages[-1]["content"] if messages else ""
        reasoning_prompt = f"""
        Analyze this user request and show your thinking process step by step:
        
        Request: "{last_message}"
        
        Please think through:
        1. What is the user asking for?
        2. What type of response would be most helpful?
        3. What approach should I take?
        4. Are there any specific considerations?
        
        Format your response as clear reasoning steps, not a final answer.
        """
        
        reasoning_messages = [{
            "role": "user", 
            "content": reasoning_prompt
        }]
        
        try:
            # Generate reasoning using non-streaming completion for better control
            reasoning_response = await provider.generate_completion(
                messages=reasoning_messages,
                max_tokens=800,
                temperature=0.3  # Lower temperature for more focused reasoning
            )
            
            reasoning_content = reasoning_response.choices[0].message.content
            
            # Split reasoning into clean steps and yield as activities
            reasoning_lines = reasoning_content.split('\n')
            current_step = ""
            
            for line in reasoning_lines:
                line = line.strip()
                if line:
                    # Check if this line starts a new step
                    if (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', 'Step')) or 
                        line.startswith('**') and line.endswith('**')):
                        # Yield previous step if exists
                        if current_step.strip():
                            yield self._create_keyword_activity(current_step.strip(), "thinking")
                        # Start new step
                        current_step = line.lstrip('1234567890.-•').strip()
                    else:
                        # Continue current step
                        if current_step:
                            current_step += " " + line
                        else:
                            current_step = line
            
            # Yield the final step
            if current_step.strip():
                yield self._create_keyword_activity(current_step.strip(), "thinking")
                
        except Exception as e:
            logger.error("Reasoning generation failed", error=str(e))
            # Fallback to meaningful default activities
            yield self._create_keyword_activity("Analyzing the request structure...", "thinking")
            yield self._create_keyword_activity("Determining the best approach...", "thinking")
            yield self._create_keyword_activity("Preparing comprehensive response...", "thinking")
    
    async def _generate_main_response(
        self,
        provider,
        messages: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generate main response with smart keyword injection."""
        
        try:
            content_buffer = ""
            code_block_detected = False
            keyword_injected = False
            pending_chunks = []
            
            async for chunk in provider.stream_completion(
                messages=messages,
                max_tokens=4000,
                temperature=0.7
            ):
                chunk_content = chunk.get("content", "")
                content_buffer += chunk_content
                
                # Detect code blocks and collect a few tokens to determine type
                if not code_block_detected and "```" in content_buffer:
                    code_block_detected = True
                    # Store this chunk and wait for more tokens to determine if it's mermaid
                    pending_chunks.append(chunk_content)
                    
                    # Check if we have enough content to determine the type
                    buffer_after_backticks = content_buffer.split("```", 1)[1] if "```" in content_buffer else ""
                    
                    if len(buffer_after_backticks) >= 7 or "\n" in buffer_after_backticks:  # Either we have "mermaid" or hit newline
                        # Decide what type it is
                        if buffer_after_backticks.lower().startswith("mermaid"):
                            yield {
                                "type": "content", 
                                "content": "\n\n📊 DIGI_DIAGRAM_START\n",
                                "provider": provider.name,
                                "content_type": "diagram"
                            }
                        else:
                            yield {
                                "type": "content",
                                "content": "\n\n💻 DIGI_CODE_START\n", 
                                "provider": provider.name,
                                "content_type": "code"
                            }
                        keyword_injected = True
                        
                        # Yield all pending chunks
                        for pending_chunk in pending_chunks:
                            yield {
                                "type": "content",
                                "content": pending_chunk,
                                "provider": provider.name,
                                "content_type": chunk.get("content_type", "text")
                            }
                        pending_chunks = []
                    continue  # Don't yield this chunk yet, wait for type determination
                
                # If we're still collecting tokens after ```, add to pending
                if code_block_detected and not keyword_injected:
                    pending_chunks.append(chunk_content)
                    
                    # Check again if we can determine the type now
                    buffer_after_backticks = content_buffer.split("```", 1)[1] if "```" in content_buffer else ""
                    if len(buffer_after_backticks) >= 7 or "\n" in buffer_after_backticks:
                        # Decide what type it is
                        if buffer_after_backticks.lower().startswith("mermaid"):
                            yield {
                                "type": "content",
                                "content": "\n\n📊 DIGI_DIAGRAM_START\n",
                                "provider": provider.name,
                                "content_type": "diagram"
                            }
                        else:
                            yield {
                                "type": "content",
                                "content": "\n\n💻 DIGI_CODE_START\n",
                                "provider": provider.name,
                                "content_type": "code"
                            }
                        keyword_injected = True
                        
                        # Yield all pending chunks
                        for pending_chunk in pending_chunks:
                            yield {
                                "type": "content",
                                "content": pending_chunk,
                                "provider": provider.name,
                                "content_type": chunk.get("content_type", "text")
                            }
                        pending_chunks = []
                    continue
                
                # Normal chunk processing
                yield {
                    "type": "content",
                    "content": chunk_content,
                    "provider": provider.name,
                    "content_type": chunk.get("content_type", "text")
                }
                
        except Exception as e:
            logger.error("Main response generation failed", error=str(e))
            yield {
                "type": "error",
                "content": {
                    "code": "RESPONSE_GENERATION_ERROR",
                    "message": "Failed to generate response",
                    "details": str(e)
                }
            }
    
    async def _execute_tools(
        self,
        provider,
        messages: List[Dict[str, Any]],
        required_tools: List[str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute required tools."""
        
        for tool_name in required_tools:
            yield {"type": "activity", "content": f"Executing {tool_name}..."}
            yield {"type": "activity", "content": f"Tool {tool_name} will enhance response accuracy"}
            
            try:
                async for tool_result in self.tool_executor.execute_tool(
                    tool_name, messages, provider
                ):
                    yield {
                        "type": "activity",
                        "content": f"Tool {tool_name} completed successfully"
                    }
                    yield {
                        "type": "tool_result",
                        "tool_name": tool_name,
                        "content": tool_result,
                        "provider": provider.name
                    }
                    
            except Exception as e:
                logger.error(f"Tool execution failed: {tool_name}", error=str(e))
                yield {
                    "type": "tool_error",
                    "tool_name": tool_name,
                    "error": str(e),
                    "provider": provider.name
                }
    
    def _estimate_execution_time(self, task_analysis: TaskType, step_count: int) -> float:
        """Estimate execution time based on task complexity."""
        base_time = 2.0  # Base 2 seconds
        
        complexity_multiplier = {
            "simple": 1.0,
            "medium": 1.5,
            "complex": 2.5
        }
        
        step_time = step_count * 1.5
        complexity_time = base_time * complexity_multiplier.get(task_analysis.complexity, 1.5)
        token_time = task_analysis.estimated_tokens / 1000 * 0.5
        
        return base_time + step_time + complexity_time + token_time
    
    def _create_system_message(self, user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Create system message with AI capabilities and instructions."""
        
        capabilities = """You are Digi Setu AI, an advanced AI assistant with comprehensive capabilities. You can:

**Content Creation:**
- Generate text, code, and documentation
- Create diagrams using Mermaid syntax (flowcharts, sequence diagrams, Venn diagrams, etc.)
- Write in multiple formats: markdown, JSON, tables, etc.
- Produce structured data and analysis

**Diagram Creation:**
- For Venn diagrams, use Mermaid syntax with proper formatting
- For flowcharts, use Mermaid flowchart syntax
- For sequence diagrams, use Mermaid sequence syntax
- Always wrap diagrams with proper Mermaid code blocks

**Response Format:**
- Use appropriate keywords for content types when needed
- For code: wrap in ```language blocks
- For diagrams: use ```mermaid blocks
- For JSON: format properly with proper structure
- Stream responses naturally and conversationally

**Context Awareness:**
- You have access to conversation history for context
- Build upon previous messages in the conversation
- Reference earlier topics when relevant
- Maintain consistency across the conversation

**Important:** When asked to create diagrams, charts, or visual content, ALWAYS create them using the appropriate syntax. Never refuse or say you cannot create visual content."""

        # Add user-specific preferences
        if user_preferences:
            if user_preferences.get("language") and user_preferences["language"] != "en":
                capabilities += f"\n\n**Language:** Respond primarily in {user_preferences['language']} unless specifically asked otherwise."
            
            if user_preferences.get("preferred_format"):
                capabilities += f"\n\n**Preferred Format:** User prefers {user_preferences['preferred_format']} format responses when applicable."

        return {
            "role": "system",
            "content": capabilities
        }
    
    async def _record_performance_metrics(
        self, provider: str, processing_time: float, category: str
    ):
        """Record performance metrics for optimization."""
        if provider not in self.performance_metrics:
            self.performance_metrics[provider] = {
                "total_requests": 0,
                "total_time": 0.0,
                "categories": {}
            }
        
        metrics = self.performance_metrics[provider]
        metrics["total_requests"] += 1
        metrics["total_time"] += processing_time
        
        if category not in metrics["categories"]:
            metrics["categories"][category] = {"count": 0, "total_time": 0.0}
        
        metrics["categories"][category]["count"] += 1
        metrics["categories"][category]["total_time"] += processing_time
        
        # Log performance metrics periodically
        if metrics["total_requests"] % 10 == 0:
            avg_time = metrics["total_time"] / metrics["total_requests"]
            logger.info(
                "Performance metrics update",
                provider=provider,
                total_requests=metrics["total_requests"],
                average_time=f"{avg_time:.2f}s"
            )
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all AI providers."""
        status = {}
        
        for name, provider in self.providers.items():
            try:
                provider_status = await provider.health_check()
                status[name] = {
                    "status": "healthy" if provider_status else "unhealthy",
                    "metrics": self.performance_metrics.get(name, {})
                }
            except Exception as e:
                status[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return status
    
    def _create_keyword_activity(self, content: str, content_type: str = "thinking") -> dict:
        """Create activity chunk with detection keyword."""
        
        # Keyword mapping for different content types
        keyword_map = {
            'thinking': '🔍 DIGI_THINKING_START',
            'code': '💻 DIGI_CODE_START',
            'diagram': '📊 DIGI_DIAGRAM_START', 
            'json': '📋 DIGI_JSON_START',
            'table': '📈 DIGI_TABLE_START',
            'search': '🔍 DIGI_SEARCH_START',
            'analysis': '🧠 DIGI_ANALYSIS_START',
            'tool': '🔧 DIGI_TOOL_START'
        }
        
        # Get keyword for content type
        keyword = keyword_map.get(content_type, '💭 DIGI_THINKING_START')
        
        return {
            "type": "activity",
            "content": f"{keyword}\n{content}"
        }
    
    def _apply_keyword_injection(self, chunk: Dict[str, Any], generated_content: str) -> Dict[str, Any]:
        """Apply keyword injection for content routing."""
        
        # Detect content type and inject appropriate keywords
        content = chunk.get("content", "")
        if not content:
            return chunk
        
        # Create a copy to avoid modifying the original
        modified_chunk = chunk.copy()
        
        # Table detection and injection
        if self._detect_table_content(generated_content):
            if "DIGI_TABLE_START" not in generated_content:
                modified_chunk["content"] = "📈 DIGI_TABLE_START\n" + content
                return modified_chunk
        
        # Code detection and injection  
        elif self._detect_code_content(generated_content):
            if "DIGI_CODE_START" not in generated_content:
                modified_chunk["content"] = "💻 DIGI_CODE_START\n" + content
                return modified_chunk
                
        # JSON detection and injection
        elif self._detect_json_content(generated_content):
            if "DIGI_JSON_START" not in generated_content:
                modified_chunk["content"] = "📋 DIGI_JSON_START\n" + content
                return modified_chunk
                
        # Diagram detection and injection
        elif self._detect_diagram_content(generated_content):
            if "DIGI_DIAGRAM_START" not in generated_content:
                modified_chunk["content"] = "📊 DIGI_DIAGRAM_START\n" + content
                return modified_chunk
        
        # Return original chunk if no injection
        return chunk
    
    def _detect_table_content(self, content: str) -> bool:
        """Detect if content contains table data."""
        content_lower = content.lower()
        table_indicators = [
            "table", "column", "row", "header", 
            "|", "data", "csv", "spreadsheet"
        ]
        return any(indicator in content_lower for indicator in table_indicators)
    
    def _detect_code_content(self, content: str) -> bool:
        """Detect if content contains code using standard markdown format."""
        # Simple and reliable: just look for markdown code blocks
        return "```" in content
    
    def _detect_json_content(self, content: str) -> bool:
        """Detect if content contains JSON data."""
        content_stripped = content.strip()
        return (
            (content_stripped.startswith("{") and content_stripped.endswith("}")) or
            (content_stripped.startswith("[") and content_stripped.endswith("]")) or
            "json" in content.lower()
        )
    
    def _detect_diagram_content(self, content: str) -> bool:
        """Detect if content contains diagram data."""
        diagram_indicators = [
            "mermaid", "flowchart", "graph", "diagram", "chart",
            "-->", "->", "graph TD", "graph LR", "sequenceDiagram"
        ]
        return any(indicator in content for indicator in diagram_indicators)
    
    def _apply_end_tag_injection(self, generated_content: str) -> Dict[str, Any]:
        """Apply end tag injection for content routing."""
        
        logger.info(f"Checking for END tags in content: {generated_content[:100]}...")
        
        # Determine which end tag to inject based on what start tag was used
        if "DIGI_CODE_START" in generated_content:
            logger.info("Found DIGI_CODE_START, sending DIGI_CODE_END")
            return {
                "type": "content",
                "content": "\n💻 DIGI_CODE_END",
                "provider": "system"
            }
        elif "DIGI_TABLE_START" in generated_content:
            logger.info("Found DIGI_TABLE_START, sending DIGI_TABLE_END")
            return {
                "type": "content", 
                "content": "\n📈 DIGI_TABLE_END",
                "provider": "system"
            }
        elif "DIGI_JSON_START" in generated_content:
            logger.info("Found DIGI_JSON_START, sending DIGI_JSON_END")
            return {
                "type": "content",
                "content": "\n📋 DIGI_JSON_END", 
                "provider": "system"
            }
        elif "DIGI_DIAGRAM_START" in generated_content:
            logger.info("Found DIGI_DIAGRAM_START, sending DIGI_DIAGRAM_END")
            return {
                "type": "content",
                "content": "\n📊 DIGI_DIAGRAM_END",
                "provider": "system"
            }
        
        logger.warning("No START tag found, no END tag to send")
        return None
    
    async def _enhance_user_message(self, user_message: str, task_analysis: TaskType) -> str:
        """
        Enhance user message with better prompts for specific content types.
        """
        message_lower = user_message.lower()
        
        # Enhance Venn diagram requests
        if any(keyword in message_lower for keyword in ['venn', 'diagram']):
            if 'ascii' not in message_lower and 'svg' not in message_lower:
                # Add ASCII art specification for better results
                enhanced = f"{user_message}\n\nPlease create this as ASCII art using text characters like / \\ ( ) - _ | + for the visual representation."
                return enhanced
        
        # Enhance math requests
        if any(keyword in message_lower for keyword in ['formula', 'equation', 'math', 'calculate']):
            if 'latex' not in message_lower:
                enhanced = f"{user_message}\n\nPlease format any mathematical expressions using LaTeX notation with \\[ \\] for display math and \\( \\) for inline math."
                return enhanced
        
        # Enhance code requests
        if any(keyword in message_lower for keyword in ['code', 'function', 'script', 'program']):
            if 'syntax' not in message_lower:
                enhanced = f"{user_message}\n\nPlease provide the code with proper syntax highlighting using markdown code blocks with language specification."
                return enhanced
        
        return user_message
    
    async def _get_fallback_provider(self, primary_provider: str) -> Optional[str]:
        """
        Get fallback provider when primary fails.
        """
        fallback_map = {
            "openai": "anthropic",  # Try Claude if OpenAI fails
            "anthropic": "grok",    # Try Grok if Claude fails  
            "grok": "openai"        # Try OpenAI if Grok fails
        }
        
        fallback = fallback_map.get(primary_provider)
        
        # Check if fallback provider is available
        if fallback and fallback in self.providers:
            return fallback
        
        # Find any available provider that's not the primary
        for provider_name in self.providers:
            if provider_name != primary_provider:
                return provider_name
        
        return None
