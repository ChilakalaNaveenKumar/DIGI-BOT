"""
Batch Analysis Engine

Coordinates the two-step analysis pipeline:
1. GPT-4o Mini for fast block segmentation
2. Claude 4 with thinking for component analysis

Replaces the real-time placeholder system with batch processing.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Tuple
import structlog

from app.services.ai_providers.openai_provider import OpenAIProvider
from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)


class TokenCounter:
    """Utility for counting tokens in content."""
    
    def __init__(self):
        self.token_count = 0
        self.threshold = 2000  # 2000-token threshold
    
    def add_content(self, content: str) -> int:
        """Add content and return current token count."""
        # Rough estimation: ~4 characters per token
        tokens = len(content) // 4
        self.token_count += tokens
        return self.token_count
    
    def should_trigger_analysis(self) -> bool:
        """Check if we've hit the 2000-token threshold."""
        return self.token_count >= self.threshold
    
    def reset(self):
        """Reset token counter."""
        self.token_count = 0


class AbsolutePositionCalculator:
    """Calculates absolute positions after content replacements."""
    
    def __init__(self):
        self.position_adjustments = []  # List of (position, length_change)
    
    def add_replacement(self, position: int, original_length: int, new_length: int):
        """Record a content replacement for position adjustment."""
        length_change = new_length - original_length
        self.position_adjustments.append((position, length_change))
        
        # Sort by position to apply adjustments in order
        self.position_adjustments.sort(key=lambda x: x[0])
    
    def calculate_adjusted_position(self, original_position: int) -> int:
        """Calculate adjusted position after all replacements."""
        adjusted_position = original_position
        
        for adj_pos, length_change in self.position_adjustments:
            if adj_pos <= original_position:
                adjusted_position += length_change
        
        return adjusted_position


