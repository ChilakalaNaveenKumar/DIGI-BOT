"""
Usage examples for Chart Matcher service.

These examples demonstrate how to use ChartMatcherClient and VectorStoreManager
for intelligent chart format matching and documentation management.
"""

import asyncio
import os
from typing import List, Dict, Any
from .client import ChartMatcherClient
from .vector_manager import VectorStoreManager


class ChartMatcherExamples:
    """Examples and utilities for Chart Matcher service"""
    
    def __init__(self):
        self.matcher = ChartMatcherClient()
        self.vector_manager = VectorStoreManager()
    
    async def setup_documentation(self):
        """Initialize vector store with chart documentation"""
        print("=== Setting up Chart Documentation ===")
        
        # Initialize vector store
        await self.vector_manager.initialize()
        
        # Get documents folder path
        docs_folder = self.vector_manager.get_documents_folder()
        
        # Ensure chart format documents exist in vector store
        chart_docs = [
            ("chartjs_markdown_format_v1.md", "Chart.js Format Documentation"),
            ("data_table_markdown_format_v1.md", "Data Table Format Documentation")
        ]
        
        for filename, description in chart_docs:
            file_path = os.path.join(docs_folder, filename)
            if os.path.exists(file_path):
                await self.vector_manager.ensure_file_exists(file_path, filename)
                print(f"✅ {description} ready")
            else:
                print(f"⚠️  {filename} not found at {file_path}")
    
    async def example_chart_queries(self):
        """Example chart format matching queries"""
        print("\n=== Chart Format Matching Examples ===")
        
        # Test queries that should match chart formats
        test_queries = [
            "Show me sales data by region as a bar chart",
            "Create a pie chart for market share percentages", 
            "Display revenue trends over time in a line chart",
            "Make a data table with product performance metrics",
            "Show quarterly growth in a bar chart",
            "Random text that shouldn't match any format"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            
            # Stream the response
            full_response = ""
            async for event in self.matcher.analyze(query):
                if event["type"] == "content":
                    full_response += event["content"]
                elif event["type"] == "error":
                    print(f"❌ Error: {event['error']}")
                    break
                elif event["type"] == "completion":
                    break
            
            # Check if we got a match
            if self.matcher.has_match(full_response):
                print(f"✅ Match found!")
                print(f"📋 Format: {full_response[:100]}...")
            else:
                print(f"❌ No match (response: {full_response})")
    
    async def example_quick_matching(self):
        """Example of quick non-streaming matching"""
        print("\n=== Quick Match Examples ===")
        
        queries = [
            "Show pie chart of browser usage",
            "Create bar chart for sales comparison", 
            "Display data table with financial metrics",
            "Just some regular text"
        ]
        
        for query in queries:
            print(f"\n🔍 Quick match: '{query}'")
            result = await self.matcher.quick_match(query)
            
            if self.matcher.has_match(result):
                print(f"✅ Quick match found!")
                print(f"📋 Format preview: {result[:150]}...")
            else:
                print(f"❌ No quick match")
    
    async def example_vector_store_management(self):
        """Example vector store file management"""
        print("\n=== Vector Store Management Examples ===")
        
        # List current files
        files = await self.vector_manager.list_files()
        print(f"\n📁 Current files in vector store ({len(files)}):")
        for file_info in files:
            print(f"  - {file_info['filename']} (ID: {file_info['id'][:8]}...)")
        
        # Query vector store directly
        print(f"\n🔍 Direct vector store query:")
        query_result = await self.vector_manager.query_vector_store(
            "Find chart formats for displaying sales data"
        )
        print(f"📋 Query result: {query_result[:200]}...")
    
    async def example_custom_documentation_matching(self):
        """Example with custom documentation"""
        print("\n=== Custom Documentation Matching ===")
        
        # Custom documentation for testing
        custom_docs = """
        # Custom Chart Format
        
        ## Scatter Plot Format
        Use for: Correlation analysis, data point relationships
        
        Format:
        ```
        :::scatter-chart
        title: Sales vs Marketing Spend
        data: [
          {"x": 1000, "y": 50000, "label": "Q1"},
          {"x": 1500, "y": 75000, "label": "Q2"},
          {"x": 2000, "y": 100000, "label": "Q3"}
        ]
        :::
        ```
        """
        
        query = "Show correlation between marketing spend and sales"
        print(f"🔍 Query with custom docs: '{query}'")
        
        full_response = ""
        async for event in self.matcher.analyze(query, documentation=custom_docs):
            if event["type"] == "content":
                full_response += event["content"]
            elif event["type"] == "error":
                print(f"❌ Error: {event['error']}")
                break
            elif event["type"] == "completion":
                break
        
        if self.matcher.has_match(full_response):
            print(f"✅ Custom format matched!")
            print(f"📋 Format: {full_response}")
        else:
            print(f"❌ No match with custom docs")
    
    async def example_integration_with_vision(self):
        """Example showing integration with vision models"""
        print("\n=== Integration with Vision Models ===")
        
        # Simulate a workflow where vision analysis leads to chart matching
        vision_analysis_result = """
        The image shows a bar chart with sales data across different regions:
        - North America: $125,000
        - Europe: $98,000  
        - Asia Pacific: $156,000
        - Latin America: $67,000
        """
        
        print(f"📸 Vision analysis result: {vision_analysis_result}")
        
        # Use chart matcher to find appropriate format for recreating this chart
        query = "Create a bar chart showing sales data by region with specific values"
        print(f"🔍 Chart matcher query: '{query}'")
        
        result = await self.matcher.quick_match(query)
        if self.matcher.has_match(result):
            print(f"✅ Found matching format for recreation!")
            print(f"📋 Suggested format: {result[:300]}...")
        else:
            print(f"❌ No matching format found")


async def example_complete_workflow():
    """Complete workflow example combining all features"""
    print("=== Complete Chart Matcher Workflow ===")
    
    examples = ChartMatcherExamples()
    
    # 1. Setup documentation
    await examples.setup_documentation()
    
    # 2. Test various matching scenarios
    await examples.example_chart_queries()
    await examples.example_quick_matching()
    
    # 3. Demonstrate vector store management
    await examples.example_vector_store_management()
    
    # 4. Show custom documentation usage
    await examples.example_custom_documentation_matching()
    
    # 5. Integration example
    await examples.example_integration_with_vision()
    
    print("\n✅ Chart Matcher workflow complete!")


async def example_batch_processing():
    """Example of processing multiple queries efficiently"""
    print("\n=== Batch Processing Example ===")
    
    matcher = ChartMatcherClient()
    
    # Batch of queries to process
    queries = [
        "Show revenue by quarter in a line chart",
        "Display customer satisfaction as pie chart", 
        "Create data table for product inventory",
        "Show correlation between price and sales",
        "Regular text without chart intent"
    ]
    
    print(f"Processing {len(queries)} queries...")
    
    results = []
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] Processing: '{query[:50]}...'")
        
        result = await matcher.quick_match(query)
        has_match = matcher.has_match(result)
        
        results.append({
            "query": query,
            "has_match": has_match,
            "result": result[:100] + "..." if len(result) > 100 else result
        })
        
        print(f"  {'✅' if has_match else '❌'} {'Match' if has_match else 'No match'}")
    
    # Summary
    matches = sum(1 for r in results if r["has_match"])
    print(f"\n📊 Batch Summary: {matches}/{len(queries)} queries matched formats")
    
    return results


