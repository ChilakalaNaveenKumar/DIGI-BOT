"""
Usage examples for Audio Processing clients.

These examples demonstrate how to use AudioTranscriberClient and SpeechSynthClient
for speech-to-text and text-to-speech operations.
"""

import asyncio
import os
from typing import Dict, List, Any
from .audio_transcriber import AudioTranscriberClient
from .speech_synth import SpeechSynthClient


class AudioProcessingExamples:
    """Examples and utilities for Audio Processing service"""
    
    def __init__(self):
        self.transcriber = AudioTranscriberClient()
        self.synthesizer = SpeechSynthClient()
    
    async def initialize(self):
        """Initialize both audio clients"""
        print("🎵 Initializing Audio Processing clients...")
        await self.transcriber.initialize()
        await self.synthesizer.initialize()
        print("✅ Audio clients initialized")


async def example_transcribe_file():
    """Example: Transcribe a local audio file"""
    print("=== File Transcription Example ===")
    
    transcriber = AudioTranscriberClient()
    
    # Example with a local audio file (you'd replace with actual file)
    audio_file = "example_audio.mp3"  # Replace with actual file path
    
    if os.path.exists(audio_file):
        print(f"🎤 Transcribing file: {audio_file}")
        
        # Basic transcription
        result = await transcriber.transcribe_file(
            audio_file,
            language="en",
            response_format="json"
        )
        
        print(f"📝 Transcription: {result['text']}")
        
        # Transcription with timestamps (verbose format)
        verbose_result = await transcriber.transcribe_file(
            audio_file,
            response_format="verbose_json"
        )
        
        print(f"📊 Verbose result keys: {list(verbose_result.keys())}")
        if hasattr(verbose_result, 'segments'):
            print(f"🕐 Found {len(verbose_result.segments)} segments")
    else:
        print(f"⚠️  Audio file not found: {audio_file}")
        print("📝 Simulated transcription result: 'Hello, this is a test audio file.'")


async def example_transcribe_bytes():
    """Example: Transcribe audio from bytes (e.g., uploaded file)"""
    print("\n=== Bytes Transcription Example ===")
    
    transcriber = AudioTranscriberClient()
    
    # Simulate reading audio bytes (in real usage, this would be uploaded data)
    audio_file = "example_audio.wav"
    
    if os.path.exists(audio_file):
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        
        print(f"🎤 Transcribing {len(audio_bytes)} bytes of audio data")
        
        result = await transcriber.transcribe_bytes(
            audio_bytes,
            filename="uploaded_audio.wav",
            language="en",
            response_format="json"
        )
        
        print(f"📝 Transcription: {result['text']}")
    else:
        print("📝 Simulated bytes transcription: 'This audio was uploaded as bytes.'")


async def example_speech_synthesis():
    """Example: Generate speech from text"""
    print("\n=== Speech Synthesis Example ===")
    
    synthesizer = SpeechSynthClient()
    
    # Test different voices and formats
    test_texts = [
        ("Hello! This is a test of the speech synthesis system.", "alloy", "mp3"),
        ("Welcome to our audio processing service.", "verse", "wav"),
        ("This demonstrates different voice options.", "amber", "mp3")
    ]
    
    for i, (text, voice, format_type) in enumerate(test_texts, 1):
        print(f"\n[{i}] Synthesizing with voice '{voice}' in {format_type} format")
        print(f"📝 Text: '{text}'")
        
        # Generate to file
        output_file = f"speech_example_{i}.{format_type}"
        
        try:
            saved_path = await synthesizer.synth_to_file(
                text,
                output_file,
                voice=voice,
                audio_format=format_type
            )
            
            print(f"🔊 Audio saved to: {saved_path}")
            
            # Also demonstrate getting bytes
            audio_bytes = await synthesizer.synth_to_bytes(
                text,
                voice=voice,
                audio_format=format_type
            )
            
            print(f"📊 Generated {len(audio_bytes)} bytes of audio data")
            
        except Exception as e:
            print(f"❌ Synthesis failed: {e}")


async def example_voice_comparison():
    """Example: Compare different voices"""
    print("\n=== Voice Comparison Example ===")
    
    synthesizer = SpeechSynthClient()
    
    test_text = "This is a comparison of different voice options available in the text-to-speech system."
    voices = ["alloy", "verse", "coral", "amber", "sage"]
    
    print(f"📝 Test text: '{test_text}'")
    print(f"🎭 Testing {len(voices)} different voices...")
    
    for voice in voices:
        print(f"\n🎤 Voice: {voice}")
        
        try:
            output_file = f"voice_comparison_{voice}.mp3"
            
            await synthesizer.synth_to_file(
                test_text,
                output_file,
                voice=voice,
                audio_format="mp3"
            )
            
            print(f"  ✅ Generated: {output_file}")
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")


async def example_audio_formats():
    """Example: Test different audio formats"""
    print("\n=== Audio Format Example ===")
    
    synthesizer = SpeechSynthClient()
    
    text = "Testing different audio formats for speech synthesis."
    formats = ["mp3", "wav", "flac", "opus", "aac"]
    
    print(f"📝 Text: '{text}'")
    print(f"🎵 Testing {len(formats)} audio formats...")
    
    for audio_format in formats:
        print(f"\n📊 Format: {audio_format}")
        
        try:
            output_file = f"format_test.{audio_format}"
            
            await synthesizer.synth_to_file(
                text,
                output_file,
                voice="alloy",
                audio_format=audio_format
            )
            
            # Check file size
            file_size = os.path.getsize(output_file)
            print(f"  ✅ Generated: {output_file} ({file_size} bytes)")
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")


