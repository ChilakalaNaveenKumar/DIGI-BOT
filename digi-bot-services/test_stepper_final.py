"""
Final comprehensive test of the 3-step stepper
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.comprehensive_tools import get_conditional_tools

async def test_final_stepper():
    """Final comprehensive test."""
    
    print("🧪 Final 3-Step Stepper Test")
    print("=" * 40)
    
    try:
        # Initialize provider
        provider = AnthropicProvider()
        await provider.initialize()
        print("✅ Provider initialized")
        
        # Test messages that should trigger custom tools
        test_messages = [
            {
                "role": "system",
                "content": "You are Digi Setu AI, an advanced AI assistant with comprehensive capabilities."
            },
            {
                "role": "user", 
                "content": "Analyze the current state of AI development in 2025. I need a comprehensive analysis with charts showing market positions and tables with detailed data."
            }
        ]
        
        # Get available tools
        available_tools = get_conditional_tools(
            has_audio=False,
            has_image=False,
            enable_audio_generation=False
        )
        
        print(f"📋 Available tools: {[t.get('name') for t in available_tools]}")
        
        steps_executed = []
        tool_executions = 0
        chunks_processed = 0
        
        print("\n🔄 Executing 3-Step Stepper...")
        print("-" * 30)
        
        # Execute stepper
        async for chunk in provider.stream_stepper(
            messages=test_messages,
            tools=available_tools,
            enable_thinking=True,
            complex_reasoning=True
        ):
            chunks_processed += 1
            chunk_type = chunk.get("type", "unknown")
            
            # Track steps based on logs
            if "Step 1:" in str(chunk) and "Step 1" not in steps_executed:
                steps_executed.append("Step 1")
                print("📍 Step 1: Planning + Built-in Research")
            elif "Step 2:" in str(chunk) and "Step 2" not in steps_executed:
                steps_executed.append("Step 2")
                print("📍 Step 2: Custom Tool Execution")
            elif "Step 3:" in str(chunk) and "Step 3" not in steps_executed:
                steps_executed.append("Step 3")
                print("📍 Step 3: Final Analysis")
            
            # Track tool executions
            if chunk_type == "tool_output":
                tool_executions += 1
                tool_name = chunk.get("tool_name", "unknown")
                print(f"  🔧 Tool executed: {tool_name}")
            
            # Check for completion
            if chunk_type == "completion_finished":
                print("  ✅ Stepper completed")
                break
            elif chunk_type == "error":
                print(f"  ❌ Error: {chunk.get('error')}")
                break
        
        print(f"\n📊 Final Results:")
        print(f"  Steps executed: {steps_executed}")
        print(f"  Total chunks: {chunks_processed}")
        print(f"  Tool executions: {tool_executions}")
        
        if len(steps_executed) == 3 and tool_executions > 0:
            print("  🎉 SUCCESS: All 3 steps executed with tools!")
        elif len(steps_executed) == 1 and tool_executions == 0:
            print("  ⚠️  PARTIAL: Only Step 1 executed (no custom tools triggered)")
        else:
            print("  ❓ UNEXPECTED: Check implementation")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'provider' in locals():
            await provider.cleanup()

if __name__ == "__main__":
    asyncio.run(test_final_stepper())
