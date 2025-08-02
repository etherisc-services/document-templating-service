---
layout: default
title: Documentation
nav_order: 1
description: "Documentation home for the Document Template Processing Service."
---

# Documentation

Welcome to the Document Template Processing Service documentation.

## Quick Start

1. **[Installation](installation.html)** - Get the service running
2. **[Usage Guide](usage.html)** - Quick start and overview
3. **[API Endpoints](api-endpoints.html)** - Complete API reference
4. **[Document Templates](document-templates.html)** - Create Jinja2 templates
5. **[Examples](examples.html)** - Working code samples

## Comprehensive Guides

### 🚀 **[Installation Guide](installation.html)**
Complete setup instructions from local development to production deployment.

### 📋 **[Usage Guide](usage.html)**
Quick start guide with essential concepts and links to detailed sections.

### 🔌 **[API Endpoints](api-endpoints.html)**
Complete API reference with parameters, responses, and examples for all endpoints.

### 📄 **[Document Templates](document-templates.html)**
Learn how to create Word templates with Jinja2 syntax:
- Variable substitution and conditional logic
- Loops and advanced template patterns
- Best practices and troubleshooting

### 🖼️ **[Image Support](image-support.html)**
Advanced image processing capabilities:
- Base64 encoding for React applications
- Size specifications and optimization
- Template integration and troubleshooting

### 🚫 **[Error Handling](error-handling.html)**
Understanding and debugging errors:
- HTTP status codes and error types
- Structured error responses
- Common issues and debugging strategies

### 💡 **[Examples](examples.html)**
Complete practical examples:
- Invoice generation with complex data
- React, Node.js, and Python integration
- Postman testing and real-world use cases

### 🐳 **[Integration Guide](integration.html)**
Docker Compose setup and integration patterns for existing applications.

---

## Architecture Overview

The service combines three powerful technologies:

- **[docxtpl](https://docxtpl.readthedocs.io/)** - Python library for Word template processing
- **[Jinja2](https://jinja.palletsprojects.com/)** - Template engine for dynamic content
- **[Gotenberg](https://gotenberg.dev/)** - Microservice for PDF conversion

## Features

✅ **Unified API** - Single endpoint with smart mode detection  
✅ **Image Support** - Inline images with Base64 encoding  
✅ **Error Handling** - Comprehensive error reporting  
✅ **Docker Ready** - Complete containerization  
✅ **React Friendly** - Optimized for modern web applications  
✅ **Backward Compatible** - No breaking changes for existing integrations  

---

## Quick Links

- **[GitHub Repository](https://github.com/etherisc-services/document-templating-service)**
- **[Docker Images](https://ghcr.io/etherisc-services/document-templating-service)**
- **[Live Service](http://localhost:8000)** (when running locally)

## Support

For questions and support:
1. Check the **[Error Handling](error-handling.html)** guide
2. Try the **[Examples](examples.html)** for working code
3. Review the **[API Endpoints](api-endpoints.html)** reference
4. Create an issue in the GitHub repository

---

*Copyright © 2024, Etherisc GmbH*
*Originally created by [M.B.C.M (PapiHack)](https://github.com/PapiHack)*