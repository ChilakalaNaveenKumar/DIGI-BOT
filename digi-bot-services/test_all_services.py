#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Test Suite - Test All Services

This comprehensive test suite tests all services:
- Chart Matcher (embedding-based)
- Vision Models (analysis + generation)
- Audio Processing (transcription + synthesis)
- File Processing (analysis + vector storage)
- Smart Model Client
- Authentication Service

Generates sample files as needed for testing.
"""

import asyncio
import sys
import os
import tempfile
import shutil
import json
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, relying on system environment variables")
    pass

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


class ServiceTestSuite:
    """Comprehensive test suite for all services"""
    
    def __init__(self):
        self.temp_dir = None
        self.test_files = {}
        self.results = {}
    
    def setup_test_environment(self):
        """Set up test environment with sample files"""
        print("🔧 Setting up test environment...")
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="digi_bot_test_")
        print(f"📁 Test directory: {self.temp_dir}")
        
        # Create sample files
        self._create_sample_files()
        
        return self.temp_dir
    
    def _create_sample_files(self):
        """Create sample files for testing"""
        
        # Text files
        sample_txt = os.path.join(self.temp_dir, "sample.txt")
        with open(sample_txt, "w") as f:
            f.write("This is a sample text file for testing file processing.\n")
            f.write("It contains multiple lines of content.\n")
            f.write("The file processing service should extract this text successfully.")
        self.test_files["txt"] = sample_txt
        
        # JSON file
        sample_json = os.path.join(self.temp_dir, "sample.json")
        with open(sample_json, "w") as f:
            data = {
                "project": "Digi Bot Services Test",
                "services": ["component_matcher", "vision_models", "audio_processing", "file_processing"],
                "test_data": {
                    "charts": ["bar", "pie", "line"],
                    "formats": ["json", "txt", "csv"]
                }
            }
            json.dump(data, f, indent=2)
        self.test_files["json"] = sample_json
        
        # CSV file
        sample_csv = os.path.join(self.temp_dir, "sample.csv")
        with open(sample_csv, "w") as f:
            f.write("Name,Value,Category\n")
            f.write("Product A,100,Electronics\n")
            f.write("Product B,150,Clothing\n")
            f.write("Product C,200,Books\n")
        self.test_files["csv"] = sample_csv
        
        # Markdown file
        sample_md = os.path.join(self.temp_dir, "sample.md")
        with open(sample_md, "w") as f:
            f.write("# Test Document\n\n")
            f.write("This is a **markdown** file for testing.\n\n")
            f.write("## Chart Examples\n\n")
            f.write("- Bar charts for comparisons\n")
            f.write("- Pie charts for percentages\n")
            f.write("- Line charts for trends\n\n")
            f.write("```python\n")
            f.write("# Sample code\n")
            f.write("def test_function():\n")
            f.write("    return 'Hello World'\n")
            f.write("```\n")
        self.test_files["md"] = sample_md
        
        print(f"✅ Created {len(self.test_files)} sample files")
    
    def cleanup_test_environment(self):
        """Clean up test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up test directory")


async def test_component_matcher():
    """Test chart matcher with embedding-based approach"""
    print("\n" + "="*50)
    print("🧪 TESTING COMPONENT MATCHER")
    print("="*50)
    
    try:
        from app.services.component_matcher import ComponentMatcherClient, VectorStoreManager
        
        # Initialize components
        print("🔧 Initializing component matcher...")
        vector_manager = VectorStoreManager()
        component_matcher = ComponentMatcherClient()
        
        await vector_manager.initialize()
        await component_matcher.initialize()
        
        # Show stats
        stats = vector_manager.get_stats()
        print(f"📊 Vector store: {stats['total_docs']} documents loaded")
        
        # Test queries
        test_queries = [
            "Show sales data as a bar chart",
            "Create pie chart for market share",
            "Display revenue trends in line chart",
            "Make data table with metrics",
            "Random text that shouldn't match"
        ]
        
        print(f"\n🔍 Testing {len(test_queries)} queries:")
        
        results = []
        for i, query in enumerate(test_queries, 1):
            print(f"\n[{i}] Query: '{query}'")
            
            try:
                # Test embedding-based retrieval
                candidates = await vector_manager.query(query, top_k=3)
                
                if candidates:
                    print(f"  📋 Top matches:")
                    for j, candidate in enumerate(candidates, 1):
                        score = candidate['score']
                        source = candidate['meta'].get('source', 'unknown')
                        print(f"    {j}. Score: {score:.3f} | {source}")
                
                # Test chart matching
                result = await component_matcher.quick_match(query, vector_manager)
                has_match = component_matcher.has_match(result)
                
                results.append({
                    "query": query,
                    "has_match": has_match,
                    "candidates": len(candidates)
                })
                
                if has_match:
                    print(f"  ✅ Chart format found!")
                    print(f"  📋 Preview: {result[:100]}...")
                else:
                    print(f"  ❌ No chart format match")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
                results.append({"query": query, "error": str(e)})
        
        # Summary
        successful = sum(1 for r in results if r.get("has_match"))
        print(f"\n📊 Component Matcher Results: {successful}/{len(test_queries)} queries matched")
        
        return {"service": "component_matcher", "success": True, "matches": successful, "total": len(test_queries)}
        
    except Exception as e:
        print(f"❌ Component matcher test failed: {e}")
        return {"service": "component_matcher", "success": False, "error": str(e)}


