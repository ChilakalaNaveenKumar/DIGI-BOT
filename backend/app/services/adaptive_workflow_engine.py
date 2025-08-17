"""
Adaptive Workflow Engine

Replaces the static orchestrator with an intelligent workflow engine
that can adapt and make decisions at each step based on accumulated context.
"""

import asyncio
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

import structlog
from pydantic import BaseModel

from app.services.workflow_context import WorkflowContext
from app.services.ai_decision_engine import AIDecisionEngine, NextStepPlan
from app.services.activity_streamer import ActivityStreamer
from app.services.tool_executor import ToolExecutor
from app.services.coordinated_tool_executor import CoordinatedToolExecutor
from app.services.conditional_execution_engine import ConditionalExecutionEngine

logger = structlog.get_logger(__name__)


class WorkflowResult(BaseModel):
    """Final result of workflow execution."""
    success: bool
    workflow_id: str
    total_steps: int
    execution_time: float
    final_content: str
    context_summary: str
    decisions_made: int
    error_message: Optional[str] = None


class AdaptiveWorkflowEngine:
    """
    Adaptive workflow engine with AI-driven decision making.
    
    Features:
    - Context accumulation across steps
    - AI decision points between steps
    - Dynamic workflow adaptation
    - Quality assessment loops
    - Tool coordination
    - Error recovery
    """
    
    def __init__(self, ai_providers: Dict[str, Any]):
        self.ai_providers = ai_providers
        self.decision_engine = None  # Will be initialized with primary provider
        self.activity_streamer = ActivityStreamer()
        self.tool_executor = ToolExecutor()
        self.coordinated_tool_executor = CoordinatedToolExecutor()
        self.conditional_engine = ConditionalExecutionEngine()
        
        # Workflow management
        self.active_workflows: Dict[str, WorkflowContext] = {}
        self.max_workflow_steps = 20  # Prevent infinite loops
        
    async def initialize(self):
        """Initialize the workflow engine."""
        try:
            # Initialize decision engine with primary AI provider
            primary_provider = self.ai_providers.get("openai") or list(self.ai_providers.values())[0]
            self.decision_engine = AIDecisionEngine(primary_provider)
            
            # Initialize supporting services
            await self.activity_streamer.initialize()
            await self.tool_executor.initialize()
            await self.coordinated_tool_executor.initialize()
            
            # Initialize conditional execution engine with default rules
            self._setup_default_conditional_rules()
            
            logger.info("Adaptive workflow engine initialized")
            
        except Exception as e:
            logger.error("Failed to initialize adaptive workflow engine", error=str(e))
            raise
    
    async def execute_adaptive_workflow(
        self,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]] = None,
        project_settings: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute an adaptive workflow with AI decision points.
        
        Args:
            user_message: User's input message
            conversation_history: Previous conversation context
            user_preferences: User's AI preferences
            project_settings: Project-specific settings
            
        Yields:
            Streaming response chunks with activity updates
        """
        start_time = time.time()
        
        # Create workflow context
        context = WorkflowContext()
        context.set_initial_context(user_message, user_preferences)
        self.active_workflows[context.workflow_id] = context
        
        try:
            yield self._create_activity("🧠 Initializing adaptive workflow...", "activity")
            
            # Step 1: Initial AI analysis of the request
            yield self._create_activity("🔍 Understanding your request...", "analysis")
            
            analysis_result = await self._perform_initial_analysis(
                user_message, conversation_history, context
            )
            
            yield self._create_activity(
                f"✅ Request analyzed: {analysis_result.get('task_type', 'general')} task detected",
                "analysis"
            )
            
            # Step 2: AI-driven workflow execution with decision points
            step_count = 0
            remaining_goals = [user_message]  # Start with the original request as goal
            
            while remaining_goals and step_count < self.max_workflow_steps:
                step_count += 1
                
                if step_count == 1:
                    yield self._create_activity("🎯 Planning approach...", "activity")
                else:
                    yield self._create_activity("🎯 Refining response...", "activity")
                
                # AI decides next steps
                next_steps = await self.decision_engine.plan_next_steps(
                    context, remaining_goals
                )
                
                if not next_steps:
                    logger.info("No more steps planned, workflow complete")
                    break
                
                # Execute planned steps
                for step_plan in next_steps:
                    # Create user-friendly activity message
                    friendly_message = self._create_friendly_activity_message(step_plan)
                    yield self._create_activity(friendly_message, "execution")
                    
                    # Execute the step
                    step_result = await self._execute_workflow_step(
                        step_plan, context, user_message, conversation_history
                    )
                    
                    # Yield step results
                    if step_result.get("stream_chunks"):
                        for chunk in step_result["stream_chunks"]:
                            yield chunk
                    
                    # Check if we should continue or if goals are met
                    if step_result.get("goals_completed"):
                        remaining_goals = []
                        break
                    
                    # Update remaining goals based on step result
                    remaining_goals = step_result.get("remaining_goals", remaining_goals)
                
                # AI decision point: Should we continue?
                if remaining_goals and step_count < self.max_workflow_steps:
                    should_continue = await self._should_continue_workflow(context, remaining_goals)
                    if not should_continue:
                        yield self._create_activity("✅ Workflow goals achieved, completing...", "completion")
                        break
            
            # Step 3: Final quality assessment and refinement
            yield self._create_activity("✅ Finalizing response...", "quality")
            
            final_result = await self._perform_final_assessment(context, user_message)
            
            # Generate final workflow result
            workflow_result = WorkflowResult(
                success=True,
                workflow_id=context.workflow_id,
                total_steps=len(context.steps),
                execution_time=time.time() - start_time,
                final_content=final_result.get("content", ""),
                context_summary=context._generate_context_summary(),
                decisions_made=len(context.decisions)
            )
            
            yield {
                "type": "workflow_complete",
                "content": workflow_result.dict()
            }
            
            logger.info(
                "Adaptive workflow completed",
                workflow_id=context.workflow_id,
                total_steps=workflow_result.total_steps,
                execution_time=workflow_result.execution_time
            )
            
        except Exception as e:
            logger.error(
                "Error in adaptive workflow execution",
                workflow_id=context.workflow_id,
                error=str(e)
            )
            
            yield {
                "type": "error",
                "content": {
                    "code": "WORKFLOW_ERROR",
                    "message": "Workflow execution failed",
                    "details": str(e),
                    "workflow_id": context.workflow_id
                }
            }
        
        finally:
            # Clean up workflow context
            if context.workflow_id in self.active_workflows:
                del self.active_workflows[context.workflow_id]
    
    async def _perform_initial_analysis(
        self,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        context: WorkflowContext
    ) -> Dict[str, Any]:
        """Perform initial AI analysis of the user request."""
        
        # Create analysis prompt
        analysis_prompt = f"""
        Analyze this user request and determine the best approach:
        
        Request: "{user_message}"
        
        Context: {len(conversation_history)} previous messages
        
        Determine:
        1. Task type (analysis, creative, coding, search, data, visual)
        2. Complexity level (simple, medium, complex)
        3. Required capabilities (reasoning, tools, generation)
        4. Success criteria
        5. Potential challenges
        
        Respond with JSON:
        {{
            "task_type": "analysis|creative|coding|search|data|visual|general",
            "complexity": "simple|medium|complex",
            "requires_reasoning": true/false,
            "requires_tools": true/false,
            "requires_generation": true/false,
            "success_criteria": ["criterion1", "criterion2"],
            "challenges": ["challenge1", "challenge2"],
            "estimated_steps": 3
        }}
        """
        
        try:
            primary_provider = list(self.ai_providers.values())[0]
            response = await primary_provider.generate_completion(
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            import json
            analysis_result = json.loads(response.choices[0].message.content)
            
            # Record the analysis result
            context.add_step_result(
                step_name="initial_analysis",
                step_type="analysis",
                result=analysis_result,
                execution_time=1.0
            )
            
            return analysis_result
            
        except Exception as e:
            logger.warning("Initial analysis failed, using defaults", error=str(e))
            
            # Fallback analysis
            fallback_result = {
                "task_type": "general",
                "complexity": "medium",
                "requires_reasoning": True,
                "requires_tools": False,
                "requires_generation": True,
                "success_criteria": ["Address user request"],
                "challenges": ["Understanding intent"],
                "estimated_steps": 2
            }
            
            context.add_step_result(
                step_name="initial_analysis",
                step_type="analysis",
                result=fallback_result,
                execution_time=1.0
            )
            
            return fallback_result
    
    async def _execute_workflow_step(
        self,
        step_plan: NextStepPlan,
        context: WorkflowContext,
        original_message: str,
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a single workflow step based on the plan."""
        
        start_time = time.time()
        step_result = {
            "success": False,
            "stream_chunks": [],
            "goals_completed": False,
            "remaining_goals": []
        }
        
        try:
            if step_plan.step_type == "generation":
                step_result = await self._execute_generation_step(
                    step_plan, context, original_message, conversation_history
                )
                
            elif step_plan.step_type == "tool_execution":
                step_result = await self._execute_tool_step(
                    step_plan, context, original_message
                )
                
            elif step_plan.step_type == "quality_check":
                step_result = await self._execute_quality_step(
                    step_plan, context, original_message
                )
                
            elif step_plan.step_type == "analysis":
                step_result = await self._execute_analysis_step(
                    step_plan, context, original_message
                )
            
            else:
                # Default to generation
                step_result = await self._execute_generation_step(
                    step_plan, context, original_message, conversation_history
                )
            
            # Record step completion
            execution_time = time.time() - start_time
            context.add_step_result(
                step_name=step_plan.step_name,
                step_type=step_plan.step_type,
                result=step_result.get("result"),
                execution_time=execution_time,
                success=step_result["success"]
            )
            
            context.mark_step_complete(step_plan.step_name)
            
            return step_result
            
        except Exception as e:
            logger.error(
                "Step execution failed",
                step_name=step_plan.step_name,
                error=str(e)
            )
            
            execution_time = time.time() - start_time
            context.add_step_result(
                step_name=step_plan.step_name,
                step_type=step_plan.step_type,
                result=None,
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
            
            return {
                "success": False,
                "stream_chunks": [{
                    "type": "error",
                    "content": f"Step {step_plan.step_name} failed: {str(e)}"
                }],
                "goals_completed": False,
                "remaining_goals": []
            }
    
    async def _execute_generation_step(
        self,
        step_plan: NextStepPlan,
        context: WorkflowContext,
        original_message: str,
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a content generation step."""
        
        # Build context-aware prompt
        context_data = context.get_context_for_next_step("generation")
        
        # Create messages for AI provider
        messages = self._build_messages_for_generation(
            original_message, conversation_history, context_data, step_plan
        )
        
        # Select appropriate AI provider
        provider = self._select_provider_for_step(step_plan, context)
        
        # Stream generation
        stream_chunks = []
        generated_content = ""
        keyword_injected = False
        
        async for chunk in provider.stream_completion(
            messages=messages,
            max_tokens=4000,
            temperature=0.7
        ):
            chunk_content = chunk.get("content", "")
            generated_content += chunk_content
            
            # Apply keyword injection only once at the beginning
            if not keyword_injected and len(generated_content.strip()) > 10:
                processed_chunk = self._apply_keyword_injection(chunk, generated_content)
                keyword_injected = True
            else:
                processed_chunk = chunk
                
            stream_chunks.append(processed_chunk)
        
        # Quality assessment and refinement if needed
        if len(generated_content) > 50:  # Only assess substantial content
            try:
                # Assess quality and refine if below threshold
                refined_content, final_assessment = await self.decision_engine.assess_and_refine_if_needed(
                    generated_content, original_message, context, quality_threshold=0.7
                )
                
                # If content was refined, add refinement chunks
                if refined_content != generated_content:
                    stream_chunks.append({
                        "type": "quality_refinement",
                        "original_score": final_assessment.overall_score if hasattr(final_assessment, 'overall_score') else 0.7,
                        "content": refined_content
                    })
                    generated_content = refined_content
                
            except Exception as e:
                logger.warning("Quality assessment failed, using original content", error=str(e))
        
        return {
            "success": True,
            "result": generated_content,
            "stream_chunks": stream_chunks,
            "goals_completed": len(generated_content) > 100,  # Simple completion check
            "remaining_goals": []
        }
    
    async def _execute_tool_step(
        self,
        step_plan: NextStepPlan,
        context: WorkflowContext,
        original_message: str
    ) -> Dict[str, Any]:
        """Execute a tool execution step."""
        
        stream_chunks = []
        tool_results = {}
        
        for tool_name in step_plan.tool_names:
            stream_chunks.append({
                "type": "activity",
                "content": f"🔧 Executing {tool_name}..."
            })
            
            try:
                # Execute tool with context
                tool_result = await self.tool_executor.execute_tool_with_context(
                    tool_name, original_message, context.get_context_for_next_step()
                )
                
                tool_results[tool_name] = tool_result
                
                stream_chunks.append({
                    "type": "tool_result",
                    "tool_name": tool_name,
                    "content": tool_result
                })
                
            except Exception as e:
                logger.error(f"Tool {tool_name} execution failed", error=str(e))
                stream_chunks.append({
                    "type": "tool_error",
                    "tool_name": tool_name,
                    "error": str(e)
                })
        
        return {
            "success": len(tool_results) > 0,
            "result": tool_results,
            "stream_chunks": stream_chunks,
            "goals_completed": False,
            "remaining_goals": []
        }
    
    async def _execute_quality_step(
        self,
        step_plan: NextStepPlan,
        context: WorkflowContext,
        original_message: str
    ) -> Dict[str, Any]:
        """Execute a quality assessment step."""
        
        # Get the latest generated content
        latest_content = None
        for step in reversed(context.steps):
            if step.step_type == "generation" and step.success:
                latest_content = step.result
                break
        
        if not latest_content:
            return {
                "success": False,
                "result": "No content to assess",
                "stream_chunks": [],
                "goals_completed": True,
                "remaining_goals": []
            }
        
        # Perform quality assessment
        assessment = await self.decision_engine.assess_quality(
            latest_content, original_message, context
        )
        
        stream_chunks = [{
            "type": "quality_assessment",
            "content": {
                "score": assessment.overall_score,
                "needs_improvement": assessment.needs_improvement,
                "strengths": assessment.strengths,
                "suggestions": assessment.suggestions
            }
        }]
        
        return {
            "success": True,
            "result": assessment,
            "stream_chunks": stream_chunks,
            "goals_completed": not assessment.needs_improvement,
            "remaining_goals": assessment.suggestions if assessment.needs_improvement else []
        }
    
    async def _execute_analysis_step(
        self,
        step_plan: NextStepPlan,
        context: WorkflowContext,
        original_message: str
    ) -> Dict[str, Any]:
        """Execute an analysis step."""
        
        # Create analysis prompt based on step parameters
        analysis_prompt = f"""
        Perform detailed analysis for: {step_plan.step_name}
        
        Original request: {original_message}
        Current context: {context.get_context_for_next_step('analysis')}
        
        Focus on: {step_plan.reasoning}
        """
        
        provider = list(self.ai_providers.values())[0]
        response = await provider.generate_completion(
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=800,
            temperature=0.3
        )
        
        analysis_result = response.choices[0].message.content
        
        return {
            "success": True,
            "result": analysis_result,
            "stream_chunks": [{
                "type": "analysis_result",
                "content": analysis_result
            }],
            "goals_completed": False,
            "remaining_goals": []
        }
    
    async def _should_continue_workflow(
        self,
        context: WorkflowContext,
        remaining_goals: List[str]
    ) -> bool:
        """AI decides whether to continue the workflow."""
        
        if not remaining_goals:
            return False
        
        if len(context.steps) >= self.max_workflow_steps:
            return False
        
        # Simple heuristic for now - could be enhanced with AI decision
        return len(remaining_goals) > 0 and len(context.steps) < 10
    
    async def _perform_final_assessment(
        self,
        context: WorkflowContext,
        original_message: str
    ) -> Dict[str, Any]:
        """Perform final quality assessment of the workflow result."""
        
        # Get the final generated content
        final_content = ""
        for step in reversed(context.steps):
            if step.step_type == "generation" and step.success and step.result:
                final_content = step.result
                break
        
        if not final_content:
            final_content = "Workflow completed without final content generation."
        
        # Perform final quality check
        assessment = await self.decision_engine.assess_quality(
            final_content, original_message, context
        )
        
        return {
            "content": final_content,
            "assessment": assessment,
            "context_summary": context._generate_context_summary()
        }
    
    def _build_messages_for_generation(
        self,
        original_message: str,
        conversation_history: List[Dict[str, Any]],
        context_data: Dict[str, Any],
        step_plan: NextStepPlan
    ) -> List[Dict[str, str]]:
        """Build messages for AI generation with context."""
        
        messages = []
        
        # System message with context awareness
        system_content = f"""You are Digi Setu AI executing step: {step_plan.step_name}

Step purpose: {step_plan.reasoning}

Current context:
- Original query: {original_message}
- Steps completed: {context_data.get('steps_completed', 0)}
- Key insights: {context_data.get('key_insights', {})}
- Previous results available: {len(context_data.get('previous_results', []))}

Generate content that builds upon the existing context and moves toward completing the user's request."""
        
        messages.append({"role": "system", "content": system_content})
        
        # Add relevant conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages
            if msg.get("content"):
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg["content"]
                })
        
        # Add current request
        messages.append({"role": "user", "content": original_message})
        
        return messages
    
    def _select_provider_for_step(
        self,
        step_plan: NextStepPlan,
        context: WorkflowContext
    ) -> Any:
        """Select the best AI provider for the current step."""
        
        # Simple provider selection logic - can be enhanced
        if step_plan.step_type == "analysis":
            return self.ai_providers.get("anthropic") or list(self.ai_providers.values())[0]
        elif step_plan.requires_tools:
            return self.ai_providers.get("openai") or list(self.ai_providers.values())[0]
        else:
            return list(self.ai_providers.values())[0]
    
    def _apply_keyword_injection(self, chunk: Dict[str, Any], full_content: str) -> Dict[str, Any]:
        """Apply keyword injection for content routing."""
        
        chunk_content = chunk.get("content", "")
        
        # Detect if we need to inject keywords for content routing
        if "```" in full_content and "DIGI_CODE_START" not in full_content:
            # Inject code keyword
            if chunk_content and "```" in chunk_content:
                chunk["content"] = "\n\n💻 DIGI_CODE_START\n" + chunk_content
                chunk["content_type"] = "code"
        
        elif full_content.strip().startswith(("{", "[")) and "DIGI_JSON_START" not in full_content:
            # Inject JSON keyword
            if len(full_content) > 10:  # Only after we have some content
                chunk["content"] = "\n\n📋 DIGI_JSON_START\n" + chunk_content
                chunk["content_type"] = "json"
        
        return chunk
    
    def _create_activity(self, content: str, activity_type: str = "thinking") -> Dict[str, Any]:
        """Create activity chunk with detection keyword."""
        
        keyword_map = {
            'thinking': '🔍 DIGI_THINKING_START',
            'analysis': '🧠 DIGI_ANALYSIS_START',
            'execution': '⚡ DIGI_EXECUTION_START',
            'quality': '✅ DIGI_QUALITY_START',
            'completion': '🎯 DIGI_COMPLETION_START'
        }
        
        keyword = keyword_map.get(activity_type, '💭 DIGI_THINKING_START')
        
        return {
            "type": "activity",
            "content": f"{keyword}\n{content}"
        }
    
    async def cleanup(self):
        """Cleanup workflow engine resources."""
        await self.activity_streamer.cleanup()
        await self.tool_executor.cleanup()
        await self.coordinated_tool_executor.cleanup()
        
        logger.info("Adaptive workflow engine cleaned up")
    
    def _setup_default_conditional_rules(self):
        """Setup default conditional rules for common scenarios."""
        
        # Import ActionType from the conditional execution engine module
        from app.services.conditional_execution_engine import ActionType
        
        # Quality improvement rule
        quality_rule = self.conditional_engine.create_quality_rule(
            quality_threshold=0.7,
            action_type=ActionType.RETRY_STEP
        )
        self.conditional_engine.add_rule(quality_rule)
        
        # Performance optimization rule
        performance_rule = self.conditional_engine.create_performance_rule(
            max_execution_time=30.0
        )
        self.conditional_engine.add_rule(performance_rule)
        
        # Error recovery rule
        from app.services.conditional_execution_engine import ConditionalRule, Condition, ConditionalAction, ConditionType
        
        error_condition = Condition(
            condition_id="error_threshold",
            condition_type=ConditionType.ERROR_COUNT,
            operator=">=",
            threshold=2,
            description="Too many errors encountered",
            priority=3
        )
        
        error_action = ConditionalAction(
            action_id="error_recovery",
            action_type=ActionType.CHANGE_PROVIDER,
            target="current_step",
            parameters={"provider": "anthropic"},  # Switch to more reliable provider
            description="Switch provider due to errors"
        )
        
        error_rule = ConditionalRule(
            rule_id="error_recovery_rule",
            name="Error Recovery Rule",
            conditions=[error_condition],
            actions=[error_action]
        )
        
        self.conditional_engine.add_rule(error_rule)
        
        logger.info("Default conditional rules configured")
    
    def _apply_keyword_injection(self, chunk: Dict[str, Any], generated_content: str) -> Dict[str, Any]:
        """Apply keyword injection for content routing."""
        
        # Detect content type and inject appropriate keywords
        content = chunk.get("content", "")
        if not content:
            return chunk
        
        # Table detection and injection
        if self._detect_table_content(generated_content):
            if "DIGI_TABLE_START" not in generated_content:
                chunk["content"] = "📈 DIGI_TABLE_START\n" + content
        
        # Code detection and injection  
        elif self._detect_code_content(generated_content):
            if "DIGI_CODE_START" not in generated_content:
                chunk["content"] = "💻 DIGI_CODE_START\n" + content
                
        # JSON detection and injection
        elif self._detect_json_content(generated_content):
            if "DIGI_JSON_START" not in generated_content:
                chunk["content"] = "📋 DIGI_JSON_START\n" + content
                
        # Diagram detection and injection
        elif self._detect_diagram_content(generated_content):
            if "DIGI_DIAGRAM_START" not in generated_content:
                chunk["content"] = "📊 DIGI_DIAGRAM_START\n" + content
        
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
        """Detect if content contains code."""
        code_indicators = [
            "function", "class", "def ", "import", "const ", "let ", "var ",
            "```", "def(", "function(", "class ", "public ", "private ",
            "return", "if(", "for(", "while(", "{", "}", ";"
        ]
        return any(indicator in content for indicator in code_indicators)
    
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
    
    def _create_friendly_activity_message(self, step_plan) -> str:
        """Create user-friendly activity messages instead of technical details."""
        
        # Map technical step names to friendly messages
        friendly_messages = {
            "continue_processing": "✨ Generating your response...",
            "generate_content": "✨ Creating content for you...",
            "analyze_request": "🔍 Understanding your request...",
            "generate_response": "💭 Crafting a thoughtful response...",
            "explain_bubble_chart": "📊 Explaining bubble charts...",
            "create_table": "📋 Creating a table...",
            "generate_code": "💻 Writing code...",
            "create_diagram": "📈 Drawing a diagram...",
            "search_information": "🔍 Searching for information...",
            "process_data": "⚙️ Processing data...",
        }
        
        step_name = step_plan.step_name.lower()
        
        # Check for exact matches first
        if step_name in friendly_messages:
            return friendly_messages[step_name]
        
        # Check for partial matches
        for key, message in friendly_messages.items():
            if key in step_name or step_name in key:
                return message
        
        # Fallback: create a generic friendly message
        if "generate" in step_name:
            return "✨ Generating content..."
        elif "analyze" in step_name:
            return "🔍 Analyzing..."
        elif "create" in step_name:
            return "🎨 Creating..."
        elif "explain" in step_name:
            return "💡 Explaining..."
        else:
            return "⚡ Working on your request..."
