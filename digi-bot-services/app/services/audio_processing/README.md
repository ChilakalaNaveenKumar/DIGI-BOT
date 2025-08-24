# Audio Processing Service

This package provides two lightweight clients for audio-related AI operations using OpenAI's stable audio endpoints:

## Components

### AudioTranscriberClient
Speech-to-text client with automatic model fallback.

**Features:**
- Automatic model fallback: `gpt-4o-mini-transcribe` → `whisper-1`
- Support for local files and in-memory bytes
- Multiple output formats: JSON, text, SRT, VTT, verbose JSON
- Language detection and custom prompts
- Common audio formats: MP3, MP4, M4A, WAV, WebM, OGG

**Usage:**
```python
from app.services.audio_processing import AudioTranscriberClient

# Transcribe local file
transcriber = AudioTranscriberClient()
result = await transcriber.transcribe_file(
    "meeting.mp3",
    language="en",
    response_format="json"
)
print(result["text"])

# Transcribe bytes (e.g., uploaded file)
with open("audio.wav", "rb") as f:
    audio_bytes = f.read()

result = await transcriber.transcribe_bytes(
    audio_bytes,
    filename="audio.wav",
    response_format="verbose_json"
)
```

### SpeechSynthClient
Text-to-speech client with multiple voice options.

**Features:**
- Multiple voices: alloy, verse, coral, amber, sage
- Various audio formats: MP3, WAV, FLAC, Opus, AAC
- Speed control (0.25-4.0x when supported)
- Direct file output or bytes return
- Stable `tts-1` model

**Usage:**
```python
from app.services.audio_processing import SpeechSynthClient

# Generate speech to file
synthesizer = SpeechSynthClient()
output_path = await synthesizer.synth_to_file(
    "Hello, this is a test of text-to-speech.",
    "output.mp3",
    voice="alloy",
    audio_format="mp3"
)

# Generate speech to bytes
audio_bytes = await synthesizer.synth_to_bytes(
    "This returns raw audio data.",
    voice="verse",
    audio_format="wav"
)
```

## Integration with Existing Services

These clients integrate seamlessly with your:
- File management service (for audio uploads/storage)
- Authentication system
- Conversation services (for voice interactions)
- Vision models (for multimodal experiences)

## Response Formats

### AudioTranscriberClient Formats
- `"json"`: `{"text": "transcribed content"}`
- `"text"`: Raw text string
- `"verbose_json"`: Includes segments and timestamps
- `"srt"`: SubRip subtitle format
- `"vtt"`: WebVTT subtitle format

### SpeechSynthClient Options
- **Voices**: `"alloy"`, `"verse"`, `"coral"`, `"amber"`, `"sage"`
- **Formats**: `"mp3"`, `"wav"`, `"flac"`, `"opus"`, `"aac"`
- **Speed**: 0.25 to 4.0 (when supported)

## Examples

### Basic Transcription
```python
# Simple file transcription
transcriber = AudioTranscriberClient()
result = await transcriber.transcribe_file("audio.mp3")
print(f"Transcription: {result['text']}")

# With language and custom prompt
result = await transcriber.transcribe_file(
    "meeting.mp3",
    language="en",
    prompt="This is a business meeting about quarterly results.",
    response_format="verbose_json"
)

# Access segments with timestamps
if hasattr(result, 'segments'):
    for segment in result.segments:
        print(f"[{segment.start:.2f}s - {segment.end:.2f}s]: {segment.text}")
```

### Voice Synthesis
```python
# Basic synthesis
synthesizer = SpeechSynthClient()
await synthesizer.synth_to_file(
    "Welcome to our service!",
    "welcome.mp3",
    voice="alloy"
)

# Different voices and formats
voices = ["alloy", "verse", "amber"]
for voice in voices:
    await synthesizer.synth_to_file(
        f"This is the {voice} voice.",
        f"voice_{voice}.wav",
        voice=voice,
        audio_format="wav"
    )
```

### Batch Processing
```python
# Batch transcription
transcriber = AudioTranscriberClient()
audio_files = ["file1.mp3", "file2.wav", "file3.m4a"]

results = []
for audio_file in audio_files:
    result = await transcriber.transcribe_file(audio_file)
    results.append({
        "file": audio_file,
        "text": result["text"],
        "length": len(result["text"])
    })

print(f"Processed {len(results)} files")
```

### Integration Workflow
```python
# Complete audio processing workflow
async def process_audio_message(audio_file_path: str) -> str:
    # Step 1: Transcribe user audio
    transcriber = AudioTranscriberClient()
    transcription = await transcriber.transcribe_file(audio_file_path)
    user_text = transcription["text"]
    
    # Step 2: Process with AI (your existing logic)
    ai_response = await your_ai_service.process(user_text)
    
    # Step 3: Convert response to speech
    synthesizer = SpeechSynthClient()
    response_audio = await synthesizer.synth_to_file(
        ai_response,
        "response.mp3",
        voice="alloy"
    )
    
    return response_audio

# Usage
response_file = await process_audio_message("user_question.mp3")
```

### Error Handling
```python
async def safe_transcription(audio_path: str):
    try:
        transcriber = AudioTranscriberClient()
        result = await transcriber.transcribe_file(audio_path)
        return result["text"]
    except FileNotFoundError:
        print(f"Audio file not found: {audio_path}")
        return None
    except Exception as e:
        print(f"Transcription failed: {e}")
        return None

async def safe_synthesis(text: str, output_path: str):
    try:
        synthesizer = SpeechSynthClient()
        return await synthesizer.synth_to_file(text, output_path)
    except Exception as e:
        print(f"Speech synthesis failed: {e}")
        return None
```

## Model Fallback

The AudioTranscriberClient automatically handles model availability:

1. **Primary**: `gpt-4o-mini-transcribe` (fast, accurate)
2. **Fallback**: `whisper-1` (widely available)

```python
# The client will automatically use the best available model
transcriber = AudioTranscriberClient()
await transcriber.initialize()  # Checks model availability

# Or specify a preferred model
transcriber = AudioTranscriberClient(model="whisper-1")
```

## File Format Support

### Input Formats (Transcription)
- MP3, MP4, M4A
- WAV, WebM, OGG
- Most common audio/video formats

### Output Formats (Synthesis)
- **MP3**: Small file size, good quality
- **WAV**: Uncompressed, highest quality
- **FLAC**: Lossless compression
- **Opus**: Optimized for speech
- **AAC**: Good compression, quality

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for OpenAI API access

### Default Settings
- **STT Model**: `gpt-4o-mini-transcribe` with `whisper-1` fallback
- **TTS Model**: `tts-1`
- **Default Voice**: `alloy`
- **Default Format**: `mp3`

## Performance Tips

1. **Large Files**: Use `transcribe_file()` for better streaming
2. **Batch Processing**: Process multiple files concurrently
3. **Format Selection**: Use MP3 for smaller files, WAV for quality
4. **Language Hints**: Specify language for better accuracy
5. **Custom Prompts**: Use prompts to improve domain-specific transcription

## Testing

Run the examples:

```bash
# Audio processing examples
python -c "import asyncio; from app.services.audio_processing.examples import run_audio_examples; asyncio.run(run_audio_examples())"

# Quick test
python -c "
import asyncio
from app.services.audio_processing import SpeechSynthClient

async def test():
    tts = SpeechSynthClient()
    await tts.synth_to_file('Hello world!', 'test.mp3')
    print('Generated test.mp3')

asyncio.run(test())
"
```
