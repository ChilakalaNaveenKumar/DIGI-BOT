from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import json
import re
from models.chat_models import (
    ChatRequest, ProvidersResponse, ProviderInfo, AIProvider,
    EnhancedMessage, FileInfo, ToolInfo, ToolCall, ToolResult, EnhancedChatResponse,
    ContentType, MultimodalContent
)
from services.openai_service import OpenAIService
from services.grok_service import GrokService
from services.anthropic_service import AnthropicService

router = APIRouter()

# Initialize services lazily
services = {}

def detect_content_type(content: str) -> ContentType:
    """Detect content type based on content patterns"""
    if not content:
        return ContentType.TEXT
    
    # Check for JSON
    if content.strip().startswith('{') or content.strip().startswith('['):
        try:
            json.loads(content.strip())
            return ContentType.JSON
        except:
            pass
    
    # Check for markdown patterns
    markdown_patterns = [
        r'^#{1,6}\s',  # Headers
        r'\|.*\|',     # Tables
        r'```',        # Code blocks
        r'\*\*.*\*\*', # Bold
        r'\*.*\*',     # Italic
        r'^\s*[-*+]\s', # Lists
        r'^\s*\d+\.\s', # Numbered lists
    ]
    
    for pattern in markdown_patterns:
        if re.search(pattern, content, re.MULTILINE):
            return ContentType.MARKDOWN
    
    # Check for table patterns
    if '|' in content and re.search(r'\|.*\|.*\|', content):
        return ContentType.TABLE
    
    # Check for diagram patterns
    diagram_patterns = [
        r'┌.*┐',  # Box drawing
        r'│.*│',  # Vertical lines
        r'└.*┘',  # Box drawing
        r'┬.*┴',  # T-junctions
        r'→|←|↑|↓', # Arrows
        r'flowchart|graph|diagram'
    ]
    
    for pattern in diagram_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return ContentType.DIAGRAM
    
    return ContentType.TEXT

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
                
                # Don't send fake reasoning - let the AI models provide real reasoning
                
                # Route to appropriate enhanced stream handler
                if request.provider == "openai":
                    print(f"🔍 Processing OpenAI request - tools: {len(tools) if tools else 0}, model: {request.model}")
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
    print(f"🎯 get_enhanced_openai_stream called - tools: {len(tools) if tools else 0}, model: {model}")
    try:
        openai_messages = []
        
        # Process messages with enhanced features
        for msg in messages:
            message_content = msg.content
            
            # Add file context if present
            if hasattr(msg, 'files') and msg.files:
                file_context = "\n\nAttached files:\n"
                for file_info in msg.files:
                    # Handle both dict and FileInfo objects
                    if isinstance(file_info, dict):
                        filename = file_info.get('filename', 'Unknown')
                        media_type = file_info.get('mediaType', 'unknown')
                    else:
                        # FileInfo object
                        filename = getattr(file_info, 'filename', 'Unknown') or 'Unknown'
                        media_type = getattr(file_info, 'mediaType', 'unknown') or 'unknown'
                    
                    file_context += f"- {filename} ({media_type})\n"
                message_content += file_context
            
            openai_messages.append({
                "role": msg.role, 
                "content": message_content
            })

        # Simple, natural system message - let AI decide when to use tools
        system_content = """You are Digi Setu AI, a helpful assistant with access to image generation capabilities.

You have access to tools that you can use when appropriate. Use your best judgment to decide when tools would be helpful for the user's request."""

        if enable_reasoning:
            system_content += "\n\nIMPORTANT: Think through your response step by step. Show your reasoning process clearly before providing the final answer."

        # Add system message
        if not any(msg["role"] == "system" for msg in openai_messages):
            openai_messages.insert(0, {"role": "system", "content": system_content})

        # Prepare tools for OpenAI
        openai_tools = []
        if tools:
            for tool in tools:
                # Handle both dict and ToolInfo objects
                if isinstance(tool, dict):
                    tool_name = tool.get("name", "unknown_tool")
                    tool_desc = tool.get("description", "")
                    tool_params = tool.get("parameters", {})
                else:
                    # ToolInfo object
                    tool_name = getattr(tool, 'name', 'unknown_tool')
                    tool_desc = getattr(tool, 'description', '') or ''
                    tool_params = getattr(tool, 'parameters', {}) or {}
                
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
        
        # Set appropriate token limits based on model (be generous with limits)
        if 'o1' in actual_model.lower():
            # O1 models have different limits and don't support max_completion_tokens
            request_params["max_tokens"] = 65536  # O1 models can handle more
        elif 'gpt-4o' in actual_model.lower():
            request_params["max_completion_tokens"] = 16384  # GPT-4o max output
        elif 'gpt-4' in actual_model.lower():
            request_params["max_completion_tokens"] = 8192   # GPT-4 max output
        else:
            request_params["max_completion_tokens"] = 4096   # Default for older models
        
        # Re-enable tools with simplified processing
        if openai_tools and 'o1' not in actual_model.lower():
            request_params["tools"] = openai_tools
            
            # Let AI decide naturally when to use tools
            request_params["tool_choice"] = "auto"
            
            # Use auto mode - let the AI decide when to use tools (forced mode was causing failures)
            print(f"🔧 Tools being sent to OpenAI: {len(openai_tools)} tools (AUTO mode)")
            
            # Log user message for debugging
            user_message = openai_messages[-1]["content"] if openai_messages else ""
            print(f"🎯 User message: '{user_message[:100]}...'")
            print(f"🎨 Tools available - AI will decide when to use them")
            
            for tool in openai_tools:
                print(f"   - {tool['function']['name']}: {tool['function']['description'][:50]}...")
            # Debug: Print the exact tool format being sent
            print(f"🔍 Tool format: {json.dumps(openai_tools[0], indent=2)}")
        else:
            print(f"⚠️ Tools disabled for debugging - tools: {len(openai_tools) if openai_tools else 0}, model: {actual_model}")

        print(f"🚀 OpenAI Request params keys: {list(request_params.keys())}")
        
        try:
            print(f"🚀 Making OpenAI request with {len(request_params)} parameters...")
            print(f"🔍 Request params: {json.dumps({k: v for k, v in request_params.items() if k != 'messages'}, indent=2)}")
            response = service.client.chat.completions.create(**request_params)
            print(f"✅ OpenAI request successful, starting stream processing...")
        except Exception as e:
            print(f"❌ OpenAI API Error: {str(e)}")
            # Return error response instead of crashing
            error_response = {
                'type': 'content',
                'content': f"Error calling OpenAI API: {str(e)}",
                'content_type': 'text',
                'provider': 'openai',
                'model': actual_model,
                'multimodal_content': [{'type': 'text', 'data': f"Error: {str(e)}", 'format': 'text'}],
                'preserve_formatting': True
            }
            yield f"data: {json.dumps(error_response)}\n\n"
            yield "data: [DONE]\n\n"
            return

        # Enhanced streaming state management
        accumulated_tool_calls = {}
        tool_prep_shown = False
        reasoning_phase = True  # Track if we're in reasoning/thinking phase
        has_content_started = False  # Track if actual response content has started

        # Process enhanced streaming response with multimodal support
        print(f"🔄 Starting to process streaming chunks...")
        chunk_count = 0
        for chunk in response:
            chunk_count += 1
            if chunk_count % 10 == 0:
                print(f"🔄 Processed {chunk_count} chunks...")
            
            delta = chunk.choices[0].delta
            
            # Handle reasoning content (O1 models)
            if hasattr(delta, 'reasoning') and delta.reasoning:
                enhanced_response = {
                    'type': 'reasoning',
                    'content': delta.reasoning,
                    'content_type': 'reasoning',
                    'provider': 'openai',
                    'model': actual_model,
                    'multimodal_content': [{
                        'type': 'reasoning',
                        'data': delta.reasoning,
                        'format': 'text'
                    }]
                }
                yield f"data: {json.dumps(enhanced_response)}\n\n"
            
            # Handle regular content with enhanced formatting detection and reasoning
            if delta.content is not None:
                content = delta.content
                
                # Enhanced reasoning detection for non-O1 models
                if not has_content_started and enable_reasoning:
                    # Check if this looks like thinking/reasoning content
                    thinking_patterns = [
                        'let me think', 'i need to', 'first, i', 'let me analyze', 
                        'thinking about', 'considering', 'i should', 'let me create',
                        'i\'ll generate', 'i\'ll create'
                    ]
                    is_reasoning = any(pattern in content.lower() for pattern in thinking_patterns)
                    
                    if is_reasoning:
                        # Stream as thinking/reasoning content
                        enhanced_response = {
                            'type': 'thinking',
                            'content': content,
                            'content_type': 'thinking',
                            'provider': 'openai',
                            'model': actual_model,
                            'multimodal_content': [{
                                'type': 'thinking',
                                'data': content,
                                'format': 'text'
                            }],
                            'preserve_formatting': True
                        }
                        yield f"data: {json.dumps(enhanced_response)}\n\n"
                        continue
                    else:
                        has_content_started = True
                        reasoning_phase = False
                
                # Detect content type and format
                content_type = detect_content_type(content)
                multimodal_content = []
                
                if content_type == ContentType.MARKDOWN:
                    multimodal_content.append({
                        'type': 'markdown',
                        'data': content,
                        'format': 'markdown'
                    })
                elif content_type == ContentType.JSON:
                    try:
                        parsed_json = json.loads(content)
                        multimodal_content.append({
                            'type': 'json',
                            'data': parsed_json,
                            'format': 'json'
                        })
                    except:
                        multimodal_content.append({
                            'type': 'text',
                            'data': content,
                            'format': 'text'
                        })
                else:
                    multimodal_content.append({
                        'type': 'text',
                        'data': content,
                        'format': 'text'
                    })
                
                enhanced_response = {
                    'type': 'content',
                    'content': content,  # Keep for backward compatibility
                    'content_type': content_type.value if content_type else 'text',
                    'provider': 'openai',
                    'model': actual_model,
                    'multimodal_content': multimodal_content,
                    'preserve_formatting': True
                }
                yield f"data: {json.dumps(enhanced_response)}\n\n"
            
            # Handle tool calls - ACCUMULATE during streaming, DON'T spam messages
            if hasattr(delta, 'tool_calls') and delta.tool_calls:
                print(f"🔧 Tool calls detected: {delta.tool_calls}")
                for tool_call_delta in delta.tool_calls:
                    # Use index as the key since OpenAI sends id=None for continuation chunks
                    tool_call_index = getattr(tool_call_delta, 'index', 0)
                    tool_call_id = tool_call_delta.id
                    
                    # Use index as the primary key, but store the actual ID when available
                    if tool_call_index not in accumulated_tool_calls:
                        accumulated_tool_calls[tool_call_index] = {
                            'id': tool_call_id,  # This will be None for continuation chunks
                            'name': '',
                            'arguments': ''
                        }
                    
                    # Update the ID if we get a real one (first chunk)
                    if tool_call_id and accumulated_tool_calls[tool_call_index]['id'] is None:
                        accumulated_tool_calls[tool_call_index]['id'] = tool_call_id
                    
                    # Accumulate tool call data
                    if tool_call_delta.function:
                        if tool_call_delta.function.name:
                            accumulated_tool_calls[tool_call_index]['name'] = tool_call_delta.function.name
                        if tool_call_delta.function.arguments:
                            accumulated_tool_calls[tool_call_index]['arguments'] += tool_call_delta.function.arguments
                
                # Show enhanced tool preparation with loading state
                if not tool_prep_shown and accumulated_tool_calls:
                    print(f"🔧 DEBUG: Showing tool preparation. Tool calls detected: {list(accumulated_tool_calls.keys())}")
                    tool_prep_shown = True
                    
                    # Send tool loading state
                    tool_loading = {
                        'type': 'tool_loading',
                        'content': 'Preparing to execute tools...',
                        'content_type': 'tool_loading',
                        'provider': 'openai',
                        'model': actual_model,
                        'multimodal_content': [{'type': 'tool_loading', 'data': 'Preparing tools...', 'format': 'text'}],
                        'preserve_formatting': True
                    }
                    yield f"data: {json.dumps(tool_loading)}\n\n"
            
        # After streaming completes, check if there were any tool calls to process
        print(f"✅ Initial streaming completed with {chunk_count} chunks")
        print(f"🔍 Accumulated tool calls: {accumulated_tool_calls}")
        print(f"🔍 Number of accumulated tool calls: {len(accumulated_tool_calls) if accumulated_tool_calls else 0}")
        
        # Process any accumulated tool calls AFTER the main stream
        if accumulated_tool_calls:
            print(f"🔧 Processing {len(accumulated_tool_calls)} tool calls after stream completion...")
            print(f"🔧 Tool calls data: {accumulated_tool_calls}")
            
            # Execute all tool calls in parallel
            for tool_call_index, tool_data in accumulated_tool_calls.items():
                if tool_data['name'] and tool_data['arguments']:
                    try:
                        # Try to parse complete arguments
                        tool_args = json.loads(tool_data['arguments'])
                        print(f"🎨 Executing {tool_data['name']} with complete args: {tool_args}")
                        
                        # Stream enhanced loading state for tool execution
                        tool_name_clean = tool_data['name'].replace('generate', '').replace('create', '').lower().strip()
                        loading_msg = {
                            'type': 'tool_executing',
                            'content': f"Generating {tool_name_clean}...",
                            'content_type': 'tool_executing',
                            'provider': 'openai',
                            'model': actual_model,
                            'tool_info': {
                                'name': tool_data['name'],
                                'status': 'executing',
                                'description': f"Creating {tool_name_clean} with AI"
                            },
                            'multimodal_content': [{'type': 'tool_executing', 'data': f"Generating {tool_name_clean}...", 'format': 'text'}],
                            'preserve_formatting': True
                        }
                        yield f"data: {json.dumps(loading_msg)}\n\n"
                        
                        # Execute tool
                        if tool_data['name'] in ['generateImage', 'createDiagram']:
                            print(f"🎨 Executing {tool_data['name']} with args: {tool_args}")
                            tool_result = await execute_image_generation_tool(tool_data['name'], tool_args, 'openai')
                            print(f"🔍 Tool execution result: {tool_result}")
                            
                            # Check if tool execution was successful
                            if tool_result.get('success'):
                                print(f"✅ Tool execution successful")
                                
                                # Stream tool result with image
                                tool_result_response = {
                                    'type': 'tool_result',
                                    'content_type': 'tool_result',
                                    'tool_result': {
                                        'id': tool_data['id'],
                                        'name': tool_data['name'],
                                        'result': tool_result
                                    },
                                    'provider': 'openai',
                                    'model': actual_model,
                                    'multimodal_content': [{'type': 'tool_result', 'data': tool_result, 'format': 'json'}]
                                }
                                yield f"data: {json.dumps(tool_result_response)}\n\n"
                            else:
                                print(f"❌ Tool execution failed: {tool_result.get('error')}")
                                
                                # Stream tool error
                                error_response = {
                                    'type': 'tool_error',
                                    'content_type': 'tool_error',
                                    'tool_error': {
                                        'id': tool_data['id'],
                                        'name': tool_data['name'],
                                        'error': tool_result.get('error', 'Unknown error')
                                    },
                                    'provider': 'openai',
                                    'model': actual_model,
                                    'multimodal_content': [{'type': 'tool_error', 'data': tool_result, 'format': 'json'}]
                                }
                                yield f"data: {json.dumps(error_response)}\n\n"
                                
                                # Also stream a user-friendly error message
                                error_msg = {
                                    'type': 'content',
                                    'content': f"\n❌ Image generation failed: {tool_result.get('error', 'Unknown error')}\n",
                                    'content_type': 'text',
                                    'provider': 'openai',
                                    'model': actual_model,
                                    'multimodal_content': [{'type': 'text', 'data': 'Error occurred', 'format': 'text'}],
                                    'preserve_formatting': True
                                }
                                yield f"data: {json.dumps(error_msg)}\n\n"
                            
                            # Continue conversation with tool result
                            print(f"🔄 Continuing conversation with tool result...")
                            
                            # Create continued conversation
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
                                            'model': actual_model,
                                            'multimodal_content': [{'type': 'text', 'data': content, 'format': 'text'}],
                                            'preserve_formatting': True
                                        }
                                        yield f"data: {json.dumps(follow_response)}\n\n"
                                        
                            except Exception as e:
                                print(f"❌ Follow-up conversation error: {str(e)}")
                                # Still provide a basic completion message
                                completion_msg = {
                                    'type': 'content',
                                    'content': f"\n✅ I've generated the {tool_data['name'].replace('generate', '').lower().strip()} for you!",
                                    'content_type': 'text',
                                    'provider': 'openai',
                                    'model': actual_model,
                                    'multimodal_content': [{'type': 'text', 'data': 'Image generated!', 'format': 'text'}],
                                    'preserve_formatting': True
                                }
                                yield f"data: {json.dumps(completion_msg)}\n\n"
                        
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON decode error for {tool_call_index}: {str(e)}")
                        print(f"⚠️ Raw arguments: {tool_data.get('arguments', 'None')}")
                    except Exception as e:
                        print(f"❌ Tool execution error for {tool_call_index}: {str(e)}")
                        print(f"❌ Tool data: {tool_data}")
                        import traceback
                        print(f"❌ Full traceback: {traceback.format_exc()}")
                        error_response = {
                            'type': 'tool_error',
                            'content_type': 'tool_error',
                            'tool_error': {'id': tool_data['id'], 'name': tool_data['name'], 'error': str(e)},
                            'provider': 'openai',
                            'model': actual_model
                        }
                        yield f"data: {json.dumps(error_response)}\n\n"
                        
                        # Stream tool call initiation
                        enhanced_response = {
                            'type': 'tool_call',
                            'content_type': 'tool_call',
                            'tool_call': {
                                'id': tool_data['id'],
                                'name': tool_data['name'],
                                'arguments': tool_data['arguments']
                            },
                            'provider': 'openai',
                            'model': actual_model,
                            'multimodal_content': [{
                                'type': 'tool_call',
                                'data': {
                                    'id': tool_data['id'],
                                    'name': tool_data['name'],
                                    'arguments': tool_data['arguments']
                                },
                                'format': 'json'
                            }]
                        }
                        yield f"data: {json.dumps(enhanced_response)}\n\n"
                        
                        # Execute image generation tools
                        if tool_data['name'] in ['generateImage', 'createDiagram']:
                            try:
                                tool_args = json.loads(tool_data['arguments'])
                                print(f"🎨 Executing {tool_data['name']} with args: {tool_args}")
                                
                                # Add smooth transition message before tool execution
                                transition_response = {
                                    'type': 'content',
                                    'content': f"🎨 Creating your {tool_data['name'].replace('generate', '').replace('create', '').lower().strip()} now...\n\n",
                                    'content_type': 'text',
                                    'provider': 'openai',
                                    'model': actual_model,
                                    'multimodal_content': [{
                                        'type': 'text',
                                        'data': f"🎨 Creating your visual content...\n\n",
                                        'format': 'text'
                                    }],
                                    'preserve_formatting': True
                                }
                                yield f"data: {json.dumps(transition_response)}\n\n"
                                
                                tool_result = await execute_image_generation_tool(tool_data['name'], tool_args, 'openai')
                                print(f"✅ Tool execution successful: {tool_result}")
                                
                                # Stream tool result
                                tool_result_response = {
                                    'type': 'tool_result',
                                    'content_type': 'tool_result',
                                    'tool_result': {
                                        'id': tool_data['id'],
                                        'name': tool_data['name'],
                                        'result': tool_result
                                    },
                                    'provider': 'openai',
                                    'model': actual_model,
                                    'multimodal_content': [{
                                        'type': 'tool_result',
                                        'data': tool_result,
                                        'format': 'json'
                                    }]
                                }
                                yield f"data: {json.dumps(tool_result_response)}\n\n"
                                
                                # Add completion message after successful tool execution
                                completion_response = {
                                    'type': 'content',
                                    'content': f"✅ Your visual content has been generated! The {tool_data['name'].replace('generate', '').lower().strip()} shows the requested information.",
                                    'content_type': 'text',
                                    'provider': 'openai',
                                    'model': actual_model,
                                    'multimodal_content': [{
                                        'type': 'text',
                                        'data': f"✅ Visual content generated successfully!",
                                        'format': 'text'
                                    }],
                                    'preserve_formatting': True
                                }
                                yield f"data: {json.dumps(completion_response)}\n\n"
                                
                            except Exception as e:
                                print(f"❌ Tool execution error: {str(e)}")
                                # Stream tool error
                                error_response = {
                                    'type': 'tool_error',
                                    'content_type': 'tool_error',
                                    'tool_error': {
                                        'id': tool_data['id'],
                                        'name': tool_data['name'],
                                        'error': str(e)
                                    },
                                    'provider': 'openai',
                                    'model': actual_model
                                }
                                yield f"data: {json.dumps(error_response)}\n\n"
                        
                        # Remove processed tool call
                        del accumulated_tool_calls[tool_call_index]
                        
                    except json.JSONDecodeError:
                        # Arguments not complete yet, continue accumulating
                        pass
        else:
            print(f"⚠️ No tool calls were accumulated during streaming!")
        
        print(f"✅ Completed processing {chunk_count} chunks")
        
    except Exception as e:
        print(f"❌ Enhanced OpenAI Error: {str(e)}")
        yield f"data: {json.dumps({'error': f'Enhanced OpenAI Error: {str(e)}'})}\n\n"
    
    # Always send final DONE signal
    yield "data: [DONE]\n\n"

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
                        # Handle both dict and FileInfo objects
                        if isinstance(file_info, dict):
                            filename = file_info.get('filename', 'Unknown')
                            media_type = file_info.get('mediaType', 'unknown')
                        else:
                            # FileInfo object
                            filename = getattr(file_info, 'filename', 'Unknown') or 'Unknown'
                            media_type = getattr(file_info, 'mediaType', 'unknown') or 'unknown'
                        
                        file_context += f"- {filename} ({media_type})\n"
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
                # Handle both dict and ToolInfo objects
                if isinstance(tool, dict):
                    tool_name = tool.get("name", "unknown_tool")
                    tool_desc = tool.get("description", "")
                    tool_params = tool.get("parameters", {})
                else:
                    # ToolInfo object
                    tool_name = getattr(tool, 'name', 'unknown_tool')
                    tool_desc = getattr(tool, 'description', '') or ''
                    tool_params = getattr(tool, 'parameters', {}) or {}
                
                anthropic_tools.append({
                    "name": tool_name,
                    "description": tool_desc,
                    "input_schema": tool_params
                })

        # Enhanced request parameters
        # Use model mapping from service
        actual_model = getattr(service, 'model_mapping', {}).get(model or service.default_model, "claude-3-5-sonnet-20241022")
        
        # Updated Claude API limits based on actual model capabilities
        if 'claude-sonnet-4' in actual_model or 'claude-3-7-sonnet' in actual_model:
            max_tokens = 64000  # Claude 4 Sonnet & 3.7 Sonnet (64K output) 🔥
        elif 'claude-opus-4' in actual_model:
            max_tokens = 32000  # Claude 4 Opus (32K output) 🔥
        elif 'claude-3-5-sonnet' in actual_model:
            max_tokens = 8192   # Claude 3.5 Sonnet (8K output - old model)
        elif 'opus' in actual_model.lower():
            max_tokens = 4096   # Claude 3 Opus maximum
        elif 'haiku' in actual_model.lower():
            max_tokens = 8192   # Claude 3.5 Haiku maximum
        else:
            max_tokens = 64000  # Default to highest available (Claude 4 Sonnet)
            
        request_params = {
            "model": actual_model,
            "max_tokens": max_tokens,
            "system": system_message,
            "messages": anthropic_messages
        }
        
        # Add tools if available
        if anthropic_tools:
            request_params["tools"] = anthropic_tools

        # Let Anthropic provide real reasoning, not fake messages

        # Add beta header for Claude 3.5 Sonnet to get full 8K output tokens
        extra_headers = {}
        if 'sonnet' in actual_model.lower():
            extra_headers = {"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"}

        # Use enhanced streaming API with multimodal support
        with service.client.messages.stream(**request_params, extra_headers=extra_headers) as stream:
            for text in stream.text_stream:
                if text:
                    # Detect reasoning patterns in Claude's response
                    is_reasoning = enable_reasoning and any(phrase in text.lower() for phrase in ['let me think', 'first,', 'step 1', 'reasoning:', 'analysis:', 'i need to', 'let me analyze'])
                    
                    if is_reasoning:
                        enhanced_response = {
                            'type': 'reasoning',
                            'content': text,
                            'content_type': 'reasoning',
                            'provider': 'anthropic',
                            'model': actual_model,
                            'multimodal_content': [{
                                'type': 'reasoning',
                                'data': text,
                                'format': 'text'
                            }]
                        }
                        yield f"data: {json.dumps(enhanced_response)}\n\n"
                    else:
                        # Enhanced content detection for Claude
                        content_type = detect_content_type(text)
                        multimodal_content = []
                        
                        if content_type == ContentType.MARKDOWN:
                            multimodal_content.append({
                                'type': 'markdown',
                                'data': text,
                                'format': 'markdown'
                            })
                        elif content_type == ContentType.TABLE:
                            multimodal_content.append({
                                'type': 'table',
                                'data': text,
                                'format': 'markdown_table'
                            })
                        elif content_type == ContentType.DIAGRAM:
                            multimodal_content.append({
                                'type': 'diagram',
                                'data': text,
                                'format': 'ascii_art'
                            })
                        elif content_type == ContentType.JSON:
                            try:
                                parsed_json = json.loads(text)
                                multimodal_content.append({
                                    'type': 'json',
                                    'data': parsed_json,
                                    'format': 'json'
                                })
                            except:
                                multimodal_content.append({
                                    'type': 'text',
                                    'data': text,
                                    'format': 'text'
                                })
                        else:
                            multimodal_content.append({
                                'type': 'text',
                                'data': text,
                                'format': 'text'
                            })
                        
                        enhanced_response = {
                            'type': 'content',
                            'content': text,  # Keep for backward compatibility
                            'content_type': content_type.value if content_type else 'text',
                            'provider': 'anthropic',
                            'model': actual_model,
                            'multimodal_content': multimodal_content,
                            'preserve_formatting': True
                        }
                        yield f"data: {json.dumps(enhanced_response)}\n\n"
        
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
        system_content = """You are Digi Setu AI powered by Grok, an advanced educational content transformation assistant with Aurora image generation capabilities.

Key capabilities:
- Transform static content into interactive learning experiences
- Generate images using Aurora when users request images or when images would enhance understanding
- Create detailed educational responses with examples
- Process and analyze various content types
- Provide engaging, witty, and informative responses
- Show reasoning process when requested

🎨 IMAGE GENERATION: When users ask for images or when images would help explain concepts, you can generate them using Aurora. Simply mention what image you would create and the system will generate it.

Always be helpful, educational, and engaging with a touch of Grok's characteristic wit."""

        if enable_reasoning:
            system_content += "\n\nIMPORTANT: When reasoning is enabled, think through your response step by step. Show your thought process clearly."

        # Add system message
        if not any(msg["role"] == "system" for msg in grok_messages):
            grok_messages.insert(0, {"role": "system", "content": system_content})

        # Let Grok provide real reasoning, not fake messages
        
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
                                    is_reasoning = enable_reasoning and any(phrase in content.lower() for phrase in ['let me think', 'reasoning:', 'step by step', 'analysis:', 'let me analyze', 'thinking through'])
                                    
                                    if is_reasoning:
                                        enhanced_response = {
                                            'type': 'reasoning',
                                            'content': content,
                                            'content_type': 'reasoning',
                                            'provider': 'grok',
                                            'model': model or service.default_model,
                                            'multimodal_content': [{
                                                'type': 'reasoning',
                                                'data': content,
                                                'format': 'text'
                                            }]
                                        }
                                        yield f"data: {json.dumps(enhanced_response)}\n\n"
                                    else:
                                        # Enhanced content detection for Grok
                                        content_type = detect_content_type(content)
                                        multimodal_content = []
                                        
                                        if content_type == ContentType.MARKDOWN:
                                            multimodal_content.append({
                                                'type': 'markdown',
                                                'data': content,
                                                'format': 'markdown'
                                            })
                                        elif content_type == ContentType.TABLE:
                                            multimodal_content.append({
                                                'type': 'table',
                                                'data': content,
                                                'format': 'markdown_table'
                                            })
                                        elif content_type == ContentType.DIAGRAM:
                                            multimodal_content.append({
                                                'type': 'diagram',
                                                'data': content,
                                                'format': 'ascii_art'
                                            })
                                        elif content_type == ContentType.JSON:
                                            try:
                                                parsed_json = json.loads(content)
                                                multimodal_content.append({
                                                    'type': 'json',
                                                    'data': parsed_json,
                                                    'format': 'json'
                                                })
                                            except:
                                                multimodal_content.append({
                                                    'type': 'text',
                                                    'data': content,
                                                    'format': 'text'
                                                })
                                        else:
                                            multimodal_content.append({
                                                'type': 'text',
                                                'data': content,
                                                'format': 'text'
                                            })
                                        
                                        enhanced_response = {
                                            'type': 'content',
                                            'content': content,  # Keep for backward compatibility
                                            'content_type': content_type.value if content_type else 'text',
                                            'provider': 'grok',
                                            'model': model or service.default_model,
                                            'multimodal_content': multimodal_content,
                                            'preserve_formatting': True
                                        }
                                        yield f"data: {json.dumps(enhanced_response)}\n\n"
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
                description="256k context, 256k output, Aurora image generation",
                reasoning=True,
                toolCalling=True,
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

