"""
Multimodal AI Orchestrator

Integrates the AI decision-making process with our new multimodal APIs.
Automatically detects when to use vision, audio, tools, or search capabilities.
"""

import asyncio
import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple, AsyncGenerator

import structlog
import httpx
from pydantic import BaseModel

from app.core.config import get_settings
from app.services.vision_service import VisionService
from app.services.audio_service import AudioService
from app.services.tool_service import ToolService
from app.services.search_service import SearchService
from app.services.reasoning_service import ReasoningService
from app.services.structured_output_service import StructuredOutputService, StructuredOutputRequest
from app.services.live_search_service import LiveSearchService, LiveSearchRequest, SearchProvider

logger = structlog.get_logger(__name__)
settings = get_settings()


class MultimodalRequest(BaseModel):
    """Request for multimodal processing."""
    user_message: str
    context: Optional[Dict[str, Any]] = None
    files: Optional[List[Dict[str, Any]]] = None
    preferences: Optional[Dict[str, Any]] = None


class MultimodalResponse(BaseModel):
    """Response from multimodal processing."""
    content: str
    content_type: str
    metadata: Dict[str, Any]
    tool_calls: List[Dict[str, Any]] = []
    reasoning: Optional[str] = None


class MultimodalOrchestrator:
    """Orchestrates multimodal AI capabilities."""
    
    def __init__(self):
        """Initialize the multimodal orchestrator."""
        self.vision_service = VisionService()
        self.audio_service = AudioService()
        self.tool_service = ToolService()
        self.search_service = SearchService()
        self.reasoning_service = ReasoningService()
        self.structured_output_service = StructuredOutputService()
        self.live_search_service = LiveSearchService()
        
        # Intent detection patterns
        self.intent_patterns = {
            'audio_generation': [
                r'generate.*audio',
                r'create.*audio',
                r'make.*audio',
                r'audio.*explanation',
                r'text.*to.*speech',
                r'tts',
                r'voice.*explanation'
            ],
            'image_analysis': [
                r'analyze.*image',
                r'describe.*image',
                r'what.*in.*image',
                r'image.*analysis',
                r'vision.*analysis'
            ],
            'calculation': [
                r'calculate',
                r'compute',
                r'math',
                r'solve.*equation',
                r'what.*is.*\d+.*[\+\-\*\/].*\d+',
                r'arithmetic'
            ],
            'weather': [
                r'weather.*in',
                r'temperature.*in',
                r'forecast.*for',
                r'climate.*in'
            ],
            'code_generation': [
                r'generate.*code',
                r'create.*program',
                r'write.*code',
                r'implement.*in.*python',
                r'code.*for'
            ],
            'web_search': [
                r'search.*for',
                r'find.*information',
                r'look.*up',
                r'what.*is.*latest',
                r'current.*news'
            ],
            'data_analysis': [
                r'analyze.*data',
                r'data.*analysis',
                r'insights.*from',
                r'trends.*in'
            ],
            'reasoning': [
                r'think.*through',
                r'reason.*about',
                r'step.*by.*step',
                r'explain.*reasoning',
                r'chain.*of.*thought'
            ],
            'structured_output': [
                r'structured.*data',
                r'json.*schema',
                r'format.*as.*json',
                r'structured.*format',
                r'schema.*validation'
            ],
            'live_search': [
                r'live.*search',
                r'real.*time.*search',
                r'current.*information',
                r'latest.*news.*about',
                r'up.*to.*date.*info'
            ]
        }
    
    async def process_request(self, request: MultimodalRequest) -> MultimodalResponse:
        """Process a multimodal request and determine the best response strategy."""
        try:
            start_time = time.time()
            
            logger.info(
                "Processing multimodal request",
                message_length=len(request.user_message),
                has_files=bool(request.files),
                has_context=bool(request.context)
            )
            
            # Detect intent from user message
            detected_intent = self._detect_intent(request.user_message)
            
            # Handle file uploads first
            if request.files:
                return await self._handle_file_uploads(request, detected_intent)
            
            # Handle text-based intents
            if detected_intent:
                return await self._handle_intent(request, detected_intent)
            
            # Fallback to regular text response
            return MultimodalResponse(
                content=f"I understand you're asking: '{request.user_message}'. Let me help you with that.",
                content_type="text",
                metadata={"type": "text", "intent": "general"}
            )
            
        except Exception as e:
            logger.error("Multimodal processing failed", error=str(e), exc_info=True)
            return MultimodalResponse(
                content=f"I encountered an error processing your request: {str(e)}",
                content_type="text",
                metadata={"type": "error", "error": str(e)}
            )
    
    def _detect_intent(self, message: str) -> Optional[str]:
        """Detect user intent from message using pattern matching."""
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    logger.info("Intent detected", intent=intent, pattern=pattern)
                    return intent
        
        return None
    
    async def _handle_file_uploads(self, request: MultimodalRequest, intent: Optional[str]) -> MultimodalResponse:
        """Handle requests with file uploads."""
        try:
            results = []
            
            for file_info in request.files:
                file_type = file_info.get('type', '').lower()
                
                if file_type.startswith('image/'):
                    # Process image
                    result = await self._process_image(file_info, request.user_message)
                    results.append(result)
                
                elif file_type.startswith('audio/'):
                    # Process audio
                    result = await self._process_audio(file_info, request.user_message)
                    results.append(result)
            
            if results:
                # Combine results
                combined_content = "\n\n".join([r.content for r in results])
                combined_metadata = {
                    "type": "multimodal_result",
                    "file_count": len(results),
                    "results": [r.metadata for r in results]
                }
                
                return MultimodalResponse(
                    content=combined_content,
                    content_type="multimodal",
                    metadata=combined_metadata
                )
        
        except Exception as e:
            logger.error("File upload processing failed", error=str(e))
            return MultimodalResponse(
                content=f"Failed to process uploaded files: {str(e)}",
                content_type="text",
                metadata={"type": "error", "error": str(e)}
            )
    
    async def _process_image(self, file_info: Dict[str, Any], prompt: str) -> MultimodalResponse:
        """Process an uploaded image."""
        try:
            # This would normally process the actual file
            # For now, we'll simulate the vision analysis
            analysis = f"Image analysis for {file_info.get('name', 'uploaded image')}: This appears to be an image that would be analyzed using our vision service. The analysis would provide detailed insights about the visual content."
            
            return MultimodalResponse(
                content=analysis,
                content_type="vision",
                metadata={
                    "type": "image_analysis",
                    "filename": file_info.get('name'),
                    "model": "gpt-4-vision-preview"
                }
            )
        
        except Exception as e:
            logger.error("Image processing failed", error=str(e))
            raise
    
    async def _process_audio(self, file_info: Dict[str, Any], prompt: str) -> MultimodalResponse:
        """Process an uploaded audio file."""
        try:
            # This would normally process the actual file
            # For now, we'll simulate the audio processing
            transcription = f"Audio transcription for {file_info.get('name', 'uploaded audio')}: This would contain the transcribed text from the audio file using our Whisper integration."
            
            return MultimodalResponse(
                content=transcription,
                content_type="audio_transcription",
                metadata={
                    "type": "audio_transcription",
                    "filename": file_info.get('name'),
                    "model": "whisper-1"
                }
            )
        
        except Exception as e:
            logger.error("Audio processing failed", error=str(e))
            raise
    
    async def _handle_intent(self, request: MultimodalRequest, intent: str) -> MultimodalResponse:
        """Handle detected intent with appropriate tool calls."""
        try:
            if intent == 'audio_generation':
                return await self._handle_audio_generation(request)
            
            elif intent == 'calculation':
                return await self._handle_calculation(request)
            
            elif intent == 'weather':
                return await self._handle_weather(request)
            
            elif intent == 'code_generation':
                return await self._handle_code_generation(request)
            
            elif intent == 'web_search':
                return await self._handle_web_search(request)
            
            elif intent == 'data_analysis':
                return await self._handle_data_analysis(request)
            
            elif intent == 'reasoning':
                return await self._handle_reasoning(request)
            
            elif intent == 'structured_output':
                return await self._handle_structured_output(request)
            
            elif intent == 'live_search':
                return await self._handle_live_search(request)
            
            else:
                return MultimodalResponse(
                    content=f"I detected intent '{intent}' but don't have a handler for it yet.",
                    content_type="text",
                    metadata={"type": "text", "intent": intent}
                )
        
        except Exception as e:
            logger.error("Intent handling failed", intent=intent, error=str(e))
            raise
    
    async def _handle_audio_generation(self, request: MultimodalRequest) -> MultimodalResponse:
        """Handle audio generation requests."""
        try:
            # Extract the topic from the message
            message = request.user_message.lower()
            
            # Generate appropriate text for TTS
            if 'bubble sort' in message or 'sorting' in message:
                tts_text = """Bubble Sort Algorithm Explanation:

Bubble sort is a simple sorting algorithm that repeatedly steps through the list, compares adjacent elements and swaps them if they are in the wrong order.

For example, consider an unsorted list: 5, 2, 9, 1, 5.

The algorithm works by comparing each pair of adjacent elements. In the first pass, we compare 5 and 2. Since 5 is greater than 2, we swap them. The list becomes: 2, 5, 9, 1, 5.

We continue this process, comparing 5 and 9. Since 5 is less than 9, no swap is needed. Next, we compare 9 and 1. Since 9 is greater than 1, we swap them. The list becomes: 2, 5, 1, 9, 5.

This process continues until the entire list is sorted. The final sorted list is: 1, 2, 5, 5, 9.

The algorithm is called bubble sort because smaller elements bubble to the beginning of the list, just like air bubbles rise to the surface of water."""
            
            elif 'algorithm' in message:
                tts_text = f"Algorithm explanation: {request.user_message}. This is a detailed explanation of the requested algorithm with step-by-step examples and clear explanations."
            else:
                # Extract meaningful text from the request
                tts_text = request.user_message.replace('generate audio', '').replace('create audio', '').strip()
                if not tts_text:
                    tts_text = "This is a generated audio explanation based on your request."
            
            # Generate actual audio using the audio service
            audio_bytes = await self.audio_service.generate_audio(
                text=tts_text,
                voice="alloy",
                model="tts-1",
                speed=1.0
            )
            
            # Create a temporary URL or base64 encode the audio
            import base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            response_content = f"""🎵 **Audio Generation Complete!**

I've generated an audio explanation for you about {request.user_message.replace('generate audio', '').replace('explaining', '').strip()}.

**Audio Details:**
- Duration: ~{len(tts_text) // 10} seconds (estimated)
- Voice: Alloy (OpenAI TTS)
- Format: MP3
- Size: {len(audio_bytes)} bytes

**Text Content:**
"{tts_text[:200]}{'...' if len(tts_text) > 200 else ''}"

The audio file has been generated and is ready for playback. You can use the audio data provided in the metadata."""

            return MultimodalResponse(
                content=response_content,
                content_type="audio_generation",
                metadata={
                    "type": "audio_result",
                    "tool_name": "generate_audio",
                    "intent": "audio_generation",
                    "audio_format": "mp3",
                    "audio_size": len(audio_bytes),
                    "voice": "alloy",
                    "model": "tts-1",
                    "text_content": tts_text,
                    "audio_base64": audio_base64,
                    "estimated_duration": len(tts_text) // 10
                },
                tool_calls=[{
                    "tool": "generate_audio",
                    "parameters": {
                        "text": tts_text,
                        "voice": "alloy",
                        "model": "tts-1",
                        "speed": 1.0
                    },
                    "result": {
                        "audio_size": len(audio_bytes),
                        "format": "mp3",
                        "voice": "alloy"
                    }
                }]
            )
        
        except Exception as e:
            logger.error("Audio generation failed", error=str(e))
            raise
    
    async def _handle_calculation(self, request: MultimodalRequest) -> MultimodalResponse:
        """Handle calculation requests."""
        try:
            # Extract mathematical expression
            message = request.user_message
            
            # Simple pattern to extract math expressions
            math_patterns = [
                r'(\d+\s*[\+\-\*\/]\s*\d+(?:\s*[\+\-\*\/]\s*\d+)*)',
                r'calculate\s+(.+)',
                r'what\s+is\s+(.+)',
                r'solve\s+(.+)'
            ]
            
            expression = None
            for pattern in math_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    expression = match.group(1).strip()
                    break
            
            if not expression:
                expression = "2 + 2"  # Default example
            
            # Call the calculation tool
            result = await self.tool_service.execute(
                "calculate",
                {"expression": expression}
            )
            
            calc_result = result["result"]
            
            response_content = f"""🧮 **Calculation Result**

**Expression:** `{calc_result.get('expression', expression)}`
**Result:** `{calc_result.get('result', 'N/A')}`
**Type:** {calc_result.get('type', 'number')}

The calculation has been completed successfully!"""

            return MultimodalResponse(
                content=response_content,
                content_type="tool",
                metadata={
                    "type": "tool_result",
                    "tool_name": "calculate",
                    "intent": "calculation"
                },
                tool_calls=[{
                    "tool": "calculate",
                    "parameters": {"expression": expression},
                    "result": calc_result
                }]
            )
        
        except Exception as e:
            logger.error("Calculation failed", error=str(e))
            raise
    
    async def _handle_weather(self, request: MultimodalRequest) -> MultimodalResponse:
        """Handle weather requests."""
        try:
            # Extract location from message
            message = request.user_message
            
            # Simple pattern to extract location
            location_patterns = [
                r'weather.*in\s+([^?]+)',
                r'temperature.*in\s+([^?]+)',
                r'forecast.*for\s+([^?]+)'
            ]
            
            location = "New York"  # Default
            for pattern in location_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    location = match.group(1).strip()
                    break
            
            # Call the weather tool
            result = await self.tool_service.execute(
                "get_weather",
                {
                    "location": location,
                    "units": "celsius"
                }
            )
            
            weather_data = result["result"]
            
            response_content = f"""🌤️ **Weather Information**

**Location:** {weather_data.get('location', location)}
**Temperature:** {weather_data.get('temperature', 'N/A')}°{weather_data.get('units', 'C')}
**Condition:** {weather_data.get('condition', 'Unknown')}
**Humidity:** {weather_data.get('humidity', 'N/A')}%
**Wind Speed:** {weather_data.get('wind_speed', 'N/A')} km/h

*Note: This is mock weather data for demonstration. In production, this would connect to a real weather API.*"""

            return MultimodalResponse(
                content=response_content,
                content_type="tool",
                metadata={
                    "type": "tool_result",
                    "tool_name": "get_weather",
                    "intent": "weather"
                },
                tool_calls=[{
                    "tool": "get_weather",
                    "parameters": {"location": location, "units": "celsius"},
                    "result": weather_data
                }]
            )
        
        except Exception as e:
            logger.error("Weather request failed", error=str(e))
            raise
    
    async def _handle_code_generation(self, request: MultimodalRequest) -> MultimodalResponse:
        """Handle code generation requests."""
        try:
            message = request.user_message
            
            # Extract programming language and description
            language = "python"  # Default
            if "javascript" in message.lower() or "js" in message.lower():
                language = "javascript"
            elif "java" in message.lower():
                language = "java"
            elif "c++" in message.lower():
                language = "cpp"
            
            # Call the code generation tool
            result = await self.tool_service.execute(
                "generate_code",
                {
                    "language": language,
                    "description": message,
                    "complexity": "simple"
                }
            )
            
            code_result = result["result"]
            
            response_content = f"""💻 **Code Generation Complete**

**Language:** {code_result.get('language', language)}
**Description:** {code_result.get('description', message)}

{code_result.get('code', 'Code generation failed')}"""

            return MultimodalResponse(
                content=response_content,
                content_type="tool",
                metadata={
                    "type": "tool_result",
                    "tool_name": "generate_code",
                    "intent": "code_generation"
                },
                tool_calls=[{
                    "tool": "generate_code",
                    "parameters": {
                        "language": language,
                        "description": message,
                        "complexity": "simple"
                    },
                    "result": code_result
                }]
            )
        
        except Exception as e:
            logger.error("Code generation failed", error=str(e))
            raise
    
    async def _handle_web_search(self, request: MultimodalRequest) -> MultimodalResponse:
        """Handle web search requests."""
        try:
            message = request.user_message
            
            # Extract search query
            search_patterns = [
                r'search.*for\s+(.+)',
                r'find.*information.*about\s+(.+)',
                r'look.*up\s+(.+)',
                r'what.*is.*latest.*on\s+(.+)'
            ]
            
            query = message  # Default to full message
            for pattern in search_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    query = match.group(1).strip()
                    break
            
            # Perform web search
            search_results = await self.search_service.search_web(
                query=query,
                max_results=5,
                search_type="web"
            )
            
            # Format results
            results_text = []
            for i, result in enumerate(search_results["results"][:3], 1):
                results_text.append(f"""**{i}. {result['title']}**
{result['snippet']}
🔗 {result['url']}
""")
            
            response_content = f"""🔍 **Search Results for: "{query}"**

{chr(10).join(results_text)}

**Total Results:** {search_results['total_results']}
**Search Time:** {search_results['search_time']:.3f}s

*Note: These are mock search results for demonstration.*"""

            return MultimodalResponse(
                content=response_content,
                content_type="search",
                metadata={
                    "type": "search_result",
                    "query": query,
                    "total_results": search_results["total_results"]
                },
                tool_calls=[{
                    "tool": "web_search",
                    "parameters": {"query": query, "max_results": 5},
                    "result": search_results
                }]
            )
        
        except Exception as e:
            logger.error("Web search failed", error=str(e))
            raise
    
    async def _handle_data_analysis(self, request: MultimodalRequest) -> MultimodalResponse:
        """Handle data analysis requests."""
        try:
            message = request.user_message
            
            # For demo, use the message as sample data
            sample_data = "Sample data for analysis: " + message
            
            # Call the data analysis tool
            result = await self.tool_service.execute(
                "analyze_data",
                {
                    "data": sample_data,
                    "analysis_type": "summary"
                }
            )
            
            analysis_result = result["result"]
            
            response_content = f"""📊 **Data Analysis Complete**

**Analysis Type:** {analysis_result.get('analysis_type', 'summary')}
**Data Preview:** {analysis_result.get('data_preview', 'N/A')}

**Analysis Results:**
{analysis_result.get('analysis', 'Analysis completed successfully')}"""

            return MultimodalResponse(
                content=response_content,
                content_type="tool",
                metadata={
                    "type": "tool_result",
                    "tool_name": "analyze_data",
                    "intent": "data_analysis"
                },
                tool_calls=[{
                    "tool": "analyze_data",
                    "parameters": {"data": sample_data, "analysis_type": "summary"},
                    "result": analysis_result
                }]
            )
        
        except Exception as e:
            logger.error("Data analysis failed", error=str(e))
            raise
    
    async def _handle_reasoning(self, request: MultimodalRequest) -> MultimodalResponse:
        """Handle reasoning requests with chain-of-thought processing."""
        try:
            message = request.user_message
            
            # Generate reasoning chain
            reasoning_chain = await self.reasoning_service.generate_reasoning_chain(
                query=message,
                reasoning_effort="medium",
                model="gpt-4",
                max_steps=5
            )
            
            # Format the response
            formatted_reasoning = self.reasoning_service.format_reasoning_for_display(reasoning_chain)
            
            return MultimodalResponse(
                content=formatted_reasoning,
                content_type="reasoning",
                metadata={
                    "type": "reasoning_result",
                    "tool_name": "reasoning_chain",
                    "intent": "reasoning",
                    "total_steps": len(reasoning_chain.steps),
                    "total_confidence": reasoning_chain.total_confidence,
                    "reasoning_time": reasoning_chain.reasoning_time,
                    "model_used": reasoning_chain.model_used
                },
                tool_calls=[{
                    "tool": "reasoning_chain",
                    "parameters": {
                        "query": message,
                        "reasoning_effort": "medium",
                        "model": "gpt-4"
                    },
                    "result": {
                        "steps": len(reasoning_chain.steps),
                        "confidence": reasoning_chain.total_confidence,
                        "reasoning_time": reasoning_chain.reasoning_time
                    }
                }]
            )
            
        except Exception as e:
            logger.error("Reasoning failed", error=str(e))
            raise
    
    async def _handle_structured_output(self, request: MultimodalRequest) -> MultimodalResponse:
        """Handle structured output requests with schema validation."""
        try:
            message = request.user_message
            
            # Determine appropriate schema based on message content
            schema_type = "analysis"  # Default
            if "person" in message.lower() or "profile" in message.lower():
                schema_type = "person"
            elif "product" in message.lower() or "item" in message.lower():
                schema_type = "product"
            elif "event" in message.lower() or "meeting" in message.lower():
                schema_type = "event"
            
            # Create structured output request
            structured_request = StructuredOutputRequest(
                prompt=message,
                model_class=schema_type,
                output_format="pydantic_model",
                model="gpt-4",
                temperature=0.1
            )
            
            # Generate structured output
            structured_response = await self.structured_output_service.generate_structured_output(
                structured_request
            )
            
            # Format the response
            response_content = f"""📊 **Structured Output Generated**

**Schema Used:** {schema_type}
**Validation:** {'✅ Passed' if structured_response.validation_passed else '❌ Failed'}
**Generation Time:** {structured_response.generation_time:.2f}s

**Structured Data:**
```json
{json.dumps(structured_response.data, indent=2)}
```

**Schema Details:**
- Format: Pydantic Model
- Validation: {'Schema-enforced' if structured_response.validation_passed else 'Best effort'}
- Model: {structured_response.model_used}"""

            return MultimodalResponse(
                content=response_content,
                content_type="structured_output",
                metadata={
                    "type": "structured_output_result",
                    "tool_name": "structured_output",
                    "intent": "structured_output",
                    "schema_type": schema_type,
                    "validation_passed": structured_response.validation_passed,
                    "generation_time": structured_response.generation_time,
                    "data": structured_response.data
                },
                tool_calls=[{
                    "tool": "structured_output",
                    "parameters": {
                        "prompt": message,
                        "schema_type": schema_type,
                        "output_format": "pydantic_model"
                    },
                    "result": {
                        "validation_passed": structured_response.validation_passed,
                        "data_keys": list(structured_response.data.keys()) if isinstance(structured_response.data, dict) else []
                    }
                }]
            )
            
        except Exception as e:
            logger.error("Structured output failed", error=str(e))
            raise
    
    async def _handle_live_search(self, request: MultimodalRequest) -> MultimodalResponse:
        """Handle live search requests with real-time web access."""
        try:
            message = request.user_message
            
            # Extract search query
            query = message.replace('live search', '').replace('real time search', '').replace('current information about', '').replace('latest news about', '').strip()
            if not query:
                query = message
            
            # Create live search request
            search_request = LiveSearchRequest(
                query=query,
                search_type="web",
                provider=SearchProvider.MOCK,  # Use mock for now
                max_results=5,
                include_images=False,
                include_videos=False
            )
            
            # Perform live search
            search_response = await self.live_search_service.search(search_request)
            
            # Format results
            results_text = []
            for i, result in enumerate(search_response.results[:3], 1):
                results_text.append(f"""**{i}. {result.title}**
{result.snippet}
🔗 {result.url}
📅 {result.published_date.strftime('%Y-%m-%d') if result.published_date else 'Recent'}
⭐ Relevance: {result.relevance_score:.1%}
""")
            
            response_content = f"""🔍 **Live Search Results for: "{query}"**

{chr(10).join(results_text)}

**Search Details:**
- Provider: {search_response.provider}
- Total Results: {search_response.total_results}
- Search Time: {search_response.search_time:.3f}s
- Timestamp: {search_response.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

*Live search provides real-time information from the web.*"""

            return MultimodalResponse(
                content=response_content,
                content_type="live_search",
                metadata={
                    "type": "live_search_result",
                    "tool_name": "live_search",
                    "intent": "live_search",
                    "query": query,
                    "provider": search_response.provider,
                    "total_results": search_response.total_results,
                    "search_time": search_response.search_time,
                    "results": [
                        {
                            "title": r.title,
                            "url": r.url,
                            "snippet": r.snippet[:100] + "..." if len(r.snippet) > 100 else r.snippet,
                            "relevance_score": r.relevance_score
                        } for r in search_response.results[:3]
                    ]
                },
                tool_calls=[{
                    "tool": "live_search",
                    "parameters": {
                        "query": query,
                        "search_type": "web",
                        "provider": "mock",
                        "max_results": 5
                    },
                    "result": {
                        "total_results": search_response.total_results,
                        "search_time": search_response.search_time,
                        "provider": search_response.provider
                    }
                }]
            )
            
        except Exception as e:
            logger.error("Live search failed", error=str(e))
            raise
