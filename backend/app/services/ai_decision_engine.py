"""
AI Decision Engine

Uses AI to make intelligent decisions about workflow execution,
including next steps, tool selection, and quality assessment.
"""

import json
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

import structlog
from pydantic import BaseModel

from app.services.workflow_context import WorkflowContext

logger = structlog.get_logger(__name__)


class NextStepPlan(BaseModel):
    """Plan for the next workflow step."""
    step_name: str
    step_type: str
    reasoning: str
    confidence: float
    estimated_time: float
    requires_tools: bool
    tool_names: List[str] = []
    parameters: Dict[str, Any] = {}
    alternatives: List[str] = []


class QualityAssessment(BaseModel):
    """Quality assessment of generated content."""
    overall_score: float  # 0.0 to 1.0
    needs_improvement: bool
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    iteration_count: int = 0


class AIDecisionEngine:
    """
    AI-powered decision engine for adaptive workflow execution.
    
    Features:
    - Context-aware next step planning
    - Quality assessment and refinement loops
    - Tool selection and coordination
    - Dynamic workflow adaptation
    """
    
    def __init__(self, ai_provider=None):
        self.ai_provider = ai_provider
        self.decision_cache: Dict[str, Any] = {}
        self.max_iterations = 3  # Prevent infinite loops
        
    async def plan_next_steps(
        self, 
        context: WorkflowContext,
        remaining_goals: List[str] = None
    ) -> List[NextStepPlan]:
        """
        Analyze current context and plan the next workflow steps.
        
        Args:
            context: Current workflow context with accumulated results
            remaining_goals: Any remaining goals to accomplish
            
        Returns:
            List of planned next steps with reasoning
        """
        start_time = time.time()
        
        try:
            # Get context for decision making
            context_data = context.get_context_for_next_step()
            
            # Create AI prompt for step planning
            planning_prompt = self._create_step_planning_prompt(
                context_data, remaining_goals
            )
            
            # Get AI decision
            ai_response = await self._get_ai_decision(
                planning_prompt,
                max_tokens=800,
                temperature=0.3  # Lower temperature for more consistent planning
            )
            
            # Parse the response
            plans = self._parse_step_plans(ai_response)
            
            # Record the decision
            decision_reasoning = f"Planned {len(plans)} next steps based on current context"
            context.add_ai_decision(
                decision_point="next_step_planning",
                decision_made=f"Execute {len(plans)} steps: {[p.step_name for p in plans]}",
                reasoning=decision_reasoning,
                confidence=sum(p.confidence for p in plans) / len(plans) if plans else 0.0,
                alternatives=[p.alternatives for p in plans]
            )
            
            execution_time = time.time() - start_time
            logger.info(
                "Next steps planned",
                workflow_id=context.workflow_id,
                steps_planned=len(plans),
                execution_time=execution_time
            )
            
            return plans
            
        except Exception as e:
            logger.error(
                "Failed to plan next steps",
                workflow_id=context.workflow_id,
                error=str(e)
            )
            
            # Fallback to basic next step
            return [NextStepPlan(
                step_name="continue_generation",
                step_type="generation",
                reasoning="Fallback step due to planning error",
                confidence=0.5,
                estimated_time=5.0,
                requires_tools=False
            )]
    
    async def assess_quality(
        self, 
        content: Any, 
        original_query: str,
        context: WorkflowContext
    ) -> QualityAssessment:
        """
        Assess the quality of generated content and suggest improvements.
        
        Args:
            content: The content to assess
            original_query: The original user query
            context: Current workflow context
            
        Returns:
            Quality assessment with improvement suggestions
        """
        try:
            # Create quality assessment prompt
            assessment_prompt = self._create_quality_assessment_prompt(
                content, original_query, context.get_context_for_next_step()
            )
            
            # Get AI assessment
            ai_response = await self._get_ai_decision(
                assessment_prompt,
                max_tokens=600,
                temperature=0.2  # Low temperature for consistent assessment
            )
            
            # Parse the assessment
            assessment = self._parse_quality_assessment(ai_response)
            
            # Record the decision
            context.add_ai_decision(
                decision_point="quality_assessment",
                decision_made=f"Quality score: {assessment.overall_score:.2f}, Needs improvement: {assessment.needs_improvement}",
                reasoning=f"Assessed based on {len(assessment.strengths)} strengths and {len(assessment.weaknesses)} weaknesses",
                confidence=assessment.overall_score
            )
            
            logger.info(
                "Quality assessed",
                workflow_id=context.workflow_id,
                quality_score=assessment.overall_score,
                needs_improvement=assessment.needs_improvement
            )
            
            return assessment
            
        except Exception as e:
            logger.error(
                "Failed to assess quality",
                workflow_id=context.workflow_id,
                error=str(e)
            )
            
            # Fallback assessment
            return QualityAssessment(
                overall_score=0.7,
                needs_improvement=False,
                strengths=["Content generated"],
                weaknesses=[],
                suggestions=[]
            )
    
    async def refine_content_with_assessment(
        self,
        content: Any,
        assessment: QualityAssessment,
        original_query: str,
        context: WorkflowContext,
        max_iterations: int = 2
    ) -> Tuple[Any, List[QualityAssessment]]:
        """
        Refine content based on quality assessment with iterative improvement.
        
        Args:
            content: The content to refine
            assessment: Initial quality assessment
            original_query: Original user query
            context: Workflow context
            max_iterations: Maximum refinement iterations
            
        Returns:
            Tuple of (refined_content, list_of_assessments)
        """
        refinement_history = [assessment]
        current_content = content
        
        for iteration in range(max_iterations):
            if not assessment.needs_improvement:
                break
                
            logger.info(
                f"Starting refinement iteration {iteration + 1}",
                workflow_id=context.workflow_id,
                current_score=assessment.overall_score
            )
            
            # Generate refinement prompt
            refinement_prompt = self._create_refinement_prompt(
                current_content, assessment, original_query, iteration + 1
            )
            
            # Get refined content
            refined_response = await self._get_ai_decision(
                refinement_prompt,
                max_tokens=4000,
                temperature=0.3
            )
            
            current_content = refined_response
            
            # Re-assess the refined content
            new_assessment = await self.assess_quality(
                current_content, original_query, context
            )
            new_assessment.iteration_count = iteration + 1
            
            refinement_history.append(new_assessment)
            
            # Record refinement decision
            context.add_ai_decision(
                decision_point=f"content_refinement_iteration_{iteration + 1}",
                decision_made=f"Refined content, new score: {new_assessment.overall_score:.2f}",
                reasoning=f"Applied {len(assessment.suggestions)} suggestions from previous assessment",
                confidence=new_assessment.overall_score
            )
            
            # Check if improvement was made
            if new_assessment.overall_score <= assessment.overall_score + 0.05:
                # No significant improvement, stop refining
                logger.info(
                    "No significant improvement in refinement, stopping",
                    workflow_id=context.workflow_id,
                    old_score=assessment.overall_score,
                    new_score=new_assessment.overall_score
                )
                break
            
            assessment = new_assessment
        
        return current_content, refinement_history
    
    async def assess_and_refine_if_needed(
        self,
        content: Any,
        original_query: str,
        context: WorkflowContext,
        quality_threshold: float = 0.75
    ) -> Tuple[Any, QualityAssessment]:
        """
        Assess content quality and automatically refine if below threshold.
        
        Args:
            content: Content to assess and potentially refine
            original_query: Original user query
            context: Workflow context
            quality_threshold: Minimum quality score (0.0-1.0)
            
        Returns:
            Tuple of (final_content, final_assessment)
        """
        # Initial assessment
        initial_assessment = await self.assess_quality(content, original_query, context)
        
        if initial_assessment.overall_score >= quality_threshold:
            # Quality is already good enough
            return content, initial_assessment
        
        # Quality is below threshold, refine it
        logger.info(
            "Content quality below threshold, starting refinement",
            workflow_id=context.workflow_id,
            current_score=initial_assessment.overall_score,
            threshold=quality_threshold
        )
        
        refined_content, refinement_history = await self.refine_content_with_assessment(
            content, initial_assessment, original_query, context
        )
        
        final_assessment = refinement_history[-1]
        
        # Log refinement results
        improvement = final_assessment.overall_score - initial_assessment.overall_score
        logger.info(
            "Content refinement completed",
            workflow_id=context.workflow_id,
            initial_score=initial_assessment.overall_score,
            final_score=final_assessment.overall_score,
            improvement=improvement,
            iterations=len(refinement_history) - 1
        )
        
        return refined_content, final_assessment
    
    async def select_tools(
        self, 
        task_description: str,
        available_tools: List[str],
        context: WorkflowContext
    ) -> List[str]:
        """
        Select the most appropriate tools for a given task.
        
        Args:
            task_description: Description of the task
            available_tools: List of available tool names
            context: Current workflow context
            
        Returns:
            List of selected tool names
        """
        try:
            # Create tool selection prompt
            selection_prompt = self._create_tool_selection_prompt(
                task_description, available_tools, context.get_context_for_next_step()
            )
            
            # Get AI selection
            ai_response = await self._get_ai_decision(
                selection_prompt,
                max_tokens=400,
                temperature=0.2
            )
            
            # Parse selected tools
            selected_tools = self._parse_tool_selection(ai_response, available_tools)
            
            # Record the decision
            context.add_ai_decision(
                decision_point="tool_selection",
                decision_made=f"Selected tools: {selected_tools}",
                reasoning=f"Selected {len(selected_tools)} tools for task: {task_description[:100]}",
                confidence=0.8,
                alternatives=available_tools
            )
            
            logger.info(
                "Tools selected",
                workflow_id=context.workflow_id,
                task=task_description[:50],
                selected_tools=selected_tools
            )
            
            return selected_tools
            
        except Exception as e:
            logger.error(
                "Failed to select tools",
                workflow_id=context.workflow_id,
                error=str(e)
            )
            return []
    
    def _create_step_planning_prompt(
        self, 
        context_data: Dict[str, Any], 
        remaining_goals: List[str] = None
    ) -> str:
        """Create prompt for AI step planning."""
        
        prompt = f"""
You are an AI workflow planner. Analyze the current context and plan the next steps.

CURRENT CONTEXT:
- Original Query: "{context_data.get('original_query', '')}"
- Steps Completed: {context_data.get('steps_completed', 0)}
- Previous Results: {json.dumps(context_data.get('previous_results', []), indent=2)}
- Key Insights: {json.dumps(context_data.get('key_insights', {}), indent=2)}
- Decisions Made: {json.dumps(context_data.get('decisions_made', {}), indent=2)}

REMAINING GOALS: {remaining_goals or ['Complete the user request']}

AVAILABLE STEP TYPES:
- analysis: Analyze requirements or data
- generation: Generate content, code, or responses
- tool_execution: Execute external tools
- quality_check: Assess and refine content
- coordination: Coordinate multiple AI providers

Plan the next 1-3 steps to progress toward completing the user's request.
For each step, consider:
1. What needs to be accomplished?
2. What step type is most appropriate?
3. What tools might be needed?
4. How confident are you in this approach?
5. What are alternative approaches?

Respond with JSON array:
[
  {{
    "step_name": "descriptive_step_name",
    "step_type": "analysis|generation|tool_execution|quality_check|coordination",
    "reasoning": "Why this step is needed and how it helps",
    "confidence": 0.0-1.0,
    "estimated_time": 5.0,
    "requires_tools": true/false,
    "tool_names": ["tool1", "tool2"],
    "parameters": {{"key": "value"}},
    "alternatives": ["alternative1", "alternative2"]
  }}
]
"""
        
        return prompt
    
    def _create_quality_assessment_prompt(
        self, 
        content: Any, 
        original_query: str,
        context_data: Dict[str, Any]
    ) -> str:
        """Create prompt for quality assessment."""
        
        content_preview = str(content)[:1000] + "..." if len(str(content)) > 1000 else str(content)
        
        prompt = f"""
You are an AI quality assessor. Evaluate how well the content addresses the user's request.

ORIGINAL REQUEST: "{original_query}"

CONTENT TO ASSESS:
{content_preview}

CONTEXT:
- Steps completed: {context_data.get('steps_completed', 0)}
- Key insights: {json.dumps(context_data.get('key_insights', {}), indent=2)}

ASSESSMENT CRITERIA:
1. Relevance: Does it address the user's request?
2. Completeness: Is all requested information included?
3. Accuracy: Is the information correct and well-structured?
4. Clarity: Is it easy to understand and well-formatted?
5. Usefulness: Would this be helpful to the user?

Respond with JSON:
{{
  "overall_score": 0.0-1.0,
  "needs_improvement": true/false,
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "suggestions": ["improvement1", "improvement2"],
  "iteration_count": 0
}}
"""
        
        return prompt
    
    def _create_tool_selection_prompt(
        self, 
        task: str, 
        available_tools: List[str],
        context_data: Dict[str, Any]
    ) -> str:
        """Create prompt for tool selection."""
        
        prompt = f"""
You are an AI tool selector. Choose the best tools for the given task.

TASK: {task}

AVAILABLE TOOLS: {available_tools}

CONTEXT:
- Original query: "{context_data.get('original_query', '')}"
- Previous results: {context_data.get('previous_results', [])}
- Tools already used: {context_data.get('providers_used', [])}

Select the most appropriate tools for this task. Consider:
1. Which tools are most relevant to the task?
2. Which tools haven't been overused?
3. Which tools work well together?
4. What's the minimum set of tools needed?

Respond with JSON array of tool names:
["tool1", "tool2"]
"""
        
        return prompt
    
    def _create_refinement_prompt(
        self,
        content: Any,
        assessment: QualityAssessment,
        original_query: str,
        iteration: int
    ) -> str:
        """Create prompt for content refinement based on quality assessment."""
        
        content_preview = str(content)[:1500] + "..." if len(str(content)) > 1500 else str(content)
        
        prompt = f"""
You are an AI content refiner. Improve the content based on the quality assessment.

ORIGINAL REQUEST: "{original_query}"

CURRENT CONTENT:
{content_preview}

QUALITY ASSESSMENT (Iteration {iteration}):
- Overall Score: {assessment.overall_score:.2f}/1.0
- Needs Improvement: {assessment.needs_improvement}

STRENGTHS IDENTIFIED:
{chr(10).join(f"- {strength}" for strength in assessment.strengths)}

WEAKNESSES TO ADDRESS:
{chr(10).join(f"- {weakness}" for weakness in assessment.weaknesses)}

SPECIFIC IMPROVEMENT SUGGESTIONS:
{chr(10).join(f"- {suggestion}" for suggestion in assessment.suggestions)}

REFINEMENT INSTRUCTIONS:
1. Keep all the strengths that were identified
2. Address each weakness systematically
3. Implement the specific suggestions provided
4. Ensure the content better fulfills the original request
5. Maintain or improve clarity, accuracy, and usefulness
6. Do not change the fundamental format unless suggested

Provide the refined content that addresses these issues while maintaining what works well:
"""
        
        return prompt
    
    async def _get_ai_decision(
        self, 
        prompt: str, 
        max_tokens: int = 500,
        temperature: float = 0.3
    ) -> str:
        """Get AI decision using the configured provider."""
        if not self.ai_provider:
            raise ValueError("No AI provider configured")
        
        messages = [{"role": "user", "content": prompt}]
        
        response = await self.ai_provider.generate_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    def _parse_step_plans(self, ai_response: str) -> List[NextStepPlan]:
        """Parse AI response into step plans."""
        try:
            # Try to extract JSON from the response
            json_start = ai_response.find('[')
            json_end = ai_response.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = ai_response[json_start:json_end]
            else:
                # Fallback: try to find JSON object
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_content = '[' + ai_response[json_start:json_end] + ']'
                else:
                    raise json.JSONDecodeError("No JSON found", ai_response, 0)
            
            plans_data = json.loads(json_content)
            plans = []
            
            # Handle both single object and array
            if not isinstance(plans_data, list):
                plans_data = [plans_data]
            
            for plan_data in plans_data:
                plan = NextStepPlan(
                    step_name=plan_data.get("step_name", "unknown_step"),
                    step_type=plan_data.get("step_type", "generation"),
                    reasoning=plan_data.get("reasoning", ""),
                    confidence=float(plan_data.get("confidence", 0.5)),
                    estimated_time=float(plan_data.get("estimated_time", 5.0)),
                    requires_tools=plan_data.get("requires_tools", False),
                    tool_names=plan_data.get("tool_names", []),
                    parameters=plan_data.get("parameters", {}),
                    alternatives=plan_data.get("alternatives", [])
                )
                plans.append(plan)
            
            return plans
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Failed to parse step plans JSON: {str(e)}, AI response: {ai_response[:200]}...")
            return [NextStepPlan(
                step_name="continue_processing",
                step_type="generation",
                reasoning="Default step due to parsing error",
                confidence=0.5,
                estimated_time=5.0,
                requires_tools=False
            )]
    
    def _parse_quality_assessment(self, ai_response: str) -> QualityAssessment:
        """Parse AI response into quality assessment."""
        try:
            assessment_data = json.loads(ai_response)
            
            return QualityAssessment(
                overall_score=float(assessment_data.get("overall_score", 0.7)),
                needs_improvement=assessment_data.get("needs_improvement", False),
                strengths=assessment_data.get("strengths", []),
                weaknesses=assessment_data.get("weaknesses", []),
                suggestions=assessment_data.get("suggestions", []),
                iteration_count=assessment_data.get("iteration_count", 0)
            )
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse quality assessment JSON")
            return QualityAssessment(
                overall_score=0.7,
                needs_improvement=False,
                strengths=["Content generated"],
                weaknesses=[],
                suggestions=[]
            )
    
    def _parse_tool_selection(self, ai_response: str, available_tools: List[str]) -> List[str]:
        """Parse AI response into tool selection."""
        try:
            selected_tools = json.loads(ai_response)
            
            # Validate that selected tools are available
            valid_tools = [
                tool for tool in selected_tools 
                if tool in available_tools
            ]
            
            return valid_tools
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse tool selection JSON")
            return []
