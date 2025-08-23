"""
Tool Service - Function Calling and Tool Execution

Handles execution of various tools and functions with AI integration.
"""

import time
import json
import asyncio
from typing import Any, Dict, List, Optional, Callable

import structlog
import httpx
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)
settings = get_settings()


class ToolService:
    """Service for handling tool execution and function calling."""
    
    def __init__(self):
        """Initialize tool service with available tools."""
        self.openai_client = None
        
        # Initialize OpenAI client if API key is available
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Register available tools
        self.available_tools = {
            "get_weather": {
                "function": self.get_weather,
                "description": "Get current weather information for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name or coordinates"
                        },
                        "units": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "Temperature units"
                        }
                    },
                    "required": ["location"]
                }
            },
            "calculate": {
                "function": self.calculate,
                "description": "Perform mathematical calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            },
            "search_database": {
                "function": self.search_database,
                "description": "Search internal database for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "table": {
                            "type": "string",
                            "description": "Database table to search"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results"
                        }
                    },
                    "required": ["query"]
                }
            },
            "generate_code": {
                "function": self.generate_code,
                "description": "Generate code in specified programming language",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "language": {
                            "type": "string",
                            "description": "Programming language"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of what the code should do"
                        },
                        "complexity": {
                            "type": "string",
                            "enum": ["simple", "intermediate", "advanced"],
                            "description": "Code complexity level"
                        }
                    },
                    "required": ["language", "description"]
                }
            },
            "analyze_data": {
                "function": self.analyze_data,
                "description": "Analyze provided data and generate insights",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "string",
                            "description": "Data to analyze (JSON, CSV, or text)"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["statistical", "trend", "summary", "correlation"],
                            "description": "Type of analysis to perform"
                        }
                    },
                    "required": ["data"]
                }
            }
        }
    
    async def execute(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a specific tool/function.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
            context: Optional execution context
        
        Returns:
            Dictionary with execution result and metadata
        
        Raises:
            ValueError: If tool is not available
            DigiSetuException: If execution fails
        """
        try:
            if tool_name not in self.available_tools:
                available = ", ".join(self.available_tools.keys())
                raise ValueError(f"Tool '{tool_name}' not available. Available tools: {available}")
            
            start_time = time.time()
            
            logger.info(
                "Executing tool",
                tool_name=tool_name,
                parameters=list(parameters.keys()) if parameters else []
            )
            
            # Get tool function
            tool_function = self.available_tools[tool_name]["function"]
            
            # Execute tool with parameters
            if context:
                result = await tool_function(context=context, **parameters)
            else:
                result = await tool_function(**parameters)
            
            execution_time = time.time() - start_time
            
            logger.info(
                "Tool execution completed",
                tool_name=tool_name,
                execution_time=execution_time
            )
            
            return {
                "result": result,
                "execution_time": execution_time,
                "tool_name": tool_name,
                "parameters": parameters
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error("Tool execution failed", tool_name=tool_name, error=str(e), exc_info=True)
            raise DigiSetuException(
                "TOOL_EXECUTION_FAILED",
                f"Tool execution failed: {str(e)}",
                500,
                {"tool_name": tool_name, "parameters": parameters}
            )
    
    async def batch_execute(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute multiple tools in batch.
        
        Args:
            tools: List of tool execution requests
        
        Returns:
            List of execution results
        """
        try:
            logger.info("Executing batch tools", tool_count=len(tools))
            
            # Execute tools concurrently
            tasks = []
            for tool_request in tools:
                task = self.execute(
                    tool_request.tool_name,
                    tool_request.parameters,
                    tool_request.context
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "success": False,
                        "error": str(result),
                        "tool_name": tools[i].tool_name
                    })
                else:
                    processed_results.append({
                        "success": True,
                        **result
                    })
            
            return processed_results
            
        except Exception as e:
            logger.error("Batch tool execution failed", error=str(e))
            raise DigiSetuException(
                "BATCH_EXECUTION_FAILED",
                f"Batch execution failed: {str(e)}",
                500
            )
    
    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools/functions.
        
        Returns:
            List of available tools with descriptions
        """
        tools = []
        for name, tool_info in self.available_tools.items():
            tools.append({
                "name": name,
                "description": tool_info["description"],
                "parameters": tool_info["parameters"]
            })
        return tools
    
    async def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific tool.
        
        Args:
            tool_name: Name of the tool
        
        Returns:
            Tool information or None if not found
        """
        if tool_name not in self.available_tools:
            return None
        
        tool_info = self.available_tools[tool_name]
        return {
            "name": tool_name,
            "description": tool_info["description"],
            "parameters": tool_info["parameters"]
        }
    
    # Tool implementations
    
    async def get_weather(self, location: str, units: str = "celsius", **kwargs) -> Dict[str, Any]:
        """Get weather information for a location."""
        try:
            # Mock weather API call (replace with real API)
            # For demo purposes, return mock data
            import random
            
            temp_celsius = random.randint(-10, 35)
            temp_fahrenheit = (temp_celsius * 9/5) + 32
            
            conditions = ["sunny", "cloudy", "rainy", "partly cloudy", "overcast"]
            condition = random.choice(conditions)
            
            result = {
                "location": location,
                "temperature": temp_celsius if units == "celsius" else temp_fahrenheit,
                "units": "°C" if units == "celsius" else "°F",
                "condition": condition,
                "humidity": random.randint(30, 90),
                "wind_speed": random.randint(0, 25),
                "timestamp": time.time()
            }
            
            logger.info("Weather data retrieved", location=location, condition=condition)
            return result
            
        except Exception as e:
            logger.error("Weather retrieval failed", error=str(e))
            return {"error": f"Weather retrieval failed: {str(e)}"}
    
    async def calculate(self, expression: str, **kwargs) -> Dict[str, Any]:
        """Perform mathematical calculations."""
        try:
            # Safe evaluation of mathematical expressions
            import ast
            import operator
            
            # Allowed operations
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.USub: operator.neg,
            }
            
            def eval_expr(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
                elif isinstance(node, ast.UnaryOp):
                    return ops[type(node.op)](eval_expr(node.operand))
                else:
                    raise TypeError(f"Unsupported operation: {type(node)}")
            
            # Parse and evaluate
            tree = ast.parse(expression, mode='eval')
            result = eval_expr(tree.body)
            
            logger.info("Calculation completed", expression=expression, result=result)
            
            return {
                "expression": expression,
                "result": result,
                "type": type(result).__name__
            }
            
        except Exception as e:
            logger.error("Calculation failed", expression=expression, error=str(e))
            return {"error": f"Calculation failed: {str(e)}"}
    
    async def search_database(self, query: str, table: str = "general", limit: int = 10, **kwargs) -> Dict[str, Any]:
        """Search internal database for information."""
        try:
            # Mock database search (replace with real database queries)
            mock_results = [
                {"id": 1, "title": f"Result for '{query}' - Item 1", "content": f"Mock content related to {query}"},
                {"id": 2, "title": f"Result for '{query}' - Item 2", "content": f"Another mock result for {query}"},
                {"id": 3, "title": f"Result for '{query}' - Item 3", "content": f"Third result matching {query}"}
            ]
            
            # Limit results
            results = mock_results[:limit]
            
            logger.info("Database search completed", query=query, results_count=len(results))
            
            return {
                "query": query,
                "table": table,
                "results": results,
                "total_found": len(results),
                "limit": limit
            }
            
        except Exception as e:
            logger.error("Database search failed", error=str(e))
            return {"error": f"Database search failed: {str(e)}"}
    
    async def generate_code(self, language: str, description: str, complexity: str = "simple", **kwargs) -> Dict[str, Any]:
        """Generate code in specified programming language."""
        try:
            if not self.openai_client:
                return {"error": "Code generation requires OpenAI API key"}
            
            prompt = f"""Generate {complexity} {language} code that {description}.
            
            Requirements:
            - Write clean, well-commented code
            - Include error handling where appropriate
            - Follow best practices for {language}
            - Provide a brief explanation of the code
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are an expert {language} programmer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            code_result = response.choices[0].message.content
            
            logger.info("Code generation completed", language=language, complexity=complexity)
            
            return {
                "language": language,
                "description": description,
                "complexity": complexity,
                "code": code_result
            }
            
        except Exception as e:
            logger.error("Code generation failed", error=str(e))
            return {"error": f"Code generation failed: {str(e)}"}
    
    async def analyze_data(self, data: str, analysis_type: str = "summary", **kwargs) -> Dict[str, Any]:
        """Analyze provided data and generate insights."""
        try:
            if not self.openai_client:
                return {"error": "Data analysis requires OpenAI API key"}
            
            prompt = f"""Analyze the following data and provide {analysis_type} insights:

            Data:
            {data[:2000]}  # Limit data length
            
            Please provide:
            1. Key findings
            2. Patterns or trends
            3. Statistical summary (if applicable)
            4. Recommendations or insights
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a data analyst expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            analysis_result = response.choices[0].message.content
            
            logger.info("Data analysis completed", analysis_type=analysis_type)
            
            return {
                "analysis_type": analysis_type,
                "data_preview": data[:200] + "..." if len(data) > 200 else data,
                "analysis": analysis_result
            }
            
        except Exception as e:
            logger.error("Data analysis failed", error=str(e))
            return {"error": f"Data analysis failed: {str(e)}"}

