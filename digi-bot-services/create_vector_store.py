#!/usr/bin/env python3
"""
Create OpenAI Vector Store with consistent ID and upload documents
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def create_vector_store():
    """Create OpenAI Vector Store and upload documents"""
    
    print("🚀 Creating OpenAI Vector Store")
    print("=" * 50)
    
    try:
        from app.services.component_matcher.openai_vector_store_http import OpenAIVectorStoreManager
        
        # Initialize vector store manager
        vector_manager = OpenAIVectorStoreManager()
        
        print("🔧 Creating vector store and uploading documents...")
        file_count = await vector_manager.initialize()
        
        print(f"✅ Vector store creation completed!")
        print(f"   Files uploaded: {file_count}")
        
        # Get detailed stats
        stats = await vector_manager.get_stats()
        print(f"\n📊 Vector Store Details:")
        print(f"   Vector Store ID: {stats.get('vector_store_id', 'N/A')}")
        print(f"   Name: {stats.get('vector_store_name', 'N/A')}")
        print(f"   Status: {stats.get('status', 'N/A')}")
        print(f"   Storage Type: {stats.get('storage_type', 'N/A')}")
        print(f"   Total Files: {len(stats.get('files', []))}")
        print(f"   Total Size: {stats.get('total_bytes', 0):,} bytes")
        
        if stats.get('file_counts'):
            print(f"   File Counts: {stats['file_counts']}")
        
        if stats.get('files'):
            print(f"\n📁 Uploaded Files:")
            for filename in stats['files']:
                print(f"     - {filename}")
        
        if stats.get('file_details'):
            print(f"\n📄 File Details:")
            for file in stats['file_details']:
                print(f"     - {file['filename']}")
                print(f"       ID: {file['id']}")
                print(f"       Size: {file['bytes']:,} bytes")
                print(f"       Status: {file['status']}")
                print()
        
        print("\n🎯 Vector Store Benefits:")
        print("   ✅ Persistent cloud storage")
        print("   ✅ Consistent vector store ID")
        print("   ✅ Automatic embeddings and indexing")
        print("   ✅ Optimized for semantic search")
        print("   ✅ Integrated with OpenAI Assistants API")
        
        # Test query capability
        print("\n🧪 Testing vector store query...")
        results = await vector_manager.query("chart examples with data", top_k=3)
        print(f"   Query results: {len(results)} matches found")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector store creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run vector store creation"""
    
    success = await create_vector_store()
    
    if success:
        print("\n🎉 Vector Store Creation Successful!")
        print("   Your documents are now stored in OpenAI's Vector Store")
        print("   The vector store ID is saved locally for consistency")
        print("   You can now use semantic search with the component matcher")
    else:
        print("\n❌ Vector Store Creation Failed!")
        print("   Check your OpenAI API key and try again")

if __name__ == "__main__":
    asyncio.run(main())
