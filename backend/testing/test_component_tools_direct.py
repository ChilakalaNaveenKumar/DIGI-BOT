#!/usr/bin/env python3
"""
Test Component Tools with Direct API

Test if Claude can automatically detect when to use component tools
during text generation, eliminating the need for 2000-token analysis.
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
        },
        {
            "name": "line_chart_tool",
            "description": "Generate line chart for trends and time-based data",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Chart title"
                    },
                    "data": {
                        "type": "array",
                        "description": "Array of data series",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "data": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "x": {"type": "string"},
                                            "y": {"type": "number"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "required": ["title", "data"]
            }
        },
        {
            "name": "data_table_tool",
            "description": "Generate data table for structured information with multiple attributes",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Table title"
                    },
                    "headers": {
                        "type": "array",
                        "description": "Column headers",
                        "items": {"type": "string"}
                    },
                    "rows": {
                        "type": "array",
                        "description": "Table rows",
                        "items": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                },
                "required": ["title", "headers", "rows"]
            }
        }
    ]

def process_tool_calls(tool_calls):
    """Process tool calls and return component markdown."""
    components = []
    
    for tool_call in tool_calls:
        tool_name = tool_call.get('name')
        input_data = tool_call.get('input', {})
        
        if tool_name == 'pie_chart_tool':
            # Generate pie chart markdown
            title = input_data.get('title', 'Pie Chart')
            data = input_data.get('data', [])
            
            markdown = f":::pie-chart\n"
            markdown += f"title: {title}\n"
            markdown += f"data: {json.dumps(data)}\n"
            markdown += ":::\n"
            
            components.append({
                'type': 'pie_chart',
                'markdown': markdown,
                'data': data,
                'title': title
            })
            
        elif tool_name == 'bar_chart_tool':
            # Generate bar chart markdown
            title = input_data.get('title', 'Bar Chart')
            data = input_data.get('data', [])
            
            markdown = f":::bar-chart\n"
            markdown += f"title: {title}\n"
            markdown += f"data: {json.dumps(data)}\n"
            markdown += ":::\n"
            
            components.append({
                'type': 'bar_chart',
                'markdown': markdown,
                'data': data,
                'title': title
            })
            
        elif tool_name == 'line_chart_tool':
            # Generate line chart markdown
            title = input_data.get('title', 'Line Chart')
            data = input_data.get('data', [])
            
            markdown = f":::line-chart\n"
            markdown += f"title: {title}\n"
            markdown += f"data: {json.dumps(data)}\n"
            markdown += ":::\n"
            
            components.append({
                'type': 'line_chart',
                'markdown': markdown,
                'data': data,
                'title': title
            })
            
        elif tool_name == 'data_table_tool':
            # Generate data table markdown
            title = input_data.get('title', 'Data Table')
            headers = input_data.get('headers', [])
            rows = input_data.get('rows', [])
            
            markdown = f":::data-table\n"
            markdown += f"title: {title}\n"
            markdown += f"headers: {json.dumps(headers)}\n"
            markdown += f"rows: {json.dumps(rows)}\n"
            markdown += ":::\n"
            
            components.append({
                'type': 'data_table',
                'markdown': markdown,
                'headers': headers,
                'rows': rows,
                'title': title
            })
    
    return components

async def test_component_detection():
    """Test if Claude can detect when to use component tools."""
    
    print("🧪 Testing Component Tool Detection")
    print("=" * 60)
    
    # Initialize Anthropic provider
    provider = AnthropicProvider()
    await provider.initialize()
    
    test_cases = [
        {
            "name": "EXPLICIT Pie Chart Request",
            "prompt": "I have market share data: Instagram 45%, TikTok 30%, Facebook 15%, Twitter 10%. Create a pie chart to visualize this percentage distribution and then provide a detailed analysis of what the data reveals about market dominance, competitive landscape, and strategic implications for each platform."
        },
        {
            "name": "EXPLICIT Bar Chart Request", 
            "prompt": "Here's our quarterly sales: Q1=$120k, Q2=$150k, Q3=$180k, Q4=$200k. Create a bar chart to compare these quarterly results and then analyze the trends in detail - discuss growth patterns, seasonal factors, and business implications."
        },
        {
            "name": "EXPLICIT Line Chart Request",
            "prompt": "User growth data: Jan=1000, Feb=1500, Mar=2200, Apr=3100, May=4500. Generate a line chart to show this growth trend over time and then provide comprehensive analysis of the growth pattern, acceleration points, and future projections."
        },
        {
            "name": "EXPLICIT Data Table Request",
            "prompt": "Product comparison data: Basic ($10/month, 5GB, email support), Pro ($25/month, 50GB, priority support), Enterprise ($100/month, unlimited, dedicated support). Create a data table to organize this information and then analyze the pricing strategy, value propositions, and target customer segments for each tier."
        },
        {
            "name": "Percentage Data (Should auto-detect pie chart)",
            "prompt": "The survey results show: 45% prefer Instagram, 30% prefer TikTok, 15% prefer Facebook, and 10% prefer Twitter. Analyze this social media preference data thoroughly - create appropriate visualizations and discuss user demographics, platform strengths, market trends, and implications for digital marketing strategies."
        },
        {
            "name": "Regular Text (Should NOT trigger tools)",
            "prompt": "Explain the concept of artificial intelligence and its applications in modern technology. Provide a comprehensive overview covering core concepts, implementation approaches, and future implications."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        
        start_time = time.time()
        
        try:
            response = await provider.generate_completion(
                messages=[{"role": "user", "content": test_case['prompt']}],
                model="claude-sonnet-4-20250514",
                max_tokens=16000,  # Increased to see full responses
                temperature=0.7,
                tools=get_component_tools()
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            # Parse response
            content_blocks = response.get('content', [])
            text_response = ""
            tool_calls = []
            
            for block in content_blocks:
                if block.get('type') == 'text':
                    text_response += block.get('text', '')
                elif block.get('type') == 'tool_use':
                    tool_calls.append({
                        'name': block.get('name'),
                        'input': block.get('input', {})
                    })
            
            print(f"⏱️  Response time: {response_time:.0f}ms")
            print(f"📝 Text length: {len(text_response)} chars")
            print(f"🔧 Tools called: {len(tool_calls)}")
            
            # Save full response to file for debugging
            response_file = f"testing/response_{i}_{test_case['name'].replace(' ', '_').replace('(', '').replace(')', '')}.json"
            with open(response_file, 'w') as f:
                json.dump({
                    'test_name': test_case['name'],
                    'prompt': test_case['prompt'],
                    'full_response': response,
                    'text_content': text_response,
                    'tool_calls': tool_calls,
                    'response_time_ms': response_time
                }, f, indent=2)
            print(f"📁 Full response saved to: {response_file}")
            
            if tool_calls:
                print("🎯 TOOLS DETECTED:")
                for j, tool_call in enumerate(tool_calls):
                    tool_name = tool_call.get('name')
                    tool_input = tool_call.get('input', {})
                    print(f"   - Tool {j+1}: {tool_name}")
                    print(f"     Input: {json.dumps(tool_input, indent=6)}")
                
                # Process tools to generate components
                components = process_tool_calls(tool_calls)
                print(f"📊 Components generated: {len(components)}")
                
                for component in components:
                    print(f"   - {component['type']}: {component['title']}")
                    print(f"     Markdown preview: {component['markdown'][:100]}...")
            else:
                print("❌ No tools called - Claude handled directly")
                print("🔍 CHECKING: Why no tools were called...")
                
                # Check if response mentions charts/visualization
                text_lower = text_response.lower()
                chart_keywords = ['chart', 'graph', 'visualiz', 'pie', 'bar', 'line', 'table']
                found_keywords = [kw for kw in chart_keywords if kw in text_lower]
                if found_keywords:
                    print(f"   ⚠️  Response mentions: {found_keywords} but no tools called!")
                else:
                    print(f"   ✅ Response doesn't mention visualization - correct behavior")
            
            # Analyze response structure in detail
            print(f"\n🔍 RESPONSE STRUCTURE ANALYSIS:")
            content_blocks = response.get('content', [])
            for j, block in enumerate(content_blocks):
                block_type = block.get('type')
                if block_type == 'text':
                    text_content = block.get('text', '')
                    print(f"   Block {j+1}: TEXT ({len(text_content)} chars)")
                    print(f"      Preview: {text_content[:100]}{'...' if len(text_content) > 100 else ''}")
                elif block_type == 'tool_use':
                    tool_name = block.get('name')
                    tool_input = block.get('input', {})
                    print(f"   Block {j+1}: TOOL_USE ({tool_name})")
                    print(f"      Data points: {len(tool_input.get('data', []))}")
                    print(f"      Title: {tool_input.get('title', 'N/A')}")
            
            print(f"\n💬 FULL TEXT RESPONSE:")
            print(f"   {text_response}")
            print(f"   (Length: {len(text_response)} characters)")
            
            # Show token usage details
            usage = response.get('usage', {})
            if usage:
                input_tokens = usage.get('input_tokens', 0)
                output_tokens = usage.get('output_tokens', 0)
                print(f"🪙 Token usage: {input_tokens} input + {output_tokens} output = {input_tokens + output_tokens} total")
                
            # Show stop reason
            stop_reason = response.get('stop_reason')
            print(f"🛑 Stop reason: {stop_reason}")
            if stop_reason == 'tool_use':
                print("   ⚠️  Claude stopped after calling tool - no continuation text!")
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            print(f"❌ Failed in {response_time:.0f}ms: {e}")
        
        print("-" * 40)

async def main():
    """Run component detection tests."""
    await test_component_detection()
    
    print(f"\n" + "=" * 60)
    print("🎯 COMPONENT TOOL DETECTION TEST SUMMARY:")
    print("✅ Testing if Claude can automatically detect data patterns")
    print("✅ Testing real-time tool calling during text generation") 
    print("✅ Testing elimination of 2000-token analysis overhead")
    print("✅ Measuring accuracy and timing of component detection")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
