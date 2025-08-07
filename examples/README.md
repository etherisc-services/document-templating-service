# Examples

This directory contains example scripts and demonstrations for the Document Template Processing Service.

## Available Examples

### DocX Linter Demo
- `demo_linter.py` - Interactive demonstration of the template linter
  - Creates sample templates with various error types
  - Shows linting results and error reporting
  - Provides curl examples for API testing
  - Demonstrates both valid and invalid templates

## Running Examples

### Linter Demo
```bash
cd examples
python3 demo_linter.py
```

This will:
1. Create demonstration template files in `temp/demo/`
2. Show linter service information
3. Display curl command examples
4. Provide Python usage examples

### Generated Demo Files

The linter demo creates:
- `perfect.docx` - Valid template with no errors
- `unclosed.docx` - Template with unclosed tags
- `mismatched.docx` - Template with mismatched tag pairs
- `syntax_error.docx` - Template with Jinja syntax errors
- `nested.docx` - Template with excessive nesting

## API Testing Examples

### Basic Template Processing
```bash
curl -X POST 'http://localhost:8000/api/v1/process-template-document' \
     -F 'file=@examples/temp/demo/perfect.docx' \
     -F 'data={"name": "John Doe", "amount": 100.50}'
```

### Template Linting Only
```bash
curl -X POST 'http://localhost:8000/api/v1/lint-docx-template' \
     -F 'document=@examples/temp/demo/unclosed.docx'
```

### Enhanced Mode with Linter Options
```bash
curl -X POST 'http://localhost:8000/api/v1/process-template-document' \
     -F 'file=@examples/temp/demo/perfect.docx' \
     -F 'request_data={
       "template_data": {"name": "John Doe"},
       "linter_options": {
         "verbose": true,
         "max_line_length": 100
       }
     }'
```

## Prerequisites

1. **Service Running**: Ensure the service is running on port 8000
2. **Dependencies**: Install requirements with `pip install -r requirements.txt`
3. **Gotenberg**: For full PDF generation, ensure Gotenberg is running

## Development

When adding new examples:
1. Create clear, documented scripts
2. Include error handling
3. Provide both success and failure scenarios
4. Add README documentation for usage