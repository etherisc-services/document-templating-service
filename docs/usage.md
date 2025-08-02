---
layout: default
title: Usage Guide
nav_order: 3
has_toc: true
description: "Quick start guide and overview for the Document Template Processing Service."
---

# Usage Guide
{: .no_toc }

Quick start guide for using the Document Template Processing Service API.

<details open markdown="block">
  <summary>
    Table of Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

---

## Overview

The Document Template Processing Service converts Word document templates with data injection into PDF files. It uses Jinja2 templating syntax and supports both simple text substitution and advanced features like images, loops, and conditional logic.

## Quick Start

### 1. Basic Example

**Template (template.docx):**
```
Customer: {{customer_name}}
Amount: ${{amount}}
```

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/process-template-document \
  -F "file=@template.docx" \
  -F "data={\"customer_name\":\"John Doe\",\"amount\":150.00}" \
  -o result.pdf
```

### 2. With Images

**Template (template.docx):**
```
Company Logo: {{company_logo}}
Customer: {{customer_name}}
```

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/process-template-document \
  -F "file=@template.docx" \
  -F "request_data={\"template_data\":{\"customer_name\":\"John Doe\",\"company_logo\":\"{{logo}}\"},\"images\":{\"logo\":{\"data\":\"base64_data\",\"width_mm\":40}}}" \
  -o result.pdf
```

## API Modes

The service supports two usage modes through a single unified endpoint:

### Legacy Mode
- **Parameter:** `data` (JSON object)
- **Use case:** Simple templates without images
- **Benefit:** Backward compatible with existing integrations

### Enhanced Mode  
- **Parameter:** `request_data` (JSON string)
- **Use case:** Templates with images and complex data structures
- **Benefit:** Support for inline images and React-friendly format

## Documentation Sections

### 📋 **[API Endpoints](api-endpoints.html)**
Complete API reference with parameters, responses, and examples for all endpoints.

### 📄 **[Document Templates](document-templates.html)**
Learn how to create Word templates with Jinja2 syntax, including:
- Variable substitution
- Conditional logic (if/else)
- Loops (for each)
- Advanced template patterns
- Best practices and troubleshooting

### 🖼️ **[Image Support](image-support.html)**
Comprehensive guide to including images in templates:
- Base64 encoding for React applications
- Size specifications and optimization
- Template integration examples
- Troubleshooting image issues

### 🚫 **[Error Handling](error-handling.html)**
Understanding and debugging errors:
- HTTP status codes and error types
- Structured error responses
- Common issues and solutions
- Debugging strategies

### 💡 **[Examples](examples.html)**
Complete practical examples:
- Invoice generation with complex data
- React and Node.js integration code
- Postman testing setup
- Real-world use cases

### 🐳 **[Integration Guide](integration.html)**
Docker Compose setup and integration patterns for existing applications.

## Base URL

- **Local:** `http://localhost:8000`
- **Docker:** `http://document-templating-service:8000` (within Docker network)

## Health Check

**GET** `/` or `/health-check`

```json
{
  "status": "Service is healthy !"
}
```

## Main Endpoint

**POST** `/api/v1/process-template-document`

**Parameters:**
- `file`: Word document template (.docx)
- `data`: JSON object (legacy mode)
- `request_data`: JSON string with template_data and images (enhanced mode)

**Response:** PDF file download

## Template Syntax Examples

### Variable Substitution
```
Hello {{name}}, your order total is ${{amount}}.
```

### Conditional Logic
```
{% raw %}{% if premium_customer %}
Thank you for being a premium customer!
{% else %}
Thank you for your business!
{% endif %}{% endraw %}
```

### Loops
```
{% raw %}Order Items:
{% for item in items %}
- {{item.name}}: ${{item.price}}
{% endfor %}{% endraw %}
```

## Getting Started

1. **📖 Start with [API Endpoints](api-endpoints.html)** to understand the available endpoints
2. **📄 Learn [Document Templates](document-templates.html)** to create your first template
3. **💡 Try [Examples](examples.html)** for complete working examples
4. **🚫 Reference [Error Handling](error-handling.html)** when troubleshooting
5. **🖼️ Add [Image Support](image-support.html)** for enhanced templates
6. **🐳 Deploy with [Integration Guide](integration.html)** for production use

## Need Help?

- Check the **[Error Handling](error-handling.html)** guide for common issues
- Try the **[Examples](examples.html)** for working code samples  
- Review the **[Document Templates](document-templates.html)** guide for syntax help
- Use the **[API Endpoints](api-endpoints.html)** reference for parameter details