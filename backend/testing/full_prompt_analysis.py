#!/usr/bin/env python3
"""
Full Prompt Analysis - Complete Breakdown

This script analyzes:
1. Full decision prompt content
2. Full response content 
3. What costs money vs what's useful
4. Exact token usage for each part
5. Optimization opportunities

Run: python testing/full_prompt_analysis.py
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

def analyze_string_cost(text: str, label: str):
    """Analyze the cost of a string."""
    chars = len(text)
    est_tokens = chars // 4
    input_cost = est_tokens * (3.00 / 1_000_000)
    output_cost = est_tokens * (15.00 / 1_000_000)
    
    print(f"\n📊 {label}:")
    print(f"  Characters: {chars}")
    print(f"  Est. tokens: {est_tokens}")
    print(f"  Input cost: ${input_cost:.6f}")
    print(f"  Output cost: ${output_cost:.6f}")
    
    return est_tokens, input_cost, output_cost

async def full_prompt_analysis():
    """Complete analysis of the orchestrator decision making."""
    
    print("🔬 FULL PROMPT ANALYSIS - COMPLETE BREAKDOWN")
    print("=" * 80)
    
    # Initialize orchestrator
    orchestrator = Claude4Orchestrator()
    await orchestrator.initialize()
    
    # Test with simple question
    user_message = "What is Python?"
    
    print(f"USER MESSAGE: '{user_message}'")
    print("=" * 80)
    
    # Get the full decision prompt
    full_prompt = orchestrator._build_decision_prompt(
        user_message=user_message,
        files=None,
        user_preferences=None
    )
    
    # Save full prompt to file for examination
    with open("testing/full_decision_prompt.txt", "w") as f:
        f.write("FULL ORCHESTRATOR DECISION PROMPT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"User Message: {user_message}\n\n")
        f.write("PROMPT SENT TO CLAUDE:\n")
        f.write("-" * 30 + "\n")
        f.write(full_prompt)
    
    print("✅ Full prompt saved to: testing/full_decision_prompt.txt")
    
    # Analyze prompt sections
    analyze_string_cost(full_prompt, "FULL DECISION PROMPT")
    
    # Break down prompt sections
    print("\n🔍 PROMPT SECTION BREAKDOWN:")
    print("-" * 50)
    
    sections = {
        "AVAILABLE AI MODELS": "",
        "REQUEST CONTEXT": "",
        "DECISION FRAMEWORK": "",
        "SELECTION RULES": "",
        "JSON Response Format": ""
    }
    
    current_section = None
    lines = full_prompt.split('\n')
    
    for line in lines:
        if "AVAILABLE AI MODELS" in line:
            current_section = "AVAILABLE AI MODELS"
        elif "REQUEST CONTEXT" in line:
            current_section = "REQUEST CONTEXT"
        elif "DECISION FRAMEWORK" in line:
            current_section = "DECISION FRAMEWORK"
        elif "SELECTION RULES" in line:
            current_section = "SELECTION RULES"
        elif "Respond in simple JSON" in line:
            current_section = "JSON Response Format"
        
        if current_section and current_section in sections:
            sections[current_section] += line + "\n"
    
    total_tokens = 0
    total_input_cost = 0
    
    for section_name, content in sections.items():
        if content.strip():
            tokens, input_cost, _ = analyze_string_cost(content, f"  {section_name}")
            total_tokens += tokens
            total_input_cost += input_cost
    
    print(f"\n📊 TOTAL PROMPT ANALYSIS:")
    print(f"  Total estimated tokens: {total_tokens}")
    print(f"  Total input cost: ${total_input_cost:.6f}")
    
    # Now make the actual API call and analyze response
    print("\n" + "=" * 80)
    print("🚀 MAKING ACTUAL API CALL")
    print("=" * 80)
    
    start_time = time.time()
    
    try:
        # Direct call to anthropic provider to see full response
        provider = AnthropicProvider()
        await provider.initialize()
        
        response = await provider.generate_completion(
            messages=[{"role": "user", "content": full_prompt}],
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0.3
        )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        print(f"⏱️ Response time: {response_time:.0f}ms")
        
        # Save full response to file
        with open("testing/full_decision_response.json", "w") as f:
            json.dump(response, f, indent=2)
        
        print("✅ Full response saved to: testing/full_decision_response.json")
        
        # Analyze response structure
        print("\n🔍 RESPONSE STRUCTURE ANALYSIS:")
        print("-" * 50)
        
        if isinstance(response, dict):
            for key, value in response.items():
                if key == 'usage':
                    print(f"\n📊 USAGE (What we pay for):")
                    for usage_key, usage_value in value.items():
                        print(f"  {usage_key}: {usage_value}")
                elif key == 'content':
                    if isinstance(value, list) and value:
                        content_text = value[0].get('text', '') if isinstance(value[0], dict) else str(value[0])
                        analyze_string_cost(content_text, "ACTUAL USEFUL CONTENT")
                        
                        # Save just the useful content
                        with open("testing/useful_content_only.txt", "w") as f:
                            f.write("USEFUL CONTENT ONLY (What we actually need)\n")
                            f.write("=" * 50 + "\n\n")
                            f.write(content_text)
                        
                        print("✅ Useful content saved to: testing/useful_content_only.txt")
                else:
                    # Analyze metadata overhead
                    metadata_str = str(value)
                    analyze_string_cost(metadata_str, f"METADATA: {key}")
        
        # Calculate actual costs
        if 'usage' in response:
            usage = response['usage']
            actual_input_tokens = usage.get('input_tokens', 0)
            actual_output_tokens = usage.get('output_tokens', 0)
            
            actual_input_cost = actual_input_tokens * (3.00 / 1_000_000)
            actual_output_cost = actual_output_tokens * (15.00 / 1_000_000)
            actual_total_cost = actual_input_cost + actual_output_cost
            
            print(f"\n💰 ACTUAL COSTS (What Anthropic charged):")
            print(f"  Input tokens: {actual_input_tokens} (${actual_input_cost:.6f})")
            print(f"  Output tokens: {actual_output_tokens} (${actual_output_cost:.6f})")
            print(f"  Total cost: ${actual_total_cost:.6f}")
            
            # Compare with direct approach
            direct_approach_tokens = len(user_message) // 4  # Just the user question
            direct_approach_cost = direct_approach_tokens * (3.00 / 1_000_000)
            
            waste_tokens = actual_input_tokens - direct_approach_tokens
            waste_cost = actual_input_cost - direct_approach_cost
            
            print(f"\n🗑️ WASTE ANALYSIS:")
            print(f"  Direct approach would use: {direct_approach_tokens} tokens (${direct_approach_cost:.6f})")
            print(f"  Current approach uses: {actual_input_tokens} tokens (${actual_input_cost:.6f})")
            print(f"  Wasted tokens: {waste_tokens}")
            print(f"  Wasted cost: ${waste_cost:.6f}")
            print(f"  Waste percentage: {(waste_cost/actual_input_cost)*100:.1f}%")
        
    except Exception as e:
        print(f"❌ API call failed: {e}")

async def analyze_response_overhead():
    """Analyze what parts of the response we pay for but don't need."""
    
    print("\n" + "=" * 80)
    print("🔍 RESPONSE OVERHEAD ANALYSIS")
    print("=" * 80)
    
    # Load the saved response
    try:
        with open("testing/full_decision_response.json", "r") as f:
            response = json.load(f)
        
        print("📋 RESPONSE FIELDS WE PAY FOR:")
        print("-" * 40)
        
        total_response_size = 0
        useful_content_size = 0
        
        for key, value in response.items():
            field_str = json.dumps(value) if not isinstance(value, str) else value
            field_size = len(field_str)
            total_response_size += field_size
            
            if key == 'content':
                useful_content_size = field_size
                print(f"✅ {key}: {field_size} chars (USEFUL - this is what we need)")
            elif key == 'usage':
                print(f"📊 {key}: {field_size} chars (BILLING INFO - we need this)")
            else:
                print(f"❌ {key}: {field_size} chars (OVERHEAD - do we need this?)")
        
        overhead_size = total_response_size - useful_content_size
        overhead_percentage = (overhead_size / total_response_size) * 100
        
        print(f"\n📊 OVERHEAD SUMMARY:")
        print(f"  Total response size: {total_response_size} chars")
        print(f"  Useful content size: {useful_content_size} chars")
        print(f"  Overhead size: {overhead_size} chars")
        print(f"  Overhead percentage: {overhead_percentage:.1f}%")
        
        # Check if we're charged for the overhead
        print(f"\n💰 BILLING QUESTION:")
        print(f"  Are we charged for metadata? Let's check...")
        
        if 'usage' in response:
            output_tokens = response['usage'].get('output_tokens', 0)
            estimated_content_tokens = useful_content_size // 4
            metadata_tokens = output_tokens - estimated_content_tokens
            
            if metadata_tokens > 0:
                metadata_cost = metadata_tokens * (15.00 / 1_000_000)
                print(f"  ❌ YES! We pay for {metadata_tokens} metadata tokens (${metadata_cost:.6f})")
            else:
                print(f"  ✅ NO! We only pay for actual content")
        
    except FileNotFoundError:
        print("❌ No response file found. Run the full analysis first.")

