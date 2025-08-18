"""
Image Tools

3 separate image tools for analysis, generation, and editing.
"""

from typing import Dict, Any, Optional, AsyncGenerator
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.tools.base_tool import MultimodalTool, ToolCapabilities, ToolResult
from app.services.ai_providers.openai_provider import OpenAIProvider
from app.services.file_service import FileService
from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class ImageAnalysisTool(MultimodalTool):
    """Tool for analyzing and understanding images using vision models."""
    
    def _define_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            name="image_analysis_tool",
            description="Analyze and understand images, extract information, describe visual content",
            category="multimodal",
            supports_streaming=True,
            supports_files=True,
            input_types=["image", "text"],
            output_types=["text"]
        )
    
    async def _initialize_api_client(self) -> None:
        """Initialize OpenAI client for vision."""
        self.provider = OpenAIProvider()
        await self.provider.initialize()
    
    async def execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Execute image analysis."""
        try:
            messages = request.get("messages", [])
            model = request.get("model", "gpt-4o")
            max_tokens = request.get("max_tokens", 1000)
            
            if not messages:
                return ToolResult(
                    success=False,
                    content="",
                    error="No messages provided for image analysis"
                )
            
            # Use chat completions for vision analysis
            response = await self.provider.generate_completion(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            metadata = {
                "model": model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "provider": "openai",
                "analysis_type": "vision"
            }
            
            return ToolResult(
                success=True,
                content=content,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error("Image analysis failed", error=str(e))
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
        """Stream image analysis."""
        try:
            messages = request.get("messages", [])
            model = request.get("model", "gpt-4o")
            max_tokens = request.get("max_tokens", 1000)
            
            if not messages:
                yield {
                    "type": "error",
                    "content": "No messages provided for image analysis",
                    "final": True
                }
                return
            
            async for chunk in self.provider.stream_completion(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=0.7
            ):
                yield {
                    "type": "content",
                    "content": chunk.get("content", ""),
                    "metadata": {
                        "model": model,
                        "provider": "openai",
                        "tool": "image_analysis_tool",
                        "analysis_type": "vision"
                    },
                    "final": chunk.get("final", False)
                }
                
        except Exception as e:
            logger.error("Image analysis streaming failed", error=str(e))
            yield {
                "type": "error",
                "content": f"Image analysis streaming failed: {str(e)}",
                "final": True
            }


class ImageGenerationTool(MultimodalTool):
    """Tool for generating images from text prompts."""
    
    def _define_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            name="image_generation_tool",
            description="Generate images from text descriptions using advanced image generation models",
            category="multimodal",
            supports_streaming=False,  # Image generation is typically not streamed
            supports_files=False,
            input_types=["text"],
            output_types=["image"]
        )
    
    async def _initialize_api_client(self) -> None:
        """Initialize OpenAI client for image generation."""
        self.provider = OpenAIProvider()
        await self.provider.initialize()
    
    async def execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Execute image generation."""
        try:
            prompt = request.get("prompt")
            model = request.get("model", "dall-e-3")
            size = request.get("size", "1024x1024")
            quality = request.get("quality", "hd")  # Changed from "standard" to "hd"
            n = request.get("n", 1)
            
            if not prompt:
                return ToolResult(
                    success=False,
                    content="",
                    error="No prompt provided for image generation"
                )
            
            # Use OpenAI image generation API
            response = await self.provider.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n
            )
            
            # Extract image URLs
            image_urls = [img.url for img in response.data]
            
            # TODO: Fix database saving for generated images
            # Temporarily disabled due to SQLAlchemy async context issue
            saved_files = []
            context = context or {}
            # user_id = context.get("user_id")
            # db = context.get("db")
            
            if False:  # Temporarily disabled
                file_service = FileService()
                for i, image_url in enumerate(image_urls):
                    try:
                        file_record = await file_service.save_generated_image(
                            image_url=image_url,
                            user_id=user_id,
                            db=db,
                            filename=f"generated_image_{i+1}.png",
                            metadata={
                                "model": model,
                                "size": size,
                                "quality": quality,
                                "provider": "openai",
                                "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt
                            }
                        )
                        saved_files.append(file_record)
                    except Exception as e:
                        logger.error(f"Failed to save image {i+1}", error=str(e))
            
            metadata = {
                "model": model,
                "size": size,
                "quality": quality,
                "provider": "openai",
                "images_generated": len(image_urls),
                "saved_files": [{"file_id": f.file_id, "filename": f.filename, "url": f.url} for f in saved_files]
            }
            
            content_parts = [f"Generated {len(image_urls)} image(s)"]
            if saved_files:
                content_parts.append(f"Saved {len(saved_files)} image(s) to your files")
            content_parts.extend(image_urls)
            
            return ToolResult(
                success=True,
                content="\n".join(content_parts),
                metadata={**metadata, "image_urls": image_urls}
            )
            
        except Exception as e:
            logger.error("Image generation failed", error=str(e))
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )


class ImageEditingTool(MultimodalTool):
    """Tool for editing existing images with masks and prompts."""
    
    def _define_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            name="image_editing_tool",
            description="Edit existing images using masks and text prompts for inpainting and modifications",
            category="multimodal",
            supports_streaming=False,  # Image editing is typically not streamed
            supports_files=True,
            input_types=["image", "text"],
            output_types=["image"]
        )
    
    async def _initialize_api_client(self) -> None:
        """Initialize OpenAI client for image editing."""
        self.provider = OpenAIProvider()
        await self.provider.initialize()
    
    async def execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Execute image editing."""
        try:
            image = request.get("image")
            mask = request.get("mask")
            prompt = request.get("prompt")
            model = request.get("model", "gpt-image-1")
            size = request.get("size", "1024x1024")
            n = request.get("n", 1)
            
            if not image or not prompt:
                return ToolResult(
                    success=False,
                    content="",
                    error="Image file and prompt are required for image editing"
                )
            
            # Prepare editing parameters
            edit_params = {
                "model": model,
                "image": image,
                "prompt": prompt,
                "size": size,
                "n": n
            }
            
            if mask:
                edit_params["mask"] = mask
            
            # Use OpenAI image editing API
            response = await self.provider.client.images.edit(**edit_params)
            
            # Extract edited image URLs
            image_urls = [img.url for img in response.data]
            
            metadata = {
                "model": model,
                "size": size,
                "provider": "openai",
                "images_edited": len(image_urls),
                "has_mask": bool(mask)
            }
            
            return ToolResult(
                success=True,
                content=f"Edited {len(image_urls)} image(s): {', '.join(image_urls)}",
                metadata={**metadata, "image_urls": image_urls}
            )
            
        except Exception as e:
            logger.error("Image editing failed", error=str(e))
            return ToolResult(
                success=False,
                content="",
                error=str(e)
            )
