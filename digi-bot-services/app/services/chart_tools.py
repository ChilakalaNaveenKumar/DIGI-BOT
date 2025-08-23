"""
Chart Tools for Direct Streaming

Simplified tools that work with Chart.js frontend.
No complex schemas - AI figures out data format automatically.
"""

import json
from typing import Dict, Any, List


def get_chart_tools() -> List[Dict[str, Any]]:
    """Micro chart tools - AI auto-detects best format."""
    return [
        {
            "name": "chartjs_tool",
            "description": "Create Chart.js charts when you want to increase learning experience to explain same concept charts, but check the possibility and correctness",
            "input_schema": {
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string", 
                        "enum": ["pie", "bar", "line", "doughnut", "radar", "polarArea", "bubble", "scatter"],
                        "description": "Chart type: pie (percentages), bar (categories), line (trends), scatter (x,y relationships)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title"
                    },
                    "data": {
                        "type": "array",
                        "description": "SIMPLE numerical data ONLY: [{label: 'Category', value: 123}] for bar/pie OR [{x: 1, y: 2}] for scatter"
                    }
                },
                "required": ["chart_type", "title", "data"]
            }
        },
        {
            "name": "data_table_tool", 
            "description": "Create DATA TABLES for complex structured data with multiple columns/fields. Use for: statistical measures, detailed comparisons, text data, formulas, explanations",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Table title"
                    },
                    "data": {
                        "type": "array",
                        "description": "Array of objects with multiple fields: [{field1: 'value', field2: 'value', field3: 'value'}]"
                    }
                },
                "required": ["title", "data"]
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
        
        if tool_name == 'chartjs_tool':
            markdown = execute_chart_tool(tool_call)
            result = {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": f"✅ Chart created!\n\n{markdown}\n\nChart is displayed above."
            }
            results.append(result)
            
        elif tool_name == 'data_table_tool':
            markdown = execute_table_tool(tool_call)
            result = {
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": f"✅ Table created!\n\n{markdown}\n\nTable is displayed above."
            }
            results.append(result)
    
    return results


def execute_table_tool(tool_call: Dict[str, Any]) -> str:
    """Execute table tool and return markdown component."""
    
    tool_input = tool_call.get('input', {})
    title = tool_input.get('title', 'Data Table')
    data = tool_input.get('data', [])
    
    # Generate table markdown
    markdown = f":::data-table\n"
    markdown += f"title: {title}\n"
    markdown += f"data: {json.dumps(data)}\n"
    markdown += ":::\n"
    
    return markdown


# Example usage for testing
if __name__ == "__main__":
    # Test tool execution
    test_tool_call = {
        "name": "chartjs_tool",
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
