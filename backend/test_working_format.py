#!/usr/bin/env python3
"""
Test with the EXACT format that works via curl
"""

import asyncio
import json
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_working_format():
    """Test with exact format that works in curl"""
    print("🎯 Testing with EXACT working format from curl...")
    
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return False
    
    # Use EXACT format that works
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # EXACT payload that works
    payload = {
        "model": "claude-opus-4-1-20250805",
        "max_tokens": 4096,
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
    
    try:
        async with httpx.AsyncClient() as client:
            print("📝 Sending request with working format...")
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS!")
                print(f"   - Model: {result['model']}")
                print(f"   - Content blocks: {len(result['content'])}")
                
                # Check for thinking content
                thinking_blocks = [block for block in result['content'] if block.get('type') == 'thinking']
                text_blocks = [block for block in result['content'] if block.get('type') == 'text']
                
                print(f"   - Thinking blocks: {len(thinking_blocks)}")
                print(f"   - Text blocks: {len(text_blocks)}")
                
                if thinking_blocks:
                    print(f"🧠 THINKING CONTENT:")
                    print(f"   {thinking_blocks[0]['thinking'][:200]}...")
                
                if text_blocks:
                    print(f"💬 TEXT CONTENT:")
                    print(f"   {text_blocks[0]['text'][:200]}...")
                
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_streaming_format():
    """Test streaming with working format"""
    print("\n🌊 Testing STREAMING with working format...")
    
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ No API key found")
        return False
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-opus-4-1-20250805",
        "max_tokens": 4096,
        "stream": True,  # Enable streaming
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
                        "text": "What is 15 * 23? Show your thinking."
                    }
                ]
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            print("📝 Sending streaming request...")
            
            thinking_chunks = 0
            content_chunks = 0
            
            async with client.stream(
                "POST",
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status_code != 200:
                    print(f"❌ Failed: {response.status_code}")
                    content = await response.aread()
                    print(f"   Response: {content.decode()}")
                    return False
                
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
                                    if thinking_text:
                                        print(f"🤔 THINKING: {thinking_text[:60]}...")
                                
                                elif delta.get("type") == "text_delta":
                                    content_chunks += 1
                                    text_content = delta.get("text", "")
                                    if text_content:
                                        print(f"💬 CONTENT: {text_content[:60]}...")
                            
                            elif data.get("type") == "message_stop":
                                print("✅ STREAMING COMPLETE")
                                break
                        
                        except json.JSONDecodeError:
                            continue
                
                print(f"\n✅ Streaming Results:")
                print(f"   - Thinking chunks: {thinking_chunks}")
                print(f"   - Content chunks: {content_chunks}")
                print(f"   - Streaming: {'✅ Working' if thinking_chunks > 0 else '❌ No thinking'}")
                
                return thinking_chunks > 0
                
    except Exception as e:
        print(f"❌ Streaming error: {e}")
        return False


async def main():
    """Test the working format"""
    print("🎯 Testing CONFIRMED WORKING API Format\n")
    
    # Test non-streaming first
    non_streaming_works = await test_working_format()
    
    # Test streaming
    streaming_works = await test_streaming_format()
    
    print(f"\n📊 RESULTS:")
    print(f"   - Non-streaming thinking: {'✅' if non_streaming_works else '❌'}")
    print(f"   - Streaming thinking: {'✅' if streaming_works else '❌'}")
    
    if non_streaming_works and streaming_works:
        print(f"\n🎉 EXTENDED THINKING CONFIRMED WORKING!")
        print(f"   ✅ Model: claude-opus-4-1-20250805")
        print(f"   ✅ Thinking parameter: correct")
        print(f"   ✅ Message format: correct")
        print(f"   ✅ Streaming: works perfectly")
        print(f"\n🚀 Now fix the provider code to match this format!")
    else:
        print(f"\n⚠️  Need to debug further")


if __name__ == "__main__":
    asyncio.run(main())
