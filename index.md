---
layout: default
title: Home
nav_order: 1
description: "Document Template Processing Service - A lightweight microservice for processing Word document templates with data injection and PDF conversion."
permalink: /
---

# Document Template Processing Service
{: .fs-9 }

A lightweight microservice for processing Word document templates with data injection and PDF conversion.
{: .fs-6 .fw-300 }

[Get started now](#getting-started){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View on GitHub](https://github.com/etherisc-services/document-templating-service){: .btn .fs-5 .mb-4 .mb-md-0 }

---

## Features

✨ **Easy Template Processing**: Transform Word documents with dynamic data injection  
🔄 **Automatic PDF Conversion**: Seamless conversion to PDF using Gotenberg  
🚀 **Fast REST API**: Built with FastAPI for high performance  
🐳 **Docker Ready**: Complete containerization with Docker Compose  
☸️ **Kubernetes Support**: Production-ready deployment manifests  

## Technology Stack

- **Backend**: FastAPI 0.115.6, Python 3.12
- **Templating**: docxtpl 0.19.0 (Jinja2-based)
- **PDF Generation**: Gotenberg 8
- **Deployment**: Docker, Kubernetes

---

## Getting Started

### Quick Start with Docker Compose

The fastest way to get up and running:

```bash
git clone https://github.com/etherisc-services/document-templating-service.git
cd document-templating-service
docker compose up -d
```

Your API will be available at:
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/](http://localhost:8000/)

### Next Steps

1. 📖 Read the **[Installation Guide](docs/installation)** for detailed setup options
2. 🔧 Check the **[Usage Guide](docs/usage)** for API documentation and examples
3. 🚀 Start building your document templates!

---

## API Example

Process a Word template with dynamic data:

```bash
curl -X POST \
  http://localhost:8000/api/v1/process-template-document \
  -F "file=@template.docx" \
  -F "data={\"name\":\"John Doe\",\"amount\":150.00}" \
  --output result.pdf
```

---

## Documentation

<div class="code-example" markdown="1">

📋 **[Installation Guide](docs/installation)**  
Complete setup instructions for all environments

🔧 **[Usage Guide](docs/usage)**  
API documentation with templating examples

📑 **[API Reference](http://localhost:8000/docs)**  
Interactive API documentation (when service is running)

</div>

---

## About

This service combines the power of [docxtpl](https://docxtpl.readthedocs.io/) for Word document templating with [Gotenberg](https://gotenberg.dev) for PDF conversion, providing a simple REST API for document processing workflows.

### Original Author

**Etherisc GmbH** (Originally created by [M.B.C.M (PapiHack)](https://github.com/PapiHack))  

---

## Contributing

We welcome contributions! Please feel free to submit a Pull Request. Make sure to include a description with your PR.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/etherisc-services/document-templating-service/blob/master/LICENSE) file for details. 