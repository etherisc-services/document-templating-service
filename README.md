# 🚀 Document Template Processing Service

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-1.1.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://hub.docker.com)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](./LICENSE)
[![Documentation](https://img.shields.io/badge/Documentation-Available-green?style=for-the-badge)](./docs/)

A lightweight microservice for processing Word document templates with data injection and PDF conversion. Combines the power of [docxtpl](https://docxtpl.readthedocs.io/) templating with [Gotenberg](https://gotenberg.dev) PDF generation.

## ✨ Features

- 📄 Process `.docx` templates with dynamic data
- 🔄 Convert results to PDF automatically  
- 🚀 Fast REST API built with FastAPI
- 🐳 Docker-ready with compose setup
- ☸️ Kubernetes deployment manifests
- 📚 Comprehensive documentation and examples

## 🚀 Quick Start

```bash
# Clone and start with Docker Compose
git clone <repository-url>
cd document-templating-service
docker compose up -d

# API will be available at http://localhost:8000/docs
```

## 📖 Documentation

- **[📋 Installation Guide](docs/installation.md)** - Complete setup instructions
- **[🔧 Usage Guide](docs/usage.md)** - API documentation and templating examples
- **[📑 API Docs](http://localhost:8000/docs)** - Interactive API documentation (when running)

## 🛠️ Technology Stack

- **Backend:** FastAPI 0.115.6, Python 3.12
- **Templating:** docxtpl 0.19.0 (Jinja2-based)
- **PDF Generation:** Gotenberg 8
- **Deployment:** Docker, Kubernetes

## 📊 Updated Dependencies (v1.1.0)

This version includes major dependency updates:
- Python 3.8 → 3.12
- FastAPI 0.68.0 → 0.115.6  
- Pydantic 1.8.2 → 2.10.3
- All dependencies updated to latest stable versions

## 🤝 Contributing

Feel free to open issues and pull requests. Please include a description with your PR.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Original Author

**Etherisc GmbH** (Originally created by [M.B.C.M (PapiHack)](https://github.com/PapiHack))  
[![Twitter](https://img.shields.io/twitter/follow/the_it_dev?style=social)](https://twitter.com/the_it_dev)

---

> 💡 **Need help?** Check the [documentation](docs/) or open an issue!
