"""
Text Extraction Examples - Extract and Save Only Text Content

This demonstrates the difference between:
1. VectorStoreSaver: Uploads entire files to OpenAI
2. TextVectorSaver: Extracts text and saves only text content

The TextVectorSaver is what you want - it processes files locally and saves only the extracted text.
"""

import asyncio
import os
import tempfile
import shutil
from typing import Dict, List, Any
from .text_vector_saver import TextVectorSaver
from .vector_store_saver import VectorStoreSaver
from .file_analyzer import FileAnalyzer


async def example_text_only_extraction():
    """Example: Extract text and save only text content (no original files)"""
    print("=== Text-Only Extraction Example ===")
    
    # Create test files
    temp_dir = tempfile.mkdtemp(prefix="text_extraction_")
    
    # Create sample document
    doc_path = os.path.join(temp_dir, "sample_document.txt")
    with open(doc_path, "w") as f:
        f.write("# Sample Document\n\n")
        f.write("This is a sample document for testing text extraction.\n")
        f.write("The TextVectorSaver will extract this content and save only the text.\n")
        f.write("The original file will NOT be uploaded to OpenAI.\n\n")
        f.write("## Key Benefits\n")
        f.write("- Privacy: Original files stay local\n")
        f.write("- Efficiency: Only text content is stored\n")
        f.write("- Cost: Smaller storage footprint\n")
    
    # Create JSON data file
    json_path = os.path.join(temp_dir, "data.json")
    with open(json_path, "w") as f:
        import json
        data = {
            "project": "Text Extraction Demo",
            "features": ["text extraction", "vector storage", "privacy"],
            "benefits": {
                "privacy": "Files stay local",
                "efficiency": "Only text stored",
                "cost": "Reduced storage"
            }
        }
        json.dump(data, f, indent=2)
    
    print(f"📁 Created test files in: {temp_dir}")
    
    # Initialize TextVectorSaver
    text_saver = TextVectorSaver()
    
    # Process first file
    print(f"\n📄 Processing document: {os.path.basename(doc_path)}")
    
    result = await text_saver.extract_and_save_text(
        doc_path,
        vector_store_name="Text Extraction Demo Store",
        expires_days=1,
        chunk_size=2000,
        include_metadata=True
    )
    
    if result["success"]:
        print(f"✅ Text extraction successful!")
        print(f"📊 Characters extracted: {result['characters']}")
        print(f"📝 Text chunks created: {result['chunks']}")
        print(f"🗂️  Vector store ID: {result['vector_store_id']}")
        print(f"🔗 File IDs: {result['file_ids']}")
    else:
        print(f"❌ Extraction failed: {result['error']}")
    
    # Process second file
    print(f"\n📄 Processing JSON: {os.path.basename(json_path)}")
    
    result2 = await text_saver.extract_and_save_text(
        json_path,
        vector_store_id=result.get("vector_store_id"),  # Reuse same store
        chunk_size=1000,
        include_metadata=True
    )
    
    if result2["success"]:
        print(f"✅ JSON extraction successful!")
        print(f"📊 Characters extracted: {result2['characters']}")
        print(f"📝 Text chunks created: {result2['chunks']}")
    else:
        print(f"❌ JSON extraction failed: {result2['error']}")
    
    # Show what was actually saved
    print(f"\n📋 Summary:")
    print(f"  🔒 Original files: Kept locally, NOT uploaded")
    print(f"  📝 Text content: Extracted and saved to vector store")
    print(f"  🗂️  Vector store: Contains only processed text")
    
    # Cleanup local files
    shutil.rmtree(temp_dir)
    print(f"🧹 Cleaned up local files")
    print(f"ℹ️  Vector store content remains (expires in 1 day)")


