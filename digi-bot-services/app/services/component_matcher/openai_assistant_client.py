"""
OpenAI Assistant Client
Uses OpenAI's Assistant API with structured prompts for component matching
"""
import os
import asyncio
from typing import Dict, List, Optional, Any
from openai import AsyncOpenAI
import structlog

logger = structlog.get_logger(__name__)

class OpenAIAssistantClient:
    """Client for OpenAI's Assistant API with structured prompts"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # Get prompt details from environment
        self.prompt_id = os.getenv('OPENAI_PROMPT_ID', 'pmpt_68ac54284c0c81968cfefea4c34023f208a9d02ea796bb2d')
        self.prompt_version = os.getenv('prompt_version', '1')
        
        # Vector store ID from our created store
        self.vector_store_id = None
        self._load_vector_store_id()
    
    def _load_vector_store_id(self):
        """Load vector store ID from metadata"""
        try:
            metadata_file = "/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services/app/services/component_matcher/documents/vector_store_metadata.json"
            if os.path.exists(metadata_file):
                import json
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    self.vector_store_id = data.get('vector_store_id')
                logger.info("Loaded vector store ID", vector_store_id=self.vector_store_id)
            else:
                logger.warning("Vector store metadata not found")
        except Exception as e:
            logger.error("Failed to load vector store ID", error=str(e))
    
    async def query_components(self, query_text: str, documentation: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Query components using the structured prompt with proper input placeholders"""
        try:
            logger.info("Querying components with Responses API", 
                       query_length=len(query_text),
                       prompt_id=self.prompt_id,
                       vector_store_id=self.vector_store_id)
            
            # Prepare the request - try string input format first
            request_data = {
                "prompt": {
                    "id": self.prompt_id,
                    "version": self.prompt_version
                },
                "input": query_text  # Simple string input
            }
            
            # Add any additional parameters
            request_data.update(kwargs)
            
            # Make the API call
            response = await self.client.responses.create(**request_data)
            
            logger.info("Received response from OpenAI", 
                       response_type=type(response).__name__)
            
            # Parse the response using the proper Responses API format
            if hasattr(response, 'output_text'):
                # Responses API format - use output_text accessor
                content = response.output_text
                
                # Try to parse as JSON for structured output
                try:
                    import json
                    parsed_content = json.loads(content)
                    return {
                        "success": True,
                        "data": parsed_content,
                        "raw_content": content,
                        "usage": getattr(response, 'usage', None),
                        "response_id": getattr(response, 'id', None)
                    }
                except json.JSONDecodeError:
                    # Return as text if not JSON
                    return {
                        "success": True,
                        "data": {"text": content},
                        "raw_content": content,
                        "usage": getattr(response, 'usage', None),
                        "response_id": getattr(response, 'id', None)
                    }
            else:
                # Fallback - direct response format
                return {
                    "success": True,
                    "data": response,
                    "raw_content": str(response),
                    "usage": getattr(response, 'usage', None)
                }
                
        except Exception as e:
            logger.error("Failed to query components", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def query_components_streaming(self, query_text: str, documentation: Optional[str] = None, **kwargs):
        """Query components using streaming responses - fallback to non-streaming if streaming fails"""
        try:
            logger.info("Starting streaming query", 
                       query_length=len(query_text),
                       prompt_id=self.prompt_id)
            
            # For now, simulate streaming by doing a regular call and yielding chunks
            # This provides the same interface while we resolve the streaming API format
            result = await self.query_components(query_text, documentation, **kwargs)
            
            if result["success"]:
                # Simulate streaming by yielding the content in chunks
                content = result.get("raw_content", "")
                chunk_size = 50  # Characters per chunk
                
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i + chunk_size]
                    yield {
                        "type": "delta",
                        "delta": chunk,
                        "accumulated": content[:i + len(chunk)]
                    }
                    # Small delay to simulate real streaming
                    await asyncio.sleep(0.01)
                
                # Yield completion
                yield {
                    "type": "completed",
                    "data": result["data"],
                    "raw_content": result["raw_content"],
                    "usage": result.get("usage"),
                    "response_id": result.get("response_id")
                }
            else:
                yield {
                    "type": "error",
                    "error": result.get("error", "Unknown error")
                }
                        
        except Exception as e:
            logger.error("Streaming query failed", error=str(e))
            yield {
                "type": "error",
                "error": str(e)
            }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection and prompt"""
        try:
            logger.info("Testing OpenAI Assistant API connection")
            
            # Simple test query
            result = await self.query_components("test query for charts")
            
            if result["success"]:
                logger.info("Connection test successful")
                return {
                    "status": "success",
                    "prompt_id": self.prompt_id,
                    "prompt_version": self.prompt_version,
                    "vector_store_id": self.vector_store_id,
                    "test_result": result
                }
            else:
                logger.error("Connection test failed", error=result.get("error"))
                return {
                    "status": "error",
                    "error": result.get("error"),
                    "prompt_id": self.prompt_id,
                    "vector_store_id": self.vector_store_id
                }
                
        except Exception as e:
            logger.error("Connection test failed", error=str(e))
            return {
                "status": "error",
                "error": str(e)
            }

# Backward compatibility
ComponentMatcherClient = OpenAIAssistantClient
