"""
Streaming Analysis Wrapper

This service wraps the Claude streaming response and injects analysis placeholders
in real-time without blocking the main stream. It detects markdown headers as
boundaries and triggers parallel component analysis.
"""

import asyncio
import json
import time
import re
from typing import Dict, Any, Optional, List, AsyncGenerator
import structlog

from app.services.component_analysis_service import ComponentAnalysisService

logger = structlog.get_logger(__name__)


class PlaceholderManager:
    """Manages analysis placeholders in the streaming content."""
    
    def __init__(self):
        self.placeholders: Dict[str, Dict[str, Any]] = {}
        self.pending_analysis: Dict[str, Any] = {}
    
    def create_placeholder(self, block_content: str, position: int) -> str:
        """Create a new placeholder for analysis."""
        placeholder_id = f"PH_{int(time.time() * 1000)}_{len(self.placeholders)}"
        
        self.placeholders[placeholder_id] = {
            'status': 'analyzing',
            'created_at': time.time(),
            'block_content': block_content,
            'position': position,
            'component': None
        }
        
        logger.info(f"Created placeholder {placeholder_id} for block at position {position}")
        return placeholder_id
    
    def fill_placeholder(self, placeholder_id: str, component: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fill a placeholder with analysis results."""
        if placeholder_id not in self.placeholders:
            logger.error(f"Placeholder {placeholder_id} not found")
            return None
        
        self.placeholders[placeholder_id]['component'] = component
        self.placeholders[placeholder_id]['status'] = 'ready'
        
        logger.info(f"Filled placeholder {placeholder_id} with {component.get('type', 'unknown')} component")
        
        return {
            "type": "component_replacement",
            "placeholder_id": placeholder_id,
            "component": component,
            "metadata": {
                "analysis_time": time.time() - self.placeholders[placeholder_id]['created_at']
            }
        }
    
    def get_placeholder_status(self, placeholder_id: str) -> Optional[str]:
        """Get the status of a placeholder."""
        return self.placeholders.get(placeholder_id, {}).get('status')


class StreamingAnalysisWrapper:
    """
    Wraps Claude streaming responses with real-time analysis and placeholder injection.
    
    This wrapper:
    1. Streams content from Claude without interruption
    2. Detects markdown header boundaries
    3. Injects analysis placeholders at boundaries
    4. Runs component analysis in parallel
    5. Fills placeholders with results when ready
    """
    
    def __init__(self):
        self.placeholder_manager = PlaceholderManager()
        self.component_analysis_service = None
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.analysis_queue = asyncio.Queue()
        self.completed_components_queue = asyncio.Queue()
        self.analysis_worker_task = None
        self.shutdown_event = asyncio.Event()
        
    async def initialize(self):
        """Initialize the wrapper and start background workers."""
        # Initialize component analysis service
        self.component_analysis_service = ComponentAnalysisService()
        await self.component_analysis_service.initialize()
        
        # Start analysis worker
        self.analysis_worker_task = asyncio.create_task(self._analysis_worker())
        
        logger.info("Streaming Analysis Wrapper initialized")
    
    async def wrap_stream(
        self,
        original_stream: AsyncGenerator[Dict[str, Any], None],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Wrap the original stream with analysis capabilities.
        
        Args:
            original_stream: The original Claude streaming response
            user_preferences: User preferences for component analysis
            
        Yields:
            Enhanced stream chunks with placeholders and components
        """
        try:
            accumulated_content = ""
            last_header_position = 0
            current_block_content = ""
            position_counter = 0
            
            async for chunk in original_stream:
                chunk_type = chunk.get("type")
                chunk_content = chunk.get("content", "")
                
                # Always forward the original chunk first (no blocking)
                yield chunk
                
                # Only process content chunks for analysis
                if chunk_type == "content" and chunk_content:
                    accumulated_content += chunk_content
                    current_block_content += chunk_content
                    position_counter += len(chunk_content)
                    
                    # Check for header boundaries
                    new_headers = self._detect_new_headers(accumulated_content, last_header_position)
                    
                    for header_match in new_headers:
                        header_position = header_match['position']
                        
                        # Extract the block content before this header
                        if current_block_content.strip():
                            block_content = current_block_content[:header_match['relative_position']].strip()
                            
                            if self._has_potential_for_analysis(block_content):
                                # Create placeholder
                                placeholder_id = self.placeholder_manager.create_placeholder(
                                    block_content, header_position
                                )
                                
                                # Inject placeholder chunk
                                placeholder_chunk = {
                                    "type": "placeholder",
                                    "placeholder_id": placeholder_id,
                                    "content": "🔄 Analyzing data...",
                                    "metadata": {
                                        "position": header_position,
                                        "block_preview": block_content[:100] + "..." if len(block_content) > 100 else block_content
                                    }
                                }
                                yield placeholder_chunk
                                
                                # Queue for analysis (non-blocking)
                                await self.analysis_queue.put({
                                    'placeholder_id': placeholder_id,
                                    'content': block_content,
                                    'user_preferences': user_preferences
                                })
                        
                        # Reset for next block
                        current_block_content = current_block_content[header_match['relative_position']:]
                        last_header_position = header_position
                    
                    # Check for completed components (non-blocking)
                    while not self.completed_components_queue.empty():
                        try:
                            completed_chunk = self.completed_components_queue.get_nowait()
                            yield completed_chunk
                        except asyncio.QueueEmpty:
                            break
            
            # Handle final block if it has potential
            if current_block_content.strip() and self._has_potential_for_analysis(current_block_content):
                placeholder_id = self.placeholder_manager.create_placeholder(
                    current_block_content, position_counter
                )
                
                placeholder_chunk = {
                    "type": "placeholder",
                    "placeholder_id": placeholder_id,
                    "content": "🔄 Analyzing final section...",
                    "metadata": {"position": position_counter, "final_block": True}
                }
                yield placeholder_chunk
                
                await self.analysis_queue.put({
                    'placeholder_id': placeholder_id,
                    'content': current_block_content,
                    'user_preferences': user_preferences
                })
            
            # Wait for any remaining analysis to complete
            logger.info("Stream ended, waiting for pending analyses...")
            
            # Check for completed components for up to 15 seconds
            max_wait_cycles = 150  # 15 seconds at 0.1s per cycle
            wait_cycles = 0
            pending_placeholders = len([p for p in self.placeholder_manager.placeholders.values() 
                                      if p['status'] == 'analyzing'])
            
            while wait_cycles < max_wait_cycles and pending_placeholders > 0:
                # Check for completed components
                while not self.completed_components_queue.empty():
                    try:
                        completed_chunk = self.completed_components_queue.get_nowait()
                        yield completed_chunk
                        logger.info(f"Yielded late component: {completed_chunk.get('type')}")
                    except asyncio.QueueEmpty:
                        break
                
                # Update pending count
                pending_placeholders = len([p for p in self.placeholder_manager.placeholders.values() 
                                          if p['status'] == 'analyzing'])
                
                if pending_placeholders == 0:
                    break
                    
                await asyncio.sleep(0.1)
                wait_cycles += 1
            
            # Final check for any remaining components
            while not self.completed_components_queue.empty():
                try:
                    completed_chunk = self.completed_components_queue.get_nowait()
                    yield completed_chunk
                    logger.info(f"Yielded final component: {completed_chunk.get('type')}")
                except asyncio.QueueEmpty:
                    break
                    
            if pending_placeholders > 0:
                logger.warning(f"Stream ending with {pending_placeholders} pending analyses")
            
        except Exception as e:
            logger.error("Streaming wrapper error", error=str(e))
            yield {
                "type": "error",
                "content": f"Streaming analysis error: {str(e)}",
                "final": True
            }
    
    def _detect_new_headers(self, content: str, last_position: int) -> List[Dict[str, Any]]:
        """Detect new headers since the last position."""
        new_headers = []
        
        for match in self.header_pattern.finditer(content[last_position:]):
            header_level = len(match.group(1))
            header_title = match.group(2).strip()
            absolute_position = last_position + match.start()
            relative_position = match.start()
            
            new_headers.append({
                'level': header_level,
                'title': header_title,
                'position': absolute_position,
                'relative_position': relative_position,
                'match': match
            })
        
        return new_headers
    
    def _has_potential_for_analysis(self, content: str) -> bool:
        """Quick check if content has potential for component generation."""
        if len(content.strip()) < 50:  # Too short
            return False
        
        # Look for data patterns
        data_patterns = [
            r'\d+[%$]',  # Percentages or currency
            r'\d+\.\d+[%$]',  # Decimal percentages or currency
            r'Q[1-4]',  # Quarters
            r'\b\d+k?\b',  # Numbers with optional 'k'
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',  # Months
            r'\d+:\s*\$?\d+',  # Ratio patterns like "Q1: $100k"
        ]
        
        for pattern in data_patterns:
            if len(re.findall(pattern, content, re.IGNORECASE)) >= 2:
                return True
        
        return False
    
    async def _analysis_worker(self):
        """Background worker that processes analysis requests."""
        logger.info("Analysis worker started")
        
        while not self.shutdown_event.is_set():
            try:
                # Wait for analysis request with timeout to check shutdown
                try:
                    analysis_request = await asyncio.wait_for(self.analysis_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue  # Check shutdown and try again
                
                placeholder_id = analysis_request['placeholder_id']
                content = analysis_request['content']
                user_preferences = analysis_request.get('user_preferences', {})
                
                logger.info(f"Processing analysis for placeholder {placeholder_id}")
                
                # Perform component analysis
                logger.info(f"Analyzing content for {placeholder_id}: {content[:100]}...")
                try:
                    decision = await asyncio.wait_for(
                        self.component_analysis_service.analyze_content(
                            content=content,
                            context="Streaming header-based analysis",
                            user_preferences=user_preferences
                        ),
                        timeout=10.0  # 10 second timeout
                    )
                    logger.info(f"Analysis result for {placeholder_id}: {decision.decision if decision else 'None'} (confidence: {decision.confidence if decision else 'N/A'})")
                except asyncio.TimeoutError:
                    logger.error(f"Analysis timed out for {placeholder_id}")
                    decision = None
                except Exception as analysis_error:
                    logger.error(f"Analysis failed for {placeholder_id}: {str(analysis_error)}")
                    decision = None
                
                if decision and decision.decision == 'GENERATE_NOW' and decision.markdown:
                    # Create component
                    component = {
                        'type': decision.component_type,
                        'markdown': decision.markdown,
                        'confidence': decision.confidence,
                        'reasoning': decision.reasoning,
                        'extracted_data': decision.extracted_data
                    }
                    
                    # Fill placeholder
                    replacement_chunk = self.placeholder_manager.fill_placeholder(placeholder_id, component)
                    
                    # Queue the replacement chunk for the main stream
                    if replacement_chunk:
                        await self.completed_components_queue.put(replacement_chunk)
                    
                    logger.info(f"Analysis completed for {placeholder_id}: {decision.component_type}")
                else:
                    # Mark as no component needed (remove placeholder)
                    no_component_chunk = {
                        "type": "placeholder_removal",
                        "placeholder_id": placeholder_id,
                        "reasoning": decision.reasoning if decision else 'Analysis failed'
                    }
                    
                    self.placeholder_manager.fill_placeholder(placeholder_id, {
                        'type': 'no_component',
                        'reasoning': decision.reasoning if decision else 'Analysis failed'
                    })
                    
                    await self.completed_components_queue.put(no_component_chunk)
                    
                    logger.info(f"No component generated for {placeholder_id}")
                
                self.analysis_queue.task_done()
                
            except Exception as e:
                logger.error("Analysis worker error", error=str(e))
                await asyncio.sleep(1)  # Brief pause before retrying
        
        logger.info("Analysis worker shutting down")
    

    
    async def cleanup(self):
        """Cleanup resources."""
        if self.analysis_worker_task:
            # Signal shutdown and wait for worker to finish current tasks
            logger.info("Signaling shutdown to analysis worker...")
            self.shutdown_event.set()
            
            try:
                # Wait for worker to finish gracefully
                await asyncio.wait_for(self.analysis_worker_task, timeout=15.0)
            except asyncio.TimeoutError:
                logger.warning("Analysis worker timeout, canceling...")
                self.analysis_worker_task.cancel()
                try:
                    await self.analysis_worker_task
                except asyncio.CancelledError:
                    pass
        
        if self.component_analysis_service:
            await self.component_analysis_service.cleanup()
        
        logger.info("Streaming Analysis Wrapper cleaned up")
