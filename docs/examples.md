---
layout: default
title: Examples
nav_order: 7
description: "Complete examples and use cases for the Document Template Processing Service."
---

# Examples
{: .no_toc }

Practical examples and complete use cases for the Document Template Processing Service.

<details open markdown="block">
  <summary>
    Table of Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

---

## Testing with Postman

### Basic Request Setup

1. **Create New Request**
   - Method: `POST`
   - URL: `http://localhost:8000/api/v1/process-template-document`

2. **Set Headers**
   - Content-Type: `multipart/form-data` (Postman sets this automatically)

3. **Configure Body**
   - Select "form-data"
   - Add key `file` (type: File), upload your .docx template
   - Add key `data` (type: Text), value: `{"customer_name": "John Doe", "amount": 150.00}`

4. **Send Request**
   - Response should be a PDF file
   - Save the response to view the generated PDF

### Advanced Postman Example with Images

1. **Prepare Base64 Image**
   ```bash
   base64 -w 0 logo.png > logo_base64.txt
   ```

2. **Request Body**
   - Key: `file` (File) → Upload template.docx
   - Key: `request_data` (Text) → JSON with images:

```json
{
  "template_data": {
    "customer_name": "John Doe",
    "invoice_number": "INV-2023-001",
    "company_logo": "{{logo_image}}"
  },
  "images": {
    "logo_image": {
      "data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
      "width_mm": 30,
      "height_mm": 15
    }
  }
}
```

## Complete Example: Invoice Template

### Template File (invoice_template.docx)

Create a Word document with this content:

```
                    INVOICE

Company: {{company_name}}
Logo: {{company_logo}}

Invoice #: {{invoice_number}}
Date: {{invoice_date}}
Due Date: {{due_date}}

Bill To:
{{customer_name}}
{{customer_address}}
{{customer_city}}, {{customer_state}} {{customer_zip}}

{% raw %}{% if customer_email %}
Email: {{customer_email}}
{% endif %}

ITEMS:
{% for item in line_items %}
{{item.description}}
Quantity: {{item.quantity}} × ${{item.unit_price}} = ${{item.total}}
{% endfor %}

Subtotal: ${{subtotal}}
{% if tax_rate > 0 %}
Tax ({{tax_rate}}%): ${{tax_amount}}
{% endif %}
{% if discount > 0 %}
Discount: -${{discount}}
{% endif %}

TOTAL: ${{total_amount}}

{% if payment_terms %}
Payment Terms: {{payment_terms}}
{% endif %}

{% if notes %}
Notes:
{{notes}}
{% endif %}{% endraw %}

Thank you for your business!
```

### JSON Data

```json
{
  "company_name": "Acme Corporation",
  "company_logo": "{{company_logo}}",
  "invoice_number": "INV-2023-001",
  "invoice_date": "December 1, 2023",
  "due_date": "December 31, 2023",
  
  "customer_name": "John Doe",
  "customer_address": "123 Main Street",
  "customer_city": "Anytown",
  "customer_state": "CA",
  "customer_zip": "12345",
  "customer_email": "john.doe@email.com",
  
  "line_items": [
    {
      "description": "Web Development Services",
      "quantity": 40,
      "unit_price": 75.00,
      "total": 3000.00
    },
    {
      "description": "Domain Registration",
      "quantity": 1,
      "unit_price": 15.00,
      "total": 15.00
    },
    {
      "description": "SSL Certificate",
      "quantity": 1,
      "unit_price": 50.00,
      "total": 50.00
    }
  ],
  
  "subtotal": 3065.00,
  "tax_rate": 8.5,
  "tax_amount": 260.53,
  "discount": 0,
  "total_amount": 3325.53,
  
  "payment_terms": "Net 30",
  "notes": "Please include invoice number on payment."
}
```

### cURL Command

```bash
# Simple version (without images)
curl -X POST http://localhost:8000/api/v1/process-template-document \
  -F "file=@invoice_template.docx" \
  -F 'data={
    "company_name": "Acme Corporation",
    "invoice_number": "INV-2023-001",
    "invoice_date": "December 1, 2023",
    "due_date": "December 31, 2023",
    "customer_name": "John Doe",
    "customer_address": "123 Main Street",
    "customer_city": "Anytown",
    "customer_state": "CA",
    "customer_zip": "12345",
    "customer_email": "john.doe@email.com",
    "line_items": [
      {
        "description": "Web Development Services",
        "quantity": 40,
        "unit_price": 75.00,
        "total": 3000.00
      }
    ],
    "subtotal": 3000.00,
    "tax_rate": 8.5,
    "tax_amount": 255.00,
    "total_amount": 3255.00,
    "payment_terms": "Net 30"
  }' \
  -o invoice_result.pdf
```

### Enhanced Version with Company Logo

