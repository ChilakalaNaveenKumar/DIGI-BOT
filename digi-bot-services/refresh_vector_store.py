"""
Refresh Vector Store with Updated Documentation
Forces reload of all documents including the new pattern examples
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

async def refresh_vector_store():
    """Clear and reload the vector store with updated documentation"""
    
    print("🔄 Refreshing Vector Store with Updated Documentation")
    print("=" * 60)
    
    try:
        from app.services.component_matcher import VectorStoreManager
        
        # Create vector manager
        vector_manager = VectorStoreManager()
        
        print("🗑️  Clearing existing vector store...")
        vector_manager.clear_all_docs()
        
        print("📚 Reloading documents with new pattern examples...")
        doc_count = await vector_manager.initialize()
        
        print(f"✅ Vector store refreshed with {doc_count} documents")
        
        # Test a query to make sure it works
        print("\n🧪 Testing updated vector store...")
        test_query = "Frontend team: 45 tasks, Backend: 38 tasks, QA: 29 tasks"
        candidates = await vector_manager.query(test_query, top_k=3)
        
        print(f"📊 Test query results:")
        for i, candidate in enumerate(candidates, 1):
            score = candidate.get('score', 0)
            text_preview = candidate["text"][:100].replace('\n', ' ')
            print(f"   {i}. Score: {score:.3f}")
            print(f"      Text: {text_preview}...")
            
            # Check if it found the new pattern examples
            if 'frontend' in candidate["text"].lower() or 'team' in candidate["text"].lower():
                print(f"      🎯 Found new pattern example!")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Vector store refresh failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Refresh vector store and test"""
    
    success = await refresh_vector_store()
    
    if success:
        print("✅ Vector store successfully refreshed!")
        print("   The component matcher should now recognize the new patterns.")
    else:
        print("❌ Vector store refresh failed!")

if __name__ == "__main__":
    asyncio.run(main())