async def example_batch_text_extraction():
    """Example: Batch process multiple files, extract text only"""
    print("\n=== Batch Text Extraction Example ===")
    
    # Create multiple test files
    temp_dir = tempfile.mkdtemp(prefix="batch_text_")
    
    files_to_create = [
        ("readme.md", "# Project README\n\nThis is a markdown file.\n\n## Features\n- Text extraction\n- Batch processing"),
        ("config.json", '{"app": "demo", "version": "1.0", "settings": {"debug": true}}'),
        ("notes.txt", "Meeting Notes\n\n1. Implement text extraction\n2. Test batch processing\n3. Verify privacy"),
        ("code.py", "#!/usr/bin/env python3\ndef extract_text():\n    return 'Hello World'\n\nif __name__ == '__main__':\n    print(extract_text())")
    ]
    
    file_paths = []
    for filename, content in files_to_create:
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, "w") as f:
            f.write(content)
        file_paths.append(file_path)
    
    print(f"📁 Created {len(file_paths)} test files")
    
    # Batch process with TextVectorSaver
    text_saver = TextVectorSaver()
    
    batch_result = await text_saver.batch_extract_and_save(
        file_paths,
        vector_store_name="Batch Text Extraction Store",
        expires_days=1,
        chunk_size=1500
    )
    
    print(f"\n📊 Batch Processing Results:")
    print(f"  📄 Files processed: {batch_result['processed']}")
    print(f"  ✅ Successful: {batch_result['successful']}")
    print(f"  ❌ Failed: {batch_result['failed']}")
    print(f"  📝 Total characters: {batch_result['total_characters']:,}")
    print(f"  📋 Total chunks: {batch_result['total_chunks']}")
    print(f"  🗂️  Vector store: {batch_result['vector_store_id']}")
    
    # Show individual results
    print(f"\n📋 Individual File Results:")
    for result in batch_result['results']:
        status = "✅" if result['success'] else "❌"
        if result['success']:
            action = result.get('action', 'saved_text')
            chars = result.get('characters', 0)
            chunks = result.get('chunks', 0)
            print(f"  {status} {result['file']}: {action} ({chars} chars, {chunks} chunks)")
        else:
            print(f"  {status} {result['file']}: {result.get('error', 'Unknown error')}")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print(f"\n🧹 Cleaned up local files")


async def example_comparison_old_vs_new():
    """Example: Compare VectorStoreSaver (uploads files) vs TextVectorSaver (text only)"""
    print("\n=== Comparison: File Upload vs Text Extraction ===")
    
    # Create test file
    temp_dir = tempfile.mkdtemp(prefix="comparison_")
    test_file = os.path.join(temp_dir, "comparison_test.txt")
    
    with open(test_file, "w") as f:
        f.write("This is a test file for comparing approaches.\n")
        f.write("VectorStoreSaver: Uploads the entire file to OpenAI\n")
        f.write("TextVectorSaver: Extracts text and saves only text content\n")
        f.write("Choose TextVectorSaver for privacy and efficiency!")
    
    file_size = os.path.getsize(test_file)
    print(f"📄 Test file: {os.path.basename(test_file)} ({file_size} bytes)")
    
    # Method 1: VectorStoreSaver (uploads entire file)
    print(f"\n🔄 Method 1: VectorStoreSaver (uploads entire file)")
    
    try:
        old_saver = VectorStoreSaver()
        vs_id_old = await old_saver.upload_if_needed(
            test_file,
            vector_store_name="Old Method - File Upload Store",
            expires_days=1
        )
        print(f"  ✅ File uploaded to vector store: {vs_id_old}")
        print(f"  📁 What's stored: Entire original file ({file_size} bytes)")
        print(f"  🔒 Privacy: File content stored in OpenAI")
    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
    
    # Method 2: TextVectorSaver (extracts text only)
    print(f"\n🔄 Method 2: TextVectorSaver (extracts text only)")
    
    try:
        new_saver = TextVectorSaver()
        result = await new_saver.extract_and_save_text(
            test_file,
            vector_store_name="New Method - Text Only Store",
            expires_days=1,
            include_metadata=True
        )
        
        if result["success"]:
            print(f"  ✅ Text extracted and saved: {result['vector_store_id']}")
            print(f"  📝 What's stored: Only extracted text ({result['characters']} chars)")
            print(f"  🔒 Privacy: Original file stays local")
            print(f"  📋 Chunks: {result['chunks']}")
        else:
            print(f"  ❌ Extraction failed: {result['error']}")
    except Exception as e:
        print(f"  ❌ Text extraction failed: {e}")
    
    print(f"\n📊 Comparison Summary:")
    print(f"  📁 VectorStoreSaver: Uploads entire files (less private)")
    print(f"  📝 TextVectorSaver: Extracts and saves only text (more private)")
    print(f"  ✅ Recommended: Use TextVectorSaver for privacy and efficiency")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print(f"\n🧹 Cleaned up local files")


