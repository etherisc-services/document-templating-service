---
layout: default
title: Error Handling
nav_order: 6
description: "Comprehensive error handling guide with HTTP status codes, error types, and debugging tips."
---

# Error Handling
{: .no_toc }

Comprehensive guide to understanding and handling errors in the Document Template Processing Service.

<details open markdown="block">
  <summary>
    Table of Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

---

## HTTP Status Codes

| Status Code | Description | When It Occurs |
|-------------|-------------|----------------|
| **200** | Success | Document processed successfully |
| **400** | Bad Request | Invalid file type, malformed data, or template errors |
| **422** | Unprocessable Entity | Invalid JSON structure or validation errors |
| **500** | Internal Server Error | Service errors, Gotenberg issues, or unexpected failures |

## Error Response Format

All errors return a structured JSON response:

```json
{
  "message": "Human-readable error description",
  "error_type": "machine_readable_error_category",
  "details": {
    "field": "additional_context",
    "suggestion": "how_to_fix_the_issue"
  }
}
```

## Error Categories

### File Processing Errors

#### invalid_file_type
**Cause:** Non-.docx file uploaded  
**Status:** 400

```json
{
  "message": "Invalid file type. Only .docx files are supported",
  "error_type": "invalid_file_type",
  "details": {
    "provided_filename": "document.pdf",
    "supported_types": [".docx"],
    "requirement": "Upload a Microsoft Word .docx file"
  }
}
```

#### missing_file
**Cause:** No file provided in request  
**Status:** 400

```json
{
  "message": "No file uploaded",
  "error_type": "missing_file",
  "details": {
    "requirement": "A valid .docx file must be uploaded"
  }
}
```

#### file_upload_error
**Cause:** File system or I/O errors during upload  
**Status:** 500

```json
{
  "message": "Failed to save uploaded file: [details]",
  "error_type": "file_upload_error",
  "details": {
    "io_error": "Permission denied",
    "suggestion": "Check file permissions and disk space"
  }
}
```

#### image_processing_error
**Cause:** Invalid image data or processing failures (Enhanced Mode only)  
**Status:** 400

```json
{
  "message": "Failed to process image 'company_logo': Invalid base64 data",
  "error_type": "image_processing_error",
  "details": {
    "image_name": "company_logo",
    "error": "Invalid base64 data",
    "suggestion": "Ensure image data is valid base64 encoded PNG"
  }
}
```

### Template Processing Errors

#### missing_template_data
**Cause:** No data parameter provided  
**Status:** 400

```json
{
  "message": "No template data provided. Use either 'data' parameter (legacy) or 'request_data' parameter (enhanced with images)",
  "error_type": "missing_template_data",
  "details": {
    "requirement": "Provide either 'data' (JSON object) or 'request_data' (JSON string)",
    "examples": {
      "legacy": "{\"name\": \"John Doe\"}",
      "enhanced": "{\"template_data\": {\"name\": \"John Doe\"}, \"images\": {}}"
    }
  }
}
```

#### invalid_json
**Cause:** Malformed JSON in data or request_data  
**Status:** 400

```json
{
  "message": "Invalid JSON data: Expecting ',' delimiter: line 2 column 15 (char 16)",
  "error_type": "invalid_json",
  "details": {
    "json_error": "Expecting ',' delimiter: line 2 column 15 (char 16)",
    "line": 2,
    "column": 15,
    "suggestion": "Ensure the data parameter contains valid JSON"
  }
}
```

#### invalid_json_data
**Cause:** Non-serializable data types  
**Status:** 422

```json
{
  "message": "Invalid template data: Object of type datetime is not JSON serializable",
  "error_type": "invalid_json_data",
  "details": {
    "json_error": "Object of type datetime is not JSON serializable",
    "data_type": "dict",
    "suggestion": "Ensure all data values are JSON serializable (strings, numbers, booleans, lists, dicts)"
  }
}
```

#### template_syntax_error
**Cause:** Invalid Jinja2 template syntax  
**Status:** 400

```json
{
  "message": "Template syntax error in template.docx: unexpected 'end of template'",
  "error_type": "template_syntax_error",
  "details": {
    "file": "template.docx",
    "syntax_error": "unexpected 'end of template'",
    "line": 15,
    "suggestion": "Check template for missing {% raw %}{% endif %}{% endraw %} or {% raw %}{% endfor %}{% endraw %} tags"
  }
}
```

#### template_undefined_error
**Cause:** Template references undefined variable  
**Status:** 400

```json
{
  "message": "Template error in template.docx: 'customer_namme' is undefined",
  "error_type": "template_undefined_error",
  "details": {
    "file": "template.docx",
    "undefined_variable": "customer_namme",
    "suggestion": "Ensure all template variables are provided in the data or check for typos"
  }
}
```

#### template_runtime_error
**Cause:** Runtime errors during template processing (type errors, division by zero, etc.)  
**Status:** 400

```json
{
  "message": "Template runtime error in template.docx: unsupported operand type(s) for /: 'str' and 'int'",
  "error_type": "template_runtime_error",
  "details": {
    "file": "template.docx",
    "runtime_error": "unsupported operand type(s) for /: 'str' and 'int'",
    "suggestion": "Check data types in template expressions and ensure mathematical operations use numbers"
  }
}
```

#### template_document_corruption
**Cause:** Corrupted or invalid .docx file  
**Status:** 400

```json
{
  "message": "Document corruption detected in template.docx: not a valid docx file",
  "error_type": "template_document_corruption",
  "details": {
    "file": "template.docx",
    "corruption_details": "not a valid docx file",
    "suggestion": "Ensure the file is a valid Microsoft Word .docx document and not corrupted"
  }
}
```