```bash
# Encode company logo
LOGO_BASE64=$(base64 -w 0 company_logo.png)

# Create request with image
curl -X POST http://localhost:8000/api/v1/process-template-document \
  -F "file=@invoice_template.docx" \
  -F "request_data={
    \"template_data\": {
      \"company_name\": \"Acme Corporation\",
      \"company_logo\": \"{{company_logo}}\",
      \"invoice_number\": \"INV-2023-001\",
      \"invoice_date\": \"December 1, 2023\",
      \"customer_name\": \"John Doe\",
      \"total_amount\": 3255.00
    },
    \"images\": {
      \"company_logo\": {
        \"data\": \"$LOGO_BASE64\",
        \"width_mm\": 40,
        \"height_mm\": 20
      }
    }
  }" \
  -o invoice_with_logo.pdf
```

## React Integration Example

### Basic Hook for Template Processing

```javascript
import { useState } from 'react';

export const useTemplateProcessor = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const processTemplate = async (templateFile, data, images = null) => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', templateFile);
      
      if (images) {
        // Enhanced mode with images
        formData.append('request_data', JSON.stringify({
          template_data: data,
          images: images
        }));
      } else {
        // Legacy mode
        formData.append('data', JSON.stringify(data));
      }
      
      const response = await fetch('/api/v1/process-template-document', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Processing failed');
      }
      
      const pdfBlob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'generated-document.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return pdfBlob;
      
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  return { processTemplate, loading, error };
};
```

### Component Example

```javascript
import React, { useState } from 'react';
import { useTemplateProcessor } from './useTemplateProcessor';

export const InvoiceGenerator = () => {
  const [templateFile, setTemplateFile] = useState(null);
  const [customerName, setCustomerName] = useState('');
  const [amount, setAmount] = useState('');
  const [logoFile, setLogoFile] = useState(null);
  
  const { processTemplate, loading, error } = useTemplateProcessor();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!templateFile) {
      alert('Please select a template file');
      return;
    }
    
    try {
      const data = {
        customer_name: customerName,
        amount: parseFloat(amount),
        invoice_date: new Date().toLocaleDateString()
      };
      
      let images = null;
      
      if (logoFile) {
        // Convert logo to base64
        const logoBase64 = await fileToBase64(logoFile);
        images = {
          company_logo: {
            data: logoBase64,
            width_mm: 40,
            height_mm: 20
          }
        };
        data.company_logo = '{{company_logo}}';
      }
      
      await processTemplate(templateFile, data, images);
      
    } catch (err) {
      console.error('Processing failed:', err);
    }
  };
  
  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const base64 = reader.result.split(',')[1]; // Remove data:image/png;base64,
        resolve(base64);
      };
      reader.onerror = reject;
    });
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Template File (.docx):</label>
        <input
          type="file"
          accept=".docx"
          onChange={(e) => setTemplateFile(e.target.files[0])}
          required
        />
      </div>
      
      <div>
        <label>Customer Name:</label>
        <input
          type="text"
          value={customerName}
          onChange={(e) => setCustomerName(e.target.value)}
          required
        />
      </div>
      
      <div>
        <label>Amount:</label>
        <input
          type="number"
          step="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />
      </div>
      
      <div>
        <label>Company Logo (optional):</label>
        <input
          type="file"
          accept=".png"
          onChange={(e) => setLogoFile(e.target.files[0])}
        />
      </div>
      
      <button type="submit" disabled={loading}>
        {loading ? 'Processing...' : 'Generate PDF'}
      </button>
      
      {error && <div style={{color: 'red'}}>Error: {error}</div>}
    </form>
  );
};
```

## Python Integration Example

```python
import requests
import json
import base64
from pathlib import Path

class TemplateProcessor:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/v1/process-template-document"
    
    def process_simple_template(self, template_path, data, output_path):
        """Process template without images (legacy mode)"""
        try:
            with open(template_path, 'rb') as template_file:
                files = {'file': template_file}
                form_data = {'data': json.dumps(data)}
                
                response = requests.post(
                    self.endpoint,
                    files=files,
                    data=form_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    with open(output_path, 'wb') as output_file:
                        output_file.write(response.content)
                    return True
                else:
                    error = response.json()
                    print(f"Error: {error['message']}")
                    return False
                    
        except Exception as e:
            print(f"Request failed: {e}")
            return False
    
    def process_template_with_images(self, template_path, data, images, output_path):
        """Process template with images (enhanced mode)"""
        try:
            # Prepare image data
            image_data = {}
            for image_name, image_info in images.items():
                image_path = image_info['path']
                with open(image_path, 'rb') as img_file:
                    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                
                image_data[image_name] = {
                    'data': img_base64,
                    'width_mm': image_info.get('width_mm'),
                    'height_mm': image_info.get('height_mm')
                }
            
            request_data = {
                'template_data': data,
                'images': image_data
            }
            
            with open(template_path, 'rb') as template_file:
                files = {'file': template_file}
                form_data = {'request_data': json.dumps(request_data)}
                
                response = requests.post(
                    self.endpoint,
                    files=files,
                    data=form_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    with open(output_path, 'wb') as output_file:
                        output_file.write(response.content)
                    return True
                else:
                    error = response.json()
                    print(f"Error: {error['message']}")
                    return False
                    
        except Exception as e:
            print(f"Request failed: {e}")
            return False

# Example usage
if __name__ == "__main__":
    processor = TemplateProcessor()
    
    # Simple example
    invoice_data = {
        "customer_name": "John Doe",
        "invoice_number": "INV-001",
        "amount": 1500.00,
        "date": "2023-12-01"
    }
    
    success = processor.process_simple_template(
        "invoice_template.docx",
        invoice_data,
        "invoice_output.pdf"
    )
    
    if success:
        print("Invoice generated successfully!")
    
    # Example with images
    invoice_data_with_logo = {
        "customer_name": "Jane Smith",
        "invoice_number": "INV-002",
        "amount": 2500.00,
        "company_logo": "{{logo}}"
    }
    
    images = {
        "logo": {
            "path": "company_logo.png",
            "width_mm": 40,
            "height_mm": 20
        }
    }
    
    success = processor.process_template_with_images(
        "invoice_template.docx",
        invoice_data_with_logo,
        images,
        "invoice_with_logo.pdf"
    )
    
    if success:
        print("Invoice with logo generated successfully!")
```

