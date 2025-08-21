#!/usr/bin/env python3
"""
Test Orchestrator Decision Making - Isolated Test

This script tests ONLY the orchestrator decision-making part to understand:
1. How much the decision prompt costs
2. What tokens are being consumed
3. Whether we can eliminate this step

Run: python testing/test_orchestrator_decision.py
"""

import asyncio
import json
import sys
import os
import time

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.claude4_orchestrator import Claude4Orchestrator
from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.core.config import get_settings

async def test_orchestrator_decision():
    """Test only the orchestrator decision making part."""
    
    print("🧪 Testing Orchestrator Decision Making")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = Claude4Orchestrator()
    await orchestrator.initialize()
    
    # Test different types of user messages
    test_messages = [
        "What is 2+2?",
        "Explain machine learning",
        "Create a business plan for a startup",
        "Generate an image of a cat"
    ]
    
    for i, user_message in enumerate(test_messages, 1):
        print(f"\n--- Test {i}: {user_message} ---")
        
        # Get the decision prompt that would be sent
        decision_prompt = orchestrator._build_decision_prompt(
            user_message=user_message,
            files=None,
            user_preferences=None
        )
        
        print(f"Decision prompt length: {len(decision_prompt)} characters")
        print(f"Decision prompt preview: {decision_prompt[:200]}...")
        
        # Estimate tokens (rough: ~4 chars per token)
        estimated_input_tokens = len(decision_prompt) // 4
        print(f"Estimated input tokens: {estimated_input_tokens}")
        
        # Test the actual decision making
        start_time = time.time()
        
        try:
            decision = await orchestrator._make_orchestration_decision(
                user_message=user_message,
                conversation_history=None,
                user_preferences=None,
                files=None
            )
            
            end_time = time.time()
            
            print(f"✅ Decision made in {(end_time - start_time)*1000:.0f}ms")
            print(f"Selected tools: {decision.selected_tools}")
            print(f"Reasoning: {decision.reasoning[:100]}...")
            print(f"Confidence: {decision.confidence}")
            
        except Exception as e:
            end_time = time.time()
            print(f"❌ Decision failed in {(end_time - start_time)*1000:.0f}ms: {e}")
        
        print("-" * 40)

async def test_direct_anthropic_call():
    """Test direct Anthropic call to see token usage."""
    
    print("\n🔍 Testing Direct Anthropic Call")
    print("=" * 60)
    
    provider = AnthropicProvider()
    await provider.initialize()
    
    # Simple test message
    test_message = "What is 2+2?"
    
    messages = [{"role": "user", "content": test_message}]
    
    print(f"Test message: {test_message}")
    print(f"Input length: {len(test_message)} characters")
    
    try:
        response = await provider.generate_completion(
            messages=messages,
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            temperature=0.7
        )
        
        print(f"Response type: {type(response)}")
        print(f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        if isinstance(response, dict):
            # Check usage info
            if 'usage' in response:
                usage = response['usage']
                input_tokens = usage.get('input_tokens', 0)
                output_tokens = usage.get('output_tokens', 0)
                
                print(f"📊 Token Usage:")
                print(f"  Input tokens: {input_tokens}")
                print(f"  Output tokens: {output_tokens}")
                print(f"  Total tokens: {input_tokens + output_tokens}")
                
                # Calculate cost
                input_cost = input_tokens * (3.00 / 1_000_000)
                output_cost = output_tokens * (15.00 / 1_000_000)
                total_cost = input_cost + output_cost
                
                print(f"💰 Cost:")
                print(f"  Input cost: ${input_cost:.6f}")
                print(f"  Output cost: ${output_cost:.6f}")
                print(f"  Total cost: ${total_cost:.6f}")
            
            # Check content
            if 'content' in response:
                content = response['content']
                if isinstance(content, list) and content:
                    text = content[0].get('text', '') if isinstance(content[0], dict) else str(content[0])
                    print(f"Response: {text}")
            
            # Check for extra metadata
            print(f"📋 Full Response Structure:")
            for key, value in response.items():
                if key not in ['content']:
                    print(f"  {key}: {type(value)} - {str(value)[:100]}...")
                    
    except Exception as e:
        print(f"❌ Direct call failed: {e}")

async def analyze_orchestrator_prompt():
    """Analyze the orchestrator prompt to see if we can optimize it."""
    
    print("\n🔬 Analyzing Orchestrator Prompt")
    print("=" * 60)
    
    orchestrator = Claude4Orchestrator()
    await orchestrator.initialize()
    
    # Test with simple question
    user_message = "What is Python?"
    
    prompt = orchestrator._build_decision_prompt(
        user_message=user_message,
        files=None,
        user_preferences=None
    )
    
    print(f"User message: {user_message}")
    print(f"Full prompt length: {len(prompt)} characters")
    print(f"Estimated tokens: {len(prompt) // 4}")
    
    # Break down the prompt
    lines = prompt.split('\n')
    sections = {}
    current_section = "header"
    
    for line in lines:
        if line.startswith('AVAILABLE AI MODELS'):
            current_section = "models"
            sections[current_section] = []
        elif line.startswith('REQUEST CONTEXT'):
            current_section = "context"
            sections[current_section] = []
        elif line.startswith('DECISION FRAMEWORK'):
            current_section = "framework"
            sections[current_section] = []
        elif line.startswith('SELECTION RULES'):
            current_section = "rules"
            sections[current_section] = []
        elif line.startswith('Respond in simple JSON'):
            current_section = "json_format"
            sections[current_section] = []
        else:
            if current_section not in sections:
                sections[current_section] = []
            sections[current_section].append(line)
    
    print(f"\n📊 Prompt Breakdown:")
    for section, content in sections.items():
        section_text = '\n'.join(content)
        print(f"  {section}: {len(section_text)} chars (~{len(section_text)//4} tokens)")
    
    # Suggest optimizations
    print(f"\n💡 Optimization Opportunities:")
    print(f"  1. Model descriptions: Very verbose - could be shortened")
    print(f"  2. Decision framework: 6 questions - could be simplified")
    print(f"  3. Selection rules: Repetitive - could be condensed")
    print(f"  4. JSON format: Large example - could be minimal")
    
    # Calculate potential savings
    total_chars = len(prompt)
    # Rough estimate: could reduce by 60-70%
    optimized_chars = total_chars * 0.3
    savings = total_chars - optimized_chars
    
    print(f"  Potential token savings: ~{savings//4:.0f} tokens per decision")
    print(f"  Cost savings per decision: ~${(savings//4) * (3.00/1_000_000):.6f}")

async def main():
    """Run all tests."""
    await test_direct_anthropic_call()
    await analyze_orchestrator_prompt()
    await test_orchestrator_decision()

if __name__ == "__main__":
    asyncio.run(main())
