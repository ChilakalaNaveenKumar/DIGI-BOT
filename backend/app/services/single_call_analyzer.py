"""
Cost-Effective Streaming Stack

Analyzes streaming content every 2000 tokens to find components.
Returns component array with markdown for injection into the stream.

Key Features:
- Token-based analysis (every 2000 tokens)
- Component detection and generation
- Stream wrapper for real-time analysis
- Optimized for cost efficiency
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List, AsyncGenerator
import structlog
from pydantic import BaseModel

from app.services.component_analysis_service import ComponentAnalysisService, ComponentDecision
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)


class ComponentResult(BaseModel):
    """Result from component analysis."""
    component_type: str
    markdown: str
    data: Dict[str, Any]
    confidence: float
    injection_position: int


class StreamingAnalysis(BaseModel):
    """Analysis state for streaming content."""
    total_tokens: int = 0
    content_buffer: str = ""
    last_analysis_position: int = 0
    components_generated: List[ComponentResult] = []


class CostEffectiveStreamingStack:
    """
    Cost-effective streaming analysis that triggers component analysis
    every 2000 tokens instead of analyzing every chunk.
    """
    
    def __init__(self, token_threshold: int = 2000):
        self.token_threshold = token_threshold
        self.component_service = None
        self.analysis_state = StreamingAnalysis()
        
    async def initialize(self):
        """Initialize the component analysis service."""
        try:
            self.component_service = ComponentAnalysisService()
            await self.component_service.initialize()
            logger.info("CostEffectiveStreamingStack initialized")
        except Exception as e:
            logger.error("Failed to initialize streaming stack", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="STREAMING_STACK_INIT_ERROR",
                message="Failed to initialize streaming analysis stack"
            )
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 characters ≈ 1 token)."""
        return len(text) // 4
    
    async def wrap_stream(
        self, 
        original_stream: AsyncGenerator[Dict[str, Any], None],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Wrap the original stream with component analysis.
        
        Analyzes content every 2000 tokens and injects components.
        """
        
        async for chunk in original_stream:
            chunk_type = chunk.get("type")
            chunk_content = chunk.get("content", "")
            
            # Forward non-content chunks immediately
            if chunk_type != "content" and chunk_type != "tool_output":
                yield chunk
                continue
            
            # Add content to buffer
            if chunk_content:
                self.analysis_state.content_buffer += chunk_content
                self.analysis_state.total_tokens = self._estimate_tokens(
                    self.analysis_state.content_buffer
                )
            
            # Check if we should analyze (every 2000 tokens)
            tokens_since_last_analysis = (
                self.analysis_state.total_tokens - self.analysis_state.last_analysis_position
            )
            
            should_analyze = (
                tokens_since_last_analysis >= self.token_threshold or
                chunk.get("final", False)  # Always analyze final chunks
            )
            
            if should_analyze and self.component_service:
                # Analyze content for components
                components = await self._analyze_for_components(
                    self.analysis_state.content_buffer,
                    user_preferences
                )
                
                # Inject any new components found
                for component in components:
                    yield {
                        "type": "component",
                        "content": component.markdown,
                        "metadata": {
                            "component_type": component.component_type,
                            "confidence": component.confidence,
                            "data": component.data,
                            "injection_position": component.injection_position
                        }
                    }
                
                # Update analysis position
                self.analysis_state.last_analysis_position = self.analysis_state.total_tokens
                self.analysis_state.components_generated.extend(components)
            
            # Forward the original chunk
            yield chunk
    
    async def _analyze_for_components(
        self, 
        content: str, 
        user_preferences: Optional[Dict[str, Any]]
    ) -> List[ComponentResult]:
        """
        Analyze content for components.
        
        Returns list of components that should be injected.
        """
        try:
            # Get recent content (last 1000 characters for context)
            recent_content = content[-1000:] if len(content) > 1000 else content
            
            # Analyze with component service
            decision = await self.component_service.analyze_content(
                content=recent_content,
                context="Streaming analysis for component generation",
                user_preferences=user_preferences
            )
            
            # Convert decision to component result
            components = []
            if decision.decision == "GENERATE_NOW" and decision.markdown:
                component = ComponentResult(
                    component_type=decision.component_type or "unknown",
                    markdown=decision.markdown,
                    data=decision.extracted_data or {},
                    confidence=decision.confidence,
                    injection_position=len(content)
                )
                components.append(component)
                
                logger.info(
                    "Component generated",
                    component_type=component.component_type,
                    confidence=component.confidence
                )
            
            return components
            
        except Exception as e:
            logger.error("Component analysis failed", error=str(e))
            return []
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of analysis performed."""
        return {
            "total_tokens_processed": self.analysis_state.total_tokens,
            "components_generated": len(self.analysis_state.components_generated),
            "analysis_calls_made": self.analysis_state.total_tokens // self.token_threshold,
            "token_threshold": self.token_threshold
        }
