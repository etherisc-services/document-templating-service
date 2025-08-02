---
layout: default
title: Docker Integration Guide
nav_order: 4
description: "How to integrate the Document Template Processing Service into your existing Docker Compose stack with other containers."
---

# Docker Integration Guide

This guide shows how to integrate the Document Template Processing Service into your existing Docker Compose stack alongside other containers.

## Basic Integration

### Add to Existing docker-compose.yml

Add these services to your existing `docker-compose.yml`:

```yaml
version: '3.8'

services:
  # Your existing services here...
  
  # Document Template Processing Service
  document-templating:
    image: ghcr.io/etherisc-services/document-templating-service:latest
    container_name: document-templating
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - GOTENBERG_API_URL=http://gotenberg:3000
    depends_on:
      - gotenberg
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Gotenberg PDF service
  gotenberg:
    image: gotenberg/gotenberg:8
    container_name: gotenberg
    restart: unless-stopped
    ports:
      - "3000:3000"  # Remove if only used internally
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  app-network:
    driver: bridge
```

## Integration Examples

### With a Web Application

Example integration with a Node.js/Python web application:

```yaml
version: '3.8'

services:
  # Your web application
  webapp:
    build: .
    container_name: my-webapp
    ports:
      - "3000:3000"
    environment:
      - DOCUMENT_SERVICE_URL=http://document-templating:8000
    depends_on:
      - document-templating
      - database
    networks:
      - app-network

  # Database
  database:
    image: postgres:15
    container_name: postgres-db
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  # Document Template Processing Service
  document-templating:
    image: ghcr.io/etherisc-services/document-templating-service:latest
    container_name: document-templating
    restart: unless-stopped
    environment:
      - GOTENBERG_API_URL=http://gotenberg:3000
    depends_on:
      - gotenberg
    networks:
      - app-network
    # No external port exposure - internal access only

  # Gotenberg PDF service
  gotenberg:
    image: gotenberg/gotenberg:8
    container_name: gotenberg
    restart: unless-stopped
    networks:
      - app-network
    # No external port exposure - internal access only

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

### With Reverse Proxy (Nginx)

Example with Nginx as a reverse proxy:

```yaml
version: '3.8'

services:
  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
    depends_on:
      - webapp
      - document-templating
    networks:
      - app-network

  # Your main application
  webapp:
    image: my-webapp:latest
    container_name: webapp
    networks:
      - app-network

  # Document Template Processing Service
  document-templating:
    image: ghcr.io/etherisc-services/document-templating-service:latest
    container_name: document-templating
    restart: unless-stopped
    environment:
      - GOTENBERG_API_URL=http://gotenberg:3000
    depends_on:
      - gotenberg
    networks:
      - app-network

  gotenberg:
    image: gotenberg/gotenberg:8
    container_name: gotenberg
    restart: unless-stopped
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### Example Nginx Configuration

```nginx
events {
    worker_connections 1024;
}

http {
    upstream webapp {
        server webapp:3000;
    }
    
    upstream document-service {
        server document-templating:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Main application
        location / {
            proxy_pass http://webapp;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Document processing API
        location /api/documents/ {
            proxy_pass http://document-service/api/v1/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            
            # Increase timeouts for large document processing
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # Increase max body size for file uploads
            client_max_body_size 50M;
        }
    }
}
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOTENBERG_API_URL` | `http://gotenberg:3000` | Gotenberg service URL |
| `PORT` | `8000` | Service port (internal) |

### Resource Limits

Add resource constraints for production:

```yaml
document-templating:
  image: ghcr.io/etherisc-services/document-templating-service:latest
  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 512M
      reservations:
        cpus: '0.5'
        memory: 256M
  restart: unless-stopped
```

### Volume Mounts

For custom configurations or persistent storage:

```yaml
document-templating:
  image: ghcr.io/etherisc-services/document-templating-service:latest
  volumes:
    # Mount custom templates (if needed)
    - ./templates:/app/templates:ro
    # Mount temporary files to host (optional)
    - ./temp:/app/temp
  environment:
    - GOTENBERG_API_URL=http://gotenberg:3000
```

## Security Considerations

### Internal Network Access

For production setups, avoid exposing ports externally:

```yaml
document-templating:
  image: ghcr.io/etherisc-services/document-templating-service:latest
  # No ports section - internal access only
  networks:
    - internal-network

networks:
  internal-network:
    driver: bridge
    internal: true  # No external access
```

### API Access Control

Use a reverse proxy with authentication:

```nginx
location /api/documents/ {
    # Add authentication
    auth_basic "Document API";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    # Rate limiting
    limit_req zone=api burst=10 nodelay;
    
    proxy_pass http://document-service/api/v1/;
}
```

## Client Integration Examples

