# Chart Matcher Service

Intelligent chart format matching service that analyzes queries and returns appropriate chart format templates from documentation.

## Overview

The Chart Matcher service uses OpenAI's advanced models with vector store search to:
- Match user queries to appropriate chart formats
- Return exact format templates from documentation
- Manage chart format documentation via vector store
- Provide streaming and non-streaming analysis options

## Components

### ChartMatcherClient
Main client for intelligent format matching.

**Features:**
- Stream-based format matching with real-time results
- Quick non-streaming matching for simple use cases
- Automatic model fallback (gpt-4.5 → gpt-4o)
- Integration with vector store for documentation lookup

**Usage:**
```python
from app.services.chart_matcher import ChartMatcherClient

# Initialize client
matcher = ChartMatcherClient()

# Quick format matching
result = await matcher.quick_match("Show sales data as bar chart")
if matcher.has_match(result):
    print(f"Format found: {result}")

# Streaming analysis
async for event in matcher.analyze("Create pie chart for market share"):
    if event["type"] == "content":
        print(event["content"], end="")
```

### VectorStoreManager
Manages chart format documentation in OpenAI vector store.

**Features:**
- Automatic vector store initialization
- Document upload and management
- File existence checking and updates
- Direct vector store querying

**Usage:**
```python
from app.services.chart_matcher import VectorStoreManager

# Initialize vector store
vector_manager = VectorStoreManager()
await vector_manager.initialize()

# Upload documentation
await vector_manager.insert_or_update_file(
    "path/to/chart_formats.md", 
    "chart_formats.md"
)

# Query documentation
result = await vector_manager.query_vector_store("Find bar chart formats")
```

## Chart Format Documentation

The service includes comprehensive documentation for:

### Chart.js Formats
- **Pie Charts**: Percentages, proportions, market share
- **Bar Charts**: Category comparisons, regional data
- **Line Charts**: Trends over time, growth metrics
- **Scatter Charts**: Correlations, data relationships

### Data Tables
- **Structured Data**: Multi-attribute datasets
- **Performance Metrics**: Detailed comparisons
- **Financial Data**: Exact values and calculations

## Examples

### Basic Format Matching
```python
from app.services.chart_matcher import ChartMatcherClient

matcher = ChartMatcherClient()

# Test various queries
queries = [
    "Show quarterly sales as bar chart",
    "Create pie chart for browser usage",
    "Display revenue trends over time",
    "Make data table with employee metrics"
]

for query in queries:
    result = await matcher.quick_match(query)
    if matcher.has_match(result):
        print(f"✅ Found format for: {query}")
        print(f"Format: {result[:100]}...")
    else:
        print(f"❌ No format found for: {query}")
```

### Streaming Analysis
```python
async def stream_analysis(query: str):
    matcher = ChartMatcherClient()
    
    print(f"Analyzing: {query}")
    full_response = ""
    
    async for event in matcher.analyze(query):
        if event["type"] == "content":
            full_response += event["content"]
            print(event["content"], end="")
        elif event["type"] == "error":
            print(f"Error: {event['error']}")
            return None
        elif event["type"] == "completion":
            print("\n--- Analysis complete ---")
            break
    
    return full_response

# Usage
result = await stream_analysis("Create bar chart showing regional sales")
```

### Vector Store Management
```python
from app.services.chart_matcher import VectorStoreManager

async def setup_documentation():
    vector_manager = VectorStoreManager()
    await vector_manager.initialize()
    
    # List current files
    files = await vector_manager.list_files()
    print(f"Current files: {len(files)}")
    
    # Ensure documentation exists
    docs_folder = vector_manager.get_documents_folder()
    chart_doc = os.path.join(docs_folder, "chartjs_markdown_format_v1.md")
    
    if os.path.exists(chart_doc):
        await vector_manager.ensure_file_exists(chart_doc, "chartjs_markdown_format_v1.md")
        print("✅ Chart documentation ready")
    
    # Query the documentation
    result = await vector_manager.query_vector_store("Find formats for sales data")
    print(f"Query result: {result[:200]}...")

await setup_documentation()
```

