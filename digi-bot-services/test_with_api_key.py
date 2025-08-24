"""
Test Component Matcher with Real OpenAI API Key
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_component_matcher_initialization():
    """Test component matcher with real API key"""
    print("🔑 Testing Component Matcher with Real API Key...")
    
    try:
        from app.services.component_matcher import ComponentMatcherClient
        
        # Check if API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your-openai-api-key-here':
            print("⚠️  OpenAI API key not set or is placeholder")
            print("   Please set a real OpenAI API key in .env file")
            return False
        
        print(f"✅ OpenAI API key found (length: {len(api_key)})")
        
        # Create client
        client = ComponentMatcherClient()
        print(f"✅ Client created with model: {client.model}")
        
        # Try to initialize
        try:
            await client.initialize()
            print("✅ Client initialized successfully!")
            print("   Component matcher is ready for real queries")
            return True
        except Exception as init_error:
            print(f"❌ Initialization failed: {init_error}")
            if "quota" in str(init_error).lower():
                print("   This might be due to API quota limits")
            elif "authentication" in str(init_error).lower():
                print("   This might be due to invalid API key")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

async def test_vector_store_initialization():
    """Test vector store initialization"""
    print("\n📊 Testing Vector Store Initialization...")
    
    try:
        from app.services.component_matcher import VectorStoreManager
        
        # Create vector manager
        vector_manager = VectorStoreManager()
        print("✅ Vector store manager created")
        
        # Try to initialize
        try:
            await vector_manager.initialize()
            print("✅ Vector store initialized successfully!")
            return True
        except Exception as init_error:
            print(f"❌ Vector store initialization failed: {init_error}")
            return False
            
    except Exception as e:
        print(f"❌ Vector store test error: {e}")
        return False

async def main():
    """Test component matcher with real API key"""
    print("🚀 Testing Component Matcher with Real OpenAI API Key")
    print("=" * 60)
    
    # Test 1: Component matcher initialization
    matcher_result = await test_component_matcher_initialization()
    
    # Test 2: Vector store initialization
    vector_result = await test_vector_store_initialization()
    
    print("\n" + "=" * 60)
    print("📊 Results:")
    print(f"✅ Component Matcher: {'Ready' if matcher_result else 'Failed'}")
    print(f"✅ Vector Store: {'Ready' if vector_result else 'Failed'}")
    
    if matcher_result and vector_result:
        print("\n🎉 Component Matcher API is fully ready!")
        print("   You can now make authenticated requests to:")
        print("   POST /api/component-matcher/analyze")
    else:
        print("\n⚠️  Some components need attention:")
        if not matcher_result:
            print("   - Check OpenAI API key and quota")
        if not vector_result:
            print("   - Vector store needs proper initialization")

if __name__ == "__main__":
    asyncio.run(main())
