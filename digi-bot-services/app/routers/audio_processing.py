"""
Audio Processing API Router
Provides comprehensive audio processing capabilities including transcription and synthesis
"""

from __future__ import annotations
import os
import tempfile
import json
from typing import Dict, Any, Optional, Literal
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
import structlog
import aiofiles

from app.services.auth.core.auth_deps import get_current_user_required
from app.services.audio_processing import AudioTranscriberClient, SpeechSynthClient

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/audio", tags=["audio-processing"])


class TranscriptionRequest(BaseModel):
    language: Optional[str] = Field(None, description="Language code (e.g., 'en', 'es', 'hi')")
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0, description="Temperature for transcription (0.0-1.0)")
    response_format: Literal["json", "text", "verbose_json", "srt", "vtt"] = Field("json", description="Output format")
    prompt: Optional[str] = Field(None, description="Biasing prompt for better accuracy")


class SynthesisRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize", max_length=4096)
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = Field("alloy", description="Voice to use")
    audio_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = Field("mp3", description="Audio format")
    speed: Optional[float] = Field(1.0, ge=0.25, le=4.0, description="Speech speed (0.25-4.0)")


class AudioProcessingRouter:
    """Router for audio processing with transcription and synthesis"""
    
    def __init__(self):
        self.transcriber = AudioTranscriberClient()
        self.synthesizer = SpeechSynthClient()
    
    async def initialize(self):
        """Initialize audio processing clients"""
        try:
            await self.transcriber.initialize()
            await self.synthesizer.initialize()
            logger.info("Audio processing router initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize audio processing router", error=str(e))
            raise


# Global router instance
audio_router = AudioProcessingRouter()


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio/video file to transcribe"),
    language: Optional[str] = Form(None, description="Language code (e.g., 'en', 'es', 'hi')"),
    temperature: Optional[float] = Form(None, description="Temperature for transcription (0.0-1.0)"),
    response_format: str = Form("json", description="Output format: json, text, verbose_json, srt, vtt"),
    prompt: Optional[str] = Form(None, description="Biasing prompt for better accuracy"),
    current_user: Dict[str, Any] = Depends(get_current_user_required),
    http_request: Request = None
):
    """
    Transcribe audio or video file to text
    
    Supports various audio/video formats and provides multiple output formats.
    Maximum file size: 25MB
    """
    
    try:
        # Initialize if needed
        if not audio_router.transcriber._initialized:
            await audio_router.initialize()
        
        # Validate file size (25MB limit)
        if file.size and file.size > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 25MB."
            )
        
        # Validate response format
        valid_formats = ["json", "text", "verbose_json", "srt", "vtt"]
        if response_format not in valid_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid response_format. Must be one of: {valid_formats}"
            )
        
        # Log the request
        logger.info(
            "Audio transcription request",
            user_id=current_user["id"],
            filename=file.filename,
            content_type=file.content_type,
            file_size=file.size,
            language=language,
            response_format=response_format
        )
        
        # Save uploaded file temporarily
        temp_file = None
        try:
            # Create temporary file
            suffix = os.path.splitext(file.filename or "audio.mp3")[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Transcribe the file
            result = await audio_router.transcriber.transcribe_file(
                temp_path,
                language=language,
                temperature=temperature,
                response_format=response_format,
                prompt=prompt
            )
            
            logger.info(
                "Audio transcription completed",
                user_id=current_user["id"],
                filename=file.filename,
                result_length=len(str(result))
            )
            
            return {
                "success": True,
                "filename": file.filename,
                "response_format": response_format,
                "result": result
            }
            
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        logger.error(
            "Audio transcription error",
            user_id=current_user["id"],
            filename=file.filename,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/transcribe-bytes")
async def transcribe_audio_bytes(
    request: TranscriptionRequest,
    file: UploadFile = File(..., description="Audio/video file to transcribe"),
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Transcribe audio from uploaded bytes (alternative endpoint)
    
    Uses the bytes-based transcription method for in-memory processing.
    """
    
    try:
        # Initialize if needed
        if not audio_router.transcriber._initialized:
            await audio_router.initialize()
        
        # Validate file size
        if file.size and file.size > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 25MB."
            )
        
        # Read file content
        content = await file.read()
        
        # Log the request
        logger.info(
            "Audio transcription (bytes) request",
            user_id=current_user["id"],
            filename=file.filename,
            content_type=file.content_type,
            file_size=len(content)
        )
        
        # Transcribe from bytes
        result = await audio_router.transcriber.transcribe_bytes(
            content,
            filename=file.filename or "audio.mp3",
            language=request.language,
            temperature=request.temperature,
            response_format=request.response_format,
            prompt=request.prompt
        )
        
        return {
            "success": True,
            "filename": file.filename,
            "response_format": request.response_format,
            "result": result
        }
        
    except Exception as e:
        logger.error(
            "Audio transcription (bytes) error",
            user_id=current_user["id"],
            filename=file.filename,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/synthesize")
async def synthesize_speech(
    request: SynthesisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Convert text to speech and return audio file
    
    Generates audio from text using various voices and formats.
    Returns the audio file directly for download.
    """
    
    try:
        # Initialize if needed
        if not audio_router.synthesizer._initialized:
            await audio_router.initialize()
        
        # Log the request
        logger.info(
            "Speech synthesis request",
            user_id=current_user["id"],
            text_length=len(request.text),
            voice=request.voice,
            audio_format=request.audio_format,
            speed=request.speed
        )
        
        # Generate audio
        audio_bytes = await audio_router.synthesizer.synth_to_bytes(
            request.text,
            voice=request.voice,
            audio_format=request.audio_format,
            speed=request.speed
        )
        
        logger.info(
            "Speech synthesis completed",
            user_id=current_user["id"],
            audio_size=len(audio_bytes),
            voice=request.voice,
            audio_format=request.audio_format
        )
        
        # Determine content type
        content_types = {
            "mp3": "audio/mpeg",
            "opus": "audio/opus",
            "aac": "audio/aac",
            "flac": "audio/flac",
            "wav": "audio/wav",
            "pcm": "audio/pcm"
        }
        
        content_type = content_types.get(request.audio_format, "audio/mpeg")
        filename = f"speech.{request.audio_format}"
        
        # Return audio file
        import io
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(audio_bytes))
            }
        )
        
    except Exception as e:
        logger.error(
            "Speech synthesis error",
            user_id=current_user["id"],
            text=request.text[:100],
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Speech synthesis failed: {str(e)}"
        )


