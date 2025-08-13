import os
from openai import OpenAI
from typing import List, AsyncGenerator
import json
from models.chat_models import Message

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # Use latest available GPT model with maximum capabilities
        self.default_model = "gpt-4o"  # Latest GPT-4o (GPT-5 not yet available)
        
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
                    "content": """You are Digi Setu AI. You MUST create rich visual content like ChatGPT/Claude.

🔥 MANDATORY RESPONSE RULES:
1. ALWAYS create comprehensive tables for comparisons
2. ALWAYS include ASCII diagrams and flowcharts  
3. ALWAYS use visual text representations
4. NEVER give plain text - make it visual and interactive
5. ALWAYS complete full responses - never stop mid-sentence

📊 REQUIRED FORMAT FOR EVERY RESPONSE:
- Start with overview table
- Include ASCII art diagrams
- Create step-by-step visual flows
- Use emojis and symbols for visual appeal
- Build comparison matrices
- Add interactive examples

🎯 EXAMPLE FORMAT (TCP/IP):
```
# 🌐 TCP/IP Model Complete Guide

## 📋 Quick Reference Table
| Layer | Protocols | Function | Visual |
|-------|-----------|----------|--------|
| Application | HTTP, FTP | User Interface | 🖥️ Apps |
| Transport | TCP, UDP | Data Delivery | 📦 Packages |
| Internet | IP, ICMP | Routing | 🗺️ Addresses |
| Network | Ethernet | Physical | 🔌 Cables |

## 🔄 Data Flow Diagram
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Application │ ←→ │  Transport  │ ←→ │  Internet   │
│   Layer     │    │   Layer     │    │   Layer     │
└─────────────┘    └─────────────┘    └─────────────┘
       ↕                   ↕                   ↕
   HTTP/FTP            TCP/UDP              IP/ICMP
```

CRITICAL: Always provide COMPLETE responses with maximum visual content. Never stop mid-response."""
                }
                openai_messages.insert(0, system_msg)
            
            # Create streaming response with maximum GPT-5 tokens
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=openai_messages,
                stream=True,
                temperature=0.7,
                max_completion_tokens=4096  # Increased tokens for complete responses
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
