#!/usr/bin/env python3
"""
Test File Processing Examples

Simple test script to demonstrate file processing functionality.
Run this to see the FileAnalyzer and VectorStoreSaver in action.
"""

import asyncio
import sys
import os
import tempfile
import shutil

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.file_processing.examples import run_file_processing_examples


async def simple_file_analysis_test():
    """Simple test of file analysis functionality"""
    print("🧪 Simple File Analysis Test\n")
    
    try:
        from app.services.file_processing import FileAnalyzer, AnalyzeLimits
        
        # Create temporary test files
        temp_dir = tempfile.mkdtemp(prefix="file_test_")
        print(f"📁 Created test directory: {temp_dir}")
        
        # Create test files
        test_files = {}
        
        # Text file
        txt_file = os.path.join(temp_dir, "test.txt")
        with open(txt_file, "w") as f:
            f.write("This is a test text file.\nIt has multiple lines.\nFileAnalyzer should extract this content.")
        test_files["txt"] = txt_file
        
        # JSON file
        json_file = os.path.join(temp_dir, "test.json")
        with open(json_file, "w") as f:
            import json
            data = {"name": "Test", "version": 1.0, "features": ["analysis", "extraction"]}
            json.dump(data, f, indent=2)
        test_files["json"] = json_file
        
        # CSV file
        csv_file = os.path.join(temp_dir, "test.csv")
        with open(csv_file, "w") as f:
            f.write("Name,Age,City\n")
            f.write("John,30,New York\n")
            f.write("Jane,25,Los Angeles\n")
        test_files["csv"] = csv_file
        
        # Python file
        py_file = os.path.join(temp_dir, "test.py")
        with open(py_file, "w") as f:
            f.write("#!/usr/bin/env python3\n")
            f.write("def hello():\n")
            f.write("    print('Hello from test file!')\n")
        test_files["py"] = py_file
        
        # Initialize analyzer
        analyzer = FileAnalyzer()
        print("✅ FileAnalyzer initialized")
        
        # Test each file
        print(f"\n🔍 Testing {len(test_files)} file types:")
        
        for file_type, file_path in test_files.items():
            print(f"\n📄 Analyzing {file_type.upper()} file:")
            
            result = analyzer.analyze_path(file_path)
            
            if result.ok:
                print(f"  ✅ Success!")
                print(f"  📊 Size: {result.meta['bytes']} bytes")
                print(f"  📝 Text length: {len(result.text)} chars")
                print(f"  📋 Preview: {result.text[:100]}...")
                
                if result.warning:
                    print(f"  ⚠️  Warning: {result.warning}")
            else:
                print(f"  ❌ Failed: {result.error}")
        
        # Test unsupported file type
        print(f"\n🚫 Testing unsupported file type:")
        unsupported_file = os.path.join(temp_dir, "test.xyz")
        with open(unsupported_file, "w") as f:
            f.write("Unsupported file content")
        
        result = analyzer.analyze_path(unsupported_file)
        if result.ok:
            print(f"  ❌ Unexpectedly succeeded")
        else:
            print(f"  ✅ Correctly rejected: {result.error}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up test directory")
        print(f"✅ Simple file analysis test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and have the required dependencies")
    except Exception as e:
        print(f"❌ Test failed: {e}")


async def test_custom_limits():
    """Test custom file processing limits"""
    print("\n🚫 Testing Custom Limits")
    
    try:
        from app.services.file_processing import FileAnalyzer, AnalyzeLimits
        
        # Create analyzer with very small limits
        small_limits = AnalyzeLimits(
            max_bytes=100,  # Only 100 bytes
            max_pdf_pages=1,
            ocr_enabled=False
        )
        
        analyzer = FileAnalyzer(limits=small_limits)
        
        # Create a file that exceeds the limit
        temp_dir = tempfile.mkdtemp(prefix="limits_test_")
        large_file = os.path.join(temp_dir, "large.txt")
        
        with open(large_file, "w") as f:
            f.write("This is a test file that is designed to exceed the 100 byte limit we set for testing purposes.")
        
        file_size = os.path.getsize(large_file)
        print(f"📄 Created file: {file_size} bytes (limit: {small_limits.max_bytes} bytes)")
        
        result = analyzer.analyze_path(large_file)
        
        if result.ok:
            print(f"❌ File should have been rejected but was processed")
        else:
            print(f"✅ File correctly rejected: {result.error}")
        
        # Test with normal limits
        normal_analyzer = FileAnalyzer()  # Default limits
        result = normal_analyzer.analyze_path(large_file)
        
        if result.ok:
            print(f"✅ Same file processed with normal limits: {len(result.text)} chars")
        else:
            print(f"❌ File failed with normal limits: {result.error}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up test files")
        
    except Exception as e:
        print(f"❌ Custom limits test failed: {e}")


