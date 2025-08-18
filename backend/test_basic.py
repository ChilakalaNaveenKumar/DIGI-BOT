#!/usr/bin/env python3
"""
Test basic API calls without reasoning to see if providers work
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.ai_providers.openai_provider import OpenAIProvider
from app.services.ai_providers.grok_provider import GrokProvider


async def test_basic_anthropic():
    """Test basic Anthropic API call"""
    print("🧠 Testing basic Anthropic Claude...")
    
    try:
        provider = AnthropicProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "Say hello"}]
        
        # Basic streaming without reasoning
        content_chunks = []
        async for chunk in provider.stream_completion(
            messages=messages,
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            enable_reasoning=False  # No reasoning
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            
            if chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content}")
        
        print(f"✅ Anthropic basic test: {len(content_chunks)} chunks")
        await provider.cleanup()
        return len(content_chunks) > 0
        
    except Exception as e:
        print(f"❌ Anthropic basic test failed: {e}")
        return False


async def test_basic_openai():
    """Test basic OpenAI API call"""
    print("\n🤖 Testing basic OpenAI GPT...")
    
    try:
        provider = OpenAIProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "Say hello"}]
        
        # Use GPT-4o (real model)
        content_chunks = []
        async for chunk in provider.stream_completion(
            messages=messages,
            model="gpt-4o",  # Use real model
            max_tokens=100
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            
            if chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content}")
        
        print(f"✅ OpenAI basic test: {len(content_chunks)} chunks")
        await provider.cleanup()
        return len(content_chunks) > 0
        
    except Exception as e:
        print(f"❌ OpenAI basic test failed: {e}")
        return False


async def test_basic_grok():
    """Test basic Grok API call"""
    print("\n🦾 Testing basic Grok...")
    
    try:
        provider = GrokProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "Say hello"}]
        
        # Basic streaming
        content_chunks = []
        async for chunk in provider.stream_completion(
            messages=messages,
            model="grok-4",
            max_tokens=100
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            
            if chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content}")
        
        print(f"✅ Grok basic test: {len(content_chunks)} chunks")
        await provider.cleanup()
        return len(content_chunks) > 0
        
    except Exception as e:
        print(f"❌ Grok basic test failed: {e}")
        return False


async def main():
    """Run basic API tests"""
    print("🔍 Testing Basic AI Provider Functionality\n")
    
    results = {}
    
    # Test each provider
    results['anthropic'] = await test_basic_anthropic()
    results['openai'] = await test_basic_openai()
    results['grok'] = await test_basic_grok()
    
    print(f"\n📊 BASIC API SUMMARY:")
    print(f"   - Anthropic working: {'✅' if results['anthropic'] else '❌'}")
    print(f"   - OpenAI working: {'✅' if results['openai'] else '❌'}")
    print(f"   - Grok working: {'✅' if results['grok'] else '❌'}")
    
    if any(results.values()):
        print(f"\n✅ Some providers work - reasoning issue is separate")
    else:
        print(f"\n❌ No providers work - check API keys and configuration")


if __name__ == "__main__":
    asyncio.run(main())