# 🎨 TOOL EXECUTION FUNCTIONS
async def execute_image_generation_tool(tool_name: str, tool_args: dict, provider: str):
    """Execute image generation tools (generateImage, createDiagram)"""
    try:
        prompt = tool_args.get("prompt", "")
        size = tool_args.get("size", "1024x1024")
        quality = tool_args.get("quality", "standard")
        style = tool_args.get("style", "vivid")
        
        if not prompt:
            raise ValueError("Prompt is required for image generation")
        
        # Enhance prompt based on tool type
        if tool_name == "createDiagram":
            diagram_type = tool_args.get("type", "diagram")
            diagram_style = tool_args.get("style", "educational")
            prompt = f"Create a {diagram_style} {diagram_type}: {prompt}. Make it clear, professional, and educational."
        
        if provider == "openai":
            # Use DALL-E 3 for OpenAI
            service = get_service(AIProvider.OPENAI)
            try:
                response = service.client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    style=style,
                    n=1
                )
                image_url = response.data[0].url
            except Exception as e:
                print(f"⚠️ DALL-E 3 API call failed: {str(e)}")
                # For now, use a placeholder when API key is missing
                image_url = f"https://via.placeholder.com/{size}/FF6B6B/FFFFFF?text=DALL-E+Image%3A+{prompt[:30]}..."
            
        elif provider == "grok":
            # Use Aurora for Grok image generation
            # TODO: Replace with actual Grok Aurora API when available
            try:
                # This is a placeholder implementation
                # In the future, this would call xAI's Aurora API
                grok_service = get_service(AIProvider.GROK)
                
                # For now, simulate Aurora image generation
                # Replace this with actual Aurora API call:
                # response = grok_service.aurora_client.generate_image(
                #     prompt=prompt,
                #     size=size,
                #     style=style
                # )
                
                # Placeholder response
                image_url = f"https://via.placeholder.com/{size}/9333EA/FFFFFF?text=Aurora+Image%3A+{prompt[:20]}..."
                
            except Exception as e:
                # Fallback to placeholder
                image_url = f"https://via.placeholder.com/{size}/9333EA/FFFFFF?text=Grok+Aurora+Coming+Soon"
            
        else:
            raise ValueError(f"Image generation not supported for provider: {provider}")
        
        return {
            "success": True,
            "image_url": image_url,
            "url": image_url,
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "style": style,
            "provider": provider,
            "tool_name": tool_name
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tool_name": tool_name
        }

