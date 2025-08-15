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
            "description": "Generate an image using DALL-E 3. Call this function when the user asks for any visual content, charts, diagrams, or images.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string", 
                        "description": "Detailed description of the image to generate"
                    }
                },
                "required": ["prompt"]
            }
        }
    }
]

print("Testing with explicit image request...")

try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI assistant that can generate images using the generateImage function. When users ask for visual content, charts, or images, use the generateImage function."},
            {"role": "user", "content": "Please generate an image of a donut chart showing product inventory data"}
        ],
        tools=tools,
        stream=True
    )
    
    print("Streaming started!")
    tool_calls_found = False
    
    for chunk in response:
        if chunk.choices[0].delta.content:
            print("Content:", chunk.choices[0].delta.content)
        if hasattr(chunk.choices[0].delta, 'tool_calls') and chunk.choices[0].delta.tool_calls:
            print("TOOL CALL FOUND:", chunk.choices[0].delta.tool_calls)
            tool_calls_found = True
            
    if not tool_calls_found:
        print("NO TOOL CALLS MADE")
    else:
        print("SUCCESS: Tool calls were made!")
        
except Exception as e:
    print("Error:", str(e))
