#!/usr/bin/env python3
"""
Test script to check if AI providers return reasoning content
"""

import asyncio
import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.ai_providers.openai_provider import OpenAIProvider
from app.services.ai_providers.grok_provider import GrokProvider


async def test_anthropic_reasoning():
    """Test if Anthropic provider returns reasoning content"""
    print("🧠 Testing Anthropic Claude reasoning...")
    
    try:
        provider = AnthropicProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "Explain quantum computing briefly"}]
        
        print("📝 Testing with reasoning enabled...")
        reasoning_chunks = []
        content_chunks = []
        
        async for chunk in provider.stream_completion(
            messages=messages,
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            enable_reasoning=True,
            reasoning_budget=500
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            
            if chunk_type == "reasoning":
                reasoning_chunks.append(content)
                print(f"🤔 REASONING: {content[:100]}...")
            elif chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content[:50]}...")
        
        print(f"\n✅ Anthropic Results:")
        print(f"   - Reasoning chunks: {len(reasoning_chunks)}")
        print(f"   - Content chunks: {len(content_chunks)}")
        
        if reasoning_chunks:
            print(f"   - Sample reasoning: {reasoning_chunks[0][:200]}...")
        else:
            print("   - ❌ No reasoning content found")
            
        await provider.cleanup()
        return len(reasoning_chunks) > 0
        
    except Exception as e:
        print(f"❌ Anthropic test failed: {e}")
        return False


async def test_openai_reasoning():
    """Test if OpenAI provider returns reasoning content"""
    print("\n🤖 Testing OpenAI GPT reasoning...")
    
    try:
        provider = OpenAIProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "Explain quantum computing briefly"}]
        
        print("📝 Testing with reasoning parameters...")
        reasoning_chunks = []
        content_chunks = []
        
        # Test with o1-preview model (reasoning model)
        async for chunk in provider.stream_completion(
            messages=messages,
            model="o1-preview",  # Use actual o1 reasoning model
            max_tokens=1000
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            
            if chunk_type == "reasoning":
                reasoning_chunks.append(content)
                print(f"🤔 REASONING: {content[:100]}...")
            elif chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content[:50]}...")
        
        print(f"\n✅ OpenAI Results:")
        print(f"   - Reasoning chunks: {len(reasoning_chunks)}")
        print(f"   - Content chunks: {len(content_chunks)}")
        
        if reasoning_chunks:
            print(f"   - Sample reasoning: {reasoning_chunks[0][:200]}...")
        else:
            print("   - ❌ No reasoning content found")
            
        await provider.cleanup()
        return len(reasoning_chunks) > 0
        
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False


async def test_grok_reasoning():
    """Test if Grok provider returns reasoning content"""
    print("\n🦾 Testing Grok reasoning...")
    
    try:
        provider = GrokProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "Explain quantum computing briefly"}]
        
        print("📝 Testing with thinking mode enabled...")
        reasoning_chunks = []
        content_chunks = []
        
        async for chunk in provider.stream_completion(
            messages=messages,
            model="grok-4",
            max_tokens=1000
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            
            if chunk_type == "reasoning":
                reasoning_chunks.append(content)
                print(f"🤔 REASONING: {content[:100]}...")
            elif chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content[:50]}...")
        
        print(f"\n✅ Grok Results:")
        print(f"   - Reasoning chunks: {len(reasoning_chunks)}")
        print(f"   - Content chunks: {len(content_chunks)}")
        
        if reasoning_chunks:
            print(f"   - Sample reasoning: {reasoning_chunks[0][:200]}...")
        else:
            print("   - ❌ No reasoning content found")
            
        await provider.cleanup()
        return len(reasoning_chunks) > 0
        
    except Exception as e:
        print(f"❌ Grok test failed: {e}")
        return False


async def main():
    """Run all reasoning tests"""
    print("🔍 Testing AI Provider Reasoning Capabilities\n")
    
    results = {}
    
    # Test each provider
    results['anthropic'] = await test_anthropic_reasoning()
    results['openai'] = await test_openai_reasoning()
    results['grok'] = await test_grok_reasoning()
    
    print(f"\n📊 SUMMARY:")
    print(f"   - Anthropic reasoning: {'✅' if results['anthropic'] else '❌'}")
    print(f"   - OpenAI reasoning: {'✅' if results['openai'] else '❌'}")
    print(f"   - Grok reasoning: {'✅' if results['grok'] else '❌'}")
    
    if not any(results.values()):
        print(f"\n⚠️  No providers are returning reasoning content!")
        print(f"   This means either:")
        print(f"   1. The API parameters are wrong")
        print(f"   2. The models don't support reasoning")
        print(f"   3. Our parsing logic is incorrect")
    else:
        print(f"\n✅ Some providers are working - check the streaming API integration")


if __name__ == "__main__":
    asyncio.run(main())
