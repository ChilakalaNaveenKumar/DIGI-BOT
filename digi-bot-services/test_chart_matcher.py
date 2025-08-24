"""
Chart Matcher Test with o1-preview and Vector Store
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append('/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services')

from app.services.chart_matcher import ChartMatcherClient, VectorStoreManager

async def setup_vector_store():
    """Setup vector store with chart and data table documentation"""
    
    print("📚 Setting up vector store...")
    
    vector_manager = VectorStoreManager()
    await vector_manager.initialize()
    
    # Insert Chart.js documentation
    chartjs_path = "/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services/app/services/chart_matcher/documents/chartjs_markdown_format_v1.md"
    
    # Insert Data Table documentation
    datatable_path = "/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services/app/services/chart_matcher/documents/data_table_markdown_format_v1.md"
    
    try:
        # Ensure Chart.js documentation exists (only uploads if missing)
        chartjs_file_id = await vector_manager.ensure_file_exists(
            chartjs_path, 
            "chartjs_markdown_format_v1.md"
        )
        
        # Ensure Data Table documentation exists (only uploads if missing)
        datatable_file_id = await vector_manager.ensure_file_exists(
            datatable_path,
            "data_table_markdown_format_v1.md"
        )
        
        print(f"📚 Documentation ready - Chart.js: {chartjs_file_id}, Data Table: {datatable_file_id}")
        return vector_manager
        
    except Exception as e:
        print(f"❌ Failed to setup vector store: {e}")
        return None

async def test_chart_matcher():
    """Test chart matcher with o1-preview"""
    
    print("🚀 Testing Chart Matcher with o1-preview")
    print("=" * 50)
    
    # Setup vector store
    vector_manager = await setup_vector_store()
    if not vector_manager:
        print("❌ Cannot continue without vector store")
        return
    
    # Initialize o1-preview client
    client = ChartMatcherClient()
    await client.initialize()
    
    # Test cases (same as original)
    test_cases = [
        {
            "name": "Market Share Query (Should Use Pie Chart)",
            "query": "What's the market share of social media platforms in 2025? Instagram has 45%, TikTok 30%, Facebook 15%, and Twitter 10%.",
            "should_have_chart": True
        },
        {
            "name": "Sales Comparison (Should Use Bar Chart)", 
            "query": "Compare our quarterly sales for 2025: Q1 had $125K, Q2 had $145K, Q3 had $162K, and Q4 had $178K.",
            "should_have_chart": True
        },
        {
            "name": "Simple Definition (Should NOT Use Chart)",
            "query": "What is artificial intelligence?",
            "should_have_chart": False
        },
        {
            "name": "Complex Data (Should Use Data Table)",
            "query": "Show me detailed performance metrics for our products including sales, units, growth, and ratings",
            "should_have_chart": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test_case['name']}")
        print(f"Query: {test_case['query']}")
        print("-" * 50)
        
        try:
            # Get documentation from vector store
            documentation = await vector_manager.query_vector_store(
                f"Find chart format examples for: {test_case['query']}"
            )
            
            print("🧠 Using gpt-4o with vector store documentation...")
            
            # Stream response with thinking chunks
            full_response = ""
            async for chunk in client.analyze_with_thinking(test_case['query'], documentation):
                if chunk["type"] == "content":
                    print(chunk["content"], end="", flush=True)
                    full_response += chunk["content"]
                elif chunk["type"] == "completion":
                    print(f"\n✅ Completed (reason: {chunk.get('finish_reason', 'unknown')})")
                elif chunk["type"] == "error":
                    print(f"\n❌ Error: {chunk['error']}")
                    break
            
            # Check if chart format was generated
            has_chart = ":::" in full_response
            expected = test_case["should_have_chart"]
            
            print(f"\n📈 Analysis:")
            print(f"   Chart format found: {'YES' if has_chart else 'NO'}")
            print(f"   Expected chart: {'YES' if expected else 'NO'}")
            print(f"   Test result: {'✅ PASSED' if has_chart == expected else '❌ FAILED'}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print("\n" + "=" * 50)

async def main():
    """Main test execution"""
    await test_chart_matcher()

if __name__ == "__main__":
    asyncio.run(main())
