"""
Test the new Generic Matcher
"""
import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append('/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services')

from app.services.chart_matcher import ChartMatcherClient

async def test_generic_matcher():
    """Test the generic matcher functionality"""
    
    print("🔧 Testing Generic Matcher")
    print("=" * 50)
    
    # Initialize client
    client = ChartMatcherClient()
    await client.initialize()
    
    # Test queries
    test_queries = [
        "What's the market share of social media platforms? Instagram 45%, TikTok 30%, Facebook 15%, Twitter 10%",
        "Compare quarterly sales: Q1 $125K, Q2 $145K, Q3 $162K, Q4 $178K",
        "What is artificial intelligence?",
        "Show detailed performance metrics with sales, units, growth, ratings",
        "How do I make coffee?"
    ]
    
    print(f"\n📋 Testing {len(test_queries)} queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 Test {i}: {query[:60]}{'...' if len(query) > 60 else ''}")
        print("-" * 40)
        
        try:
            # Use quick_match (automatically gets documentation from vector store)
            result = await client.quick_match(query)
            
            print(f"📊 Result:")
            if client.has_match(result):
                print(f"   ✅ MATCH FOUND")
                print(f"   📄 Format:")
                print(f"   {result}")
            else:
                print(f"   ❌ NO_MATCH")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print("\n" + "=" * 50 + "\n")
    
    print("✅ Generic matcher test completed!")

async def test_streaming():
    """Test streaming analysis"""
    
    print("🌊 Testing Streaming Analysis")
    print("=" * 50)
    
    client = ChartMatcherClient()
    await client.initialize()
    
    query = "What's the market share of social media platforms? Instagram 45%, TikTok 30%"
    
    print(f"📝 Query: {query}")
    print("📡 Streaming response:")
    print("-" * 40)
    
    full_response = ""
    async for chunk in client.analyze(query):
        if chunk["type"] == "content":
            print(chunk["content"], end="", flush=True)
            full_response += chunk["content"]
        elif chunk["type"] == "completion":
            print(f"\n✅ Completed")
            break
        elif chunk["type"] == "error":
            print(f"\n❌ Error: {chunk['error']}")
            break
    
    print(f"\n📊 Has match: {'YES' if client.has_match(full_response) else 'NO'}")

async def main():
    """Main test execution"""
    await test_generic_matcher()
    print("\n")
    await test_streaming()

if __name__ == "__main__":
    asyncio.run(main())
