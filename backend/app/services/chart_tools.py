"""
Chart Tools for Direct Streaming

Simplified tools that work with Chart.js frontend.
No complex schemas - AI figures out data format automatically.
"""

import json
from typing import Dict, Any, List


def get_chart_tools() -> List[Dict[str, Any]]:
    """Get simplified chart tools for AI to use."""
    return [
        {
            "name": "data_visualization_tool",
            "description": "Create charts (pie, bar, line) for data visualization using Chart.js",
            "input_schema": {
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string", 
                        "enum": ["pie", "bar", "line"],
                        "description": "Type of chart to create"
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title"
                    },
                    "data": {
                        "type": "array",
                        "description": "Chart data - AI determines format based on chart type"
                    }
                },
                "required": ["chart_type", "title", "data"]
            }
        }
    ]


def execute_chart_tool(tool_call: Dict[str, Any]) -> str:
    """Execute chart tool and return markdown component."""
    
    tool_input = tool_call.get('input', {})
    chart_type = tool_input.get('chart_type', 'bar')
    title = tool_input.get('title', 'Chart')
    data = tool_input.get('data', [])
    
    # Generate Chart.js compatible markdown
    markdown = f":::{chart_type}-chart\n"
    markdown += f"title: {title}\n"
    markdown += f"data: {json.dumps(data)}\n"
    markdown += ":::\n"
    
    return markdown


def process_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process tool calls and return tool results for continuation."""
    
    results = []
    
    for tool_call in tool_calls:
        tool_name = tool_call.get('name')
        tool_id = tool_call.get('id')
        
        if tool_name == 'data_visualization_tool':
            # Execute the tool
            markdown = execute_chart_tool(tool_call)
            
            # Create tool result
            result = {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": f"✅ Chart created successfully!\n\n{markdown}\n\nThe chart has been generated and will be displayed. You can now continue with your analysis."
            }
            results.append(result)
    
    return results


# Example usage for testing
if __name__ == "__main__":
    # Test tool execution
    test_tool_call = {
        "name": "data_visualization_tool",
        "id": "test_123",
        "input": {
            "chart_type": "pie",
            "title": "Market Share Distribution", 
            "data": [
                {"label": "Instagram", "value": 45, "percentage": 45},
                {"label": "TikTok", "value": 30, "percentage": 30},
                {"label": "Facebook", "value": 15, "percentage": 15},
                {"label": "Twitter", "value": 10, "percentage": 10}
            ]
        }
    }
    
    result = execute_chart_tool(test_tool_call)
    print("Generated markdown:")
    print(result)
