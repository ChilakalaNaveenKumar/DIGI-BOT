"""
Reasoning Processor Service

Handles AI reasoning display, step-by-step thought processes, and reasoning analysis.
"""

import asyncio
import json
import re
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
from datetime import datetime

import structlog
from pydantic import BaseModel

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class ReasoningStep(BaseModel):
    """Individual reasoning step."""
    step_number: int
    title: str
    content: str
    confidence: float
    reasoning_type: str  # analysis, deduction, inference, assumption, conclusion
    timestamp: datetime
    dependencies: List[int] = []  # Steps this depends on


class ReasoningChain(BaseModel):
    """Complete reasoning chain."""
    chain_id: str
    steps: List[ReasoningStep]
    final_conclusion: str
    confidence: float
    reasoning_quality: str  # excellent, good, fair, poor
    total_time: float
    metadata: Dict[str, Any] = {}


class ReasoningProcessor:
    """
    Service for processing and displaying AI reasoning.
    
    Features:
    - Step-by-step reasoning extraction
    - Reasoning quality assessment
    - Interactive reasoning display
    - Reasoning chain validation
    - Confidence scoring
    """
    
    def __init__(self):
        self.reasoning_patterns = {
            "step_indicators": [
                r"(?i)step\s+(\d+)[:.]?\s*(.*)",
                r"(?i)first[ly]?[:.]?\s*(.*)",
                r"(?i)second[ly]?[:.]?\s*(.*)",
                r"(?i)third[ly]?[:.]?\s*(.*)",
                r"(?i)next[:.]?\s*(.*)",
                r"(?i)then[:.]?\s*(.*)",
                r"(?i)finally[:.]?\s*(.*)",
                r"(?i)therefore[:.]?\s*(.*)",
                r"(?i)consequently[:.]?\s*(.*)",
                r"(?i)as a result[:.]?\s*(.*)"
            ],
            "reasoning_types": {
                "analysis": [r"(?i)analyz", r"(?i)examin", r"(?i)investigat", r"(?i)break down"],
                "deduction": [r"(?i)deduc", r"(?i)conclud", r"(?i)infer", r"(?i)derive"],
                "inference": [r"(?i)suggest", r"(?i)imply", r"(?i)indicate", r"(?i)point to"],
                "assumption": [r"(?i)assum", r"(?i)presume", r"(?i)suppose", r"(?i)given that"],
                "conclusion": [r"(?i)conclud", r"(?i)final", r"(?i)result", r"(?i)outcome"]
            },
            "confidence_indicators": {
                "high": [r"(?i)certain", r"(?i)definite", r"(?i)clear", r"(?i)obvious"],
                "medium": [r"(?i)likely", r"(?i)probable", r"(?i)suggest", r"(?i)indicate"],
                "low": [r"(?i)might", r"(?i)could", r"(?i)possibly", r"(?i)perhaps", r"(?i)maybe"]
            }
        }
        
        self.quality_metrics = {
            "logical_flow": 0.0,
            "evidence_support": 0.0,
            "clarity": 0.0,
            "completeness": 0.0
        }
    
    async def initialize(self):
        """Initialize the reasoning processor."""
        logger.info("ReasoningProcessor initialized successfully")
    
    async def process_reasoning(
        self,
        reasoning_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ReasoningChain:
        """Process raw reasoning text into structured reasoning chain."""
        
        try:
            # Extract reasoning steps
            steps = await self._extract_reasoning_steps(reasoning_text)
            
            # Assess reasoning quality
            quality_score = await self._assess_reasoning_quality(steps, reasoning_text)
            
            # Generate final conclusion
            final_conclusion = await self._extract_final_conclusion(reasoning_text, steps)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(steps)
            
            # Create reasoning chain
            chain = ReasoningChain(
                chain_id=f"reasoning_{int(datetime.utcnow().timestamp())}",
                steps=steps,
                final_conclusion=final_conclusion,
                confidence=overall_confidence,
                reasoning_quality=self._get_quality_label(quality_score),
                total_time=0.0,  # Will be calculated by caller
                metadata={
                    "quality_score": quality_score,
                    "step_count": len(steps),
                    "context": context or {}
                }
            )
            
            logger.info(
                "Reasoning processed successfully",
                chain_id=chain.chain_id,
                steps=len(steps),
                quality=chain.reasoning_quality
            )
            
            return chain
            
        except Exception as e:
            logger.error("Failed to process reasoning", error=str(e))
            # Return minimal reasoning chain
            return ReasoningChain(
                chain_id="error_chain",
                steps=[],
                final_conclusion="Unable to process reasoning",
                confidence=0.0,
                reasoning_quality="poor",
                total_time=0.0
            )
    
    async def stream_reasoning_display(
        self,
        reasoning_chain: ReasoningChain,
        display_speed: float = 1.0
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream reasoning steps for interactive display."""
        
        try:
            # Stream initial reasoning info
            yield {
                "type": "reasoning_start",
                "chain_id": reasoning_chain.chain_id,
                "total_steps": len(reasoning_chain.steps),
                "quality": reasoning_chain.reasoning_quality,
                "confidence": reasoning_chain.confidence,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Stream each reasoning step
            for i, step in enumerate(reasoning_chain.steps):
                # Delay based on display speed
                if i > 0:
                    await asyncio.sleep(1.0 / display_speed)
                
                yield {
                    "type": "reasoning_step",
                    "step": {
                        "number": step.step_number,
                        "title": step.title,
                        "content": step.content,
                        "confidence": step.confidence,
                        "reasoning_type": step.reasoning_type,
                        "dependencies": step.dependencies
                    },
                    "progress": (i + 1) / len(reasoning_chain.steps),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Stream final conclusion
            await asyncio.sleep(0.5 / display_speed)
            yield {
                "type": "reasoning_conclusion",
                "conclusion": reasoning_chain.final_conclusion,
                "overall_confidence": reasoning_chain.confidence,
                "quality": reasoning_chain.reasoning_quality,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to stream reasoning display", error=str(e))
            yield {
                "type": "reasoning_error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _extract_reasoning_steps(self, text: str) -> List[ReasoningStep]:
        """Extract individual reasoning steps from text."""
        
        steps = []
        lines = text.split('\n')
        current_step = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for step indicators
            step_match = None
            for pattern in self.reasoning_patterns["step_indicators"]:
                match = re.search(pattern, line)
                if match:
                    step_match = match
                    break
            
            if step_match:
                # Extract step content
                if step_match.groups():
                    if step_match.group(1).isdigit():
                        step_num = int(step_match.group(1))
                        content = step_match.group(2) if len(step_match.groups()) > 1 else line
                    else:
                        step_num = current_step
                        content = step_match.group(1)
                else:
                    step_num = current_step
                    content = line
                
                # Determine reasoning type
                reasoning_type = self._classify_reasoning_type(content)
                
                # Calculate confidence
                confidence = self._calculate_step_confidence(content)
                
                # Generate title
                title = self._generate_step_title(content, reasoning_type)
                
                step = ReasoningStep(
                    step_number=step_num,
                    title=title,
                    content=content,
                    confidence=confidence,
                    reasoning_type=reasoning_type,
                    timestamp=datetime.utcnow()
                )
                
                steps.append(step)
                current_step = max(current_step, step_num) + 1
        
        # If no explicit steps found, treat as single reasoning block
        if not steps and text.strip():
            steps.append(ReasoningStep(
                step_number=1,
                title="Analysis",
                content=text.strip(),
                confidence=0.7,
                reasoning_type="analysis",
                timestamp=datetime.utcnow()
            ))
        
        return steps
    
    def _classify_reasoning_type(self, content: str) -> str:
        """Classify the type of reasoning in content."""
        
        for reasoning_type, patterns in self.reasoning_patterns["reasoning_types"].items():
            for pattern in patterns:
                if re.search(pattern, content):
                    return reasoning_type
        
        return "analysis"  # Default
    
    def _calculate_step_confidence(self, content: str) -> float:
        """Calculate confidence score for a reasoning step."""
        
        # Check confidence indicators
        for confidence_level, patterns in self.reasoning_patterns["confidence_indicators"].items():
            for pattern in patterns:
                if re.search(pattern, content):
                    if confidence_level == "high":
                        return 0.9
                    elif confidence_level == "medium":
                        return 0.7
                    elif confidence_level == "low":
                        return 0.4
        
        # Default confidence based on content length and structure
        if len(content) > 100:
            return 0.8  # Longer explanations tend to be more confident
        elif len(content) > 50:
            return 0.6
        else:
            return 0.5
    
    def _generate_step_title(self, content: str, reasoning_type: str) -> str:
        """Generate a title for a reasoning step."""
        
        # Extract first few words as title
        words = content.split()[:6]
        title = " ".join(words)
        
        # Add ellipsis if truncated
        if len(content.split()) > 6:
            title += "..."
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        
        return title or f"{reasoning_type.title()} Step"
    
    async def _assess_reasoning_quality(self, steps: List[ReasoningStep], full_text: str) -> float:
        """Assess the quality of reasoning."""
        
        if not steps:
            return 0.0
        
        # Logical flow assessment
        logical_flow = self._assess_logical_flow(steps)
        
        # Evidence support assessment
        evidence_support = self._assess_evidence_support(full_text)
        
        # Clarity assessment
        clarity = self._assess_clarity(steps, full_text)
        
        # Completeness assessment
        completeness = self._assess_completeness(steps)
        
        # Weighted average
        quality_score = (
            logical_flow * 0.3 +
            evidence_support * 0.25 +
            clarity * 0.25 +
            completeness * 0.2
        )
        
        return min(1.0, max(0.0, quality_score))
    
    def _assess_logical_flow(self, steps: List[ReasoningStep]) -> float:
        """Assess logical flow between reasoning steps."""
        
        if len(steps) <= 1:
            return 0.8  # Single step is considered good flow
        
        # Check for logical progression
        reasoning_types = [step.reasoning_type for step in steps]
        
        # Good flow patterns
        good_patterns = [
            ["analysis", "deduction", "conclusion"],
            ["assumption", "analysis", "inference"],
            ["analysis", "inference", "conclusion"]
        ]
        
        # Check if reasoning follows good patterns
        for pattern in good_patterns:
            if all(rt in reasoning_types for rt in pattern):
                return 0.9
        
        # Check for reasonable progression
        if "analysis" in reasoning_types and "conclusion" in reasoning_types:
            return 0.7
        
        return 0.6
    
    def _assess_evidence_support(self, text: str) -> float:
        """Assess how well reasoning is supported by evidence."""
        
        evidence_indicators = [
            r"(?i)because", r"(?i)since", r"(?i)given that", r"(?i)based on",
            r"(?i)evidence", r"(?i)data shows", r"(?i)research", r"(?i)studies"
        ]
        
        evidence_count = 0
        for pattern in evidence_indicators:
            evidence_count += len(re.findall(pattern, text))
        
        # Normalize based on text length
        text_length = len(text.split())
        evidence_density = evidence_count / max(1, text_length / 50)
        
        return min(1.0, evidence_density * 0.5 + 0.3)
    
    def _assess_clarity(self, steps: List[ReasoningStep], text: str) -> float:
        """Assess clarity of reasoning."""
        
        # Check average step confidence
        avg_confidence = sum(step.confidence for step in steps) / len(steps) if steps else 0.5
        
        # Check for clear structure
        structure_score = 0.8 if len(steps) > 1 else 0.6
        
        # Check for clear language (simple heuristics)
        complex_words = len(re.findall(r'\b\w{10,}\b', text))
        total_words = len(text.split())
        complexity_ratio = complex_words / max(1, total_words)
        
        clarity_score = (avg_confidence * 0.4 + structure_score * 0.4 + (1 - complexity_ratio) * 0.2)
        
        return min(1.0, max(0.0, clarity_score))
    
    def _assess_completeness(self, steps: List[ReasoningStep]) -> float:
        """Assess completeness of reasoning."""
        
        if not steps:
            return 0.0
        
        # Check for key reasoning components
        reasoning_types = set(step.reasoning_type for step in steps)
        
        completeness_score = 0.5  # Base score
        
        if "analysis" in reasoning_types:
            completeness_score += 0.2
        if "conclusion" in reasoning_types or "deduction" in reasoning_types:
            completeness_score += 0.2
        if len(reasoning_types) >= 2:
            completeness_score += 0.1
        
        return min(1.0, completeness_score)
    
    async def _extract_final_conclusion(self, text: str, steps: List[ReasoningStep]) -> str:
        """Extract or generate final conclusion."""
        
        # Look for explicit conclusion in text
        conclusion_patterns = [
            r"(?i)in conclusion[:.]?\s*(.*)",
            r"(?i)therefore[:.]?\s*(.*)",
            r"(?i)finally[:.]?\s*(.*)",
            r"(?i)to summarize[:.]?\s*(.*)"
        ]
        
        for pattern in conclusion_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        # Use last step as conclusion if it's a conclusion type
        if steps and steps[-1].reasoning_type in ["conclusion", "deduction"]:
            return steps[-1].content
        
        # Generate generic conclusion
        return "Based on the analysis above, this represents the reasoning outcome."
    
    def _calculate_overall_confidence(self, steps: List[ReasoningStep]) -> float:
        """Calculate overall confidence from individual steps."""
        
        if not steps:
            return 0.0
        
        # Weighted average with more weight on later steps
        total_weight = 0
        weighted_confidence = 0
        
        for i, step in enumerate(steps):
            weight = (i + 1) / len(steps)  # Later steps have more weight
            weighted_confidence += step.confidence * weight
            total_weight += weight
        
        return weighted_confidence / total_weight if total_weight > 0 else 0.0
    
    def _get_quality_label(self, quality_score: float) -> str:
        """Convert quality score to label."""
        
        if quality_score >= 0.8:
            return "excellent"
        elif quality_score >= 0.6:
            return "good"
        elif quality_score >= 0.4:
            return "fair"
        else:
            return "poor"
    
    async def validate_reasoning_chain(self, chain: ReasoningChain) -> Dict[str, Any]:
        """Validate a reasoning chain for logical consistency."""
        
        validation_results = {
            "is_valid": True,
            "issues": [],
            "suggestions": [],
            "confidence_adjustment": 0.0
        }
        
        # Check for logical gaps
        if len(chain.steps) > 1:
            for i in range(1, len(chain.steps)):
                current_step = chain.steps[i]
                prev_step = chain.steps[i-1]
                
                # Check if current step logically follows previous
                if not self._steps_are_connected(prev_step, current_step):
                    validation_results["issues"].append(
                        f"Logical gap between step {prev_step.step_number} and {current_step.step_number}"
                    )
                    validation_results["confidence_adjustment"] -= 0.1
        
        # Check for contradictions
        contradictions = self._find_contradictions(chain.steps)
        if contradictions:
            validation_results["issues"].extend(contradictions)
            validation_results["confidence_adjustment"] -= 0.2
        
        # Generate suggestions
        if validation_results["issues"]:
            validation_results["suggestions"].append("Consider adding intermediate reasoning steps")
            validation_results["suggestions"].append("Review logical connections between steps")
        
        validation_results["is_valid"] = len(validation_results["issues"]) == 0
        
        return validation_results
    
    def _steps_are_connected(self, step1: ReasoningStep, step2: ReasoningStep) -> bool:
        """Check if two reasoning steps are logically connected."""
        
        # Simple heuristic: check if step2 references concepts from step1
        step1_words = set(step1.content.lower().split())
        step2_words = set(step2.content.lower().split())
        
        # Remove common words
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        step1_words -= common_words
        step2_words -= common_words
        
        # Check for word overlap
        overlap = len(step1_words & step2_words)
        return overlap > 0 or step2.step_number in step2.dependencies
    
    def _find_contradictions(self, steps: List[ReasoningStep]) -> List[str]:
        """Find potential contradictions in reasoning steps."""
        
        contradictions = []
        
        # Simple contradiction detection based on opposing words
        opposing_pairs = [
            ("increase", "decrease"), ("more", "less"), ("higher", "lower"),
            ("positive", "negative"), ("good", "bad"), ("yes", "no")
        ]
        
        for i, step1 in enumerate(steps):
            for j, step2 in enumerate(steps[i+1:], i+1):
                for word1, word2 in opposing_pairs:
                    if (word1 in step1.content.lower() and word2 in step2.content.lower()) or \
                       (word2 in step1.content.lower() and word1 in step2.content.lower()):
                        contradictions.append(
                            f"Potential contradiction between step {step1.step_number} and {step2.step_number}"
                        )
                        break
        
        return contradictions
