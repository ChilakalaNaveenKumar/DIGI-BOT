"""
Test 3-Step Stepper Flow with Detailed JSON Logging

Logs all prompts, responses, and streaming data from each step to JSON files.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.comprehensive_tools import get_conditional_tools
from app.core.config import get_settings

class StepperLogger:
    """Logger to capture all stepper data."""
    
    def __init__(self):
        self.test_data = {
            "test_info": {
                "timestamp": datetime.now().isoformat(),
                "test_description": "3-Step Stepper Flow with Complete Logging"
            },
            "step_1": {
                "name": "Planning + Built-in Research",
                "prompt_sent": None,
                "streaming_chunks": [],
                "final_result": None
            },
            "step_2": {
                "name": "Custom Tool Execution", 
                "tools_to_execute": [],
                "tool_results": []
            },
            "step_3": {
                "name": "Final Analysis",
                "prompt_sent": None,
                "streaming_chunks": [],
                "final_result": None
            },
            "summary": {
                "total_chunks": 0,
                "tool_executions": 0,
                "success": False,
                "errors": []
            }
        }
        self.current_step = None
        self.chunk_count = 0
    
    def log_step1_prompt(self, messages: List[Dict], tools: List[Dict]):
        """Log Step 1 prompt details."""
        self.test_data["step_1"]["prompt_sent"] = {
            "messages": messages,
            "tools": [{"name": t.get("name", "unknown"), "type": t.get("type", "unknown")} for t in tools],
            "full_tools": tools,
            "enable_thinking": True,
            "complex_reasoning": True
        }
    
    def log_step3_prompt(self, messages: List[Dict]):
        """Log Step 3 prompt details."""
        self.test_data["step_3"]["prompt_sent"] = {
            "messages": messages,
            "tools": None,
            "enable_thinking": False,
            "complex_reasoning": False
        }
    
    def log_chunk(self, step: str, chunk: Dict[str, Any]):
        """Log streaming chunk."""
        self.chunk_count += 1
        self.test_data["summary"]["total_chunks"] = self.chunk_count
        
        chunk_data = {
            "chunk_number": self.chunk_count,
            "timestamp": datetime.now().isoformat(),
            "chunk": chunk
        }
        
        if step == "step_1":
            self.test_data["step_1"]["streaming_chunks"].append(chunk_data)
        elif step == "step_3":
            self.test_data["step_3"]["streaming_chunks"].append(chunk_data)
    
    def log_custom_tools(self, tools: List[Dict]):
        """Log custom tools detected."""
        self.test_data["step_2"]["tools_to_execute"] = tools
    
    def log_tool_result(self, tool_name: str, tool_result: Dict):
        """Log tool execution result."""
        self.test_data["step_2"]["tool_results"].append({
            "tool_name": tool_name,
            "result": tool_result,
            "timestamp": datetime.now().isoformat()
        })
        self.test_data["summary"]["tool_executions"] += 1
    
    def log_error(self, error: str):
        """Log error."""
        self.test_data["summary"]["errors"].append({
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_final_result(self, step: str, result: Dict):
        """Log final result for a step."""
        if step == "step_1":
            self.test_data["step_1"]["final_result"] = result
        elif step == "step_3":
            self.test_data["step_3"]["final_result"] = result
    
    def mark_success(self):
        """Mark test as successful."""
        self.test_data["summary"]["success"] = True
    
    def save_to_file(self, filename: str):
        """Save all logged data to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_data, f, indent=2, ensure_ascii=False)

