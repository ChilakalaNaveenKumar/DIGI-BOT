# AI Response Format Testing

## Testing Strategy
1. Test each model (OpenAI, Anthropic, Grok) with specific prompts
2. Capture exact raw responses 
3. Analyze patterns for reliable detection
4. Build simple detection logic based on real patterns

## Test Cases

### 1. Code Block Tests
**Prompt**: "Write a Python function to calculate fibonacci numbers"

#### OpenAI Response:
```
PATTERN: ```python
def fibonacci(n):
    # code here
```

DETECTION: Look for ```{language} at start of code block
```

#### Anthropic Response:
```
[TO BE FILLED]
```

#### Grok Response:
```
[TO BE FILLED]
```

### 2. JSON Output Tests  
**Prompt**: "Return user data as JSON with name, age, email fields"

#### OpenAI Response:
```
PATTERN: ```json
{
  "name": "John Doe",
  "age": 30,
  "email": "johndoe@example.com"
}
```

DETECTION: Look for ```json at start
```

#### Anthropic Response:
```
[TO BE FILLED]
```

#### Grok Response:
```
[TO BE FILLED]
```

### 3. Table Tests
**Prompt**: "Create a comparison table of programming languages"

#### OpenAI Response:
```
PATTERN: | Language | First Appeared | Typing |
         |----------|----------------|--------|
         | Python   | 1991           | Dynamic|

DETECTION: Look for | characters with --- separators (markdown table)
```

#### Anthropic Response:
```
[TO BE FILLED]
```

#### Grok Response:
```
[TO BE FILLED]
```

### 4. Diagram/Chart Tests
**Prompt**: "Create a simple flowchart for user registration process"

#### OpenAI Response:
```
[TO BE FILLED]
```

#### Anthropic Response:
```
[TO BE FILLED]
```

#### Grok Response:
```
[TO BE FILLED]
```

## Analysis Section

### Key Findings from OpenAI Testing:
1. **Code**: Always wrapped in ```{language} blocks
2. **JSON**: Always wrapped in ```json blocks  
3. **Tables**: Use markdown | syntax with --- separators
4. **Text**: Plain markdown format

### Universal Patterns:
- All special content uses markdown formatting
- Code blocks: ```{language}
- JSON blocks: ```json
- Tables: | column | syntax
- Everything else: plain text/markdown

## Detection Patterns

### Simple & Reliable Detection Logic:
```javascript
const detectContentType = (content) => {
  // Remove whitespace for testing
  const trimmed = content.trim()
  
  // Code detection: ```{language}
  if (trimmed.includes('```') && !trimmed.includes('```json')) {
    return 'code'
  }
  
  // JSON detection: ```json
  if (trimmed.includes('```json')) {
    return 'json'
  }
  
  // Table detection: | column | with --- separators
  if (trimmed.includes('|') && trimmed.includes('---')) {
    return 'table'
  }
  
  // Default: plain text/markdown
  return 'text'
}
```

### Why This Works:
1. **Simple**: Based on actual AI output patterns
2. **Reliable**: Uses consistent markdown formatting
3. **Fast**: Simple string checks
4. **Maintainable**: Easy to understand and modify
