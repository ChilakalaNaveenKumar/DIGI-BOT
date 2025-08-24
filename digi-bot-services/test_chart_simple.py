"""
Simple Chart Format Test
Tests the chart format system with real OpenAI API calls
"""
import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append('/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services')

from app.services.openai_provider.main_provider import OpenAIProvider
from app.services.openai_provider.services.file_service import FileService
from app.services.openai_provider.core.client import OpenAIClient

async def upload_chart_documentation():
    """Upload chart_tools_documentation.md to vector store"""
    
    print("📚 Uploading chart documentation to vector store...")
    
    # Initialize OpenAI client and file service
    client = OpenAIClient()
    await client.initialize()
    file_service = FileService(client)
    
    # Path to the chart documentation
    doc_path = '/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services/app/services/openai_provider/chart_tools_documentation.md'
    
    try:
        # Upload the documentation file
        with open(doc_path, 'rb') as f:
            file_id = await file_service.upload_file(
                file_content=f,
                filename='chart_tools_documentation.md',
                purpose='assistants'
            )
        
        print(f"✅ Documentation uploaded with file_id: {file_id}")
        
        # Create vector store
        vector_store = await file_service.create_vector_store(
            name="Chart Tools Documentation",
            file_ids=[file_id]
        )
        
        print(f"✅ Vector store created: {vector_store.id}")
        print(f"   Name: {vector_store.name}")
        print(f"   File count: {vector_store.file_count}")
        
        return vector_store.id, file_id
        
    except Exception as e:
        print(f"❌ Failed to upload documentation: {e}")
        return None, None

async def test_chart_format():
    """Test the chart format system"""
    
    print("🚀 Starting Chart Format Test")
    print("="*50)
    
    # Debug: Check if API key is loaded
    api_key = os.getenv('OPENAI_API_KEY', 'NOT_FOUND')
    print(f"🔑 API Key loaded: {api_key[:20]}..." if api_key != 'NOT_FOUND' else "❌ API Key not found")
    
    # Initialize provider
    provider = OpenAIProvider()
    await provider.initialize()
    
    print("✅ OpenAI Provider initialized successfully")
    
    # Upload chart documentation to vector store
    vector_store_id, file_id = await upload_chart_documentation()
    
    if not vector_store_id:
        print("⚠️  Continuing without vector store...")
        vector_store_id = None
    else:
        print(f"✅ Using vector store: {vector_store_id}")
    
    # Test cases
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
            "name": "Instructions (Should NOT Use Chart)",
            "query": "How do I make a cup of coffee?",
            "should_have_chart": False
        },
        {
            "name": "Explain in difference between coffee and tea benefits and disbenifits",
            "query": "Explain in difference between coffee and tea benefits and disbenifits",
            "should_have_chart": True
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test_case['name']}")
        print(f"Query: {test_case['query']}")
        print(f"Expected chart: {'YES' if test_case['should_have_chart'] else 'NO'}")
        print("-" * 50)
        
        try:
            # Add system message to trigger chart awareness
            system_message = (
                "Use the chart_tools_documentation.md. Analyze the question and analyze whether we can use any formats from that document to answer this question. Your job is find any connection and representation match with question anc document"
            )

            # Print what we're sending to AI
            print("📤 SENDING TO AI:")
            print(f"   Model: gpt-4o")
            print(f"   Query: {test_case['query']}")
            if vector_store_id:
                print(f"   Vector Store: {vector_store_id}")
            print()
            
            # Stream the response
            print("📥 AI RESPONSE:")
            full_response = ""
            
            # Build the input payload for Responses API (RAG variant using vector store)
            input_payload = [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system_message}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": test_case["query"]}],
                },
            ]
            
            # Use the Responses API with file_search (vector_store_ids go inside tools)
            async for chunk in provider.stream_response_with_file_search(
                model="gpt-4o",
                input_payload=input_payload,
                vector_store_ids=[vector_store_id] if vector_store_id else None,
                max_output_tokens=16000
            ):
                if chunk["type"] == "content":
                    print(chunk["content"], end="", flush=True)
                    full_response += chunk["content"]
                elif chunk["type"] == "completion":
                    print(f"\n✅ Completed (reason: {chunk.get('finish_reason', 'unknown')})")
                elif chunk["type"] == "error":
                    print(f"\n❌ Error: {chunk['error']}")
                    break
            
            # Analyze response
            has_chart_format = any(chart_type in full_response for chart_type in [
                ":::pie-chart", ":::bar-chart", ":::line-chart", ":::data-table"
            ])
            
            chart_types_found = []
            for chart_type in [":::pie-chart", ":::bar-chart", ":::line-chart", ":::data-table"]:
                if chart_type in full_response:
                    chart_types_found.append(chart_type.replace(":::", ""))
            
            test_passed = (has_chart_format == test_case["should_have_chart"])
            
            print(f"\n📄 FULL RESPONSE RECEIVED:")
            print(f"   Length: {len(full_response)} characters")
            print(f"   Content: {full_response[:200]}{'...' if len(full_response) > 200 else ''}")
            print()
            
            print(f"📈 Analysis:")
            print(f"   Chart format used: {'YES' if has_chart_format else 'NO'}")
            print(f"   Chart types found: {chart_types_found if chart_types_found else 'None'}")
            print(f"   Expected chart: {'YES' if test_case['should_have_chart'] else 'NO'}")
            print(f"   Test result: {'✅ PASSED' if test_passed else '❌ FAILED'}")
            
            results.append({
                "name": test_case["name"],
                "passed": test_passed,
                "has_chart": has_chart_format,
                "expected_chart": test_case["should_have_chart"],
                "chart_types": chart_types_found,
                "response_length": len(full_response)
            })
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append({
                "name": test_case["name"],
                "passed": False,
                "error": str(e)
            })
        
        print("\n" + "="*50)
        
        # Small delay between tests
        await asyncio.sleep(2)
    
    # Final summary
    print(f"\n🎉 TEST SUMMARY")
    print("="*50)
    
    passed_tests = sum(1 for r in results if r.get("passed", False))
    total_tests = len(results)
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests*100):.1f}%")
    
    print(f"\n📊 Detailed Results:")
    for result in results:
        status = "✅ PASS" if result.get("passed", False) else "❌ FAIL"
        print(f"   {status} - {result['name']}")
        if result.get("error"):
            print(f"      Error: {result['error']}")
        else:
            print(f"      Chart used: {'YES' if result.get('has_chart', False) else 'NO'}")
            if result.get("chart_types"):
                print(f"      Chart types: {result['chart_types']}")
    
    return results

async def main():
    """Main test execution"""
    try:
        results = await test_chart_format()
        
        print(f"\n🎯 CONCLUSION:")
        print("The chart format system has been tested with real OpenAI API calls.")
        print("Check the results above to see if the AI appropriately uses chart formats.")
        
        return results
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
