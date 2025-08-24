import os
from typing import Optional, Dict, Any, Literal
from openai import AsyncOpenAI

PrimarySTT = "gpt-4o-mini-transcribe"   # fast + accurate, 25MB max file
FallbackSTT = "whisper-1"                # widely available, 25MB max file

class AudioTranscriberClient:
    """
    Async speech-to-text client with model fallback.
    - transcribe_file(path): transcribe a local audio/video file
    - transcribe_bytes(data, filename=...): transcribe in-memory bytes
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model or PrimarySTT
        self._initialized = False
        self._models: set[str] = set()

    async def initialize(self):
        if self._initialized:
            return
        ml = await self.client.models.list()
        self._models = {m.id for m in ml.data}
        if self.model not in self._models:
            # graceful fallback
            if FallbackSTT in self._models:
                print(f"⚠️  {self.model} not available; using {FallbackSTT}")
                self.model = FallbackSTT
            else:
                raise RuntimeError(
                    f"No supported STT models available. "
                    f"Tried: {self.model}, {FallbackSTT}"
                )
        self._initialized = True

    async def transcribe_file(
        self,
        path: str,
        *,
        language: Optional[str] = None,          # e.g. "en", "es", "hi"
        temperature: Optional[float] = None,     # Whisper accepts this; 4o-mini-transcribe ignores it
        response_format: Literal["json","text","verbose_json","srt","vtt"] = "json",
        prompt: Optional[str] = None             # biasing prompt (Whisper)
    ) -> Dict[str, Any]:
        """
        Returns a dict; if response_format="json" it includes {"text": "..."}.
        For srt/vtt/text, returns {"text": <string>}.
        """
        if not self._initialized:
            await self.initialize()

        # OpenAI STT wants the raw file object (no file_id).
        # Common formats: mp3, mp4, m4a, wav, webm, ogg
        with open(path, "rb") as f:
            return await self._transcribe_core(
                file=f,
                language=language,
                temperature=temperature,
                response_format=response_format,
                prompt=prompt
            )

    async def transcribe_bytes(
        self,
        data: bytes,
        *,
        filename: str = "audio.wav",
        language: Optional[str] = None,
        temperature: Optional[float] = None,
        response_format: Literal["json","text","verbose_json","srt","vtt"] = "json",
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Same as transcribe_file, but for in-memory audio.
        """
        if not self._initialized:
            await self.initialize()

        # The SDK accepts (filename, bytes) tuple for file-like content.
        return await self._transcribe_core(
            file=(filename, data),
            language=language,
            temperature=temperature,
            response_format=response_format,
            prompt=prompt
        )

    async def _transcribe_core(
        self,
        *,
        file,
        language: Optional[str],
        temperature: Optional[float],
        response_format: str,
        prompt: Optional[str]
    ) -> Dict[str, Any]:
        """
        Internal helper to call audio.transcriptions.create with consistent return shape.
        """
        params: Dict[str, Any] = {
            "model": self.model,
            "file": file,
            "response_format": response_format
        }
        if language:     params["language"] = language
        if prompt:       params["prompt"] = prompt
        if temperature is not None and self.model == FallbackSTT:
            # Whisper supports temperature; 4o-mini-transcribe may ignore it
            params["temperature"] = temperature

        resp = await self.client.audio.transcriptions.create(**params)

        # Normalize output
        if response_format in ("text", "srt", "vtt"):
            # The SDK returns a raw string for these formats (not an object)
            return {"text": str(resp)}
        elif response_format == "json":
            # Typical JSON response has `text`
            return {"text": resp.text}
        elif response_format == "verbose_json":
            # Includes segments/timestamps when available
            return resp  # already a dict-like object
        else:
            return {"text": str(resp)}
