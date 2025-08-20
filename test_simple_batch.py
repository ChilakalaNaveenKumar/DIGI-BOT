#!/usr/bin/env python3
"""
Simple test of BatchAnalysisEngine with timing and direct output to file.
"""
import asyncio
import json
import time
import sys
import os

# Add backend to path
sys.path.append('backend')
os.chdir('backend')

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
    print(f"🔪 Segmentation time: {segmentation_time:.2f}s")
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

if __name__ == "__main__":
    asyncio.run(test_batch_engine())
