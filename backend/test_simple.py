#!/usr/bin/env python3
import openai
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get current time",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

print("Testing OpenAI tool calling...")

try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "What time is it?"}],
        tools=tools,
        tool_choice="auto"
    )
    print("SUCCESS! Tool calling works!")
    print("Response:", response.choices[0].message.content)
    if response.choices[0].message.tool_calls:
        print("Tool calls found:", len(response.choices[0].message.tool_calls))
        for tc in response.choices[0].message.tool_calls:
            print("- Tool:", tc.function.name)
    else:
        print("No tool calls made")
except Exception as e:
    print("Error:", str(e))