### Custom Documentation
```python
# Use custom documentation instead of vector store
custom_docs = """
# Custom Chart Formats

## Heatmap Format
Use for: Correlation matrices, time-based patterns

Format:
```
:::heatmap-chart
title: Sales Heatmap by Region and Month
data: [
  {"x": "Jan", "y": "North", "value": 100},
  {"x": "Jan", "y": "South", "value": 150}
]
:::
```
"""

matcher = ChartMatcherClient()
result = await matcher.quick_match(
    "Show sales patterns as heatmap", 
    documentation=custom_docs
)

if matcher.has_match(result):
    print("Custom format matched!")
```

### Batch Processing
```python
async def batch_process_queries(queries: List[str]):
    matcher = ChartMatcherClient()
    results = []
    
    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] Processing: {query}")
        
        result = await matcher.quick_match(query)
        has_match = matcher.has_match(result)
        
        results.append({
            "query": query,
            "has_match": has_match,
            "format": result if has_match else None
        })
        
        print(f"  {'✅' if has_match else '❌'} {'Match' if has_match else 'No match'}")
    
    return results

# Usage
queries = [
    "Show revenue by quarter",
    "Display customer satisfaction scores", 
    "Create inventory data table"
]

results = await batch_process_queries(queries)
```

## Integration with Vision Models

The Chart Matcher works seamlessly with Vision Models for complete chart analysis workflows:

```python
from app.services.vision_models import VisionAnalyzerClient
from app.services.chart_matcher import ChartMatcherClient

async def analyze_and_recreate_chart(image_url: str):
    # Step 1: Analyze chart image
    vision = VisionAnalyzerClient()
    analysis = ""
    
    async for event in vision.analyze_url(
        image_url, 
        "Analyze this chart and extract data points"
    ):
        if event["type"] == "content":
            analysis += event["content"]
    
    print(f"Chart analysis: {analysis}")
    
    # Step 2: Find matching format
    matcher = ChartMatcherClient()
    format_query = f"Create chart format for: {analysis}"
    
    format_result = await matcher.quick_match(format_query)
    
    if matcher.has_match(format_result):
        print("✅ Found matching format for recreation!")
        return format_result
    else:
        print("❌ No matching format found")
        return None

# Usage
chart_format = await analyze_and_recreate_chart("https://example.com/chart.png")
```

## Error Handling

The service includes comprehensive error handling:

```python
async def safe_format_matching(query: str):
    try:
        matcher = ChartMatcherClient()
        
        # Stream with error handling
        async for event in matcher.analyze(query):
            if event["type"] == "content":
                print(event["content"], end="")
            elif event["type"] == "error":
                print(f"Stream error: {event['error']}")
                return None
            elif event["type"] == "completion":
                print("\nCompleted successfully")
                break
                
    except Exception as e:
        print(f"Exception: {e}")
        return None
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for OpenAI API access

### Model Configuration
- Primary model: `gpt-4.5` (with automatic fallback to `gpt-4o`)
- Vector store model: `gpt-4o` for file search
- Max output tokens: 4000 for format matching

### File Paths
- Documents folder: `app/services/chart_matcher/documents/`
- Cache file: `.vector_store_cache.json`

## Testing

Run the examples and tests:

```bash
# Simple test
python test_chart_matcher_examples.py

# Full examples
python -m app.services.chart_matcher.examples

# Integration examples  
python -m app.services.integration_examples
```

## Available Chart Formats

The service recognizes and provides formats for:

1. **Pie Charts** (`:::pie-chart`)
2. **Bar Charts** (`:::bar-chart`) 
3. **Line Charts** (`:::line-chart`)
4. **Data Tables** (`:::data-table`)
5. **Scatter Charts** (`:::scatter-chart`)
6. **Area Charts** (`:::area-chart`)
7. **Doughnut Charts** (`:::doughnut-chart`)

Each format includes proper data structure, styling options, and usage guidelines.
