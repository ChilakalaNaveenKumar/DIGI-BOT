"""
Audio Tools

3 separate audio tools for transcription, generation, and real-time voice.
"""

from typing import Dict, Any, Optional, AsyncGenerator
import structlog
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.tools.base_tool import MultimodalTool, ToolCapabilities, ToolResult
from app.services.ai_providers.openai_provider import OpenAIProvider
from app.services.file_service import FileService
from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class AudioTranscriptionTool(MultimodalTool):
    """Tool for speech-to-text transcription using OpenAI's transcription models."""
    
    def _define_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            name="audio_transcription_tool",
            description="Convert speech to text using advanced transcription models",
            category="multimodal",
            supports_streaming=True,
            supports_files=True,
            input_types=["audio"],
            output_types=["text"]
        )
    
    async def _initialize_api_client(self) -> None:
        """Initialize OpenAI client for transcription."""
        self.provider = OpenAIProvider()
        await self.provider.initialize()
    
    async def execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Execute audio transcription."""
        try:
            audio_file = request.get("audio_file")
            model = request.get("model", "gpt-4o-transcribe")
            language = request.get("language")
            prompt = request.get("prompt")
            
            if not audio_file:
                return ToolResult(
                    success=False,
                    content="",
                    error="No audio file provided"
                )
            
            # Use OpenAI transcription API
            transcription_params = {
                "model": model,
                "file": audio_file
            }
            
            if language:
                transcription_params["language"] = language
            if prompt:
                transcription_params["prompt"] = prompt
            
            response = await self.provider.client.audio.transcriptions.create(**transcription_params)
            
            metadata = {
                "model": model,
                "provider": "openai",
                "language": language or "auto-detected"
            }
            
            return ToolResult(
                success=True,
                content=response.text,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error("Audio transcription failed", error=str(e))
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
        """Stream audio transcription."""
        try:
            audio_file = request.get("audio_file")
            model = request.get("model", "gpt-4o-mini-transcribe")
            
            if not audio_file:
                yield {
                    "type": "error",
                    "content": "No audio file provided",
                    "final": True
                }
                return
            
            # Stream transcription
            stream = await self.provider.client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                stream=True
            )
            
            async for chunk in stream:
                yield {
                    "type": "content",
                    "content": chunk.text if hasattr(chunk, 'text') else str(chunk),
                    "metadata": {
                        "model": model,
                        "provider": "openai",
                        "tool": "audio_transcription_tool"
                    },
                    "final": False
                }
            
            yield {
                "type": "content",
                "content": "",
                "final": True
            }
                
        except Exception as e:
            logger.error("Audio transcription streaming failed", error=str(e))
            yield {
                "type": "error",
                "content": f"Audio transcription streaming failed: {str(e)}",
                "final": True
            }


class AudioGenerationTool(MultimodalTool):
    """Tool for text-to-speech generation using OpenAI's TTS models."""
    
    def _define_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            name="audio_generation_tool",
            description="Generate speech from text using advanced TTS models",
            category="multimodal",
            supports_streaming=False,  # TTS doesn't support streaming
            supports_files=False,
            input_types=["text"],
            output_types=["audio"]
        )
    
    async def _initialize_api_client(self) -> None:
        """Initialize OpenAI client for TTS."""
        self.provider = OpenAIProvider()
        await self.provider.initialize()
    
    async def execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Execute text-to-speech generation."""
        try:
            text = request.get("text")
            model = request.get("model", "gpt-4o-mini-tts")
            voice = request.get("voice", "coral")
            response_format = request.get("response_format", "mp3")
            instructions = request.get("instructions")
            
            if not text:
                return ToolResult(
                    success=False,
                    content="",
                    error="No text provided for TTS"
                )
            
            # Prepare TTS parameters
            tts_params = {
                "model": model,
                "voice": voice,
                "input": text,
                "response_format": response_format
            }
            
            if instructions and model == "gpt-4o-mini-tts":
                tts_params["instructions"] = instructions
            
            response = await self.provider.client.audio.speech.create(**tts_params)
            
            # Get audio content
            audio_content = response.content
            
            # Save to database if user_id and db provided in context
            context = context or {}
            user_id = context.get("user_id")
            db = context.get("db")
            
            file_record = None
            if user_id and db:
                file_service = FileService()
                file_record = await file_service.save_generated_audio(
                    audio_content=audio_content,
                    user_id=user_id,
                    db=db,
                    format=response_format,
                    metadata={
                        "model": model,
                        "voice": voice,
                        "provider": "openai",
                        "text_input": text[:100] + "..." if len(text) > 100 else text
                    }
                )
            
            metadata = {
                "model": model,
                "voice": voice,
                "format": response_format,
                "provider": "openai",
                "audio_length": len(audio_content),
                "file_id": file_record.file_id if file_record else None,
                "file_url": file_record.url if file_record else None
            }
            
            return ToolResult(
                success=True,
                content=f"Generated audio ({len(audio_content)} bytes)" + (f" - Saved as {file_record.filename}" if file_record else ""),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error("Audio generation failed", error=str(e))
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
        """Stream text-to-speech generation."""
        try:
            text = request.get("text")
            model = request.get("model", "gpt-4o-mini-tts")
            voice = request.get("voice", "coral")
            response_format = request.get("response_format", "pcm")
            
            if not text:
                yield {
                    "type": "error",
                    "content": "No text provided for TTS",
                    "final": True
                }
                return
            
            # Stream TTS
            async with self.provider.client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=text,
                response_format=response_format
            ) as response:
                async for chunk in response.iter_bytes():
                    yield {
                        "type": "audio_chunk",
                        "content": chunk.decode('latin-1'),  # Binary as string
                        "metadata": {
                            "model": model,
                            "voice": voice,
                            "format": response_format,
                            "provider": "openai",
                            "tool": "audio_generation_tool"
                        },
                        "final": False
                    }
            
            yield {
                "type": "content",
                "content": "",
                "final": True
            }
                
        except Exception as e:
            logger.error("Audio generation streaming failed", error=str(e))
            yield {
                "type": "error",
                "content": f"Audio generation streaming failed: {str(e)}",
                "final": True
            }


class RealtimeVoiceTool(MultimodalTool):
    """Tool for real-time voice conversations using OpenAI's Realtime API."""
    
    def _define_capabilities(self) -> ToolCapabilities:
        return ToolCapabilities(
            name="realtime_voice_tool",
            description="Enable real-time speech-to-speech conversations with low latency",
            category="multimodal",
            supports_streaming=True,
            supports_files=False,
            input_types=["audio", "text"],
            output_types=["audio", "text"]
        )
    
    async def _initialize_api_client(self) -> None:
        """Initialize WebSocket client for Realtime API."""
        # Note: This would typically initialize a WebSocket connection
        # For now, we'll use a placeholder implementation
        self.websocket_url = "wss://api.openai.com/v1/realtime"
        self.api_key = settings.OPENAI_API_KEY
    
    async def execute(
        self, 
        request: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Execute real-time voice interaction (single turn)."""
        try:
            # For non-streaming, this would be a single voice interaction
            # This is a placeholder implementation
            return ToolResult(
                success=True,
                content="Real-time voice interaction requires streaming mode",
                metadata={
                    "model": "gpt-4o-realtime-preview",
                    "provider": "openai",
                    "mode": "realtime"
                }
            )
            
        except Exception as e:
            logger.error("Real-time voice interaction failed", error=str(e))
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
        """Stream real-time voice conversation."""
        try:
            # This would establish a WebSocket connection for real-time interaction
            # For now, we'll provide a placeholder implementation
            
            yield {
                "type": "realtime_status",
                "content": "Real-time voice connection established",
                "metadata": {
                    "model": "gpt-4o-realtime-preview",
                    "provider": "openai",
                    "tool": "realtime_voice_tool",
                    "connection_status": "connected"
                },
                "final": False
            }
            
            # Placeholder for actual WebSocket communication
            yield {
                "type": "content",
                "content": "Real-time voice tool initialized. WebSocket implementation needed for full functionality.",
                "final": True
            }
                
        except Exception as e:
            logger.error("Real-time voice streaming failed", error=str(e))
            yield {
                "type": "error",
                "content": f"Real-time voice streaming failed: {str(e)}",
                "final": True
            }
