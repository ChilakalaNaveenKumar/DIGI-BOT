# Token Budget Cheat Sheet 🚀

Quick reference for OpenAI model limits and costs (Updated: August 2025)

## 📊 Model Comparison Table

| Model | Context | Output | Vision | Tools | Reasoning | Cost/1k (In/Out) | Best For |
|-------|---------|--------|--------|-------|-----------|------------------|----------|
| **gpt-4o** | 128k | 16k | ✅ | ✅ | ❌ | $2.50/$10.00 | Multimodal, tools, general |
| **gpt-4o-mini** | 128k | 16k | ✅ | ✅ | ❌ | $0.15/$0.60 | Fast, cheap, capable |
| **gpt-4.1** | 128k | 16k | ✅ | ✅ | ✅ | $3.00/$12.00 | Enhanced reasoning |
| **gpt-4.5** | 200k | 16k | ✅ | ✅ | ✅ | $5.00/$15.00 | Large context |
| **o1-preview** | 200k | 16k | ❌ | ❌ | ✅ | $15.00/$60.00 | Advanced reasoning |
| **o1-mini** | 128k | 8k | ❌ | ❌ | ✅ | $3.00/$12.00 | Reasoning, cheaper |
| **gpt-3.5-turbo** | 16k | 4k | ❌ | ✅ | ❌ | $0.50/$1.50 | Legacy, phasing out |

## 🎯 Safe Token Limits by Use Case

### Chart Matching & Analysis
```python
model = "gpt-4o"
max_output_tokens = 16000  # Full capacity
context_window = 128000    # 128k input
```

### Vision Analysis  
```python
model = "gpt-4o"
max_output_tokens = 16000
# Each image ≈ 750-1500 tokens
# 512x512 image = ~750 tokens
# 1024x1024 image = ~1500 tokens
```

### Document Analysis (Large)
```python
model = "gpt-4.5"  # Largest context
max_output_tokens = 16000
context_window = 200000    # 200k input
```

### Reasoning Tasks
```python
model = "o1-mini"          # Cost-effective reasoning
max_output_tokens = 8000   # Lower limit for o1 models
context_window = 128000
```

### Simple Chat/API
```python
model = "gpt-4o-mini"      # Fast and cheap
max_output_tokens = 16000
context_window = 128000
```

## 🔧 Audio Models (Not Token-Based)

| Model | Type | Max File | Cost | Notes |
|-------|------|----------|------|-------|
| **whisper-1** | STT | 25MB | $0.006/min | Widely available |
| **gpt-4o-mini-transcribe** | STT | 25MB | $0.004/min | Faster, newer |
| **tts-1** | TTS | - | $0.015/1k chars | Standard quality |
| **tts-1-hd** | TTS | - | $0.030/1k chars | Higher quality |

## 🖼️ Image Models

| Model | Type | Sizes | Cost | Max/Request |
|-------|------|-------|------|-------------|
| **dall-e-3** | Gen | 1024x1024, 1792x1024 | $0.040-$0.080 | 1 |
| **gpt-image-1** | Gen | 512x512 to 2048x2048 | $0.020-$0.080 | 4 |
| **dall-e-2** | Gen | 256x256 to 1024x1024 | $0.016-$0.020 | 10 |

## ⚡ Quick Configuration Examples

### High-Performance Setup
```python
# For production workloads
model = "gpt-4o"
max_output_tokens = 16000
tools = ["function_calling", "web_search", "file_search"]
```

### Cost-Optimized Setup  
```python
# For development/testing
model = "gpt-4o-mini"
max_output_tokens = 8000  # Reduce for cost savings
tools = ["function_calling"]
```

### Reasoning-Heavy Setup
```python
# For complex problem solving
model = "o1-mini"
max_output_tokens = 8000
# Note: o1 models don't support tools
```

### Large Document Setup
```python
# For processing large documents
model = "gpt-4.5"
max_output_tokens = 16000
context_window = 200000  # Can handle very large inputs
```

## 🛠️ Tool Support by Model

| Tool Type | Supported Models |
|-----------|------------------|
| **Function Calling** | gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.5, gpt-3.5-turbo |
| **Web Search** | gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.5 |
| **File Search** | gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.5 |
| **Code Interpreter** | gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.5 |
| **Vision** | gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.5 |

## 💰 Cost Estimation Examples

### Typical Chart Analysis
```
Input: 2k tokens (query + docs)
Output: 1k tokens (format response)
Model: gpt-4o
Cost: (2 × $2.50 + 1 × $10.00) / 1000 = $0.015
```

### Vision Analysis
```
Input: 1k tokens (prompt) + 750 tokens (image) = 1.75k tokens
Output: 500 tokens (description)
Model: gpt-4o  
Cost: (1.75 × $2.50 + 0.5 × $10.00) / 1000 = $0.009
```

### Large Document Processing
```
Input: 50k tokens (large document)
Output: 2k tokens (summary)
Model: gpt-4.5
Cost: (50 × $5.00 + 2 × $15.00) / 1000 = $0.280
```

## 🚨 Important Limits & Guidelines

### Context Window Management
- Always leave 1000+ tokens safety margin
- Monitor input + output total
- Use `get_safe_output_tokens()` helper

### Image Token Calculation
- 512×512 image ≈ 750 tokens
- 1024×1024 image ≈ 1500 tokens  
- Multiple images add up quickly

### File Size Limits
- Audio files: 25MB max
- Vector store files: 512MB max per file
- Image files: Reasonable sizes (no hard limit specified)

### Rate Limits
- Vary by model and tier
- Monitor usage in OpenAI dashboard
- Implement exponential backoff

## 🎯 Recommended Model Selection

```python
# Use this decision tree:

if needs_reasoning:
    model = "o1-mini"  # Cost-effective reasoning
elif needs_vision:
    model = "gpt-4o"   # Best multimodal
elif needs_large_context:
    model = "gpt-4.5"  # Largest context window  
elif budget_conscious:
    model = "gpt-4o-mini"  # Fast and cheap
else:
    model = "gpt-4o"   # General purpose
```

## 📝 Code Templates

### Safe Token Calculation
```python
from app.services.model_config import get_safe_output_tokens

input_tokens = len(prompt.split()) * 1.3  # Rough estimate
safe_output = get_safe_output_tokens("gpt-4o", input_tokens)
```

### Cost Estimation
```python
from app.services.model_config import estimate_cost

cost = estimate_cost("gpt-4o", input_tokens=2000, output_tokens=1000)
print(f"Estimated cost: ${cost:.4f}")
```

### Model Selection
```python
from app.services.model_config import get_best_model_for_task

model = get_best_model_for_task(
    task_type="vision",
    needs_vision=True,
    max_budget_per_1k_tokens=5.00
)
```

---

💡 **Pro Tips:**
- Use `gpt-4o-mini` for development and testing
- Switch to `gpt-4o` for production
- Use `o1-mini` only when you need reasoning
- Monitor costs with the `estimate_cost()` function
- Always set appropriate `max_output_tokens` limits