### Node.js Client

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function processDocument(templatePath, data) {
  const form = new FormData();
  form.append('file', fs.createReadStream(templatePath));
  form.append('data', JSON.stringify(data));

  try {
    const response = await axios.post(
      'http://document-templating:8000/api/v1/process-template-document',
      form,
      {
        headers: form.getHeaders(),
        responseType: 'stream'
      }
    );
    
    return response.data; // PDF stream
  } catch (error) {
    console.error('Document processing failed:', error);
    throw error;
  }
}
```

### Python Client

```python
import requests
import json

def process_document(template_path, data):
    url = "http://document-templating:8000/api/v1/process-template-document"
    
    with open(template_path, 'rb') as template_file:
        files = {'file': template_file}
        data_payload = {'data': json.dumps(data)}
        
        response = requests.post(url, files=files, data=data_payload)
        
        if response.status_code == 200:
            return response.content  # PDF bytes
        else:
            raise Exception(f"Document processing failed: {response.text}")
```

### Processing Templates with Images

For templates that include images, use the enhanced endpoint:

#### Node.js with Images

```javascript
const axios = require('axios');
const fs = require('fs');

async function processDocumentWithImages(templatePath, templateData, imagePaths) {
  // Convert images to base64
  const images = {};
  for (const [name, path] of Object.entries(imagePaths)) {
    const imageBuffer = fs.readFileSync(path);
    const base64Data = imageBuffer.toString('base64');
    images[name] = {
      data: base64Data,
      width_mm: 50,  // Adjust as needed
      height_mm: 20
    };
  }

  const requestData = {
    template_data: templateData,
    images: images
  };

  const form = new FormData();
  form.append('file', fs.createReadStream(templatePath));
  form.append('request_data', JSON.stringify(requestData));

  try {
    const response = await axios.post(
      'http://document-templating:8000/api/v1/process-template-document',
      form,
      {
        headers: form.getHeaders(),
        responseType: 'stream'
      }
    );
    
    return response.data; // PDF stream
  } catch (error) {
    console.error('Document processing with images failed:', error);
    throw error;
  }
}
```

#### Python with Images

```python
import requests
import json
import base64

def process_document_with_images(template_path, template_data, image_paths):
    url = "http://document-templating:8000/api/v1/process-template-document"
    
    # Convert images to base64
    images = {}
    for name, path in image_paths.items():
        with open(path, 'rb') as img_file:
            base64_data = base64.b64encode(img_file.read()).decode('utf-8')
            images[name] = {
                'data': base64_data,
                'width_mm': 50,  # Adjust as needed
                'height_mm': 20
            }
    
    request_data = {
        'template_data': template_data,
        'images': images
    }
    
    with open(template_path, 'rb') as template_file:
        files = {'file': template_file}
        data_payload = {'request_data': json.dumps(request_data)}
        
        response = requests.post(url, files=files, data=data_payload)
        
        if response.status_code == 200:
            return response.content  # PDF bytes
        else:
            raise Exception(f"Document processing failed: {response.text}")
```

## Monitoring and Logging

### Health Checks

All containers include health checks. Monitor with:

```bash
docker-compose ps
```

### Centralized Logging

Add logging configuration:

```yaml
document-templating:
  image: ghcr.io/etherisc-services/document-templating-service:latest
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

### Prometheus Monitoring

If using Prometheus, add monitoring:

```yaml
# Add to your existing monitoring stack
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
```

## Troubleshooting

### Common Issues

1. **Service can't reach Gotenberg:**
   ```bash
   docker-compose logs gotenberg
   docker-compose exec document-templating curl -f http://gotenberg:3000/health
   ```

2. **Network connectivity issues:**
   ```bash
   docker network ls
   docker network inspect your-network-name
   ```

3. **Resource constraints:**
   ```bash
   docker stats
   ```

### Debug Mode

Run with debug logging:

```yaml
document-templating:
  image: ghcr.io/etherisc-services/document-templating-service:latest
  environment:
    - DEBUG=true
    - LOG_LEVEL=debug
```

## Production Deployment

### Full Production Example

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
    depends_on:
      - webapp
      - document-templating
    networks:
      - frontend
      - backend
    restart: unless-stopped

  webapp:
    image: your-app:latest
    networks:
      - frontend
      - backend
    depends_on:
      - database
      - document-templating
    restart: unless-stopped

  document-templating:
    image: ghcr.io/etherisc-services/document-templating-service:latest
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
    environment:
      - GOTENBERG_API_URL=http://gotenberg:3000
    depends_on:
      - gotenberg
    networks:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  gotenberg:
    image: gotenberg/gotenberg:8
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
    networks:
      - backend
    restart: unless-stopped

  database:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend
    secrets:
      - db_password
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

This production setup includes security, monitoring, resource limits, and proper network isolation. 