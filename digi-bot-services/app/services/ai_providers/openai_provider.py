"""
Simple OpenAI Provider - GPT-5 Focus
"""
import json
from typing import AsyncGenerator, Dict, List, Optional, Any
import structlog
from openai import AsyncOpenAI
from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class OpenAIProvider:
    """Simple OpenAI provider - GPT-5 has everything built-in."""
    
    def __init__(self):
        self.client = None
        self.name = "openai"
        self.models = {
            "gpt-5": {
                "name": "GPT-5 (2025)",
                "max_output": 128000,
                "supports_everything": True  # Vision, audio, tools, reasoning - all built-in
            },
            "gpt-4o": {
                "name": "GPT-4o (Fallback)",
                "max_output": 16000,
                "supports_everything": True
            }
        }
    
    async def initialize(self):
        """Initialize the OpenAI client."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("OpenAI provider initialized")
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-5"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Simple streaming - GPT-5 handles everything."""
        
        try:
            # GPT-5 with everything built-in
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                max_completion_tokens=self.models.get(model, {}).get("max_output", 128000),
                tools="auto"  # GPT-5 automatically chooses tools
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield {
                        "type": "content",
                        "content": chunk.choices[0].delta.content,
                        "provider": self.name,
                        "model": model
                    }
                    
        except Exception as e:
            logger.error("OpenAI streaming failed", error=str(e))
            yield {"type": "error", "error": str(e)}
