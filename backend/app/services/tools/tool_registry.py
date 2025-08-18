"""
Tool Registry

Central registry for managing all tools in the Claude 4 orchestrator system.
"""

from typing import Dict, List, Optional, Any
import structlog
from app.services.tools.base_tool import BaseTool, ToolCapabilities

logger = structlog.get_logger(__name__)


class ToolRegistry:
    """Central registry for all available tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._capabilities_cache: Dict[str, ToolCapabilities] = {}
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize all registered tools."""
        logger.info("Initializing tool registry")
        
        for tool_name, tool in self._tools.items():
            try:
                await tool.initialize()
                self._capabilities_cache[tool_name] = tool.get_capabilities()
                logger.info(f"Tool '{tool_name}' initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize tool '{tool_name}'", error=str(e))
                # Remove failed tool from registry
                del self._tools[tool_name]
        
        self.initialized = True
        logger.info(f"Tool registry initialized with {len(self._tools)} tools")
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a new tool."""
        capabilities = tool.get_capabilities()
        tool_name = capabilities.name
        
        if tool_name in self._tools:
            logger.warning(f"Tool '{tool_name}' already registered, overwriting")
        
        self._tools[tool_name] = tool
        logger.info(f"Tool '{tool_name}' registered")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(tool_name)
    
    def get_tools_by_category(self, category: str) -> List[BaseTool]:
        """Get all tools in a specific category."""
        return [
            tool for tool in self._tools.values()
            if tool.get_capabilities().category == category
        ]
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tools."""
        return self._tools.copy()
    
    def get_tool_capabilities(self, tool_name: str) -> Optional[ToolCapabilities]:
        """Get capabilities for a specific tool."""
        return self._capabilities_cache.get(tool_name)
    
    def get_all_capabilities(self) -> Dict[str, ToolCapabilities]:
        """Get capabilities for all tools."""
        return self._capabilities_cache.copy()
    
    def find_tools_for_task(
        self, 
        task_type: str, 
        input_types: List[str] = None,
        supports_streaming: bool = None
    ) -> List[str]:
        """
        Find tools suitable for a specific task.
        
        Args:
            task_type: Type of task (reasoning, coding, search, etc.)
            input_types: Required input types (text, image, audio)
            supports_streaming: Whether streaming support is required
            
        Returns:
            List of tool names that match the criteria
        """
        matching_tools = []
        
        for tool_name, capabilities in self._capabilities_cache.items():
            # Check streaming requirement
            if supports_streaming is not None and capabilities.supports_streaming != supports_streaming:
                continue
            
            # Check input types
            if input_types:
                if not all(input_type in capabilities.input_types for input_type in input_types):
                    continue
            
            # Task-specific logic
            if self._tool_matches_task(capabilities, task_type):
                matching_tools.append(tool_name)
        
        return matching_tools
    
    def _tool_matches_task(self, capabilities: ToolCapabilities, task_type: str) -> bool:
        """Check if a tool matches a specific task type."""
        task_mappings = {
            "reasoning": ["ai_model"],
            "coding": ["ai_model"],
            "search": ["ai_model", "web_search"],
            "current_events": ["ai_model"],  # Grok-4 specifically
            "audio_transcription": ["multimodal"],
            "audio_generation": ["multimodal"],
            "image_analysis": ["multimodal"],
            "image_generation": ["multimodal"],
            "image_editing": ["multimodal"],
            "component_analysis": ["component_analysis"],
            "web_search": ["web_search"]
        }
        
        allowed_categories = task_mappings.get(task_type, [])
        return capabilities.category in allowed_categories
    
    async def cleanup(self) -> None:
        """Cleanup all tools."""
        logger.info("Cleaning up tool registry")
        
        for tool_name, tool in self._tools.items():
            try:
                await tool.cleanup()
                logger.info(f"Tool '{tool_name}' cleaned up")
            except Exception as e:
                logger.error(f"Failed to cleanup tool '{tool_name}'", error=str(e))
        
        self._tools.clear()
        self._capabilities_cache.clear()
        self.initialized = False
        logger.info("Tool registry cleanup completed")