#### invalid_request_structure
**Cause:** Invalid structure in request_data parameter (Enhanced Mode only)  
**Status:** 400

```json
{
  "message": "Invalid request structure: 1 validation error for TemplateRequest template_data field required",
  "error_type": "invalid_request_structure",
  "details": {
    "error": "1 validation error for TemplateRequest template_data field required",
    "suggestion": "Ensure request follows TemplateRequest model structure"
  }
}
```

### PDF Conversion Errors

#### pdf_conversion_timeout
**Cause:** Gotenberg conversion takes too long  
**Status:** 500

```json
{
  "message": "PDF conversion timed out after 30 seconds",
  "error_type": "pdf_conversion_timeout",
  "details": {
    "timeout_seconds": 30,
    "suggestion": "Try with a simpler template or check Gotenberg service status"
  }
}
```

#### pdf_conversion_failed
**Cause:** Gotenberg service errors  
**Status:** 500

```json
{
  "message": "PDF conversion failed: Gotenberg service returned error 400",
  "error_type": "pdf_conversion_failed",
  "details": {
    "gotenberg_status": 400,
    "gotenberg_error": "invalid document format",
    "suggestion": "Check document format and Gotenberg service availability"
  }
}
```

#### gotenberg_connection_error
**Cause:** Cannot connect to Gotenberg service  
**Status:** 500

```json
{
  "message": "Cannot connect to Gotenberg service",
  "error_type": "gotenberg_connection_error",
  "details": {
    "connection_error": "Connection refused",
    "gotenberg_url": "http://gotenberg:3000",
    "suggestion": "Ensure Gotenberg service is running and accessible"
  }
}
```

## Debugging Template Issues

### Step-by-Step Debugging

1. **Validate JSON Data**
   ```bash
   echo '{"name": "test"}' | jq .
   ```

2. **Test with Minimal Template**
   - Create simple template with `{{test_var}}`
   - Send minimal data: `{"test_var": "Hello"}`

3. **Check Template Syntax**
   - Ensure all `{% raw %}{% if %}{% endraw %}` have matching `{% raw %}{% endif %}{% endraw %}`
   - Verify loop syntax: `{% raw %}{% for item in items %}...{% endfor %}{% endraw %}`

4. **Validate Variable Names**
   - Check spelling and case sensitivity
   - Ensure all template variables exist in data

5. **Test Data Types**
   - Numbers for mathematical operations
   - Arrays for loops
   - Strings for text substitution

### Common Error Scenarios

#### Template Variable Mismatch
**Template:** `{% raw %}{{customer_namme}}{% endraw %}`  
**Data:** `{"customer_name": "John"}`  
**Error:** `template_undefined_error`  
**Fix:** Correct spelling in template

#### Invalid Template Syntax
**Template:** `{% raw %}{% if amount > 100 %}...{% endfor %}{% endraw %}`  
**Error:** `template_syntax_error`  
**Fix:** Change `{% raw %}{% endfor %}{% endraw %}` to `{% raw %}{% endif %}{% endraw %}`

#### Data Type Issues
**Template:** `{% raw %}{{price / quantity}}{% endraw %}`  
**Data:** `{"price": "100.00", "quantity": 2}`  
**Error:** `template_runtime_error`  
**Fix:** Use numbers: `{"price": 100.00, "quantity": 2}`

## Error Prevention Best Practices

### Template Development
1. **Use descriptive variable names** to avoid typos
2. **Test templates incrementally** with simple data first
3. **Validate template syntax** before deployment
4. **Include error handling** in your application

### Data Validation
1. **Validate JSON structure** before sending requests
2. **Check data types** match template expectations
3. **Handle optional fields** with default values
4. **Test with edge cases** (empty arrays, null values)

### Application Integration
1. **Implement retry logic** for temporary failures
2. **Log error responses** for debugging
3. **Provide user-friendly error messages** 
4. **Validate files** before upload

### Example Error Handling Code

#### JavaScript/React
```javascript
try {
  const response = await fetch('/api/v1/process-template-document', {
    method: 'POST',
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json();
    
    switch (error.error_type) {
      case 'invalid_file_type':
        setError('Please upload a .docx file');
        break;
      case 'template_syntax_error':
        setError(`Template error: ${error.details.suggestion}`);
        break;
      case 'pdf_conversion_failed':
        setError('PDF generation failed. Please try again.');
        break;
      default:
        setError(error.message);
    }
    return;
  }
  
  // Handle success
  const pdfBlob = await response.blob();
  // ... download logic
  
} catch (error) {
  setError('Network error. Please check your connection.');
}
```

#### Python
```python
import requests

try:
    response = requests.post(
        'http://localhost:8000/api/v1/process-template-document',
        files={'file': open('template.docx', 'rb')},
        data={'data': json.dumps(template_data)},
        timeout=30
    )
    
    if response.status_code == 200:
        with open('output.pdf', 'wb') as f:
            f.write(response.content)
    else:
        error = response.json()
        print(f"Error: {error['message']}")
        print(f"Type: {error['error_type']}")
        if 'suggestion' in error.get('details', {}):
            print(f"Suggestion: {error['details']['suggestion']}")
            
except requests.exceptions.Timeout:
    print("Request timed out. Please try again.")
except requests.exceptions.ConnectionError:
    print("Cannot connect to service. Check if it's running.")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Getting Help

If you encounter errors not covered in this guide:

1. **Check the service logs** for additional details
2. **Verify your template syntax** using online Jinja2 testers
3. **Test with minimal examples** to isolate the issue
4. **Review the API documentation** for correct usage patterns
5. **Check Gotenberg service status** if PDF conversion fails

For image-specific errors, see the **[Image Support Guide](image-support.html)** troubleshooting section.