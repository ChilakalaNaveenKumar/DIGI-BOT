"""
Tool Call Manager

Handles efficient tool calling with limits and controls.
Prevents unnecessary tool calls and manages conversation state during tool use.
"""

import json
from typing import List, Dict, Any, Optional
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.chart_tools import get_chart_tools, process_tool_calls
from app.services.conversation_manager import ConversationManager

logger = structlog.get_logger(__name__)


class ToolCallManager:
    """Manages tool calls with efficiency controls."""
    
    def __init__(self, conversation_manager: ConversationManager):
        self.conv_manager = conversation_manager
        self.tool_call_count = 0
        self.MAX_TOOL_CALLS = 10  # Your specified limit
        self.MAX_ITERATIONS = self.MAX_TOOL_CALLS + 2  # Safety limit
        
    def create_controlled_tools(self) -> List[Dict]:
        """
        Define tools with built-in efficiency controls.
        Uses existing chart tools but with better descriptions.
        """
        base_tools = get_chart_tools()
        
        # Add efficiency guidance to tool descriptions
        for tool in base_tools:
            if 'description' in tool:
                tool['description'] += " Use only when necessary for data visualization."
        
        return base_tools
    
    def create_efficiency_system_prompt(self) -> str:
        """Create system prompt that encourages efficient tool use."""
        return f"""You are an efficient AI assistant with access to data visualization tools. Follow these guidelines:

🎯 **Tool Usage Efficiency:**
- You have a maximum of {self.MAX_TOOL_CALLS} tool calls for this conversation turn
- Current tool calls used: {self.tool_call_count}/{self.MAX_TOOL_CALLS}
- Only use tools when absolutely necessary to create visualizations or data tables
- Try to answer from your knowledge first
- If you must use tools, be strategic and efficient
- Don't create multiple similar charts - one comprehensive visualization is better

🧠 **Decision Process:**
1. Can I answer this without tools? (Prefer this)
2. If tools needed, what's the minimum number required?
3. Can I combine multiple requests into one tool call?

📊 **When to Use Tools:**
- User explicitly requests charts, graphs, or data tables
- Data visualization would significantly enhance the answer
- User provides data that needs to be visualized

❌ **When NOT to Use Tools:**
- For simple explanations or text-based answers
- When you can describe the concept clearly without visuals
- For follow-up questions that don't need new visualizations

Think step by step about whether you really need to use a tool before making the call."""
    
    async def process_conversation_with_tools(
        self, 
        conversation_id: Optional[int],
        user_message: str,
        conversation_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main processing function with efficiency controls.
        
        Returns streaming generator and final result data.
        """
        self.tool_call_count = 0  # Reset for each conversation turn
        
        try:
            # 1. TRIGGER: Prepare context when user sends message
            prepared_messages, new_summary = await self.conv_manager.prepare_conversation_context(
                conversation_id=conversation_id,
                new_user_message=user_message,
                existing_summary=conversation_summary
            )
            
            logger.info(f"Processing conversation with {len(prepared_messages)} messages")
            
            # 2. Initialize AI provider
            provider = AnthropicProvider()
            await provider.initialize()
            
            # 3. Create efficiency system prompt
            system_prompt = self.create_efficiency_system_prompt()
            
            # 4. Process conversation with tool call limits
            current_messages = prepared_messages.copy()
            all_responses = []
            
            for iteration in range(self.MAX_ITERATIONS):
                logger.info(f"--- Tool Call Iteration {iteration + 1} ---")
                
                # Update system prompt with current tool usage
                current_system_prompt = system_prompt.replace(
                    f"Current tool calls used: {0}/{self.MAX_TOOL_CALLS}",
                    f"Current tool calls used: {self.tool_call_count}/{self.MAX_TOOL_CALLS}"
                )
                
                # Add warning if approaching limit
                if self.tool_call_count >= self.MAX_TOOL_CALLS - 2:
                    current_system_prompt += f"\n\n⚠️ WARNING: You are approaching your tool call limit ({self.tool_call_count}/{self.MAX_TOOL_CALLS}). Use remaining calls wisely."
                
                # Force completion if limit reached
                if self.tool_call_count >= self.MAX_TOOL_CALLS:
                    current_system_prompt += f"\n\n🛑 IMPORTANT: You have reached your tool call limit ({self.MAX_TOOL_CALLS}). You must provide a final answer with the information you have. No more tool calls allowed."
                
                # Make streaming API call with reasoning enabled
                stream = provider.stream_completion(
                    messages=current_messages,
                    tools=self.create_controlled_tools() if self.tool_call_count < self.MAX_TOOL_CALLS else None,
                    enable_thinking=True
                )
                
                # Parse response
                content_blocks = response.get('content', [])
                text_content = ""
                tool_calls = []
                
                for block in content_blocks:
                    if block.get('type') == 'text':
                        text_content += block.get('text', '')
                    elif block.get('type') == 'tool_use':
                        if self.tool_call_count < self.MAX_TOOL_CALLS:
                            tool_calls.append(block)
                        else:
                            logger.warning(f"Blocking tool call - limit reached: {block.get('name')}")
                
                # Add assistant response to conversation
                assistant_message = {
                    "role": "assistant",
                    "content": content_blocks
                }
                current_messages.append(assistant_message)
                all_responses.append({
                    "type": "content",
                    "content": text_content,
                    "iteration": iteration + 1
                })
                
                # Process tool calls if any
                if tool_calls and self.tool_call_count < self.MAX_TOOL_CALLS:
                    logger.info(f"Processing {len(tool_calls)} tool calls")
                    
                    # Process tools and update count
                    tool_results = process_tool_calls(tool_calls)
                    self.tool_call_count += len(tool_calls)
                    
                    # Add tool results to responses
                    for result in tool_results:
                        all_responses.append({
                            "type": "tool_output",
                            "content": result.get('content', ''),
                            "iteration": iteration + 1
                        })
                    
                    # Add tool results to conversation
                    current_messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                    
                    logger.info(f"Tool calls used: {self.tool_call_count}/{self.MAX_TOOL_CALLS}")
                    
                else:
                    # No tool calls - conversation is complete
                    logger.info("✅ Conversation complete - no more tool calls needed")
                    break
                
                # Safety check - prevent infinite loops
                if self.tool_call_count >= self.MAX_TOOL_CALLS:
                    logger.info("🛑 Reached maximum tool calls - forcing completion")
                    
                    # One final call to get summary without tools
                    final_response = await provider.generate_completion(
                        messages=current_messages
                    )
                    
                    final_content = ""
                    final_blocks = final_response.get('content', [])
                    for block in final_blocks:
                        if block.get('type') == 'text':
                            final_content += block.get('text', '')
                    
                    if final_content.strip():
                        all_responses.append({
                            "type": "content", 
                            "content": final_content,
                            "iteration": iteration + 2,
                            "final": True
                        })
                    
                    break
            
            # Compile final assistant response
            final_assistant_content = ""
            for response in all_responses:
                if response["type"] == "content":
                    final_assistant_content += response["content"]
                elif response["type"] == "tool_output":
                    final_assistant_content += response["content"]
            
            return {
                "responses": all_responses,
                "final_assistant_content": final_assistant_content,
                "conversation_summary": new_summary,
                "tool_calls_used": self.tool_call_count,
                "efficiency_score": f"{self.tool_call_count}/{self.MAX_TOOL_CALLS}",
                "iterations": iteration + 1
            }
            
        except Exception as e:
            logger.error("Error in tool call processing", error=str(e))
            return {
                "responses": [{"type": "error", "content": f"Error: {str(e)}"}],
                "final_assistant_content": f"I encountered an error: {str(e)}",
                "conversation_summary": conversation_summary,
                "tool_calls_used": self.tool_call_count,
                "efficiency_score": f"{self.tool_call_count}/{self.MAX_TOOL_CALLS}",
                "iterations": 0
            }
    
    async def stream_responses(self, responses: List[Dict]) -> str:
        """
        Generator function to stream responses back to client.
        This would be used in the FastAPI streaming response.
        """
        for response in responses:
            if response["type"] == "content":
                yield f"data: {json.dumps({'type': 'content', 'content': response['content']})}\n\n"
            elif response["type"] == "tool_output":
                yield f"data: {json.dumps({'type': 'tool_output', 'content': response['content']})}\n\n"
            elif response["type"] == "error":
                yield f"data: {json.dumps({'type': 'error', 'content': response['content']})}\n\n"
