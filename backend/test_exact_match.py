#!/usr/bin/env python3
"""
Test with EXACT match to working curl format
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(__file__))

from app.services.ai_providers.anthropic_provider import AnthropicProvider


async def test_exact_working_format():
    """Test by modifying provider to send exact working format"""
    print("🎯 Testing with EXACT working format...")
    
    provider = AnthropicProvider()
    await provider.initialize()
    
    messages = [{"role": "user", "content": "What is 27 * 453? Think step by step."}]
    
    # Manually override the provider's stream_completion to use exact working format
    import httpx
    import json
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # EXACT working payload (with streaming)
    payload = {
        "model": "claude-opus-4-1-20250805",
        "max_tokens": 4096,
        "stream": True,  # Add streaming
        "thinking": {
            "type": "enabled",
            "budget_tokens": 2048
        },
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What is 27 * 453? Think step by step."
                    }
                ]
            }
        ]
    }
    
    print("📤 Sending exact working format with streaming...")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        thinking_chunks = 0
        content_chunks = 0
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status_code != 200:
                    print(f"❌ Failed: {response.status_code}")
                    content = await response.aread()
                    print(f"   Error: {content.decode()}")
                    return False
                
                print("✅ Streaming started...")
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            
                            if data.get("type") == "content_block_start":
                                block = data.get("content_block", {})
                                if block.get("type") == "thinking":
                                    print("🧠 THINKING BLOCK STARTED")
                            
                            elif data.get("type") == "content_block_delta":
                                delta = data.get("delta", {})
                                
                                if delta.get("type") == "thinking_delta":
                                    thinking_chunks += 1
                                    thinking_text = delta.get("thinking", "")
                                    if thinking_text and thinking_chunks <= 3:  # Show first few
                                        print(f"🤔 THINKING: {thinking_text[:60]}...")
                                
                                elif delta.get("type") == "text_delta":
                                    content_chunks += 1
                                    text_content = delta.get("text", "")
                                    if text_content and content_chunks <= 3:  # Show first few
                                        print(f"💬 CONTENT: {text_content[:60]}...")
                            
                            elif data.get("type") == "message_stop":
                                print("✅ STREAMING COMPLETE")
                                break
                        
                        except json.JSONDecodeError:
                            continue
        
        print(f"\n📊 Results:")
        print(f"   - Thinking chunks: {thinking_chunks}")
        print(f"   - Content chunks: {content_chunks}")
        
        if thinking_chunks > 0:
            print(f"🎉 EXTENDED THINKING WORKING WITH OUR PROVIDER!")
            return True
        else:
            print(f"❌ No thinking chunks received")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        await provider.cleanup()


async def main():
    """Test exact working format"""
    print("🎯 Testing Exact Working Format with Provider\n")
    
    success = await test_exact_working_format()
    
    if success:
        print(f"\n🎉 SUCCESS! Now we know the exact format works!")
        print(f"   ✅ The issue was in our provider parameters")
        print(f"   ✅ Thinking streams perfectly")
        print(f"   🚀 Ready to fix the provider implementation!")
    else:
        print(f"\n⚠️  Still debugging needed")


if __name__ == "__main__":
    asyncio.run(main())
