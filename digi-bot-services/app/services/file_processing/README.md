# File Processing Service

This package provides comprehensive file analysis and vector store management capabilities for document processing workflows.

## Components

### FileAnalyzer
Extract text content from various document types with configurable limits and safety caps.

**Features:**
- **25+ file types**: Text, documents, code, images (with OCR)
- **Configurable limits**: File size, page counts, cell limits
- **Safe processing**: Hard limits prevent resource exhaustion
- **Structured results**: Consistent metadata and error handling
- **Optional OCR**: Extract text from images when enabled

**Supported File Types:**
- **Text**: .txt, .md, .csv, .tsv, .json, .log
- **Documents**: .pdf, .docx, .pptx, .xlsx
- **Code**: .py, .js, .ts, .html, .css, .java, .c, .cpp, .go, .rs, .sh, .sql, .yaml, .yml, .xml
- **Images**: .png, .jpg, .jpeg, .webp (with optional OCR)

### VectorStoreSaver
Manage files in OpenAI vector stores with automatic expiry and deduplication.

**Features:**
- **Automatic expiry**: 2-day default with configurable duration
- **Smart deduplication**: Avoid duplicate uploads by filename + size
- **Store management**: Find/create stores by name or ID
- **Validation integration**: Optional FileAnalyzer validation
- **Idempotent operations**: Safe to call repeatedly

## Usage

### Basic File Analysis
```python
from app.services.file_processing import FileAnalyzer, AnalyzeLimits

# Default limits (25MB, 1000 PDF pages, etc.)
analyzer = FileAnalyzer()
result = analyzer.analyze_path("document.pdf")

if result.ok:
    print(f"Extracted text: {result.text}")
    print(f"Metadata: {result.meta}")
    if result.warning:
        print(f"Warning: {result.warning}")
else:
    print(f"Error: {result.error}")
```

### Custom Limits
```python
# Custom processing limits
limits = AnalyzeLimits(
    max_bytes=10 * 1024 * 1024,  # 10MB limit
    max_pdf_pages=100,           # 100 page limit
    max_slides=50,               # 50 slide limit
    max_cells=50_000,            # 50k cell limit
    ocr_enabled=True             # Enable OCR for images
)

analyzer = FileAnalyzer(limits=limits)
result = analyzer.analyze_path("large_document.pdf")
```

### Vector Store Management
```python
from app.services.file_processing import VectorStoreSaver

# Upload file to vector store with validation
saver = VectorStoreSaver()
vector_store_id = await saver.upload_if_needed(
    "document.pdf",
    vector_store_name="My Document Store",
    expires_days=7,
    validate_with_analyzer=True
)

print(f"Stored in vector store: {vector_store_id}")
```

### Batch Processing
```python
# Process multiple files
analyzer = FileAnalyzer()
files = ["doc1.pdf", "data.xlsx", "code.py", "notes.md"]

results = []
for file_path in files:
    result = analyzer.analyze_path(file_path)
    results.append({
        "file": file_path,
        "success": result.ok,
        "text_length": len(result.text) if result.ok else 0,
        "error": result.error if not result.ok else None
    })

successful = sum(1 for r in results if r["success"])
print(f"Processed {successful}/{len(files)} files successfully")
```

## File Type Details

### Text Files (.txt, .md, .log, etc.)
- Direct UTF-8 reading with error handling
- Preserves original formatting
- No size limits beyond global max_bytes

### Data Files (.csv, .tsv, .json)
- **CSV/TSV**: Converted to tab-separated format
- **JSON**: Pretty-printed with 2-space indentation
- Handles encoding issues gracefully

### Documents (.pdf, .docx, .pptx, .xlsx)
- **PDF**: Page-by-page text extraction with page limits
- **DOCX**: Paragraph extraction from Word documents
- **PPTX**: Slide-by-slide text extraction with slide limits
- **XLSX**: Sheet-by-sheet cell extraction with cell limits

### Code Files (.py, .js, .ts, etc.)
- Treated as plain text files
- Preserves syntax and formatting
- Supports 15+ programming languages

### Images (.png, .jpg, .jpeg, .webp)
- **OCR disabled by default** (returns empty text with warning)
- **OCR enabled**: Uses Tesseract for text extraction
- Requires `pytesseract` and `Pillow` packages

## Configuration

### Default Limits
```python
AnalyzeLimits(
    max_bytes=25 * 1024 * 1024,  # 25 MB
    max_pdf_pages=1000,          # 1000 pages
    max_slides=1000,             # 1000 slides  
    max_cells=200_000,           # 200k cells
    ocr_enabled=False            # OCR disabled
)
```

### Environment Variables
- `OPENAI_API_KEY`: Required for vector store operations

### Optional Dependencies
Install based on file types you need:
```bash
# PDF support
pip install pypdf

# Office documents
pip install python-docx python-pptx openpyxl

# Image OCR (optional)
pip install pillow pytesseract
brew install tesseract  # macOS
```