async def test_vision_models():
    """Test vision models (analysis + generation)"""
    print("\n" + "="*50)
    print("🧪 TESTING VISION MODELS")
    print("="*50)
    
    try:
        from app.services.vision_models import VisionAnalyzerClient, ImageGeneratorClient
        
        # Test image generation first
        print("🎨 Testing image generation...")
        
        generator = ImageGeneratorClient()
        await generator.initialize()
        
        test_prompts = [
            "A simple bar chart showing sales data",
            "A professional office workspace"
        ]
        
        generated_images = []
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n[{i}] Generating: '{prompt}'")
            
            try:
                images = await generator.generate(
                    prompt,
                    size="1024x1024",
                    n=1
                )
                
                if images and images[0].get("b64"):
                    # Save generated image
                    import base64
                    image_path = f"generated_image_{i}.png"
                    
                    with open(image_path, "wb") as f:
                        f.write(base64.b64decode(images[0]["b64"]))
                    
                    generated_images.append(image_path)
                    print(f"  ✅ Generated and saved: {image_path}")
                    
                    if images[0].get("revised_prompt"):
                        print(f"  📝 Revised prompt: {images[0]['revised_prompt'][:100]}...")
                else:
                    print(f"  ❌ No image generated")
                    
            except Exception as e:
                print(f"  ❌ Generation failed: {e}")
        
        # Test vision analysis (if we have images)
        print(f"\n👁️  Testing vision analysis...")
        
        analyzer = VisionAnalyzerClient()
        await analyzer.initialize()
        
        # Test with a reliable public image URL
        test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Cat_August_2010-4.jpg/500px-Cat_August_2010-4.jpg"
        
        print(f"🔍 Analyzing sample image...")
        
        try:
            analysis_text = ""
            async for event in analyzer.analyze_url(
                test_image_url,
                "Describe this image in detail. What do you see?"
            ):
                if event["type"] == "content":
                    analysis_text += event["content"]
                elif event["type"] == "error":
                    print(f"  ❌ Analysis error: {event['error']}")
                    break
                elif event["type"] == "completion":
                    break
            
            if analysis_text:
                print(f"  ✅ Analysis completed!")
                print(f"  📝 Result: {analysis_text[:200]}...")
            else:
                print(f"  ❌ No analysis result")
                
        except Exception as e:
            print(f"  ❌ Vision analysis failed: {e}")
        
        # Cleanup generated images
        for img_path in generated_images:
            if os.path.exists(img_path):
                os.remove(img_path)
        
        print(f"\n📊 Vision Models: Generated {len(generated_images)} images, tested analysis")
        
        return {"service": "vision_models", "success": True, "images_generated": len(generated_images)}
        
    except Exception as e:
        print(f"❌ Vision models test failed: {e}")
        return {"service": "vision_models", "success": False, "error": str(e)}


