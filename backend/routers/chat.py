from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import json
from models.chat_models import (
    ChatRequest, ProvidersResponse, ProviderInfo, AIProvider,
    EnhancedMessage, FileInfo, ToolInfo, ToolCall, ToolResult, EnhancedChatResponse
)
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
    """Enhanced chat endpoint with reasoning, tool calling, and file support"""
    try:
        service = get_service(request.provider)
        
        # Enhanced streaming response with all AI SDK 5 features
        async def generate_enhanced_stream():
            try:
                # Check for enhanced features
                enable_reasoning = getattr(request, 'enableReasoning', False)
                enable_tools = getattr(request, 'enableToolCalling', False)
                files = getattr(request, 'files', [])
                tools = getattr(request, 'tools', [])
                
                print(f"🚀 Enhanced Chat Request: reasoning={enable_reasoning}, tools={enable_tools}, files={len(files)}")
                
                # Send reasoning start if enabled
                if enable_reasoning and request.provider in ['openai', 'anthropic']:
                    yield f"data: {json.dumps({'reasoning': 'Analyzing your request and determining the best approach...'})}\n\n"
                
                # Route to appropriate enhanced stream handler
                if request.provider == "openai":
                    async for chunk in get_enhanced_openai_stream(service, request.messages, request.model, enable_reasoning, tools, files):
                        yield chunk
                elif request.provider == "grok":
                    async for chunk in get_enhanced_grok_stream(service, request.messages, request.model, enable_reasoning, tools, files):
                        yield chunk
                elif request.provider == "anthropic":
                    async for chunk in get_enhanced_anthropic_stream(service, request.messages, request.model, enable_reasoning, tools, files):
                        yield chunk
                else:
                    yield f"data: {json.dumps({'error': 'Provider not implemented'})}\n\n"
                    
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                print(f"❌ Enhanced stream error: {str(e)}")
                yield f"data: {json.dumps({'error': f'Enhanced stream error: {str(e)}'})}\n\n"
                yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_enhanced_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced chat error: {str(e)}")

async def get_enhanced_openai_stream(service, messages, model, enable_reasoning=False, tools=None, files=None):
    """Enhanced OpenAI stream with reasoning, tool calling, and file support"""
    try:
        openai_messages = []
        
        # Process messages with enhanced features
        for msg in messages:
            message_content = msg.content
            
            # Add file context if present
            if hasattr(msg, 'files') and msg.files:
                file_context = "\n\nAttached files:\n"
                for file_info in msg.files:
                    file_context += f"- {file_info.get('filename', 'Unknown')} ({file_info.get('mediaType', 'unknown')})\n"
                message_content += file_context
            
            openai_messages.append({
                "role": msg.role, 
                "content": message_content
            })

        # Enhanced system message
        system_content = """You are Digi Setu AI, an advanced educational content transformation assistant powered by AI SDK 5. 

Key capabilities:
- Transform static content into interactive learning experiences
- Create tables, quizzes, flashcards, and charts using tool calling
- Process multiple file formats (PDFs, images, documents)
- Show reasoning process when requested
- Provide detailed, educational responses

When users request interactive content, use the appropriate tools. Always be helpful, educational, and engaging."""

        if enable_reasoning:
            system_content += "\n\nIMPORTANT: When reasoning is enabled, think through your response step by step before providing the final answer. Show your thought process clearly."

        # Add system message
        if not any(msg["role"] == "system" for msg in openai_messages):
            openai_messages.insert(0, {"role": "system", "content": system_content})

        # Prepare tools for OpenAI
        openai_tools = []
        if tools:
            for tool in tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.get("name", "unknown_tool"),
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {})
                    }
                })

        # Enhanced OpenAI request
        request_params = {
            "model": model or service.default_model,
            "messages": openai_messages,
            "max_completion_tokens": 64000,
            "stream": True
        }
        
        # Add tools if available
        if openai_tools:
            request_params["tools"] = openai_tools
            request_params["tool_choice"] = "auto"

        # Enable reasoning for O1 models
        if enable_reasoning and (model and 'o1' in model.lower()):
            request_params["reasoning"] = True

        response = service.client.chat.completions.create(**request_params)

        # Process enhanced streaming response
        for chunk in response:
            delta = chunk.choices[0].delta
            
            # Handle reasoning content (O1 models)
            if hasattr(delta, 'reasoning') and delta.reasoning:
                yield f"data: {json.dumps({'reasoning': delta.reasoning, 'provider': 'openai'})}\n\n"
            
            # Handle regular content
            if delta.content is not None:
                yield f"data: {json.dumps({'content': delta.content, 'provider': 'openai'})}\n\n"
            
            # Handle tool calls
            if hasattr(delta, 'tool_calls') and delta.tool_calls:
                for tool_call in delta.tool_calls:
                    tool_data = {
                        'tool_call': {
                            'id': tool_call.id,
                            'name': tool_call.function.name if tool_call.function else 'unknown',
                            'arguments': tool_call.function.arguments if tool_call.function else '{}'
                        }, 
                        'provider': 'openai'
                    }
                    yield f"data: {json.dumps(tool_data)}\n\n"
        
    except Exception as e:
        print(f"❌ Enhanced OpenAI Error: {str(e)}")
        yield f"data: {json.dumps({'error': f'Enhanced OpenAI Error: {str(e)}'})}\n\n"

