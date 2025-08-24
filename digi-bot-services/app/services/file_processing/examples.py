"""
Usage examples for File Processing service.

These examples demonstrate how to use FileAnalyzer and VectorStoreSaver
for document analysis and vector store management.
"""

import asyncio
import os
import tempfile
from typing import Dict, List, Any
from .file_analyzer import FileAnalyzer, AnalyzeLimits, AnalyzeResult
from .vector_store_saver import VectorStoreSaver


class FileProcessingExamples:
    """Examples and utilities for File Processing service"""
    
    def __init__(self):
        self.analyzer = FileAnalyzer()
        self.vector_saver = VectorStoreSaver()
    
    def create_test_files(self) -> Dict[str, str]:
        """Create temporary test files for examples"""
        test_files = {}
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="file_processing_test_")
        
        # Text file
        txt_path = os.path.join(temp_dir, "sample.txt")
        with open(txt_path, "w") as f:
            f.write("This is a sample text file for testing file processing capabilities.\n")
            f.write("It contains multiple lines of text content.\n")
            f.write("The FileAnalyzer should extract this text successfully.")
        test_files["txt"] = txt_path
        
        # JSON file
        json_path = os.path.join(temp_dir, "sample.json")
        with open(json_path, "w") as f:
            import json
            data = {
                "name": "File Processing Test",
                "version": "1.0",
                "features": ["text extraction", "vector storage", "document analysis"],
                "config": {
                    "max_size": "25MB",
                    "supported_formats": ["txt", "pdf", "docx", "xlsx"]
                }
            }
            json.dump(data, f, indent=2)
        test_files["json"] = json_path
        
        # CSV file
        csv_path = os.path.join(temp_dir, "sample.csv")
        with open(csv_path, "w") as f:
            f.write("Name,Age,Department,Salary\n")
            f.write("John Doe,30,Engineering,75000\n")
            f.write("Jane Smith,28,Marketing,65000\n")
            f.write("Bob Johnson,35,Sales,70000\n")
        test_files["csv"] = csv_path
        
        # Python file
        py_path = os.path.join(temp_dir, "sample.py")
        with open(py_path, "w") as f:
            f.write("#!/usr/bin/env python3\n")
            f.write('"""Sample Python file for testing"""\n\n')
            f.write("def hello_world():\n")
            f.write('    print("Hello, World!")\n\n')
            f.write("if __name__ == '__main__':\n")
            f.write("    hello_world()\n")
        test_files["py"] = py_path
        
        # Markdown file
        md_path = os.path.join(temp_dir, "sample.md")
        with open(md_path, "w") as f:
            f.write("# File Processing Test\n\n")
            f.write("This is a **markdown** file for testing.\n\n")
            f.write("## Features\n\n")
            f.write("- Text extraction\n")
            f.write("- Document analysis\n")
            f.write("- Vector store management\n\n")
            f.write("```python\n")
            f.write("# Code example\n")
            f.write("analyzer = FileAnalyzer()\n")
            f.write("result = analyzer.analyze_path('file.md')\n")
            f.write("```\n")
        test_files["md"] = md_path
        
        return test_files


async def example_basic_file_analysis():
    """Example: Basic file analysis with different file types"""
    print("=== Basic File Analysis Example ===")
    
    examples = FileProcessingExamples()
    test_files = examples.create_test_files()
    
    analyzer = FileAnalyzer()
    
    for file_type, file_path in test_files.items():
        print(f"\n📄 Analyzing {file_type.upper()} file: {os.path.basename(file_path)}")
        
        result = analyzer.analyze_path(file_path)
        
        if result.ok:
            print(f"✅ Analysis successful!")
            print(f"📊 Metadata: {result.meta}")
            print(f"📝 Text preview: {result.text[:200]}...")
            
            if result.warning:
                print(f"⚠️  Warning: {result.warning}")
        else:
            print(f"❌ Analysis failed: {result.error}")
    
    # Cleanup
    import shutil
    shutil.rmtree(os.path.dirname(list(test_files.values())[0]))
    print(f"\n🧹 Cleaned up test files")


