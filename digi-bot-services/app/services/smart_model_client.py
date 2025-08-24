"""
Smart Model Client

Automatically selects the best model for each task based on requirements
and budget constraints. Uses the model configuration to optimize performance
and cost.
"""

import os
from typing import Dict, List, Optional, Any, AsyncGenerator
from openai import AsyncOpenAI
from .model_config import (
    get_model_config, get_best_model_for_task, estimate_cost, 
    get_safe_output_tokens, supports_tool, RECOMMENDED_MODELS
)


class SmartModelClient:
    """
    Intelligent model client that automatically selects the best model
    for each task based on requirements and constraints.
    """
    
    def __init__(self, api_key: Optional[str] = None, budget_per_request: float = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.budget_per_request = budget_per_request  # Max USD per request
        self._initialized = False
    
    async def initialize(self):
        """Initialize the client"""
        if self._initialized:
            return
        
        await self.client.models.list()
        self._initialized = True
        print("✅ Smart model client initialized")
    
    async def smart_completion(
        self,
        prompt: str,
        task_type: str = "chat",
        needs_vision: bool = False,
        needs_tools: bool = False,
        needs_reasoning: bool = False,
        preferred_model: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        images: Optional[List[str]] = None,
        max_output_tokens: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Smart completion that automatically selects the best model.
        
        Args:
            prompt: The text prompt
            task_type: Type of task (chat, analysis, reasoning, vision, tools)
            needs_vision: Whether vision capabilities are required
            needs_tools: Whether tool calling is required  
            needs_reasoning: Whether advanced reasoning is required
            preferred_model: Specific model to use (overrides auto-selection)
            tools: List of tools to make available
            images: List of image URLs or file IDs
            max_output_tokens: Maximum output tokens (auto-calculated if None)
        """
        
        if not self._initialized:
            await self.initialize()
        
        # Auto-detect requirements
        if images:
            needs_vision = True
        if tools:
            needs_tools = True
        
        # Select best model
        if preferred_model:
            model = preferred_model
        else:
            budget_per_1k = None
            if self.budget_per_request:
                # Rough estimate: assume 2k input + 1k output tokens
                budget_per_1k = (self.budget_per_request / 3) * 1000
            
            model = get_best_model_for_task(
                task_type=task_type,
                needs_vision=needs_vision,
                needs_tools=needs_tools,
                needs_reasoning=needs_reasoning,
                max_budget_per_1k_tokens=budget_per_1k
            )
        
        # Get model config
        config = get_model_config(model)
        if not config:
            yield {"type": "error", "error": f"Unknown model: {model}"}
            return
        
        # Estimate input tokens (rough)
        input_tokens = len(prompt.split()) * 1.3  # Rough token estimate
        if images:
            input_tokens += len(images) * 750  # ~750 tokens per image
        
        # Calculate safe output tokens
        if max_output_tokens is None:
            max_output_tokens = get_safe_output_tokens(model, int(input_tokens))
        
        # Validate tool support
        if tools and not config.supports_tools:
            yield {"type": "error", "error": f"Model {model} does not support tools"}
            return
        
        # Build content
        content = [{"type": "input_text", "text": prompt}]
        
        # Add images if provided
        if images and config.supports_vision:
            for image in images:
                if image.startswith("http"):
                    content.append({"type": "input_image", "image_url": {"url": image}})
                else:
                    content.append({"type": "input_image", "image_file": {"file_id": image}})
        
        # Estimate cost
        estimated_cost = estimate_cost(model, int(input_tokens), max_output_tokens)
        
        yield {
            "type": "model_info",
            "model": model,
            "estimated_cost": estimated_cost,
            "input_tokens": int(input_tokens),
            "max_output_tokens": max_output_tokens
        }
        
        # Check budget
        if self.budget_per_request and estimated_cost > self.budget_per_request:
            yield {
                "type": "warning", 
                "message": f"Estimated cost ${estimated_cost:.4f} exceeds budget ${self.budget_per_request:.4f}"
            }
        
        # Make the request
        try:
            request_params = {
                "model": model,
                "input": [{"role": "user", "content": content}],
                "max_output_tokens": max_output_tokens
            }
            
            # Add tools if supported and provided
            if tools and config.supports_tools:
                request_params["tools"] = tools
            
            async with self.client.responses.stream(**request_params) as stream:
                async for event in stream:
                    event_type = getattr(event, "type", "")
                    if event_type == "response.output_text.delta":
                        yield {"type": "content", "content": event.delta}
                    elif event_type == "response.error":
                        yield {"type": "error", "error": getattr(event, "error", "unknown")}
                    elif event_type == "response.completed":
                        yield {"type": "completion", "finish_reason": "done"}
                        
        except Exception as e:
            yield {"type": "error", "error": str(e)}
    
    async def quick_completion(
        self,
        prompt: str,
        task_type: str = "chat",
        **kwargs
    ) -> str:
        """Quick non-streaming completion"""
        
        full_response = ""
        async for event in self.smart_completion(prompt, task_type, **kwargs):
            if event["type"] == "content":
                full_response += event["content"]
            elif event["type"] == "error":
                return f"ERROR: {event['error']}"
        
        return full_response.strip()
    
    def get_recommended_model(self, task_type: str) -> str:
        """Get recommended model for a task type"""
        return RECOMMENDED_MODELS.get(task_type, "gpt-4o")
    
    def estimate_request_cost(
        self, 
        prompt: str, 
        model: str, 
        output_tokens: int = 1000,
        images: int = 0
    ) -> float:
        """Estimate cost for a request"""
        
        input_tokens = len(prompt.split()) * 1.3  # Rough estimate
        input_tokens += images * 750  # Add image tokens
        
        return estimate_cost(model, int(input_tokens), output_tokens)


# Specialized clients for common use cases
class ChartAnalysisClient(SmartModelClient):
    """Specialized client for chart analysis tasks"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_model = self.get_recommended_model("chart_matching")
    
    async def analyze_chart_request(self, query: str, documentation: str = None) -> str:
        """Analyze a chart format request"""
        
        prompt = f"""You are a chart format matcher.

Compare the QUERY with the DOCUMENTATION below.
If the query matches a format/example, return the exact format block(s).
If no format applies, return only "NO_MATCH".

QUERY:
{query}

DOCUMENTATION:
{documentation or "No documentation provided"}"""
        
        return await self.quick_completion(
            prompt,
            task_type="chart_matching",
            needs_tools=True,
            preferred_model=self.default_model
        )


class VisionAnalysisClient(SmartModelClient):
    """Specialized client for vision analysis tasks"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_model = self.get_recommended_model("vision_analysis")
    
    async def analyze_image(
        self, 
        image_url: str, 
        prompt: str = "Describe this image in detail."
    ) -> str:
        """Analyze an image"""
        
        return await self.quick_completion(
            prompt,
            task_type="vision",
            needs_vision=True,
            images=[image_url],
            preferred_model=self.default_model
        )


class DocumentAnalysisClient(SmartModelClient):
    """Specialized client for document analysis tasks"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_model = self.get_recommended_model("document_analysis")
    
    async def analyze_document(
        self, 
        document_text: str, 
        analysis_type: str = "summary"
    ) -> str:
        """Analyze a document"""
        
        prompts = {
            "summary": f"Provide a comprehensive summary of this document:\n\n{document_text}",
            "key_points": f"Extract the key points from this document:\n\n{document_text}",
            "questions": f"Generate important questions answered by this document:\n\n{document_text}",
            "topics": f"Identify the main topics covered in this document:\n\n{document_text}"
        }
        
        prompt = prompts.get(analysis_type, prompts["summary"])
        
        return await self.quick_completion(
            prompt,
            task_type="analysis",
            needs_tools=True,
            preferred_model=self.default_model
        )


class ReasoningClient(SmartModelClient):
    """Specialized client for reasoning tasks"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_model = self.get_recommended_model("reasoning_tasks")
    
    async def solve_problem(self, problem: str) -> str:
        """Solve a complex problem using reasoning"""
        
        prompt = f"""Solve this problem step by step, showing your reasoning:

{problem}

Think through this carefully and provide a detailed solution."""
        
        return await self.quick_completion(
            prompt,
            task_type="reasoning",
            needs_reasoning=True,
            preferred_model=self.default_model
        )
