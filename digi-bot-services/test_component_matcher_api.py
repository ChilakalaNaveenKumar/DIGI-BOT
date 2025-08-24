"""
Test script for Component Matcher API
Tests the new thinking block streaming endpoint
"""

import asyncio
import json
import httpx
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_QUERY = "create a bar chart with sales data"

async def test_component_matcher_api():
    """Test the component matcher API endpoint"""
    
    print("🧪 Testing Component Matcher API with Thinking Blocks")
    print(f"📍 Base URL: {BASE_URL}")
    print(f"🔍 Test Query: {TEST_QUERY}")
    print("-" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test health check first
            print("1️⃣ Testing health check...")
            health_response = await client.get(f"{BASE_URL}/api/component-matcher/health")
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"✅ Health check passed: {health_data}")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                return
            
            print("\n2️⃣ Testing component matcher endpoint...")
            print("⚠️  Note: This test requires authentication token")
            print("   For full test, you need to:")
            print("   1. Login via Google OAuth")
            print("   2. Get access token from cookies")
            print("   3. Add Authorization header")
            
            # Test without authentication (should fail with 401)
            response = await client.post(
                f"{BASE_URL}/api/component-matcher/analyze",
                json={"query": TEST_QUERY}
            )
            
            if response.status_code == 401:
                print("✅ Authentication check working (401 Unauthorized as expected)")
            else:
                print(f"⚠️  Unexpected response: {response.status_code}")
                print(f"   Response: {response.text}")
            
            print("\n3️⃣ API Endpoint Details:")
            print(f"   📍 URL: POST {BASE_URL}/api/component-matcher/analyze")
            print(f"   🔐 Auth: Required (Cookie-based)")
            print(f"   📝 Body: {{'query': 'your component query'}}")
            print(f"   📤 Response: Server-Sent Events stream")
            print(f"   🧠 Format: Thinking blocks (thinking_start, thinking_delta, thinking_stop)")
            
            print("\n4️⃣ Expected Response Format:")
            print("   When match found:")
            print('   {"type": "thinking_start"}')
            print('   {"type": "thinking_delta", "text": "analyzing query..."}')
            print('   {"type": "thinking_delta", "text": "found components..."}')
            print('   {"type": "thinking_stop"}')
            print('   {"type": "content", "content": "component format"}')
            print('   {"type": "completion", "finish_reason": "done"}')
            print("\n   When no match:")
            print('   (empty stream)')
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    print(f"🚀 Starting Component Matcher API Test - {datetime.now()}")
    asyncio.run(test_component_matcher_api())
    print(f"\n✅ Test completed - {datetime.now()}")