async def example_custom_limits():
    """Example: Using custom analysis limits"""
    print("\n=== Custom Limits Example ===")
    
    # Create analyzer with custom limits
    custom_limits = AnalyzeLimits(
        max_bytes=1024 * 1024,  # 1 MB limit
        max_pdf_pages=10,
        max_slides=5,
        max_cells=1000,
        ocr_enabled=False
    )
    
    analyzer = FileAnalyzer(limits=custom_limits)
    
    # Create a test file that exceeds limits
    temp_dir = tempfile.mkdtemp(prefix="limits_test_")
    large_file = os.path.join(temp_dir, "large_file.txt")
    
    # Create a file larger than 1MB
    with open(large_file, "w") as f:
        for i in range(100000):
            f.write(f"This is line {i} of a large test file for demonstrating size limits.\n")
    
    file_size = os.path.getsize(large_file)
    print(f"📄 Created test file: {file_size} bytes")
    print(f"🚫 Size limit: {custom_limits.max_bytes} bytes")
    
    result = analyzer.analyze_path(large_file)
    
    if result.ok:
        print(f"✅ File processed successfully")
        print(f"📝 Text length: {len(result.text)} characters")
    else:
        print(f"❌ File rejected: {result.error}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print(f"🧹 Cleaned up test files")


async def example_vector_store_management():
    """Example: Vector store file management"""
    print("\n=== Vector Store Management Example ===")
    
    examples = FileProcessingExamples()
    test_files = examples.create_test_files()
    
    vector_saver = VectorStoreSaver()
    
    # Upload files to vector store
    store_name = "File Processing Test Store"
    print(f"📤 Uploading files to vector store: {store_name}")
    
    uploaded_files = []
    for file_type, file_path in test_files.items():
        print(f"\n📄 Uploading {file_type.upper()} file...")
        
        try:
            vector_store_id = await vector_saver.upload_if_needed(
                file_path,
                vector_store_name=store_name,
                expires_days=2,
                validate_with_analyzer=True
            )
            
            uploaded_files.append({
                "type": file_type,
                "path": file_path,
                "vector_store_id": vector_store_id
            })
            
            print(f"✅ Uploaded to vector store: {vector_store_id}")
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
    
    # Try uploading the same files again (should skip duplicates)
    print(f"\n🔄 Testing duplicate detection...")
    
    for file_info in uploaded_files[:2]:  # Test first 2 files
        print(f"📄 Re-uploading {file_info['type'].upper()} file...")
        
        try:
            vector_store_id = await vector_saver.upload_if_needed(
                file_info["path"],
                vector_store_name=store_name,
                expires_days=2
            )
            
            print(f"✅ Vector store ID: {vector_store_id} (should be same as before)")
            
        except Exception as e:
            print(f"❌ Re-upload failed: {e}")
    
    # Cleanup
    import shutil
    shutil.rmtree(os.path.dirname(list(test_files.values())[0]))
    print(f"\n🧹 Cleaned up local test files")
    print(f"ℹ️  Vector store files remain in OpenAI (will expire in 2 days)")


async def example_supported_file_types():
    """Example: Test all supported file types"""
    print("\n=== Supported File Types Example ===")
    
    from .file_analyzer import SUPPORTED_EXTS, TEXT_EXTS
    
    print(f"📋 Total supported extensions: {len(SUPPORTED_EXTS)}")
    print(f"📝 Text-based extensions: {len(TEXT_EXTS)}")
    
    # Group by category
    categories = {
        "Text Files": [".txt", ".md", ".log"],
        "Data Files": [".csv", ".tsv", ".json"],
        "Documents": [".pdf", ".docx", ".pptx", ".xlsx"],
        "Code Files": [".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".go", ".rs", ".sh", ".sql", ".yaml", ".yml", ".xml"],
        "Images": [".png", ".jpg", ".jpeg", ".webp"]
    }
    
    for category, extensions in categories.items():
        print(f"\n📂 {category}:")
        supported_in_category = [ext for ext in extensions if ext in SUPPORTED_EXTS]
        for ext in supported_in_category:
            print(f"  ✅ {ext}")
    
    # Test with unsupported file type
    analyzer = FileAnalyzer()
    
    # Create a test file with unsupported extension
    temp_dir = tempfile.mkdtemp(prefix="unsupported_test_")
    unsupported_file = os.path.join(temp_dir, "test.xyz")
    
    with open(unsupported_file, "w") as f:
        f.write("This file has an unsupported extension.")
    
    print(f"\n🚫 Testing unsupported file type (.xyz):")
    result = analyzer.analyze_path(unsupported_file)
    
    if result.ok:
        print(f"✅ Unexpectedly processed: {result.text[:100]}...")
    else:
        print(f"❌ Correctly rejected: {result.error}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


async def example_error_handling():
    """Example: Error handling scenarios"""
    print("\n=== Error Handling Example ===")
    
    analyzer = FileAnalyzer()
    
    # Test non-existent file
    print("🚫 Testing non-existent file:")
    try:
        result = analyzer.analyze_path("non_existent_file.txt")
        print(f"❌ Should have failed, but got: {result}")
    except Exception as e:
        print(f"✅ Correctly caught exception: {e}")
    
    # Test file without required dependencies (simulate)
    print(f"\n🚫 Testing missing dependencies:")
    
    # Create a temporary PDF-like file
    temp_dir = tempfile.mkdtemp(prefix="error_test_")
    fake_pdf = os.path.join(temp_dir, "fake.pdf")
    
    with open(fake_pdf, "w") as f:
        f.write("This is not a real PDF file, just for testing error handling.")
    
    result = analyzer.analyze_path(fake_pdf)
    
    if result.ok:
        print(f"✅ Processed fake PDF: {result.text[:100]}...")
        if result.warning:
            print(f"⚠️  Warning: {result.warning}")
    else:
        print(f"❌ Failed as expected: {result.error}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


async def example_batch_processing():
    """Example: Batch process multiple files"""
    print("\n=== Batch Processing Example ===")
    
    examples = FileProcessingExamples()
    test_files = examples.create_test_files()
    
    analyzer = FileAnalyzer()
    
    # Process all files in batch
    results = []
    file_paths = list(test_files.values())
    
    print(f"📦 Batch processing {len(file_paths)} files...")
    
    for i, file_path in enumerate(file_paths, 1):
        print(f"\n[{i}/{len(file_paths)}] Processing: {os.path.basename(file_path)}")
        
        result = analyzer.analyze_path(file_path)
        
        results.append({
            "file": os.path.basename(file_path),
            "success": result.ok,
            "text_length": len(result.text) if result.ok else 0,
            "error": result.error if not result.ok else None,
            "warning": result.warning,
            "meta": result.meta
        })
        
        if result.ok:
            print(f"  ✅ Success ({len(result.text)} chars)")
        else:
            print(f"  ❌ Failed: {result.error}")
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    total_chars = sum(r["text_length"] for r in results if r["success"])
    
    print(f"\n📊 Batch Summary:")
    print(f"  ✅ Successful: {successful}/{len(results)}")
    print(f"  📝 Total characters extracted: {total_chars:,}")
    print(f"  📄 Average file size: {total_chars // successful if successful > 0 else 0:,} chars")
    
    # Cleanup
    import shutil
    shutil.rmtree(os.path.dirname(list(test_files.values())[0]))
    print(f"\n🧹 Cleaned up test files")


async def example_integration_workflow():
    """Example: Complete file processing workflow"""
    print("\n=== Integration Workflow Example ===")
    
    examples = FileProcessingExamples()
    test_files = examples.create_test_files()
    
    analyzer = FileAnalyzer()
    vector_saver = VectorStoreSaver()
    
    # Workflow: Analyze → Validate → Upload to Vector Store
    print("🔄 Workflow: File Analysis → Validation → Vector Store Upload")
    
    workflow_results = []
    
    for file_type, file_path in test_files.items():
        print(f"\n📄 Processing {file_type.upper()} file: {os.path.basename(file_path)}")
        
        # Step 1: Analyze file
        print("  🔍 Step 1: Analyzing file...")
        result = analyzer.analyze_path(file_path)
        
        if not result.ok:
            print(f"  ❌ Analysis failed: {result.error}")
            workflow_results.append({
                "file": os.path.basename(file_path),
                "step_failed": "analysis",
                "error": result.error
            })
            continue
        
        print(f"  ✅ Analysis successful ({len(result.text)} chars)")
        
        # Step 2: Validate content (custom logic)
        print("  ✅ Step 2: Validating content...")
        if len(result.text.strip()) == 0:
            print(f"  ❌ Validation failed: Empty content")
            workflow_results.append({
                "file": os.path.basename(file_path),
                "step_failed": "validation",
                "error": "Empty content"
            })
            continue
        
        print(f"  ✅ Content validation passed")
        
        # Step 3: Upload to vector store
        print("  📤 Step 3: Uploading to vector store...")
        
        try:
            vector_store_id = await vector_saver.upload_if_needed(
                file_path,
                vector_store_name="Integration Workflow Test",
                expires_days=1,
                validate_with_analyzer=True
            )
            
            print(f"  ✅ Uploaded to vector store: {vector_store_id[:8]}...")
            
            workflow_results.append({
                "file": os.path.basename(file_path),
                "success": True,
                "vector_store_id": vector_store_id,
                "text_length": len(result.text)
            })
            
        except Exception as e:
            print(f"  ❌ Upload failed: {e}")
            workflow_results.append({
                "file": os.path.basename(file_path),
                "step_failed": "upload",
                "error": str(e)
            })
    
    # Workflow summary
    successful = sum(1 for r in workflow_results if r.get("success"))
    print(f"\n🎉 Workflow Summary:")
    print(f"  ✅ Successfully processed: {successful}/{len(workflow_results)}")
    
    for result in workflow_results:
        if result.get("success"):
            print(f"  📄 {result['file']}: ✅ Complete")
        else:
            print(f"  📄 {result['file']}: ❌ Failed at {result.get('step_failed', 'unknown')} - {result.get('error', 'Unknown error')}")
    
    # Cleanup
    import shutil
    shutil.rmtree(os.path.dirname(list(test_files.values())[0]))
    print(f"\n🧹 Cleaned up local test files")


# Utility functions
def get_supported_extensions() -> List[str]:
    """Utility: Get list of supported file extensions"""
    from .file_analyzer import SUPPORTED_EXTS
    return sorted(list(SUPPORTED_EXTS))


def is_file_supported(file_path: str) -> bool:
    """Utility: Check if file extension is supported"""
    from .file_analyzer import SUPPORTED_EXTS
    ext = os.path.splitext(file_path)[1].lower()
    return ext in SUPPORTED_EXTS


async def quick_analyze(file_path: str) -> str:
    """Utility: Quick file analysis returning just text"""
    analyzer = FileAnalyzer()
    result = analyzer.analyze_path(file_path)
    return result.text if result.ok else f"Error: {result.error}"


async def quick_upload_to_vector_store(file_path: str, store_name: str = "Quick Upload Store") -> str:
    """Utility: Quick upload to vector store"""
    saver = VectorStoreSaver()
    return await saver.upload_if_needed(file_path, vector_store_name=store_name)


# Main example runner
async def run_file_processing_examples():
    """Run all file processing examples"""
    print("🚀 Starting File Processing Examples\n")
    
    try:
        # Run individual examples
        await example_basic_file_analysis()
        await example_custom_limits()
        await example_vector_store_management()
        await example_supported_file_types()
        await example_error_handling()
        await example_batch_processing()
        await example_integration_workflow()
        
        print("\n🎉 All file processing examples completed!")
        
    except Exception as e:
        print(f"\n❌ File processing examples failed: {e}")


if __name__ == "__main__":
    asyncio.run(run_file_processing_examples())
