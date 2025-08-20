"""
Streaming Analysis Wrapper - Clean Rewrite

Simple, reliable approach:
1. Stream content normally
2. Hold complete messages until analysis is done
3. Force analysis at stream end
4. Send enhanced content as content update
5. Send complete message after analysis
"""

import asyncio
import time
from typing import Dict, Any, Optional, AsyncGenerator
import structlog

from app.services.batch_analysis_engine import BatchAnalysisEngine

logger = structlog.get_logger(__name__)


class StreamingAnalysisWrapper:
    """Clean, simple streaming analysis wrapper."""
    
    def __init__(self):
        self.batch_engine = None
        self.is_analyzing = False
        
    async def initialize(self):
        """Initialize the batch analysis engine."""
        try:
            self.batch_engine = BatchAnalysisEngine()
            await self.batch_engine.initialize()
            logger.info("StreamingAnalysisWrapper initialized")
        except Exception as e:
            logger.error("Failed to initialize StreamingAnalysisWrapper", error=str(e))
            raise
    
    async def wrap_stream(
        self,
        original_stream: AsyncGenerator[Dict[str, Any], None],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Simple stream wrapper:
        1. Forward all chunks except 'complete'
        2. Accumulate content for analysis
        3. At stream end: analyze content and send enhanced version
        4. Send complete message after analysis
        """
        try:
            accumulated_content = ""
            last_content_message = None
            held_complete_messages = []
            
            # Step 1: Stream normally and accumulate content
            async for chunk in original_stream:
                chunk_type = chunk.get("type")
                chunk_content = chunk.get("content", "")
                
                if chunk_type == "complete":
                    # Hold complete messages until analysis is done
                    held_complete_messages.append(chunk)
                    logger.info("Holding complete message until analysis finishes")
                    continue
                
                if chunk_type == "content" and chunk_content:
                    # Store content for analysis
                    accumulated_content = chunk_content  # Use latest content (already accumulated by orchestrator)
                    last_content_message = chunk
                
                # Forward all other chunks normally
                yield chunk
            
            # Step 2: Analyze accumulated content at stream end
            if accumulated_content and not self.is_analyzing:
                logger.info(f"Stream ended - analyzing {len(accumulated_content)} characters")
                
                # Send analysis status
                yield {
                    "type": "analysis_status",
                    "content": "Analyzing content for enhanced components...",
                    "metadata": {"status": "processing", "timestamp": time.time()}
                }
                
                # Run analysis
                self.is_analyzing = True
                enhanced_result = await self._analyze_content(accumulated_content, user_preferences)
                self.is_analyzing = False
                
                # Step 3: Send enhanced content with components injected
                if enhanced_result and last_content_message:
                    enhanced_content = enhanced_result.get("enhanced_content", accumulated_content)
                    components = enhanced_result.get("components", [])
                    
                    # Validate enhanced content (prevent duplication)
                    if len(enhanced_content) > len(accumulated_content) * 2:
                        logger.warning("Enhanced content seems duplicated, using original")
                        enhanced_content = accumulated_content
                    
                    # Inject components into content at their specified positions
                    if components:
                        enhanced_content = self._inject_components_into_content(enhanced_content, components)
                        logger.info(f"Injected {len(components)} components into content")
                    
                    # Send final enhanced content as content message
                    enhanced_message = last_content_message.copy()
                    enhanced_message["content"] = enhanced_content
                    yield enhanced_message
                    logger.info("Enhanced content with components sent as content update")
            
            # Step 4: Send held complete messages
            for complete_msg in held_complete_messages:
                yield complete_msg
                logger.info("Sent held complete message")
            
            # Fallback complete message if none were held
            if not held_complete_messages:
                yield {
                    "type": "complete",
                    "content": "Response completed",
                    "metadata": {"analysis_completed": True}
                }
                
        except Exception as e:
            logger.error("Stream wrapping failed", error=str(e))
            yield {
                "type": "error",
                "error": str(e),
                "metadata": {"wrapper_error": True}
            }
    
    async def _analyze_content(
        self, 
        content: str, 
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Analyze content and return enhanced version with components."""
        try:
            # Set content in batch engine
            self.batch_engine.batch_buffer = content
            self.batch_engine.token_counter.token_count = len(content) // 4
            
            # Run analysis
            result = await self.batch_engine.process_batch(user_preferences)
            
            if result and result.get("metadata", {}).get("processed"):
                components_count = len(result.get("components", []))
                logger.info(f"Analysis completed: {components_count} components generated")
                return result
            else:
                logger.info("Analysis completed with no enhancements")
                return None
                
        except Exception as e:
            logger.error("Content analysis failed", error=str(e))
            return None
    
    def _inject_components_into_content(self, content: str, components: list) -> str:
        """Inject component markdown into content at specified positions."""
        try:
            # Sort components by injection position (descending) to avoid position shifts
            sorted_components = sorted(components, key=lambda c: c.get('injection_position', 0), reverse=True)
            
            enhanced_content = content
            
            for component in sorted_components:
                injection_pos = component.get('injection_position', len(enhanced_content))
                markdown = component.get('markdown', '')
                
                # Ensure position is within bounds
                if injection_pos > len(enhanced_content):
                    injection_pos = len(enhanced_content)
                elif injection_pos < 0:
                    injection_pos = 0
                
                # Inject component markdown at the specified position
                enhanced_content = (
                    enhanced_content[:injection_pos] + 
                    "\n\n" + markdown + "\n\n" + 
                    enhanced_content[injection_pos:]
                )
                
                logger.debug(f"Injected component at position {injection_pos}: {component.get('component_type', 'unknown')}")
            
            return enhanced_content
            
        except Exception as e:
            logger.error("Failed to inject components", error=str(e))
            return content  # Return original content if injection fails
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            if self.batch_engine:
                await self.batch_engine.cleanup()
            logger.info("StreamingAnalysisWrapper cleaned up")
        except Exception as e:
            logger.error("Cleanup failed", error=str(e))