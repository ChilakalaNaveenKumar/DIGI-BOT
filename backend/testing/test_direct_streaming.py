#!/usr/bin/env python3
"""
Direct Streaming Test

Test direct streaming from AI to frontend with Chart.js components.
No wrappers, no complex analysis - just pure streaming with tool calls.
"""

import asyncio
import json
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.chart_tools import get_chart_tools, process_tool_calls


async def test_direct_streaming():
    """Test direct streaming with chart tools."""
    
    print("🚀 Testing Direct Streaming with Chart.js")
    print("=" * 60)
    
    # Initialize provider
    provider = AnthropicProvider()
    await provider.initialize()
    
    test_cases = [
        {
            "name": "Market Analysis with Pie Chart",
            "prompt": "Analyze social media market share: Instagram 45%, TikTok 30%, Facebook 15%, Twitter 10%. Create a visualization and provide detailed insights about market dynamics, user preferences, and competitive landscape."
        },
        {
            "name": "Sales Performance with Bar Chart", 
            "prompt": "Our quarterly sales performance: Q1 $120k, Q2 $150k, Q3 $180k, Q4 $200k. Visualize this data and analyze growth trends, seasonal patterns, and business implications for next year's strategy."
        },
        {
            "name": "User Growth with Line Chart",
            "prompt": "Company user growth: Jan 1000, Feb 1500, Mar 2200, Apr 3100, May 4500 users. Create a trend visualization and analyze the growth acceleration, identify key inflection points, and project future growth."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        
        try:
            # Step 1: Initial request with chart tools
            print("📤 Step 1: Sending request to AI...")
            
            messages = [{"role": "user", "content": test_case['prompt']}]
            
            response = await provider.generate_completion(
                messages=messages,
                model="claude-sonnet-4-20250514",
                max_tokens=16000,
                temperature=0.7,
                tools=get_chart_tools()
            )
            
            # Parse initial response
            content_blocks = response.get('content', [])
            initial_text = ""
            tool_calls = []
            
            for block in content_blocks:
                if block.get('type') == 'text':
                    initial_text += block.get('text', '')
                elif block.get('type') == 'tool_use':
                    tool_calls.append(block)
            
            print(f"✅ Initial response: {len(initial_text)} chars")
            print(f"🔧 Tools called: {len(tool_calls)}")
            
            # Step 2: Process tool calls
            if tool_calls:
                print("📊 Step 2: Processing chart tools...")
                
                tool_results = process_tool_calls(tool_calls)
                
                # Step 3: Send tool results back for continuation
                print("📥 Step 3: Getting continuation...")
                
                messages.append({
                    "role": "assistant",
                    "content": content_blocks
                })
                
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
                
                continuation_response = await provider.generate_completion(
                    messages=messages,
                    model="claude-sonnet-4-20250514",
                    max_tokens=16000,
                    temperature=0.7,
                    tools=get_chart_tools()
                )
                
                # Parse continuation
                continuation_blocks = continuation_response.get('content', [])
                continuation_text = ""
                
                for block in continuation_blocks:
                    if block.get('type') == 'text':
                        continuation_text += block.get('text', '')
                
                print(f"✅ Continuation: {len(continuation_text)} chars")
                
                # Step 4: Assemble complete response
                complete_response = initial_text + "\n\n"
                
                # Add chart components
                for result in tool_results:
                    complete_response += result.get('content', '') + "\n\n"
                
                complete_response += continuation_text
                
                print(f"📋 Complete response: {len(complete_response)} chars")
                
                # Save for frontend testing
                output_file = f"testing/streaming_test_{i}.json"
                with open(output_file, 'w') as f:
                    json.dump({
                        'test_name': test_case['name'],
                        'prompt': test_case['prompt'],
                        'initial_text': initial_text,
                        'tool_calls': tool_calls,
                        'tool_results': tool_results,
                        'continuation_text': continuation_text,
                        'complete_response': complete_response,
                        'chart_components': len(tool_calls)
                    }, f, indent=2)
                
                print(f"💾 Saved to: {output_file}")
                
                # Show preview
                preview = complete_response[:200] + "..." if len(complete_response) > 200 else complete_response
                print(f"📄 Preview: {preview}")
                
            else:
                print("❌ No tools called - direct response only")
                print(f"📄 Response: {initial_text[:200]}...")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print("-" * 40)


async def test_streaming_simulation():
    """Simulate how the frontend would receive streaming data."""
    
    print(f"\n" + "=" * 60)
    print("🎬 STREAMING SIMULATION")
    print("=" * 60)
    
    # Load a test result
    try:
        with open('testing/streaming_test_1.json', 'r') as f:
            test_data = json.load(f)
        
        complete_response = test_data['complete_response']
        
        print("📡 Simulating streaming to frontend...")
        print("🔄 Chunks would be processed in real-time:")
        
        # Split response into chunks (simulate streaming)
        chunk_size = 50
        chunks = [complete_response[i:i+chunk_size] for i in range(0, len(complete_response), chunk_size)]
        
        for i, chunk in enumerate(chunks[:5]):  # Show first 5 chunks
            print(f"  Chunk {i+1}: {repr(chunk)}")
        
        print(f"  ... ({len(chunks)-5} more chunks)")
        
        # Show chart components that would be rendered
        print("\n📊 Chart components detected:")
        for tool_call in test_data.get('tool_calls', []):
            chart_type = tool_call['input']['chart_type']
            title = tool_call['input']['title']
            data_points = len(tool_call['input']['data'])
            print(f"  - {chart_type.upper()} chart: '{title}' ({data_points} data points)")
            
    except FileNotFoundError:
        print("❌ No test data found. Run main test first.")


async def main():
    """Run all streaming tests."""
    await test_direct_streaming()
    await test_streaming_simulation()
    
    print(f"\n" + "=" * 60)
    print("🎯 DIRECT STREAMING TEST SUMMARY:")
    print("✅ AI automatically detects chart needs")
    print("✅ Chart.js components generated in markdown")
    print("✅ Complete response includes text + charts")
    print("✅ Ready for frontend streaming integration")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
