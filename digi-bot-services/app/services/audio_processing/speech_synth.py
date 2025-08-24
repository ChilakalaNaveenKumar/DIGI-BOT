import os
from typing import Optional, Literal
from openai import AsyncOpenAI

# Stable TTS model; voices: alloy, verse, coral, amber, sage
# tts-1: $0.015/1k chars, tts-1-hd: $0.030/1k chars (higher quality)
DefaultTTS = "tts-1"

class SpeechSynthClient:
    """
    Async text-to-speech client.
    - synth_to_bytes(text, voice="alloy"): returns raw audio bytes (mp3 by default)
    - synth_to_file(text, out_path, voice="alloy"): writes audio to disk
    """

    def __init__(self, api_key: Optional[str] = None, model: str = DefaultTTS):
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        await self.client.models.list()
        self._initialized = True

    async def synth_to_bytes(
        self,
        text: str,
        *,
        voice: str = "alloy",
        audio_format: Literal["mp3","wav","flac","opus","aac"] = "mp3",
        speed: Optional[float] = None   # 0.25–4.0 (if supported)
    ) -> bytes:
        if not self._initialized:
            await self.initialize()

        params = {
            "model": self.model,
            "voice": voice,
            "input": text,
            "response_format": audio_format,
        }
        if speed is not None:
            params["speed"] = speed

        resp = await self.client.audio.speech.create(**params)
        return resp.content  # raw bytes

    async def synth_to_file(
        self,
        text: str,
        out_path: str,
        *,
        voice: str = "alloy",
        audio_format: Literal["mp3","wav","flac","opus","aac"] = "mp3",
        speed: Optional[float] = None
    ) -> str:
        data = await self.synth_to_bytes(text, voice=voice, audio_format=audio_format, speed=speed)
        with open(out_path, "wb") as f:
            f.write(data)
        return out_path
