#!/usr/bin/env python3
"""
Test optimal token allocation theory:
max_tokens = model maximum
budget_tokens = portion for thinking (e.g., 20-30%)
remaining = for final response
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(__file__))

from app.services.ai_providers.anthropic_provider import AnthropicProvider


async def test_token_allocation(max_tokens, budget_tokens, test_name):
    """Test specific token allocation"""
    print(f"\n🧪 Testing {test_name}")
    print(f"   - Max tokens: {max_tokens:,}")
    print(f"   - Budget tokens: {budget_tokens:,}")
    print(f"   - Response tokens available: {max_tokens - budget_tokens:,}")
    
    provider = AnthropicProvider()
    await provider.initialize()
    
    # Complex question that should use substantial thinking
    messages = [{
        "role": "user", 
        "content": "Design a distributed database system that can handle 1 million transactions per second. Consider consistency, availability, partition tolerance, scalability, and fault tolerance. Think through the architecture step by step."
    }]
    
    try:
        thinking_chunks = 0
        content_chunks = 0
        thinking_length = 0
        content_length = 0
        
        async for chunk in provider.stream_completion(
            messages=messages,
            model="claude-opus-4-1-20250805",
            max_tokens=max_tokens,
            enable_reasoning=True,
            reasoning_budget=budget_tokens
        ):
            chunk_type = chunk.get("type")
            content = chunk.get("content", "")
            
            if chunk_type == "reasoning":
                thinking_chunks += 1
                thinking_length += len(content)
                if thinking_chunks <= 2:  # Show first few
                    print(f"🤔 THINKING: {content[:80]}...")
            elif chunk_type == "content":
                content_chunks += 1
                content_length += len(content)
                if content_chunks <= 2:  # Show first few
                    print(f"💬 CONTENT: {content[:80]}...")
        
        print(f"\n📊 Results for {test_name}:")
        print(f"   - Thinking chunks: {thinking_chunks}")
        print(f"   - Content chunks: {content_chunks}")
        print(f"   - Thinking length: {thinking_length:,} chars")
        print(f"   - Content length: {content_length:,} chars")
        print(f"   - Total response: {thinking_length + content_length:,} chars")
        
        # Calculate efficiency
        thinking_ratio = thinking_length / (thinking_length + content_length) if (thinking_length + content_length) > 0 else 0
        print(f"   - Thinking ratio: {thinking_ratio:.1%}")
        print(f"   - Success: {'✅' if thinking_chunks > 0 and content_chunks > 0 else '❌'}")
        
        await provider.cleanup()
        return {
            "success": thinking_chunks > 0 and content_chunks > 0,
            "thinking_chunks": thinking_chunks,
            "content_chunks": content_chunks,
            "thinking_length": thinking_length,
            "content_length": content_length,
            "thinking_ratio": thinking_ratio
        }
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        await provider.cleanup()
        return {"success": False, "error": str(e)}


async def main():
    """Test different token allocation strategies"""
    print("🎯 Testing Optimal Token Allocation Theory\n")
    print("Theory: max_tokens should be model maximum, budget_tokens should be optimal portion")
    
    # According to Anthropic docs, Claude Opus 4.1 supports up to 4096 output tokens efficiently
    # But let's test different strategies
    
    test_cases = [
        # Current working setup
        {"max_tokens": 4096, "budget_tokens": 2048, "name": "Current (50/50 split)"},
        
        # Your theory: Use higher max_tokens with reasonable budget
        {"max_tokens": 8192, "budget_tokens": 2048, "name": "Higher Max (25% thinking)"},
        {"max_tokens": 8192, "budget_tokens": 3072, "name": "Higher Max (37.5% thinking)"},
        
        # Even higher max_tokens
        {"max_tokens": 16384, "budget_tokens": 3072, "name": "Very High Max (18.75% thinking)"},
        {"max_tokens": 16384, "budget_tokens": 4096, "name": "Very High Max (25% thinking)"},
        
        # Conservative but optimal
        {"max_tokens": 6144, "budget_tokens": 2048, "name": "Conservative (33% thinking)"},
    ]
    
    results = []
    
    for test_case in test_cases:
        result = await test_token_allocation(
            test_case["max_tokens"],
            test_case["budget_tokens"], 
            test_case["name"]
        )
        result["test_name"] = test_case["name"]
        result["max_tokens"] = test_case["max_tokens"]
        result["budget_tokens"] = test_case["budget_tokens"]
        results.append(result)
    
    # Analyze results
    print(f"\n📊 FINAL ANALYSIS:")
    print(f"{'Test Name':<25} {'Success':<8} {'Think%':<8} {'Think':<6} {'Content':<8} {'Total':<8}")
    print(f"{'-' * 80}")
    
    successful_tests = []
    
    for result in results:
        if result["success"]:
            success_icon = "✅"
            think_ratio = f"{result['thinking_ratio']:.1%}"
            think_chunks = result["thinking_chunks"]
            content_chunks = result["content_chunks"]
            total_chars = result["thinking_length"] + result["content_length"]
            
            print(f"{result['test_name']:<25} {success_icon:<8} {think_ratio:<8} {think_chunks:<6} {content_chunks:<8} {total_chars:<8,}")
            successful_tests.append(result)
        else:
            print(f"{result['test_name']:<25} {'❌':<8} {'N/A':<8} {'N/A':<6} {'N/A':<8} {'N/A':<8}")
    
    if successful_tests:
        # Find optimal configuration
        best_test = max(successful_tests, key=lambda x: x["thinking_length"] + x["content_length"])
        
        print(f"\n🎯 OPTIMAL CONFIGURATION:")
        print(f"   - Test: {best_test['test_name']}")
        print(f"   - Max tokens: {best_test['max_tokens']:,}")
        print(f"   - Budget tokens: {best_test['budget_tokens']:,}")
        print(f"   - Response tokens: {best_test['max_tokens'] - best_test['budget_tokens']:,}")
        print(f"   - Thinking ratio: {best_test['thinking_ratio']:.1%}")
        print(f"   - Total output: {best_test['thinking_length'] + best_test['content_length']:,} chars")
        
        print(f"\n🚀 RECOMMENDED PRODUCTION SETTINGS:")
        print(f"   - Claude Opus 4.1: max_tokens={best_test['max_tokens']}, budget_tokens={best_test['budget_tokens']}")
        print(f"   - Claude Sonnet 4: max_tokens={best_test['max_tokens']//2}, budget_tokens={best_test['budget_tokens']//2}")
        print(f"   - Thinking/Response ratio: {best_test['thinking_ratio']:.1%}/{1-best_test['thinking_ratio']:.1%}")


if __name__ == "__main__":
    asyncio.run(main())
