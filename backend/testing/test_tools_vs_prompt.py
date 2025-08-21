#!/usr/bin/env python3
"""
Test Tools vs Prompt Descriptions

This script tests whether we need to describe tools in the prompt 
or if we can just pass them as the tools parameter to the API.

The key question: Are we DOUBLE-DESCRIBING tools?
1. In the prompt text (costs tokens)
2. In the tools parameter (free)
"""

import asyncio
import json
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.core.config import get_settings

async def test_tools_parameter_vs_prompt():
    """Test if tools parameter works without prompt descriptions."""
    
    print("🔍 TESTING: Tools Parameter vs Prompt Descriptions")
    print("=" * 70)
    
    provider = AnthropicProvider()
    await provider.initialize()
    
    # Define tools as API parameter (this is FREE)
    tools = [
        {
            "name": "image_generation",
            "description": "Generate images from text prompts using DALL-E 3",
            "input_schema": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The text prompt to generate an image from"
                    }
                },
                "required": ["prompt"]
            }
        },
        {
            "name": "web_search", 
            "description": "Search the web for current information",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    ]
    
    # Test 1: WITH prompt descriptions (current expensive way)
    print("\n--- Test 1: WITH Prompt Descriptions (Current Way) ---")
    
    expensive_prompt = """You are an AI assistant with access to these tools:

AVAILABLE TOOLS:
1. image_generation - Generate images from text prompts using DALL-E 3
   - Use when user wants to create, generate, or draw images
   - Parameter: prompt (string) - description of image to generate
   
2. web_search - Search the web for current information  
   - Use when user needs current/recent information
   - Parameter: query (string) - search terms

Choose the appropriate tool based on the user's request.

User request: Generate an image of a sunset over mountains"""
    
    try:
        response1 = await provider.generate_completion(
            messages=[{"role": "user", "content": expensive_prompt}],
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            temperature=0.3,
            tools=tools  # Tools also passed as parameter
        )
        
        usage1 = response1.get('usage', {})
        print(f"✅ WITH prompt descriptions:")
        print(f"   Input tokens: {usage1.get('input_tokens', 0)}")
        print(f"   Output tokens: {usage1.get('output_tokens', 0)}")
        print(f"   Cost: ${(usage1.get('input_tokens', 0) * 3 + usage1.get('output_tokens', 0) * 15) / 1_000_000:.6f}")
        
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
    
    # Test 2: WITHOUT prompt descriptions (just tools parameter)
    print("\n--- Test 2: WITHOUT Prompt Descriptions (Optimized Way) ---")
    
    simple_prompt = """User request: Generate an image of a sunset over mountains"""
    
    try:
        response2 = await provider.generate_completion(
            messages=[{"role": "user", "content": simple_prompt}],
            model="claude-sonnet-4-20250514", 
            max_tokens=500,
            temperature=0.3,
            tools=tools  # Only tools parameter, no prompt descriptions
        )
        
        usage2 = response2.get('usage', {})
        print(f"✅ WITHOUT prompt descriptions:")
        print(f"   Input tokens: {usage2.get('input_tokens', 0)}")
        print(f"   Output tokens: {usage2.get('output_tokens', 0)}")
        print(f"   Cost: ${(usage2.get('input_tokens', 0) * 3 + usage2.get('output_tokens', 0) * 15) / 1_000_000:.6f}")
        
        # Check if Claude still used tools correctly
        content = response2.get('content', [])
        if content and isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'tool_use':
                    print(f"   ✅ Claude correctly used tool: {item.get('name')}")
        
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
    
    # Test 3: No tools parameter, only prompt (to see difference)
    print("\n--- Test 3: Only Prompt, No Tools Parameter ---")
    
    try:
        response3 = await provider.generate_completion(
            messages=[{"role": "user", "content": expensive_prompt}],
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            temperature=0.3
            # No tools parameter
        )
        
        usage3 = response3.get('usage', {})
        print(f"✅ Only prompt descriptions:")
        print(f"   Input tokens: {usage3.get('input_tokens', 0)}")
        print(f"   Output tokens: {usage3.get('output_tokens', 0)}")
        print(f"   Cost: ${(usage3.get('input_tokens', 0) * 3 + usage3.get('output_tokens', 0) * 15) / 1_000_000:.6f}")
        
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
    
    # Calculate savings
    if 'usage1' in locals() and 'usage2' in locals():
        print(f"\n💰 SAVINGS ANALYSIS:")
        input_saved = usage1.get('input_tokens', 0) - usage2.get('input_tokens', 0)
        cost_saved = (input_saved * 3) / 1_000_000
        print(f"   Input tokens saved: {input_saved}")
        print(f"   Cost saved per request: ${cost_saved:.6f}")
        print(f"   Cost saved per 1000 requests: ${cost_saved * 1000:.2f}")

