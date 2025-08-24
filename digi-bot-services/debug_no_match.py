"""
Debug why certain queries are returning NO_MATCH
These should clearly match components
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

# Queries that should match but returned NO_MATCH
SHOULD_MATCH_QUERIES = [
    "Team productivity: Frontend: 45 tasks, Backend: 38 tasks, QA: 29 tasks",
    "Employee records: John (Manager, $80k), Sarah (Developer, $70k), Mike (Designer, $65k)",
    "Inventory: Laptops: 45 units, Monitors: 23 units, Keyboards: 67 units"
]

async def debug_no_match():
    """Debug why these queries return NO_MATCH"""
    
    print("🔍 Debugging NO_MATCH Results")
    print("🎯 These queries should clearly match components")
    print("=" * 60)
    
    try:
        from app.services.component_matcher import ComponentMatcherClient, VectorStoreManager
        
        # Initialize
        client = ComponentMatcherClient()
        await client.initialize()
        
        vector_manager = VectorStoreManager()
        await vector_manager.initialize()
        
        print(f"✅ Initialized: {client.model}")
        print()
        
        for i, query in enumerate(SHOULD_MATCH_QUERIES, 1):
            print(f"🔍 Debug {i}: '{query}'")
            print("-" * 50)
            
            # Get full streaming response to see what's happening
            print("📤 Full streaming response:")
            full_response = ""
            
            async for event in client.analyze(query, vector_manager):
                if event["type"] == "content":
                    content = event["content"]
                    full_response += content
                    print(f"   Content: {content}")
                elif event["type"] == "error":
                    print(f"   ❌ Error: {event['error']}")
                elif event["type"] == "completion":
                    print(f"   ✅ Completed: {event['finish_reason']}")
            
            print(f"\n📝 Full Response: '{full_response}'")
            
            # Check match detection
            has_match = client.has_match(full_response)
            print(f"🎯 Has Match: {has_match}")
            
            if not has_match:
                print("❓ Why NO_MATCH?")
                if full_response.strip().upper() == "NO_MATCH":
                    print("   AI explicitly returned 'NO_MATCH'")
                elif not full_response.strip():
                    print("   Empty response")
                else:
                    print(f"   Response: '{full_response.strip()}'")
                    print("   has_match() logic might be wrong")
            
            print()
    
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

async def test_has_match_logic():
    """Test the has_match logic with different responses"""
    
    print("🧪 Testing has_match() Logic")
    print("=" * 60)
    
    try:
        from app.services.component_matcher import ComponentMatcherClient
        
        client = ComponentMatcherClient()
        
        test_responses = [
            "NO_MATCH",
            "no match",
            "No Match",
            "",
            "   ",
            "Some component code here",
            ":::bar-chart\ndata: [...]\n:::",
            "```json\n[{\"label\": \"test\"}]\n```"
        ]
        
        for response in test_responses:
            has_match = client.has_match(response)
            print(f"Response: '{response}' → Has Match: {has_match}")
    
    except Exception as e:
        print(f"❌ has_match test failed: {e}")

async def main():
    """Debug NO_MATCH issues"""
    
    await debug_no_match()
    
    print("\n" + "=" * 60)
    
    await test_has_match_logic()
    
    print("\n" + "=" * 60)
    print("🎯 Analysis:")
    print("These queries have clear data patterns:")
    print("📊 'Frontend: 45, Backend: 38, QA: 29' → Bar Chart comparison")
    print("📋 'John (Manager, $80k), Sarah (Developer, $70k)' → Data Table")
    print("📋 'Laptops: 45 units, Monitors: 23 units' → Inventory Table")
    print()
    print("If they're returning NO_MATCH, either:")
    print("1. AI prompt needs improvement")
    print("2. Component documentation doesn't cover these patterns")
    print("3. Vector search isn't finding relevant docs")

if __name__ == "__main__":
    asyncio.run(main())

