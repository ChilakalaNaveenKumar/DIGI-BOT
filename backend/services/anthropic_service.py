import os
from anthropic import Anthropic
from typing import List, AsyncGenerator
import json
from models.chat_models import Message

class AnthropicService:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # Use latest available Claude model with maximum capabilities
        self.default_model = "claude-sonnet-4-20250514"  # Latest Claude 4 Sonnet with 64K output
        # Model mapping: custom name -> actual API model
        self.model_mapping = {
            "claude-4-opus": "claude-opus-4-1-20250805",     # Latest Claude 4 Opus (32K output)
            "claude-4-sonnet": "claude-sonnet-4-20250514",   # Latest Claude 4 Sonnet (64K output)
            "claude-3-7-sonnet": "claude-3-7-sonnet-20250219", # Claude 3.7 Sonnet (64K output)
            "claude-3-5-sonnet-20241022": "claude-3-5-sonnet-20241022", # Old model (8K output)
            "claude-3-5-haiku-20241022": "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229": "claude-3-opus-20240229"
        }
        
    async def stream_chat(self, messages: List[Message], model: str = None) -> AsyncGenerator[str, None]:
        """Stream chat responses from Anthropic Claude"""
        try:
            # Convert messages to Anthropic format with multimodal support
            # Enhanced system message for multimodal capabilities
            system_message = """You are Digi Setu AI. You MUST create rich visual content like ChatGPT/Claude.

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
            
            anthropic_messages = []
            for msg in messages:
                if msg.role != "system":  # Skip system messages in the message list
                    anthropic_messages.append({
                        "role": msg.role, 
                        "content": msg.content
                    })
                else:
                    system_message = msg.content  # Use custom system message if provided
            
            # Create streaming response with maximum Claude 4 tokens
            # Map custom model name to actual API model
            actual_model = self.model_mapping.get(model or self.default_model, "claude-3-5-sonnet-20241022")
            
            with self.client.messages.stream(
                model=actual_model,
                max_tokens=200000,  # Claude 3.5 maximum output tokens
                system=system_message,
                messages=anthropic_messages
                            ) as stream:
                    for text in stream.text_stream:
                        if text:
                            yield f"data: {json.dumps({'content': text, 'provider': 'anthropic'})}\n\n"
                    
                    # Send completion marker
                    yield f"data: [DONE]\n\n"
                        
        except Exception as e:
            error_msg = f"Anthropic Error: {str(e)}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
    
    def get_available_models(self) -> List[str]:
        """Get list of latest Anthropic models with maximum capabilities"""
        return [
            "claude-opus-4-1-20250805",    # Latest Claude 4 Opus (32K output) 🔥
            "claude-sonnet-4-20250514",    # Latest Claude 4 Sonnet (64K output) 🔥🔥
            "claude-3-7-sonnet-20250219",  # Claude 3.7 Sonnet (64K output) 🔥🔥
            "claude-3-5-sonnet-20241022",  # Claude 3.5 Sonnet (8K output)
            "claude-3-5-haiku-20241022",   # Claude 3.5 Haiku (8K output)
            "claude-3-opus-20240229",      # Claude 3 Opus (4K output)
            "claude-3-sonnet-20240229",    # Claude 3 Sonnet (4K output)
            "claude-3-haiku-20240307"      # Claude 3 Haiku (4K output)
        ]