async def get_openai_stream(service, messages, model):
    """Stream response from OpenAI"""
    try:
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        # No custom system prompts - send user input directly

        response = service.client.chat.completions.create(
            model=model or service.default_model,
            messages=openai_messages,
            max_completion_tokens=64000,  # GPT-4o max output tokens
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
        
        # No custom system prompts - send user input directly
        
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
                    "max_tokens": 256000,  # Grok-4 max output tokens (256k)
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

async def get_enhanced_anthropic_stream(service, messages, model, enable_reasoning=False, tools=None, files=None):
    """Enhanced Anthropic stream with reasoning and tool calling support"""
    try:
        # No custom system prompts - send user input directly
        system_message = ""
        
        anthropic_messages = []
        for msg in messages:
            if msg.role != "system":
                message_content = msg.content
                
                # Add file context if present
                if hasattr(msg, 'files') and msg.files:
                    file_context = "\n\nAttached files:\n"
                    for file_info in msg.files:
                        file_context += f"- {file_info.get('filename', 'Unknown')} ({file_info.get('mediaType', 'unknown')})\n"
                    message_content += file_context
                
                anthropic_messages.append({
                    "role": msg.role, 
                    "content": message_content
                })
            else:
                system_message = msg.content

        # Prepare tools for Anthropic
        anthropic_tools = []
        if tools:
            for tool in tools:
                anthropic_tools.append({
                    "name": tool.get("name", "unknown_tool"),
                    "description": tool.get("description", ""),
                    "input_schema": tool.get("parameters", {})
                })

        # Enhanced request parameters
        request_params = {
            "model": model or service.default_model,
            "max_tokens": 200000,
            "system": system_message,
            "messages": anthropic_messages
        }
        
        # Add tools if available
        if anthropic_tools:
            request_params["tools"] = anthropic_tools

        # Send reasoning start
        if enable_reasoning:
            yield f"data: {json.dumps({'reasoning': 'Let me think through this step by step...', 'provider': 'anthropic'})}\n\n"

        # Use enhanced streaming API
        with service.client.messages.stream(**request_params) as stream:
            for text in stream.text_stream:
                if text:
                    # Detect reasoning patterns in Claude's response
                    if enable_reasoning and any(phrase in text.lower() for phrase in ['let me think', 'first,', 'step 1', 'reasoning:', 'analysis:']):
                        yield f"data: {json.dumps({'reasoning': text, 'provider': 'anthropic'})}\n\n"
                    else:
                        yield f"data: {json.dumps({'content': text, 'provider': 'anthropic'})}\n\n"
        
    except Exception as e:
        print(f"❌ Enhanced Anthropic Error: {str(e)}")
        yield f"data: {json.dumps({'error': f'Enhanced Claude Error: {str(e)}'})}\n\n"

async def get_enhanced_grok_stream(service, messages, model, enable_reasoning=False, tools=None, files=None):
    """Enhanced Grok stream with reasoning support"""
    try:
        import httpx
        
        # Process messages with enhanced features
        grok_messages = []
        for msg in messages:
            message_content = msg.content
            
            # Add file context if present
            if hasattr(msg, 'files') and msg.files:
                file_context = "\n\nAttached files:\n"
                for file_info in msg.files:
                    file_context += f"- {file_info.get('filename', 'Unknown')} ({file_info.get('mediaType', 'unknown')})\n"
                message_content += file_context
            
            grok_messages.append({
                "role": msg.role, 
                "content": message_content
            })
        
        # Enhanced system message for Grok
        system_content = """You are Digi Setu AI powered by Grok, an advanced educational content transformation assistant.

Key capabilities:
- Transform static content into interactive learning experiences
- Create detailed educational responses with examples
- Process and analyze various content types
- Provide engaging, witty, and informative responses
- Show reasoning process when requested

Always be helpful, educational, and engaging with a touch of Grok's characteristic wit."""

        if enable_reasoning:
            system_content += "\n\nIMPORTANT: When reasoning is enabled, think through your response step by step. Show your thought process clearly."

        # Add system message
        if not any(msg["role"] == "system" for msg in grok_messages):
            grok_messages.insert(0, {"role": "system", "content": system_content})

        # Send reasoning start
        if enable_reasoning:
            yield f"data: {json.dumps({'reasoning': 'Analyzing with Grok intelligence...', 'provider': 'grok'})}\n\n"
        
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
                    "max_tokens": 256000,
                    "stream": True
                }
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data.strip() == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(data)
                            if chunk_data.get("choices") and len(chunk_data["choices"]) > 0:
                                delta = chunk_data["choices"][0].get("delta", {})
                                if "content" in delta and delta["content"]:
                                    content = delta["content"]
                                    
                                    # Detect reasoning patterns in Grok's response
                                    if enable_reasoning and any(phrase in content.lower() for phrase in ['let me think', 'reasoning:', 'step by step', 'analysis:']):
                                        yield f"data: {json.dumps({'reasoning': content, 'provider': 'grok'})}\n\n"
                                    else:
                                        yield f"data: {json.dumps({'content': content, 'provider': 'grok'})}\n\n"
                        except json.JSONDecodeError:
                            continue
        
    except Exception as e:
        print(f"❌ Enhanced Grok Error: {str(e)}")
        yield f"data: {json.dumps({'error': f'Enhanced Grok Error: {str(e)}'})}\n\n"

async def get_anthropic_stream(service, messages, model):
    """Stream response from Anthropic"""
    try:
                # No custom system prompts - send user input directly
        system_message = ""
        
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
            max_tokens=200000,  # Claude 3.5 max output tokens
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
                name="GPT-5",
                models=["gpt-5", "gpt-4o", "gpt-4o-mini", "o1", "o1-mini"],
                status="active",
                description="1M context, 64k output",
                reasoning=True,
                toolCalling=True,
                multiModal=True
            ),
            ProviderInfo(
                id="anthropic",
                name="Claude 4 Opus",
                models=["claude-opus-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
                status="active",
                description="1M context, 200k output",
                reasoning=True,
                toolCalling=True,
                multiModal=True
            ),
            ProviderInfo(
                id="grok", 
                name="Grok-4",
                models=["grok-4", "grok-4-vision", "grok-2-1212"],
                status="active",
                description="256k context, 256k output",
                reasoning=True,
                toolCalling=False,
                multiModal=True
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
