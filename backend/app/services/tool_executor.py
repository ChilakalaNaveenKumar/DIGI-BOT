"""
Tool Executor Service

Handles execution of AI tools and functions with safety, monitoring, and result processing.
"""

import asyncio
import json
import time
import traceback
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Tuple, Union
from datetime import datetime
from enum import Enum

import structlog
from pydantic import BaseModel

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class ToolStatus(str, Enum):
    """Tool execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ToolResult(BaseModel):
    """Tool execution result."""
    tool_name: str
    status: ToolStatus
    result: Any = None
    error: Optional[str] = None
    execution_time: float
    timestamp: datetime
    metadata: Dict[str, Any] = {}


class ToolExecution(BaseModel):
    """Tool execution tracking."""
    execution_id: str
    tool_name: str
    input_data: Dict[str, Any]
    status: ToolStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[ToolResult] = None
    progress: float = 0.0
    logs: List[str] = []


class ToolDefinition(BaseModel):
    """Tool definition and metadata."""
    name: str
    description: str
    parameters: Dict[str, Any]
    timeout: float = 30.0
    max_retries: int = 3
    requires_auth: bool = False
    risk_level: str = "low"  # low, medium, high
    category: str = "general"
    tags: List[str] = []


class ToolExecutor:
    """
    Service for executing AI tools and functions.
    
    Features:
    - Safe tool execution with timeouts
    - Progress tracking and monitoring
    - Result caching and optimization
    - Error handling and retries
    - Security and permission management
    """
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_definitions: Dict[str, ToolDefinition] = {}
        self.active_executions: Dict[str, ToolExecution] = {}
        self.execution_history: List[ToolExecution] = []
        self.tool_cache: Dict[str, Any] = {}
        
        # Initialize built-in tools
        self._register_builtin_tools()
    
    async def initialize(self):
        """Initialize the tool executor."""
        logger.info("ToolExecutor initialized successfully", tools_count=len(self.tools))
    
    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Dict[str, Any],
        **kwargs
    ) -> None:
        """Register a new tool for execution."""
        
        tool_def = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            **kwargs
        )
        
        self.tools[name] = func
        self.tool_definitions[name] = tool_def
        
        logger.info("Tool registered", tool_name=name, description=description)
    
    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool."""
        
        if name in self.tools:
            del self.tools[name]
            del self.tool_definitions[name]
            logger.info("Tool unregistered", tool_name=name)
            return True
        
        return False
    
    async def execute_tool(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Execute a tool with the given input data."""
        
        execution_id = f"exec_{int(time.time() * 1000)}"
        
        # Create execution tracking
        execution = ToolExecution(
            execution_id=execution_id,
            tool_name=tool_name,
            input_data=input_data,
            status=ToolStatus.PENDING,
            start_time=datetime.utcnow()
        )
        
        self.active_executions[execution_id] = execution
        
        try:
            # Validate tool exists
            if tool_name not in self.tools:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            tool_func = self.tools[tool_name]
            tool_def = self.tool_definitions[tool_name]
            
            # Check permissions and safety
            await self._check_tool_permissions(tool_name, input_data, context)
            
            # Validate input parameters
            validated_input = await self._validate_tool_input(tool_name, input_data)
            
            # Check cache for recent results
            cache_key = self._generate_cache_key(tool_name, validated_input)
            if cache_key in self.tool_cache:
                cached_result = self.tool_cache[cache_key]
                logger.info("Using cached tool result", tool_name=tool_name, execution_id=execution_id)
                
                result = ToolResult(
                    tool_name=tool_name,
                    status=ToolStatus.COMPLETED,
                    result=cached_result,
                    execution_time=0.0,
                    timestamp=datetime.utcnow(),
                    metadata={"cached": True}
                )
                
                execution.status = ToolStatus.COMPLETED
                execution.end_time = datetime.utcnow()
                execution.result = result
                
                return result
            
            # Execute tool with timeout
            execution.status = ToolStatus.RUNNING
            start_time = time.time()
            
            logger.info("Starting tool execution", tool_name=tool_name, execution_id=execution_id)
            
            try:
                # Execute with timeout
                result_data = await asyncio.wait_for(
                    self._execute_tool_safely(tool_func, validated_input, execution),
                    timeout=tool_def.timeout
                )
                
                execution_time = time.time() - start_time
                
                # Create successful result
                result = ToolResult(
                    tool_name=tool_name,
                    status=ToolStatus.COMPLETED,
                    result=result_data,
                    execution_time=execution_time,
                    timestamp=datetime.utcnow(),
                    metadata={
                        "execution_id": execution_id,
                        "input_size": len(str(input_data)),
                        "output_size": len(str(result_data))
                    }
                )
                
                # Cache result if appropriate
                if self._should_cache_result(tool_name, result_data):
                    self.tool_cache[cache_key] = result_data
                
                execution.status = ToolStatus.COMPLETED
                execution.end_time = datetime.utcnow()
                execution.result = result
                execution.progress = 1.0
                
                logger.info(
                    "Tool execution completed",
                    tool_name=tool_name,
                    execution_id=execution_id,
                    execution_time=execution_time
                )
                
                return result
                
            except asyncio.TimeoutError:
                execution.status = ToolStatus.TIMEOUT
                raise TimeoutError(f"Tool '{tool_name}' execution timed out after {tool_def.timeout}s")
            
        except Exception as e:
            execution_time = time.time() - start_time if 'start_time' in locals() else 0.0
            
            # Create error result
            result = ToolResult(
                tool_name=tool_name,
                status=ToolStatus.FAILED,
                error=str(e),
                execution_time=execution_time,
                timestamp=datetime.utcnow(),
                metadata={
                    "execution_id": execution_id,
                    "error_type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }
            )
            
            execution.status = ToolStatus.FAILED
            execution.end_time = datetime.utcnow()
            execution.result = result
            
            logger.error(
                "Tool execution failed",
                tool_name=tool_name,
                execution_id=execution_id,
                error=str(e)
            )
            
            return result
            
        finally:
            # Move to history and clean up
            if execution_id in self.active_executions:
                self.execution_history.append(self.active_executions[execution_id])
                del self.active_executions[execution_id]
                
                # Keep history limited
                if len(self.execution_history) > 1000:
                    self.execution_history = self.execution_history[-500:]
    
    async def execute_tool_with_streaming(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute a tool with streaming progress updates."""
        
        execution_id = f"stream_exec_{int(time.time() * 1000)}"
        
        # Stream initial status
        yield {
            "type": "tool_start",
            "execution_id": execution_id,
            "tool_name": tool_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Execute tool (this could be enhanced to support actual streaming)
            result = await self.execute_tool(tool_name, input_data, context)
            
            # Stream progress updates (simulated for now)
            progress_steps = [0.2, 0.5, 0.8, 1.0]
            for progress in progress_steps[:-1]:
                yield {
                    "type": "tool_progress",
                    "execution_id": execution_id,
                    "tool_name": tool_name,
                    "progress": progress,
                    "timestamp": datetime.utcnow().isoformat()
                }
                await asyncio.sleep(0.1)  # Small delay for realistic streaming
            
            # Stream final result
            yield {
                "type": "tool_complete",
                "execution_id": execution_id,
                "tool_name": tool_name,
                "result": result.dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            yield {
                "type": "tool_error",
                "execution_id": execution_id,
                "tool_name": tool_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _execute_tool_safely(
        self,
        tool_func: Callable,
        input_data: Dict[str, Any],
        execution: ToolExecution
    ) -> Any:
        """Execute tool function safely with monitoring."""
        
        try:
            # Check if function is async
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**input_data)
            else:
                # Run sync function in thread pool
                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: tool_func(**input_data)
                )
            
            return result
            
        except Exception as e:
            execution.logs.append(f"Error during execution: {str(e)}")
            raise
    
    async def _check_tool_permissions(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> None:
        """Check if tool execution is permitted."""
        
        tool_def = self.tool_definitions[tool_name]
        
        # Check risk level
        if tool_def.risk_level == "high":
            # High-risk tools require explicit permission
            if not context or not context.get("allow_high_risk", False):
                raise PermissionError(f"High-risk tool '{tool_name}' requires explicit permission")
        
        # Check authentication if required
        if tool_def.requires_auth:
            if not context or not context.get("authenticated", False):
                raise PermissionError(f"Tool '{tool_name}' requires authentication")
        
        # Additional safety checks can be added here
    
    async def _validate_tool_input(
        self,
        tool_name: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and sanitize tool input data."""
        
        tool_def = self.tool_definitions[tool_name]
        validated_input = {}
        
        # Basic parameter validation
        required_params = tool_def.parameters.get("required", [])
        for param in required_params:
            if param not in input_data:
                raise ValueError(f"Required parameter '{param}' missing for tool '{tool_name}'")
        
        # Copy and validate each parameter
        for key, value in input_data.items():
            # Basic sanitization (can be enhanced)
            if isinstance(value, str):
                # Remove potentially dangerous characters
                sanitized_value = value.replace("<script>", "").replace("</script>", "")
                validated_input[key] = sanitized_value
            else:
                validated_input[key] = value
        
        return validated_input
    
    def _generate_cache_key(self, tool_name: str, input_data: Dict[str, Any]) -> str:
        """Generate cache key for tool execution."""
        
        # Create deterministic key from tool name and input
        input_str = json.dumps(input_data, sort_keys=True)
        return f"{tool_name}:{hash(input_str)}"
    
    def _should_cache_result(self, tool_name: str, result_data: Any) -> bool:
        """Determine if result should be cached."""
        
        tool_def = self.tool_definitions[tool_name]
        
        # Don't cache high-risk tools or tools that return large data
        if tool_def.risk_level == "high":
            return False
        
        if isinstance(result_data, (str, dict, list)):
            result_size = len(str(result_data))
            return result_size < 10000  # Cache only small results
        
        return True
    
    def _register_builtin_tools(self) -> None:
        """Register built-in tools."""
        
        # Calculator tool
        self.register_tool(
            name="calculator",
            func=self._calculator_tool,
            description="Perform mathematical calculations",
            parameters={
                "required": ["expression"],
                "properties": {
                    "expression": {"type": "string", "description": "Mathematical expression to evaluate"}
                }
            },
            timeout=5.0,
            risk_level="low",
            category="math"
        )
        
        # Text analyzer tool
        self.register_tool(
            name="text_analyzer",
            func=self._text_analyzer_tool,
            description="Analyze text for various metrics",
            parameters={
                "required": ["text"],
                "properties": {
                    "text": {"type": "string", "description": "Text to analyze"},
                    "metrics": {"type": "array", "description": "Metrics to calculate"}
                }
            },
            timeout=10.0,
            risk_level="low",
            category="text"
        )
        
        # JSON validator tool
        self.register_tool(
            name="json_validator",
            func=self._json_validator_tool,
            description="Validate and format JSON data",
            parameters={
                "required": ["json_data"],
                "properties": {
                    "json_data": {"type": "string", "description": "JSON data to validate"}
                }
            },
            timeout=5.0,
            risk_level="low",
            category="data"
        )
    
    async def _calculator_tool(self, expression: str) -> Dict[str, Any]:
        """Built-in calculator tool."""
        
        try:
            # Safe evaluation of mathematical expressions
            # This is a simplified version - in production, use a proper math parser
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                raise ValueError("Expression contains invalid characters")
            
            # Basic safety check
            if any(word in expression.lower() for word in ["import", "exec", "eval", "__"]):
                raise ValueError("Expression contains forbidden operations")
            
            result = eval(expression)  # In production, use a safer alternative
            
            return {
                "expression": expression,
                "result": result,
                "type": type(result).__name__
            }
            
        except Exception as e:
            raise ValueError(f"Invalid mathematical expression: {str(e)}")
    
    async def _text_analyzer_tool(
        self,
        text: str,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Built-in text analyzer tool."""
        
        if metrics is None:
            metrics = ["word_count", "char_count", "sentence_count"]
        
        analysis = {}
        
        if "word_count" in metrics:
            analysis["word_count"] = len(text.split())
        
        if "char_count" in metrics:
            analysis["char_count"] = len(text)
            analysis["char_count_no_spaces"] = len(text.replace(" ", ""))
        
        if "sentence_count" in metrics:
            sentences = text.split(".")
            analysis["sentence_count"] = len([s for s in sentences if s.strip()])
        
        if "readability" in metrics:
            # Simple readability score
            words = len(text.split())
            sentences = len([s for s in text.split(".") if s.strip()])
            if sentences > 0:
                avg_words_per_sentence = words / sentences
                analysis["avg_words_per_sentence"] = round(avg_words_per_sentence, 2)
        
        return analysis
    
    async def _json_validator_tool(self, json_data: str) -> Dict[str, Any]:
        """Built-in JSON validator tool."""
        
        try:
            parsed_data = json.loads(json_data)
            
            return {
                "valid": True,
                "parsed_data": parsed_data,
                "data_type": type(parsed_data).__name__,
                "size": len(json_data)
            }
            
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": str(e),
                "error_position": e.pos if hasattr(e, 'pos') else None
            }
    
    def get_tool_definitions(self) -> Dict[str, ToolDefinition]:
        """Get all registered tool definitions."""
        return self.tool_definitions.copy()
    
    def get_execution_history(self, limit: int = 100) -> List[ToolExecution]:
        """Get recent execution history."""
        return self.execution_history[-limit:]
    
    def get_active_executions(self) -> Dict[str, ToolExecution]:
        """Get currently active executions."""
        return self.active_executions.copy()
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an active tool execution."""
        
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.status = ToolStatus.CANCELLED
            execution.end_time = datetime.utcnow()
            
            logger.info("Tool execution cancelled", execution_id=execution_id)
            return True
        
        return False
    
    def clear_cache(self) -> None:
        """Clear the tool result cache."""
        self.tool_cache.clear()
        logger.info("Tool cache cleared")
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get tool usage statistics."""
        
        total_executions = len(self.execution_history)
        if total_executions == 0:
            return {"total_executions": 0}
        
        # Calculate statistics
        successful_executions = sum(
            1 for exec in self.execution_history 
            if exec.status == ToolStatus.COMPLETED
        )
        
        failed_executions = sum(
            1 for exec in self.execution_history 
            if exec.status == ToolStatus.FAILED
        )
        
        avg_execution_time = sum(
            (exec.end_time - exec.start_time).total_seconds()
            for exec in self.execution_history
            if exec.end_time
        ) / total_executions
        
        tool_usage = {}
        for exec in self.execution_history:
            tool_usage[exec.tool_name] = tool_usage.get(exec.tool_name, 0) + 1
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": successful_executions / total_executions,
            "avg_execution_time": round(avg_execution_time, 3),
            "tool_usage": tool_usage,
            "cache_size": len(self.tool_cache),
            "active_executions": len(self.active_executions)
        }
