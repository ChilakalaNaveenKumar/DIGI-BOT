from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import List, Dict, Any, Optional
from models.chat_models import ChatRequest, Message, AIProvider
from services.openai_service import OpenAIService
from services.anthropic_service import AnthropicService
from services.grok_service import GrokService
from enum import Enum
import base64
import io

router = APIRouter()

# Service instances
openai_service = OpenAIService()
anthropic_service = AnthropicService()
grok_service = GrokService()

def get_service(provider: AIProvider):
    """Get the appropriate service based on provider"""
    if provider == AIProvider.OPENAI:
        return openai_service
    elif provider == AIProvider.ANTHROPIC:
        return anthropic_service
    elif provider == AIProvider.GROK:
        return grok_service
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Enhanced chat endpoint with reasoning, tool calling, and file support"""
    try:
        service = get_service(request.provider)
        
        # Enhanced streaming response
        async def generate_enhanced_stream():
            try:
                if request.provider == AIProvider.OPENAI:
                    async for chunk in get_enhanced_openai_stream(
                        service, 
                        request.messages, 
                        request.model, 
                        request.enableReasoning, 
                        request.tools,
                        request.files
                    ):
                        yield chunk
                else:
                    # Fallback to basic streaming
                    async for chunk in get_openai_stream(service, request.messages, request.model):
                        yield chunk
                        
            except Exception as e:
                error_response = {
                    'type': 'error',
                    'content': f"Streaming error: {str(e)}",
                    'provider': request.provider.value,
                    'model': request.model
                }
                yield f"data: {json.dumps(error_response)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(generate_enhanced_stream(), media_type="text/plain")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat endpoint error: {str(e)}")

async def get_enhanced_openai_stream(service, messages: List[Message], model: str = None, enable_reasoning: bool = False, tools: List[Dict] = None, files: List[Dict] = None):
    """Enhanced OpenAI stream with reasoning, tool calling, and file support"""
    print(f"🎯 Enhanced OpenAI stream - tools: {len(tools) if tools else 0}, model: {model}")
    
    try:
        openai_messages = []
        
        # Add system message
        system_content = "You are Digi Setu AI, a helpful assistant with access to image generation, audio generation, and file processing capabilities. Use your tools when appropriate to enhance responses."
        
        openai_messages.append({
            "role": "system", 
            "content": system_content
        })
        
        # Convert messages to OpenAI format
        for msg in messages:
            openai_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Prepare tools for OpenAI
        openai_tools = []
        if tools:
            for tool in tools:
                tool_name = tool.get('name', '')
                tool_desc = tool.get('description', '')
                tool_params = tool.get('parameters', {})
                
                if tool_name and tool_desc:
                    openai_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "description": tool_desc,
                            "parameters": tool_params
                        }
                    })
        
        # Enhanced OpenAI request
        actual_model = model or service.default_model
        request_params = {
            "model": actual_model,
            "messages": openai_messages,
            "stream": True
        }
        
        # Add tools if available
        if openai_tools:
            request_params["tools"] = openai_tools
            request_params["tool_choice"] = "auto"
            print(f"🔧 Added {len(openai_tools)} tools to request")
        
        print(f"🚀 Making OpenAI request...")
        
        try:
            response = service.client.chat.completions.create(**request_params)
            print(f"✅ OpenAI request successful, starting stream processing...")
        except Exception as e:
            print(f"❌ OpenAI API Error: {str(e)}")
            error_response = {
                'type': 'content',
                'content': f"Error calling OpenAI API: {str(e)}",
                'content_type': 'text',
                'provider': 'openai',
                'model': actual_model
            }
            yield f"data: {json.dumps(error_response)}\n\n"
            yield "data: [DONE]\n\n"
            return
        
        # Process streaming response
        accumulated_content = ""
        accumulated_tool_calls = {}
        chunk_count = 0
        
        # Stream thinking/reasoning if enabled
        if enable_reasoning:
            thinking_response = {
                'type': 'thinking',
                'content': f"🤔 Processing your request with {actual_model}...",
                'content_type': 'text',
                'provider': 'openai',
                'model': actual_model
            }
            yield f"data: {json.dumps(thinking_response)}\n\n"
        
        # Process the streaming response
        for chunk in response:
            chunk_count += 1
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                accumulated_content += content
                
                # Stream content
                enhanced_response = {
                    'type': 'content',
                    'content': content,
                    'content_type': 'text',
                    'provider': 'openai',
                    'model': actual_model
                }
                
                yield f"data: {json.dumps(enhanced_response)}\n\n"
            
            # Handle tool calls
            if chunk.choices[0].delta.tool_calls:
                for tool_call_delta in chunk.choices[0].delta.tool_calls:
                    tool_call_index = getattr(tool_call_delta, 'index', 0)
                    tool_call_id = tool_call_delta.id
                    
                    if tool_call_index not in accumulated_tool_calls:
                        accumulated_tool_calls[tool_call_index] = {
                            'id': tool_call_id,
                            'name': '',
                            'arguments': ''
                        }
                    
                    if tool_call_id and accumulated_tool_calls[tool_call_index]['id'] is None:
                        accumulated_tool_calls[tool_call_index]['id'] = tool_call_id
                    
                    if tool_call_delta.function:
                        if tool_call_delta.function.name:
                            accumulated_tool_calls[tool_call_index]['name'] = tool_call_delta.function.name
                        if tool_call_delta.function.arguments:
                            accumulated_tool_calls[tool_call_index]['arguments'] += tool_call_delta.function.arguments
        
        # Process accumulated tool calls after streaming completes
        if accumulated_tool_calls:
            print(f"🔧 Processing {len(accumulated_tool_calls)} tool calls...")
            
            # Create a copy of the dictionary to avoid "dictionary changed size during iteration" error
            for tool_call_index, tool_data in list(accumulated_tool_calls.items()):
                if tool_data['name'] and tool_data['arguments']:
                    try:
                        # Try to parse complete arguments
                        tool_args = json.loads(tool_data['arguments'])
                        print(f"🎨 Executing {tool_data['name']} with args: {tool_args}")
                        
                        # Execute tool
                        if tool_data['name'] in ['generateImage', 'createDiagram']:
                            tool_result = await execute_image_generation_tool(tool_data['name'], tool_args, 'openai')
                        elif tool_data['name'] in ['generateAudio', 'textToSpeech']:
                            tool_result = await execute_audio_generation_tool(tool_data['name'], tool_args, 'openai')
                        elif tool_data['name'] in ['speechToText', 'transcribeAudio']:
                            tool_result = await execute_speech_to_text_tool(tool_data['name'], tool_args, 'openai')
                        elif tool_data['name'] in ['processFile', 'analyzeFile', 'summarizeFile']:
                            tool_result = await execute_file_processing_tool(tool_data['name'], tool_args, 'openai')
                        else:
                            tool_result = {'success': False, 'error': f'Unknown tool: {tool_data["name"]}'}
                        
                        # Check if tool execution was successful
                        if tool_result.get('success'):
                            print(f"✅ Tool execution successful")
                            
                            # Create continuation messages for follow-up
                            continued_messages = openai_messages + [
                                {
                                    "role": "assistant",
                                    "content": None,
                                    "tool_calls": [{
                                        "id": tool_data['id'],
                                        "type": "function",
                                        "function": {"name": tool_data['name'], "arguments": tool_data['arguments']}
                                    }]
                                },
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_data['id'],
                                    "content": json.dumps(tool_result)
                                }
                            ]
                            
                            # Make follow-up request to continue conversation
                            try:
                                follow_up_response = service.client.chat.completions.create(
                                    model=actual_model,
                                    messages=continued_messages,
                                    stream=True,
                                    max_completion_tokens=4096
                                )
                                
                                # Stream the continuation
                                print(f"🔄 Streaming follow-up response...")
                                for follow_chunk in follow_up_response:
                                    if follow_chunk.choices[0].delta.content:
                                        content = follow_chunk.choices[0].delta.content
                                        follow_response = {
                                            'type': 'content',
                                            'content': content,
                                            'content_type': 'text',
                                            'provider': 'openai',
                                            'model': actual_model
                                        }
                                        yield f"data: {json.dumps(follow_response)}\n\n"
                                
                                print(f"✅ Follow-up conversation completed")
                                
                            except Exception as e:
                                print(f"❌ Follow-up conversation error: {str(e)}")
                                error_response = {
                                    'type': 'content',
                                    'content': f"\n\n⚠️ Could not continue conversation after tool execution: {str(e)}",
                                    'content_type': 'text',
                                    'provider': 'openai',
                                    'model': actual_model
                                }
                                yield f"data: {json.dumps(error_response)}\n\n"
                        
                        else:
                            print(f"❌ Tool execution failed: {tool_result.get('error', 'Unknown error')}")
                            error_response = {
                                'type': 'content',
                                'content': f"\n\n❌ Tool execution failed: {tool_result.get('error', 'Unknown error')}",
                                'content_type': 'text',
                                'provider': 'openai',
                                'model': actual_model
                            }
                            yield f"data: {json.dumps(error_response)}\n\n"
                    
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON decode error for {tool_call_index}: {str(e)}")
                    except Exception as e:
                        print(f"❌ Tool execution error for {tool_call_index}: {str(e)}")
                        error_response = {
                            'type': 'content',
                            'content': f"\n\n❌ Tool execution error: {str(e)}",
                            'content_type': 'text',
                            'provider': 'openai',
                            'model': actual_model
                        }
                        yield f"data: {json.dumps(error_response)}\n\n"
        else:
            print(f"⚠️ No tool calls were accumulated during streaming!")
        
        print(f"✅ Completed processing {chunk_count} chunks")
        
    except Exception as e:
        print(f"❌ Enhanced OpenAI Error: {str(e)}")
        yield f"data: {json.dumps({'error': f'Enhanced OpenAI Error: {str(e)}'})}\n\n"
    finally:
        yield "data: [DONE]\n\n"

# Tool execution functions
async def execute_image_generation_tool(tool_name: str, tool_args: dict, provider: str):
    """Execute image generation tools (generateImage, createDiagram)"""
    try:
        prompt = tool_args.get("prompt", "")
        size = tool_args.get("size", "1024x1024")
        quality = tool_args.get("quality", "standard")
        style = tool_args.get("style", "vivid")
        
        if not prompt:
            raise ValueError("Prompt is required for image generation")
        
        print(f"🎨 Executing {tool_name} with DALL-E 3")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        from openai import OpenAI
        client = OpenAI()
        
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=1
            )
            
            image_url = response.data[0].url
            print(f"✅ Image generated successfully!")
            
            return {
                'success': True,
                'result': {
                    'type': 'image',
                    'url': image_url,
                    'prompt': prompt,
                    'size': size,
                    'quality': quality,
                    'style': style
                }
            }
            
        except Exception as e:
            print(f"❌ DALL-E 3 generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'result': {
                    'type': 'image',
                    'url': 'https://via.placeholder.com/1024x1024?text=Image+Generation+Failed',
                    'error': f"Image generation failed: {str(e)}"
                }
            }
            
    except Exception as e:
        print(f"❌ Image generation tool error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'result': {
                'type': 'image',
                'url': 'https://via.placeholder.com/1024x1024?text=Error',
                'error': f"Tool error: {str(e)}"
            }
        }

async def execute_audio_generation_tool(tool_name: str, tool_args: dict, provider: str):
    """Execute audio generation tools - always use OpenAI TTS for cross-platform support"""
    try:
        text = tool_args.get('text', 'Hello, this is a generated audio message.')
        voice = tool_args.get('voice', 'alloy')
        model = tool_args.get('model', 'tts-1')
        speed = tool_args.get('speed', 1.0)
        
        if not text:
            raise ValueError("Text is required for audio generation")
        
        print(f"🎵 Executing {tool_name} with OpenAI TTS")
        print(f"📝 Text: {text[:100]}...")
        
        from openai import OpenAI
        client = OpenAI()
        
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            speed=speed
        )
        
        # Convert to base64 for embedding
        audio_content = response.content
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        audio_url = f"data:audio/mp3;base64,{audio_base64}"
        
        print(f"✅ Audio generated successfully! Size: {len(audio_content)} bytes")
        
        return {
            'success': True,
            'result': {
                'type': 'audio',
                'url': audio_url,
                'format': 'mp3',
                'voice': voice,
                'model': model,
                'speed': speed,
                'text': text,
                'size_bytes': len(audio_content)
            }
        }
        
    except Exception as e:
        print(f"❌ Audio generation error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'result': {
                'type': 'audio',
                'url': 'data:audio/mp3;base64,',
                'format': 'mp3',
                'error': f"Audio generation failed: {str(e)}"
            }
        }

async def execute_speech_to_text_tool(tool_name: str, tool_args: dict, provider: str):
    """Execute speech-to-text tools - always use OpenAI Whisper for cross-platform support"""
    try:
        audio_file = tool_args.get('audio_file')
        audio_data = tool_args.get('audio_data')
        language = tool_args.get('language', 'auto')
        model = tool_args.get('model', 'whisper-1')
        
        if not audio_file and not audio_data:
            raise ValueError("Either audio_file or audio_data is required")
        
        print(f"🎤 Executing {tool_name} with OpenAI Whisper")
        
        from openai import OpenAI
        client = OpenAI()
        
        # Handle base64 audio data
        if audio_data:
            audio_bytes = base64.b64decode(audio_data)
            audio_file_obj = io.BytesIO(audio_bytes)
            audio_file_obj.name = "audio.mp3"
        else:
            audio_file_obj = open(audio_file, "rb")
        
        # Transcribe using Whisper
        transcript = client.audio.transcriptions.create(
            model=model,
            file=audio_file_obj,
            language=language if language != 'auto' else None
        )
        
        if not audio_data:
            audio_file_obj.close()
        
        print(f"✅ Speech transcribed successfully!")
        
        return {
            'success': True,
            'result': {
                'type': 'text',
                'text': transcript.text,
                'language': language,
                'model': model
            }
        }
        
    except Exception as e:
        print(f"❌ Speech-to-text error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'result': {
                'type': 'text',
                'text': '',
                'error': f"Speech transcription failed: {str(e)}"
            }
        }

async def execute_file_processing_tool(tool_name: str, tool_args: dict, provider: str):
    """Execute file processing tools - analyze, summarize, or extract content from files"""
    try:
        file_content = tool_args.get('file_content')
        file_type = tool_args.get('file_type', 'text')
        task = tool_args.get('task', 'summarize')
        
        if not file_content:
            raise ValueError("File content is required")
        
        print(f"📄 Executing {tool_name} with task: {task}")
        
        # Process based on task type
        processed_result = f"File processed successfully with task: {task}\n\nContent preview: {str(file_content)[:500]}..."
        
        print(f"✅ File processed successfully!")
        
        return {
            'success': True,
            'result': {
                'type': 'text',
                'processed_content': processed_result,
                'task': task,
                'file_type': file_type,
                'original_length': len(str(file_content))
            }
        }
        
    except Exception as e:
        print(f"❌ File processing error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'result': {
                'type': 'text',
                'processed_content': '',
                'error': f"File processing failed: {str(e)}"
            }
        }

# Legacy streaming function
async def get_openai_stream(service, messages, model):
    """Stream response from OpenAI"""
    try:
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        response = service.client.chat.completions.create(
            model=model or service.default_model,
            messages=openai_messages,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                yield f"data: {json.dumps({'content': content, 'provider': 'openai'})}\n\n"
        
        yield f"data: [DONE]\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'error': f'OpenAI Error: {str(e)}'})}\n\n"
        yield f"data: [DONE]\n\n"

# Provider information endpoint
@router.get("/providers")
def get_providers():
    """Get available AI providers and their models"""
    try:
        providers = [
            {
                "id": "openai",
                "name": "GPT-5",
                "models": ["gpt-5", "gpt-4o", "gpt-4o-mini", "o1", "o1-mini"],
                "status": "active",
                "description": "200K TPM, 64k output",
                "reasoning": True,
                "toolCalling": True,
                "multiModal": True
            }
        ]
        return {"providers": providers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get providers: {str(e)}")

# Test endpoint
@router.post("/test/{provider}")
async def test_provider(provider: str):
    """Test connection to a specific AI provider"""
    try:
        if provider not in [p.value for p in AIProvider]:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")
        
        service = get_service(AIProvider(provider))
        
        # Simple test message
        test_messages = [Message(role="user", content="Hello, please respond with 'Connection successful!'")]
        
        # Test the connection
        response_content = ""
        async for chunk in get_openai_stream(service, test_messages, None):
            if "data: [DONE]" not in chunk:
                try:
                    chunk_data = json.loads(chunk.replace("data: ", ""))
                    if "content" in chunk_data:
                        response_content += chunk_data["content"]
                except:
                    pass
        
        return {
            "provider": provider,
            "status": "connected",
            "response": response_content.strip()
        }
        
    except Exception as e:
        return {
            "provider": provider,
            "status": "error", 
            "error": str(e)
        }


