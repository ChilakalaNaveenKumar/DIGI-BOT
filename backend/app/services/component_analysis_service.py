"""
Component Analysis Service

AI-powered service for analyzing content and determining when to generate
enhanced components like charts and tables.
"""

import json
import re
from typing import Dict, Any, Optional, List, Tuple

import structlog
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.exceptions import DigiSetuException
from app.services.ai_providers.anthropic_provider import AnthropicProvider

logger = structlog.get_logger(__name__)
settings = get_settings()


class ComponentDecision(BaseModel):
    """Model for component generation decision."""
    decision: str  # "GENERATE_NOW" or "NO_COMPONENT"
    component_type: Optional[str] = None
    confidence: float
    reasoning: str
    markdown: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None


class ComponentAnalysisService:
    """Service for AI-powered component analysis and generation."""
    
    def __init__(self):
        self.anthropic_provider = None
        self.component_docs = self._load_component_documentation()
    
    async def initialize(self):
        """Initialize the service with AI provider."""
        try:
            self.anthropic_provider = AnthropicProvider()
            await self.anthropic_provider.initialize()
            logger.info("Component Analysis Service initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Component Analysis Service", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="COMPONENT_ANALYSIS_INIT_ERROR",
                message="Failed to initialize component analysis service"
            )
    
    def _load_component_documentation(self) -> str:
        """Load component documentation for AI prompts."""
        return """
AVAILABLE ENHANCED COMPONENTS:

## PieChart
Purpose: Display percentage-based data as circular segments
Best for: Market share, demographics, survey results, categorical percentages
Data format: [{"label": "Instagram", "value": 45, "percentage": 45}]
Markdown: :::pie-chart
When to use: Content mentions percentages, proportions, parts of a whole

## BarChart
Purpose: Compare quantities across categories
Best for: Performance metrics, comparisons, rankings, time-based data
Data format: [{"label": "Q1", "value": 100000}]
Markdown: :::bar-chart
When to use: Comparative data, performance metrics, quantity comparisons

## LineChart
Purpose: Show trends and changes over time
Best for: Time series, growth trends, performance tracking
Data format: [{"name": "Sales", "data": [{"x": "Jan", "y": 1200}]}]
Markdown: :::line-chart
When to use: Time-based progression, trend analysis, growth patterns

## DataTable
Purpose: Present structured data with sorting/filtering
Best for: Detailed datasets, comparison tables, lists with attributes
Data format: headers + rows array
Markdown: :::data-table
When to use: Structured lists, comparison data, detailed specifications

DECISION RULES:
- GENERATE_NOW: Clear, complete dataset ready for visualization (confidence > 0.7)
- NO_COMPONENT: No data patterns or unsuitable for visualization
- Extract actual data from content, don't make up data
- Use appropriate component type based on data structure

ANALYSIS CONTEXT:
You are analyzing content in real-time as it streams. Each chunk may be:
- Complete data (ready to visualize)
- Incomplete data (might need more context)
- Non-data content (ignore for components)
"""
    
    async def analyze_content(
        self,
        content: str,
        context: Optional[str] = None,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> ComponentDecision:
        """
        Analyze content to determine if enhanced components should be generated.
        
        Args:
            content: The text content to analyze
            context: Optional context about the content
            user_preferences: User preferences for component generation
            
        Returns:
            ComponentDecision with analysis results
        """
        try:
            # Quick pre-filter: if no data patterns, return immediately
            if not self._has_data_patterns(content):
                return ComponentDecision(
                    decision="NO_COMPONENT",
                    confidence=1.0,
                    reasoning="No data patterns detected"
                )
            
            # Prepare the analysis prompt
            prompt = self._build_analysis_prompt(content, context, user_preferences)
            
            # Get AI analysis
            response = await self._get_ai_analysis(prompt)
            
            # Parse and validate the response
            decision = self._parse_ai_response(response, content)
            
            logger.info(
                "Content analysis completed",
                decision=decision.decision,
                component_type=decision.component_type,
                confidence=decision.confidence
            )
            
            return decision
            
        except Exception as e:
            logger.error("Content analysis failed", error=str(e))
            return ComponentDecision(
                decision="NO_COMPONENT",
                confidence=0.0,
                reasoning="Analysis error"
            )
    
    def _build_analysis_prompt(
        self,
        content: str,
        context: Optional[str],
        user_preferences: Optional[Dict[str, Any]]
    ) -> str:
        """Build the AI analysis prompt."""
        
        prompt = f"""
You are an expert at analyzing content and determining when to generate interactive components.

{self.component_docs}

TASK: Analyze the following content and determine if an enhanced component should be generated.

CONTENT TO ANALYZE:
{content}

{f"CONTEXT: {context}" if context else ""}

ANALYSIS REQUIREMENTS:
1. Look for data patterns (percentages, quantities, comparisons, time series, structured lists)
2. Determine if data is suitable for visualization or interactive presentation
3. Extract actual data from the content (don't fabricate data)
4. Choose the most appropriate component type
5. Generate proper markdown syntax if component should be created

RESPONSE FORMAT (JSON only):
{{
  "decision": "GENERATE_NOW" or "NO_COMPONENT",
  "component_type": "pie-chart" | "bar-chart" | "line-chart" | "data-table" | null,
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation of decision",
  "markdown": "Component markdown if generating" | null,
  "extracted_data": {{"raw_data": "extracted data structure"}} | null
}}

IMPORTANT: 
- Generate components when data is present that would benefit from visualization
- Confidence must be > 0.5 for generation (be generous with useful data)
- Use exact markdown syntax from documentation
- Extract real data from content, never invent data
- Prefer generating components over rejecting - users benefit from visual data presentation
"""
        
        return prompt
    
    async def _get_ai_analysis(self, prompt: str) -> str:
        """Get AI analysis using Anthropic provider."""
        try:
            messages = [{"role": "user", "content": prompt}]
            
            # Use the anthropic provider to get analysis
            response = await self.anthropic_provider.generate_completion(
                messages=messages,
                model="claude-opus-4-1-20250805",
                max_tokens=2000,
                temperature=0.1  # Low temperature for consistent analysis
            )
            
            # Extract content from Anthropic response format
            if "content" in response and len(response["content"]) > 0:
                return response["content"][0].get("text", "")
            return ""
            
        except Exception as e:
            logger.error("AI analysis request failed", error=str(e))
            raise DigiSetuException(
                status_code=500,
                error_code="AI_ANALYSIS_ERROR",
                message=f"AI analysis failed: {str(e)}"
            )
    
    def _parse_ai_response(self, response: str, original_content: str) -> ComponentDecision:
        """Parse and validate AI response."""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in AI response")
            
            json_str = json_match.group(0)
            parsed = json.loads(json_str)
            
            # Validate required fields
            decision = parsed.get("decision", "NO_COMPONENT")
            confidence = float(parsed.get("confidence", 0.0))
            reasoning = parsed.get("reasoning", "No reasoning provided")
            
            # Validate decision value
            if decision not in ["GENERATE_NOW", "NO_COMPONENT"]:
                decision = "NO_COMPONENT"
                confidence = 0.0
                reasoning = "Invalid decision format"
            
            # Validate confidence threshold
            if decision == "GENERATE_NOW" and confidence < 0.7:
                decision = "NO_COMPONENT"
                reasoning = f"Confidence too low: {confidence}"
            
            # Extract optional fields
            component_type = parsed.get("component_type")
            markdown = parsed.get("markdown")
            extracted_data = parsed.get("extracted_data")
            
            # Validate component type if generating
            if decision == "GENERATE_NOW":
                valid_types = ["pie-chart", "bar-chart", "line-chart", "data-table"]
                if component_type not in valid_types:
                    decision = "NO_COMPONENT"
                    reasoning = f"Invalid component type: {component_type}"
                    component_type = None
                    markdown = None
            
            return ComponentDecision(
                decision=decision,
                component_type=component_type,
                confidence=confidence,
                reasoning=reasoning,
                markdown=markdown,
                extracted_data=extracted_data
            )
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI response JSON", error=str(e), response=response[:200])
            return ComponentDecision(
                decision="NO_COMPONENT",
                confidence=0.0,
                reasoning="Failed to parse AI response"
            )
        except Exception as e:
            logger.error("Failed to parse AI response", error=str(e))
            return ComponentDecision(
                decision="NO_COMPONENT",
                confidence=0.0,
                reasoning=f"Response parsing error: {str(e)}"
            )
    
    def _has_data_patterns(self, content: str) -> bool:
        """
        Quick pre-filter to detect if content has any data patterns.
        Returns immediately for non-data content to avoid AI calls.
        """
        import re
        
        # Data pattern indicators (optimized for speed)
        data_patterns = [
            r'\d+%',                           # Percentages: 45%
            r'\$[\d,]+',                       # Money: $1,000
            r'\d{1,3}(?:,\d{3})+',            # Large numbers: 1,000+
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b',  # Months
            r'\bQ[1-4]\b',                     # Quarters
            r'\d+:\s*\d+',                     # Ratios: 3:1
            r'\d+\s*(?:vs|versus)\s*\d+',      # Comparisons: 100 vs 200
            r'\d+\.\d+',                       # Decimals: 3.14
            r'\b\d+\s*(?:hours?|days?|months?|years?)\b',  # Time units
            r'\b\d+\s*(?:users?|customers?|visitors?)\b',   # Metrics
            r'\b(?:increased?|decreased?|grew?|fell)\s+(?:to|by)\s+\d+',  # Growth language
        ]
        
        # Quick regex check (much faster than AI)
        for pattern in data_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
                
        return False

    async def cleanup(self):
        """Cleanup resources."""
        if self.anthropic_provider:
            await self.anthropic_provider.cleanup()
        logger.info("Component Analysis Service cleaned up")