async def example_error_handling():
    """Example demonstrating error handling"""
    print("\n=== Error Handling Examples ===")
    
    matcher = ChartMatcherClient()
    
    # Test with invalid API key (simulate error)
    print("🔍 Testing error scenarios...")
    
    try:
        # This should work normally
        result = await matcher.quick_match("Show sales in bar chart")
        print(f"✅ Normal operation successful")
        
        # Test streaming with error handling
        print("🔍 Testing streaming error handling...")
        async for event in matcher.analyze("Create pie chart for market data"):
            if event["type"] == "content":
                print(".", end="")
            elif event["type"] == "error":
                print(f"\n❌ Stream error: {event['error']}")
                break
            elif event["type"] == "completion":
                print(f"\n✅ Stream completed successfully")
                break
                
    except Exception as e:
        print(f"❌ Exception caught: {e}")


# Utility functions for integration
async def get_chart_format_for_data_type(data_description: str) -> str:
    """Utility: Get appropriate chart format for described data"""
    matcher = ChartMatcherClient()
    
    query = f"What chart format should I use for: {data_description}"
    result = await matcher.quick_match(query)
    
    return result if matcher.has_match(result) else "NO_MATCH"


async def validate_chart_format(format_text: str) -> bool:
    """Utility: Validate if text contains valid chart format"""
    # Simple validation - check for chart format markers
    chart_markers = [":::pie-chart", ":::bar-chart", ":::line-chart", ":::data-table"]
    return any(marker in format_text for marker in chart_markers)


# Main example runner
async def run_all_examples():
    """Run all chart matcher examples"""
    print("🚀 Starting Chart Matcher Examples\n")
    
    try:
        # Run complete workflow
        await example_complete_workflow()
        
        # Run batch processing
        await example_batch_processing()
        
        # Run error handling
        await example_error_handling()
        
        print("\n🎉 All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(run_all_examples())
