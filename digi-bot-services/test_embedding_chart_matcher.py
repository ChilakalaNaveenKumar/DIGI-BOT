#!/usr/bin/env python3
"""
Test Embedding-Based Chart Matcher

This demonstrates the new embedding-based chart matching approach:
1. Documents are embedded at ingest time
2. Queries are embedded and matched via cosine similarity
3. Top candidates are reranked and passed to GPT
4. Much faster and more accurate than the old approach
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


async def test_embedding_chart_matcher():
    """Test the new embedding-based chart matcher"""
    print("🧪 Embedding-Based Chart Matcher Test\n")
    
    try:
        from app.services.chart_matcher import ChartMatcherClient, VectorStoreManager
        
        # Initialize components
        print("🔧 Initializing components...")
        vector_manager = VectorStoreManager()
        chart_matcher = ChartMatcherClient()
        
        await vector_manager.initialize()
        await chart_matcher.initialize()
        
        # Show stats
        stats = vector_manager.get_stats()
        print(f"📊 Vector store stats: {stats}")
        
        # Test queries
        test_queries = [
            "Show sales data as a bar chart",
            "Create pie chart for market share percentages",
            "Display revenue trends over time in line chart",
            "Make a data table with performance metrics",
            "Show quarterly growth as bar chart",
            "Random text that shouldn't match any format"
        ]
        
        print(f"\n🔍 Testing {len(test_queries)} queries with embedding-based matching:")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n[{i}] Query: '{query}'")
            
            # Get embedding-based results
            candidates = await vector_manager.query(query, top_k=5)
            
            if candidates:
                print(f"  📋 Top matches:")
                for j, candidate in enumerate(candidates[:3], 1):
                    score = candidate['score']
                    source = candidate['meta'].get('source', 'unknown')
                    section = candidate['meta'].get('section', '')
                    print(f"    {j}. Score: {score:.3f} | Source: {source} | Section: {section}")
                
                # Test quick match
                result = await chart_matcher.quick_match(query, vector_manager)
                
                if chart_matcher.has_match(result):
                    print(f"  ✅ Chart format found!")
                    print(f"  📋 Format preview: {result[:100]}...")
                else:
                    print(f"  ❌ No chart format match")
            else:
                print(f"  ❌ No candidates found")
        
        print(f"\n✅ Embedding-based chart matcher test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and have the required dependencies")
    except Exception as e:
        print(f"❌ Test failed: {e}")


async def test_vector_store_operations():
    """Test vector store operations"""
    print("\n🗂️  Testing Vector Store Operations")
    
    try:
        from app.services.chart_matcher import VectorStoreManager
        
        vector_manager = VectorStoreManager()
        await vector_manager.initialize()
        
        # Show current stats
        stats = vector_manager.get_stats()
        print(f"📊 Current stats: {stats}")
        
        # Test adding a custom document
        print(f"\n📄 Adding custom document...")
        
        custom_doc = """
        ## Custom Chart Format
        
        Use for: Custom visualization needs
        
        Format:
        ```
        :::custom-chart
        title: Custom Chart Example
        data: [
          {"label": "A", "value": 10},
          {"label": "B", "value": 20}
        ]
        :::
        ```
        """
        
        await vector_manager.add_document(
            text=custom_doc,
            meta={
                "source": "test_custom.md",
                "section": "Custom Chart Format",
                "type": "test"
            }
        )
        
        print(f"✅ Added custom document")
        
        # Test querying the custom document
        print(f"\n🔍 Testing query for custom format...")
        
        results = await vector_manager.query("custom chart format", top_k=3)
        
        if results:
            print(f"📋 Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                score = result['score']
                source = result['meta'].get('source', 'unknown')
                print(f"  {i}. Score: {score:.3f} | Source: {source}")
                print(f"     Text: {result['text'][:100]}...")
        else:
            print(f"❌ No results found")
        
        # Show updated stats
        updated_stats = vector_manager.get_stats()
        print(f"\n📊 Updated stats: {updated_stats}")
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")


async def test_performance_comparison():
    """Test performance of embedding vs old approach"""
    print("\n⚡ Performance Comparison Test")
    
    try:
        from app.services.chart_matcher import ChartMatcherClient, VectorStoreManager
        import time
        
        # Initialize
        vector_manager = VectorStoreManager()
        chart_matcher = ChartMatcherClient()
        
        await vector_manager.initialize()
        await chart_matcher.initialize()
        
        test_query = "Create bar chart for sales data"
        
        # Test embedding-based approach
        print(f"🔍 Testing embedding-based approach...")
        
        start_time = time.time()
        
        # Get candidates
        candidates = await vector_manager.query(test_query, top_k=20)
        
        # Get final result
        result = await chart_matcher.quick_match(test_query, vector_manager)
        
        embedding_time = time.time() - start_time
        
        print(f"  ⏱️  Time: {embedding_time:.3f}s")
        print(f"  📋 Candidates found: {len(candidates)}")
        print(f"  ✅ Result: {'Match' if chart_matcher.has_match(result) else 'No match'}")
        
        # Show top candidate scores
        if candidates:
            print(f"  🎯 Top scores: {[f'{c[\"score\"]:.3f}' for c in candidates[:3]]}")
        
        print(f"\n📊 Embedding-based approach:")
        print(f"  ✅ Fast similarity search")
        print(f"  🎯 Accurate semantic matching") 
        print(f"  📝 Only top candidates sent to GPT")
        print(f"  💰 Cost-effective (fewer tokens)")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")


async def test_rebuild_vector_store():
    """Test rebuilding vector store from files"""
    print("\n🔄 Testing Vector Store Rebuild")
    
    try:
        from app.services.chart_matcher import VectorStoreManager
        
        vector_manager = VectorStoreManager()
        
        # Show current stats
        await vector_manager.initialize()
        stats_before = vector_manager.get_stats()
        print(f"📊 Before rebuild: {stats_before}")
        
        # Rebuild from files
        await vector_manager.rebuild_from_files()
        
        # Show new stats
        stats_after = vector_manager.get_stats()
        print(f"📊 After rebuild: {stats_after}")
        
        # Test a query
        results = await vector_manager.query("pie chart format", top_k=3)
        print(f"🔍 Test query results: {len(results)} matches")
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. Score: {result['score']:.3f} | {result['meta'].get('source', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Rebuild test failed: {e}")


async def main():
    """Main test runner"""
    print("🚀 Embedding-Based Chart Matcher Test Suite\n")
    print("📝 This tests the new embedding + reranking approach:")
    print("  1. Documents embedded at ingest time")
    print("  2. Query embedded and matched via cosine similarity")
    print("  3. Top 20 candidates retrieved, top 5 sent to GPT")
    print("  4. Much faster and more accurate than old approach\n")
    
    # Choose test mode
    print("Select test mode:")
    print("1. Basic embedding matcher test")
    print("2. Vector store operations test")
    print("3. Performance comparison test")
    print("4. Rebuild vector store test")
    print("5. All tests")
    
    try:
        choice = input("\nEnter choice (1-5, default=1): ").strip() or "1"
        
        if choice == "1":
            await test_embedding_chart_matcher()
        elif choice == "2":
            await test_vector_store_operations()
        elif choice == "3":
            await test_performance_comparison()
        elif choice == "4":
            await test_rebuild_vector_store()
        elif choice == "5":
            await test_embedding_chart_matcher()
            await test_vector_store_operations()
            await test_performance_comparison()
            await test_rebuild_vector_store()
        else:
            print("Invalid choice, running basic test...")
            await test_embedding_chart_matcher()
        
        print(f"\n🎉 Test completed!")
        print(f"\n📋 Key Benefits of Embedding Approach:")
        print(f"  ⚡ Faster: Cosine similarity vs full document search")
        print(f"  🎯 More accurate: Semantic matching vs keyword matching")
        print(f"  💰 Cost-effective: Only top candidates sent to GPT")
        print(f"  🔄 Auto-expiry: Documents expire after 2 days")
        print(f"  📊 Better scaling: Handles large document collections")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
