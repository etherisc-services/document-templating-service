---
layout: default
title: Image Support Guide
nav_order: 5
description: "How to include inline images in document templates using the enhanced API endpoint."
---

# Image Support Guide

The Document Template Processing Service now supports inline images in Word document templates using the enhanced API endpoint. This guide explains how to include PNG images directly in your templates.

## Overview

The service provides inline image support through:
- **Base64 image encoding** for easy React integration
- **Flexible sizing options** (millimeters or pixels)
- **Template variable substitution** using Jinja2 syntax
- **Enhanced error handling** for image processing issues

Based on the [docxtpl inline image documentation](https://docxtpl.readthedocs.io/en/latest/#inline-image), images are processed and injected into templates during rendering.

## API Endpoint

### Unified Endpoint: `/api/v1/process-template-document`

**Method:** `POST`  
**Content-Type:** `multipart/form-data`

**Enhanced Mode Parameters:**
- `file`: Word document template (.docx file)
- `request_data`: JSON string containing template data and images

**Note:** This is the same endpoint used for simple templates (without images) via the `data` parameter. The endpoint automatically detects which mode to use based on the parameters provided.

## Request Format

```json
{
  "template_data": {
    "customer_name": "John Doe",
    "invoice_date": "2024-01-15",
    "logo": "{{company_logo}}",
    "signature": "{{user_signature}}"
  },
  "images": {
    "company_logo": {
      "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ...",
      "width_mm": 50,
      "height_mm": 20
    },
    "user_signature": {
      "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ...",
      "width_px": 200,
      "height_px": 80
    }
  }
}
```

## Image Data Structure

### ImageData Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `data` | string | ✅ | Base64 encoded PNG image data (without `data:image/png;base64,` prefix) |
| `width_mm` | number | ❌ | Width in millimeters (preferred for print) |
| `height_mm` | number | ❌ | Height in millimeters |
| `width_px` | number | ❌ | Width in pixels (converted to mm at 96 DPI) |
| `height_px` | number | ❌ | Height in pixels |

### Sizing Priority

1. **Millimeters take precedence** over pixels
2. **Single dimension** preserves aspect ratio
3. **No dimensions** uses original image size
4. **Pixel conversion**: 96 DPI (96px = 25.4mm)

## Template Setup

### 1. Create Word Template

In your `.docx` template, place image placeholders using Jinja2 syntax:

```
Invoice Header
{{ company_logo }}

Customer: {{ customer_name }}
Date: {{ invoice_date }}

Approved by:
{{ user_signature }}
```

### 2. Image Variable Names

- Use descriptive names: `company_logo`, `user_signature`, `product_image`
- Match template variables with image keys in the request
- Variables are case-sensitive

## React Integration

### File Upload with Images

```javascript
import React, { useState } from 'react';

const DocumentProcessor = () => {
  const [templateFile, setTemplateFile] = useState(null);
  const [logoFile, setLogoFile] = useState(null);
  const [signatureFile, setSignatureFile] = useState(null);

  // Convert file to base64
  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        // Remove data:image/png;base64, prefix
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  };

  const handleSubmit = async () => {
    try {
      // Convert images to base64
      const logoBase64 = await fileToBase64(logoFile);
      const signatureBase64 = await fileToBase64(signatureFile);

      // Prepare request data
      const requestData = {
        template_data: {
          customer_name: "John Doe",
          invoice_date: "2024-01-15",
          amount: 1500.00,
          logo: "{{company_logo}}",
          signature: "{{user_signature}}"
        },
        images: {
          company_logo: {
            data: logoBase64,
            width_mm: 50,
            height_mm: 20
          },
          user_signature: {
            data: signatureBase64,
            width_mm: 80,
            height_mm: 30
          }
        }
      };

      // Create form data
      const formData = new FormData();
      formData.append('file', templateFile);
      formData.append('request_data', JSON.stringify(requestData));

      // Submit request
      const response = await fetch('/api/v1/process-template-document', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        // Download PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'document.pdf';
        a.click();
      } else {
        const error = await response.json();
        console.error('Processing failed:', error);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      <input 
        type="file" 
        accept=".docx"
        onChange={(e) => setTemplateFile(e.target.files[0])}
      />
      <input 
        type="file" 
        accept="image/png"
        onChange={(e) => setLogoFile(e.target.files[0])}
      />
      <input 
        type="file" 
        accept="image/png"
        onChange={(e) => setSignatureFile(e.target.files[0])}
      />
      <button onClick={handleSubmit}>Process Document</button>
    </div>
  );
};
```

### Simplified React Hook

```javascript
import { useState, useCallback } from 'react';

export const useDocumentProcessor = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const processDocument = useCallback(async (templateFile, templateData, images = {}) => {
    setLoading(true);
    setError(null);

    try {
      // Convert image files to base64
      const processedImages = {};
      for (const [key, imageConfig] of Object.entries(images)) {
        const { file, ...dimensions } = imageConfig;
        const base64 = await fileToBase64(file);
        processedImages[key] = {
          data: base64,
          ...dimensions
        };
      }

      const requestData = {
        template_data: templateData,
        images: processedImages
      };

      const formData = new FormData();
      formData.append('file', templateFile);
      formData.append('request_data', JSON.stringify(requestData));

      const response = await fetch('/api/v1/process-template-document', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Processing failed');
      }

      return await response.blob();
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { processDocument, loading, error };
};

// Usage:
const { processDocument } = useDocumentProcessor();

const handleProcess = async () => {
  const pdfBlob = await processDocument(
    templateFile,
    { customer_name: "John Doe", amount: 1500 },
    {
      company_logo: { 
        file: logoFile, 
        width_mm: 50, 
        height_mm: 20 
      },
      user_signature: { 
        file: signatureFile, 
        width_mm: 80, 
        height_mm: 30 
      }
    }
  );
  
  // Handle PDF blob (download, display, etc.)
};
```

## cURL Examples

### Basic Image Processing

```bash
# Prepare base64 encoded image
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

### Multiple Images

```bash
LOGO_BASE64=$(base64 -w 0 logo.png)
SIGNATURE_BASE64=$(base64 -w 0 signature.png)

REQUEST_DATA='{
  "template_data": {
    "customer_name": "John Doe",
    "amount": 1500.00,
    "logo": "{{company_logo}}",
    "signature": "{{user_signature}}"
  },
  "images": {
    "company_logo": {
      "data": "'$LOGO_BASE64'",
      "width_mm": 50,
      "height_mm": 20
    },
    "user_signature": {
      "data": "'$SIGNATURE_BASE64'",
      "width_px": 200,
      "height_px": 80
    }
  }
}'