async def example_transcription_formats():
    """Example: Test different transcription output formats"""
    print("\n=== Transcription Format Example ===")
    
    transcriber = AudioTranscriberClient()
    
    audio_file = "example_audio.mp3"  # Replace with actual file
    formats = ["json", "text", "verbose_json", "srt", "vtt"]
    
    if os.path.exists(audio_file):
        print(f"🎤 Testing transcription formats for: {audio_file}")
        
        for response_format in formats:
            print(f"\n📊 Format: {response_format}")
            
            try:
                result = await transcriber.transcribe_file(
                    audio_file,
                    response_format=response_format
                )
                
                if response_format == "verbose_json":
                    print(f"  ✅ Keys: {list(result.keys())}")
                    print(f"  📝 Text: {result.get('text', 'N/A')[:100]}...")
                else:
                    text_content = result.get('text', str(result))
                    print(f"  ✅ Result: {text_content[:100]}...")
                    
            except Exception as e:
                print(f"  ❌ Failed: {e}")
    else:
        print(f"⚠️  Audio file not found: {audio_file}")
        print("📝 Simulated format testing...")


async def example_batch_transcription():
    """Example: Batch transcribe multiple files"""
    print("\n=== Batch Transcription Example ===")
    
    transcriber = AudioTranscriberClient()
    
    # Simulate multiple audio files
    audio_files = [
        "meeting_part1.mp3",
        "meeting_part2.mp3", 
        "interview.wav",
        "presentation.m4a"
    ]
    
    print(f"🎤 Batch transcribing {len(audio_files)} files...")
    
    results = []
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] Processing: {audio_file}")
        
        if os.path.exists(audio_file):
            try:
                result = await transcriber.transcribe_file(
                    audio_file,
                    language="en",
                    response_format="json"
                )
                
                results.append({
                    "file": audio_file,
                    "success": True,
                    "text": result["text"],
                    "length": len(result["text"])
                })
                
                print(f"  ✅ Transcribed ({len(result['text'])} chars)")
                
            except Exception as e:
                results.append({
                    "file": audio_file,
                    "success": False,
                    "error": str(e)
                })
                print(f"  ❌ Failed: {e}")
        else:
            print(f"  ⚠️  File not found, simulating result...")
            results.append({
                "file": audio_file,
                "success": True,
                "text": f"Simulated transcription for {audio_file}",
                "length": 50
            })
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    total_chars = sum(r.get("length", 0) for r in results if r["success"])
    
    print(f"\n📊 Batch Summary:")
    print(f"  ✅ Successful: {successful}/{len(audio_files)}")
    print(f"  📝 Total characters: {total_chars}")


async def example_integration_workflow():
    """Example: Complete audio processing workflow"""
    print("\n=== Integration Workflow Example ===")
    
    transcriber = AudioTranscriberClient()
    synthesizer = SpeechSynthClient()
    
    # Workflow: Transcribe → Process → Synthesize response
    print("🔄 Workflow: Audio input → Transcription → Processing → Audio output")
    
    # Step 1: Transcribe input audio
    input_audio = "user_question.mp3"
    
    if os.path.exists(input_audio):
        print(f"🎤 Step 1: Transcribing {input_audio}")
        
        transcription = await transcriber.transcribe_file(
            input_audio,
            language="en",
            response_format="json"
        )
        
        user_text = transcription["text"]
        print(f"📝 User said: '{user_text}'")
    else:
        user_text = "What is the weather like today?"
        print(f"📝 Simulated user input: '{user_text}'")
    
    # Step 2: Process the text (simulate AI response)
    print("🤖 Step 2: Processing user input...")
    ai_response = f"I heard you ask: '{user_text}'. This is a simulated AI response to your question."
    print(f"💭 AI response: '{ai_response}'")
    
    # Step 3: Synthesize response to audio
    print("🔊 Step 3: Converting response to speech...")
    
    try:
        output_audio = "ai_response.mp3"
        
        await synthesizer.synth_to_file(
            ai_response,
            output_audio,
            voice="alloy",
            audio_format="mp3"
        )
        
        print(f"✅ Workflow complete! Response saved to: {output_audio}")
        
    except Exception as e:
        print(f"❌ Synthesis failed: {e}")


# Utility functions
async def quick_transcribe(audio_path: str) -> str:
    """Utility: Quick transcription of audio file"""
    transcriber = AudioTranscriberClient()
    result = await transcriber.transcribe_file(audio_path, response_format="json")
    return result["text"]


async def quick_synthesize(text: str, output_path: str, voice: str = "alloy") -> str:
    """Utility: Quick text-to-speech synthesis"""
    synthesizer = SpeechSynthClient()
    return await synthesizer.synth_to_file(text, output_path, voice=voice)


async def get_available_voices() -> List[str]:
    """Utility: Get list of available voices (hardcoded for now)"""
    return ["alloy", "verse", "coral", "amber", "sage"]


# Main example runner
async def run_audio_examples():
    """Run all audio processing examples"""
    print("🚀 Starting Audio Processing Examples\n")
    
    try:
        # Initialize examples
        examples = AudioProcessingExamples()
        await examples.initialize()
        
        # Run individual examples
        await example_transcribe_file()
        await example_transcribe_bytes()
        await example_speech_synthesis()
        await example_voice_comparison()
        await example_audio_formats()
        await example_transcription_formats()
        await example_batch_transcription()
        await example_integration_workflow()
        
        print("\n🎉 All audio processing examples completed!")
        
    except Exception as e:
        print(f"\n❌ Audio examples failed: {e}")


if __name__ == "__main__":
    asyncio.run(run_audio_examples())
