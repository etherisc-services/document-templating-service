---
layout: default
title: Usage Guide
nav_order: 3
description: "Comprehensive service usage and templating examples for the Document Template Processing Service."
---

# Usage Guide

This guide covers how to use the Document Template Processing Service API and create Word document templates.

## API Overview

The service provides a REST API for processing Word document templates with data injection and PDF conversion.

### Base URL
- Local: `http://localhost:8000`

## API Endpoints

### Health Check

**GET** `/`

Returns the service health status.

**Response:**
```json
{
  "status": "Service is healthy !"
}
```

**Example:**
```bash
curl http://localhost:8000/
```

### Health Check (Alternative)

**GET** `/health-check`

Alternative health check endpoint.

### Process Template Document

**POST** `/api/v1/process-template-document`

Main endpoint for processing Word templates into PDFs (without image support).

**Parameters:**
- `file` (required): Word document template (.docx file)
- `data` (required): JSON object containing template variables

**Content-Type:** `multipart/form-data`

**Response:** PDF file download

### Process Template Document with Images

**POST** `/api/v1/process-template-document-with-images`

Enhanced endpoint for processing Word templates with inline image support.

**Parameters:**
- `file` (required): Word document template (.docx file)
- `request_data` (required): JSON string containing template_data and optional images

**Content-Type:** `multipart/form-data`

**Response:** PDF file download

**Request Data Structure:**
```json
{
  "template_data": {
    "customer_name": "John Doe",
    "logo": "{{company_logo}}"
  },
  "images": {
    "company_logo": {
      "data": "base64_encoded_png_data",
      "width_mm": 50,
      "height_mm": 20
    }
  }
}
```

**Example with curl:**
```bash
# Encode image to base64
IMAGE_BASE64=$(base64 -w 0 logo.png)

# Create request data
REQUEST_DATA='{
  "template_data": {
    "customer_name": "John Doe",
    "logo": "{{company_logo}}"
  },
  "images": {
    "company_logo": {
      "data": "'$IMAGE_BASE64'",
      "width_mm": 50,
      "height_mm": 20
    }
  }
}'

# Submit request
curl -X POST http://localhost:8000/api/v1/process-template-document-with-images \
  -F "file=@template.docx" \
  -F "request_data=$REQUEST_DATA" \
  -o output.pdf
```

For detailed image support documentation, see the **[Image Support Guide](image-support.md)**.

**Original Endpoint Example:**
```bash
curl -X POST \
  http://localhost:8000/api/v1/process-template-document \
  -F "file=@template.docx" \
  -F "data={\"name\":\"John Doe\",\"amount\":150.00}" \
  --output result.pdf
```

**Example with Python:**
```python
import requests

url = "http://localhost:8000/api/v1/process-template-document"

# Template data
data = {
    "name": "John Doe",
    "company": "Acme Corp",
    "amount": 150.00,
    "items": [
        {"description": "Web Development", "quantity": 1, "price": 100.00},
        {"description": "Consulting", "quantity": 2, "price": 25.00}
    ]
}

# Upload file and data
with open("invoice_template.docx", "rb") as f:
    files = {"file": f}
    form_data = {"data": json.dumps(data)}
    
    response = requests.post(url, files=files, data=form_data)
    
    if response.status_code == 200:
        with open("invoice.pdf", "wb") as pdf_file:
            pdf_file.write(response.content)
        print("PDF generated successfully!")
```

## Document Templates

