# DocX Jinja Template Linter

The Document Templating Service now includes a comprehensive linter for validating Jinja2 templates embedded in `.docx` files. This tool helps identify syntax errors, structural issues, and quality problems before processing templates.

## Features

### ✅ Comprehensive Validation
- **Jinja2 Syntax Checking**: Validates template syntax using the Jinja2 parser
- **Tag Matching**: Ensures all opening tags have corresponding closing tags (`{% if %}` → `{% endif %}`)
- **Nested Structure**: Validates proper nesting and detects excessive depth
- **Quality Analysis**: Provides template completeness scoring and best practice recommendations

### 🚀 Performance
- Fast processing with sub-second response times
- Memory-efficient document parsing
- Configurable validation depth

### 📊 Detailed Reporting
- Line-by-line error locations
- Contextual error messages with suggestions
- Processing statistics and metrics
- Template content extraction and preview

## API Endpoint

### `POST /api/v1/lint-docx-template`

Validates a DocX file containing Jinja2 templates.

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document` | File | Yes | DocX file to lint |
| `options` | JSON | No | Linting configuration options |

#### Linting Options

```json
{
  "verbose": false,
  "check_undefined_vars": true,
  "max_line_length": 200,
  "fail_on_warnings": false,
  "check_tag_matching": true,
  "check_nested_structure": true
}
```

#### Response Formats

The linter endpoint supports two response formats:

#### 📄 PDF Report (Default)
Professional linting report as a PDF document with:
- Document metadata and validation status
- Summary table with error/warning counts  
- Detailed error table with line numbers and descriptions
- Template preview with highlighted issues
- Formatted for easy reading and sharing

#### 📋 JSON Data (Optional)
Structured data response for programmatic use:

```json
{
  "success": true,
  "errors": [
    {
      "line_number": 15,
      "column": 8,
      "error_type": "unclosed_tag",
      "message": "Unclosed 'if' tag",
      "context": "{% if customer.vip %}",
      "tag_name": "if",
      "suggestion": "Add {% endif %} tag to close this block"
    }
  ],
  "warnings": [
    {
      "line_number": 23,
      "warning_type": "long_line",
      "message": "Line too long (250 > 200 characters)",
      "suggestion": "Consider breaking long lines for better readability"
    }
  ],
  "summary": {
    "total_errors": 1,
    "total_warnings": 1,
    "template_size": 1024,
    "lines_count": 42,
    "jinja_tags_count": 8,
    "completeness_score": 85.5,
    "processing_time_ms": 45.2
  },
  "template_preview": "Customer: {{ customer.name }}\\nCompany: {{ customer.company }}..."
}
```

## Error Types

### Syntax Errors
- **`syntax_error`**: Invalid Jinja2 syntax
- **`invalid_expression`**: Malformed template expressions

### Structure Errors  
- **`unclosed_tag`**: Missing closing tags ({% endif %}, {% endfor %}, etc.)
- **`mismatched_tag`**: Incorrect tag pairing
- **`nested_error`**: Excessive nesting depth (>10 levels)

### Document Errors
- **`document_error`**: File format or extraction issues
- **`undefined_variable`**: Template references undefined variables

## Warning Types

### Quality Warnings
- **`long_line`**: Lines exceeding configured length limit
- **`complex_expression`**: Overly complex template expressions
- **`suspicious_syntax`**: Potentially problematic syntax patterns
- **`unused_variable`**: Variables defined but not used

## Usage Examples

### Basic PDF Linting (Default)

```bash
# Returns PDF report
curl -X POST 'http://localhost:8000/api/v1/lint-docx-template' \
     -F 'document=@template.docx' \
     -o 'lint_report.pdf'
```

### JSON Response Option

```bash
# Returns JSON data
curl -X POST 'http://localhost:8000/api/v1/lint-docx-template' \
     -F 'document=@template.docx' \
     -F 'options={"response_format": "json", "verbose": true}' \
     | jq '.summary'
```

### Advanced PDF Options

```bash
# Detailed PDF report with custom settings
curl -X POST 'http://localhost:8000/api/v1/lint-docx-template' \
     -F 'document=@template.docx' \
     -F 'options={"verbose": true, "max_line_length": 100}' \
     -o 'detailed_lint_report.pdf'
```

### Python Usage

```python
import httpx
import asyncio

