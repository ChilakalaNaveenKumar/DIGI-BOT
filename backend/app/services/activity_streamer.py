"""
Activity Streamer Service

Manages natural activity streaming with privacy-aware message generation.
"""

import asyncio
import re
from typing import AsyncGenerator, Dict, List, Optional, Any
from datetime import datetime

import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class ActivityStreamer:
    """Service for streaming natural activity updates to users."""
    
    def __init__(self):
        self.privacy_mode = settings.ACTIVITY_PRIVACY_MODE
        self.activity_templates = {
            "analyzing": [
                "Analyzing your request...",
                "Processing your question...",
                "Understanding what you're asking...",
                "Breaking down your request...",
                "Examining the details..."
            ],
            "thinking": [
                "Thinking through this problem...",
                "Considering the best approach...",
                "Working through the logic...",
                "Evaluating different options...",
                "Processing the information..."
            ],
            "searching": [
                "Searching for relevant information...",
                "Looking up current data...",
                "Gathering the latest information...",
                "Checking for updates...",
                "Finding relevant sources..."
            ],
            "generating": [
                "Generating your response...",
                "Crafting a detailed answer...",
                "Preparing your response...",
                "Putting together the information...",
                "Finalizing the details..."
            ],
            "tool_executing": [
                "Executing the requested action...",
                "Running the analysis...",
                "Processing the data...",
                "Performing the calculation...",
                "Completing the task..."
            ],
            "reasoning": [
                "Working through the reasoning...",
                "Analyzing step by step...",
                "Considering all aspects...",
                "Evaluating the logic...",
                "Thinking it through..."
            ]
        }
        
        self.sensitive_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',  # Phone
            r'\b[A-Z]{2}\d{6,8}\b',  # Passport-like
            r'\bapi[_-]?key\b',  # API keys
            r'\bpassword\b',  # Password mentions
            r'\btoken\b',  # Token mentions
        ]
    
    async def initialize(self):
        """Initialize the activity streamer service."""
        logger.info("ActivityStreamer initialized successfully")
    
    async def cleanup(self):
        """Cleanup the activity streamer service."""
        logger.info("ActivityStreamer cleaned up successfully")
    
    async def stream_activity(
        self,
        activity_type: str,
        context: Optional[Dict[str, Any]] = None,
        duration_estimate: Optional[float] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream activity updates for a given activity type."""
        
        try:
            # Get activity messages for this type
            messages = self.activity_templates.get(activity_type, ["Working on your request..."])
            
            # Select appropriate message based on context
            message = self._select_activity_message(activity_type, messages, context)
            
            # Sanitize message if privacy mode is enabled
            if self.privacy_mode:
                message = self._sanitize_message(message, context)
            
            # Stream initial activity
            yield {
                "type": "activity",
                "activity": message,
                "activity_type": activity_type,
                "timestamp": datetime.utcnow().isoformat(),
                "progress": 0.0
            }
            
            # Stream progress updates if duration is estimated
            if duration_estimate and duration_estimate > 2.0:
                await self._stream_progress_updates(activity_type, message, duration_estimate)
            
        except Exception as e:
            logger.error("Activity streaming failed", activity_type=activity_type, error=str(e))
            yield {
                "type": "activity",
                "activity": "Processing your request...",
                "activity_type": "fallback",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def _stream_progress_updates(
        self,
        activity_type: str,
        message: str,
        duration: float
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream progress updates during long-running activities."""
        
        steps = max(3, min(10, int(duration)))  # 3-10 progress updates
        step_duration = duration / steps
        
        for i in range(1, steps):
            await asyncio.sleep(step_duration)
            
            progress = (i / steps) * 0.9  # Cap at 90% until completion
            
            yield {
                "type": "activity",
                "activity": message,
                "activity_type": activity_type,
                "timestamp": datetime.utcnow().isoformat(),
                "progress": progress
            }
    
    def _select_activity_message(
        self,
        activity_type: str,
        messages: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Select the most appropriate activity message based on context."""
        
        if not context:
            return messages[0]  # Default to first message
        
        # Context-aware message selection
        if activity_type == "analyzing":
            if context.get("has_files"):
                return "Analyzing your uploaded files..."
            elif context.get("is_complex_query"):
                return "Analyzing your complex request..."
            elif context.get("has_code"):
                return "Analyzing the code you provided..."
        
        elif activity_type == "searching":
            if context.get("search_query"):
                return "Searching for the latest information..."
            elif context.get("fact_checking"):
                return "Verifying current facts and data..."
        
        elif activity_type == "generating":
            if context.get("content_type") == "code":
                return "Generating code for you..."
            elif context.get("content_type") == "analysis":
                return "Preparing detailed analysis..."
            elif context.get("is_long_response"):
                return "Crafting a comprehensive response..."
        
        elif activity_type == "tool_executing":
            tool_name = context.get("tool_name", "")
            if tool_name:
                return f"Executing {tool_name}..."
            return "Running the requested tool..."
        
        # Default selection (first message or random for variety)
        import random
        return random.choice(messages) if len(messages) > 1 else messages[0]
    
    def _sanitize_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Sanitize activity message to remove sensitive information."""
        
        if not self.privacy_mode:
            return message
        
        sanitized = message
        
        # Remove sensitive patterns
        for pattern in self.sensitive_patterns:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
        
        # Remove specific user data from context if present
        if context:
            user_data = context.get("user_input", "")
            if user_data and len(user_data) > 50:  # Only redact long inputs
                # Replace specific mentions with generic terms
                sanitized = sanitized.replace(user_data[:20], "your request")
        
        return sanitized
    
    async def stream_tool_activity(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        estimated_duration: Optional[float] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream activity updates for tool execution."""
        
        # Create context for tool execution
        context = {
            "tool_name": tool_name,
            "has_input": bool(tool_input),
            "input_size": len(str(tool_input)) if tool_input else 0
        }
        
        # Generate tool-specific activity message
        activity_message = self._generate_tool_activity_message(tool_name, tool_input)
        
        yield {
            "type": "tool_activity",
            "activity": activity_message,
            "tool_name": tool_name,
            "timestamp": datetime.utcnow().isoformat(),
            "progress": 0.0
        }
        
        # Stream progress if duration is estimated
        if estimated_duration and estimated_duration > 1.0:
            async for update in self._stream_progress_updates("tool_executing", activity_message, estimated_duration):
                update["type"] = "tool_activity"
                update["tool_name"] = tool_name
                yield update
    
    def _generate_tool_activity_message(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> str:
        """Generate activity message for specific tool execution."""
        
        tool_messages = {
            "web_search": "Searching the web for information...",
            "image_generation": "Generating image based on your description...",
            "code_execution": "Running the code...",
            "file_analysis": "Analyzing the uploaded file...",
            "data_processing": "Processing the data...",
            "api_call": "Making API request...",
            "database_query": "Querying the database...",
            "calculation": "Performing calculations...",
            "translation": "Translating the text...",
            "summarization": "Summarizing the content..."
        }
        
        return tool_messages.get(tool_name, f"Executing {tool_name}...")
    
    async def stream_reasoning_activity(
        self,
        reasoning_steps: List[str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream activity updates for reasoning process."""
        
        for i, step in enumerate(reasoning_steps):
            # Sanitize reasoning step if needed
            sanitized_step = self._sanitize_message(step) if self.privacy_mode else step
            
            yield {
                "type": "reasoning_activity",
                "activity": f"Step {i + 1}: {sanitized_step}",
                "step_number": i + 1,
                "total_steps": len(reasoning_steps),
                "timestamp": datetime.utcnow().isoformat(),
                "progress": (i + 1) / len(reasoning_steps)
            }
            
            # Small delay between reasoning steps
            await asyncio.sleep(0.5)
    
    def create_completion_activity(
        self,
        activity_type: str = "completed"
    ) -> Dict[str, Any]:
        """Create completion activity message."""
        
        completion_messages = {
            "completed": "Response ready!",
            "analysis_completed": "Analysis complete!",
            "search_completed": "Search results ready!",
            "generation_completed": "Generation finished!",
            "tool_completed": "Tool execution complete!"
        }
        
        return {
            "type": "activity",
            "activity": completion_messages.get(activity_type, "Task completed!"),
            "activity_type": activity_type,
            "timestamp": datetime.utcnow().isoformat(),
            "progress": 1.0,
            "completed": True
        }
    
    def get_activity_summary(
        self,
        activities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate summary of all activities performed."""
        
        if not activities:
            return {"total_activities": 0, "duration": 0}
        
        activity_types = [a.get("activity_type", "unknown") for a in activities]
        start_time = activities[0].get("timestamp")
        end_time = activities[-1].get("timestamp")
        
        # Calculate duration if timestamps are available
        duration = 0
        if start_time and end_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                duration = (end_dt - start_dt).total_seconds()
            except Exception:
                pass
        
        return {
            "total_activities": len(activities),
            "activity_types": list(set(activity_types)),
            "duration": duration,
            "completed": any(a.get("completed", False) for a in activities)
        }
