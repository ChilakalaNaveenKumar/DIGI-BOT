"""
Test file management - no duplicates
"""
import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append('/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services')

from app.services.chart_matcher import VectorStoreManager

async def test_file_management():
    """Test the improved file management"""
    
    print("🗂️  Testing File Management")
    print("=" * 40)
    
    vector_manager = VectorStoreManager()
    await vector_manager.initialize()
    
    # Test 1: List current files
    print("📋 Current files in vector store:")
    files = await vector_manager.list_files()
    for i, f in enumerate(files, 1):
        print(f"   {i}. {f['filename']} (ID: {f['id'][:20]}...)")
    
    print(f"\n📊 Total files: {len(files)}")
    
    # Test 2: Try to ensure files exist (should skip if already there)
    print("\n🔍 Testing ensure_file_exists (should skip duplicates):")
    
    chartjs_path = "/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services/app/services/chart_matcher/documents/chartjs_markdown_format_v1.md"
    datatable_path = "/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services/app/services/chart_matcher/documents/data_table_markdown_format_v1.md"
    
    chartjs_id = await vector_manager.ensure_file_exists(chartjs_path, "chartjs_markdown_format_v1.md")
    datatable_id = await vector_manager.ensure_file_exists(datatable_path, "data_table_markdown_format_v1.md")
    
    # Test 3: List files again (should be same count)
    print("\n📋 Files after ensure_file_exists:")
    files_after = await vector_manager.list_files()
    for i, f in enumerate(files_after, 1):
        print(f"   {i}. {f['filename']} (ID: {f['id'][:20]}...)")
    
    print(f"\n📊 Total files after: {len(files_after)}")
    
    if len(files) == len(files_after):
        print("✅ SUCCESS: No duplicates created!")
    else:
        print("❌ ISSUE: File count changed")
    
    # Test 4: Force update example (commented out to avoid actual update)
    print("\n💡 To force update a file, use:")
    print("   await vector_manager.insert_or_update_file(path, filename, force=True)")

if __name__ == "__main__":
    asyncio.run(test_file_management())

