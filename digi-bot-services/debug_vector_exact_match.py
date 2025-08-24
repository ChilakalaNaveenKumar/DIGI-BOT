"""
Debug Vector Search for Exact Matching
Check what documents vector search returns for exact vs non-exact queries
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

# Test queries - exact matches vs similar patterns
TEST_QUERIES = [
    # These matched (exact entities in doc)
    "Instagram dominates with forty-five percent market share, TikTok thirty percent",
    "Marketing should get thirty-five percent, Development forty percent",
    
    # These didn't match (different entities)
    "Northern region forty-five percent, Southern thirty percent", 
    "Frontend team forty-five tasks, Backend thirty-eight tasks",
    "John eighty thousand salary, Sarah seventy thousand",
    
    # Simple direct queries
    "Instagram TikTok Facebook Twitter",
    "Marketing Development Operations Research",
    "North South East West regions",
    "Frontend Backend QA teams"
]

async def debug_vector_search_exact():
    """Debug vector search to see what it's actually finding"""
    
    print("🔍 Debugging Vector Search for Exact vs Pattern Matching")
    print("🎯 Check what documents are being retrieved")
    print("=" * 80)
    
    try:
        from app.services.component_matcher import VectorStoreManager
        
        # Initialize vector manager
        vector_manager = VectorStoreManager()
        await vector_manager.initialize()
        
        print(f"✅ Vector store initialized")
        print()
        
        for i, query in enumerate(TEST_QUERIES, 1):
            print(f"🔍 Query {i}: '{query[:60]}{'...' if len(query) > 60 else ''}'")
            print("-" * 60)
            
            # Get top candidates
            candidates = await vector_manager.query(query, top_k=3)
            
            print(f"📊 Top {len(candidates)} results:")
            for j, candidate in enumerate(candidates, 1):
                score = candidate.get('score', 0)
                text = candidate["text"][:150].replace('\n', ' ')
                
                print(f"   {j}. Score: {score:.3f}")
                print(f"      Text: {text}...")
                
                # Check for exact entity matches
                query_lower = query.lower()
                text_lower = text.lower()
                
                exact_matches = []
                if 'instagram' in query_lower and 'instagram' in text_lower:
                    exact_matches.append('Instagram')
                if 'tiktok' in query_lower and 'tiktok' in text_lower:
                    exact_matches.append('TikTok')
                if 'marketing' in query_lower and 'marketing' in text_lower:
                    exact_matches.append('Marketing')
                if 'development' in query_lower and 'development' in text_lower:
                    exact_matches.append('Development')
                
                if exact_matches:
                    print(f"      🎯 EXACT ENTITIES: {', '.join(exact_matches)}")
                else:
                    print(f"      ❓ No exact entity matches")
                
                print()
            
            print()
    
    except Exception as e:
        print(f"❌ Vector search debug failed: {e}")
        import traceback
        traceback.print_exc()

async def test_vector_similarity_scores():
    """Compare similarity scores for exact vs pattern queries"""
    
    print("📊 Vector Similarity Score Comparison")
    print("=" * 80)
    
    try:
        from app.services.component_matcher import VectorStoreManager
        
        vector_manager = VectorStoreManager()
        await vector_manager.initialize()
        
        # Exact match queries
        exact_queries = [
            "Instagram TikTok Facebook market share",
            "Marketing Development Operations budget"
        ]
        
        # Pattern match queries (different entities, same structure)
        pattern_queries = [
            "North South East West regional performance", 
            "Frontend Backend QA team productivity"
        ]
        
        print("🎯 EXACT ENTITY QUERIES:")
        for query in exact_queries:
            candidates = await vector_manager.query(query, top_k=1)
            if candidates:
                score = candidates[0].get('score', 0)
                print(f"   '{query}' → Score: {score:.3f}")
        
        print("\n🔄 PATTERN QUERIES (different entities):")
        for query in pattern_queries:
            candidates = await vector_manager.query(query, top_k=1)
            if candidates:
                score = candidates[0].get('score', 0)
                print(f"   '{query}' → Score: {score:.3f}")
        
        print("\n💡 Analysis:")
        print("   If exact entity queries get much higher scores,")
        print("   then vector search is biased toward exact matches")
        print("   rather than semantic pattern similarity.")
        
    except Exception as e:
        print(f"❌ Similarity test failed: {e}")

async def main():
    """Debug vector search exact matching behavior"""
    
    await debug_vector_search_exact()
    
    print("=" * 80)
    
    await test_vector_similarity_scores()
    
    print("\n" + "=" * 80)
    print("🎯 Key Questions:")
    print("1. Do exact entity queries get higher vector similarity scores?")
    print("2. Are pattern-based queries finding relevant chart documentation?")
    print("3. Is the AI only matching when it sees exact entities from examples?")
    print("4. Should we add more diverse examples to the documentation?")

if __name__ == "__main__":
    asyncio.run(main())