# Get PDF report (default)
async def get_pdf_report():
    async with httpx.AsyncClient() as client:
        with open('template.docx', 'rb') as f:
            files = {'document': ('template.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = await client.post(
                'http://localhost:8000/api/v1/lint-docx-template',
                files=files
            )
            
            if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
                with open('lint_report.pdf', 'wb') as f:
                    f.write(response.content)
                print("✅ PDF report saved as lint_report.pdf")
            else:
                print("❌ Failed to get PDF report")

# Get JSON data
async def get_json_data():
    async with httpx.AsyncClient() as client:
        with open('template.docx', 'rb') as f:
            files = {'document': ('template.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {'options': '{"response_format": "json", "verbose": true}'}
            
            response = await client.post(
                'http://localhost:8000/api/v1/lint-docx-template',
                files=files,
                data=data
            )
            result = response.json()
            
            if result['success']:
                print("✅ Template is valid!")
                print(f"Completeness score: {result['summary']['completeness_score']:.1f}%")
            else:
                print("❌ Template has errors:")
                for error in result['errors']:
                    print(f"  Line {error['line_number']}: {error['message']}")

# Run examples
asyncio.run(get_pdf_report())
asyncio.run(get_json_data())
```

## Supported Jinja Tags

### Paired Tags (require closing tags)
- `{% if %}` → `{% endif %}`
- `{% for %}` → `{% endfor %}`
- `{% with %}` → `{% endwith %}`
- `{% block %}` → `{% endblock %}`
- `{% macro %}` → `{% endmacro %}`
- `{% raw %}` → `{% endraw %}`
- `{% autoescape %}` → `{% endautoescape %}`

### Standalone Tags
- `{% else %}`, `{% elif %}`
- `{% include %}`, `{% import %}`, `{% from %}`
- `{% extends %}`
- `{% break %}`, `{% continue %}`

## Best Practices

### Template Structure
1. **Keep nesting shallow**: Avoid more than 5-6 levels of nesting
2. **Use descriptive variable names**: `{{ customer.company_name }}` vs `{{ c.n }}`
3. **Break complex expressions**: Use intermediate variables for readability
4. **Consistent formatting**: Follow consistent spacing and indentation

### Error Prevention
1. **Always close tags**: Every `{% if %}` needs `{% endif %}`
2. **Match tag pairs**: Don't mix `{% if %}` with `{% endfor %}`
3. **Test with data**: Validate templates with real data before deployment
4. **Use meaningful names**: Avoid generic variable names like `item`, `data`

### Performance Tips
1. **Minimize complexity**: Simple templates process faster
2. **Avoid deep nesting**: Excessive nesting impacts both linting and rendering
3. **Use includes**: Break large templates into smaller, reusable components
4. **Cache frequently used templates**: Store validated templates for reuse

## Testing

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run linter tests
pytest test_docx_linter.py -v

# Run with existing templates
python test_with_existing_templates.py

# Create demo templates and examples
python demo_linter.py
```

### Demo Templates

The service includes demo templates showcasing different error types:

- **`perfect.docx`**: Error-free template with best practices
- **`unclosed.docx`**: Template with unclosed tags
- **`mismatched.docx`**: Template with mismatched tag pairs  
- **`syntax_error.docx`**: Template with Jinja syntax errors
- **`nested.docx`**: Template with excessive nesting

## Integration

### CI/CD Pipeline

```yaml
# Example GitHub Actions workflow
name: Template Validation
on: [push, pull_request]

jobs:
  lint-templates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Lint templates
        run: |
          for template in templates/*.docx; do
            curl -X POST 'http://localhost:8000/api/v1/lint-docx-template' \
                 -F "document=@$template" | jq '.success'
          done
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
for file in $(git diff --cached --name-only | grep '\.docx$'); do
    result=$(curl -s -X POST 'http://localhost:8000/api/v1/lint-docx-template' \
                  -F "document=@$file" | jq '.success')
    if [ "$result" != "true" ]; then
        echo "❌ Template validation failed for $file"
        exit 1
    fi
done
```

## Troubleshooting

### Common Issues

1. **"No template content found"**
   - Ensure the DocX file contains text content
   - Check if the file is corrupted or empty

2. **"Syntax error: Unexpected end of template"**
   - Look for unclosed tags (missing `{% endif %}`, `{% endfor %}`, etc.)
   - Verify tag nesting is correct

3. **"File too large for linting"**
   - The service has a 10MB limit for linting
   - Consider breaking large templates into smaller files

4. **High processing time**
   - Complex templates with deep nesting take longer to process
   - Consider simplifying template structure

### Debug Mode

Enable verbose logging for detailed analysis:

```json
{
  "verbose": true,
  "check_undefined_vars": true,
  "max_line_length": 80
}
```

This provides:
- Full template content extraction
- Detailed error context
- Processing step breakdown
- Performance metrics

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`  
- **OpenAPI Spec**: `http://localhost:8000/openapi.json`

The interactive documentation provides request/response examples and allows testing the API directly from the browser.