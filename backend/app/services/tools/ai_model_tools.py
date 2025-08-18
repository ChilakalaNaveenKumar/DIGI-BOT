"""
AI Model Tools

Specialized tools for different AI models (GPT-5, GPT-4, Grok-4) that Claude 4 can use.
"""

from typing import Dict, Any, Optional, AsyncGenerator
import structlog
from app.services.tools.base_tool import AIModelTool, ToolCapabilities, ToolResult
from app.services.ai_providers.openai_provider import OpenAIProvider
from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.ai_providers.grok_provider import GrokProvider

logger = structlog.get_logger(__name__)


class GPT5Tool(AIModelTool):
    """GPT-5 tool for complex reasoning and latest knowledge."""
    
    def _define_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            name="gpt5_tool",
            description="Use for complex reasoning, advanced analysis, latest knowledge, and sophisticated problem-solving",
            category="ai_model",
            supports_streaming=True,
            supports_files=True,
            input_types=["text", "image"],
            output_types=["text"]
        )
    
    async def _initialize_provider(self) -> None:
        """Initialize OpenAI provider for GPT-5."""
        self.provider = OpenAIProvider()
        await self.provider.initialize()
    
    async def execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Execute GPT-5 completion."""
        try:
            messages = request.get("messages", [])
            model = request.get("model", "gpt-5")
            temperature = request.get("temperature", 0.7)
            max_tokens = request.get("max_tokens")
            tools = request.get("tools")
            
            response = await self.provider.generate_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools
            )
            
            content = response.choices[0].message.content
            metadata = {
                "model": model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "provider": "openai"
            }
            
            return ToolResult(
                success=True,
                content=content,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error("GPT-5 tool execution failed", error=str(e))
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )
    
    async def stream_execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream GPT-5 completion."""
        try:
            messages = request.get("messages", [])
            model = request.get("model", "gpt-5")
            temperature = request.get("temperature", 0.7)
            max_tokens = request.get("max_tokens")
            tools = request.get("tools")
            
            async for chunk in self.provider.stream_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools
            ):
                yield {
                    "type": "content",
                    "content": chunk.get("content", ""),
                    "metadata": {
                        "model": model,
                        "provider": "openai",
                        "tool": "gpt5_tool"
                    },
                    "final": chunk.get("final", False)
                }
                
        except Exception as e:
            logger.error("GPT-5 streaming failed", error=str(e))
            yield {
                "type": "error",
                "content": f"GPT-5 streaming failed: {str(e)}",
                "final": True
            }


class GPT4Tool(AIModelTool):
    """GPT-4 tool for general intelligence and coding tasks."""
    
    def _define_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            name="gpt4_tool",
            description="Use for coding, general intelligence, structured tasks, and reliable problem-solving",
            category="ai_model",
            supports_streaming=True,
            supports_files=True,
            input_types=["text", "image"],
            output_types=["text"]
        )
    
    async def _initialize_provider(self) -> None:
        """Initialize OpenAI provider for GPT-4."""
        self.provider = OpenAIProvider()
        await self.provider.initialize()
    
    async def execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Execute GPT-4 completion."""
        try:
            messages = request.get("messages", [])
            model = request.get("model", "gpt-4o")
            temperature = request.get("temperature", 0.7)
            max_tokens = request.get("max_tokens")
            tools = request.get("tools")
            
            response = await self.provider.generate_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools
            )
            
            content = response.choices[0].message.content
            metadata = {
                "model": model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "provider": "openai"
            }
            
            return ToolResult(
                success=True,
                content=content,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error("GPT-4 tool execution failed", error=str(e))
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )
    
    async def stream_execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream GPT-4 completion."""
        try:
            messages = request.get("messages", [])
            model = request.get("model", "gpt-4o")
            temperature = request.get("temperature", 0.7)
            max_tokens = request.get("max_tokens")
            tools = request.get("tools")
            
            async for chunk in self.provider.stream_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools
            ):
                yield {
                    "type": "content",
                    "content": chunk.get("content", ""),
                    "metadata": {
                        "model": model,
                        "provider": "openai",
                        "tool": "gpt4_tool"
                    },
                    "final": chunk.get("final", False)
                }
                
        except Exception as e:
            logger.error("GPT-4 streaming failed", error=str(e))
            yield {
                "type": "error",
                "content": f"GPT-4 streaming failed: {str(e)}",
                "final": True
            }


class Grok4Tool(AIModelTool):
    """Grok-4 tool for real-time information and current events."""
    
    def _define_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            name="grok4_tool",
            description="Use for real-time information, current events, search-enhanced responses, and up-to-date knowledge",
            category="ai_model",
            supports_streaming=True,
            supports_files=True,
            input_types=["text", "image"],
            output_types=["text"]
        )
    
    async def _initialize_provider(self) -> None:
        """Initialize Grok provider for Grok-4."""
        self.provider = GrokProvider()
        await self.provider.initialize()
    
    async def execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Execute Grok-4 completion."""
        try:
            messages = request.get("messages", [])
            model = request.get("model", "grok-4")
            temperature = request.get("temperature", 0.7)
            max_tokens = request.get("max_tokens")
            tools = request.get("tools")
            enable_search = request.get("enable_search", True)
            
            response = await self.provider.generate_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
                enable_search=enable_search
            )
            
            content = response["choices"][0]["message"]["content"]
            metadata = {
                "model": model,
                "tokens_used": response.get("usage", {}).get("total_tokens", 0),
                "provider": "grok",
                "search_enabled": enable_search
            }
            
            return ToolResult(
                success=True,
                content=content,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error("Grok-4 tool execution failed", error=str(e))
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )
    
    async def stream_execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream Grok-4 completion."""
        try:
            messages = request.get("messages", [])
            model = request.get("model", "grok-4")
            temperature = request.get("temperature", 0.7)
            max_tokens = request.get("max_tokens")
            tools = request.get("tools")
            enable_search = request.get("enable_search", True)
            
            async for chunk in self.provider.stream_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
                enable_search=enable_search
            ):
                yield {
                    "type": "content",
                    "content": chunk.get("content", ""),
                    "metadata": {
                        "model": model,
                        "provider": "grok",
                        "tool": "grok4_tool",
                        "search_enabled": enable_search
                    },
                    "final": chunk.get("final", False)
                }
                
        except Exception as e:
            logger.error("Grok-4 streaming failed", error=str(e))
            yield {
                "type": "error",
                "content": f"Grok-4 streaming failed: {str(e)}",
                "final": True
            }
