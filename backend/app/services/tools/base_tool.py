"""
Base Tool Classes

Foundation classes for the Claude 4 orchestrator tool system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, AsyncGenerator
from pydantic import BaseModel
import structlog

logger = structlog.get_logger(__name__)


class ToolResult(BaseModel):
    """Result from tool execution."""
    success: bool
    content: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ToolCapabilities(BaseModel):
    """Defines what a tool can do."""
    name: str
    description: str
    category: str  # "ai_model", "multimodal", "web_search", "component_analysis"
    supports_streaming: bool = False
    supports_files: bool = False
    input_types: List[str] = ["text"]  # text, image, audio, video
    output_types: List[str] = ["text"]  # text, image, audio, component


class BaseTool(ABC):
    """Base class for all tools in the Claude 4 orchestrator system."""
    
    def __init__(self):
        self.capabilities = self._define_capabilities()
        self.initialized = False
    
    @abstractmethod
    def _define_capabilities(self) -> ToolCapabilities:
        """Define what this tool can do."""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the tool."""
        pass
    
    @abstractmethod
    async def execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Execute the tool with given request."""
        pass
    
    async def stream_execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream execution (override if tool supports streaming)."""
        if not self.capabilities.supports_streaming:
            # Fallback: execute normally and yield result
            result = await self.execute(request, context)
            yield {
                "type": "content",
                "content": result.content,
                "metadata": result.metadata,
                "final": True
            }
            return
        
        # Override this method in streaming-capable tools
        raise NotImplementedError("Streaming not implemented for this tool")
    
    async def cleanup(self) -> None:
        """Cleanup tool resources."""
        pass
    
    def get_capabilities(self) -> ToolCapabilities:
        """Get tool capabilities."""
        return self.capabilities


class AIModelTool(BaseTool):
    """Base class for AI model tools (GPT-5, GPT-4, Grok-4, etc.)."""
    
    def __init__(self):
        super().__init__()
        self.provider = None
    
    @abstractmethod
    async def _initialize_provider(self) -> None:
        """Initialize the AI provider."""
        pass
    
    async def initialize(self) -> None:
        """Initialize the AI model tool."""
        await self._initialize_provider()
        self.initialized = True
        logger.info(f"{self.capabilities.name} tool initialized")


class MultimodalTool(BaseTool):
    """Base class for multimodal tools (audio, image, etc.)."""
    
    def __init__(self):
        super().__init__()
        self.api_client = None
    
    @abstractmethod
    async def _initialize_api_client(self) -> None:
        """Initialize the API client for this multimodal tool."""
        pass
    
    async def initialize(self) -> None:
        """Initialize the multimodal tool."""
        await self._initialize_api_client()
        self.initialized = True
        logger.info(f"{self.capabilities.name} tool initialized")
