"""
Conditional Execution Engine

Advanced workflow adaptation system that can dynamically modify
execution paths based on real-time conditions and results.
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

import structlog

logger = structlog.get_logger(__name__)


class ConditionType(Enum):
    """Types of conditions that can be evaluated."""
    QUALITY_THRESHOLD = "quality_threshold"
    CONTENT_LENGTH = "content_length"
    EXECUTION_TIME = "execution_time"
    ERROR_COUNT = "error_count"
    USER_SATISFACTION = "user_satisfaction"
    TOOL_AVAILABILITY = "tool_availability"
    CONTEXT_COMPLETENESS = "context_completeness"
    CUSTOM = "custom"


class ActionType(Enum):
    """Types of actions that can be taken when conditions are met."""
    SKIP_STEP = "skip_step"
    RETRY_STEP = "retry_step"
    ADD_STEP = "add_step"
    MODIFY_PARAMETERS = "modify_parameters"
    CHANGE_PROVIDER = "change_provider"
    TERMINATE_WORKFLOW = "terminate_workflow"
    BRANCH_WORKFLOW = "branch_workflow"
    MERGE_RESULTS = "merge_results"


@dataclass
class Condition:
    """Represents a condition that can trigger workflow changes."""
    condition_id: str
    condition_type: ConditionType
    operator: str  # "==", "!=", ">", "<", ">=", "<=", "contains", "in"
    threshold: Any
    description: str
    priority: int = 1  # Higher priority conditions are checked first
    enabled: bool = True


@dataclass
class ConditionalAction:
    """Action to take when a condition is met."""
    action_id: str
    action_type: ActionType
    target: str  # Step name, parameter name, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    max_executions: int = 3  # Prevent infinite loops
    execution_count: int = 0


@dataclass
class ConditionalRule:
    """Rule that combines conditions and actions."""
    rule_id: str
    name: str
    conditions: List[Condition]
    actions: List[ConditionalAction]
    logic_operator: str = "AND"  # "AND", "OR"
    enabled: bool = True
    execution_count: int = 0
    max_executions: int = 10


class ConditionalExecutionEngine:
    """
    Advanced conditional execution engine for dynamic workflow adaptation.
    
    Features:
    - Real-time condition evaluation
    - Dynamic workflow path modification
    - Quality-based branching
    - Error recovery automation
    - Performance optimization
    - Custom condition support
    """
    
    def __init__(self):
        self.rules: Dict[str, ConditionalRule] = {}
        self.condition_evaluators: Dict[ConditionType, Callable] = {}
        self.action_executors: Dict[ActionType, Callable] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
        # Initialize built-in evaluators and executors
        self._initialize_built_in_systems()
    
    def _initialize_built_in_systems(self):
        """Initialize built-in condition evaluators and action executors."""
        
        # Condition evaluators
        self.condition_evaluators = {
            ConditionType.QUALITY_THRESHOLD: self._evaluate_quality_threshold,
            ConditionType.CONTENT_LENGTH: self._evaluate_content_length,
            ConditionType.EXECUTION_TIME: self._evaluate_execution_time,
            ConditionType.ERROR_COUNT: self._evaluate_error_count,
            ConditionType.USER_SATISFACTION: self._evaluate_user_satisfaction,
            ConditionType.TOOL_AVAILABILITY: self._evaluate_tool_availability,
            ConditionType.CONTEXT_COMPLETENESS: self._evaluate_context_completeness,
            ConditionType.CUSTOM: self._evaluate_custom_condition
        }
        
        # Action executors
        self.action_executors = {
            ActionType.SKIP_STEP: self._execute_skip_step,
            ActionType.RETRY_STEP: self._execute_retry_step,
            ActionType.ADD_STEP: self._execute_add_step,
            ActionType.MODIFY_PARAMETERS: self._execute_modify_parameters,
            ActionType.CHANGE_PROVIDER: self._execute_change_provider,
            ActionType.TERMINATE_WORKFLOW: self._execute_terminate_workflow,
            ActionType.BRANCH_WORKFLOW: self._execute_branch_workflow,
            ActionType.MERGE_RESULTS: self._execute_merge_results
        }
    
    def add_rule(self, rule: ConditionalRule):
        """Add a conditional rule to the engine."""
        self.rules[rule.rule_id] = rule
        logger.info(f"Conditional rule added: {rule.name}", rule_id=rule.rule_id)
    
    def remove_rule(self, rule_id: str):
        """Remove a conditional rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Conditional rule removed", rule_id=rule_id)
    
    async def evaluate_conditions(
        self,
        context: Dict[str, Any],
        current_step: str,
        workflow_state: Dict[str, Any]
    ) -> List[ConditionalAction]:
        """
        Evaluate all conditions and return actions to execute.
        
        Args:
            context: Current workflow context
            current_step: Name of current step
            workflow_state: Current workflow state
            
        Returns:
            List of actions to execute
        """
        actions_to_execute = []
        
        # Sort rules by priority (if conditions have priorities)
        sorted_rules = sorted(
            [rule for rule in self.rules.values() if rule.enabled],
            key=lambda r: max((c.priority for c in r.conditions), default=1),
            reverse=True
        )
        
        for rule in sorted_rules:
            if rule.execution_count >= rule.max_executions:
                continue
                
            try:
                # Evaluate all conditions in the rule
                condition_results = []
                
                for condition in rule.conditions:
                    if not condition.enabled:
                        continue
                        
                    evaluator = self.condition_evaluators.get(condition.condition_type)
                    if evaluator:
                        result = await evaluator(condition, context, current_step, workflow_state)
                        condition_results.append(result)
                        
                        logger.debug(
                            f"Condition evaluated: {condition.description}",
                            condition_id=condition.condition_id,
                            result=result
                        )
                
                # Apply logic operator
                if rule.logic_operator == "AND":
                    rule_triggered = all(condition_results)
                elif rule.logic_operator == "OR":
                    rule_triggered = any(condition_results)
                else:
                    rule_triggered = any(condition_results)  # Default to OR
                
                # Execute actions if rule is triggered
                if rule_triggered:
                    logger.info(
                        f"Conditional rule triggered: {rule.name}",
                        rule_id=rule.rule_id,
                        current_step=current_step
                    )
                    
                    for action in rule.actions:
                        if action.execution_count < action.max_executions:
                            actions_to_execute.append(action)
                    
                    rule.execution_count += 1
                    
            except Exception as e:
                logger.error(
                    f"Error evaluating rule: {rule.name}",
                    rule_id=rule.rule_id,
                    error=str(e)
                )
        
        return actions_to_execute
    
    async def execute_actions(
        self,
        actions: List[ConditionalAction],
        context: Dict[str, Any],
        workflow_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute conditional actions and return modified workflow state.
        
        Args:
            actions: Actions to execute
            context: Current workflow context
            workflow_state: Current workflow state
            
        Returns:
            Modified workflow state
        """
        modified_state = workflow_state.copy()
        execution_results = []
        
        for action in actions:
            try:
                executor = self.action_executors.get(action.action_type)
                if executor:
                    result = await executor(action, context, modified_state)
                    
                    execution_results.append({
                        "action_id": action.action_id,
                        "action_type": action.action_type.value,
                        "result": result,
                        "success": True
                    })
                    
                    action.execution_count += 1
                    
                    logger.info(
                        f"Conditional action executed: {action.description}",
                        action_id=action.action_id,
                        action_type=action.action_type.value
                    )
                    
            except Exception as e:
                logger.error(
                    f"Error executing action: {action.description}",
                    action_id=action.action_id,
                    error=str(e)
                )
                
                execution_results.append({
                    "action_id": action.action_id,
                    "action_type": action.action_type.value,
                    "error": str(e),
                    "success": False
                })
        
        # Store execution history
        self.execution_history.append({
            "timestamp": time.time(),
            "actions_executed": len(actions),
            "results": execution_results
        })
        
        return modified_state
    
    # Condition Evaluators
    async def _evaluate_quality_threshold(
        self, condition: Condition, context: Dict[str, Any], 
        current_step: str, workflow_state: Dict[str, Any]
    ) -> bool:
        """Evaluate quality threshold condition."""
        quality_score = context.get("quality_score", 0.0)
        threshold = float(condition.threshold)
        
        return self._apply_operator(quality_score, condition.operator, threshold)
    
    async def _evaluate_content_length(
        self, condition: Condition, context: Dict[str, Any],
        current_step: str, workflow_state: Dict[str, Any]
    ) -> bool:
        """Evaluate content length condition."""
        content = context.get("generated_content", "")
        content_length = len(str(content))
        threshold = int(condition.threshold)
        
        return self._apply_operator(content_length, condition.operator, threshold)
    
    async def _evaluate_execution_time(
        self, condition: Condition, context: Dict[str, Any],
        current_step: str, workflow_state: Dict[str, Any]
    ) -> bool:
        """Evaluate execution time condition."""
        execution_time = context.get("execution_time", 0.0)
        threshold = float(condition.threshold)
        
        return self._apply_operator(execution_time, condition.operator, threshold)
    
    async def _evaluate_error_count(
        self, condition: Condition, context: Dict[str, Any],
        current_step: str, workflow_state: Dict[str, Any]
    ) -> bool:
        """Evaluate error count condition."""
        error_count = context.get("error_count", 0)
        threshold = int(condition.threshold)
        
        return self._apply_operator(error_count, condition.operator, threshold)
    
    async def _evaluate_user_satisfaction(
        self, condition: Condition, context: Dict[str, Any],
        current_step: str, workflow_state: Dict[str, Any]
    ) -> bool:
        """Evaluate user satisfaction condition."""
        satisfaction_score = context.get("user_satisfaction", 0.5)
        threshold = float(condition.threshold)
        
        return self._apply_operator(satisfaction_score, condition.operator, threshold)
    
    async def _evaluate_tool_availability(
        self, condition: Condition, context: Dict[str, Any],
        current_step: str, workflow_state: Dict[str, Any]
    ) -> bool:
        """Evaluate tool availability condition."""
        available_tools = context.get("available_tools", [])
        required_tool = condition.threshold
        
        if condition.operator == "contains":
            return required_tool in available_tools
        elif condition.operator == "not_contains":
            return required_tool not in available_tools
        else:
            return len(available_tools) > 0
    
    async def _evaluate_context_completeness(
        self, condition: Condition, context: Dict[str, Any],
        current_step: str, workflow_state: Dict[str, Any]
    ) -> bool:
        """Evaluate context completeness condition."""
        required_keys = condition.threshold if isinstance(condition.threshold, list) else [condition.threshold]
        
        if condition.operator == "contains_all":
            return all(key in context for key in required_keys)
        elif condition.operator == "contains_any":
            return any(key in context for key in required_keys)
        else:
            completeness_score = len([k for k in required_keys if k in context]) / len(required_keys)
            threshold = 0.8  # Default completeness threshold
            return completeness_score >= threshold
    
    async def _evaluate_custom_condition(
        self, condition: Condition, context: Dict[str, Any],
        current_step: str, workflow_state: Dict[str, Any]
    ) -> bool:
        """Evaluate custom condition using provided function."""
        # Custom conditions can be implemented by providing a function in parameters
        custom_func = condition.threshold
        if callable(custom_func):
            return await custom_func(context, current_step, workflow_state)
        return False
    
    # Action Executors
    async def _execute_skip_step(
        self, action: ConditionalAction, context: Dict[str, Any], 
        workflow_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute skip step action."""
        step_to_skip = action.target
        
        if "steps_to_skip" not in workflow_state:
            workflow_state["steps_to_skip"] = []
        
        workflow_state["steps_to_skip"].append(step_to_skip)
        
        return {"skipped_step": step_to_skip}
    
    async def _execute_retry_step(
        self, action: ConditionalAction, context: Dict[str, Any],
        workflow_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute retry step action."""
        step_to_retry = action.target
        retry_params = action.parameters
        
        if "steps_to_retry" not in workflow_state:
            workflow_state["steps_to_retry"] = []
        
        workflow_state["steps_to_retry"].append({
            "step_name": step_to_retry,
            "parameters": retry_params
        })
        
        return {"retried_step": step_to_retry, "parameters": retry_params}
    
    async def _execute_add_step(
        self, action: ConditionalAction, context: Dict[str, Any],
        workflow_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute add step action."""
        new_step = action.parameters
        
        if "additional_steps" not in workflow_state:
            workflow_state["additional_steps"] = []
        
        workflow_state["additional_steps"].append(new_step)
        
        return {"added_step": new_step}
    
    async def _execute_modify_parameters(
        self, action: ConditionalAction, context: Dict[str, Any],
        workflow_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute modify parameters action."""
        target_step = action.target
        new_parameters = action.parameters
        
        if "parameter_modifications" not in workflow_state:
            workflow_state["parameter_modifications"] = {}
        
        workflow_state["parameter_modifications"][target_step] = new_parameters
        
        return {"modified_parameters": {target_step: new_parameters}}
    
    async def _execute_change_provider(
        self, action: ConditionalAction, context: Dict[str, Any],
        workflow_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute change provider action."""
        new_provider = action.parameters.get("provider", "openai")
        
        workflow_state["preferred_provider"] = new_provider
        
        return {"changed_provider": new_provider}
    
    async def _execute_terminate_workflow(
        self, action: ConditionalAction, context: Dict[str, Any],
        workflow_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute terminate workflow action."""
        reason = action.parameters.get("reason", "Conditional termination")
        
        workflow_state["terminate_workflow"] = True
        workflow_state["termination_reason"] = reason
        
        return {"terminated": True, "reason": reason}
    
    async def _execute_branch_workflow(
        self, action: ConditionalAction, context: Dict[str, Any],
        workflow_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute branch workflow action."""
        branch_config = action.parameters
        
        if "workflow_branches" not in workflow_state:
            workflow_state["workflow_branches"] = []
        
        workflow_state["workflow_branches"].append(branch_config)
        
        return {"branched_workflow": branch_config}
    
    async def _execute_merge_results(
        self, action: ConditionalAction, context: Dict[str, Any],
        workflow_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute merge results action."""
        merge_strategy = action.parameters.get("strategy", "concatenate")
        
        workflow_state["merge_strategy"] = merge_strategy
        workflow_state["should_merge_results"] = True
        
        return {"merge_strategy": merge_strategy}
    
    def _apply_operator(self, value: Any, operator: str, threshold: Any) -> bool:
        """Apply comparison operator between value and threshold."""
        try:
            if operator == "==":
                return value == threshold
            elif operator == "!=":
                return value != threshold
            elif operator == ">":
                return value > threshold
            elif operator == "<":
                return value < threshold
            elif operator == ">=":
                return value >= threshold
            elif operator == "<=":
                return value <= threshold
            elif operator == "contains":
                return threshold in str(value)
            elif operator == "not_contains":
                return threshold not in str(value)
            elif operator == "in":
                return value in threshold
            elif operator == "not_in":
                return value not in threshold
            else:
                return False
        except Exception:
            return False
    
    def create_quality_rule(
        self, 
        quality_threshold: float = 0.7,
        action_type: ActionType = ActionType.RETRY_STEP
    ) -> ConditionalRule:
        """Create a pre-configured quality-based rule."""
        
        condition = Condition(
            condition_id="quality_check",
            condition_type=ConditionType.QUALITY_THRESHOLD,
            operator="<",
            threshold=quality_threshold,
            description=f"Quality score below {quality_threshold}",
            priority=2
        )
        
        action = ConditionalAction(
            action_id="quality_action",
            action_type=action_type,
            target="current_step",
            description="Improve quality through retry or refinement"
        )
        
        return ConditionalRule(
            rule_id="quality_improvement_rule",
            name="Quality Improvement Rule",
            conditions=[condition],
            actions=[action]
        )
    
    def create_performance_rule(
        self,
        max_execution_time: float = 30.0
    ) -> ConditionalRule:
        """Create a pre-configured performance-based rule."""
        
        condition = Condition(
            condition_id="performance_check",
            condition_type=ConditionType.EXECUTION_TIME,
            operator=">",
            threshold=max_execution_time,
            description=f"Execution time exceeds {max_execution_time}s",
            priority=3
        )
        
        action = ConditionalAction(
            action_id="performance_action",
            action_type=ActionType.CHANGE_PROVIDER,
            target="current_step",
            parameters={"provider": "openai"},  # Switch to faster provider
            description="Switch to faster AI provider"
        )
        
        return ConditionalRule(
            rule_id="performance_optimization_rule",
            name="Performance Optimization Rule",
            conditions=[condition],
            actions=[action]
        )
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "total_rules": len(self.rules),
            "active_rules": len([r for r in self.rules.values() if r.enabled]),
            "total_executions": len(self.execution_history),
            "recent_executions": self.execution_history[-10:] if self.execution_history else []
        }
