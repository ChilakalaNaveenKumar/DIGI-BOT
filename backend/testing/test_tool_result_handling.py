#!/usr/bin/env python3
"""
Test Tool Result Handling

Test the complete flow:
1. Claude calls tool with data
2. We process tool and return result
3. Claude continues with detailed analysis

This is the REAL use case for component generation!
"""

import asyncio
import json
import sys
import os
import time

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.ai_providers.anthropic_provider import AnthropicProvider

def get_component_tools():
    """Define component tools that Claude can call when it detects data."""
    return [
        {
            "name": "pie_chart_tool",
            "description": "Generate pie chart when content has percentage or proportional data",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Chart title"
                    },
                    "data": {
                        "type": "array",
                        "description": "Array of data points with label, value, and percentage",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "value": {"type": "number"},
                                "percentage": {"type": "number"}
                            }
                        }
                    }
                },
                "required": ["title", "data"]
            }
        },
        {
            "name": "bar_chart_tool", 
            "description": "Generate bar chart for comparing quantities across categories",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Chart title"
                    },
                    "data": {
                        "type": "array",
                        "description": "Array of categories with labels and values",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "value": {"type": "number"}
                            }
                        }
                    }
                },
                "required": ["title", "data"]
            }
        }
    ]

def execute_tool_call(tool_call):
    """Execute tool call and return the result that Claude expects."""
    tool_name = tool_call.get('name')
    tool_id = tool_call.get('id')
    input_data = tool_call.get('input', {})
    
    if tool_name == 'pie_chart_tool':
        # Generate pie chart markdown
        title = input_data.get('title', 'Pie Chart')
        data = input_data.get('data', [])
        
        markdown = f":::pie-chart\n"
        markdown += f"title: {title}\n"
        markdown += f"data: {json.dumps(data)}\n"
        markdown += ":::\n"
        
        return {
            "type": "tool_result",
            "tool_use_id": tool_id,
            "content": f"✅ Pie chart created successfully!\n\n{markdown}\n\nThe chart has been generated with {len(data)} data points. You can now provide detailed analysis of this data."
        }
        
    elif tool_name == 'bar_chart_tool':
        # Generate bar chart markdown
        title = input_data.get('title', 'Bar Chart')
        data = input_data.get('data', [])
        
        markdown = f":::bar-chart\n"
        markdown += f"title: {title}\n"
        markdown += f"data: {json.dumps(data)}\n"
        markdown += ":::\n"
        
        return {
            "type": "tool_result", 
            "tool_use_id": tool_id,
            "content": f"✅ Bar chart created successfully!\n\n{markdown}\n\nThe chart has been generated with {len(data)} data points. You can now analyze the trends and patterns."
        }
    
    return {
        "type": "tool_result",
        "tool_use_id": tool_id,
        "content": f"❌ Unknown tool: {tool_name}"
    }