## Node.js Integration Example

```javascript
const fs = require('fs');
const FormData = require('form-data');
const fetch = require('node-fetch');

class TemplateProcessor {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.endpoint = `${baseUrl}/api/v1/process-template-document`;
    }
    
    async processSimpleTemplate(templatePath, data, outputPath) {
        try {
            const form = new FormData();
            form.append('file', fs.createReadStream(templatePath));
            form.append('data', JSON.stringify(data));
            
            const response = await fetch(this.endpoint, {
                method: 'POST',
                body: form
            });
            
            if (response.ok) {
                const buffer = await response.buffer();
                fs.writeFileSync(outputPath, buffer);
                return true;
            } else {
                const error = await response.json();
                console.error('Error:', error.message);
                return false;
            }
        } catch (error) {
            console.error('Request failed:', error);
            return false;
        }
    }
    
    async processTemplateWithImages(templatePath, data, images, outputPath) {
        try {
            // Prepare image data
            const imageData = {};
            for (const [imageName, imageInfo] of Object.entries(images)) {
                const imageBuffer = fs.readFileSync(imageInfo.path);
                const imageBase64 = imageBuffer.toString('base64');
                
                imageData[imageName] = {
                    data: imageBase64,
                    width_mm: imageInfo.width_mm,
                    height_mm: imageInfo.height_mm
                };
            }
            
            const requestData = {
                template_data: data,
                images: imageData
            };
            
            const form = new FormData();
            form.append('file', fs.createReadStream(templatePath));
            form.append('request_data', JSON.stringify(requestData));
            
            const response = await fetch(this.endpoint, {
                method: 'POST',
                body: form
            });
            
            if (response.ok) {
                const buffer = await response.buffer();
                fs.writeFileSync(outputPath, buffer);
                return true;
            } else {
                const error = await response.json();
                console.error('Error:', error.message);
                return false;
            }
        } catch (error) {
            console.error('Request failed:', error);
            return false;
        }
    }
}

// Example usage
async function main() {
    const processor = new TemplateProcessor();
    
    // Simple example
    const invoiceData = {
        customer_name: "John Doe",
        invoice_number: "INV-001",
        amount: 1500.00,
        date: "2023-12-01"
    };
    
    const success1 = await processor.processSimpleTemplate(
        'invoice_template.docx',
        invoiceData,
        'invoice_output.pdf'
    );
    
    if (success1) {
        console.log('Invoice generated successfully!');
    }
    
    // Example with images
    const invoiceDataWithLogo = {
        customer_name: "Jane Smith",
        invoice_number: "INV-002",
        amount: 2500.00,
        company_logo: "{{logo}}"
    };
    
    const images = {
        logo: {
            path: 'company_logo.png',
            width_mm: 40,
            height_mm: 20
        }
    };
    
    const success2 = await processor.processTemplateWithImages(
        'invoice_template.docx',
        invoiceDataWithLogo,
        images,
        'invoice_with_logo.pdf'
    );
    
    if (success2) {
        console.log('Invoice with logo generated successfully!');
    }
}

main().catch(console.error);
```

## Additional Resources

- **[Installation Guide](installation.md)** - Setup and deployment
- **[API Endpoints](api-endpoints.md)** - Complete API reference
- **[Document Templates](document-templates.md)** - Template creation guide
- **[Image Support](image-support.md)** - Advanced image features
- **[Error Handling](error-handling.md)** - Debugging and troubleshooting
- **[Integration Guide](integration.md)** - Docker Compose integration

### External Resources

- **[Jinja2 Documentation](https://jinja.palletsprojects.com/)** - Template syntax reference
- **[docxtpl Documentation](https://docxtpl.readthedocs.io/)** - Python templating library
- **[Gotenberg Documentation](https://gotenberg.dev/)** - PDF conversion service