async def test_vector_store_basic():
    """Test basic vector store functionality"""
    print("\n📤 Testing Vector Store Basic Operations")
    
    try:
        from app.services.file_processing import VectorStoreSaver
        
        # Create a test file
        temp_dir = tempfile.mkdtemp(prefix="vector_test_")
        test_file = os.path.join(temp_dir, "vector_test.txt")
        
        with open(test_file, "w") as f:
            f.write("This is a test file for vector store operations.\n")
            f.write("It contains sample content for testing upload functionality.")
        
        print(f"📄 Created test file: {os.path.basename(test_file)}")
        
        # Initialize vector store saver
        saver = VectorStoreSaver()
        print("✅ VectorStoreSaver initialized")
        
        # Upload file
        print("📤 Uploading file to vector store...")
        
        vector_store_id = await saver.upload_if_needed(
            test_file,
            vector_store_name="File Processing Test Store",
            expires_days=1,  # Short expiry for testing
            validate_with_analyzer=True
        )
        
        print(f"✅ Upload successful!")
        print(f"🗂️  Vector store ID: {vector_store_id}")
        
        # Try uploading the same file again (should skip)
        print("🔄 Testing duplicate detection...")
        
        vector_store_id_2 = await saver.upload_if_needed(
            test_file,
            vector_store_name="File Processing Test Store",
            expires_days=1
        )
        
        if vector_store_id == vector_store_id_2:
            print("✅ Duplicate detection working (same vector store ID)")
        else:
            print("⚠️  Got different vector store ID (may be expected)")
        
        # Cleanup local files
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up local test files")
        print(f"ℹ️  Vector store files remain in OpenAI (will expire in 1 day)")
        
    except Exception as e:
        print(f"❌ Vector store test failed: {e}")
        print("Make sure OPENAI_API_KEY is set in your environment")


async def test_supported_extensions():
    """Test supported file extensions"""
    print("\n📋 Testing Supported Extensions")
    
    try:
        from app.services.file_processing import FileAnalyzer
        from app.services.file_processing.file_analyzer import SUPPORTED_EXTS, TEXT_EXTS
        
        print(f"📊 Total supported extensions: {len(SUPPORTED_EXTS)}")
        print(f"📝 Text-based extensions: {len(TEXT_EXTS)}")
        
        # Show categories
        categories = {
            "Text": [".txt", ".md", ".log"],
            "Data": [".csv", ".tsv", ".json"],
            "Documents": [".pdf", ".docx", ".pptx", ".xlsx"],
            "Code": [".py", ".js", ".ts", ".html", ".css"],
            "Images": [".png", ".jpg", ".jpeg", ".webp"]
        }
        
        for category, examples in categories.items():
            supported = [ext for ext in examples if ext in SUPPORTED_EXTS]
            print(f"\n📂 {category}: {len(supported)} supported")
            for ext in supported[:3]:  # Show first 3
                print(f"  ✅ {ext}")
            if len(supported) > 3:
                print(f"  ... and {len(supported) - 3} more")
        
        # Test file extension checking
        analyzer = FileAnalyzer()
        
        temp_dir = tempfile.mkdtemp(prefix="ext_test_")
        
        # Test supported extension
        supported_file = os.path.join(temp_dir, "test.txt")
        with open(supported_file, "w") as f:
            f.write("Supported file content")
        
        result = analyzer.analyze_path(supported_file)
        print(f"\n✅ Supported file (.txt): {'Success' if result.ok else 'Failed'}")
        
        # Test unsupported extension
        unsupported_file = os.path.join(temp_dir, "test.unknown")
        with open(unsupported_file, "w") as f:
            f.write("Unsupported file content")
        
        result = analyzer.analyze_path(unsupported_file)
        print(f"❌ Unsupported file (.unknown): {'Rejected' if not result.ok else 'Unexpectedly accepted'}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"❌ Extension test failed: {e}")


async def test_integration_workflow():
    """Test complete integration workflow"""
    print("\n🔄 Testing Integration Workflow")
    
    try:
        from app.services.file_processing import FileAnalyzer, VectorStoreSaver
        
        # Create test files
        temp_dir = tempfile.mkdtemp(prefix="integration_test_")
        
        files_to_process = []
        
        # Create different file types
        file_configs = [
            ("document.txt", "This is a sample document for integration testing."),
            ("data.json", '{"test": true, "integration": "workflow", "files": 3}'),
            ("info.md", "# Integration Test\n\nThis is a **markdown** file for testing.")
        ]
        
        for filename, content in file_configs:
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, "w") as f:
                f.write(content)
            files_to_process.append(file_path)
        
        print(f"📁 Created {len(files_to_process)} test files")
        
        # Initialize services
        analyzer = FileAnalyzer()
        saver = VectorStoreSaver()
        
        # Process each file through complete workflow
        results = []
        
        for file_path in files_to_process:
            filename = os.path.basename(file_path)
            print(f"\n📄 Processing: {filename}")
            
            # Step 1: Analyze
            print("  🔍 Analyzing...")
            result = analyzer.analyze_path(file_path)
            
            if not result.ok:
                print(f"  ❌ Analysis failed: {result.error}")
                results.append({"file": filename, "step": "analysis", "success": False})
                continue
            
            print(f"  ✅ Extracted {len(result.text)} characters")
            
            # Step 2: Upload to vector store
            print("  📤 Uploading...")
            
            try:
                vector_store_id = await saver.upload_if_needed(
                    file_path,
                    vector_store_name="Integration Test Store",
                    expires_days=1,
                    validate_with_analyzer=True
                )
                
                print(f"  ✅ Uploaded to: {vector_store_id[:8]}...")
                results.append({
                    "file": filename,
                    "success": True,
                    "text_length": len(result.text),
                    "vector_store_id": vector_store_id
                })
                
            except Exception as e:
                print(f"  ❌ Upload failed: {e}")
                results.append({"file": filename, "step": "upload", "success": False})
        
        # Summary
        successful = sum(1 for r in results if r.get("success"))
        print(f"\n📊 Integration Summary:")
        print(f"  ✅ Successfully processed: {successful}/{len(files_to_process)}")
        
        if successful > 0:
            total_chars = sum(r.get("text_length", 0) for r in results if r.get("success"))
            print(f"  📝 Total characters processed: {total_chars}")
        
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up local files")
        
    except Exception as e:
        print(f"❌ Integration workflow test failed: {e}")


