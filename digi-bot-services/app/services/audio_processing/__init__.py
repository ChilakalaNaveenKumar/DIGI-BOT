"""
Audio Processing Service Package

This package provides clients for audio-related AI operations:
- AudioTranscriberClient: Speech-to-text with automatic model fallback
- SpeechSynthClient: Text-to-speech with multiple voice options

Both clients use OpenAI's stable audio endpoints for reliable audio processing.
"""

from .audio_transcriber import AudioTranscriberClient
from .speech_synth import SpeechSynthClient

__all__ = ["AudioTranscriberClient", "SpeechSynthClient"]
