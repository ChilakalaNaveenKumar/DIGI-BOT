"""
Reasoning Service - Chain-of-Thought Processing

Implements advanced reasoning capabilities with thinking process display.
"""

import asyncio
import json
import time
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple
from datetime import datetime

import structlog
from pydantic import BaseModel

from app.core.config import get_settings
from app.services.ai_providers.openai_provider import OpenAIProvider
from app.services.ai_providers.anthropic_provider import AnthropicProvider

logger = structlog.get_logger(__name__)
settings = get_settings()


class ReasoningStep(BaseModel):
    """Individual reasoning step."""
    step_number: int
    thought: str
    reasoning: str
    conclusion: str
    confidence: float
    timestamp: datetime


class ReasoningChain(BaseModel):
    """Complete reasoning chain."""
    query: str
    steps: List[ReasoningStep]
    final_answer: str
    total_confidence: float
    reasoning_time: float
    model_used: str


class ReasoningService:
    """Service for advanced reasoning and chain-of-thought processing."""
    
    def __init__(self):
        """Initialize reasoning service."""
        self.openai_provider = OpenAIProvider()
        self.anthropic_provider = AnthropicProvider()
    
    async def generate_reasoning_chain(
        self,
        query: str,
        reasoning_effort: str = "medium",
        model: str = "gpt-4",
        max_steps: int = 5
    ) -> ReasoningChain:
        """
        Generate a complete reasoning chain for a query.
        
        Args:
            query: The question or problem to reason about
            reasoning_effort: Level of reasoning (minimal, medium, high)
            model: AI model to use for reasoning
            max_steps: Maximum number of reasoning steps
            
        Returns:
            Complete reasoning chain with steps and final answer
        """
        try:
            start_time = time.time()
            
            logger.info(
                "Starting reasoning chain generation",
                query=query[:100],
                reasoning_effort=reasoning_effort,
                model=model,
                max_steps=max_steps
            )
            
            # Generate reasoning chain based on model
            if model.startswith('gpt'):
                reasoning_chain = await self._generate_openai_reasoning(
                    query, reasoning_effort, model, max_steps
                )
            elif model.startswith('claude'):
                reasoning_chain = await self._generate_anthropic_reasoning(
                    query, reasoning_effort, model, max_steps
                )
            else:
                # Default to OpenAI
                reasoning_chain = await self._generate_openai_reasoning(
                    query, reasoning_effort, "gpt-4", max_steps
                )
            
            reasoning_time = time.time() - start_time
            reasoning_chain.reasoning_time = reasoning_time
            
            logger.info(
                "Reasoning chain completed",
                steps_generated=len(reasoning_chain.steps),
                final_confidence=reasoning_chain.total_confidence,
                reasoning_time=reasoning_time
            )
            
            return reasoning_chain
            
        except Exception as e:
            logger.error("Reasoning chain generation failed", error=str(e), exc_info=True)
            raise
    
    async def _generate_openai_reasoning(
        self,
        query: str,
        reasoning_effort: str,
        model: str,
        max_steps: int
    ) -> ReasoningChain:
        """Generate reasoning chain using OpenAI with chain-of-thought."""
        
        # Adjust reasoning prompt based on effort level
        effort_prompts = {
            "minimal": "Think step by step, but be concise.",
            "medium": "Think through this step by step, showing your reasoning process.",
            "high": "Think deeply about this problem. Break it down into detailed steps, consider multiple approaches, and show your complete reasoning process."
        }
        
        system_prompt = f"""You are an expert reasoning assistant. {effort_prompts.get(reasoning_effort, effort_prompts['medium'])}

For each step of your reasoning:
1. State what you're thinking about
2. Explain your reasoning process
3. Draw a conclusion for that step
4. Rate your confidence (0.0 to 1.0)

Format your response as JSON with this structure:
{{
  "steps": [
    {{
      "step_number": 1,
      "thought": "What I'm thinking about",
      "reasoning": "My reasoning process",
      "conclusion": "What I conclude from this step",
      "confidence": 0.8
    }}
  ],
  "final_answer": "Your final comprehensive answer",
  "total_confidence": 0.85
}}"""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please reason through this query: {query}"}
            ]
            
            response = await self.openai_provider.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            reasoning_data = json.loads(response.choices[0].message.content)
            
            # Convert to ReasoningChain
            steps = []
            for i, step_data in enumerate(reasoning_data.get("steps", [])):
                step = ReasoningStep(
                    step_number=i + 1,
                    thought=step_data.get("thought", ""),
                    reasoning=step_data.get("reasoning", ""),
                    conclusion=step_data.get("conclusion", ""),
                    confidence=step_data.get("confidence", 0.5),
                    timestamp=datetime.now()
                )
                steps.append(step)
            
            return ReasoningChain(
                query=query,
                steps=steps,
                final_answer=reasoning_data.get("final_answer", ""),
                total_confidence=reasoning_data.get("total_confidence", 0.5),
                reasoning_time=0.0,  # Will be set by caller
                model_used=model
            )
            
        except Exception as e:
            logger.error("OpenAI reasoning generation failed", error=str(e))
            raise
    
    async def _generate_anthropic_reasoning(
        self,
        query: str,
        reasoning_effort: str,
        model: str,
        max_steps: int
    ) -> ReasoningChain:
        """Generate reasoning chain using Anthropic with thinking tags."""
        
        effort_prompts = {
            "minimal": "Think step by step, but be concise.",
            "medium": "Think through this step by step, showing your reasoning process.",
            "high": "Think deeply about this problem. Use <thinking> tags to show your internal reasoning process."
        }
        
        system_prompt = f"""You are an expert reasoning assistant. {effort_prompts.get(reasoning_effort, effort_prompts['medium'])}

Use <thinking> tags to show your reasoning process, then provide a structured response.

For each step:
1. Use <thinking>Your internal reasoning here</thinking>
2. State your conclusion
3. Rate your confidence

Format your final response as JSON:
{{
  "steps": [
    {{
      "step_number": 1,
      "thought": "What I'm thinking about",
      "reasoning": "My reasoning process", 
      "conclusion": "What I conclude",
      "confidence": 0.8
    }}
  ],
  "final_answer": "Your final answer",
  "total_confidence": 0.85
}}"""

        try:
            messages = [
                {"role": "user", "content": f"{system_prompt}\n\nQuery: {query}"}
            ]
            
            response = await self.anthropic_provider.client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.3,
                messages=messages
            )
            
            content = response.content[0].text
            
            # Extract JSON from response (it might be wrapped in other text)
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                reasoning_data = json.loads(content[json_start:json_end])
            else:
                # Fallback: create reasoning from text
                reasoning_data = {
                    "steps": [{
                        "step_number": 1,
                        "thought": "Analyzing the query",
                        "reasoning": content,
                        "conclusion": "Generated response using Anthropic reasoning",
                        "confidence": 0.7
                    }],
                    "final_answer": content,
                    "total_confidence": 0.7
                }
            
            # Convert to ReasoningChain
            steps = []
            for i, step_data in enumerate(reasoning_data.get("steps", [])):
                step = ReasoningStep(
                    step_number=i + 1,
                    thought=step_data.get("thought", ""),
                    reasoning=step_data.get("reasoning", ""),
                    conclusion=step_data.get("conclusion", ""),
                    confidence=step_data.get("confidence", 0.5),
                    timestamp=datetime.now()
                )
                steps.append(step)
            
            return ReasoningChain(
                query=query,
                steps=steps,
                final_answer=reasoning_data.get("final_answer", ""),
                total_confidence=reasoning_data.get("total_confidence", 0.5),
                reasoning_time=0.0,
                model_used=model
            )
            
        except Exception as e:
            logger.error("Anthropic reasoning generation failed", error=str(e))
            raise
    
    async def stream_reasoning_chain(
        self,
        query: str,
        reasoning_effort: str = "medium",
        model: str = "gpt-4"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream reasoning chain generation in real-time.
        
        Args:
            query: The question to reason about
            reasoning_effort: Level of reasoning
            model: AI model to use
            
        Yields:
            Streaming reasoning steps as they're generated
        """
        try:
            logger.info("Starting streaming reasoning", query=query[:100])
            
            yield {
                "type": "reasoning_start",
                "query": query,
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            
            # Generate reasoning chain
            reasoning_chain = await self.generate_reasoning_chain(
                query, reasoning_effort, model
            )
            
            # Stream each step
            for step in reasoning_chain.steps:
                yield {
                    "type": "reasoning_step",
                    "step": {
                        "step_number": step.step_number,
                        "thought": step.thought,
                        "reasoning": step.reasoning,
                        "conclusion": step.conclusion,
                        "confidence": step.confidence,
                        "timestamp": step.timestamp.isoformat()
                    }
                }
                
                # Small delay to simulate real-time thinking
                await asyncio.sleep(0.5)
            
            # Final answer
            yield {
                "type": "reasoning_complete",
                "final_answer": reasoning_chain.final_answer,
                "total_confidence": reasoning_chain.total_confidence,
                "reasoning_time": reasoning_chain.reasoning_time,
                "total_steps": len(reasoning_chain.steps)
            }
            
        except Exception as e:
            logger.error("Streaming reasoning failed", error=str(e))
            yield {
                "type": "reasoning_error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def format_reasoning_for_display(self, reasoning_chain: ReasoningChain) -> str:
        """Format reasoning chain for human-readable display."""
        
        output = f"🧠 **Reasoning Chain Analysis**\n\n"
        output += f"**Query:** {reasoning_chain.query}\n"
        output += f"**Model:** {reasoning_chain.model_used}\n"
        output += f"**Reasoning Time:** {reasoning_chain.reasoning_time:.2f}s\n\n"
        
        output += "**Step-by-Step Reasoning:**\n\n"
        
        for step in reasoning_chain.steps:
            output += f"**Step {step.step_number}:** {step.thought}\n"
            output += f"*Reasoning:* {step.reasoning}\n"
            output += f"*Conclusion:* {step.conclusion}\n"
            output += f"*Confidence:* {step.confidence:.1%}\n\n"
        
        output += f"**Final Answer:**\n{reasoning_chain.final_answer}\n\n"
        output += f"**Overall Confidence:** {reasoning_chain.total_confidence:.1%}"
        
        return output

