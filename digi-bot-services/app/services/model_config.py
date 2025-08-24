"""
Model Configuration and Token Limits

This module provides centralized configuration for OpenAI models with their
context windows, output limits, and supported tools.

Updated: August 2025
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Configuration for an OpenAI model"""
    name: str
    context_tokens: int  # Max input tokens
    output_tokens: int   # Max output tokens
    supports_vision: bool = False
    supports_tools: bool = False
    supports_reasoning: bool = False
    cost_per_1k_input: float = 0.0  # USD per 1k input tokens
    cost_per_1k_output: float = 0.0  # USD per 1k output tokens
    description: str = ""


# Model configurations based on latest OpenAI specs
MODEL_CONFIGS = {
    # GPT-4o family - multimodal, tool-capable
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        context_tokens=128_000,
        output_tokens=16_000,
        supports_vision=True,
        supports_tools=True,
        supports_reasoning=False,
        cost_per_1k_input=2.50,
        cost_per_1k_output=10.00,
        description="Latest multimodal model with vision, tools, and large context"
    ),
    
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        context_tokens=128_000,
        output_tokens=16_000,
        supports_vision=True,
        supports_tools=True,
        supports_reasoning=False,
        cost_per_1k_input=0.15,
        cost_per_1k_output=0.60,
        description="Smaller, faster, cheaper version of gpt-4o"
    ),
    
    # GPT-4.1 family (if available)
    "gpt-4.1": ModelConfig(
        name="gpt-4.1",
        context_tokens=128_000,
        output_tokens=16_000,
        supports_vision=True,
        supports_tools=True,
        supports_reasoning=True,
        cost_per_1k_input=3.00,
        cost_per_1k_output=12.00,
        description="Enhanced reasoning and multimodal capabilities"
    ),
    
    # GPT-4.5 preview (early access)
    "gpt-4.5": ModelConfig(
        name="gpt-4.5",
        context_tokens=200_000,  # Some configs up to 1M in preview
        output_tokens=16_000,
        supports_vision=True,
        supports_tools=True,
        supports_reasoning=True,
        cost_per_1k_input=5.00,
        cost_per_1k_output=15.00,
        description="Preview model with very large context window"
    ),
    
    # GPT-5 (next generation)
    "gpt-5": ModelConfig(
        name="gpt-5",
        context_tokens=256_000,  # Estimated larger context
        output_tokens=32_000,    # Estimated larger output
        supports_vision=True,
        supports_tools=True,
        supports_reasoning=True,
        cost_per_1k_input=10.00,  # Estimated higher cost
        cost_per_1k_output=30.00,
        description="Next generation model with enhanced capabilities"
    ),
    
    # Reasoning models (o1 family)
    "o1-preview": ModelConfig(
        name="o1-preview",
        context_tokens=200_000,
        output_tokens=16_000,
        supports_vision=False,
        supports_tools=False,
        supports_reasoning=True,
        cost_per_1k_input=15.00,
        cost_per_1k_output=60.00,
        description="Advanced reasoning model with internal thinking"
    ),
    
    "o1-mini": ModelConfig(
        name="o1-mini",
        context_tokens=128_000,
        output_tokens=8_000,
        supports_vision=False,
        supports_tools=False,
        supports_reasoning=True,
        cost_per_1k_input=3.00,
        cost_per_1k_output=12.00,
        description="Smaller reasoning model, faster and cheaper"
    ),
    
    # Legacy models
    "gpt-3.5-turbo": ModelConfig(
        name="gpt-3.5-turbo",
        context_tokens=16_000,
        output_tokens=4_000,
        supports_vision=False,
        supports_tools=True,
        supports_reasoning=False,
        cost_per_1k_input=0.50,
        cost_per_1k_output=1.50,
        description="Legacy model, being phased out"
    ),
}

# Audio model configurations (not token-based)
AUDIO_MODELS = {
    "whisper-1": {
        "type": "speech-to-text",
        "max_file_size_mb": 25,
        "cost_per_minute": 0.006,
        "formats": ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
    },
    
    "gpt-4o-mini-transcribe": {
        "type": "speech-to-text", 
        "max_file_size_mb": 25,
        "cost_per_minute": 0.004,  # Estimated
        "formats": ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"],
        "description": "Faster transcription model"
    },
    
    "tts-1": {
        "type": "text-to-speech",
        "cost_per_1k_chars": 0.015,
        "voices": ["alloy", "verse", "coral", "amber", "sage"],
        "formats": ["mp3", "wav", "flac", "opus", "aac"]
    },
    
    "tts-1-hd": {
        "type": "text-to-speech",
        "cost_per_1k_chars": 0.030,
        "voices": ["alloy", "verse", "coral", "amber", "sage"],
        "formats": ["mp3", "wav", "flac", "opus", "aac"],
        "description": "Higher quality voice synthesis"
    }
}

