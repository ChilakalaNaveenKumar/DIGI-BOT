"""
Test the new check_match function
"""
import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append('/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services')

from app.services.chart_matcher import ChartMatcherClient

async def test_match_checker():
    """Test the check_match function"""
    
    print("🔍 Testing Chart Match Checker")
    print("=" * 50)
    
    # Initialize client (will show gpt-4.5 or fallback to gpt-4o)
    client = ChartMatcherClient()
    await client.initialize()
    
    # Test queries
    test_queries = [
        "What's the market share of social media platforms? Instagram 45%, TikTok 30%",
        "Compare quarterly sales: Q1 $125K, Q2 $145K, Q3 $162K",
        "What is artificial intelligence?",
        "Show detailed performance metrics with sales, units, growth, ratings",
        "How do I make coffee?"
    ]
    
    print(f"\n📋 Testing {len(test_queries)} queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 Test {i}: {query[:60]}{'...' if len(query) > 60 else ''}")
        print("-" * 40)
        
        try:
            # Use check_match function (automatically gets documentation from vector store)
            result = await client.check_match(query)
            
            print(f"📊 Result:")
            print(f"   Has Match: {'✅ YES' if result['has_match'] else '❌ NO'}")
            print(f"   Chart Type: {result['chart_type']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Reasoning: {result['reasoning']}")
            
            if result.get('error'):
                print(f"   ⚠️  Error: {result['error']}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print("\n" + "=" * 50 + "\n")
    
    print("✅ Match checker test completed!")

async def main():
    """Main test execution"""
    await test_match_checker()

if __name__ == "__main__":
    asyncio.run(main())