async def example_deduplication():
    """Example: Show how TextVectorSaver handles duplicate content"""
    print("\n=== Deduplication Example ===")
    
    # Create identical content in different files
    temp_dir = tempfile.mkdtemp(prefix="dedup_")
    
    content = "This is identical content that will be deduplicated.\nThe TextVectorSaver detects duplicate content by hash."
    
    file1 = os.path.join(temp_dir, "file1.txt")
    file2 = os.path.join(temp_dir, "file2.txt")
    
    with open(file1, "w") as f:
        f.write(content)
    
    with open(file2, "w") as f:
        f.write(content)  # Identical content
    
    print(f"📄 Created two files with identical content")
    
    text_saver = TextVectorSaver()
    
    # Process first file
    print(f"\n📄 Processing first file...")
    result1 = await text_saver.extract_and_save_text(
        file1,
        vector_store_name="Deduplication Test Store",
        expires_days=1
    )
    
    if result1["success"]:
        print(f"  ✅ First file processed: {result1['action']}")
        print(f"  🔗 Content hash: {result1['content_hash']}")
    
    # Process second file (should be deduplicated)
    print(f"\n📄 Processing second file (identical content)...")
    result2 = await text_saver.extract_and_save_text(
        file2,
        vector_store_id=result1.get("vector_store_id"),
        expires_days=1
    )
    
    if result2["success"]:
        print(f"  ✅ Second file processed: {result2['action']}")
        if result2['action'] == 'skipped_duplicate':
            print(f"  🎯 Deduplication working! Content not saved twice")
        else:
            print(f"  ⚠️  Content was saved again (deduplication may need improvement)")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print(f"\n🧹 Cleaned up local files")


async def example_chunking_large_content():
    """Example: Show how large content is split into chunks"""
    print("\n=== Large Content Chunking Example ===")
    
    # Create a large text file
    temp_dir = tempfile.mkdtemp(prefix="chunking_")
    large_file = os.path.join(temp_dir, "large_document.txt")
    
    # Generate large content
    content_parts = []
    for i in range(50):
        content_parts.append(f"Section {i+1}\n")
        content_parts.append(f"This is section {i+1} of a large document. " * 20)
        content_parts.append(f"\n\nThis section contains important information about topic {i+1}. " * 15)
        content_parts.append(f"\n\n")
    
    large_content = "".join(content_parts)
    
    with open(large_file, "w") as f:
        f.write(large_content)
    
    file_size = os.path.getsize(large_file)
    print(f"📄 Created large file: {file_size:,} bytes, {len(large_content):,} characters")
    
    # Process with different chunk sizes
    text_saver = TextVectorSaver()
    
    chunk_sizes = [1000, 2000, 4000]
    
    for chunk_size in chunk_sizes:
        print(f"\n📝 Processing with chunk size: {chunk_size:,} characters")
        
        result = await text_saver.extract_and_save_text(
            large_file,
            vector_store_name=f"Chunking Test Store {chunk_size}",
            expires_days=1,
            chunk_size=chunk_size,
            include_metadata=True
        )
        
        if result["success"]:
            print(f"  ✅ Success: {result['chunks']} chunks created")
            print(f"  📊 Average chunk size: {result['characters'] // result['chunks']:,} chars")
        else:
            print(f"  ❌ Failed: {result['error']}")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print(f"\n🧹 Cleaned up local files")


# Main example runner
async def run_text_extraction_examples():
    """Run all text extraction examples"""
    print("🚀 Starting Text Extraction Examples\n")
    print("📝 These examples show how to extract text from files")
    print("🔒 and save ONLY the text content (not the original files)\n")
    
    try:
        await example_text_only_extraction()
        await example_batch_text_extraction()
        await example_comparison_old_vs_new()
        await example_deduplication()
        await example_chunking_large_content()
        
        print("\n🎉 All text extraction examples completed!")
        print("\n📋 Key Takeaways:")
        print("  ✅ Use TextVectorSaver for privacy (files stay local)")
        print("  📝 Only extracted text is saved to vector store")
        print("  🔄 Automatic deduplication prevents duplicate content")
        print("  📊 Large content is intelligently chunked")
        print("  🗂️  Vector stores auto-expire to save costs")
        
    except Exception as e:
        print(f"\n❌ Text extraction examples failed: {e}")


if __name__ == "__main__":
    asyncio.run(run_text_extraction_examples())
