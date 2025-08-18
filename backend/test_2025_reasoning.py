#!/usr/bin/env python3
"""
Test script for 2025 AI models with correct reasoning parameters
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.services.ai_providers.openai_provider import OpenAIProvider
from app.services.ai_providers.grok_provider import GrokProvider


async def test_claude_4_reasoning():
    """Test Claude 4 models with thinking parameter"""
    print("🧠 Testing Claude 4 (2025) with thinking...")
    
    try:
        provider = AnthropicProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "Explain quantum computing step by step"}]
        
        # Test Claude Opus 4 with thinking
        print("📝 Testing Claude Opus 4 with thinking parameter...")
        reasoning_chunks = []
        content_chunks = []
        
        async for chunk in provider.stream_completion(
            messages=messages,
            model="claude-opus-4-20250514",  # 2025 Claude 4 model
            max_tokens=2000,
            enable_reasoning=True,
            reasoning_budget=1000
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            
            if chunk_type == "reasoning":
                reasoning_chunks.append(content)
                print(f"🤔 REASONING: {content[:100]}...")
            elif chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content[:50]}...")
        
        print(f"\n✅ Claude 4 Results:")
        print(f"   - Model: claude-opus-4-20250514")
        print(f"   - Reasoning chunks: {len(reasoning_chunks)}")
        print(f"   - Content chunks: {len(content_chunks)}")
        
        if reasoning_chunks:
            print(f"   - Sample reasoning: {reasoning_chunks[0][:200]}...")
        else:
            print("   - ❌ No reasoning content found")
            
        await provider.cleanup()
        return len(reasoning_chunks) > 0
        
    except Exception as e:
        print(f"❌ Claude 4 test failed: {e}")
        return False


async def test_gpt5_o3_reasoning():
    """Test GPT-5/o3 models with reasoning_effort parameter"""
    print("\n🤖 Testing GPT-5/o3 (2025) with reasoning_effort...")
    
    try:
        provider = OpenAIProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "Explain quantum computing step by step"}]
        
        # Test o3 with reasoning_effort
        print("📝 Testing o3 with reasoning_effort parameter...")
        reasoning_chunks = []
        content_chunks = []
        
        async for chunk in provider.stream_completion(
            messages=messages,
            model="o3",  # 2025 o3 reasoning model
            max_tokens=2000,
            reasoning_effort="medium"  # Correct 2025 parameter
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
        print(f"   - Model: o3")
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


async def test_grok3_reasoning():
    """Test Grok 3 with Think mode"""
    print("\n🦾 Testing Grok 3 (2025) with Think mode...")
    
    try:
        provider = GrokProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "Explain quantum computing step by step"}]
        
        # Test Grok 3 with Think mode
        print("📝 Testing Grok 3 with think_mode parameter...")
        reasoning_chunks = []
        content_chunks = []
        
        async for chunk in provider.stream_completion(
            messages=messages,
            model="grok-3",  # 2025 Grok 3 model
            max_tokens=2000,
            enable_thinking=True  # Activates Think mode
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            
            if chunk_type == "reasoning":
                reasoning_chunks.append(content)
                print(f"🤔 REASONING: {content[:100]}...")
            elif chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content[:50]}...")
        
        print(f"\n✅ Grok 3 Results:")
        print(f"   - Model: grok-3")
        print(f"   - Reasoning chunks: {len(reasoning_chunks)}")
        print(f"   - Content chunks: {len(content_chunks)}")
        
        if reasoning_chunks:
            print(f"   - Sample reasoning: {reasoning_chunks[0][:200]}...")
        else:
            print("   - ❌ No reasoning content found")
            
        await provider.cleanup()
        return len(reasoning_chunks) > 0
        
    except Exception as e:
        print(f"❌ Grok 3 test failed: {e}")
        return False


async def main():
    """Test all 2025 reasoning models"""
    print("🔥 Testing 2025 AI Models with Reasoning Capabilities\n")
    
    results = {}
    
    # Test each 2025 model
    results['claude4'] = await test_claude_4_reasoning()
    results['gpt5_o3'] = await test_gpt5_o3_reasoning()
    results['grok3'] = await test_grok3_reasoning()
    
    print(f"\n📊 2025 REASONING MODELS SUMMARY:")
    print(f"   - Claude 4 reasoning: {'✅' if results['claude4'] else '❌'}")
    print(f"   - GPT-5/o3 reasoning: {'✅' if results['gpt5_o3'] else '❌'}")
    print(f"   - Grok 3 reasoning: {'✅' if results['grok3'] else '❌'}")
    
    if any(results.values()):
        print(f"\n🎉 Some 2025 models are returning reasoning content!")
        print(f"   Next step: Check if streaming API captures it correctly")
    else:
        print(f"\n⚠️  No 2025 models are returning reasoning content!")
        print(f"   Possible issues:")
        print(f"   1. API keys don't have access to 2025 models")
        print(f"   2. Model names are still incorrect")
        print(f"   3. Parameters are still wrong")
        print(f"   4. Models aren't released yet")


if __name__ == "__main__":
    asyncio.run(main())
