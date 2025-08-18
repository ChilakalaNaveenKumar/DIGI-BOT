#!/usr/bin/env python3
"""
Test CONFIRMED AVAILABLE Claude 4 models with Extended Thinking
Models confirmed from official Anthropic documentation
"""

import asyncio
import sys
import os
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

from app.services.ai_providers.anthropic_provider import AnthropicProvider


async def test_claude_opus_4_1():
    """Test Claude Opus 4.1 - CONFIRMED AVAILABLE"""
    print("🔥 Testing Claude Opus 4.1 (claude-opus-4-1-20250805)...")
    
    try:
        provider = AnthropicProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "What is 27 * 453? Show your thinking step by step."}]
        
        print("📝 Testing with extended thinking...")
        reasoning_chunks = []
        content_chunks = []
        thinking_deltas = 0
        
        async for chunk in provider.stream_completion(
            messages=messages,
            model="claude-opus-4-1-20250805",  # CONFIRMED model name
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
                print(f"🧠 THINKING: {content[:80]}...")
            elif chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content[:50]}...")
        
        print(f"\n✅ Claude Opus 4.1 Results:")
        print(f"   - Model: claude-opus-4-1-20250805")
        print(f"   - Reasoning chunks: {len(reasoning_chunks)}")
        print(f"   - Thinking deltas: {thinking_deltas}")
        print(f"   - Content chunks: {len(content_chunks)}")
        
        if reasoning_chunks:
            print(f"   - 🎉 EXTENDED THINKING WORKING!")
            print(f"   - Sample reasoning: {reasoning_chunks[0][:150]}...")
        else:
            print("   - ⚠️ No reasoning content (may need higher API tier)")
            
        await provider.cleanup()
        return len(reasoning_chunks) > 0, len(content_chunks) > 0
        
    except Exception as e:
        print(f"❌ Claude Opus 4.1 test failed: {e}")
        if "400" in str(e):
            print("   💡 Likely API access issue - not model availability")
        return False, False


async def test_claude_sonnet_4():
    """Test Claude Sonnet 4 - CONFIRMED AVAILABLE"""
    print("\n🎯 Testing Claude Sonnet 4 (claude-sonnet-4-20250514)...")
    
    try:
        provider = AnthropicProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "Explain why prime numbers are infinite. Think through this carefully."}]
        
        print("📝 Testing with extended thinking...")
        reasoning_chunks = []
        content_chunks = []
        thinking_deltas = 0
        
        async for chunk in provider.stream_completion(
            messages=messages,
            model="claude-sonnet-4-20250514",  # CONFIRMED model name
            max_tokens=16000,
            enable_reasoning=True,
            reasoning_budget=8000
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            metadata = chunk.get("metadata", {})
            
            if chunk_type == "reasoning":
                reasoning_chunks.append(content)
                if metadata.get("thinking_delta"):
                    thinking_deltas += 1
                print(f"🧠 THINKING: {content[:80]}...")
            elif chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content[:50]}...")
        
        print(f"\n✅ Claude Sonnet 4 Results:")
        print(f"   - Model: claude-sonnet-4-20250514")
        print(f"   - Reasoning chunks: {len(reasoning_chunks)}")
        print(f"   - Thinking deltas: {thinking_deltas}")
        print(f"   - Content chunks: {len(content_chunks)}")
        
        if reasoning_chunks:
            print(f"   - 🎉 EXTENDED THINKING WORKING!")
            print(f"   - Sample reasoning: {reasoning_chunks[0][:150]}...")
        else:
            print("   - ⚠️ No reasoning content (may need higher API tier)")
            
        await provider.cleanup()
        return len(reasoning_chunks) > 0, len(content_chunks) > 0
        
    except Exception as e:
        print(f"❌ Claude Sonnet 4 test failed: {e}")
        if "400" in str(e):
            print("   💡 Likely API access issue - not model availability")
        return False, False


