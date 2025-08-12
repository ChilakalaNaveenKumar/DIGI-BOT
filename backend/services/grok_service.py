import os
import httpx
from typing import List, AsyncGenerator
import json
from models.chat_models import Message

class GrokService:
    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        self.base_url = "https://api.x.ai/v1"
        self.default_model = "grok-beta"
        
    async def stream_chat(self, messages: List[Message], model: str = None) -> AsyncGenerator[str, None]:
        """Stream chat responses from Grok"""
        try:
            # Convert messages to Grok format
            grok_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ]
            
            # Add system message if not present
            if not any(msg["role"] == "system" for msg in grok_messages):
                system_msg = {
                    "role": "system",
                    "content": "You are Digi Setu AI powered by Grok, an educational content transformation assistant. You help transform static content into interactive learning experiences with wit and intelligence. Be helpful, educational, and engaging."
                }
                grok_messages.insert(0, system_msg)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": grok_messages,
                "model": model or self.default_model,
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST", 
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            if data.strip() == "[DONE]":
                                break
                            try:
                                chunk_data = json.loads(data)
                                if chunk_data.get("choices") and len(chunk_data["choices"]) > 0:
                                    delta = chunk_data["choices"][0].get("delta", {})
                                    if "content" in delta and delta["content"]:
                                        content = delta["content"]
                                        yield f"data: {json.dumps({'content': content, 'provider': 'grok'})}\n\n"
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            error_msg = f"Grok Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    def get_available_models(self) -> List[str]:
        """Get list of available Grok models"""
        return ["grok-beta", "grok-1"]
