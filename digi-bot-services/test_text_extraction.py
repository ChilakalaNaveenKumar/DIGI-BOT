#!/usr/bin/env python3
"""
Test Text Extraction - Extract and Save Only Text Content

This demonstrates the TextVectorSaver which extracts text from files
and saves ONLY the text content to vector store (not the original files).
"""

import asyncio
import sys
import os
import tempfile
import shutil

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


async def simple_text_extraction_test():
    """Simple test showing text-only extraction"""
    print("🧪 Simple Text Extraction Test\n")
    
    try:
        from app.services.file_processing import TextVectorSaver
        
        # Create a test file
        temp_dir = tempfile.mkdtemp(prefix="text_extract_test_")
        test_file = os.path.join(temp_dir, "sample.txt")
        
        with open(test_file, "w") as f:
            f.write("# Sample Document\n\n")
            f.write("This is a test document for text extraction.\n")
            f.write("The TextVectorSaver will extract this content.\n")
            f.write("The original file will NOT be uploaded to OpenAI.\n")
            f.write("Only the extracted text will be saved to the vector store.\n\n")
            f.write("Benefits:\n")
            f.write("- Privacy: Original files stay local\n")
            f.write("- Efficiency: Only text content stored\n")
            f.write("- Cost: Reduced storage footprint\n")
        
        file_size = os.path.getsize(test_file)
        print(f"📄 Created test file: {os.path.basename(test_file)} ({file_size} bytes)")
        
        # Initialize TextVectorSaver
        text_saver = TextVectorSaver()
        print("✅ TextVectorSaver initialized")
        
        # Extract text and save to vector store
        print(f"\n🔍 Extracting text from file...")
        
        result = await text_saver.extract_and_save_text(
            test_file,
            vector_store_name="Text Extraction Test Store",
            expires_days=1,
            chunk_size=2000,
            include_metadata=True
        )
        
        if result["success"]:
            print(f"✅ Text extraction successful!")
            print(f"📊 Characters extracted: {result['characters']:,}")
            print(f"📝 Text chunks created: {result['chunks']}")
            print(f"🗂️  Vector store ID: {result['vector_store_id']}")
            print(f"🔗 Saved file IDs: {len(result['file_ids'])} text files")
            print(f"🔒 Original file: Kept locally (NOT uploaded)")
            
            # Show what action was taken
            action = result.get('action', 'unknown')
            if action == 'saved_text':
                print(f"✅ Action: New text content saved")
            elif action == 'skipped_duplicate':
                print(f"ℹ️  Action: Duplicate content detected, skipped")
            
        else:
            print(f"❌ Text extraction failed: {result['error']}")
        
        # Try processing the same file again (should detect duplicate)
        print(f"\n🔄 Testing duplicate detection...")
        
        result2 = await text_saver.extract_and_save_text(
            test_file,
            vector_store_id=result.get("vector_store_id"),
            expires_days=1
        )
        
        if result2["success"]:
            action = result2.get('action', 'unknown')
            if action == 'skipped_duplicate':
                print(f"✅ Duplicate detection working! Content not saved twice")
            else:
                print(f"ℹ️  Content processed again: {action}")
        
        # Cleanup local files
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up local test file")
        print(f"ℹ️  Vector store content remains in OpenAI (expires in 1 day)")
        
        print(f"\n✅ Text extraction test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and have the required dependencies")
    except Exception as e:
        print(f"❌ Test failed: {e}")


