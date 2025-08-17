"""
Workflow Context Memory System

Maintains context and state across workflow execution steps,
enabling AI to make informed decisions at each step.
"""

import time
import uuid
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class WorkflowStep:
    """Individual workflow step result."""
    step_id: str
    step_name: str
    step_type: str  # 'analysis', 'generation', 'tool_execution', etc.
    result: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class AIDecision:
    """AI decision made during workflow execution."""
    decision_id: str
    decision_point: str
    decision_made: str
    reasoning: str
    confidence: float
    alternatives_considered: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class WorkflowContext:
    """
    Context memory system that accumulates knowledge across workflow steps.
    
    Features:
    - Step result storage and retrieval
    - Key insights extraction and accumulation
    - Decision history tracking
    - Context-aware next step planning
    """
    
    def __init__(self, workflow_id: str = None):
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.original_query = ""
        self.user_preferences = {}
        
        # Step tracking
        self.steps: List[WorkflowStep] = []
        self.step_results: Dict[str, Any] = {}
        self.current_step_index = 0
        
        # AI decisions
        self.decisions: List[AIDecision] = []
        self.decision_history: Dict[str, str] = {}
        
        # Accumulated insights
        self.key_insights: Dict[str, Any] = {}
        self.extracted_data: Dict[str, Any] = {}
        self.context_summary = ""
        
        # Workflow metadata
        self.start_time = time.time()
        self.total_tokens_used = 0
        self.providers_used: List[str] = []
        
        logger.info("Workflow context initialized", workflow_id=self.workflow_id)
    
    def set_initial_context(
        self, 
        query: str, 
        user_preferences: Dict[str, Any] = None
    ):
        """Set the initial context for the workflow."""
        self.original_query = query
        self.user_preferences = user_preferences or {}
        
        # Extract initial insights from the query
        self._extract_query_insights(query)
        
        logger.info(
            "Initial context set",
            workflow_id=self.workflow_id,
            query_length=len(query),
            preferences_count=len(self.user_preferences)
        )
    
    def add_step_result(
        self, 
        step_name: str, 
        step_type: str,
        result: Any, 
        execution_time: float = 0.0,
        metadata: Dict[str, Any] = None,
        success: bool = True,
        error_message: str = None
    ) -> str:
        """Add a workflow step result and extract key data."""
        step_id = f"step_{len(self.steps) + 1}_{step_name}"
        
        step = WorkflowStep(
            step_id=step_id,
            step_name=step_name,
            step_type=step_type,
            result=result,
            metadata=metadata or {},
            execution_time=execution_time,
            success=success,
            error_message=error_message
        )
        
        self.steps.append(step)
        self.step_results[step_name] = result
        
        # Extract and accumulate key data from the result
        if success and result:
            self._extract_key_data_from_result(step_name, step_type, result)
        
        logger.info(
            "Step result added",
            workflow_id=self.workflow_id,
            step_id=step_id,
            step_type=step_type,
            success=success
        )
        
        return step_id
    
    def add_ai_decision(
        self,
        decision_point: str,
        decision_made: str,
        reasoning: str,
        confidence: float,
        alternatives: List[str] = None
    ) -> str:
        """Record an AI decision made during workflow execution."""
        decision_id = f"decision_{len(self.decisions) + 1}"
        
        decision = AIDecision(
            decision_id=decision_id,
            decision_point=decision_point,
            decision_made=decision_made,
            reasoning=reasoning,
            confidence=confidence,
            alternatives_considered=alternatives or []
        )
        
        self.decisions.append(decision)
        self.decision_history[decision_point] = decision_made
        
        logger.info(
            "AI decision recorded",
            workflow_id=self.workflow_id,
            decision_point=decision_point,
            decision=decision_made,
            confidence=confidence
        )
        
        return decision_id
    
    def get_context_for_next_step(self, next_step_type: str = None) -> Dict[str, Any]:
        """Get relevant context for planning the next step."""
        context = {
            "workflow_id": self.workflow_id,
            "original_query": self.original_query,
            "current_step_index": self.current_step_index,
            
            # Previous results summary
            "previous_results": self._summarize_previous_results(),
            "key_insights": self.key_insights,
            "extracted_data": self.extracted_data,
            
            # Decision history
            "decisions_made": self.decision_history,
            "recent_decisions": [asdict(d) for d in self.decisions[-3:]] if self.decisions else [],
            
            # Performance context
            "execution_time_so_far": time.time() - self.start_time,
            "steps_completed": len(self.steps),
            "providers_used": self.providers_used,
            
            # User preferences
            "user_preferences": self.user_preferences
        }
        
        # Add step-type specific context
        if next_step_type:
            context["step_specific_context"] = self._get_step_specific_context(next_step_type)
        
        return context
    
    def get_final_result(self) -> Dict[str, Any]:
        """Get the final accumulated result of the workflow."""
        return {
            "workflow_id": self.workflow_id,
            "original_query": self.original_query,
            "total_steps": len(self.steps),
            "successful_steps": len([s for s in self.steps if s.success]),
            "total_execution_time": time.time() - self.start_time,
            
            # Results
            "step_results": self.step_results,
            "key_insights": self.key_insights,
            "extracted_data": self.extracted_data,
            "context_summary": self._generate_context_summary(),
            
            # Decisions
            "decisions_made": len(self.decisions),
            "decision_history": self.decision_history,
            
            # Performance
            "tokens_used": self.total_tokens_used,
            "providers_used": self.providers_used
        }
    
    def _extract_query_insights(self, query: str):
        """Extract initial insights from the user query."""
        insights = {}
        
        # Query characteristics
        insights["query_length"] = len(query)
        insights["query_complexity"] = "complex" if len(query) > 100 else "simple"
        insights["has_questions"] = "?" in query
        insights["has_requests"] = any(word in query.lower() for word in ["create", "build", "make", "generate", "write"])
        insights["mentions_code"] = any(word in query.lower() for word in ["code", "function", "class", "script"])
        insights["mentions_data"] = any(word in query.lower() for word in ["data", "table", "json", "csv", "database"])
        insights["mentions_visual"] = any(word in query.lower() for word in ["chart", "graph", "diagram", "visualization"])
        
        self.key_insights.update(insights)
    
    def _extract_key_data_from_result(self, step_name: str, step_type: str, result: Any):
        """Extract key data from step results for future reference."""
        extracted = {}
        
        if step_type == "analysis":
            # Extract analysis insights
            if isinstance(result, dict):
                extracted.update({
                    f"{step_name}_analysis": result,
                    "analysis_complete": True
                })
        
        elif step_type == "generation":
            # Extract generated content metadata
            if isinstance(result, str):
                extracted.update({
                    f"{step_name}_content_length": len(result),
                    f"{step_name}_has_code": "```" in result,
                    f"{step_name}_has_tables": "|" in result and "---" in result,
                    f"{step_name}_has_json": result.strip().startswith(("{", "[")),
                    "content_generated": True
                })
        
        elif step_type == "tool_execution":
            # Extract tool results
            extracted.update({
                f"{step_name}_tool_result": result,
                "tools_executed": True
            })
        
        # Update extracted data
        self.extracted_data.update(extracted)
    
    def _summarize_previous_results(self) -> List[Dict[str, Any]]:
        """Create a summary of previous step results."""
        summaries = []
        
        for step in self.steps[-5:]:  # Last 5 steps
            summary = {
                "step_name": step.step_name,
                "step_type": step.step_type,
                "success": step.success,
                "execution_time": step.execution_time,
                "has_result": step.result is not None
            }
            
            # Add type-specific summary
            if step.step_type == "generation" and isinstance(step.result, str):
                summary["content_length"] = len(step.result)
                summary["content_preview"] = step.result[:100] + "..." if len(step.result) > 100 else step.result
            
            summaries.append(summary)
        
        return summaries
    
    def _get_step_specific_context(self, step_type: str) -> Dict[str, Any]:
        """Get context specific to the next step type."""
        context = {}
        
        if step_type == "analysis":
            context["previous_analyses"] = [
                step.result for step in self.steps 
                if step.step_type == "analysis" and step.success
            ]
        
        elif step_type == "generation":
            context["content_requirements"] = self.key_insights
            context["user_preferences"] = self.user_preferences
            context["previous_content"] = [
                step.result for step in self.steps 
                if step.step_type == "generation" and step.success
            ]
        
        elif step_type == "tool_execution":
            context["available_data"] = self.extracted_data
            context["tool_history"] = [
                step for step in self.steps 
                if step.step_type == "tool_execution"
            ]
        
        return context
    
    def _generate_context_summary(self) -> str:
        """Generate a human-readable summary of the workflow context."""
        summary_parts = [
            f"Workflow {self.workflow_id} processed query: '{self.original_query[:100]}...'"
        ]
        
        if self.steps:
            summary_parts.append(f"Completed {len(self.steps)} steps in {time.time() - self.start_time:.2f} seconds")
            
            successful_steps = [s for s in self.steps if s.success]
            if successful_steps:
                step_types = list(set(s.step_type for s in successful_steps))
                summary_parts.append(f"Step types executed: {', '.join(step_types)}")
        
        if self.decisions:
            summary_parts.append(f"Made {len(self.decisions)} AI decisions during execution")
        
        if self.key_insights:
            insight_count = len([k for k, v in self.key_insights.items() if v])
            summary_parts.append(f"Extracted {insight_count} key insights")
        
        return ". ".join(summary_parts)
    
    def update_token_usage(self, tokens: int, provider: str):
        """Update token usage tracking."""
        self.total_tokens_used += tokens
        if provider not in self.providers_used:
            self.providers_used.append(provider)
    
    def mark_step_complete(self, step_name: str):
        """Mark the current step as complete and advance."""
        self.current_step_index += 1
        logger.info(
            "Step marked complete",
            workflow_id=self.workflow_id,
            step_name=step_name,
            current_index=self.current_step_index
        )
