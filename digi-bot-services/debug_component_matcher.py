#!/usr/bin/env python3
"""
Debug Component Matcher - Detailed Analysis
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def debug_component_matcher():
    """Debug component matcher step by step"""
    
    # Shorter test content with clear data
    test_content = """Student test scores show the following distribution:

Scores: [65, 68, 70, 72, 75, 78, 80, 82, 85, 87, 90, 92, 95]
Mean: 78.4

This data shows a normal distribution pattern with most students scoring around 78-82 points."""

    print("🔍 Debug Component Matcher")
    print("=" * 50)
    print(f"Test content: {test_content}")
    print(f"Content length: {len(test_content)} characters")
    print()

    try:
        from app.services.component_matcher.gpt5_client import GPT5ComponentMatcherClient
        from app.services.component_matcher import VectorStoreManager
        
        # Initialize services
        vector_manager = VectorStoreManager()
        await vector_manager.initialize()
        
        print("🔍 Step 1: Vector Search Results")
        print("-" * 30)
        
        # Test vector search directly
        vector_results = await vector_manager.query(test_content, top_k=5)
        
        for i, result in enumerate(vector_results, 1):
            score = result.get('score', 0)
            text = result.get('text', '')
            print(f"{i}. Score: {score:.3f}")
            print(f"   Text: {text[:200]}...")
            print()
        
        print("🤖 Step 2: Component Matcher Analysis")
        print("-" * 30)
        
        # Initialize component matcher
        component_matcher = GPT5ComponentMatcherClient(
            model="gpt-5",
            reasoning_effort="medium",
            liberal_match=True,
            allow_placeholders=True
        )
        
        await component_matcher.initialize()
        
        # Test full analysis with streaming
        print("Running full analysis...")
        
        full_result = ""
        async for event in component_matcher.analyze(test_content, vector_manager):
            print(f"Event: {event}")
            if event["type"] == "content":
                full_result += event["content"]
            elif event["type"] == "error":
                print(f"❌ Error: {event['error']}")
                break
            elif event["type"] == "completion":
                print("✅ Analysis complete")
                break
        
        print(f"\nFull result: {full_result}")
        print(f"Has match: {component_matcher.has_match(full_result)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_component_matcher())