async def test_complete_flow():
    """Test the complete tool result handling flow."""
    
    print("🔄 Testing Complete Tool Result Handling Flow")
    print("=" * 60)
    
    # Initialize Anthropic provider
    provider = AnthropicProvider()
    await provider.initialize()
    
    test_cases = [
        {
            "name": "Market Share Analysis with Tool Results",
            "prompt": "Analyze this market share data: Instagram 45%, TikTok 30%, Facebook 15%, Twitter 10%. Create a pie chart and then provide comprehensive analysis covering market dominance, competitive dynamics, user demographics, and strategic implications for each platform."
        },
        {
            "name": "Sales Performance with Tool Results", 
            "prompt": "Examine our quarterly sales: Q1=$120k, Q2=$150k, Q3=$180k, Q4=$200k. Create a bar chart and then analyze growth patterns, identify trends, discuss seasonal factors, and provide recommendations for next year."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        
        # Step 1: Initial request with tools
        print("📤 Step 1: Sending initial request to Claude...")
        
        messages = [{"role": "user", "content": test_case['prompt']}]
        
        start_time = time.time()
        
        try:
            response = await provider.generate_completion(
                messages=messages,
                model="claude-sonnet-4-20250514",
                max_tokens=16000,
                temperature=0.7,
                tools=get_component_tools()
            )
            
            step1_time = time.time() - start_time
            
            # Parse initial response
            content_blocks = response.get('content', [])
            text_response = ""
            tool_calls = []
            
            for block in content_blocks:
                if block.get('type') == 'text':
                    text_response += block.get('text', '')
                elif block.get('type') == 'tool_use':
                    tool_calls.append(block)
            
            print(f"✅ Step 1 completed in {step1_time*1000:.0f}ms")
            print(f"   Initial text: {text_response}")
            print(f"   Tools called: {len(tool_calls)}")
            
            if not tool_calls:
                print("❌ No tools called - skipping test")
                continue
            
            # Step 2: Execute tools and prepare results
            print("\n🔧 Step 2: Executing tools...")
            
            tool_results = []
            for tool_call in tool_calls:
                tool_result = execute_tool_call(tool_call)
                tool_results.append(tool_result)
                print(f"   ✅ Executed {tool_call.get('name')}")
            
            # Step 3: Send tool results back to Claude for continuation
            print("\n📥 Step 3: Sending tool results back to Claude...")
            
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": content_blocks
            })
            
            # Add tool results
            messages.append({
                "role": "user", 
                "content": tool_results
            })
            
            step3_start = time.time()
            
            # Get continuation from Claude
            continuation_response = await provider.generate_completion(
                messages=messages,
                model="claude-sonnet-4-20250514",
                max_tokens=16000,
                temperature=0.7,
                tools=get_component_tools()  # Keep tools available
            )
            
            step3_time = time.time() - step3_start
            total_time = time.time() - start_time
            
            # Parse continuation response
            continuation_blocks = continuation_response.get('content', [])
            continuation_text = ""
            
            for block in continuation_blocks:
                if block.get('type') == 'text':
                    continuation_text += block.get('text', '')
            
            print(f"✅ Step 3 completed in {step3_time*1000:.0f}ms")
            print(f"📊 Total flow time: {total_time*1000:.0f}ms")
            
            # Show results
            print(f"\n📋 COMPLETE FLOW RESULTS:")
            print(f"   Initial response: {len(text_response)} chars")
            print(f"   Tool calls made: {len(tool_calls)}")
            print(f"   Continuation text: {len(continuation_text)} chars")
            print(f"   Total response: {len(text_response + continuation_text)} chars")
            
            # Show token usage
            initial_usage = response.get('usage', {})
            continuation_usage = continuation_response.get('usage', {})
            
            total_input = initial_usage.get('input_tokens', 0) + continuation_usage.get('input_tokens', 0)
            total_output = initial_usage.get('output_tokens', 0) + continuation_usage.get('output_tokens', 0)
            
            print(f"🪙 Token usage: {total_input} input + {total_output} output = {total_input + total_output} total")
            
            # Construct complete text including tool results
            tool_results_text = ""
            for tool_result in tool_results:
                tool_results_text += tool_result.get('content', '') + "\n\n"
            
            complete_text = text_response + "\n\n" + tool_results_text + continuation_text
            
            # Save complete response
            complete_response = {
                'test_name': test_case['name'],
                'prompt': test_case['prompt'],
                'step1_response': response,
                'step1_text': text_response,
                'tool_calls': tool_calls,
                'tool_results': tool_results,
                'tool_results_text': tool_results_text,
                'step3_response': continuation_response,
                'continuation_text': continuation_text,
                'complete_text': complete_text,
                'total_time_ms': total_time * 1000,
                'total_tokens': total_input + total_output
            }
            
            response_file = f"testing/complete_flow_{i}_{test_case['name'].replace(' ', '_').replace('(', '').replace(')', '')}.json"
            with open(response_file, 'w') as f:
                json.dump(complete_response, f, indent=2)
            print(f"📁 Complete flow saved to: {response_file}")
            
            # Show preview of continuation
            if continuation_text:
                preview = continuation_text[:300] + "..." if len(continuation_text) > 300 else continuation_text
                print(f"\n💬 CONTINUATION PREVIEW:")
                print(f"   {preview}")
            else:
                print(f"\n❌ No continuation text received!")
                
        except Exception as e:
            total_time = time.time() - start_time
            print(f"❌ Test failed in {total_time*1000:.0f}ms: {e}")
        
        print("-" * 40)

async def main():
    """Run complete tool result handling tests."""
    await test_complete_flow()
    
    print(f"\n" + "=" * 60)
    print("🎯 TOOL RESULT HANDLING TEST SUMMARY:")
    print("✅ Testing complete flow: Request → Tool Call → Tool Result → Continuation")
    print("✅ This is the REAL use case for component generation")
    print("✅ Both visualization AND detailed analysis in one flow")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
