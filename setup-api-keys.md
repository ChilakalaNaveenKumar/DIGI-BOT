# 🔑 API Keys Setup Guide

## Required for Image Generation

To enable DALL-E 3 image generation, you need to configure your OpenAI API key.

## Setup Instructions

### Option 1: Environment Variable (Recommended)
```bash
export OPENAI_API_KEY="your_actual_openai_api_key_here"
```

### Option 2: Create .env file
Create a file named `.env` in the `digi-setu-demo/backend/` directory:
```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### Option 3: Set in terminal before running
```bash
cd digi-setu-demo/backend
OPENAI_API_KEY="your_key_here" python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Get Your OpenAI API Key

1. Go to https://platform.openai.com/account/api-keys
2. Create a new API key
3. Copy the key and use it in one of the options above

## Test the Setup

After setting up the API key, test with:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Generate an image of a cat"}],
    "provider": "openai",
    "model": "gpt-4o",
    "enableToolCalling": true,
    "tools": [{"name": "generateImage", "description": "Generate image", "parameters": {"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]}}]
  }'
```

You should see:
1. "Preparing to generate visual content..."
2. "Generating your image..."
3. Tool result with actual DALL-E 3 image URL
4. AI explanation of the generated image

## Current Status Without API Key

✅ **Working:** Tool calling detection, streaming, frontend integration
❌ **Not Working:** Actual image generation (falls back to placeholder)

Once you add the API key, everything will work perfectly! 🎯
