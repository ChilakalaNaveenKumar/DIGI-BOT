"""
Tools Package

Tool system for Claude 4 orchestrator with AI models and multimodal capabilities as tools.
"""

from .base_tool import BaseTool, AIModelTool, MultimodalTool, ToolResult, ToolCapabilities
from .tool_registry import ToolRegistry
from .ai_model_tools import GPT5Tool, GPT4Tool, Grok4Tool
from .audio_tools import AudioTranscriptionTool, AudioGenerationTool, RealtimeVoiceTool
from .image_tools import ImageAnalysisTool, ImageGenerationTool, ImageEditingTool

__all__ = [
    "BaseTool",
    "AIModelTool", 
    "MultimodalTool",
    "ToolResult",
    "ToolCapabilities",
    "ToolRegistry",
    "GPT5Tool",
    "GPT4Tool", 
    "Grok4Tool",
    "AudioTranscriptionTool",
    "AudioGenerationTool",
    "RealtimeVoiceTool",
    "ImageAnalysisTool",
    "ImageGenerationTool",
    "ImageEditingTool",
]
