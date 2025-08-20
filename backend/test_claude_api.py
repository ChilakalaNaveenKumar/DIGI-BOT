#!/usr/bin/env python3
"""
Test Claude API directly to see if it's working
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_providers.anthropic_provider import AnthropicProvider

async def test_claude_api():
    """Test Claude API directly"""
    
    provider = AnthropicProvider()
    await provider.initialize()
    
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Respond with a simple JSON object."
        },
        {
            "role": "user", 
            "content": "Analyze this data: Revenue $100K. Should this generate a chart? Respond with JSON: {\"decision\": \"GENERATE_NOW\" or \"NO_COMPONENT\", \"confidence\": 0.8}"
        }
    ]
    
    print("Testing Claude API...")
    
    try:
        response_content = ""
        
        # Test with timeout
        async def collect_response():
            content = ""
            async for chunk in provider.stream_completion(
                messages=messages,
                model="claude-opus-4-1-20250805",
                max_tokens=500,
                temperature=0.2,
                enable_thinking=True
            ):
                if chunk.get("type") == "content":
                    content += chunk.get("content", "")
                    print(f"Content chunk: {chunk.get('content', '')}")
                elif chunk.get("type") == "thinking":
                    print(f"Thinking: {chunk.get('content', '')}")
            return content
        
        response_content = await asyncio.wait_for(collect_response(), timeout=30.0)
        
        print(f"✅ Claude API working! Response: {response_content}")
        
    except asyncio.TimeoutError:
        print("❌ Claude API timed out after 30 seconds")
    except Exception as e:
        print(f"❌ Claude API error: {str(e)}")
    
    await provider.cleanup()

if __name__ == "__main__":
    asyncio.run(test_claude_api())
