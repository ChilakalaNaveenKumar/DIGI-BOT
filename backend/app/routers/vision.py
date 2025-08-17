"""
Vision API Router - Image Analysis Endpoints

Handles image upload and analysis using AI vision models.
"""

import logging
from typing import Optional

import structlog
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from app.services.vision_service import VisionService
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/vision", tags=["vision"])


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    prompt: str = Form("Describe this image in detail"),
    model: str = Form("gpt-4-vision-preview")
):
    """
    Analyze uploaded image with AI vision models.
    
    Args:
        file: Image file to analyze
        prompt: Analysis prompt (default: "Describe this image in detail")
        model: Vision model to use (default: "gpt-4-vision-preview")
    
    Returns:
        JSON response with image analysis
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Validate file size (max 20MB)
        if file.size and file.size > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image file too large (max 20MB)"
            )
        
        logger.info(
            "Processing image analysis request",
            filename=file.filename,
            content_type=file.content_type,
            prompt=prompt[:100] + "..." if len(prompt) > 100 else prompt
        )
        
        vision_service = VisionService()
        result = await vision_service.analyze_image(file, prompt, model)
        
        logger.info("Image analysis completed successfully")
        
        return {
            "success": True,
            "analysis": result,
            "metadata": {
                "filename": file.filename,
                "content_type": file.content_type,
                "model": model,
                "type": "image_analysis"
            }
        }
        
    except DigiSetuException:
        raise
    except Exception as e:
        logger.error("Image analysis failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image analysis failed: {str(e)}"
        )


@router.post("/stream")
async def stream_image_analysis(
    file: UploadFile = File(...),
    prompt: str = Form("Analyze this image"),
    model: str = Form("gpt-4-vision-preview")
):
    """
    Stream image analysis results in real-time.
    
    Args:
        file: Image file to analyze
        prompt: Analysis prompt
        model: Vision model to use
    
    Returns:
        Streaming response with analysis chunks
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        logger.info(
            "Processing streaming image analysis request",
            filename=file.filename,
            content_type=file.content_type
        )
        
        vision_service = VisionService()
        
        async def generate_stream():
            try:
                async for chunk in vision_service.stream_image_analysis(file, prompt, model):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error("Streaming analysis failed", error=str(e))
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except DigiSetuException:
        raise
    except Exception as e:
        logger.error("Streaming image analysis setup failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Streaming setup failed: {str(e)}"
        )


@router.get("/models")
async def list_vision_models():
    """
    List available vision models.
    
    Returns:
        JSON response with available models
    """
    try:
        vision_service = VisionService()
        models = await vision_service.list_available_models()
        
        return {
            "success": True,
            "models": models
        }
        
    except Exception as e:
        logger.error("Failed to list vision models", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list models: {str(e)}"
        )