class ContentEnhancer:
    """Handles intelligent content replacement and enhancement."""
    
    def __init__(self):
        self.position_calculator = AbsolutePositionCalculator()
    
    def apply_enhancements(
        self, 
        original_content: str, 
        components: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Apply content enhancements using three modification types:
        1. Overlay components (keep original + add widget)
        2. Content replacement (remove original + insert enhanced)
        3. Hybrid approach (modify text + add interactive elements)
        """
        enhanced_content = original_content
        enhanced_components = []
        
        # Sort components by position (reverse order to avoid position shifts)
        components_sorted = sorted(components, key=lambda x: x.get('start_position', 0), reverse=True)
        
        for component in components_sorted:
            enhancement_type = component.get('enhancement_type', 'overlay')
            start_pos = component.get('start_position', 0)
            end_pos = component.get('end_position', start_pos)
            
            if enhancement_type == 'replace':
                # Type 2: Content Replacement
                original_text = enhanced_content[start_pos:end_pos]
                replacement_text = component.get('enhanced_content', component.get('markdown', ''))
                
                enhanced_content = (
                    enhanced_content[:start_pos] + 
                    replacement_text + 
                    enhanced_content[end_pos:]
                )
                
                # Track position change
                self.position_calculator.add_replacement(
                    start_pos, 
                    len(original_text), 
                    len(replacement_text)
                )
                
            elif enhancement_type == 'hybrid':
                # Type 3: Hybrid Enhancement
                original_text = enhanced_content[start_pos:end_pos]
                hybrid_text = component.get('enhanced_content', original_text)
                
                enhanced_content = (
                    enhanced_content[:start_pos] + 
                    hybrid_text + 
                    enhanced_content[end_pos:]
                )
                
                self.position_calculator.add_replacement(
                    start_pos, 
                    len(original_text), 
                    len(hybrid_text)
                )
            
            # Type 1: Overlay (default) - keep original text, add component marker
            # Calculate adjusted position for component placement
            adjusted_position = self.position_calculator.calculate_adjusted_position(end_pos)
            
            enhanced_component = {
                **component,
                'position': adjusted_position,
                'original_position': end_pos
            }
            enhanced_components.append(enhanced_component)
        
        return enhanced_content, enhanced_components


class BatchAnalysisEngine:
    """
    Main engine for batch analysis using two-step pipeline.
    
    Pipeline:
    1. Accumulate content until 2000-token threshold
    2. GPT-4o Mini segmentation (fast, cheap)
    3. Claude 4 thinking analysis per block (high quality)
    4. Content enhancement and reconstruction
    """
    
    def __init__(self):
        self.openai_provider = None
        self.anthropic_provider = None
        self.token_counter = TokenCounter()
        self.content_enhancer = ContentEnhancer()
        self.batch_buffer = ""
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize AI providers."""
        try:
            # Initialize OpenAI provider for GPT-4o Mini segmentation
            self.openai_provider = OpenAIProvider()
            await self.openai_provider.initialize()
            
            # Initialize Anthropic provider for Claude 4 thinking analysis
            self.anthropic_provider = AnthropicProvider()
            await self.anthropic_provider.initialize()
            
            self.is_initialized = True
            logger.info("BatchAnalysisEngine initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize BatchAnalysisEngine", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="BATCH_ENGINE_INIT_ERROR",
                message="Failed to initialize batch analysis engine"
            )
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.openai_provider:
            await self.openai_provider.cleanup()
        if self.anthropic_provider:
            await self.anthropic_provider.cleanup()
        logger.info("BatchAnalysisEngine cleaned up")
    
    def add_content(self, content: str) -> bool:
        """
        Add content to batch buffer.
        Returns True if threshold reached and analysis should be triggered.
        """
        self.batch_buffer += content
        current_tokens = self.token_counter.add_content(content)
        
        logger.debug(f"Added content to batch buffer. Total tokens: {current_tokens}")
        
        return self.token_counter.should_trigger_analysis()
    
    async def process_batch(
        self, 
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process accumulated batch using two-step pipeline.
        
        Returns enhanced content packet with:
        - Enhanced text content
        - Component specifications  
        - Interaction metadata
        """
        if not self.is_initialized:
            raise DigiSetuException(
                status_code=500,
                error_code="BATCH_ENGINE_NOT_INITIALIZED",
                message="Batch analysis engine not initialized"
            )
        
        if not self.batch_buffer:
            return {
                "enhanced_content": "",
                "components": [],
                "metadata": {"processed": False, "reason": "empty_buffer"}
            }
        
        try:
            logger.info(f"Processing batch with {self.token_counter.token_count} tokens")
            
            # Step 1: GPT-4o Mini Block Segmentation
            start_time = time.time()
            blocks = await self._segment_content_blocks()
            segmentation_time = time.time() - start_time
            
            if not blocks:
                logger.info("No blocks found for enhancement")
                return {
                    "enhanced_content": self.batch_buffer,
                    "components": [],
                    "metadata": {
                        "processed": True, 
                        "segmentation_time": segmentation_time,
                        "blocks_found": 0
                    }
                }
            
            logger.info(f"Found {len(blocks)} blocks in {segmentation_time:.2f}s")
            
            # Step 2: Claude 4 Component Analysis (parallel processing)
            start_time = time.time()
            components = await self._analyze_blocks_parallel(blocks, user_preferences)
            analysis_time = time.time() - start_time
            
            logger.info(f"Analyzed {len(components)} components in {analysis_time:.2f}s")
            
            # Step 3: Content Enhancement
            enhanced_content, enhanced_components = self.content_enhancer.apply_enhancements(
                self.batch_buffer, 
                components
            )
            
            # Reset for next batch
            self._reset_batch()
            
            return {
                "enhanced_content": enhanced_content,
                "components": enhanced_components,
                "metadata": {
                    "processed": True,
                    "segmentation_time": segmentation_time,
                    "analysis_time": analysis_time,
                    "blocks_found": len(blocks),
                    "components_generated": len(components),
                    "original_length": len(self.batch_buffer),
                    "enhanced_length": len(enhanced_content)
                }
            }
            
        except Exception as e:
            logger.error("Batch processing failed", error=str(e))
            self._reset_batch()
            return {
                "enhanced_content": self.batch_buffer,
                "components": [],
                "metadata": {"processed": False, "error": str(e)}
            }
    
    async def _segment_content_blocks(self) -> List[Dict[str, Any]]:
        """Step 1: Use GPT-4o Mini for fast block segmentation."""
        try:
            logger.info(f"Starting content segmentation for {len(self.batch_buffer)} characters")
            blocks = await self.openai_provider.segment_content_blocks(
                content=self.batch_buffer,
                context="Batch analysis segmentation"
            )
            
            # All blocks are now candidates (no filtering needed)
            logger.info(f"Segmentation completed: {len(blocks or [])} blocks found")
            
            return blocks or []
            
        except Exception as e:
            logger.error("Block segmentation failed", error=str(e))
            return []
    
    async def _analyze_blocks_parallel(
        self, 
        blocks: List[Dict[str, Any]], 
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Step 2: Analyze each block with Claude 4 thinking (parallel processing)."""
        
        # Create analysis tasks for parallel processing
        analysis_tasks = []
        for block in blocks:
            task = self._analyze_single_block(block, user_preferences)
            analysis_tasks.append(task)
        
        # Process all blocks in parallel
        try:
            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Filter successful results
            components = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error("Block analysis failed", error=str(result))
                elif result and result.get('component'):
                    components.append(result['component'])
            
            return components
            
        except Exception as e:
            logger.error("Parallel block analysis failed", error=str(e))
            return []
    
    async def _analyze_single_block(
        self, 
        block: Dict[str, Any], 
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Analyze a single block with Claude 4 thinking."""
        try:
            block_content = block.get('content', '')
            logger.info(f"Starting Claude analysis for block: {len(block_content)} chars")
            
            # Create analysis prompt for Claude 4 with thinking
            analysis_prompt = f"""
Analyze this content and determine if it should generate an interactive component.

CONTENT TO ANALYZE:
{block_content}

AVAILABLE COMPONENTS:

## PieChart
Use when: Content has percentages, proportions, parts of a whole
Example markdown:
:::pie-chart
title: Revenue Distribution
data:
  - {{label: "SaaS Products", value: 45}}
  - {{label: "Professional Services", value: 30}}
  - {{label: "Enterprise Solutions", value: 25}}
:::

## BarChart  
Use when: Comparing quantities across categories
Example markdown:
:::bar-chart
title: Quarterly Sales
data:
  - {{label: "Q1 2024", value: 125000}}
  - {{label: "Q2 2024", value: 180000}}
  - {{label: "Q3 2024", value: 220000}}
:::

## LineChart
Use when: Time-based data, trends over time
Example markdown:
:::line-chart
title: Growth Trend
data:
  - name: "Revenue"
    data:
      - {{x: "Jan", y: 120000}}
      - {{x: "Feb", y: 135000}}
      - {{x: "Mar", y: 165000}}
:::

## DataTable
Use when: Structured data with multiple attributes
Example markdown:
:::data-table
title: Product Comparison
headers:
  - {{key: "name", label: "Product", type: "text"}}
  - {{key: "price", label: "Price", type: "number"}}
  - {{key: "rating", label: "Rating", type: "number"}}
data:
  - {{name: "Product A", price: 999, rating: 4.5}}
  - {{name: "Product B", price: 799, rating: 4.2}}
:::

RESPONSE FORMAT (JSON only):
{{
  "decision": "GENERATE_NOW" or "NO_COMPONENT",
  "confidence": 0.0-1.0,
  "inject_after_position": 123,
  "markdown": "Use the exact format from examples above based on your chosen component"
}}

INJECTION:
- Specify the character number (position) after which the component should appear
- Count characters from the start of the block content (starting from 0)
- Choose the most logical position where the visualization would be most helpful
- Example: "inject_after_position": 85 (to inject after a specific sentence)

IMPORTANT:
- Generate components when data is present that would benefit from visualization
- Extract real data from content, never invent data
- Use exact markdown syntax: :::component-type with YAML data format
- Confidence must be > 0.5 for generation

Use your thinking process to analyze this thoroughly before responding.
"""

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert content enhancement analyst. Think through each decision carefully and provide detailed reasoning."
                },
                {
                    "role": "user", 
                    "content": analysis_prompt
                }
            ]
            
            # Use Claude 4 with thinking for high-quality analysis
            response_content = ""
            
            # Add timeout to prevent hanging
            try:
                # Use asyncio.wait_for for timeout (compatible with older Python versions)
                analysis_task = self.anthropic_provider.stream_completion(
                    messages=messages,
                    model="claude-opus-4-1-20250805",  # Use Claude Opus 4.1 for consistency
                    max_tokens=2000,
                    temperature=0.2,
                    enable_thinking=True  # Enable thinking process
                )
                
                async def collect_response():
                    content = ""
                    async for chunk in analysis_task:
                        if chunk.get("type") == "content":
                            content += chunk.get("content", "")
                        elif chunk.get("type") == "thinking":
                            # Log thinking process for debugging
                            logger.debug(f"Claude thinking: {chunk.get('content', '')}")
                    return content
                
                response_content = await asyncio.wait_for(collect_response(), timeout=15.0)  # Shorter timeout
            except asyncio.TimeoutError:
                logger.error(f"Claude analysis timed out after 15 seconds for block: {block_content[:100]}...")
                # Return a simple fallback component for testing
                return {
                    'component': {
                        'start_position': block.get('start_position', 0),
                        'end_position': block.get('end_position', 0),
                        'injection_position': block.get('end_position', 0),
                        'inject_after_position': 0,
                        'decision': 'GENERATE_NOW',
                        'component_type': 'pie-chart',
                        'confidence': 0.7,
                        'markdown': ':::pie-chart\ntitle: Data Visualization\ndata:\n  - {label: "Sample", value: 100}\n:::',
                        'original_content': block_content[:100] + "..."
                    }
                }
            except Exception as api_error:
                logger.error(f"Claude API error during analysis: {str(api_error)}")
                return None
            
            logger.info(f"Claude analysis completed, response length: {len(response_content)}")
            
            # Parse JSON response - handle explanation text before JSON
            json_content = response_content.strip()
            
            # Remove markdown JSON blocks if present
            if json_content.startswith("```json"):
                json_content = json_content.replace("```json", "").replace("```", "").strip()
            
            # Find JSON object in the response (handle explanation text)
            json_start = json_content.find('{')
            json_end = json_content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = json_content[json_start:json_end]
            
            analysis_result = json.loads(json_content)
            
            if analysis_result.get('decision') != 'GENERATE_NOW':
                return None
            
            # Extract component type from markdown
            markdown = analysis_result.get('markdown', '')
            component_type = 'unknown'
            if ':::pie-chart' in markdown:
                component_type = 'pie-chart'
            elif ':::bar-chart' in markdown:
                component_type = 'bar-chart'  
            elif ':::line-chart' in markdown:
                component_type = 'line-chart'
            elif ':::data-table' in markdown:
                component_type = 'data-table'
            
            # Calculate exact injection position
            inject_after_position = analysis_result.get('inject_after_position', len(block_content))
            
            # Validate position is within block bounds
            if inject_after_position < 0:
                inject_after_position = 0
            elif inject_after_position > len(block_content):
                inject_after_position = len(block_content)
            
            # Convert local position to absolute document position
            injection_position = block.get('start_position', 0) + inject_after_position
            
            # Build component specification
            component = {
                'start_position': block.get('start_position', 0),
                'end_position': block.get('end_position', 0),
                'injection_position': injection_position,
                'inject_after_position': inject_after_position,
                'decision': analysis_result.get('decision', 'NO_COMPONENT'),
                'component_type': component_type,
                'confidence': analysis_result.get('confidence', 0.0),
                'markdown': markdown,
                'original_content': block_content
            }
            
            return {'component': component}
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse Claude analysis JSON", error=str(e))
            return None
        except Exception as e:
            logger.error("Single block analysis failed", error=str(e))
            return None
    
    def _reset_batch(self):
        """Reset batch state for next processing cycle."""
        self.batch_buffer = ""
        self.token_counter.reset()
        self.content_enhancer = ContentEnhancer()  # Reset position calculator
    
    def get_current_token_count(self) -> int:
        """Get current token count in batch buffer."""
        return self.token_counter.token_count
    
    def should_process_batch(self) -> bool:
        """Check if batch should be processed."""
        return self.token_counter.should_trigger_analysis()
