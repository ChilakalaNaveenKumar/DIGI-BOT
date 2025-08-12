import os
from anthropic import Anthropic
from typing import List, AsyncGenerator
import json
from models.chat_models import Message

class AnthropicService:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.default_model = "claude-3-sonnet-20240229"
        
    async def stream_chat(self, messages: List[Message], model: str = None) -> AsyncGenerator[str, None]:
        """Stream chat responses from Anthropic Claude"""
        try:
            # Convert messages to Anthropic format
            # Anthropic expects system message separately
            system_message = "You are Digi Setu AI powered by Claude, an educational content transformation assistant. You help transform static content into interactive learning experiences with thoughtful analysis. Be helpful, educational, and engaging."
            
            anthropic_messages = []
            for msg in messages:
                if msg.role != "system":  # Skip system messages in the message list
                    anthropic_messages.append({
                        "role": msg.role, 
                        "content": msg.content
                    })
                else:
                    system_message = msg.content  # Use custom system message if provided
            
            # Create streaming response
            with self.client.messages.stream(
                model=model or self.default_model,
                max_tokens=500,
                temperature=0.7,
                system=system_message,
                messages=anthropic_messages
            ) as stream:
                for text in stream.text_stream:
                    if text:
                        yield f"data: {json.dumps({'content': text, 'provider': 'anthropic'})}\n\n"
                        
        except Exception as e:
            error_msg = f"Anthropic Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    def get_available_models(self) -> List[str]:
        """Get list of available Anthropic models"""
        return [
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307",
            "claude-3-opus-20240229"
        ]
