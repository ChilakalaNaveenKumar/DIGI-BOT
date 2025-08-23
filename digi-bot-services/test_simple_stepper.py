"""
Simple test to verify the stepper is working correctly
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.comprehensive_tools import get_conditional_tools
from app.core.config import get_settings

async def test_simple_stepper():
    """Simple test to verify stepper behavior."""
    
    print("🧪 Simple Stepper Test")
    print("=" * 30)
    
    try:
        # Initialize provider
        provider = AnthropicProvider()
        await provider.initialize()
        print("✅ Provider initialized")
        
        # Prepare test messages
        test_messages = [
            {
                "role": "system",
                "content": "You are Digi Setu AI, an advanced AI assistant."
            },
            {
                "role": "user", 
                "content": "Analyze AI companies and create a chart showing their market positions."
            }
        ]
        
        # Get available tools (this should be ignored by stepper in Step 1)
        available_tools = get_conditional_tools(
            has_audio=False,
            has_image=False,
            enable_audio_generation=False
        )
        
        print(f"📋 Tools passed to stepper: {[t.get('name') for t in available_tools]}")
        
        step_count = 0
        tool_executions = 0
        
        # Execute stepper
        async for chunk in provider.stream_stepper(
            messages=test_messages,
            tools=available_tools,
            enable_thinking=True,
            complex_reasoning=True
        ):
            chunk_type = chunk.get("type", "unknown")
            
            # Track steps
            if "Step 1:" in str(chunk):
                step_count = 1
                print("📍 Step 1: Planning + Research")
            elif "Step 2:" in str(chunk):
                step_count = 2
                print("📍 Step 2: Tool Execution")
            elif "Step 3:" in str(chunk):
                step_count = 3
                print("📍 Step 3: Final Analysis")
            
            # Track tool executions
            if chunk_type == "tool_output":
                tool_executions += 1
                tool_name = chunk.get("tool_name", "unknown")
                print(f"  🔧 Tool executed: {tool_name}")
            
            # Check for completion
            if chunk_type == "completion_finished":
                print("  ✅ Step completed")
                break
            elif chunk_type == "error":
                print(f"  ❌ Error: {chunk.get('error')}")
                break
        
        print(f"\n📊 Results:")
        print(f"  Steps executed: {step_count}")
        print(f"  Tool executions: {tool_executions}")
        print("  ✅ Test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'provider' in locals():
            await provider.cleanup()

if __name__ == "__main__":
    asyncio.run(test_simple_stepper())
