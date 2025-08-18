#!/usr/bin/env python3
"""
Debug what our provider is actually sending vs the working format
"""

import asyncio
import json
import sys
import os

sys.path.append(os.path.dirname(__file__))

from app.services.ai_providers.anthropic_provider import AnthropicProvider


async def debug_provider_request():
    """Debug what the provider actually sends"""
    print("🔍 Debugging Provider Request Format...")
    
    provider = AnthropicProvider()
    await provider.initialize()
    
    # Test the same message as our working test
    messages = [{"role": "user", "content": "What is 27 * 453? Think step by step."}]
    
    # Let's intercept what gets sent
    print("📝 Provider will send:")
    print("   - Model: claude-opus-4-1-20250805")
    print("   - Enable reasoning: True")
    print("   - Reasoning budget: 2048")
    print("   - Messages:", messages)
    
    # Check what the provider converts this to
    anthropic_messages = []
    for msg in messages:
        content = msg["content"]
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        
        anthropic_messages.append({
            "role": msg["role"],
            "content": content
        })
    
    print("\n📤 Converted messages:")
    print(json.dumps(anthropic_messages, indent=2))
    
    # Check thinking params
    model = "claude-opus-4-1-20250805"
    max_tokens = provider.models[model]["max_output"]  # Should be 75000
    reasoning_budget = 2048
    
    print(f"\n🧠 Thinking calculation:")
    print(f"   - Max tokens: {max_tokens}")
    print(f"   - Reasoning budget requested: {reasoning_budget}")
    
    # This is what our provider calculates
    reasoning_budget_calculated = min(reasoning_budget, max(max_tokens - 100, 1024))
    print(f"   - Reasoning budget calculated: {reasoning_budget_calculated}")
    
    # Build the request like our provider does
    request_data = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "messages": anthropic_messages,
        "stream": True,
        "thinking": {
            "type": "enabled",
            "budget_tokens": reasoning_budget_calculated
        }
    }
    
    print(f"\n📤 Full request data:")
    print(json.dumps(request_data, indent=2))
    
    # Compare with working format
    working_format = {
        "model": "claude-opus-4-1-20250805",
        "max_tokens": 4096,  # Much smaller!
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
    
    print(f"\n✅ Working format (from curl):")
    print(json.dumps(working_format, indent=2))
    
    print(f"\n🔍 DIFFERENCES:")
    print(f"   - Our max_tokens: {max_tokens} vs Working: 4096")
    print(f"   - Our budget_tokens: {reasoning_budget_calculated} vs Working: 2048")
    print(f"   - Our temperature: 0.7 vs Working: (none)")
    print(f"   - Our stream: True vs Working: (none in non-streaming)")
    
    await provider.cleanup()


if __name__ == "__main__":
    asyncio.run(debug_provider_request())
