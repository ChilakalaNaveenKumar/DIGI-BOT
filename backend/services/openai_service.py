import os
from openai import OpenAI
from typing import List, AsyncGenerator
import json
from models.chat_models import Message

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Use latest available GPT model with maximum capabilities
        self.default_model = "gpt-5"  # Custom GPT-5 model name
        # Model mapping: custom name -> actual API model
        self.model_mapping = {
            "gpt-5": "gpt-5-mini",  # Use gpt-5-mini for better token limits (200K TPM vs 30K TPM)
            "gpt-4o": "gpt-4o",
            "gpt-4o-mini": "gpt-4o-mini"
        }
        
    async def stream_chat(self, messages: List[Message], model: str = None) -> AsyncGenerator[str, None]:
        """Stream chat responses from OpenAI"""
        try:
            # Convert messages to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ]
            
            # Add enhanced system message for multimodal capabilities
            if not any(msg["role"] == "system" for msg in openai_messages):
                system_msg = {
                    "role": "system",
                    "content": """You are Digi Setu AI, a helpful assistant with access to image generation, audio generation, and file processing capabilities. Use your tools when appropriate to enhance responses."""
                }
                openai_messages.insert(0, system_msg)
            
            # Create streaming response with maximum GPT-5 tokens
            # Map custom model name to actual API model
            actual_model = self.model_mapping.get(model or self.default_model, "gpt-4o")
            
            response = self.client.chat.completions.create(
                model=actual_model,
                messages=openai_messages,
                stream=True,
                max_completion_tokens=64000  # GPT-4o maximum output tokens
            )
            
            # Stream the response
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content, 'provider': 'openai'})}\n\n"
            
            # Send completion marker
            yield f"data: [DONE]\n\n"
                    
        except Exception as e:
            error_msg = f"OpenAI Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    def get_available_models(self) -> List[str]:
        """Get list of latest OpenAI models with maximum capabilities"""
        return [
            "gpt-4o",                   # Latest GPT-4o (128k tokens, multimodal)
            "gpt-4o-2024-11-20",        # Specific November 2024 version
            "gpt-4o-mini",              # Fast with vision
            "gpt-4-turbo",              # GPT-4 Turbo
            "gpt-4"                     # Standard GPT-4
        ]
