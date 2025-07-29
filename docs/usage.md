---
layout: default
title: Usage Guide
nav_order: 3
description: "Comprehensive API documentation and templating examples for the Document Template Processing Service."
---

# Usage Guide

This guide covers how to use the Document Template Processing Service API and create Word document templates.

## API Overview

The service provides a REST API for processing Word document templates with data injection and PDF conversion.

### Base URL
- Local: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

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

Main endpoint for processing Word templates into PDFs.

**Parameters:**
- `file` (required): Word document template (.docx file)
- `data` (required): JSON object containing template variables

**Content-Type:** `multipart/form-data`

**Response:** PDF file download

**Example with curl:**
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

### Data Types

The service accepts various data types in the JSON payload:

- **Strings:** `"Hello World"`
- **Numbers:** `42`, `3.14`
- **Booleans:** `true`, `false`
- **Arrays:** `["item1", "item2"]`
- **Objects:** `{"key": "value"}`
- **Nested structures:** Complex JSON objects

### Error Handling

The API returns appropriate HTTP status codes:

- **200 OK:** Successful processing
- **400 Bad Request:** Missing or invalid parameters
- **500 Internal Server Error:** Processing errors

**Error Response Example:**
```json
{
  "status": "error",
  "message": "file is required"
}
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
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - API framework documentation 