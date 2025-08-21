#!/usr/bin/env python3
"""
Simple Token Test for Current Backend

Quick test to see what's happening with our current Anthropic implementation.
"""

import asyncio
import json
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.core.config import get_settings

async def test_simple_queries():
    """Test simple queries to see token usage."""
    
    print("🧪 Testing Current Backend Anthropic Implementation")
    print("=" * 60)
    
    # Check settings
    settings = get_settings()
    print(f"API Key configured: {'✅' if settings.ANTHROPIC_API_KEY else '❌'}")
    
    # Initialize provider
    provider = AnthropicProvider()
    try:
        await provider.initialize()
        print("Provider initialized: ✅")
    except Exception as e:
        print(f"Provider initialization failed: ❌ {e}")
        return
    
    # Test queries
    test_queries = [
        "What is 2+2?",
        "Explain Python in 50 words.",
        "Write a simple hello world function in Python with comments."
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i} ---")
        print(f"Query: {query}")
        
        try:
            messages = [{"role": "user", "content": query}]
            
            # Test non-streaming
            print("Testing non-streaming...")
            response = await provider.generate_completion(
                messages=messages,
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                temperature=0.7
            )
            
            print(f"Response type: {type(response)}")
            print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
            
            if isinstance(response, dict):
                if 'usage' in response:
                    usage = response['usage']
                    print(f"Input tokens: {usage.get('input_tokens', 'N/A')}")
                    print(f"Output tokens: {usage.get('output_tokens', 'N/A')}")
                    print(f"Total tokens: {usage.get('input_tokens', 0) + usage.get('output_tokens', 0)}")
                else:
                    print("No usage info in response")
                
                if 'content' in response:
                    content = response['content']
                    if isinstance(content, list) and content:
                        text = content[0].get('text', '') if isinstance(content[0], dict) else str(content[0])
                        print(f"Response preview: {text[:100]}...")
                    else:
                        print(f"Content: {content}")
                else:
                    print("No content in response")
            
            print("✅ Non-streaming test successful")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test_simple_queries())
