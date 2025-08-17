"""
Coordinated Tool Executor

Enhanced tool execution system that enables tools to share data,
coordinate execution, and build upon each other's results.
"""

import asyncio
import json
import time
import uuid
from typing import Any, Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ToolResult:
    """Result from a tool execution."""
    tool_name: str
    execution_id: str
    result: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)  # Tool results this depends on


@dataclass
class ToolExecutionPlan:
    """Plan for coordinated tool execution."""
    execution_id: str
    tools: List[Dict[str, Any]]
    execution_order: List[str]
    data_dependencies: Dict[str, List[str]]  # tool_name -> list of dependency tool names
    parallel_groups: List[List[str]]  # Groups of tools that can run in parallel
    estimated_time: float
    context: Dict[str, Any] = field(default_factory=dict)


class CoordinatedToolExecutor:
    """
    Advanced tool executor with coordination capabilities.
    
    Features:
    - Tool data sharing and dependencies
    - Parallel execution where possible
    - Sequential execution where needed
    - Context accumulation across tools
    - Smart tool selection based on available data
    - Error recovery and fallback strategies
    """
    
    def __init__(self):
        self.available_tools = {}
        self.execution_history: Dict[str, List[ToolResult]] = {}
        self.shared_context: Dict[str, Any] = {}
        self.active_executions: Dict[str, ToolExecutionPlan] = {}
        
    async def initialize(self):
        """Initialize the coordinated tool executor."""
        # Register available tools
        await self._register_tools()
        logger.info("Coordinated Tool Executor initialized")
    
    async def execute_coordinated_workflow(
        self,
        tool_requests: List[Dict[str, Any]],
        workflow_context: Dict[str, Any] = None,
        user_query: str = ""
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a coordinated workflow of tools with data sharing.
        
        Args:
            tool_requests: List of tool execution requests
            workflow_context: Context from the workflow engine
            user_query: Original user query for context
            
        Yields:
            Tool execution results and progress updates
        """
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            yield {
                "type": "tool_coordination_start",
                "execution_id": execution_id,
                "tools_requested": len(tool_requests)
            }
            
            # Step 1: Analyze dependencies and create execution plan
            yield {"type": "activity", "content": "🔍 Analyzing tool dependencies..."}
            
            execution_plan = await self._create_execution_plan(
                tool_requests, workflow_context, user_query
            )
            
            self.active_executions[execution_id] = execution_plan
            
            yield {
                "type": "execution_plan",
                "plan": {
                    "execution_order": execution_plan.execution_order,
                    "parallel_groups": execution_plan.parallel_groups,
                    "estimated_time": execution_plan.estimated_time
                }
            }
            
            # Step 2: Execute tools according to plan
            shared_data = {}
            execution_results = {}
            
            for group in execution_plan.parallel_groups:
                if len(group) == 1:
                    # Sequential execution
                    tool_name = group[0]
                    yield {"type": "activity", "content": f"🔧 Executing {tool_name}..."}
                    
                    result = await self._execute_single_tool(
                        tool_name,
                        execution_plan.tools,
                        shared_data,
                        workflow_context
                    )
                    
                    execution_results[tool_name] = result
                    shared_data[tool_name] = result.result
                    
                    yield {
                        "type": "tool_result",
                        "tool_name": tool_name,
                        "result": result.result,
                        "execution_time": result.execution_time,
                        "success": result.success
                    }
                    
                else:
                    # Parallel execution
                    yield {
                        "type": "activity", 
                        "content": f"⚡ Executing {len(group)} tools in parallel: {', '.join(group)}"
                    }
                    
                    parallel_results = await self._execute_parallel_tools(
                        group,
                        execution_plan.tools,
                        shared_data,
                        workflow_context
                    )
                    
                    for tool_name, result in parallel_results.items():
                        execution_results[tool_name] = result
                        shared_data[tool_name] = result.result
                        
                        yield {
                            "type": "tool_result",
                            "tool_name": tool_name,
                            "result": result.result,
                            "execution_time": result.execution_time,
                            "success": result.success
                        }
            
            # Step 3: Synthesize results
            yield {"type": "activity", "content": "🔄 Synthesizing tool results..."}
            
            synthesis = await self._synthesize_results(
                execution_results, user_query, workflow_context
            )
            
            total_time = time.time() - start_time
            
            # Store execution history
            self.execution_history[execution_id] = list(execution_results.values())
            
            yield {
                "type": "coordination_complete",
                "execution_id": execution_id,
                "total_tools": len(execution_results),
                "successful_tools": len([r for r in execution_results.values() if r.success]),
                "total_time": total_time,
                "synthesis": synthesis,
                "shared_data": shared_data
            }
            
        except Exception as e:
            logger.error("Tool coordination failed", execution_id=execution_id, error=str(e))
            yield {
                "type": "coordination_error",
                "execution_id": execution_id,
                "error": str(e)
            }
        
        finally:
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    async def _create_execution_plan(
        self,
        tool_requests: List[Dict[str, Any]],
        workflow_context: Dict[str, Any],
        user_query: str
    ) -> ToolExecutionPlan:
        """Create an optimized execution plan for the requested tools."""
        
        execution_id = str(uuid.uuid4())
        
        # Analyze dependencies
        dependencies = {}
        tools_by_name = {}
        
        for tool_request in tool_requests:
            tool_name = tool_request.get("tool_name", "unknown")
            tools_by_name[tool_name] = tool_request
            
            # Determine dependencies based on tool type and data requirements
            tool_deps = await self._analyze_tool_dependencies(
                tool_request, tools_by_name, workflow_context
            )
            dependencies[tool_name] = tool_deps
        
        # Create execution order using topological sort
        execution_order = self._topological_sort(dependencies)
        
        # Group tools for parallel execution
        parallel_groups = self._create_parallel_groups(execution_order, dependencies)
        
        # Estimate execution time
        estimated_time = self._estimate_execution_time(tool_requests, parallel_groups)
        
        return ToolExecutionPlan(
            execution_id=execution_id,
            tools=tools_by_name,
            execution_order=execution_order,
            data_dependencies=dependencies,
            parallel_groups=parallel_groups,
            estimated_time=estimated_time,
            context=workflow_context or {}
        )
    
    async def _analyze_tool_dependencies(
        self,
        tool_request: Dict[str, Any],
        available_tools: Dict[str, Any],
        workflow_context: Dict[str, Any]
    ) -> List[str]:
        """Analyze what other tools this tool depends on."""
        
        tool_name = tool_request.get("tool_name", "")
        dependencies = []
        
        # Define known tool dependencies
        dependency_rules = {
            "web_search": [],  # No dependencies - can run first
            "data_analysis": ["web_search"],  # Needs search results
            "image_generation": ["data_analysis"],  # Needs analyzed data
            "code_generation": ["web_search", "data_analysis"],  # Needs context
            "document_analysis": [],  # No dependencies
            "calculation": ["data_analysis"],  # Needs data to calculate
            "translation": [],  # No dependencies
            "summarization": ["web_search", "document_analysis"]  # Needs content
        }
        
        # Get base dependencies
        base_deps = dependency_rules.get(tool_name, [])
        
        # Filter to only include tools that are actually requested
        for dep in base_deps:
            if dep in available_tools:
                dependencies.append(dep)
        
        # Smart dependency detection based on tool parameters
        tool_params = tool_request.get("parameters", {})
        
        # If tool needs "search_results", it depends on search tools
        if "search_results" in str(tool_params) or "web_data" in str(tool_params):
            search_tools = [name for name in available_tools.keys() 
                          if "search" in name.lower()]
            dependencies.extend(search_tools)
        
        # If tool needs "analyzed_data", it depends on analysis tools
        if "analyzed_data" in str(tool_params) or "analysis" in str(tool_params):
            analysis_tools = [name for name in available_tools.keys() 
                            if "analysis" in name.lower()]
            dependencies.extend(analysis_tools)
        
        return list(set(dependencies))  # Remove duplicates
    
    def _topological_sort(self, dependencies: Dict[str, List[str]]) -> List[str]:
        """Create execution order using topological sort."""
        
        # Kahn's algorithm for topological sorting
        in_degree = {node: 0 for node in dependencies}
        
        # Calculate in-degrees
        for node in dependencies:
            for dep in dependencies[node]:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Find nodes with no dependencies
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            # Remove this node and update in-degrees
            for dependent in dependencies:
                if node in dependencies[dependent]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        return result
    
    def _create_parallel_groups(
        self, 
        execution_order: List[str], 
        dependencies: Dict[str, List[str]]
    ) -> List[List[str]]:
        """Group tools that can be executed in parallel."""
        
        parallel_groups = []
        remaining_tools = set(execution_order)
        completed_tools = set()
        
        while remaining_tools:
            # Find tools that can run now (all dependencies completed)
            ready_tools = []
            
            for tool in remaining_tools:
                tool_deps = dependencies.get(tool, [])
                if all(dep in completed_tools or dep not in dependencies 
                      for dep in tool_deps):
                    ready_tools.append(tool)
            
            if not ready_tools:
                # Fallback: take the first remaining tool to avoid infinite loop
                ready_tools = [next(iter(remaining_tools))]
            
            parallel_groups.append(ready_tools)
            
            # Mark these tools as completed
            for tool in ready_tools:
                remaining_tools.remove(tool)
                completed_tools.add(tool)
        
        return parallel_groups
    
    def _estimate_execution_time(
        self, 
        tool_requests: List[Dict[str, Any]], 
        parallel_groups: List[List[str]]
    ) -> float:
        """Estimate total execution time considering parallelization."""
        
        # Base execution times for different tool types (in seconds)
        tool_times = {
            "web_search": 3.0,
            "data_analysis": 5.0,
            "image_generation": 8.0,
            "code_generation": 4.0,
            "document_analysis": 6.0,
            "calculation": 2.0,
            "translation": 3.0,
            "summarization": 4.0
        }
        
        total_time = 0.0
        
        for group in parallel_groups:
            # For parallel groups, time is the maximum time of any tool in the group
            group_time = max(
                tool_times.get(tool_name, 3.0) for tool_name in group
            )
            total_time += group_time
        
        # Add coordination overhead
        coordination_overhead = len(tool_requests) * 0.5
        
        return total_time + coordination_overhead
    
    async def _execute_single_tool(
        self,
        tool_name: str,
        tools_config: Dict[str, Any],
        shared_data: Dict[str, Any],
        workflow_context: Dict[str, Any]
    ) -> ToolResult:
        """Execute a single tool with access to shared data."""
        
        start_time = time.time()
        execution_id = str(uuid.uuid4())
        
        try:
            tool_config = tools_config.get(tool_name, {})
            
            # Enhance tool parameters with shared data
            enhanced_params = self._enhance_tool_parameters(
                tool_config.get("parameters", {}),
                shared_data,
                workflow_context
            )
            
            # Execute the tool (mock implementation - replace with actual tool execution)
            result = await self._mock_tool_execution(tool_name, enhanced_params)
            
            execution_time = time.time() - start_time
            
            return ToolResult(
                tool_name=tool_name,
                execution_id=execution_id,
                result=result,
                metadata={
                    "enhanced_params": enhanced_params,
                    "shared_data_used": list(shared_data.keys())
                },
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Tool {tool_name} execution failed", error=str(e))
            
            return ToolResult(
                tool_name=tool_name,
                execution_id=execution_id,
                result=None,
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    async def _execute_parallel_tools(
        self,
        tool_names: List[str],
        tools_config: Dict[str, Any],
        shared_data: Dict[str, Any],
        workflow_context: Dict[str, Any]
    ) -> Dict[str, ToolResult]:
        """Execute multiple tools in parallel."""
        
        tasks = []
        for tool_name in tool_names:
            task = asyncio.create_task(
                self._execute_single_tool(
                    tool_name, tools_config, shared_data, workflow_context
                )
            )
            tasks.append((tool_name, task))
        
        results = {}
        for tool_name, task in tasks:
            try:
                result = await task
                results[tool_name] = result
            except Exception as e:
                logger.error(f"Parallel execution failed for {tool_name}", error=str(e))
                results[tool_name] = ToolResult(
                    tool_name=tool_name,
                    execution_id=str(uuid.uuid4()),
                    result=None,
                    success=False,
                    error_message=str(e)
                )
        
        return results
    
    def _enhance_tool_parameters(
        self,
        base_params: Dict[str, Any],
        shared_data: Dict[str, Any],
        workflow_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance tool parameters with data from previous tool executions."""
        
        enhanced_params = base_params.copy()
        
        # Add shared data to parameters
        enhanced_params["shared_data"] = shared_data
        enhanced_params["workflow_context"] = workflow_context
        
        # Smart parameter enhancement based on available data
        if "web_search" in shared_data and "query" not in enhanced_params:
            # Use search results to enhance query
            search_results = shared_data["web_search"]
            if isinstance(search_results, dict) and "summary" in search_results:
                enhanced_params["context"] = search_results["summary"]
        
        if "data_analysis" in shared_data:
            # Use analysis results to enhance parameters
            analysis = shared_data["data_analysis"]
            if isinstance(analysis, dict):
                enhanced_params["analysis_context"] = analysis
        
        return enhanced_params
    
    async def _mock_tool_execution(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock tool execution - replace with actual tool implementations."""
        
        # Simulate execution time
        await asyncio.sleep(0.5)
        
        # Mock results based on tool type
        mock_results = {
            "web_search": {
                "query": parameters.get("query", "search query"),
                "results": [
                    {"title": "Result 1", "url": "https://example.com/1", "snippet": "Sample content 1"},
                    {"title": "Result 2", "url": "https://example.com/2", "snippet": "Sample content 2"}
                ],
                "summary": "Search found relevant information about the query"
            },
            "data_analysis": {
                "analysis_type": "statistical",
                "insights": ["Key insight 1", "Key insight 2"],
                "metrics": {"accuracy": 0.95, "confidence": 0.87},
                "recommendations": ["Recommendation 1", "Recommendation 2"]
            },
            "code_generation": {
                "language": parameters.get("language", "python"),
                "code": "def example_function():\n    return 'Generated code'",
                "explanation": "This code demonstrates the requested functionality"
            }
        }
        
        return mock_results.get(tool_name, {"result": f"Mock result for {tool_name}"})
    
    async def _synthesize_results(
        self,
        execution_results: Dict[str, ToolResult],
        user_query: str,
        workflow_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize results from multiple tools into a coherent response."""
        
        successful_results = {
            name: result for name, result in execution_results.items() 
            if result.success
        }
        
        synthesis = {
            "total_tools": len(execution_results),
            "successful_tools": len(successful_results),
            "failed_tools": len(execution_results) - len(successful_results),
            "key_findings": [],
            "recommendations": [],
            "data_connections": []
        }
        
        # Extract key findings from each tool
        for tool_name, result in successful_results.items():
            if isinstance(result.result, dict):
                # Extract insights, summaries, recommendations
                if "insights" in result.result:
                    synthesis["key_findings"].extend(result.result["insights"])
                if "summary" in result.result:
                    synthesis["key_findings"].append(f"{tool_name}: {result.result['summary']}")
                if "recommendations" in result.result:
                    synthesis["recommendations"].extend(result.result["recommendations"])
        
        # Identify data connections between tools
        for tool_name, result in successful_results.items():
            dependencies = result.dependencies
            if dependencies:
                synthesis["data_connections"].append({
                    "tool": tool_name,
                    "used_data_from": dependencies
                })
        
        return synthesis
    
    async def _register_tools(self):
        """Register available tools."""
        # This would register actual tool implementations
        # For now, just mark as initialized
        self.available_tools = {
            "web_search": {"description": "Search the web for information"},
            "data_analysis": {"description": "Analyze data and extract insights"},
            "code_generation": {"description": "Generate code based on requirements"},
            "image_generation": {"description": "Generate images from descriptions"},
            "document_analysis": {"description": "Analyze documents and extract information"},
            "calculation": {"description": "Perform mathematical calculations"},
            "translation": {"description": "Translate text between languages"},
            "summarization": {"description": "Summarize long text content"}
        }
    
    async def cleanup(self):
        """Cleanup coordinated tool executor."""
        self.active_executions.clear()
        self.shared_context.clear()
        logger.info("Coordinated Tool Executor cleaned up")
