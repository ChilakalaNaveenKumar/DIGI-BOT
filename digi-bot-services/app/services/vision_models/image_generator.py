# image_generator.py
import os
from typing import List, Optional, Literal
from openai import AsyncOpenAI

# Image generation models: dall-e-3 (best quality), gpt-image-1 (fast), dall-e-2 (legacy)
DefaultImageModel = "gpt-image-1"

class ImageGeneratorClient:
    """
    Generate images from text.
    Uses the Images API (stable) for creation; returns base64 so you can persist to disk.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = DefaultImageModel):
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model  # gpt-image-1, dall-e-3, or dall-e-2
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        await self.client.models.list()
        self._initialized = True

    async def generate(
        self,
        prompt: str,
        size: Literal["512x512","768x768","1024x1024","2048x2048"] = "1024x1024",
        background: Optional[Literal["transparent","white","black"]] = None,
        n: int = 1
    ) -> List[dict]:
        """
        Returns a list of dicts: {"b64": str, "revised_prompt": str}
        """
        if not self._initialized:
            await self.initialize()

        # Try different models based on what's available
        # First try with dall-e-3 (most reliable)
        try:
            kwargs = dict(model="dall-e-3", prompt=prompt, size=size, n=n, response_format="b64_json")
            resp = await self.client.images.generate(**kwargs)
        except Exception as e:
            # Fallback to dall-e-2 without response_format
            try:
                kwargs = dict(model="dall-e-2", prompt=prompt, size="1024x1024", n=n)
                resp = await self.client.images.generate(**kwargs)
            except Exception as e2:
                # Last fallback - basic generation
                kwargs = dict(model=self.model, prompt=prompt, size=size, n=n)
                resp = await self.client.images.generate(**kwargs)

        out = []
        for item in resp.data:
            # Handle both b64_json and url responses
            if hasattr(item, 'b64_json') and item.b64_json:
                out.append({
                    "b64": item.b64_json,
                    "revised_prompt": getattr(item, "revised_prompt", None)
                })
            elif hasattr(item, 'url') and item.url:
                # Download URL and convert to base64
                import httpx
                import base64
                async with httpx.AsyncClient() as client:
                    img_resp = await client.get(item.url)
                    if img_resp.status_code == 200:
                        b64_data = base64.b64encode(img_resp.content).decode()
                        out.append({
                            "b64": b64_data,
                            "revised_prompt": getattr(item, "revised_prompt", None)
                        })
        return out