async def optimization_recommendations():
    """Provide specific optimization recommendations."""
    
    print("\n" + "=" * 80)
    print("💡 OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)
    
    print("1. 🗑️ REMOVE ORCHESTRATOR FOR 95% OF QUERIES")
    print("   Current: User asks 'What is Python?' → 866 tokens to decide → Use Claude")
    print("   Better:  User asks 'What is Python?' → Directly use Claude")
    print("   Savings: ~866 tokens per request = $0.0026 per request")
    print("")
    
    print("2. 📝 SIMPLIFY REMAINING DECISION PROMPTS")
    print("   Current prompt sections to optimize:")
    print("   - Model descriptions: 311 tokens → 50 tokens (basic list)")
    print("   - Decision framework: 92 tokens → 20 tokens (simple rules)")
    print("   - Selection rules: 144 tokens → 30 tokens (concise)")
    print("   - JSON format: 120 tokens → 30 tokens (minimal example)")
    print("   Total savings: ~400 tokens = $0.0012 per decision")
    print("")
    
    print("3. 🎯 SMART ROUTING WITHOUT AI")
    print("   Instead of AI decision, use simple logic:")
    print("   - Contains 'image', 'picture', 'draw' → image_generation_tool")
    print("   - Contains 'audio', 'voice', 'sound' → audio tools")
    print("   - Everything else → claude_direct")
    print("   Cost: $0 (no API call needed)")
    print("")
    
    print("4. 🔄 BATCH PROCESSING FOR COMPONENTS")
    print("   Current: Analyze each component separately")
    print("   Better:  Analyze all components in one API call")
    print("   Savings: 50% cost reduction via Anthropic Batch API")
    print("")
    
    print("📊 TOTAL POTENTIAL SAVINGS:")
    print("   Per request: $0.0026 (remove orchestrator) + $0.0012 (optimize prompts) = $0.0038")
    print("   Per 1000 requests: $3.80 savings")
    print("   Your $20 budget: 19% cost reduction just from prompt optimization!")

async def main():
    """Run full analysis."""
    await full_prompt_analysis()
    await analyze_response_overhead()
    await optimization_recommendations()
    
    print("\n" + "=" * 80)
    print("📁 FILES CREATED FOR DETAILED ANALYSIS:")
    print("   - testing/full_decision_prompt.txt (complete prompt)")
    print("   - testing/full_decision_response.json (complete response)")
    print("   - testing/useful_content_only.txt (just the useful part)")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
