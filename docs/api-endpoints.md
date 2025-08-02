---
layout: default
title: API Endpoints
nav_order: 4
description: "Complete API reference for the Document Template Processing Service endpoints."
---

# API Endpoints
{: .no_toc }

Complete reference for all available API endpoints in the Document Template Processing Service.

<details open markdown="block">
  <summary>
    Table of Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

---

## Base URL

- Local: `http://localhost:8000`
- Docker: `http://document-templating-service:8000` (within Docker network)

## Health Check

**GET** `/`

Returns basic service information and status.

**Response:**
```json
{
  "status": "Service is healthy !"
}
```

### Health Check (Alternative)

**GET** `/health-check`

Alternative health check endpoint.

## Process Template Document

**POST** `/api/v1/process-template-document`

Unified endpoint for processing Word templates into PDFs with optional image support.

**Supports two usage modes:**

### Legacy Mode (Simple Templates)
Use the `data` parameter for templates without images:

**Parameters:**
- `file` (required): Word document template (.docx file)
- `data` (required): JSON object containing template variables

### Enhanced Mode (Templates with Images) 
Use the `request_data` parameter for templates with inline images:

**Parameters:**
- `file` (required): Word document template (.docx file)
- `request_data` (required): JSON string containing template_data and images

**Content-Type:** `multipart/form-data`

**Response:** PDF file download

## Legacy Mode Example

**Simple templates without images:**
```bash
curl -X POST http://localhost:8000/api/v1/process-template-document \
  -F "file=@template.docx" \
  -F "data={\"customer_name\":\"John Doe\",\"amount\":150.00}" \
  -o result.pdf
```

## Enhanced Mode Example

**Templates with inline images:**

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

**cURL Example:**
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
curl -X POST http://localhost:8000/api/v1/process-template-document \
  -F "file=@template.docx" \
  -F "request_data=$REQUEST_DATA" \
  -o output.pdf
```

For detailed image support documentation, see the **[Image Support Guide](image-support.html)**.

## Response Format

**Success Response:**
- **Status:** 200 OK
- **Content-Type:** `application/pdf`
- **Body:** PDF file binary data

**Error Response:**
- **Status:** 4xx or 5xx
- **Content-Type:** `application/json`
- **Body:** Structured error details

```json
{
  "message": "Error description",
  "error_type": "error_category",
  "details": {
    "field": "additional_info"
  }
}
```

## Rate Limiting

Currently no rate limiting is implemented. The service processes requests as they arrive.

## Authentication

No authentication is required for API endpoints. Ensure proper network security when deploying.