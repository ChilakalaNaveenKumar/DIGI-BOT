"""
Vision/Image Processing API Router
Provides comprehensive vision capabilities including image analysis and generation
"""

from __future__ import annotations
import os
import tempfile
import json
import io
from typing import Dict, Any, Optional, AsyncGenerator, Literal
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
import structlog
import aiofiles

from app.services.auth.core.auth_deps import get_current_user_required
from app.services.vision_models import VisionAnalyzerClient, ImageGeneratorClient

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/vision", tags=["vision-processing"])


class ImageAnalysisRequest(BaseModel):
    prompt: str = Field("Describe the image in detail.", description="Analysis prompt")
    max_tokens: int = Field(16000, description="Maximum tokens in response")


class ImageAnalysisUrlRequest(BaseModel):
    image_url: str = Field(..., description="URL of the image to analyze")
    prompt: str = Field("Describe the image in detail.", description="Analysis prompt")
    max_tokens: int = Field(16000, description="Maximum tokens in response")


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation", max_length=4000)
    model: Literal["dall-e-2", "dall-e-3"] = Field("dall-e-3", description="Image generation model")
    size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] = Field("1024x1024", description="Image size")
    quality: Literal["standard", "hd"] = Field("standard", description="Image quality (DALL-E 3 only)")
    style: Literal["vivid", "natural"] = Field("vivid", description="Image style (DALL-E 3 only)")
    n: int = Field(1, ge=1, le=10, description="Number of images to generate")


class VisionProcessingRouter:
    """Router for vision processing with analysis and generation"""
    
    def __init__(self):
        self.vision_analyzer = VisionAnalyzerClient()
        self.image_generator = ImageGeneratorClient()
    
    async def initialize(self):
        """Initialize vision processing clients"""
        try:
            await self.vision_analyzer.initialize()
            await self.image_generator.initialize()
            logger.info("Vision processing router initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize vision processing router", error=str(e))
            raise


# Global router instance
vision_router = VisionProcessingRouter()


async def stream_analysis_response(
    analysis_generator: AsyncGenerator[Dict, None],
    user_id: str,
    source: str
) -> AsyncGenerator[str, None]:
    """Convert vision analysis stream to SSE format"""
    
    try:
        yield f"data: {json.dumps({'type': 'analysis_start', 'source': source})}\n\n"
        
        full_content = ""
        async for event in analysis_generator:
            if event["type"] == "content":
                content = event["content"]
                full_content += content
                yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
            elif event["type"] == "error":
                yield f"data: {json.dumps({'type': 'error', 'error': event['error']})}\n\n"
                return
            elif event["type"] == "completion":
                yield f"data: {json.dumps({'type': 'completion', 'finish_reason': 'done', 'full_content': full_content})}\n\n"
                return
                
    except Exception as e:
        logger.error(
            "Vision analysis streaming error",
            user_id=user_id,
            source=source,
            error=str(e)
        )
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"


