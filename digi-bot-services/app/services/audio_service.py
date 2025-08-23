"""
Audio Service - Audio Processing and Transcription

Handles audio transcription and analysis using Whisper and other AI audio models.
"""

import tempfile
import os
import time
from typing import Dict, List, Optional

import structlog
import aiofiles
from fastapi import UploadFile
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)
settings = get_settings()


class AudioService:
    """Service for handling audio processing and transcription tasks."""
    
    def __init__(self):
        """Initialize audio service with AI clients."""
        self.openai_client = None
        
        # Initialize OpenAI client if API key is available
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def transcribe(
        self, 
        audio_file: UploadFile, 
        language: str = "en", 
        model: str = "whisper-1"
    ) -> str:
        """
        Transcribe audio to text using Whisper API.
        
        Args:
            audio_file: Uploaded audio file
            language: Language code for transcription
            model: Whisper model to use
        
        Returns:
            Transcribed text
        
        Raises:
            DigiSetuException: If transcription fails
        """
        try:
            if not self.openai_client:
                raise DigiSetuException(
                    "AUDIO_SERVICE_UNAVAILABLE",
                    "Audio service unavailable. Please configure OpenAI API key.",
                    500
                )
            
            start_time = time.time()
            
            # Save uploaded file temporarily
            temp_file_path = await self._save_temp_file(audio_file)
            
            try:
                # Transcribe using OpenAI Whisper
                async with aiofiles.open(temp_file_path, "rb") as audio:
                    transcript = await self.openai_client.audio.transcriptions.create(
                        model=model,
                        file=audio,
                        language=language,
                        response_format="text"
                    )
                
                transcription_time = time.time() - start_time
                
                logger.info(
                    "Audio transcription completed",
                    model=model,
                    language=language,
                    transcription_time=transcription_time,
                    result_length=len(transcript) if isinstance(transcript, str) else len(str(transcript))
                )
                
                # Handle different response formats
                if isinstance(transcript, str):
                    return transcript
                else:
                    return transcript.text if hasattr(transcript, 'text') else str(transcript)
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            
        except DigiSetuException:
            raise
        except Exception as e:
            logger.error("Audio transcription failed", error=str(e), exc_info=True)
            raise DigiSetuException(
                "AUDIO_TRANSCRIPTION_FAILED",
                f"Audio transcription failed: {str(e)}",
                500,
                {"model": model, "language": language}
            )
    
    async def generate_audio(
        self,
        text: str,
        voice: str = "alloy",
        model: str = "tts-1",
        speed: float = 1.0
    ) -> bytes:
        """
        Generate audio from text using OpenAI TTS.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            model: TTS model (tts-1 or tts-1-hd)
            speed: Speech speed (0.25 to 4.0)
            
        Returns:
            Audio bytes in MP3 format
        """
        try:
            start_time = time.time()
            
            logger.info(
                "Generating audio from text",
                text_length=len(text),
                voice=voice,
                model=model,
                speed=speed
            )
            
            # Generate audio using OpenAI TTS
            response = await self.openai_client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            )
            
            # Get audio bytes
            audio_bytes = response.content
            
            generation_time = time.time() - start_time
            
            logger.info(
                "Audio generation completed",
                model=model,
                voice=voice,
                generation_time=generation_time,
                audio_size_bytes=len(audio_bytes)
            )
            
            return audio_bytes
            
        except Exception as e:
            logger.error("Audio generation failed", error=str(e), exc_info=True)
            raise DigiSetuException(
                "AUDIO_GENERATION_FAILED",
                f"Audio generation failed: {str(e)}",
                500,
                {"model": model, "voice": voice, "text_length": len(text)}
            )

    async def analyze_audio(
        self, 
        audio_file: UploadFile, 
        analysis_type: str = "general",
        include_transcription: bool = True
    ) -> Dict[str, any]:
        """
        Analyze audio content and structure.
        
        Args:
            audio_file: Uploaded audio file
            analysis_type: Type of analysis to perform
            include_transcription: Whether to include transcription
        
        Returns:
            Dictionary with analysis results
        """
        try:
            start_time = time.time()
            result = {}
            
            # Get transcription if requested
            if include_transcription:
                transcription = await self.transcribe(audio_file)
                result["transcription"] = transcription
                
                # Analyze transcription based on type
                if analysis_type == "sentiment":
                    result["sentiment"] = await self._analyze_sentiment(transcription)
                elif analysis_type == "topics":
                    result["topics"] = await self._extract_topics(transcription)
                elif analysis_type == "summary":
                    result["summary"] = await self._summarize_content(transcription)
                else:  # general analysis
                    result.update(await self._general_analysis(transcription))
            
            # Get audio metadata
            result["metadata"] = await self._get_audio_metadata(audio_file)
            
            analysis_time = time.time() - start_time
            result["analysis_time"] = analysis_time
            
            logger.info(
                "Audio analysis completed",
                analysis_type=analysis_type,
                analysis_time=analysis_time
            )
            
            return result
            
        except Exception as e:
            logger.error("Audio analysis failed", error=str(e), exc_info=True)
            raise DigiSetuException(
                "AUDIO_ANALYSIS_FAILED",
                f"Audio analysis failed: {str(e)}",
                500,
                {"analysis_type": analysis_type}
            )
    
    async def _save_temp_file(self, audio_file: UploadFile) -> str:
        """Save uploaded file to temporary location."""
        # Get file extension
        file_extension = os.path.splitext(audio_file.filename or "")[1] or ".wav"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            return tmp_file.name
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, any]:
        """Analyze sentiment of transcribed text."""
        try:
            if not self.openai_client:
                return {"error": "OpenAI client not available"}
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze the sentiment of the following text. Return a JSON object with 'sentiment' (positive/negative/neutral), 'confidence' (0-1), and 'explanation'."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            import json
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                return {
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "explanation": response.choices[0].message.content
                }
                
        except Exception as e:
            logger.error("Sentiment analysis failed", error=str(e))
            return {"error": f"Sentiment analysis failed: {str(e)}"}
    
    async def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from transcribed text."""
        try:
            if not self.openai_client:
                return ["Error: OpenAI client not available"]
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract the main topics discussed in the following text. Return a JSON array of topic strings."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            import json
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                # Fallback: split by lines and clean up
                topics = response.choices[0].message.content.split('\n')
                return [topic.strip('- ').strip() for topic in topics if topic.strip()]
                
        except Exception as e:
            logger.error("Topic extraction failed", error=str(e))
            return [f"Error: Topic extraction failed: {str(e)}"]
    
    async def _summarize_content(self, text: str) -> str:
        """Summarize transcribed content."""
        try:
            if not self.openai_client:
                return "Error: OpenAI client not available"
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Provide a concise summary of the following text in 2-3 sentences."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error("Content summarization failed", error=str(e))
            return f"Error: Content summarization failed: {str(e)}"
    
    async def _general_analysis(self, text: str) -> Dict[str, any]:
        """Perform general analysis of transcribed text."""
        try:
            # Basic text statistics
            words = text.split()
            sentences = text.split('.')
            
            analysis = {
                "word_count": len(words),
                "sentence_count": len([s for s in sentences if s.strip()]),
                "average_words_per_sentence": len(words) / max(len([s for s in sentences if s.strip()]), 1),
                "character_count": len(text),
                "estimated_reading_time": len(words) / 200  # Average reading speed
            }
            
            # Get AI-powered insights if available
            if self.openai_client:
                try:
                    response = await self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "Analyze this text and provide key insights including main themes, tone, and notable points. Keep it concise."
                            },
                            {
                                "role": "user",
                                "content": text[:2000]  # Limit text length
                            }
                        ],
                        max_tokens=200,
                        temperature=0.3
                    )
                    
                    analysis["ai_insights"] = response.choices[0].message.content
                    
                except Exception as e:
                    analysis["ai_insights"] = f"AI insights unavailable: {str(e)}"
            
            return analysis
            
        except Exception as e:
            logger.error("General analysis failed", error=str(e))
            return {"error": f"General analysis failed: {str(e)}"}
    
    async def _get_audio_metadata(self, audio_file: UploadFile) -> Dict[str, any]:
        """Extract metadata from audio file."""
        try:
            metadata = {
                "filename": audio_file.filename,
                "content_type": audio_file.content_type,
                "file_size": audio_file.size if hasattr(audio_file, 'size') else None
            }
            
            # Try to get additional audio metadata using mutagen (if available)
            try:
                import mutagen
                temp_file_path = await self._save_temp_file(audio_file)
                
                try:
                    audio_info = mutagen.File(temp_file_path)
                    if audio_info:
                        metadata.update({
                            "duration": getattr(audio_info.info, 'length', None),
                            "bitrate": getattr(audio_info.info, 'bitrate', None),
                            "sample_rate": getattr(audio_info.info, 'sample_rate', None),
                            "channels": getattr(audio_info.info, 'channels', None)
                        })
                finally:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                        
            except ImportError:
                logger.debug("Mutagen not available for audio metadata extraction")
            except Exception as e:
                logger.warning("Failed to extract detailed audio metadata", error=str(e))
            
            return metadata
            
        except Exception as e:
            logger.error("Failed to get audio metadata", error=str(e))
            return {
                "filename": audio_file.filename,
                "error": f"Failed to extract metadata: {str(e)}"
            }
    
    async def list_available_models(self) -> List[Dict[str, str]]:
        """
        List available audio processing models.
        
        Returns:
            List of available models
        """
        models = []
        
        if self.openai_client:
            models.extend([
                {
                    "id": "whisper-1",
                    "name": "Whisper v1",
                    "provider": "OpenAI",
                    "capabilities": ["transcription", "translation"],
                    "supported_formats": ["mp3", "wav", "m4a", "ogg", "flac", "webm"],
                    "max_file_size": "25MB"
                }
            ])
        
        return models