The service uses [docxtpl](https://docxtpl.readthedocs.io/) for template processing. Templates are Word documents with special syntax for variable substitution.

### Basic Variable Substitution

**Template:**
```
Hello {{name}}!

Your invoice amount is ${{amount}}.
```

**Data:**
```json
{
  "name": "John Doe",
  "amount": 150.00
}
```

**Result:**
```
Hello John Doe!

Your invoice amount is $150.00.
```

### Conditional Logic (If/Then/Else)

**Template:**
```
{% raw %}
Dear {{name}},

{%- if premium_customer %}
Thank you for being a premium customer! You receive a 10% discount.
{%- else %}
Thank you for your business!
{%- endif %}

{%- if amount > 100 %}
This is a large order. Processing may take 2-3 business days.
{%- endif %}
{% endraw %}
```

**Data:**
```json
{
  "name": "Jane Smith",
  "premium_customer": true,
  "amount": 250.00
}
```

**Result:**
```
Dear Jane Smith,

Thank you for being a premium customer! You receive a 10% discount.

This is a large order. Processing may take 2-3 business days.
```

### Loops (For Each)

**Template:**
```
{% raw %}
Invoice Items:

{%- for item in items %}
- {{item.description}}: {{item.quantity}} x ${{item.price}} = ${{item.quantity * item.price}}
{%- endfor %}

Total: ${{total}}
{% endraw %}
```

**Data:**
```json
{
  "items": [
    {"description": "Web Development", "quantity": 1, "price": 100.00},
    {"description": "Consulting", "quantity": 2, "price": 25.00},
    {"description": "Hosting", "quantity": 12, "price": 10.00}
  ],
  "total": 270.00
}
```

**Result:**
```
Invoice Items:

- Web Development: 1 x $100.00 = $100.00
- Consulting: 2 x $25.00 = $50.00
- Hosting: 12 x $10.00 = $120.00

Total: $270.00
```

### Advanced Examples

#### Nested Loops with Conditions

**Template:**
```
{% raw %}
Customer Orders Report

{%- for customer in customers %}

Customer: {{customer.name}}
{%- if customer.orders %}
Orders:
  {%- for order in customer.orders %}
  - Order #{{order.id}} ({{order.date}})
    {%- if order.items %}
    Items:
      {%- for item in order.items %}
      * {{item.name}} - ${{item.price}}
      {%- endfor %}
    {%- endif %}
    Total: ${{order.total}}
  {%- endfor %}
{%- else %}
No orders found.
{%- endif %}

{%- endfor %}
{% endraw %}
```

#### Table Generation

**Template (in a Word table):**
```
{% raw %}
| Item | Qty | Price | Total |
|------|-----|-------|-------|
{%- for item in items %}
| {{item.name}} | {{item.qty}} | ${{item.price}} | ${{item.qty * item.price}} |
{%- endfor %}
{% endraw %}
```

#### Date Formatting

**Template:**
```
{% raw %}
Invoice Date: {{invoice_date|date_format('%B %d, %Y')}}
Due Date: {{due_date|date_format('%m/%d/%Y')}}
{% endraw %}
```

**Data:**
```json
{
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-15"
}
```

### Template Syntax Reference

| Syntax | Purpose | Example |
|--------|---------|---------|
| `{% raw %}{{variable}}{% endraw %}` | Variable substitution | `{% raw %}{{name}}{% endraw %}` |
| `{% raw %}{%- if condition %}...{%- endif %}{% endraw %}` | Conditional | `{% raw %}{%- if amount > 100 %}Large order{%- endif %}{% endraw %}` |
| `{% raw %}{%- for item in list %}...{%- endfor %}{% endraw %}` | Loop | `{% raw %}{%- for item in items %}{{item}}{%- endfor %}{% endraw %}` |
| `{% raw %}{%- else %}{% endraw %}` | Else clause | Used with if statements |
| `{% raw %}{{variable|filter}}{% endraw %}` | Apply filter | `{% raw %}{{date|date_format('%Y-%m-%d')}}{% endraw %}` |
| `{% raw %}{{image_variable}}{% endraw %}` | Image insertion | `{% raw %}{{company_logo}}{% endraw %}` |

### Image Support in Templates

🎯 **Available in:** `/api/v1/process-template-document-with-images` endpoint only

Images can be embedded directly in templates using the enhanced endpoint. Images are provided as Base64-encoded PNG data and referenced in templates using standard Jinja2 variable syntax.

**Template Example:**
```
Company Logo: {{company_logo}}

Invoice for {{customer_name}}
Date: {{invoice_date}}

Signature: {{authorized_signature}}
```

**Request Data with Images:**
```json
{
  "template_data": {
    "customer_name": "John Doe", 
    "invoice_date": "2024-01-15",
    "company_logo": "{{company_logo}}",
    "authorized_signature": "{{signature_image}}"
  },
  "images": {
    "company_logo": {
      "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ...",
      "width_mm": 60,
      "height_mm": 20
    },
    "signature_image": {
      "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ...",
      "width_px": 150,
      "height_px": 50
    }
  }
}
```

**Image Specifications:**
- **Format:** PNG only (Base64 encoded)
- **Sizing:** Millimeters (preferred) or pixels  
- **DPI Conversion:** 96px = 25.4mm
- **Variable Names:** Must match between template and images object

For comprehensive image documentation, see the **[Image Support Guide](image-support.md)**.

### Data Types

The service accepts various data types in the JSON payload:

- **Strings:** `"Hello World"`
- **Numbers:** `42`, `3.14`
- **Booleans:** `true`, `false`
- **Arrays:** `["item1", "item2"]`
- **Objects:** `{"key": "value"}`
- **Nested structures:** Complex JSON objects

### Error Handling

The API provides comprehensive error handling with detailed error information for debugging and troubleshooting.

#### HTTP Status Codes

- **200 OK:** Successful processing
- **400 Bad Request:** Client errors (invalid input, template errors, etc.)
- **500 Internal Server Error:** Server errors (service failures, unexpected errors)

#### Error Response Format

All error responses follow a structured format:

```json
{
  "status": "error",
  "error_type": "specific_error_category",
  "message": "Human-readable error description",
  "details": {
    "additional": "contextual information",
    "for": "debugging purposes"
  }
}
```

#### Error Categories

##### File Processing Errors

**Missing File (400):**
```json
{
  "status": "error",
  "error_type": "missing_file",
  "message": "No file provided or filename is empty",
  "details": {
    "requirement": "A valid .docx file must be uploaded"
  }
}
```

**Invalid File Type (400):**
```json
{
  "status": "error",
  "error_type": "invalid_file_type", 
  "message": "Invalid file type. Only .docx files are supported",
  "details": {
    "provided_filename": "document.pdf",
    "supported_types": [".docx"],
    "requirement": "Upload a Microsoft Word .docx file"
  }
}
```

**File Too Large (400):**
```json
{
  "status": "error",
  "error_type": "file_too_large",
  "message": "File too large. Maximum size is 50MB",
  "details": {
    "max_size_mb": 50,
    "file_size_bytes": 67108864
  }
}
```

**Corrupted File (400):**
```json
{
  "status": "error",
  "error_type": "invalid_docx_format",
  "message": "Invalid or corrupted .docx file",
  "details": {
    "file": "template.docx",
    "error": "not a valid docx file",
    "suggestion": "Ensure the file is a valid Microsoft Word .docx document"
  }
}
```

##### Template Processing Errors

**Missing Template Data (400):**
```json
{
  "status": "error",
  "error_type": "missing_template_data",
  "message": "No template data provided",
  "details": {
    "requirement": "Provide JSON data for template variable injection",
    "example": "{\"name\": \"John\", \"company\": \"Acme Corp\"}"
  }
}
```

**Invalid JSON (400):**
```json
{
  "status": "error",
  "error_type": "invalid_json",
  "message": "Invalid JSON data: Expecting ',' delimiter: line 3 column 15",
  "details": {
    "json_error": "Expecting ',' delimiter: line 3 column 15",
    "line": 3,
    "column": 15
  }
}
```

**Template Syntax Error (400):**
```json
{
  "status": "error",
  "error_type": "template_syntax_error",
  "message": "Template syntax error: unexpected 'end of template'",
  "details": {
    "file": "template.docx",
    "line": 5,
    "column": 12,
    "template_name": "template.docx",
    "syntax_error": "unexpected 'end of template'"
  }
}
```

**Undefined Variable (400):**
```json
{
  "status": "error",
  "error_type": "undefined_variable",
  "message": "Undefined variable in template: 'customer_name' is undefined",
  "details": {
    "file": "template.docx",
    "undefined_variable": "'customer_name' is undefined",
    "suggestion": "Check your template variables match the provided data"
  }
}
```

**Template Runtime Error (400):**
```json
{
  "status": "error", 
  "error_type": "template_runtime_error",
  "message": "Template runtime error: unsupported operand type(s) for *: 'str' and 'int'",
  "details": {
    "file": "template.docx",
    "runtime_error": "unsupported operand type(s) for *: 'str' and 'int'"
  }
}
```

##### PDF Conversion Errors

**Gotenberg Connection Error (500):**
```json
{
  "status": "error",
  "error_type": "gotenberg_connection_error",
  "message": "Cannot connect to Gotenberg service: Connection refused",
  "details": {
    "gotenberg_url": "http://gotenberg:3000",
    "connection_error": "Connection refused",
    "suggestion": "Check if Gotenberg service is running and accessible"
  }
}
```

**Gotenberg Timeout (500):**
```json
{
  "status": "error",
  "error_type": "gotenberg_timeout", 
  "message": "Gotenberg request timed out (60s)",
  "details": {
    "timeout_seconds": 60,
    "suggestion": "Try with a smaller document or check Gotenberg service health"
  }
}
```

**Gotenberg Conversion Failed (500):**
```json
{
  "status": "error",
  "error_type": "gotenberg_conversion_failed",
  "message": "Gotenberg could not process the document (unprocessable entity)",
  "details": {
    "gotenberg_url": "http://gotenberg:3000/forms/libreoffice/convert",
    "status_code": 422,
    "response_headers": {
      "content-type": "application/json"
    },
    "error_data": {
      "message": "Document format not supported"
    }
  }
}
```

#### Debugging Template Issues

When encountering template errors, follow these steps:

1. **Check Variable Names:** Ensure template variables match your data exactly
   ```text
   Template: {{customer.name}}
   Data: {"customer": {"name": "John Doe"}}  ✓
   Data: {"customer_name": "John Doe"}       ✗
   ```

2. **Validate Template Syntax:** Use proper Jinja2 syntax
   ```text
   {% raw %}
   Correct: {% if items %}...{% endif %}
   Wrong:   {% if items %}...{% end %}
   {% endraw %}
   ```

3. **Check Data Types:** Ensure operations match data types
   ```text
   Template: {{quantity * price}}
   Data: {"quantity": "5", "price": 10}      ✗ (string * number)
   Data: {"quantity": 5, "price": 10}        ✓ (number * number)
   ```

4. **Use Optional Variables:** Handle optional data gracefully
   ```text
   {% raw %}
   Safe: {% if customer.email %}{{customer.email}}{% endif %}
   Risky: {{customer.email}} (fails if email is missing)
   {% endraw %}
   ```

#### Common Error Scenarios

##### Template Variable Mismatch
```bash
# Template contains: {{invoice.customer_name}}
# But data provides: {"customer": {"name": "John"}}
# Solution: Change template to {{customer.name}} or data to {"invoice": {"customer_name": "John"}}
```

##### Invalid Template Syntax
```bash
{% raw %}
# Template contains unclosed tags: {% for item in items %}...
# Missing: {% endfor %}
# Error: "unexpected 'end of template'"
{% endraw %}
```

##### Data Type Issues
```bash
# Template: Total: ${{item.quantity * item.price}}
# Data: {"item": {"quantity": "5", "price": "10.50"}}
# Error: can't multiply string by string
# Solution: Use numbers: {"item": {"quantity": 5, "price": 10.50}}
```

## Testing with Postman

1. **Set up request:**
   - Method: POST
   - URL: `http://localhost:8000/api/v1/process-template-document`

2. **Configure body:**
   - Type: form-data
   - Add `file` key with your .docx template
   - Add `data` key with your JSON data

3. **Send request and save response as PDF**

## Complete Example: Invoice Template

### Template File (invoice_template.docx)

Create a Word document with this content:

```
{% raw %}
INVOICE

Date: {{invoice_date}}
Invoice #: {{invoice_number}}

Bill To:
{{customer.name}}
{{customer.address}}
{{customer.city}}, {{customer.state}} {{customer.zip}}

{%- if customer.email %}
Email: {{customer.email}}
{%- endif %}

Items:
{%- for item in items %}
{{loop.index}}. {{item.description}}
   Quantity: {{item.quantity}}
   Unit Price: ${{item.unit_price}}
   Total: ${{item.quantity * item.unit_price}}

{%- endfor %}

{%- if discount > 0 %}
Subtotal: ${{subtotal}}
Discount ({{discount_percent}}%): -${{discount}}
{%- endif %}

TOTAL: ${{total}}

{%- if notes %}
Notes: {{notes}}
{%- endif %}
{% endraw %}
```

### JSON Data

```json
{
  "invoice_date": "January 15, 2024",
  "invoice_number": "INV-2024-001",
  "customer": {
    "name": "Acme Corporation",
    "address": "123 Business St",
    "city": "New York",
    "state": "NY",
    "zip": "10001",
    "email": "billing@acme.com"
  },
  "items": [
    {
      "description": "Web Development Services",
      "quantity": 40,
      "unit_price": 75.00
    },
    {
      "description": "Project Management",
      "quantity": 10,
      "unit_price": 100.00
    }
  ],
  "subtotal": 4000.00,
  "discount_percent": 10,
  "discount": 400.00,
  "total": 3600.00,
  "notes": "Payment due within 30 days. Thank you for your business!"
}
```

This will generate a professional PDF invoice with all the data properly formatted.

## Additional Resources

- [docxtpl Documentation](https://docxtpl.readthedocs.io/) - Complete templating syntax
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) - Underlying template engine
- [Gotenberg Documentation](https://gotenberg.dev/) - PDF conversion service 