@router.post("/synthesize-to-file")
async def synthesize_to_file(
    request: SynthesisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Convert text to speech and save to server file
    
    Generates audio and saves it to the server's uploads directory.
    Returns the file path and metadata.
    """
    
    try:
        # Initialize if needed
        if not audio_router.synthesizer._initialized:
            await audio_router.initialize()
        
        # Create output filename
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        filename = f"speech_{unique_id}.{request.audio_format}"
        
        # Ensure uploads directory exists
        uploads_dir = "uploads/audio"
        os.makedirs(uploads_dir, exist_ok=True)
        output_path = os.path.join(uploads_dir, filename)
        
        # Log the request
        logger.info(
            "Speech synthesis to file request",
            user_id=current_user["id"],
            text_length=len(request.text),
            voice=request.voice,
            audio_format=request.audio_format,
            output_path=output_path
        )
        
        # Generate and save audio
        saved_path = await audio_router.synthesizer.synth_to_file(
            request.text,
            output_path,
            voice=request.voice,
            audio_format=request.audio_format,
            speed=request.speed
        )
        
        # Get file info
        file_size = os.path.getsize(saved_path) if os.path.exists(saved_path) else 0
        
        logger.info(
            "Speech synthesis to file completed",
            user_id=current_user["id"],
            saved_path=saved_path,
            file_size=file_size
        )
        
        return {
            "success": True,
            "filename": filename,
            "file_path": saved_path,
            "file_size": file_size,
            "voice": request.voice,
            "audio_format": request.audio_format,
            "speed": request.speed,
            "text_length": len(request.text)
        }
        
    except Exception as e:
        logger.error(
            "Speech synthesis to file error",
            user_id=current_user["id"],
            text=request.text[:100],
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Speech synthesis to file failed: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_audio_file(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_required)
):
    """
    Download a previously generated audio file
    
    Downloads audio files from the server's uploads directory.
    """
    
    try:
        # Validate filename (security check)
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )
        
        file_path = os.path.join("uploads/audio", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail="Audio file not found"
            )
        
        # Determine content type from extension
        ext = os.path.splitext(filename)[1].lower()
        content_types = {
            ".mp3": "audio/mpeg",
            ".opus": "audio/opus",
            ".aac": "audio/aac",
            ".flac": "audio/flac",
            ".wav": "audio/wav",
            ".pcm": "audio/pcm"
        }
        
        content_type = content_types.get(ext, "audio/mpeg")
        
        logger.info(
            "Audio file download",
            user_id=current_user["id"],
            filename=filename,
            file_path=file_path
        )
        
        return FileResponse(
            file_path,
            media_type=content_type,
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Audio file download error",
            user_id=current_user["id"],
            filename=filename,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"File download failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for audio processing service"""
    try:
        if not audio_router.transcriber._initialized:
            await audio_router.initialize()
        
        return {
            "status": "healthy",
            "service": "audio-processing",
            "transcriber_initialized": audio_router.transcriber._initialized,
            "synthesizer_initialized": audio_router.synthesizer._initialized,
            "transcriber_model": audio_router.transcriber.model,
            "synthesizer_model": audio_router.synthesizer.model
        }
    except Exception as e:
        logger.error("Audio processing health check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


# Export the router
__all__ = ["router"]
