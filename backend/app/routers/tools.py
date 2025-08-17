"""
Tools API Router - Function Calling Endpoints

Handles tool execution and function calling capabilities.
"""

import logging
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.tool_service import ToolService
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/tools", tags=["tools"])


class ToolExecutionRequest(BaseModel):
    """Request model for tool execution."""
    tool_name: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class ToolExecutionResponse(BaseModel):
    """Response model for tool execution."""
    success: bool
    result: Any
    tool_name: str
    execution_time: float
    metadata: Dict[str, Any]


@router.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest):
    """
    Execute a specific tool/function.
    
    Args:
        request: Tool execution request with tool name and parameters
    
    Returns:
        JSON response with tool execution result
    """
    try:
        logger.info(
            "Processing tool execution request",
            tool_name=request.tool_name,
            parameters=list(request.parameters.keys()) if request.parameters else []
        )
        
        tool_service = ToolService()
        result = await tool_service.execute(
            request.tool_name, 
            request.parameters, 
            request.context
        )
        
        logger.info(
            "Tool execution completed successfully",
            tool_name=request.tool_name,
            execution_time=result.get("execution_time", 0)
        )
        
        return ToolExecutionResponse(
            success=True,
            result=result["result"],
            tool_name=request.tool_name,
            execution_time=result.get("execution_time", 0),
            metadata={
                "type": "tool_result",
                "tool_name": request.tool_name,
                "parameters": request.parameters,
                "context": request.context
            }
        )
        
    except DigiSetuException:
        raise
    except ValueError as e:
        logger.warning("Tool execution failed - invalid tool", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Tool execution failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool execution failed: {str(e)}"
        )


@router.get("/available")
async def list_available_tools():
    """
    List all available tools/functions.
    
    Returns:
        JSON response with available tools and their descriptions
    """
    try:
        tool_service = ToolService()
        tools = await tool_service.list_available_tools()
        
        return {
            "success": True,
            "tools": tools,
            "count": len(tools)
        }
        
    except Exception as e:
        logger.error("Failed to list available tools", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}"
        )


@router.get("/tool/{tool_name}")
async def get_tool_info(tool_name: str):
    """
    Get detailed information about a specific tool.
    
    Args:
        tool_name: Name of the tool to get info for
    
    Returns:
        JSON response with tool information
    """
    try:
        tool_service = ToolService()
        tool_info = await tool_service.get_tool_info(tool_name)
        
        if not tool_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_name}' not found"
            )
        
        return {
            "success": True,
            "tool": tool_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get tool info", tool_name=tool_name, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tool info: {str(e)}"
        )


@router.post("/batch-execute")
async def batch_execute_tools(tools: List[ToolExecutionRequest]):
    """
    Execute multiple tools in batch.
    
    Args:
        tools: List of tool execution requests
    
    Returns:
        JSON response with batch execution results
    """
    try:
        if len(tools) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 tools can be executed in batch"
            )
        
        logger.info(
            "Processing batch tool execution",
            tool_count=len(tools),
            tool_names=[tool.tool_name for tool in tools]
        )
        
        tool_service = ToolService()
        results = await tool_service.batch_execute(tools)
        
        logger.info("Batch tool execution completed successfully")
        
        return {
            "success": True,
            "results": results,
            "count": len(results),
            "metadata": {
                "type": "batch_tool_results",
                "executed_tools": [tool.tool_name for tool in tools]
            }
        }
        
    except DigiSetuException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Batch tool execution failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch execution failed: {str(e)}"
        )

