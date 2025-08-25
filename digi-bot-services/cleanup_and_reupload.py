#!/usr/bin/env python3
"""
Clean up old files and re-upload with consistent names
"""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

async def cleanup_and_reupload():
    """Delete old files and re-upload with consistent names"""
    
    print("🧹 Cleaning up and re-uploading files")
    print("=" * 50)
    
    try:
        client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # List all files
        print("📁 Listing current files...")
        files = await client.files.list()
        
        # Find our old files (with original names)
        old_files = []
        target_filenames = [
            "data_table_markdown_format_v1.md",
            "PositionAnchors.md", 
            "chartjs_markdown_format_v1.md",
            "Examples.md"
        ]
        
        for file in files.data:
            if file.filename in target_filenames:
                old_files.append(file)
        
        print(f"🗑️  Found {len(old_files)} old files to delete:")
        for file in old_files:
            print(f"   - {file.filename} (ID: {file.id})")
        
        # Delete old files
        for file in old_files:
            try:
                await client.files.delete(file_id=file.id)
                print(f"   ✅ Deleted: {file.filename}")
            except Exception as e:
                print(f"   ❌ Failed to delete {file.filename}: {e}")
        
        print(f"\n🔄 Re-uploading with consistent names...")
        
        # Now re-upload using our file manager
        from app.services.component_matcher.openai_file_manager import OpenAIFileStorageManager
        
        # Clear local metadata first
        metadata_file = "/Users/chilakalanaveenkumar/Digi Bot/digi-bot-services/app/services/component_matcher/documents/openai_files_metadata.json"
        if os.path.exists(metadata_file):
            os.remove(metadata_file)
            print("   🗑️  Cleared local metadata")
        
        # Initialize file manager (will re-upload)
        file_manager = OpenAIFileStorageManager()
        file_count = await file_manager.initialize()
        
        print(f"✅ Re-upload completed! Files: {file_count}")
        
        # Verify new files
        print(f"\n🔍 Verifying new files...")
        new_files = await client.files.list()
        
        digi_setu_files = []
        for file in new_files.data:
            if file.filename and file.filename.startswith("digi_setu_"):
                digi_setu_files.append(file)
        
        print(f"✅ Found {len(digi_setu_files)} files with consistent names:")
        for file in digi_setu_files:
            print(f"   - {file.filename} (ID: {file.id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run cleanup and re-upload"""
    
    success = await cleanup_and_reupload()
    
    if success:
        print("\n🎉 Cleanup and re-upload successful!")
        print("   Files now have consistent naming in OpenAI storage")
    else:
        print("\n❌ Cleanup failed!")

if __name__ == "__main__":
    asyncio.run(main())