async def comparison_test():
    """Compare file upload vs text extraction approaches"""
    print("\n🔄 Comparison Test: File Upload vs Text Extraction")
    
    try:
        from app.services.file_processing import VectorStoreSaver, TextVectorSaver
        
        # Create test file
        temp_dir = tempfile.mkdtemp(prefix="comparison_test_")
        test_file = os.path.join(temp_dir, "comparison.txt")
        
        with open(test_file, "w") as f:
            f.write("Comparison Test Document\n\n")
            f.write("This file demonstrates the difference between:\n")
            f.write("1. VectorStoreSaver: Uploads entire file to OpenAI\n")
            f.write("2. TextVectorSaver: Extracts text, saves only text content\n\n")
            f.write("For privacy and efficiency, use TextVectorSaver!")
        
        file_size = os.path.getsize(test_file)
        print(f"📄 Test file: {file_size} bytes")
        
        # Method 1: VectorStoreSaver (uploads entire file)
        print(f"\n📁 Method 1: VectorStoreSaver (uploads entire file)")
        try:
            file_saver = VectorStoreSaver()
            vs_id1 = await file_saver.upload_if_needed(
                test_file,
                vector_store_name="File Upload Test Store",
                expires_days=1
            )
            print(f"  ✅ Entire file uploaded: {vs_id1}")
            print(f"  📁 What's stored: Complete original file ({file_size} bytes)")
            print(f"  🔒 Privacy: File content stored in OpenAI")
        except Exception as e:
            print(f"  ❌ File upload failed: {e}")
        
        # Method 2: TextVectorSaver (extracts text only)
        print(f"\n📝 Method 2: TextVectorSaver (extracts text only)")
        try:
            text_saver = TextVectorSaver()
            result = await text_saver.extract_and_save_text(
                test_file,
                vector_store_name="Text Extraction Test Store",
                expires_days=1
            )
            
            if result["success"]:
                print(f"  ✅ Text extracted and saved: {result['vector_store_id']}")
                print(f"  📝 What's stored: Only text content ({result['characters']} chars)")
                print(f"  🔒 Privacy: Original file stays local")
                print(f"  📋 Chunks: {result['chunks']}")
            else:
                print(f"  ❌ Text extraction failed: {result['error']}")
        except Exception as e:
            print(f"  ❌ Text extraction failed: {e}")
        
        print(f"\n📊 Recommendation:")
        print(f"  ✅ Use TextVectorSaver for better privacy and efficiency")
        print(f"  🔒 Your files stay on your system")
        print(f"  📝 Only processed text goes to vector store")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up local files")
        
    except Exception as e:
        print(f"❌ Comparison test failed: {e}")


async def batch_extraction_test():
    """Test batch processing of multiple files"""
    print("\n📦 Batch Text Extraction Test")
    
    try:
        from app.services.file_processing import TextVectorSaver
        
        # Create multiple test files
        temp_dir = tempfile.mkdtemp(prefix="batch_test_")
        
        files_data = [
            ("readme.md", "# Project README\n\nThis is a markdown file.\n\n## Features\n- Text extraction\n- Privacy protection"),
            ("config.json", '{"app": "test", "version": "1.0", "features": ["extraction", "privacy"]}'),
            ("notes.txt", "Meeting Notes\n\n1. Extract text only\n2. Keep files local\n3. Save to vector store")
        ]
        
        file_paths = []
        for filename, content in files_data:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, "w") as f:
                f.write(content)
            file_paths.append(file_path)
        
        print(f"📁 Created {len(file_paths)} test files")
        
        # Batch process
        text_saver = TextVectorSaver()
        
        result = await text_saver.batch_extract_and_save(
            file_paths,
            vector_store_name="Batch Test Store",
            expires_days=1
        )
        
        print(f"\n📊 Batch Results:")
        print(f"  📄 Files processed: {result['processed']}")
        print(f"  ✅ Successful: {result['successful']}")
        print(f"  ❌ Failed: {result['failed']}")
        print(f"  📝 Total characters: {result['total_characters']:,}")
        print(f"  📋 Total chunks: {result['total_chunks']}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up local files")
        print(f"✅ Batch extraction test completed!")
        
    except Exception as e:
        print(f"❌ Batch test failed: {e}")


async def main():
    """Main test runner"""
    print("🚀 Text Extraction Test Suite\n")
    print("📝 This demonstrates extracting text from files")
    print("🔒 and saving ONLY the text content (not original files)\n")
    
    # Choose test mode
    print("Select test mode:")
    print("1. Simple text extraction test")
    print("2. Comparison test (file upload vs text extraction)")
    print("3. Batch extraction test")
    print("4. All tests")
    
    try:
        choice = input("\nEnter choice (1-4, default=1): ").strip() or "1"
        
        if choice == "1":
            await simple_text_extraction_test()
        elif choice == "2":
            await comparison_test()
        elif choice == "3":
            await batch_extraction_test()
        elif choice == "4":
            await simple_text_extraction_test()
            await comparison_test()
            await batch_extraction_test()
        else:
            print("Invalid choice, running simple test...")
            await simple_text_extraction_test()
        
        print(f"\n🎉 Test completed!")
        print(f"\n📋 Key Points:")
        print(f"  ✅ TextVectorSaver extracts text and saves only text content")
        print(f"  🔒 Original files stay on your local system")
        print(f"  📝 Vector store contains only processed text")
        print(f"  🔄 Automatic deduplication prevents duplicate content")
        print(f"  💰 More cost-effective (smaller storage footprint)")
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
