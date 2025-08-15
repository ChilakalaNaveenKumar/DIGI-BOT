#!/usr/bin/env python3
import openai
import os

from dotenv import load_dotenv
load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "generateImage",
            "description": "Generate an image using AI",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string", 
                        "description": "Image description"
                    }
                },
                "required": ["prompt"]
            }
        }
    }
]

print("Testing OpenAI streaming with tools...")

try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Create a donut chart showing product inventory"}],
        tools=tools,
        stream=True
    )
    print("Streaming started!")
    
    for chunk in response:
        if chunk.choices[0].delta.content:
            print("Content:", chunk.choices[0].delta.content)
        if hasattr(chunk.choices[0].delta, 'tool_calls') and chunk.choices[0].delta.tool_calls:
            print("Tool call chunk:", chunk.choices[0].delta.tool_calls)
            
    print("Streaming completed!")
    
except Exception as e:
    print("Streaming Error:", str(e))
