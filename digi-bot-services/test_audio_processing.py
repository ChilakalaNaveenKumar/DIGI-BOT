#!/usr/bin/env python3
"""
Test Audio Processing Examples

Simple test script to demonstrate audio processing functionality.
Run this to see the audio transcription and synthesis in action.
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.audio_processing.examples import run_audio_examples


async def simple_audio_test():
    """Simple test of audio processing functionality"""
    print("🧪 Simple Audio Processing Test\n")
    
    try:
        from app.services.audio_processing import AudioTranscriberClient, SpeechSynthClient
        
        # Test Speech Synthesis
        print("🔊 Testing Speech Synthesis...")
        synthesizer = SpeechSynthClient()
        
        test_text = "Hello! This is a test of the audio processing system."
        output_file = "test_speech.mp3"
        
        try:
            saved_path = await synthesizer.synth_to_file(
                test_text,
                output_file,
                voice="alloy",
                audio_format="mp3"
            )
            
            print(f"✅ Speech synthesis successful!")
            print(f"🔊 Generated audio: {saved_path}")
            
            # Check file size
            if os.path.exists(saved_path):
                file_size = os.path.getsize(saved_path)
                print(f"📊 File size: {file_size} bytes")
            
        except Exception as e:
            print(f"❌ Speech synthesis failed: {e}")
        
        # Test Audio Transcription (if test file exists)
        print(f"\n🎤 Testing Audio Transcription...")
        transcriber = AudioTranscriberClient()
        
        # Try to transcribe the file we just created
        if os.path.exists(output_file):
            try:
                result = await transcriber.transcribe_file(
                    output_file,
                    language="en",
                    response_format="json"
                )
                
                print(f"✅ Transcription successful!")
                print(f"📝 Original text: '{test_text}'")
                print(f"📝 Transcribed text: '{result['text']}'")
                
            except Exception as e:
                print(f"❌ Transcription failed: {e}")
        else:
            print("⚠️  No audio file to transcribe")
        
        print(f"\n✅ Simple audio test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and have the required dependencies")
    except Exception as e:
        print(f"❌ Test failed: {e}")


async def test_voice_options():
    """Test different voice options"""
    print("\n🎭 Testing Voice Options")
    
    try:
        from app.services.audio_processing import SpeechSynthClient
        
        synthesizer = SpeechSynthClient()
        test_text = "This is a test of different voice options."
        voices = ["alloy", "verse", "amber"]
        
        print(f"📝 Test text: '{test_text}'")
        
        for voice in voices:
            print(f"\n🎤 Testing voice: {voice}")
            
            try:
                output_file = f"voice_test_{voice}.mp3"
                
                await synthesizer.synth_to_file(
                    test_text,
                    output_file,
                    voice=voice,
                    audio_format="mp3"
                )
                
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    print(f"  ✅ Generated: {output_file} ({file_size} bytes)")
                else:
                    print(f"  ❌ File not created")
                    
            except Exception as e:
                print(f"  ❌ Failed: {e}")
        
        print("✅ Voice options test completed!")
        
    except Exception as e:
        print(f"❌ Voice test failed: {e}")


async def test_audio_formats():
    """Test different audio formats"""
    print("\n🎵 Testing Audio Formats")
    
    try:
        from app.services.audio_processing import SpeechSynthClient
        
        synthesizer = SpeechSynthClient()
        test_text = "Testing different audio formats."
        formats = ["mp3", "wav", "flac"]
        
        print(f"📝 Test text: '{test_text}'")
        
        for audio_format in formats:
            print(f"\n📊 Testing format: {audio_format}")
            
            try:
                output_file = f"format_test.{audio_format}"
                
                await synthesizer.synth_to_file(
                    test_text,
                    output_file,
                    voice="alloy",
                    audio_format=audio_format
                )
                
                if os.path.exists(output_file):
                    file_size = os.path.getsize(output_file)
                    print(f"  ✅ Generated: {output_file} ({file_size} bytes)")
                else:
                    print(f"  ❌ File not created")
                    
            except Exception as e:
                print(f"  ❌ Failed: {e}")
        
        print("✅ Audio formats test completed!")
        
    except Exception as e:
        print(f"❌ Format test failed: {e}")


async def test_model_fallback():
    """Test model fallback functionality"""
    print("\n🔄 Testing Model Fallback")
    
    try:
        from app.services.audio_processing import AudioTranscriberClient
        
        # Test with primary model
        print("🎤 Testing with primary model...")
        transcriber1 = AudioTranscriberClient()
        await transcriber1.initialize()
        print(f"✅ Using model: {transcriber1.model}")
        
        # Test with explicit whisper-1
        print("🎤 Testing with explicit whisper-1...")
        transcriber2 = AudioTranscriberClient(model="whisper-1")
        await transcriber2.initialize()
        print(f"✅ Using model: {transcriber2.model}")
        
        print("✅ Model fallback test completed!")
        
    except Exception as e:
        print(f"❌ Model fallback test failed: {e}")


async def cleanup_test_files():
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...")
    
    test_files = [
        "test_speech.mp3",
        "voice_test_alloy.mp3",
        "voice_test_verse.mp3", 
        "voice_test_amber.mp3",
        "format_test.mp3",
        "format_test.wav",
        "format_test.flac"
    ]
    
    cleaned = 0
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                cleaned += 1
                print(f"  🗑️  Removed: {file_path}")
            except Exception as e:
                print(f"  ❌ Failed to remove {file_path}: {e}")
    
    if cleaned > 0:
        print(f"✅ Cleaned up {cleaned} test files")
    else:
        print("ℹ️  No test files to clean up")


async def main():
    """Main test runner"""
    print("🚀 Audio Processing Test Suite\n")
    
    # Choose test mode
    print("Select test mode:")
    print("1. Simple test (basic functionality)")
    print("2. Voice options test")
    print("3. Audio formats test")
    print("4. Model fallback test")
    print("5. Full examples (comprehensive)")
    print("6. All tests")
    print("7. Cleanup test files")
    
    try:
        choice = input("\nEnter choice (1-7, default=1): ").strip() or "1"
        
        if choice == "1":
            await simple_audio_test()
        elif choice == "2":
            await test_voice_options()
        elif choice == "3":
            await test_audio_formats()
        elif choice == "4":
            await test_model_fallback()
        elif choice == "5":
            await run_audio_examples()
        elif choice == "6":
            await simple_audio_test()
            await test_voice_options()
            await test_audio_formats()
            await test_model_fallback()
        elif choice == "7":
            await cleanup_test_files()
        else:
            print("Invalid choice, running simple test...")
            await simple_audio_test()
            
        # Ask about cleanup
        if choice not in ["7"]:
            cleanup = input("\nCleanup test files? (y/N): ").strip().lower()
            if cleanup in ["y", "yes"]:
                await cleanup_test_files()
            
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
