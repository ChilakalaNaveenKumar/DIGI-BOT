from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import json
from models.chat_models import ChatRequest, ProvidersResponse, ProviderInfo, AIProvider
from services.openai_service import OpenAIService
from services.grok_service import GrokService
from services.anthropic_service import AnthropicService

router = APIRouter()

# Initialize services lazily
services = {}

def get_service(provider: AIProvider):
    """Get or create service instance"""
    if provider not in services:
        if provider == AIProvider.OPENAI:
            services[provider] = OpenAIService()
        elif provider == AIProvider.GROK:
            services[provider] = GrokService()
        elif provider == AIProvider.ANTHROPIC:
            services[provider] = AnthropicService()
        else:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
    
    return services[provider]

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint with streaming support for all AI providers"""
    try:
        service = get_service(request.provider)
        
        # Return streaming response for all providers
        async def generate_stream():
            try:
                if request.provider == "openai":
                    async for chunk in get_openai_stream(service, request.messages, request.model):
                        yield chunk
                elif request.provider == "grok":
                    async for chunk in get_grok_stream(service, request.messages, request.model):
                        yield chunk
                elif request.provider == "anthropic":
                    async for chunk in get_anthropic_stream(service, request.messages, request.model):
                        yield chunk
                else:
                    yield f"data: {json.dumps({'error': 'Provider not implemented'})}\n\n"
                    
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': f'Stream error: {str(e)}'})}\n\n"
                yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

async def get_openai_stream(service, messages, model):
    """Stream response from OpenAI"""
    try:
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        # Add system message if not present
        if not any(msg["role"] == "system" for msg in openai_messages):
            system_msg = {
                "role": "system",
                "content": "You are Digi Setu AI, an educational content transformation assistant. You help transform static content into interactive learning experiences. Be helpful, educational, and engaging."
            }
            openai_messages.insert(0, system_msg)

        response = service.client.chat.completions.create(
            model=model or service.default_model,
            messages=openai_messages,
            temperature=0.7,
            max_tokens=500,
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'content': content, 'provider': 'openai'})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'error': f'OpenAI Error: {str(e)}'})}\n\n"

async def get_grok_stream(service, messages, model):
    """Stream response from Grok"""
    try:
        import httpx
        
        # Convert messages to Grok format
        grok_messages = [
            {"role": msg.role, "content": msg.content} 
            for msg in messages
        ]
        
        # Add system message if not present
        if not any(msg["role"] == "system" for msg in grok_messages):
            system_msg = {
                "role": "system",
                "content": "You are Digi Setu AI powered by Grok. Be helpful, educational, and engaging."
            }
            grok_messages.insert(0, system_msg)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream(
                "POST",
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {service.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model or service.default_model,
                    "messages": grok_messages,
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "stream": True
                }
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
        yield f"data: {json.dumps({'error': f'Grok Error: {str(e)}'})}\n\n"

async def get_anthropic_stream(service, messages, model):
    """Stream response from Anthropic"""
    try:
        # Use the Anthropic client directly with streaming
        system_message = "You are Digi Setu AI powered by Claude. Be helpful, educational, and engaging."
        
        anthropic_messages = []
        for msg in messages:
            if msg.role != "system":
                anthropic_messages.append({
                    "role": msg.role, 
                    "content": msg.content
                })
            else:
                system_message = msg.content
        
        # Use streaming API
        with service.client.messages.stream(
            model=model or service.default_model,
            max_tokens=500,
            temperature=0.7,
            system=system_message,
            messages=anthropic_messages
        ) as stream:
            for text in stream.text_stream:
                if text:
                    yield f"data: {json.dumps({'content': text, 'provider': 'anthropic'})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'error': f'Claude Error: {str(e)}'})}\n\n"

@router.get("/providers", response_model=ProvidersResponse)
def get_providers():
    """Get available AI providers and their models"""
    try:
        providers = [
            ProviderInfo(
                id="openai",
                name="GPT-4o (16k tokens)",
                models=["gpt-4o", "gpt-4o-2024-11-20", "gpt-4o-mini", "gpt-4-turbo", "gpt-4"],
                status="active"
            ),
            ProviderInfo(
                id="anthropic",
                name="Claude 3.5 (8k tokens)",
                models=["claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20240620", "claude-3-5-haiku-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                status="active"
            ),
            ProviderInfo(
                id="grok", 
                name="Grok-2 (32k tokens)",
                models=["grok-2-1212", "grok-2-vision-1212", "grok-2-public-beta", "grok-beta", "grok-1"],
                status="active"
            )
        ]
        
        return ProvidersResponse(providers=providers)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Providers error: {str(e)}")

@router.get("/test/{provider}")
async def test_provider(provider: str):
    """Test connection to a specific AI provider"""
    try:
        if provider not in [p.value for p in AIProvider]:
            raise HTTPException(status_code=400, detail="Invalid provider")
            
        # Simple test message
        from models.chat_models import Message, MessageRole
        test_messages = [
            Message(role=MessageRole.USER, content="Hello, can you respond with just 'OK'?")
        ]
        
        service = get_service(AIProvider(provider))
        
        # Get first response chunk to test connection
        async for chunk in service.stream_chat(test_messages):
            return {"status": "success", "provider": provider, "response": "Connected"}
            
    except Exception as e:
        return {"status": "error", "provider": provider, "error": str(e)}