async def cleanup_test_resources():
    """Clean up any test resources"""
    print("\n🧹 Cleanup Test Resources")
    
    # Remove any temporary directories that might be left over
    import glob
    temp_dirs = glob.glob("/tmp/file_test_*") + glob.glob("/tmp/limits_test_*") + glob.glob("/tmp/vector_test_*") + glob.glob("/tmp/ext_test_*") + glob.glob("/tmp/integration_test_*")
    
    cleaned = 0
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                cleaned += 1
                print(f"  🗑️  Removed: {temp_dir}")
            except Exception as e:
                print(f"  ❌ Failed to remove {temp_dir}: {e}")
    
    if cleaned > 0:
        print(f"✅ Cleaned up {cleaned} temporary directories")
    else:
        print("ℹ️  No temporary directories to clean up")


async def main():
    """Main test runner"""
    print("🚀 File Processing Test Suite\n")
    
    # Choose test mode
    print("Select test mode:")
    print("1. Simple analysis test (basic functionality)")
    print("2. Custom limits test")
    print("3. Vector store test (requires OPENAI_API_KEY)")
    print("4. Supported extensions test")
    print("5. Integration workflow test")
    print("6. Full examples (comprehensive)")
    print("7. All tests")
    print("8. Cleanup test resources")
    
    try:
        choice = input("\nEnter choice (1-8, default=1): ").strip() or "1"
        
        if choice == "1":
            await simple_file_analysis_test()
        elif choice == "2":
            await test_custom_limits()
        elif choice == "3":
            await test_vector_store_basic()
        elif choice == "4":
            await test_supported_extensions()
        elif choice == "5":
            await test_integration_workflow()
        elif choice == "6":
            await run_file_processing_examples()
        elif choice == "7":
            await simple_file_analysis_test()
            await test_custom_limits()
            await test_vector_store_basic()
            await test_supported_extensions()
            await test_integration_workflow()
        elif choice == "8":
            await cleanup_test_resources()
        else:
            print("Invalid choice, running simple test...")
            await simple_file_analysis_test()
            
        # Ask about cleanup
        if choice not in ["8"]:
            cleanup = input("\nCleanup test resources? (y/N): ").strip().lower()
            if cleanup in ["y", "yes"]:
                await cleanup_test_resources()
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