## Examples

### Complete Workflow
```python
from app.services.file_processing import FileAnalyzer, VectorStoreSaver

async def process_document(file_path: str):
    # Step 1: Analyze file
    analyzer = FileAnalyzer()
    result = analyzer.analyze_path(file_path)
    
    if not result.ok:
        print(f"Analysis failed: {result.error}")
        return None
    
    print(f"Extracted {len(result.text)} characters")
    
    # Step 2: Upload to vector store
    saver = VectorStoreSaver()
    vector_store_id = await saver.upload_if_needed(
        file_path,
        vector_store_name="Document Processing Store",
        expires_days=3,
        validate_with_analyzer=True
    )
    
    return {
        "text": result.text,
        "metadata": result.meta,
        "vector_store_id": vector_store_id
    }

# Usage
result = await process_document("important_document.pdf")
```

### Error Handling
```python
def safe_analyze(file_path: str):
    try:
        analyzer = FileAnalyzer()
        result = analyzer.analyze_path(file_path)
        
        if result.ok:
            return result.text
        else:
            print(f"Analysis error: {result.error}")
            return None
            
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

text = safe_analyze("document.pdf")
```

### Custom File Type Handling
```python
from app.services.file_processing import SUPPORTED_EXTS

def check_file_support(file_path: str) -> bool:
    ext = os.path.splitext(file_path)[1].lower()
    return ext in SUPPORTED_EXTS

# Check before processing
if check_file_support("document.xyz"):
    result = analyzer.analyze_path("document.xyz")
else:
    print("Unsupported file type")
```

### Vector Store Deduplication
```python
# First upload
vector_store_id = await saver.upload_if_needed("document.pdf")
print("First upload completed")

# Second upload (will be skipped due to deduplication)
vector_store_id = await saver.upload_if_needed("document.pdf")
print("Second upload skipped (duplicate detected)")
```

## Integration with Other Services

### With Chart Matcher
```python
# Extract text from document, then find chart formats
result = analyzer.analyze_path("chart_documentation.md")
if result.ok:
    from app.services.chart_matcher import ChartMatcherClient
    matcher = ChartMatcherClient()
    
    # Use extracted text as documentation
    format_result = await matcher.quick_match(
        "Create bar chart for sales data",
        documentation=result.text
    )
```

### With Vision Models
```python
# Process document, then generate visual representation
result = analyzer.analyze_path("data_report.xlsx")
if result.ok:
    from app.services.vision_models import ImageGeneratorClient
    generator = ImageGeneratorClient()
    
    # Generate chart based on extracted data
    images = await generator.generate(
        f"Create a professional chart visualization for: {result.text[:500]}",
        size="1024x1024"
    )
```

### With Audio Processing
```python
# Convert document to speech
result = analyzer.analyze_path("article.md")
if result.ok:
    from app.services.audio_processing import SpeechSynthClient
    tts = SpeechSynthClient()
    
    # Convert to audio (handle length limits)
    text_chunks = [result.text[i:i+4000] for i in range(0, len(result.text), 4000)]
    
    for i, chunk in enumerate(text_chunks):
        await tts.synth_to_file(chunk, f"article_part_{i+1}.mp3")
```

## Performance Tips

1. **File Size**: Keep files under 25MB for optimal processing
2. **PDF Pages**: Large PDFs are truncated at 1000 pages by default
3. **Spreadsheets**: Excel files stop at 200k cells to prevent memory issues
4. **OCR**: Enable only when needed (slower processing)
5. **Batch Processing**: Process files concurrently for better throughput
6. **Vector Stores**: Use deduplication to avoid redundant uploads

## Testing

Run the examples:
```bash
# Full examples
python -c "import asyncio; from app.services.file_processing.examples import run_file_processing_examples; asyncio.run(run_file_processing_examples())"

# Quick test
python -c "
from app.services.file_processing import FileAnalyzer
import tempfile, os

# Create test file
with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
    f.write('Hello, file processing!')
    test_file = f.name

# Analyze
analyzer = FileAnalyzer()
result = analyzer.analyze_path(test_file)

print(f'Success: {result.ok}')
print(f'Text: {result.text}')
print(f'Meta: {result.meta}')

# Cleanup
os.unlink(test_file)
"
```

## Troubleshooting

### Common Issues

**"pypdf not installed"**
```bash
pip install pypdf
```

**"python-docx not installed"**
```bash
pip install python-docx python-pptx openpyxl
```

**"OCR not available"**
```bash
pip install pillow pytesseract
# macOS:
brew install tesseract
# Ubuntu:
sudo apt-get install tesseract-ocr
```

**"File too large"**
- Increase `max_bytes` in AnalyzeLimits
- Or split large files into smaller chunks

**"Vector store upload failed"**
- Check `OPENAI_API_KEY` environment variable
- Verify file passes FileAnalyzer validation
- Check OpenAI API quotas and limits
