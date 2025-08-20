#!/usr/bin/env python3
"""
Simple test of BatchAnalysisEngine with timing and direct output to file.
"""
import asyncio
import json
import time

from app.services.batch_analysis_engine import BatchAnalysisEngine

# Sample content from frontend demo
TEST_CONTENT = """# Financial Performance Overview

### Revenue Distribution Analysis

Our total quarterly revenue reached $4.2M, distributed as follows:

- SaaS Products: $1.89M (45%)
- Professional Services: $1.26M (30%) 
- Enterprise Solutions: $840K (20%)
- Training & Support: $210K (5%)

### Monthly Revenue Progression

The revenue growth throughout the quarter showed consistent upward momentum:

January generated $1.2M, February achieved $1.35M, March reached $1.65M.

### Operating Expenses Analysis

Total operating expenses were $3.1M for the quarter:

- Personnel & Benefits: $1.55M (50%)
- Sales & Marketing: $620K (20%)
- Technology Infrastructure: $465K (15%)
- Research & Development: $310K (10%)
- Administrative Costs: $155K (5%)"""

async def test_batch_engine():
    """Test BatchAnalysisEngine with timing."""
    
    print("🧪 Testing BatchAnalysisEngine...")
    
    # Initialize engine
    engine = BatchAnalysisEngine()
    await engine.initialize()
    
    # Add content
    engine.add_content(TEST_CONTENT)
    
    # Process batch with timing
    start_time = time.time()
    result = await engine.process_batch()
    total_time = time.time() - start_time
    
    # Extract timing info
    metadata = result.get('metadata', {})
    blocks_found = metadata.get('blocks_found', 0)
    components_generated = len(result.get('components', []))
    segmentation_time = metadata.get('segmentation_time', 0)
    analysis_time = metadata.get('analysis_time', 0)
    
    # Print summary
    print(f"⏱️  Total time: {total_time:.2f}s")
    print(f"📦 Blocks found: {blocks_found}")
    print(f"🎯 Components generated: {components_generated}")
    if segmentation_time > 0:
        print(f"🔪 Segmentation time: {segmentation_time:.2f}s")
    if analysis_time > 0:
        print(f"🧠 Analysis time: {analysis_time:.2f}s")
    
    # Write full result to file
    output_data = {
        "timing": {
            "total_time": total_time,
            "segmentation_time": segmentation_time,
            "analysis_time": analysis_time
        },
        "summary": {
            "blocks_found": blocks_found,
            "components_generated": components_generated
        },
        "full_result": result
    }
    
    with open("batch_test_output.txt", "w") as f:
        f.write("BATCH ANALYSIS ENGINE TEST RESULT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total Time: {total_time:.2f}s\n")
        f.write(f"Blocks Found: {blocks_found}\n")
        f.write(f"Components Generated: {components_generated}\n")
        f.write(f"Segmentation Time: {segmentation_time:.2f}s\n")
        f.write(f"Analysis Time: {analysis_time:.2f}s\n\n")
        f.write("FULL JSON RESULT:\n")
        f.write("=" * 20 + "\n")
        f.write(json.dumps(result, indent=2))
    
    print("📁 Full result written to batch_test_output.txt")
    
    # Show components if any
    if result.get('components'):
        print("\n🎯 Components Generated:")
        for i, comp in enumerate(result.get('components', [])):
            comp_type = comp.get('component_type', 'unknown')
            decision = comp.get('decision', 'unknown')
            confidence = comp.get('confidence', 0)
            print(f"   {i+1}. {comp_type} (decision: {decision}, confidence: {confidence})")
    else:
        print("\n❌ No components generated - check Claude responses")
    
    # Show actual Claude responses for debugging
    print("\n🔍 DEBUG: Check what Claude actually returned...")
    await show_claude_responses(engine)
    
    # Also test segmentation directly to see why it's slow
    print("\n🔪 DEBUG: Testing segmentation directly...")
    await test_segmentation_directly(engine)
    
