"""
Debug vector search - check if it's finding the right documents
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

PROBLEM_QUERIES = [
    "Team productivity: Frontend: 45 tasks, Backend: 38 tasks, QA: 29 tasks",
    "Employee records: John (Manager, $80k), Sarah (Developer, $70k), Mike (Designer, $65k)",
    "Inventory: Laptops: 45 units, Monitors: 23 units, Keyboards: 67 units"
]

async def debug_vector_search():
    """Check what documents the vector search is finding"""
    
    print("🔍 Debugging Vector Search Results")
    print("🎯 Check if chartjs_markdown_format_v1.md is being found")
    print("=" * 70)
    
    try:
        from app.services.component_matcher import VectorStoreManager
        
        # Initialize vector manager
        vector_manager = VectorStoreManager()
        await vector_manager.initialize()
        
        print(f"✅ Vector store initialized with documents")
        print()
        
        for i, query in enumerate(PROBLEM_QUERIES, 1):
            print(f"🔍 Query {i}: '{query[:50]}...'")
            print("-" * 50)
            
            # Get top candidates
            candidates = await vector_manager.query(query, top_k=5)
            
            print(f"📊 Found {len(candidates)} candidates:")
            for j, candidate in enumerate(candidates, 1):
                text_preview = candidate["text"][:100].replace('\n', ' ')
                print(f"   {j}. Score: {candidate.get('score', 'N/A'):.3f}")
                print(f"      Text: {text_preview}...")
                
                # Check if it's from the chartjs document
                if 'chart' in candidate["text"].lower() or 'bar-chart' in candidate["text"].lower():
                    print(f"      🎯 Contains chart content!")
                print()
            
            print()
    
    except Exception as e:
        print(f"❌ Vector search debug failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Debug vector search for problem queries"""
    
    await debug_vector_search()
    
    print("=" * 70)
    print("🎯 Analysis:")
    print("If chartjs_markdown_format_v1.md is NOT in top results:")
    print("1. Vector embeddings might not capture the semantic similarity")
    print("2. Query terms don't match document content well")
    print("3. Other documents are scoring higher")
    print()
    print("The document clearly covers:")
    print("📊 'Category Comparisons → Bar Chart'")
    print("📋 'Data with label/value pairs'")
    print("🎯 These queries should match!")

if __name__ == "__main__":
    asyncio.run(main())