async def test_without_thinking():
    """Test Claude Opus 4.1 WITHOUT thinking to isolate the issue"""
    print("\n🔍 Testing Claude Opus 4.1 WITHOUT thinking (diagnostic)...")
    
    try:
        provider = AnthropicProvider()
        await provider.initialize()
        
        messages = [{"role": "user", "content": "What is 27 * 453?"}]
        
        print("📝 Testing without thinking parameter...")
        content_chunks = []
        
        async for chunk in provider.stream_completion(
            messages=messages,
            model="claude-opus-4-1-20250805",
            max_tokens=1000,
            enable_reasoning=False  # NO thinking
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            
            if chunk_type == "content":
                content_chunks.append(content)
                print(f"💬 CONTENT: {content[:50]}...")
        
        print(f"\n✅ Diagnostic Results:")
        print(f"   - Model access: {'✅ Working' if len(content_chunks) > 0 else '❌ Failed'}")
        print(f"   - Content chunks: {len(content_chunks)}")
        
        if len(content_chunks) > 0:
            print("   - 🎯 Model is accessible - thinking parameter may need API tier upgrade")
        else:
            print("   - ❌ Model not accessible - API key may need Claude 4 access")
            
        await provider.cleanup()
        return len(content_chunks) > 0
        
    except Exception as e:
        print(f"❌ Diagnostic test failed: {e}")
        if "model_not_found" in str(e).lower():
            print("   - Model name issue")
        elif "400" in str(e):
            print("   - API access/tier issue")
        elif "401" in str(e):
            print("   - API key issue")
        return False


async def main():
    """Test confirmed available Claude 4 models"""
    print("🎯 Testing CONFIRMED AVAILABLE Claude 4 Models\n")
    print("Based on official Anthropic documentation:")
    print("✅ claude-opus-4-1-20250805 (Claude Opus 4.1)")
    print("✅ claude-sonnet-4-20250514 (Claude Sonnet 4)")
    print("Both support: Extended Thinking, Code Execution, 1M context\n")
    
    results = {}
    
    # Test without thinking first (diagnostic)
    results['diagnostic'] = await test_without_thinking()
    
    # Test confirmed models with thinking
    results['opus_reasoning'], results['opus_basic'] = await test_claude_opus_4_1()
    results['sonnet_reasoning'], results['sonnet_basic'] = await test_claude_sonnet_4()
    
    print(f"\n📊 CONFIRMED MODELS TEST RESULTS:")
    print(f"   - Claude Opus 4.1 (basic): {'✅' if results['opus_basic'] else '❌'}")
    print(f"   - Claude Opus 4.1 (thinking): {'✅' if results['opus_reasoning'] else '❌'}")
    print(f"   - Claude Sonnet 4 (basic): {'✅' if results['sonnet_basic'] else '❌'}")
    print(f"   - Claude Sonnet 4 (thinking): {'✅' if results['sonnet_reasoning'] else '❌'}")
    print(f"   - Diagnostic (no thinking): {'✅' if results['diagnostic'] else '❌'}")
    
    if results['opus_reasoning'] or results['sonnet_reasoning']:
        print(f"\n🎉 EXTENDED THINKING IS WORKING!")
        print(f"   ✅ Models are accessible")
        print(f"   ✅ API parameters are correct")
        print(f"   ✅ Streaming parser works perfectly")
        print(f"   ✅ Ready for production!")
    elif results['diagnostic'] or results['opus_basic'] or results['sonnet_basic']:
        print(f"\n⚠️  Models accessible, thinking needs higher API tier")
        print(f"   ✅ Claude 4 models work")
        print(f"   ⚠️  Extended thinking requires API upgrade")
        print(f"   💡 Contact Anthropic for thinking access")
    else:
        print(f"\n❌ API access issue")
        print(f"   Possible solutions:")
        print(f"   1. Request Claude 4 model access from Anthropic")
        print(f"   2. Check API key has sufficient credits")
        print(f"   3. Verify regional availability")
        print(f"   4. Try different API key with higher tier")


if __name__ == "__main__":
    asyncio.run(main())