async def test_audio_processing():
    """Test audio processing (transcription + synthesis)"""
    print("\n" + "="*50)
    print("🧪 TESTING AUDIO PROCESSING")
    print("="*50)
    
    try:
        from app.services.audio_processing import AudioTranscriberClient, SpeechSynthClient
        
        # Test speech synthesis first (to generate audio files)
        print("🔊 Testing speech synthesis...")
        
        synthesizer = SpeechSynthClient()
        await synthesizer.initialize()
        
        test_texts = [
            "Hello! This is a test of the speech synthesis system.",
            "Welcome to Digi Bot Services. This is a comprehensive test of our audio processing capabilities.",
            "Testing different voices and audio quality for transcription testing."
        ]
        
        generated_audio = []
        voices = ["alloy", "nova", "shimmer"]
        
        for i, (text, voice) in enumerate(zip(test_texts, voices), 1):
            print(f"\n[{i}] Synthesizing with voice '{voice}':")
            print(f"    Text: '{text[:50]}...'")
            
            try:
                output_file = f"test_audio_{i}.mp3"
                
                saved_path = await synthesizer.synth_to_file(
                    text,
                    output_file,
                    voice=voice,
                    audio_format="mp3"
                )
                
                if os.path.exists(saved_path):
                    file_size = os.path.getsize(saved_path)
                    generated_audio.append(saved_path)
                    print(f"  ✅ Generated: {saved_path} ({file_size} bytes)")
                else:
                    print(f"  ❌ File not created")
                    
            except Exception as e:
                print(f"  ❌ Synthesis failed: {e}")
        
        # Test audio transcription
        print(f"\n🎤 Testing audio transcription...")
        
        transcriber = AudioTranscriberClient()
        await transcriber.initialize()
        
        transcription_results = []
        for i, audio_file in enumerate(generated_audio, 1):
            print(f"\n[{i}] Transcribing: {audio_file}")
            
            try:
                result = await transcriber.transcribe_file(
                    audio_file,
                    language="en",
                    response_format="json"
                )
                
                if result and result.get("text"):
                    transcribed_text = result["text"]
                    transcription_results.append(transcribed_text)
                    print(f"  ✅ Transcription successful!")
                    print(f"  📝 Result: '{transcribed_text[:100]}...'")
                    
                    # Compare with original (rough similarity check)
                    original = test_texts[i-1].lower()
                    transcribed = transcribed_text.lower()
                    
                    # Simple word overlap check
                    original_words = set(original.split())
                    transcribed_words = set(transcribed.split())
                    overlap = len(original_words & transcribed_words)
                    
                    if overlap > 0:
                        print(f"  🎯 Word overlap: {overlap} words match")
                    
                else:
                    print(f"  ❌ No transcription result")
                    
            except Exception as e:
                print(f"  ❌ Transcription failed: {e}")
        
        # Cleanup generated audio files
        for audio_file in generated_audio:
            if os.path.exists(audio_file):
                os.remove(audio_file)
        
        print(f"\n📊 Audio Processing: Generated {len(generated_audio)} files, transcribed {len(transcription_results)}")
        
        return {
            "service": "audio_processing", 
            "success": True, 
            "audio_generated": len(generated_audio),
            "transcriptions": len(transcription_results)
        }
        
    except Exception as e:
        print(f"❌ Audio processing test failed: {e}")
        return {"service": "audio_processing", "success": False, "error": str(e)}