async def test_stepper_with_detailed_logging():
    """Test the 3-step stepper with comprehensive logging."""
    
    logger = StepperLogger()
    
    print("🧪 Testing 3-Step Stepper Flow with Detailed Logging")
    print("=" * 60)
    
    try:
        # Initialize provider
        provider = AnthropicProvider()
        await provider.initialize()
        print("✅ Anthropic provider initialized")
        
        # Get settings
        settings = get_settings()
        print(f"✅ Using model: {settings.DEFAULT_AI_MODEL}")
        
        # Prepare test messages
        test_messages = [
            {
                "role": "system",
                "content": "You are Digi Setu AI, an advanced AI assistant with comprehensive capabilities. Provide well-formatted responses using markdown when it improves readability. When providing analysis, create comprehensive responses that naturally integrate visualizations and data throughout your analysis. Use tools as needed to support your insights, and reference the results of charts, tables, and searches directly in your analysis."
            },
            {
                "role": "user", 
                "content": "Can you analyze the current state of AI development in 2025? Please create a chart showing the major AI companies and their market positions, and provide insights about the competitive landscape."
            }
        ]
        
        # Get available tools
        available_tools = get_conditional_tools(
            has_audio=False,
            has_image=False,
            enable_audio_generation=False
        )
        
        tool_names = [tool.get('name', tool.get('type', 'unknown')) for tool in available_tools]
        print(f"✅ Available tools: {tool_names}")
        
        # Log Step 1 prompt
        logger.log_step1_prompt(test_messages, available_tools)
        
        print("\n🔄 Starting 3-Step Stepper with Detailed Logging...")
        print("-" * 50)
        
        # Execute stepper with detailed logging
        print("📍 Using New Stream Stepper")
        async for chunk in provider.stream_stepper(
            messages=test_messages,
            tools=available_tools,
            enable_thinking=True,
            complex_reasoning=True
        ):
            # Log every chunk from stepper
            chunk_type = chunk.get("type", "unknown")
            
            # Determine which step we're in based on chunk content
            if "Step 1:" in str(chunk) or chunk_type in ["message_start", "content_block_start", "content_block_delta"] and not hasattr(logger, '_step_detected'):
                logger.log_chunk("step_1", chunk)
                if not hasattr(logger, '_step1_printed'):
                    print("📍 Step 1: Planning + Built-in Research")
                    logger._step1_printed = True
            elif chunk_type == "tool_output":
                logger.log_chunk("step_2", chunk)
                if not hasattr(logger, '_step2_printed'):
                    print("📍 Step 2: Custom Tool Execution")
                    logger._step2_printed = True
                tool_name = chunk.get("tool_name", "unknown")
                logger.log_tool_result(tool_name, chunk)
                content_preview = str(chunk.get("content", ""))[:100]
                print(f"  🔧 Tool executed: {tool_name}")
                print(f"     Preview: {content_preview}...")
            elif "Step 3:" in str(chunk) or (hasattr(logger, '_step2_printed') and chunk_type in ["content_block_start", "content_block_delta"]):
                logger.log_chunk("step_3", chunk)
                if not hasattr(logger, '_step3_printed'):
                    print("📍 Step 3: Final Analysis")
                    logger._step3_printed = True
            else:
                # Default to step 1 logging
                logger.log_chunk("step_1", chunk)
            
            if chunk_type == "completion_finished":
                print("  ✅ Stepper completed")
                break
            elif chunk_type == "error":
                error_msg = chunk.get("error", "Unknown error")
                logger.log_error(f"Stepper error: {error_msg}")
                print(f"  ❌ Error: {error_msg}")
                break

        
        logger.mark_success()
        print("\n📊 Test Results:")
        print(f"  Total chunks processed: {logger.chunk_count}")
        print(f"  Tool executions: {logger.test_data['summary']['tool_executions']}")
        print("  ✅ Stepper flow completed successfully!")
        
    except Exception as e:
        error_msg = f"Test failed with error: {str(e)}"
        logger.log_error(error_msg)
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Save detailed logs to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stepper_detailed_log_{timestamp}.json"
        logger.save_to_file(filename)
        print(f"\n💾 Detailed logs saved to: {filename}")
        
        # Cleanup
        if 'provider' in locals():
            await provider.cleanup()
            print("🧹 Cleaned up provider")

if __name__ == "__main__":
    asyncio.run(test_stepper_with_detailed_logging())
