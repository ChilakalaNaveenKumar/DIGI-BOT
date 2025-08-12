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
    """Main chat endpoint supporting multiple AI providers"""
    try:
        # Get the appropriate service (lazy initialization)
        service = get_service(request.provider)
        
        # For now, return a simple non-streaming response
        if request.provider == "openai":
            response_text = await get_openai_response(service, request.messages, request.model)
        elif request.provider == "grok":
            response_text = await get_grok_response(service, request.messages, request.model)
        elif request.provider == "anthropic":
            response_text = await get_anthropic_response(service, request.messages, request.model)
        else:
            response_text = "Provider not implemented yet"
        
        return {"response": response_text, "provider": request.provider}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

async def get_openai_response(service, messages, model):
    """Get response from OpenAI"""
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
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"OpenAI Error: {str(e)}"

async def get_grok_response(service, messages, model):
    """Get response from Grok"""
    return "Grok integration coming soon! For now, try OpenAI or Claude."

async def get_anthropic_response(service, messages, model):
    """Get response from Anthropic"""
    return "Claude integration coming soon! For now, try OpenAI."

@router.get("/providers", response_model=ProvidersResponse)
def get_providers():
    """Get available AI providers and their models"""
    try:
        providers = [
            ProviderInfo(
                id="openai",
                name="GPT-4",
                models=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                status="active"
            ),
            ProviderInfo(
                id="grok", 
                name="Grok",
                models=["grok-beta", "grok-1"],
                status="active"
            ),
            ProviderInfo(
                id="anthropic",
                name="Claude",
                models=["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229"],
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