# Image model configurations
IMAGE_MODELS = {
    "dall-e-3": {
        "type": "text-to-image",
        "sizes": ["1024x1024", "1792x1024", "1024x1792"],
        "cost_per_image": {"1024x1024": 0.040, "1792x1024": 0.080, "1024x1792": 0.080},
        "max_images_per_request": 1
    },
    
    "dall-e-2": {
        "type": "text-to-image", 
        "sizes": ["256x256", "512x512", "1024x1024"],
        "cost_per_image": {"256x256": 0.016, "512x512": 0.018, "1024x1024": 0.020},
        "max_images_per_request": 10
    },
    
    "gpt-image-1": {
        "type": "text-to-image",
        "sizes": ["512x512", "768x768", "1024x1024", "2048x2048"],
        "cost_per_image": {"512x512": 0.020, "1024x1024": 0.040, "2048x2048": 0.080},
        "max_images_per_request": 4,
        "description": "Fast image generation model"
    }
}

# Tool configurations by model
TOOL_SUPPORT = {
    "function_calling": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.5", "gpt-3.5-turbo"],
    "web_search": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.5"],
    "file_search": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.5"],
    "code_interpreter": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.5"],
    "vision": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.5"]
}


def get_model_config(model_name: str) -> Optional[ModelConfig]:
    """Get configuration for a model"""
    return MODEL_CONFIGS.get(model_name)


def get_best_model_for_task(
    task_type: str,
    needs_vision: bool = False,
    needs_tools: bool = False,
    needs_reasoning: bool = False,
    max_budget_per_1k_tokens: float = None
) -> str:
    """
    Get the best model for a specific task type.
    
    Args:
        task_type: Type of task ("chat", "analysis", "reasoning", "vision", "tools")
        needs_vision: Whether vision capabilities are required
        needs_tools: Whether tool calling is required
        needs_reasoning: Whether advanced reasoning is required
        max_budget_per_1k_tokens: Maximum budget per 1k tokens
    
    Returns:
        Best model name for the task
    """
    
    candidates = []
    
    for model_name, config in MODEL_CONFIGS.items():
        # Filter by requirements
        if needs_vision and not config.supports_vision:
            continue
        if needs_tools and not config.supports_tools:
            continue
        if needs_reasoning and not config.supports_reasoning:
            continue
        
        # Filter by budget
        if max_budget_per_1k_tokens:
            avg_cost = (config.cost_per_1k_input + config.cost_per_1k_output) / 2
            if avg_cost > max_budget_per_1k_tokens:
                continue
        
        candidates.append((model_name, config))
    
    if not candidates:
        return "gpt-4o"  # Default fallback
    
    # Task-specific preferences
    if task_type == "reasoning":
        # Prefer reasoning models
        reasoning_models = [c for c in candidates if c[1].supports_reasoning]
        if reasoning_models:
            return min(reasoning_models, key=lambda x: x[1].cost_per_1k_output)[0]
    
    elif task_type == "vision":
        # Prefer vision-capable models
        vision_models = [c for c in candidates if c[1].supports_vision]
        if vision_models:
            return min(vision_models, key=lambda x: x[1].cost_per_1k_output)[0]
    
    elif task_type == "tools":
        # Prefer tool-capable models
        tool_models = [c for c in candidates if c[1].supports_tools]
        if tool_models:
            return min(tool_models, key=lambda x: x[1].cost_per_1k_output)[0]
    
    # Default: cheapest model that meets requirements
    return min(candidates, key=lambda x: x[1].cost_per_1k_output)[0]


def estimate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost for a model call"""
    config = get_model_config(model_name)
    if not config:
        return 0.0
    
    input_cost = (input_tokens / 1000) * config.cost_per_1k_input
    output_cost = (output_tokens / 1000) * config.cost_per_1k_output
    
    return input_cost + output_cost


def get_safe_output_tokens(model_name: str, input_tokens: int, safety_margin: int = 1000) -> int:
    """
    Get safe output token limit considering input tokens and model limits.
    
    Args:
        model_name: Name of the model
        input_tokens: Number of input tokens
        safety_margin: Safety margin to leave for model processing
    
    Returns:
        Safe number of output tokens to request
    """
    config = get_model_config(model_name)
    if not config:
        return 4000  # Conservative default
    
    # Calculate available tokens
    available_tokens = config.context_tokens - input_tokens - safety_margin
    
    # Don't exceed model's max output tokens
    max_safe_output = min(available_tokens, config.output_tokens)
    
    # Ensure we have at least some output capacity
    return max(max_safe_output, 500)


def supports_tool(model_name: str, tool_type: str) -> bool:
    """Check if a model supports a specific tool type"""
    return model_name in TOOL_SUPPORT.get(tool_type, [])


# Quick reference for common use cases
RECOMMENDED_MODELS = {
    "chart_matching": "gpt-4o",      # Needs tools, good reasoning
    "vision_analysis": "gpt-4o",     # Needs vision, multimodal
    "document_analysis": "gpt-4o",   # Large context, tools
    "audio_transcription": "gpt-4o-mini-transcribe",  # Fast, cheap
    "text_to_speech": "tts-1",       # Standard quality
    "image_generation": "dall-e-3",  # Best quality
    "reasoning_tasks": "o1-mini",    # Advanced reasoning, cheaper
    "simple_chat": "gpt-4o-mini",    # Fast, cheap, capable
    "large_documents": "gpt-4.5",    # Largest context window
}
