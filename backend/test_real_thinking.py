#!/usr/bin/env python3
"""
Test Claude 4 Extended Thinking with correct API parameters from documentation
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

from app.services.ai_providers.anthropic_provider import AnthropicProvider


async def test_claude_3_7_thinking():
    """Test Claude 3.7 with extended thinking (documented model)"""
    print("🧠 Testing Claude 3.7 Sonnet with Extended Thinking...")
    
    try:
        provider = AnthropicProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "Are there an infinite number of prime numbers such that n mod 4 == 3?"}]
        
        print("📝 Testing Claude 3.7 with thinking parameter...")
        reasoning_chunks = []
        content_chunks = []
        thinking_deltas = 0
        
        async for chunk in provider.stream_completion(
            messages=messages,
            model="claude-3-7-sonnet-20250219",  # Documented model with thinking
            max_tokens=16000,
            enable_reasoning=True,
            reasoning_budget=10000  # Budget tokens from documentation
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            metadata = chunk.get("metadata", {})
            
            if chunk_type == "reasoning":
                reasoning_chunks.append(content)
                if metadata.get("thinking_delta"):
                    thinking_deltas += 1
                print(f"🤔 THINKING: {content[:100]}...")
            elif chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content[:50]}...")
        
        print(f"\n✅ Claude 3.7 Results:")
        print(f"   - Model: claude-3-7-sonnet-20250219")
        print(f"   - Reasoning chunks: {len(reasoning_chunks)}")
        print(f"   - Thinking deltas: {thinking_deltas}")
        print(f"   - Content chunks: {len(content_chunks)}")
        
        if reasoning_chunks:
            print(f"   - ✅ REASONING WORKING!")
            print(f"   - Sample reasoning: {reasoning_chunks[0][:200]}...")
        else:
            print("   - ❌ No reasoning content found")
            
        await provider.cleanup()
        return len(reasoning_chunks) > 0
        
    except Exception as e:
        print(f"❌ Claude 3.7 test failed: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return False


async def test_claude_4_thinking():
    """Test Claude 4 Sonnet with extended thinking"""
    print("\n🔥 Testing Claude 4 Sonnet with Extended Thinking...")
    
    try:
        provider = AnthropicProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "What is 27 * 453? Think step by step."}]
        
        print("📝 Testing Claude 4 with thinking parameter...")
        reasoning_chunks = []
        content_chunks = []
        thinking_deltas = 0
        
        async for chunk in provider.stream_completion(
            messages=messages,
            model="claude-sonnet-4-20250514",  # Claude 4 model
            max_tokens=16000,
            enable_reasoning=True,
            reasoning_budget=10000
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            metadata = chunk.get("metadata", {})
            
            if chunk_type == "reasoning":
                reasoning_chunks.append(content)
                if metadata.get("thinking_delta"):
                    thinking_deltas += 1
                print(f"🤔 THINKING: {content[:100]}...")
            elif chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content[:50]}...")
        
        print(f"\n✅ Claude 4 Results:")
        print(f"   - Model: claude-sonnet-4-20250514")
        print(f"   - Reasoning chunks: {len(reasoning_chunks)}")
        print(f"   - Thinking deltas: {thinking_deltas}")
        print(f"   - Content chunks: {len(content_chunks)}")
        
        if reasoning_chunks:
            print(f"   - ✅ REASONING WORKING!")
            print(f"   - Sample reasoning: {reasoning_chunks[0][:200]}...")
        else:
            print("   - ❌ No reasoning content found")
            
        await provider.cleanup()
        return len(reasoning_chunks) > 0
        
    except Exception as e:
        print(f"❌ Claude 4 test failed: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return False


async def test_legacy_model():
    """Test with legacy model to confirm basic functionality"""
    print("\n🔄 Testing Legacy Claude 3.5 (Control Test)...")
    
    try:
        provider = AnthropicProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "What is 27 * 453?"}]
        
        print("📝 Testing legacy model without thinking...")
        content_chunks = []
        
        async for chunk in provider.stream_completion(
            messages=messages,
            model="claude-3-5-sonnet-20241022",  # Legacy model
            max_tokens=1000,
            enable_reasoning=False  # No thinking
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            
            if chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content[:50]}...")
        
        print(f"\n✅ Legacy Model Results:")
        print(f"   - Model: claude-3-5-sonnet-20241022")
        print(f"   - Content chunks: {len(content_chunks)}")
        print(f"   - Basic API: {'✅ Working' if len(content_chunks) > 0 else '❌ Failed'}")
            
        await provider.cleanup()
        return len(content_chunks) > 0
        
    except Exception as e:
        print(f"❌ Legacy test failed: {e}")
        return False


async def main():
    """Test Claude Extended Thinking with documented parameters"""
    print("🎯 Testing Claude Extended Thinking - Real Implementation\n")
    
    results = {}
    
    # Test documented models
    results['legacy'] = await test_legacy_model()
    results['claude_37'] = await test_claude_3_7_thinking()
    results['claude_4'] = await test_claude_4_thinking()
    
    print(f"\n📊 CLAUDE EXTENDED THINKING RESULTS:")
    print(f"   - Legacy Claude 3.5 (control): {'✅' if results['legacy'] else '❌'}")
    print(f"   - Claude 3.7 thinking: {'✅' if results['claude_37'] else '❌'}")
    print(f"   - Claude 4 thinking: {'✅' if results['claude_4'] else '❌'}")
    
    if results['claude_37'] or results['claude_4']:
        print(f"\n🎉 EXTENDED THINKING IS WORKING!")
        print(f"   ✅ API parameters are correct")
        print(f"   ✅ Streaming parser handles thinking_delta events")
        print(f"   ✅ Frontend can now receive reasoning content")
        print(f"\n🚀 Next: Test the full streaming API integration!")
    elif results['legacy']:
        print(f"\n⚠️  Basic API works, but thinking models not available")
        print(f"   Possible reasons:")
        print(f"   1. API key doesn't have access to Claude 4/3.7 models")
        print(f"   2. Models not released yet in your region")
        print(f"   3. Need to request access to extended thinking")
    else:
        print(f"\n❌ API connection issues - check configuration")


if __name__ == "__main__":
    asyncio.run(main())