@router.post("/analyze-image")
async def analyze_uploaded_image(
    file: UploadFile = File(..., description="Image file to analyze"),
    prompt: str = Form("Describe the image in detail.", description="Analysis prompt"),
    max_tokens: int = Form(16000, description="Maximum tokens in response"),
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Analyze uploaded image file
    
    Supports common image formats: PNG, JPEG, WebP, GIF
    Returns detailed analysis based on the provided prompt.
    """
    
    try:
        # Initialize if needed
        if not vision_router.vision_analyzer._initialized:
            await vision_router.initialize()
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (PNG, JPEG, WebP, GIF)"
            )
        
        # Validate file size (20MB limit for images)
        max_size = 20 * 1024 * 1024  # 20MB
        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"Image too large. Maximum size is {max_size} bytes."
            )
        
        # Log the request
        logger.info(
            "Image analysis request",
            user_id=current_user["id"],
            filename=file.filename,
            content_type=file.content_type,
            file_size=file.size,
            prompt_length=len(prompt)
        )
        
        # Save uploaded file temporarily
        temp_file = None
        try:
            # Create temporary file
            suffix = os.path.splitext(file.filename or "image.jpg")[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Analyze the image using file_id method
            analysis_stream = vision_router.vision_analyzer.analyze_file_id(
                temp_path,  # This will be uploaded to OpenAI
                prompt=prompt,
                max_tokens=max_tokens
            )
            
            # Return streaming response
            return StreamingResponse(
                stream_analysis_response(
                    analysis_stream,
                    current_user["id"],
                    f"uploaded_file:{file.filename}"
                ),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
            
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        logger.error(
            "Image analysis error",
            user_id=current_user["id"],
            filename=file.filename,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Image analysis failed: {str(e)}"
        )


@router.post("/analyze-url")
async def analyze_image_url(
    request: ImageAnalysisUrlRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Analyze image from URL
    
    Analyzes an image accessible via public URL.
    Returns streaming analysis results.
    """
    
    try:
        # Initialize if needed
        if not vision_router.vision_analyzer._initialized:
            await vision_router.initialize()
        
        # Log the request
        logger.info(
            "Image URL analysis request",
            user_id=current_user["id"],
            image_url=request.image_url,
            prompt_length=len(request.prompt)
        )
        
        # Analyze the image
        analysis_stream = vision_router.vision_analyzer.analyze_url(
            request.image_url,
            prompt=request.prompt,
            max_tokens=request.max_tokens
        )
        
        # Return streaming response
        return StreamingResponse(
            stream_analysis_response(
                analysis_stream,
                current_user["id"],
                f"url:{request.image_url}"
            ),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        logger.error(
            "Image URL analysis error",
            user_id=current_user["id"],
            image_url=request.image_url,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Image URL analysis failed: {str(e)}"
        )


@router.post("/analyze-quick")
async def analyze_image_quick(
    file: UploadFile = File(..., description="Image file to analyze"),
    prompt: str = Form("Describe the image in detail.", description="Analysis prompt"),
    max_tokens: int = Form(16000, description="Maximum tokens in response"),
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Quick image analysis (non-streaming)
    
    Analyzes an uploaded image and returns the complete result at once.
    Useful for simple integrations that don't need streaming.
    """
    
    try:
        # Initialize if needed
        if not vision_router.vision_analyzer._initialized:
            await vision_router.initialize()
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (PNG, JPEG, WebP, GIF)"
            )
        
        # Log the request
        logger.info(
            "Quick image analysis request",
            user_id=current_user["id"],
            filename=file.filename,
            content_type=file.content_type,
            file_size=file.size
        )
        
        # Save uploaded file temporarily
        temp_file = None
        try:
            # Create temporary file
            suffix = os.path.splitext(file.filename or "image.jpg")[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Get quick analysis result
            result = await vision_router.vision_analyzer.quick_analyze_file(
                temp_path,
                prompt=prompt,
                max_tokens=max_tokens
            )
            
            logger.info(
                "Quick image analysis completed",
                user_id=current_user["id"],
                filename=file.filename,
                result_length=len(result)
            )
            
            return {
                "success": True,
                "filename": file.filename,
                "prompt": prompt,
                "analysis": result,
                "file_size": file.size,
                "content_type": file.content_type
            }
            
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        logger.error(
            "Quick image analysis error",
            user_id=current_user["id"],
            filename=file.filename,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Quick image analysis failed: {str(e)}"
        )


@router.post("/generate")
async def generate_image(
    request: ImageGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Generate image from text prompt
    
    Creates images using DALL-E models based on text descriptions.
    Returns generated image URLs and metadata.
    """
    
    try:
        # Initialize if needed
        if not vision_router.image_generator._initialized:
            await vision_router.initialize()
        
        # Validate model-specific parameters
        if request.model == "dall-e-2":
            # DALL-E 2 constraints
            if request.size not in ["256x256", "512x512", "1024x1024"]:
                raise HTTPException(
                    status_code=400,
                    detail="DALL-E 2 only supports sizes: 256x256, 512x512, 1024x1024"
                )
            if request.quality != "standard":
                logger.warning("DALL-E 2 ignores quality parameter, using standard")
            if request.style != "vivid":
                logger.warning("DALL-E 2 ignores style parameter, using vivid")
        
        # Log the request
        logger.info(
            "Image generation request",
            user_id=current_user["id"],
            prompt_length=len(request.prompt),
            model=request.model,
            size=request.size,
            quality=request.quality,
            style=request.style,
            n=request.n
        )
        
        # Generate images
        result = await vision_router.image_generator.generate_images(
            prompt=request.prompt,
            model=request.model,
            size=request.size,
            quality=request.quality if request.model == "dall-e-3" else None,
            style=request.style if request.model == "dall-e-3" else None,
            n=request.n
        )
        
        logger.info(
            "Image generation completed",
            user_id=current_user["id"],
            model=request.model,
            images_generated=len(result.data),
            prompt_length=len(request.prompt)
        )
        
        return {
            "success": True,
            "prompt": request.prompt,
            "model": request.model,
            "size": request.size,
            "quality": request.quality,
            "style": request.style,
            "images": [
                {
                    "url": img.url,
                    "revised_prompt": getattr(img, 'revised_prompt', None)
                }
                for img in result.data
            ],
            "created": result.created
        }
        
    except Exception as e:
        logger.error(
            "Image generation error",
            user_id=current_user["id"],
            prompt=request.prompt[:100],
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {str(e)}"
        )


@router.post("/generate-and-save")
async def generate_and_save_image(
    request: ImageGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Generate image and save to server
    
    Generates images and saves them to the server's uploads directory.
    Returns local file paths along with the original URLs.
    """
    
    try:
        # Initialize if needed
        if not vision_router.image_generator._initialized:
            await vision_router.initialize()
        
        # Log the request
        logger.info(
            "Image generation and save request",
            user_id=current_user["id"],
            prompt_length=len(request.prompt),
            model=request.model,
            n=request.n
        )
        
        # Generate images
        result = await vision_router.image_generator.generate_images(
            prompt=request.prompt,
            model=request.model,
            size=request.size,
            quality=request.quality if request.model == "dall-e-3" else None,
            style=request.style if request.model == "dall-e-3" else None,
            n=request.n
        )
        
        # Save images to server
        import uuid
        import aiohttp
        
        saved_images = []
        uploads_dir = "uploads/images"
        os.makedirs(uploads_dir, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            for i, img in enumerate(result.data):
                try:
                    # Download image
                    async with session.get(img.url) as response:
                        if response.status == 200:
                            image_data = await response.read()
                            
                            # Generate unique filename
                            unique_id = str(uuid.uuid4())[:8]
                            filename = f"generated_{unique_id}_{i+1}.png"
                            file_path = os.path.join(uploads_dir, filename)
                            
                            # Save image
                            async with aiofiles.open(file_path, 'wb') as f:
                                await f.write(image_data)
                            
                            saved_images.append({
                                "original_url": img.url,
                                "local_path": file_path,
                                "filename": filename,
                                "file_size": len(image_data),
                                "revised_prompt": getattr(img, 'revised_prompt', None)
                            })
                            
                except Exception as e:
                    logger.error(
                        "Failed to save generated image",
                        user_id=current_user["id"],
                        image_index=i,
                        error=str(e)
                    )
                    saved_images.append({
                        "original_url": img.url,
                        "local_path": None,
                        "filename": None,
                        "error": str(e),
                        "revised_prompt": getattr(img, 'revised_prompt', None)
                    })
        
        logger.info(
            "Image generation and save completed",
            user_id=current_user["id"],
            images_generated=len(result.data),
            images_saved=len([img for img in saved_images if img.get("local_path")])
        )
        
        return {
            "success": True,
            "prompt": request.prompt,
            "model": request.model,
            "size": request.size,
            "images": saved_images,
            "created": result.created
        }
        
    except Exception as e:
        logger.error(
            "Image generation and save error",
            user_id=current_user["id"],
            prompt=request.prompt[:100],
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Image generation and save failed: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_generated_image(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Download a previously generated image
    
    Downloads images from the server's uploads directory.
    """
    
    try:
        # Validate filename (security check)
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )
        
        file_path = os.path.join("uploads/images", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Image file not found"
            )
        
        logger.info(
            "Generated image download",
            user_id=current_user["id"],
            filename=filename,
            file_path=file_path
        )
        
        return FileResponse(
            file_path,
            media_type="image/png",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Generated image download error",
            user_id=current_user["id"],
            filename=filename,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Image download failed: {str(e)}"
        )


@router.get("/models")
async def get_available_models():
    """
    Get available vision models
    
    Returns information about available models and their capabilities.
    """
    
    return {
        "success": True,
        "vision_models": {
            "analysis": {
                "gpt-4o": {
                    "description": "Advanced vision model with high accuracy",
                    "max_tokens": 16000,
                    "supported_formats": ["PNG", "JPEG", "WebP", "GIF"]
                }
            },
            "generation": {
                "dall-e-2": {
                    "description": "DALL-E 2 image generation",
                    "sizes": ["256x256", "512x512", "1024x1024"],
                    "max_images": 10
                },
                "dall-e-3": {
                    "description": "DALL-E 3 with enhanced quality and style options",
                    "sizes": ["1024x1024", "1792x1024", "1024x1792"],
                    "quality_options": ["standard", "hd"],
                    "style_options": ["vivid", "natural"],
                    "max_images": 1
                }
            }
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for vision processing service"""
    try:
        return {
            "status": "healthy",
            "service": "vision-processing",
            "vision_analyzer_initialized": vision_router.vision_analyzer._initialized,
            "image_generator_initialized": vision_router.image_generator._initialized,
            "vision_model": vision_router.vision_analyzer.model,
            "generation_model": vision_router.image_generator.model
        }
    except Exception as e:
        logger.error("Vision processing health check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


# Export the router
__all__ = ["router"]
