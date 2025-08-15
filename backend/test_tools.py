#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import openai
import os
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# EXACT working format from examples
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g. San Francisco"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

print("Testing OpenAI tool calling with exact working format...")

try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "What time is it in Tokyo?"}],
        tools=tools,
        tool_choice="auto"
    )
    print("SUCCESS! Tool calling works!")
    print(f"Response: {response.choices[0].message}")
    if response.choices[0].message.tool_calls:
        print(f"Tool calls: {response.choices[0].message.tool_calls}")
    else:
        print("No tool calls made")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50)
print("Testing with streaming...")

try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "What time is it in Tokyo?"}],
        tools=tools,
        tool_choice="auto",
        stream=True
    )
    print("Streaming started!")
    for chunk in response:
        if chunk.choices[0].delta.content:
            print(f"Content: {chunk.choices[0].delta.content}")
        if hasattr(chunk.choices[0].delta, 'tool_calls') and chunk.choices[0].delta.tool_calls:
            print(f"Tool call: {chunk.choices[0].delta.tool_calls}")
except Exception as e:
    print(f"Streaming Error: {e}")
