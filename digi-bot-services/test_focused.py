"""
Focused test for one query
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append('/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services')

from app.services.chart_matcher import ChartMatcherClient, VectorStoreManager

async def test_focused():
    """Test one query end-to-end"""
    
    print("🎯 Focused Test: Market Share Query")
    print("=" * 50)
    
    # Setup
    vector_manager = VectorStoreManager()
    await vector_manager.initialize()
    
    client = ChartMatcherClient()
    await client.initialize()
    
    query = "Explain in detail about data distribution"
    
    print(f"📝 Query: {query}")
    print("-" * 50)
    
    # Step 1: Get documentation
    print("📚 Getting documentation from vector store...")
    documentation = await vector_manager.query_vector_store(f"Find chart format for: {query}")
    
    print(f"✅ Documentation received ({len(documentation)} chars)")
    print(f"📄 Sample: {documentation[:150]}...")
    print()
    
    # Step 2: Analyze with client
    print("🧠 Analyzing with gpt-4o...")
    
    try:
        full_response = ""
        async for chunk in client.analyze_with_thinking(query, documentation):
            if chunk["type"] == "content":
                print(chunk["content"], end="", flush=True)
                full_response += chunk["content"]
            elif chunk["type"] == "completion":
                print(f"\n✅ Completed")
                break
            elif chunk["type"] == "error":
                print(f"\n❌ Error: {chunk['error']}")
                break
        
        # Check result
        has_chart = ":::" in full_response
        print(f"\n📊 Analysis:")
        print(f"   Chart format found: {'YES' if has_chart else 'NO'}")
        print(f"   Response length: {len(full_response)} chars")
        
        if has_chart:
            print("✅ SUCCESS: Chart format detected!")
        else:
            print("❌ FAILED: No chart format found")
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_focused())
