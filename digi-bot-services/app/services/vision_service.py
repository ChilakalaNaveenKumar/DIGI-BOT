"""
Vision Service - Image Analysis and Processing

Handles image analysis using AI vision models like GPT-4 Vision and Claude Vision.
"""

import base64
import json
import time
from typing import AsyncGenerator, Dict, List, Optional

import structlog
from fastapi import UploadFile
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.core.config import get_settings
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)
settings = get_settings()


class VisionService:
    """Service for handling image analysis and vision tasks."""
    
    def __init__(self):
        """Initialize vision service with AI clients."""
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize OpenAI client if API key is available
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Initialize Anthropic client if API key is available
        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def analyze_image(
        self, 
        image_file: UploadFile, 
        prompt: str, 
        model: str = "gpt-4-vision-preview"
    ) -> str:
        """
        Analyze image using specified AI vision model.
        
        Args:
            image_file: Uploaded image file
            prompt: Analysis prompt
            model: Vision model to use
        
        Returns:
            Analysis result as string
        
        Raises:
            DigiSetuException: If analysis fails
        """
        try:
            start_time = time.time()
            
            # Read and encode image
            image_data = await image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Determine which client to use based on model
            if model.startswith('gpt-4') and self.openai_client:
                result = await self._analyze_with_openai(base64_image, prompt, model)
            elif model.startswith('claude') and self.anthropic_client:
                result = await self._analyze_with_anthropic(base64_image, prompt, model)
            else:
                # Fallback to OpenAI if available
                if self.openai_client:
                    result = await self._analyze_with_openai(base64_image, prompt, "gpt-4-vision-preview")
                else:
                    raise DigiSetuException(
                        "VISION_SERVICE_UNAVAILABLE",
                        "No vision service available. Please configure API keys.",
                        500
                    )
            
            analysis_time = time.time() - start_time
            
            logger.info(
                "Image analysis completed",
                model=model,
                analysis_time=analysis_time,
                result_length=len(result)
            )
            
            return result
            
        except DigiSetuException:
            raise
        except Exception as e:
            logger.error("Image analysis failed", error=str(e), exc_info=True)
            raise DigiSetuException(
                "VISION_ANALYSIS_FAILED",
                f"Image analysis failed: {str(e)}",
                500,
                {"model": model, "prompt": prompt[:100]}
            )
    
    async def _analyze_with_openai(
        self, 
        base64_image: str, 
        prompt: str, 
        model: str
    ) -> str:
        """Analyze image using OpenAI GPT-4 Vision."""
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error("OpenAI vision analysis failed", error=str(e))
            raise
    
    async def _analyze_with_anthropic(
        self, 
        base64_image: str, 
        prompt: str, 
        model: str
    ) -> str:
        """Analyze image using Anthropic Claude Vision."""
        try:
            response = await self.anthropic_client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error("Anthropic vision analysis failed", error=str(e))
            raise
    
    async def stream_image_analysis(
        self, 
        image_file: UploadFile, 
        prompt: str, 
        model: str = "gpt-4-vision-preview"
    ) -> AsyncGenerator[str, None]:
        """
        Stream image analysis results in real-time.
        
        Args:
            image_file: Uploaded image file
            prompt: Analysis prompt
            model: Vision model to use
        
        Yields:
            Analysis chunks as JSON strings
        """
        try:
            # Read and encode image
            image_data = await image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Stream analysis based on model
            if model.startswith('gpt-4') and self.openai_client:
                async for chunk in self._stream_openai_analysis(base64_image, prompt, model):
                    yield chunk
            else:
                # For non-streaming models, simulate streaming
                result = await self.analyze_image(image_file, prompt, model)
                words = result.split()
                for i in range(0, len(words), 5):  # Stream 5 words at a time
                    chunk = " ".join(words[i:i+5])
                    yield json.dumps({"content": chunk, "type": "text"})
                    
        except Exception as e:
            logger.error("Streaming image analysis failed", error=str(e))
            yield json.dumps({"error": str(e), "type": "error"})
    
    async def _stream_openai_analysis(
        self, 
        base64_image: str, 
        prompt: str, 
        model: str
    ) -> AsyncGenerator[str, None]:
        """Stream analysis using OpenAI."""
        try:
            stream = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.7,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield json.dumps({"content": content, "type": "text"})
                    
        except Exception as e:
            logger.error("OpenAI streaming failed", error=str(e))
            raise
    
    async def list_available_models(self) -> List[Dict[str, str]]:
        """
        List available vision models.
        
        Returns:
            List of available models with their capabilities
        """
        models = []
        
        if self.openai_client:
            models.extend([
                {
                    "id": "gpt-4-vision-preview",
                    "name": "GPT-4 Vision Preview",
                    "provider": "OpenAI",
                    "capabilities": ["image_analysis", "streaming"],
                    "max_tokens": 1000
                }
            ])
        
        if self.anthropic_client:
            models.extend([
                {
                    "id": "claude-3-opus-20240229",
                    "name": "Claude 3 Opus",
                    "provider": "Anthropic",
                    "capabilities": ["image_analysis"],
                    "max_tokens": 1000
                },
                {
                    "id": "claude-3-sonnet-20240229",
                    "name": "Claude 3 Sonnet",
                    "provider": "Anthropic",
                    "capabilities": ["image_analysis"],
                    "max_tokens": 1000
                }
            ])
        
        return models
    
    async def get_image_metadata(self, image_file: UploadFile) -> Dict[str, any]:
        """
        Extract metadata from uploaded image.
        
        Args:
            image_file: Uploaded image file
        
        Returns:
            Dictionary with image metadata
        """
        try:
            from PIL import Image
            import io
            
            # Read image data
            image_data = await image_file.read()
            image = Image.open(io.BytesIO(image_data))
            
            metadata = {
                "filename": image_file.filename,
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height,
                "file_size": len(image_data),
                "has_transparency": image.mode in ('RGBA', 'LA') or 'transparency' in image.info
            }
            
            # Add EXIF data if available
            if hasattr(image, '_getexif') and image._getexif():
                metadata["exif"] = dict(image._getexif())
            
            return metadata
            
        except Exception as e:
            logger.error("Failed to extract image metadata", error=str(e))
            return {
                "filename": image_file.filename,
                "error": f"Failed to extract metadata: {str(e)}"
            }

