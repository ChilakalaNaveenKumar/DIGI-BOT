# vision_analyzer.py
import os
from typing import AsyncGenerator, Dict, Optional
from openai import AsyncOpenAI

class VisionAnalyzerClient:
    """
    Analyze images via the Responses API.
    Supports either a public image URL or an already-uploaded file_id.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model  # gpt-4o: 128k context, 16k output, multimodal
        self._initialized = False
        self.max_output_tokens = 16000  # Max for gpt-4o

    async def initialize(self):
        if self._initialized:
            return
        await self.client.models.list()
        self._initialized = True

    async def analyze_url(
        self,
        image_url: str,
        prompt: str = "Describe the image."
    ) -> AsyncGenerator[Dict, None]:
        """
        Stream analysis for an image accessible by URL.
        Yields dicts: {"type": "content", "content": str} | {"type":"completion"} | {"type":"error"}
        """
        if not self._initialized:
            await self.initialize()

        user_content = [
            {"type": "input_text", "text": prompt},
            {"type": "input_image", "image_url": image_url},
        ]

        try:
            async with self.client.responses.stream(
                model=self.model,
                input=[{"role": "user", "content": user_content}],
                max_output_tokens=self.max_output_tokens,
            ) as stream:
                async for event in stream:
                    et = getattr(event, "type", "")
                    if et == "response.output_text.delta":
                        yield {"type": "content", "content": event.delta}
                    elif et == "response.error":
                        yield {"type": "error", "error": getattr(event, "error", "unknown")}
                    elif et == "response.completed":
                        yield {"type": "completion", "finish_reason": "done"}
        except Exception as e:
            yield {"type": "error", "error": str(e)}

    async def analyze_file(
        self,
        file_id: str,
        prompt: str = "Describe the image."
    ) -> AsyncGenerator[Dict, None]:
        """
        Stream analysis for an image you have already uploaded via Files API.
        (Use client.files.create(file=...) to get a file_id first.)
        """
        if not self._initialized:
            await self.initialize()

        user_content = [
            {"type": "input_text", "text": prompt},
            # file-based image input
            {"type": "input_image", "image_file": {"file_id": file_id}},
        ]

        try:
            async with self.client.responses.stream(
                model=self.model,
                input=[{"role": "user", "content": user_content}],
                max_output_tokens=self.max_output_tokens,
            ) as stream:
                async for event in stream:
                    et = getattr(event, "type", "")
                    if et == "response.output_text.delta":
                        yield {"type": "content", "content": event.delta}
                    elif et == "response.error":
                        yield {"type": "error", "error": getattr(event, "error", "unknown")}
                    elif et == "response.completed":
                        yield {"type": "completion", "finish_reason": "done"}
        except Exception as e:
            yield {"type": "error", "error": str(e)}
