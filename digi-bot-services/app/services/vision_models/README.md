# Vision Models Service

This package provides two lightweight clients for vision-related AI operations using OpenAI's APIs:

## Components

### VisionAnalyzerClient
Analyze images using OpenAI's vision models via the Responses API.

**Features:**
- Stream analysis results in real-time
- Support for both URL-based and uploaded file images
- Uses officially accepted content types: `input_text` and `input_image`
- Compatible with existing event loop infrastructure

**Usage:**
```python
from app.services.vision_models import VisionAnalyzerClient

# Analyze image from URL
analyzer = VisionAnalyzerClient(model="gpt-4o")
async for event in analyzer.analyze_url(
    "https://example.com/image.jpg",
    prompt="Describe this image and identify any objects."
):
    if event["type"] == "content":
        print(event["content"], end="")
```

### ImageGeneratorClient
Generate images from text prompts using OpenAI's image generation models.

**Features:**
- Generate images in various sizes
- Returns base64 encoded images for easy storage
- Support for background options (when available)
- Multiple image generation in single request

**Usage:**
```python
from app.services.vision_models import ImageGeneratorClient
import base64

# Generate image
generator = ImageGeneratorClient(model="gpt-image-1")
images = await generator.generate(
    "A modern office workspace with plants",
    size="1024x1024",
    n=1
)

# Save to disk
with open("generated_image.png", "wb") as f:
    f.write(base64.b64decode(images[0]["b64"]))
```

## Integration with Existing Services

These clients are designed to work seamlessly with your existing:
- Authentication system
- File management service
- OpenAI provider infrastructure
- Chart matcher and conversation services

## Event Types

### VisionAnalyzerClient Events
- `{"type": "content", "content": str}` - Streaming analysis content
- `{"type": "completion", "finish_reason": "done"}` - Analysis complete
- `{"type": "error", "error": str}` - Error occurred

### ImageGeneratorClient Response
Returns list of dictionaries:
```python
[{
    "b64": str,  # Base64 encoded image
    "revised_prompt": str  # OpenAI's revised version of your prompt (optional)
}]
```

## Configuration

Both clients accept:
- `api_key`: OpenAI API key (defaults to `OPENAI_API_KEY` environment variable)
- `model`: Model to use (defaults: "gpt-4o" for vision, "gpt-image-1" for generation)

## Error Handling

All clients include proper error handling and will yield error events rather than raising exceptions during streaming operations.