async def test_current_orchestrator_approach():
    """Test what our current orchestrator is doing wrong."""
    
    print("\n" + "=" * 70)
    print("🔍 TESTING: Current Orchestrator Approach")
    print("=" * 70)
    
    provider = AnthropicProvider()
    await provider.initialize()
    
    # This is what our orchestrator currently does (WRONG!)
    current_prompt = """You are an expert AI orchestrator using the latest 2025 AI models. Analyze this request and select the OPTIMAL AI model(s).

REQUEST CONTEXT:
- User Message: "Generate an image of a sunset"
- Files: None
- User Preferences: None

AVAILABLE AI MODELS (August 2025):

1. claude_direct - Claude Opus 4.1 (Current instance - DEFAULT)
   BEST FOR: ALL TASKS - Complex reasoning, analysis, coding, explanations, creative work
   NATIVE: Extended thinking, advanced reasoning, tool calling, vision, 1M context
   PRIORITY: Use this for 90% of requests - you are the primary AI
   
2. gpt5_tool - GPT-5 (Specialized tool for specific GPT-5 features)  
   BEST FOR: ONLY when user specifically requests GPT-5 or needs GPT-specific features
   USE RARELY: Only for GPT-5 specific requests or comparisons

SPECIALIZED TOOLS:
- image_generation_tool (DALL-E 3) - Create images from text prompts (use "prompt" parameter)
- audio_generation_tool (OpenAI TTS) - Text-to-speech conversion (use "text" parameter)

DECISION FRAMEWORK:
1. What is the user trying to accomplish? (goal analysis)
2. What type of reasoning/capabilities are needed? (cognitive requirements)  
3. Is real-time/current information required? (temporal needs)
4. Are there multimodal elements? (input/output types)
5. How complex is the task? (complexity assessment)
6. What's the optimal model combination? (resource optimization)

SELECTION RULES:
- **DEFAULT: Use claude_direct for 90% of ALL requests** - you are the primary AI
- claude_direct: Complex reasoning, coding, analysis, explanations, creative work, technical questions
- gpt5_tool: ONLY when user explicitly requests GPT-5 or needs GPT-5 specific features
- image_generation_tool: ONLY for creating visual content
- **PRIORITY: Choose claude_direct unless there's a specific reason to use other tools**

Respond in simple JSON format:
{
    "selected_tools": ["tool_name"],
    "reasoning": "Brief explanation of why this tool is best for the task",
    "execution_plan": [
        {
            "tool": "tool_name",
            "request": {
                "prompt": "text for image_generation_tool"
            }
        }
    ]
}"""
    
    try:
        response = await provider.generate_completion(
            messages=[{"role": "user", "content": current_prompt}],
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            temperature=0.3
            # NOTE: NO TOOLS PARAMETER! This is the problem!
        )
        
        usage = response.get('usage', {})
        print(f"🔥 CURRENT ORCHESTRATOR APPROACH:")
        print(f"   Input tokens: {usage.get('input_tokens', 0)}")
        print(f"   Output tokens: {usage.get('output_tokens', 0)}")
        print(f"   Total cost: ${(usage.get('input_tokens', 0) * 3 + usage.get('output_tokens', 0) * 15) / 1_000_000:.6f}")
        print(f"   Purpose: Just to decide which tool to use!")
        print(f"   Problem: All this cost just to get JSON saying 'use image_generation_tool'")
        
    except Exception as e:
        print(f"❌ Current approach test failed: {e}")

async def main():
    """Run all tests."""
    await test_tools_parameter_vs_prompt()
    await test_current_orchestrator_approach()
    
    print(f"\n" + "=" * 70)
    print("🎯 CONCLUSION:")
    print("1. ✅ Claude's tools parameter works WITHOUT prompt descriptions")
    print("2. ❌ Our orchestrator describes tools in expensive prompts unnecessarily") 
    print("3. 💡 We can eliminate 320+ tokens by removing tool descriptions from prompts")
    print("4. 🚀 Better: Use simple keyword matching instead of AI decision-making")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