async def show_claude_responses(engine):
    """Debug function to show what Claude actually returned."""
    
    # Test a single block analysis to see raw output
    test_block = {
        'content': '- SaaS Products: $1.89M (45%)\n- Professional Services: $1.26M (30%)\n- Enterprise Solutions: $840K (20%)',
        'start_position': 0,
        'end_position': 100
    }
    
    print("🔍 Testing single block analysis...")
    print(f"Block content: {test_block['content'][:50]}...")
    
    # Call the analysis function directly
    try:
        result = await engine._analyze_single_block(test_block)
        print(f"✅ Analysis result: {result}")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
    
    # Also test the raw Claude call
    print("\n🧠 Testing raw Claude response...")
    
    analysis_prompt = f"""
Analyze this content and determine if it should generate an interactive component.

CONTENT TO ANALYZE:
{test_block['content']}

AVAILABLE COMPONENTS:

## PieChart (:::pie-chart)
- Purpose: Display percentage-based data as circular segments
- Best for: Market share, demographics, survey results, categorical percentages
- When to use: Content mentions percentages, proportions, parts of a whole

RESPONSE FORMAT (JSON only):
{{
  "decision": "GENERATE_NOW" or "NO_COMPONENT",
  "component_type": "pie-chart" | "bar-chart" | "line-chart" | "data-table" | null,
  "confidence": 0.0-1.0,
  "markdown": ":::component-type\\ntitle: Title\\ndata:\\n  - {{label: \\"Item\\", value: 100}}\\n:::" | null
}}

IMPORTANT:
- Generate components when data is present that would benefit from visualization
- Extract real data from content, never invent data
- Use exact markdown syntax: :::component-type with YAML data format
- Confidence must be > 0.5 for generation

Use your thinking process to analyze this thoroughly before responding.
"""

    messages = [
        {
            "role": "system",
            "content": "You are an expert content enhancement analyst. Think through each decision carefully and provide detailed reasoning."
        },
        {
            "role": "user", 
            "content": analysis_prompt
        }
    ]
    
    try:
        # Use Claude 4 with thinking for high-quality analysis
        response_content = ""
        async for chunk in engine.anthropic_provider.stream_completion(
            messages=messages,
            model="claude-3-5-sonnet-20241022",  # Use latest Claude model
            max_tokens=2000,
            temperature=0.2,
            enable_thinking=True  # Enable thinking process
        ):
            if chunk.get("type") == "content":
                response_content += chunk.get("content", "")
        
        print(f"📝 Raw Claude response length: {len(response_content)}")
        print(f"📝 Raw Claude response:\n{response_content}")
        
        # Try to parse it
        if response_content.strip().startswith("```json"):
            cleaned = response_content.replace("```json", "").replace("```", "").strip()
            print(f"🧹 Cleaned response: {cleaned}")
            try:
                parsed = json.loads(cleaned)
                print(f"✅ Successfully parsed: {parsed}")
            except Exception as parse_error:
                print(f"❌ Parse error: {parse_error}")
        else:
            print("❌ Response doesn't start with ```json")
        
    except Exception as e:
        print(f"❌ Raw Claude call failed: {e}")

async def test_segmentation_directly(engine):
    """Test segmentation directly to see why it's slow."""
    
    short_content = "Revenue: $1.2M (45%), Expenses: $800K (30%), Profit: $400K (25%)"
    
    print(f"🔪 Testing segmentation on short content: {short_content}")
    print(f"📝 Content length: {len(short_content)} chars")
    
    start_time = time.time()
    blocks = await engine.openai_provider.segment_content_blocks(
        content=short_content,
        context="Test segmentation"
    )
    seg_time = time.time() - start_time
    
    print(f"⏱️  Segmentation time: {seg_time:.2f}s")
    print(f"📦 Blocks found: {len(blocks) if blocks else 0}")
    if blocks:
        for i, block in enumerate(blocks):
            print(f"   Block {i+1}: [{block.get('start_position', 0)}, {block.get('end_position', 0)}]")

if __name__ == "__main__":
    asyncio.run(test_batch_engine())
