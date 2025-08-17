"""
Audio API Router - Audio Processing Endpoints

Handles audio upload, transcription, and analysis using AI audio models.
"""

import logging
from typing import Optional

import structlog
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response

from app.services.audio_service import AudioService
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/audio", tags=["audio"])


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("en"),
    model: str = Form("whisper-1")
):
    """
    Transcribe audio to text using Whisper API.
    
    Args:
        file: Audio file to transcribe
        language: Language code (default: "en")
        model: Whisper model to use (default: "whisper-1")
    
    Returns:
        JSON response with transcription
    """
    try:
        # Validate file type
        allowed_types = [
            'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/m4a', 
            'audio/ogg', 'audio/flac', 'audio/webm'
        ]
        if not file.content_type or file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File must be an audio file. Supported types: {', '.join(allowed_types)}"
            )
        
        # Validate file size (max 25MB for Whisper API)
        if file.size and file.size > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Audio file too large (max 25MB)"
            )
        
        logger.info(
            "Processing audio transcription request",
            filename=file.filename,
            content_type=file.content_type,
            language=language,
            model=model
        )
        
        audio_service = AudioService()
        result = await audio_service.transcribe(file, language, model)
        
        logger.info("Audio transcription completed successfully")
        
        return {
            "success": True,
            "transcription": result,
            "metadata": {
                "filename": file.filename,
                "content_type": file.content_type,
                "language": language,
                "model": model,
                "type": "audio_transcription"
            }
        }
        
    except DigiSetuException:
        raise
    except Exception as e:
        logger.error("Audio transcription failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio transcription failed: {str(e)}"
        )


@router.post("/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    analysis_type: str = Form("general"),
    include_transcription: bool = Form(True)
):
    """
    Analyze audio content and structure.
    
    Args:
        file: Audio file to analyze
        analysis_type: Type of analysis ("general", "sentiment", "topics")
        include_transcription: Whether to include transcription in analysis
    
    Returns:
        JSON response with audio analysis
    """
    try:
        # Validate file type
        allowed_types = [
            'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/m4a', 
            'audio/ogg', 'audio/flac', 'audio/webm'
        ]
        if not file.content_type or file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File must be an audio file. Supported types: {', '.join(allowed_types)}"
            )
        
        logger.info(
            "Processing audio analysis request",
            filename=file.filename,
            content_type=file.content_type,
            analysis_type=analysis_type
        )
        
        audio_service = AudioService()
        result = await audio_service.analyze_audio(file, analysis_type, include_transcription)
        
        logger.info("Audio analysis completed successfully")
        
        return {
            "success": True,
            "analysis": result,
            "metadata": {
                "filename": file.filename,
                "content_type": file.content_type,
                "analysis_type": analysis_type,
                "type": "audio_analysis"
            }
        }
        
    except DigiSetuException:
        raise
    except Exception as e:
        logger.error("Audio analysis failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio analysis failed: {str(e)}"
        )


@router.post("/generate")
async def generate_audio(
    text: str = Form(...),
    voice: str = Form("alloy"),
    model: str = Form("tts-1"),
    speed: float = Form(1.0)
):
    """
    Generate audio from text using OpenAI TTS.
    
    Args:
        text: Text to convert to speech
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
        model: TTS model (tts-1 or tts-1-hd)
        speed: Speech speed (0.25 to 4.0)
    
    Returns:
        Audio file in MP3 format
    """
    try:
        logger.info(
            "Audio generation request received",
            text_length=len(text),
            voice=voice,
            model=model,
            speed=speed
        )
        
        # Validate input
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )
        
        if len(text) > 4096:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text too long (max 4096 characters)"
            )
        
        if voice not in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid voice. Must be one of: alloy, echo, fable, onyx, nova, shimmer"
            )
        
        if model not in ["tts-1", "tts-1-hd"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid model. Must be tts-1 or tts-1-hd"
            )
        
        if not (0.25 <= speed <= 4.0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Speed must be between 0.25 and 4.0"
            )
        
        # Generate audio
        audio_service = AudioService()
        audio_bytes = await audio_service.generate_audio(
            text=text,
            voice=voice,
            model=model,
            speed=speed
        )
        
        logger.info(
            "Audio generation completed successfully",
            audio_size_bytes=len(audio_bytes)
        )
        
        # Return audio file
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=generated_audio.mp3",
                "Content-Length": str(len(audio_bytes))
            }
        )
        
    except DigiSetuException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Audio generation failed", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio generation failed: {str(e)}"
        )


@router.get("/models")
async def list_audio_models():
    """
    List available audio processing models.
    
    Returns:
        JSON response with available models
    """
    try:
        audio_service = AudioService()
        models = await audio_service.list_available_models()
        
        return {
            "success": True,
            "models": models
        }
        
    except Exception as e:
        logger.error("Failed to list audio models", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list models: {str(e)}"
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get supported audio file formats.
    
    Returns:
        JSON response with supported formats
    """
    return {
        "success": True,
        "supported_formats": [
            {
                "format": "MP3",
                "mime_type": "audio/mpeg",
                "extensions": [".mp3"]
            },
            {
                "format": "WAV",
                "mime_type": "audio/wav",
                "extensions": [".wav"]
            },
            {
                "format": "M4A",
                "mime_type": "audio/m4a",
                "extensions": [".m4a"]
            },
            {
                "format": "OGG",
                "mime_type": "audio/ogg",
                "extensions": [".ogg"]
            },
            {
                "format": "FLAC",
                "mime_type": "audio/flac",
                "extensions": [".flac"]
            },
            {
                "format": "WEBM",
                "mime_type": "audio/webm",
                "extensions": [".webm"]
            }
        ],
        "max_file_size": "25MB",
        "max_duration": "No limit"
    }
