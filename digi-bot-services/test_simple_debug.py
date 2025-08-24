"""
Simple debug test for chart matcher
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append('/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services')

from app.services.chart_matcher import ChartMatcherClient, VectorStoreManager

async def test_simple():
    """Simple test"""
    
    print("🔍 Simple Debug Test")
    print("=" * 30)
    
    # Test 1: Just vector store query
    print("📚 Testing vector store query...")
    vector_manager = VectorStoreManager()
    await vector_manager.initialize()
    
    try:
        result = await vector_manager.query_vector_store("pie chart example")
        print(f"✅ Vector store result length: {len(result)} characters")
        print(f"📄 First 200 chars: {result[:200]}...")
    except Exception as e:
        print(f"❌ Vector store failed: {e}")
        return
    
    # Test 2: Simple client query
    print("\n🧠 Testing client...")
    client = ChartMatcherClient()
    await client.initialize()
    
    try:
        simple_result = await client.quick_analysis(
            "What's the market share?", 
            "Use pie chart for market share data."
        )
        print(f"✅ Client result: {simple_result[:200]}...")
    except Exception as e:
        print(f"❌ Client failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple())

