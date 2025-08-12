import os
from openai import OpenAI
from typing import List, AsyncGenerator
import json
from models.chat_models import Message

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.default_model = "gpt-4"
        
    async def stream_chat(self, messages: List[Message], model: str = None) -> AsyncGenerator[str, None]:
        """Stream chat responses from OpenAI"""
        try:
            # Convert messages to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ]
            
            # Add system message if not present
            if not any(msg["role"] == "system" for msg in openai_messages):
                system_msg = {
                    "role": "system",
                    "content": "You are Digi Setu AI, an educational content transformation assistant. You help transform static content into interactive learning experiences. Be helpful, educational, and engaging."
                }
                openai_messages.insert(0, system_msg)
            
            # Create streaming response
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=openai_messages,
                stream=True,
                temperature=0.7,
                max_tokens=500
            )
            
            # Stream the response
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content, 'provider': 'openai'})}\n\n"
                    
        except Exception as e:
            error_msg = f"OpenAI Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        return ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
