import os
import httpx
from typing import List, AsyncGenerator
import json
from models.chat_models import Message

class GrokService:
    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        self.base_url = "https://api.x.ai/v1"
        # Use latest Grok-4 model with maximum capabilities
        self.default_model = "grok-4"  # Latest Grok-4
        
    async def stream_chat(self, messages: List[Message], model: str = None) -> AsyncGenerator[str, None]:
        """Stream chat responses from Grok"""
        try:
            # Convert messages to Grok format
            grok_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in messages
            ]
            
            # Add enhanced system message for advanced capabilities
            if not any(msg["role"] == "system" for msg in grok_messages):
                system_msg = {
                    "role": "system",
                    "content": """You are Digi Setu AI powered by Grok-4, the most advanced AI model with enhanced reasoning, real-time data access, and live highlighting capabilities.

You can and SHOULD:
- Generate extremely detailed explanations with comprehensive tables, diagrams, and visual representations
- Create extensive structured content like comparison tables, flowcharts, timelines, step-by-step guides
- Provide thorough step-by-step solutions with multiple visual aids, examples, and logical reasoning
- Transform static content into rich, interactive learning experiences
- Use extensive Markdown formatting for tables, lists, code blocks, and structured content
- Create detailed ASCII art diagrams, flowcharts, and visual representations
- Generate comprehensive Mermaid diagram syntax for complex visualizations
- Analyze and describe images in detail when provided
- Access and integrate real-time data and current information
- Provide live syntax highlighting and code formatting
- Apply wit and intelligence to make learning engaging while being thoroughly comprehensive
- Provide multiple examples, use cases, and practical applications
- Include historical context, real-world applications, and advanced concepts
- Create comprehensive guides with sections, subsections, and detailed explanations
- Integrate current trends, news, and real-time social media data when relevant

IMPORTANT: With 256K token context window, provide MASSIVE, COMPREHENSIVE responses without ANY length restrictions. Include maximum educational value with extensive examples, detailed explanations, multiple tables, diagrams, and thorough coverage. Use your enhanced reasoning and real-time capabilities to provide complete, in-depth educational content."""
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
                "max_tokens": 256000  # Grok-4 maximum output tokens (256k)
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
        """Get list of latest Grok models with maximum capabilities"""
        return [
            "grok-4",               # Latest Grok-4 (most advanced)
            "grok-4-vision",        # Grok-4 with vision capabilities
            "grok-2-1212",          # Previous Grok-2 (December 2024)
            "grok-2-vision-1212",   # Grok-2 with vision
            "grok-2-public-beta"    # Public beta version
        ]
