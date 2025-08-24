#!/usr/bin/env python3
"""
Test Chart Matcher Examples

Simple test script to demonstrate chart_matcher functionality.
Run this to see the chart matcher in action.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.chart_matcher.examples import ChartMatcherExamples, run_all_examples


async def simple_chart_matcher_test():
    """Simple test of chart matcher functionality"""
    print("🧪 Simple Chart Matcher Test\n")
    
    try:
        from app.services.chart_matcher import ChartMatcherClient
        
        # Initialize client
        matcher = ChartMatcherClient()
        print("✅ ChartMatcherClient initialized")
        
        # Test queries
        test_queries = [
            "Show sales data as a bar chart",
            "Create pie chart for market share",
            "Display revenue trends in line chart", 
            "Make data table with performance metrics",
            "This is just regular text"
        ]
        
        print(f"\n🔍 Testing {len(test_queries)} queries:")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n[{i}] Query: '{query}'")
            
            try:
                result = await matcher.quick_match(query)
                has_match = matcher.has_match(result)
                
                if has_match:
                    print(f"  ✅ Match found!")
                    print(f"  📋 Format preview: {result[:100]}...")
                else:
                    print(f"  ❌ No match")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print(f"\n✅ Simple test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and have the required dependencies")
    except Exception as e:
        print(f"❌ Test failed: {e}")


async def test_vector_store_setup():
    """Test vector store initialization"""
    print("\n🗂️  Testing Vector Store Setup")
    
    try:
        from app.services.chart_matcher import VectorStoreManager
        
        vector_manager = VectorStoreManager()
        await vector_manager.initialize()
        
        # List files
        files = await vector_manager.list_files()
        print(f"📁 Vector store has {len(files)} files:")
        for file_info in files:
            print(f"  - {file_info.get('filename', 'Unknown')}")
        
        # Test query
        result = await vector_manager.query_vector_store("Find chart formats")
        print(f"🔍 Query result: {result[:150]}...")
        
        print("✅ Vector store test completed!")
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")


async def main():
    """Main test runner"""
    print("🚀 Chart Matcher Examples Test Suite\n")
    
    # Choose test mode
    print("Select test mode:")
    print("1. Simple test (quick)")
    print("2. Vector store test")
    print("3. Full examples (comprehensive)")
    print("4. All tests")
    
    try:
        choice = input("\nEnter choice (1-4, default=1): ").strip() or "1"
        
        if choice == "1":
            await simple_chart_matcher_test()
        elif choice == "2":
            await test_vector_store_setup()
        elif choice == "3":
            await run_all_examples()
        elif choice == "4":
            await simple_chart_matcher_test()
            await test_vector_store_setup()
            await run_all_examples()
        else:
            print("Invalid choice, running simple test...")
            await simple_chart_matcher_test()
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