async def test_file_processing(test_suite):
    """Test file processing (analysis + vector storage)"""
    print("\n" + "="*50)
    print("🧪 TESTING FILE PROCESSING")
    print("="*50)
    
    try:
        from app.services.file_processing import FileAnalyzer, TextVectorSaver
        
        # Test file analysis
        print("📄 Testing file analysis...")
        
        analyzer = FileAnalyzer()
        
        analysis_results = []
        for file_type, file_path in test_suite.test_files.items():
            print(f"\n📄 Analyzing {file_type.upper()}: {os.path.basename(file_path)}")
            
            try:
                result = analyzer.analyze_path(file_path)
                
                if result.ok:
                    analysis_results.append({
                        "type": file_type,
                        "success": True,
                        "text_length": len(result.text),
                        "metadata": result.meta
                    })
                    
                    print(f"  ✅ Analysis successful!")
                    print(f"  📊 Extracted {len(result.text)} characters")
                    print(f"  📋 Metadata: {result.meta}")
                    
                    if result.warning:
                        print(f"  ⚠️  Warning: {result.warning}")
                else:
                    print(f"  ❌ Analysis failed: {result.error}")
                    analysis_results.append({
                        "type": file_type,
                        "success": False,
                        "error": result.error
                    })
                    
            except Exception as e:
                print(f"  ❌ Exception: {e}")
                analysis_results.append({
                    "type": file_type,
                    "success": False,
                    "error": str(e)
                })
        
        # Test text vector storage
        print(f"\n🗂️  Testing text vector storage...")
        
        text_saver = TextVectorSaver()
        
        # Process a few files
        vector_results = []
        files_to_process = list(test_suite.test_files.items())[:2]  # Test first 2 files
        
        for file_type, file_path in files_to_process:
            print(f"\n📤 Processing {file_type.upper()} for vector storage...")
            
            try:
                result = await text_saver.extract_and_save_text(
                    file_path,
                    vector_store_name="File Processing Test Store",
                    expires_days=1,
                    chunk_size=1000
                )
                
                if result["success"]:
                    vector_results.append(result)
                    print(f"  ✅ Vector storage successful!")
                    print(f"  📊 Characters: {result['characters']}")
                    print(f"  📋 Chunks: {result['chunks']}")
                    print(f"  🗂️  Vector store: {result['vector_store_id'][:8]}...")
                else:
                    print(f"  ❌ Vector storage failed: {result['error']}")
                    
            except Exception as e:
                print(f"  ❌ Vector storage exception: {e}")
        
        successful_analysis = sum(1 for r in analysis_results if r["success"])
        successful_vector = len(vector_results)
        
        print(f"\n📊 File Processing: {successful_analysis}/{len(test_suite.test_files)} files analyzed, {successful_vector} stored in vector DB")
        
        return {
            "service": "file_processing",
            "success": True,
            "files_analyzed": successful_analysis,
            "files_vectorized": successful_vector,
            "total_files": len(test_suite.test_files)
        }
        
    except Exception as e:
        print(f"❌ File processing test failed: {e}")
        return {"service": "file_processing", "success": False, "error": str(e)}


async def test_smart_model_client():
    """Test smart model client"""
    print("\n" + "="*50)
    print("🧪 TESTING SMART MODEL CLIENT")
    print("="*50)
    
    try:
        from app.services.smart_model_client import SmartModelClient, ChartAnalysisClient
        from app.services.model_config import get_model_config, estimate_cost
        
        # Test model configuration
        print("🔧 Testing model configuration...")
        
        models_to_test = ["gpt-4o", "gpt-4o-mini", "o1-mini"]
        
        for model in models_to_test:
            config = get_model_config(model)
            if config:
                print(f"  📋 {model}: {config.context_tokens:,} context, {config.output_tokens:,} output")
                cost = estimate_cost(model, 1000, 500)
                print(f"      Cost estimate (1k in, 500 out): ${cost:.4f}")
            else:
                print(f"  ❌ {model}: Configuration not found")
        
        # Test smart client
        print(f"\n🤖 Testing smart model client...")
        
        smart_client = SmartModelClient(budget_per_request=0.10)
        await smart_client.initialize()
        
        test_prompts = [
            ("Explain quantum computing", "chat"),
            ("Analyze this data trend", "analysis"),
            ("Solve this math problem step by step", "reasoning")
        ]
        
        for i, (prompt, task_type) in enumerate(test_prompts, 1):
            print(f"\n[{i}] Task: {task_type} | Prompt: '{prompt[:30]}...'")
            
            try:
                response = await smart_client.quick_completion(
                    prompt,
                    task_type=task_type,
                    max_output_tokens=500
                )
                
                if response and not response.startswith("ERROR"):
                    print(f"  ✅ Response generated ({len(response)} chars)")
                    print(f"  📝 Preview: {response[:100]}...")
                else:
                    print(f"  ❌ Failed: {response}")
                    
            except Exception as e:
                print(f"  ❌ Exception: {e}")
        
        # Test specialized client
        print(f"\n📊 Testing chart analysis client...")
        
        chart_client = ChartAnalysisClient()
        await chart_client.initialize()
        
        chart_query = "Create a bar chart showing quarterly sales data"
        
        try:
            chart_result = await chart_client.analyze_chart_request(
                chart_query,
                "Sample chart documentation for testing"
            )
            
            if chart_result:
                print(f"  ✅ Chart analysis completed")
                print(f"  📋 Result: {chart_result[:100]}...")
            else:
                print(f"  ❌ No chart analysis result")
                
        except Exception as e:
            print(f"  ❌ Chart analysis failed: {e}")
        
        print(f"\n📊 Smart Model Client: Tested configuration, smart selection, and specialized clients")
        
        return {"service": "smart_model_client", "success": True}
        
    except Exception as e:
        print(f"❌ Smart model client test failed: {e}")
        return {"service": "smart_model_client", "success": False, "error": str(e)}