@router.post("/generate-image")
async def generate_image(request: dict):
    """Generate images using DALL-E (OpenAI only) - Legacy endpoint"""
    try:
        prompt = request.get("prompt", "")
        provider = request.get("provider", "openai")
        size = request.get("size", "1024x1024")
        quality = request.get("quality", "standard")
        
        if provider != "openai":
            raise HTTPException(status_code=400, detail="Image generation only supported for OpenAI")
        
        service = get_service(AIProvider.OPENAI)
        
        # Generate image using DALL-E
        response = service.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=1
        )
        
        image_url = response.data[0].url
        
        return {
            "type": "image_generation",
            "content_type": "image",
            "provider": "openai",
            "model": "dall-e-3",
            "multimodal_content": [{
                "type": "image",
                "data": image_url,
                "format": "png",
                "url": image_url,
                "metadata": {
                    "size": size,
                    "quality": quality,
                    "prompt": prompt
                }
            }],
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation error: {str(e)}")

@router.post("/transcribe-audio")
async def transcribe_audio(request: dict):
    """Transcribe audio using Whisper (OpenAI only)"""
    try:
        audio_data = request.get("audio_data", "")
        provider = request.get("provider", "openai")
        
        if provider != "openai":
            raise HTTPException(status_code=400, detail="Audio transcription only supported for OpenAI")
        
        service = get_service(AIProvider.OPENAI)
        
        # Note: This would need proper file handling in a real implementation
        # For now, return a placeholder response
        
        return {
            "type": "audio_transcription",
            "content_type": "text",
            "provider": "openai",
            "model": "whisper-1",
            "multimodal_content": [{
                "type": "text",
                "data": "Audio transcription would be processed here",
                "format": "text"
            }],
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio transcription error: {str(e)}")

@router.get("/test-multimodal")
async def test_multimodal_response():
    """Test endpoint to demonstrate multimodal response capabilities"""
    try:
        # Sample multimodal content to test frontend rendering
        sample_responses = [
            {
                'type': 'content',
                'content': '# Sample Table\n\n| Name | Age | City |\n|------|-----|------|\n| John | 25 | NYC |\n| Jane | 30 | LA |',
                'content_type': 'table',
                'provider': 'test',
                'model': 'sample',
                'multimodal_content': [{
                    'type': 'table',
                    'data': '# Sample Table\n\n| Name | Age | City |\n|------|-----|------|\n| John | 25 | NYC |\n| Jane | 30 | LA |',
                    'format': 'markdown_table'
                }],
                'preserve_formatting': True
            },
            {
                'type': 'content',
                'content': '{"users": [{"name": "John", "age": 25}, {"name": "Jane", "age": 30}], "total": 2}',
                'content_type': 'json',
                'provider': 'test',
                'model': 'sample',
                'multimodal_content': [{
                    'type': 'json',
                    'data': {"users": [{"name": "John", "age": 25}, {"name": "Jane", "age": 30}], "total": 2},
                    'format': 'json'
                }],
                'preserve_formatting': True
            },
            {
                'type': 'content',
                'content': '┌─────────────┐    ┌─────────────┐\n│   Frontend  │ ←→ │   Backend   │\n│     Vue     │    │   FastAPI   │\n└─────────────┘    └─────────────┘\n       ↕                   ↕\n   User Input          Database',
                'content_type': 'diagram',
                'provider': 'test',
                'model': 'sample',
                'multimodal_content': [{
                    'type': 'diagram',
                    'data': '┌─────────────┐    ┌─────────────┐\n│   Frontend  │ ←→ │   Backend   │\n│     Vue     │    │   FastAPI   │\n└─────────────┘    └─────────────┘\n       ↕                   ↕\n   User Input          Database',
                    'format': 'ascii_art'
                }],
                'preserve_formatting': True
            }
        ]
        
        return {
            "message": "Multimodal test content generated",
            "samples": sample_responses,
            "capabilities": [
                "markdown_tables",
                "json_objects", 
                "ascii_diagrams",
                "image_generation",
                "syntax_highlighting"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test error: {str(e)}")