curl -X POST http://localhost:8000/api/v1/process-template-document \
  -F "file=@invoice_template.docx" \
  -F "request_data=$REQUEST_DATA" \
  -o invoice_with_images.pdf
```

## Error Handling

### Image-Specific Error Types

| Error Type | Description | Solution |
|------------|-------------|----------|
| `image_processing_error` | Failed to process base64 image data | Check base64 encoding and PNG format |
| `invalid_request_structure` | Request doesn't match expected format | Validate JSON structure against schema |
| `missing_template_data` | No template_data provided | Include template_data field in request |

### Example Error Response

```json
{
  "status": "error",
  "error_type": "image_processing_error",
  "message": "Failed to process image 'company_logo': Invalid base64 data",
  "details": {
    "image_name": "company_logo",
    "error": "Invalid base64 data",
    "error_class": "binascii.Error",
    "suggestion": "Ensure image data is valid base64 encoded PNG"
  }
}
```

## Best Practices

### Image Optimization

1. **Format**: Use PNG for best compatibility
2. **Size**: Optimize images before base64 encoding
3. **Resolution**: Use appropriate DPI for print (300 DPI) vs screen (96 DPI)
4. **Dimensions**: Specify dimensions to avoid layout issues

### Template Design

1. **Placeholders**: Use descriptive variable names
2. **Layout**: Consider image dimensions in template design
3. **Fallback**: Include fallback text for missing images
4. **Testing**: Test with various image sizes

### React Implementation

1. **Error Handling**: Implement proper error boundaries
2. **Loading States**: Show progress during processing
3. **File Validation**: Validate file types before upload
4. **Memory Management**: Handle large base64 strings carefully

## Unified Endpoint Design

The `/api/v1/process-template-document` endpoint now supports both modes:

### Legacy Mode (Backward Compatible)
Use the `data` parameter for:
- Templates without images
- Existing integrations  
- Simple use cases
- Maintaining existing code without changes

### Enhanced Mode
Use the `request_data` parameter when:
- Templates include images
- You need structured error handling
- Building React applications with complex data structures

**Smart Detection:** The endpoint automatically detects which mode to use based on the parameters provided, ensuring seamless operation.

## Troubleshooting

### Common Issues

**1. Base64 Encoding Issues**
```javascript
// ❌ Wrong: includes data URL prefix
const wrongBase64 = reader.result; // "data:image/png;base64,iVBORw0KG..."

// ✅ Correct: only base64 data
const correctBase64 = reader.result.split(',')[1]; // "iVBORw0KG..."
```

**2. Image Sizing Problems**
```json
// ❌ Wrong: missing dimensions
"company_logo": {
  "data": "iVBORw0KG..."
}

// ✅ Better: specify dimensions
"company_logo": {
  "data": "iVBORw0KG...",
  "width_mm": 50,
  "height_mm": 20
}
```

**3. Template Variable Mismatch**
```
Template: {{ company_logo }}
Request: "images": { "logo": { ... } }  ❌

Template: {{ company_logo }}
Request: "images": { "company_logo": { ... } }  ✅
```

### Debugging Tips

1. **Validate Base64**: Test base64 data in online decoders
2. **Check Logs**: Review server logs for detailed error information
3. **Test Incrementally**: Start with simple templates and single images
4. **Use Browser DevTools**: Monitor network requests and responses

For additional support, refer to the [main usage guide](usage.md) and [error handling documentation](usage.md#error-handling-and-troubleshooting).