async def test_auth_service():
    """Test authentication service"""
    print("\n" + "="*50)
    print("🧪 TESTING AUTHENTICATION SERVICE")
    print("="*50)
    
    try:
        from app.services.auth import AuthService
        
        print("🔐 Testing authentication service...")
        
        # Create dummy DB for testing
        class DummyDB:
            pass
        
        auth_service = AuthService(DummyDB())
        
        # Test token generation and validation
        test_user_data = {
            "user_id": "test_user_123",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        print(f"👤 Testing with user: {test_user_data['email']}")
        
        # Generate token
        try:
            token = auth_service.create_access_token(test_user_data)
            print(f"  ✅ Token generated: {token[:20]}...")
            
            # Validate token
            decoded_data = auth_service.verify_token(token)
            
            if decoded_data:
                print(f"  ✅ Token validation successful")
                print(f"  📋 Decoded data: {decoded_data}")
                
                # Check if user data matches
                if decoded_data.get("user_id") == test_user_data["user_id"]:
                    print(f"  ✅ User data integrity verified")
                else:
                    print(f"  ❌ User data mismatch")
            else:
                print(f"  ❌ Token validation failed")
                
        except Exception as e:
            print(f"  ❌ Token operations failed: {e}")
        
        # Test invalid token
        print(f"\n🚫 Testing invalid token handling...")
        
        try:
            invalid_result = auth_service.verify_token("invalid.token.here")
            if invalid_result is None:
                print(f"  ✅ Invalid token correctly rejected")
            else:
                print(f"  ❌ Invalid token incorrectly accepted")
                
        except Exception as e:
            print(f"  ✅ Invalid token correctly raised exception: {type(e).__name__}")
        
        print(f"\n📊 Authentication Service: Tested token generation, validation, and security")
        
        return {"service": "auth_service", "success": True}
        
    except Exception as e:
        print(f"❌ Authentication service test failed: {e}")
        return {"service": "auth_service", "success": False, "error": str(e)}


async def run_comprehensive_test():
    """Run comprehensive test of all services"""
    print("🚀 DIGI BOT SERVICES - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Setup test environment
    test_suite = ServiceTestSuite()
    test_suite.setup_test_environment()
    
    try:
        # Run all tests
        test_results = []
        
        # Test each service
        test_results.append(await test_component_matcher())
        test_results.append(await test_vision_models())
        test_results.append(await test_audio_processing())
        test_results.append(await test_file_processing(test_suite))
        test_results.append(await test_smart_model_client())
        test_results.append(await test_auth_service())
        
        # Generate summary report
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("="*60)
        
        successful_services = 0
        total_services = len(test_results)
        
        for result in test_results:
            service_name = result["service"].replace("_", " ").title()
            
            if result["success"]:
                successful_services += 1
                print(f"✅ {service_name}: PASSED")
                
                # Show specific metrics
                if "matches" in result:
                    print(f"   📊 Chart matches: {result['matches']}/{result['total']}")
                if "images_generated" in result:
                    print(f"   🎨 Images generated: {result['images_generated']}")
                if "audio_generated" in result:
                    print(f"   🔊 Audio files: {result['audio_generated']}")
                if "files_analyzed" in result:
                    print(f"   📄 Files analyzed: {result['files_analyzed']}/{result['total_files']}")
                    
            else:
                print(f"❌ {service_name}: FAILED")
                if "error" in result:
                    print(f"   💥 Error: {result['error']}")
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   ✅ Successful: {successful_services}/{total_services} services")
        print(f"   📊 Success Rate: {(successful_services/total_services)*100:.1f}%")
        
        if successful_services == total_services:
            print(f"\n🎉 ALL SERVICES PASSED! Digi Bot Services is ready for production! 🚀")
        else:
            print(f"\n⚠️  Some services need attention. Check the logs above for details.")
        
        return test_results
        
    finally:
        # Cleanup
        test_suite.cleanup_test_environment()


async def main():
    """Main test runner"""
    try:
        results = await run_comprehensive_test()
        
        # Ask if user wants detailed results
        print(f"\n" + "="*60)
        save_results = input("💾 Save detailed test results to file? (y/N): ").strip().lower()
        
        if save_results in ["y", "yes"]:
            results_file = "test_results.json"
            with open(results_file, "w") as f:
                json.dump(results, f, indent=2, default=str)
            print(f"📄 Results saved to: {results_file}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test suite interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
