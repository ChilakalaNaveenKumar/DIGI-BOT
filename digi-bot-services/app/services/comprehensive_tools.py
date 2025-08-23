"""
Comprehensive Tools - All Available Tools for AI
Includes chart tools, audio, vision, search, and more.
"""

import json
from typing import Dict, Any, List
import structlog
from app.services.chart_tools import get_chart_tools, process_tool_calls as process_chart_tools

from app.services.audio_service import AudioService
from app.services.vision_service import VisionService
from app.services.tool_service import ToolService

logger = structlog.get_logger(__name__)


def get_default_tools() -> List[Dict[str, Any]]:
    """Get default tools - web search, charts, and data tables."""
    
    tools = []
    
    # Add Anthropic's native web search tool
    tools.append({
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 3
    })
    
    # Add chart tools
    chart_tools = get_chart_tools()
    tools.extend(chart_tools)
    
    return tools


def get_conditional_tools(has_audio: bool = False, has_image: bool = False, enable_audio_generation: bool = False) -> List[Dict[str, Any]]:
    """Get tools based on user input - only include what's needed."""
    
    tools = get_default_tools()  # Start with web search, charts, data tables
    
    # Add audio transcription tool if user uploaded audio
    if has_audio:
        tools.append({
            "name": "transcribe_audio",
            "description": "Transcribe audio to text",
            "input_schema": {
                "type": "object",
                "properties": {
                    "audio_data": {
                        "type": "string",
                        "description": "Base64 encoded audio data"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (optional)"
                    }
                },
                "required": ["audio_data"]
            }
        })
    
    # Add audio generation tool if enabled (for future GPT-5 like functionality)
    if enable_audio_generation:
        tools.append({
            "name": "generate_audio",
            "description": "Generate audio from text",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to convert to audio"
                    },
                    "voice": {
                        "type": "string",
                        "enum": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                        "description": "Voice to use for generation"
                    },
                    "speed": {
                        "type": "number",
                        "description": "Speed of speech (0.25 to 4.0)"
                    }
                },
                "required": ["text"]
            }
        })
    
    # Add image analysis tool if user uploaded image
    if has_image:
        tools.append({
            "name": "analyze_image",
            "description": "Analyze images",
            "input_schema": {
                "type": "object",
                "properties": {
                    "image_data": {
                        "type": "string",
                        "description": "Base64 encoded image data"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["general", "ocr", "detailed", "objects"],
                        "description": "Type of analysis"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Analysis instruction"
                    }
                },
                "required": ["image_data"]
            }
        })
    
    return tools


# Backward compatibility
def get_all_tools() -> List[Dict[str, Any]]:
    """Backward compatibility - returns default tools only."""
    return get_default_tools()


async def process_comprehensive_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process all types of tool calls including charts, audio, vision, search, etc."""
    
    logger.info(f"🔧 Processing {len(tool_calls)} tool calls")
    results = []
    
    # Initialize services
    audio_service = AudioService()
    vision_service = VisionService()
    tool_service = ToolService()
    
    for tool_call in tool_calls:
        tool_name = tool_call.get('name')
        tool_id = tool_call.get('id')
        tool_input = tool_call.get('input', {})
        
        logger.info(f"🚀 Processing tool: {tool_name} (ID: {tool_id})")
        logger.info(f"📝 Tool input: {tool_input}")
        
        try:
            if tool_name in ['chartjs_tool', 'data_table_tool']:
                # Handle chart tools
                logger.info(f"📊 Processing chart tool: {tool_name}")
                chart_results = process_chart_tools([tool_call])
                logger.info(f"✅ Chart tool result: {len(chart_results)} results")
                results.extend(chart_results)
                
            elif tool_name == 'web_search':
                # Anthropic's native web search is handled by the provider itself
                # We don't need to process it here - it's handled natively by Claude
                logger.info("🌐 Web search handled natively by Anthropic Claude")
                continue
                
            elif tool_name == 'transcribe_audio':
                # Handle audio transcription
                logger.info("🎵 Processing audio transcription")
                audio_data = tool_input.get('audio_data', '')
                language = tool_input.get('language')
                
                transcription = await audio_service.transcribe_audio_base64(audio_data, language)
                logger.info(f"✅ Audio transcription completed")
                
                # Handle different response types safely
                if isinstance(transcription, dict):
                    content = transcription.get('transcription', 'No transcription available')
                elif hasattr(transcription, 'transcription'):
                    content = transcription.transcription
                else:
                    content = str(transcription) if transcription else 'No transcription available'
                
                result = {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": f"🎵 Audio Transcription:\n\n{content}"
                }
                results.append(result)
                
            elif tool_name == 'generate_audio':
                # Handle audio generation (future GPT-5 like functionality)
                logger.info("🔊 Processing audio generation")
                text = tool_input.get('text', '')
                voice = tool_input.get('voice', 'alloy')
                speed = tool_input.get('speed', 1.0)
                
                audio_generation = await audio_service.generate_audio_from_text(text, voice, speed)
                logger.info(f"✅ Audio generation completed")
                
                # Handle different response types safely
                if isinstance(audio_generation, dict):
                    content = audio_generation.get('audio_url', 'No audio generated')
                elif hasattr(audio_generation, 'audio_url'):
                    content = audio_generation.audio_url
                else:
                    content = str(audio_generation) if audio_generation else 'No audio generated'
                
                result = {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": f"🔊 Audio Generated:\n\n{content}"
                }
                results.append(result)
                
            elif tool_name == 'analyze_image':
                # Handle image analysis
                logger.info("👁️ Processing image analysis")
                image_data = tool_input.get('image_data', '')
                analysis_type = tool_input.get('analysis_type', 'general')
                prompt = tool_input.get('prompt', 'Analyze this image')
                
                analysis = await vision_service.analyze_image_base64(image_data, prompt, analysis_type)
                logger.info(f"✅ Image analysis completed")
                
                # Handle different response types safely
                if isinstance(analysis, dict):
                    content = analysis.get('analysis', 'No analysis available')
                elif hasattr(analysis, 'analysis'):
                    content = analysis.analysis
                else:
                    content = str(analysis) if analysis else 'No analysis available'
                
                result = {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": f"👁️ Image Analysis:\n\n{content}"
                }
                results.append(result)
                
# Removed old unused tools: calculate, get_weather, generate_code, analyze_data
                
            else:
                # Unknown tool
                logger.warning(f"❌ Unknown tool: {tool_name}")
                result = {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": f"❌ Unknown tool: {tool_name}"
                }
                results.append(result)
                
        except Exception as e:
            # Error handling
            logger.error(f"❌ Error executing {tool_name}: {str(e)}")
            result = {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": f"❌ Error executing {tool_name}: {str(e)}"
            }
            results.append(result)
    
    logger.info(f"✅ Completed processing {len(tool_calls)} tool calls, generated {len(results)} results")
    return results
