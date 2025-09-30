# Production Deployment Guide

Complete guide for deploying Fast Embedding API in production using Docker.

## 🚀 Quick Start with Docker

### Option 1: Docker Compose (Recommended)

```bash
# Build and start the service
docker-compose up -d

# Check logs
docker-compose logs -f

# Check health
curl http://localhost:8000/health

# Stop the service
docker-compose down
```

### Option 2: Docker Build & Run

```bash
# Build the image
docker build -t fast-embedding:latest --target production .

# Run the container
docker run -d \
  --name fast-embedding \
  -p 8000:8000 \
  -e ENABLE_RATE_LIMIT=true \
  -e CORS_ORIGINS=https://yourdomain.com \
  -v model_cache:/app/.cache/fastembed \
  fast-embedding:latest

# Check logs
docker logs -f fast-embedding
```

## 🔧 Production Configuration

### Environment Variables for Production

Create a `.env` file with production settings:

```bash
# API Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Required Models
REQUIRED_MODELS=BAAI/bge-small-en-v1.5,BAAI/bge-base-en-v1.5,sentence-transformers/all-MiniLM-L6-v2

# Security (CRITICAL!)
ALLOWED_MODELS=BAAI/bge-small-en-v1.5,BAAI/bge-base-en-v1.5,sentence-transformers/all-MiniLM-L6-v2
ENABLE_CORS=true
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
ENABLE_RATE_LIMIT=true
RATE_LIMIT_REQUESTS=100

# Performance
THREAD_POOL_WORKERS=4  # Match CPU cores
MAX_TEXT_LENGTH=8192
MAX_BATCH_SIZE=32
REQUEST_TIMEOUT=300

# Cache
MODEL_CACHE_TTL=3600
MAX_CACHED_MODELS=5
CLEANUP_INTERVAL=60

# Monitoring
ENABLE_METRICS=true
```

### Docker Compose with Environment File

```bash
# Use .env file
docker-compose --env-file .env up -d
```

## 🏗️ Multi-Stage Build Explained

The Dockerfile uses multi-stage builds for optimization:

1. **base**: Base Python image with system dependencies
2. **dependencies**: Installs Python packages
3. **production**: Minimal runtime image (default)
4. **development**: Development environment with testing tools

### Build specific target:

```bash
# Production build (default)
docker build -t fast-embedding:prod --target production .

# Development build
docker build -t fast-embedding:dev --target development .
```

## 🔐 Security Best Practices

### 1. Use Non-Root User

The Dockerfile already creates and uses a non-root user (`appuser`).

### 2. Set Specific CORS Origins

```bash
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
# Never use "*" in production!
```

### 3. Enable Rate Limiting

```bash
ENABLE_RATE_LIMIT=true
RATE_LIMIT_REQUESTS=100  # Adjust based on your needs
```

### 4. Use Model Whitelist

```bash
ALLOWED_MODELS=BAAI/bge-small-en-v1.5,BAAI/bge-base-en-v1.5
```

### 5. Use HTTPS (Reverse Proxy)

Always use HTTPS in production. See nginx configuration below.

## 📊 Resource Limits

### Docker Compose Resource Limits

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G
    reservations:
      cpus: '2'
      memory: 2G
```

### Adjust Based on Your Needs

- **Small deployment**: 2 CPUs, 2GB RAM
- **Medium deployment**: 4 CPUs, 4GB RAM
- **Large deployment**: 8 CPUs, 8GB RAM

Each model requires approximately 100-500MB of memory.

## 🔄 High Availability Setup

### Multiple Workers with Nginx Load Balancer

1. **Update docker-compose.yml** to create multiple replicas:

    ```yaml
    services:
    fast-embedding:
        # ... configuration ...
        deploy:
        mode: replicated
        replicas: 3  # Run 3 instances

    nginx:
        image: nginx:alpine
        ports:
        - "80:80"
        - "443:443"
        volumes:
        - ./nginx.conf:/etc/nginx/nginx.conf:ro
        - ./ssl:/etc/nginx/ssl:ro
        depends_on:
        - fast-embedding
    ```

2. **Use the provided nginx.conf** for load balancing

3. **Start the stack**:

    ```bash
    docker-compose up -d --scale fast-embedding=3
    ```

## 🐳 Docker Best Practices

### 1. Multi-Stage Builds ✅

- Reduces final image size
- Separates build and runtime dependencies
- Included in Dockerfile

### 2. Layer Caching ✅

- Dependencies installed before copying code
- Faster rebuilds

### 3. .dockerignore ✅

- Excludes unnecessary files
- Reduces build context size

### 4. Health Checks ✅

- Built into Dockerfile and docker-compose
- Monitors container health

### 5. Volume for Model Cache ✅

- Persists downloaded models
- Faster container restarts

## 📈 Monitoring in Production

### 1. Health Checks

```bash
# Manual check
curl http://localhost:8000/health

# Docker health check
docker inspect --format='{{.State.Health.Status}}' fast-embedding
```

### 2. Metrics Collection

```bash
# View metrics
curl http://localhost:8000/metrics
```

### 3. Log Aggregation

```bash
# View logs
docker-compose logs -f fast-embedding

# Export to file
docker-compose logs fast-embedding > logs.txt
```

### 4. Monitoring Tools Integration

**Prometheus** (optional):

- Expose `/metrics` endpoint
- Configure Prometheus to scrape metrics
- Set up Grafana dashboards

**ELK Stack** (optional):

- Forward container logs to Elasticsearch
- Visualize with Kibana

## 🚦 Deployment Strategies

### Blue-Green Deployment

```bash
# Deploy new version (green)
docker-compose -f docker-compose.yml -f docker-compose.green.yml up -d

# Test the new version
curl http://localhost:8001/health

# Switch traffic (update load balancer)
# ...

# Remove old version (blue)
docker-compose -f docker-compose.blue.yml down
```

### Rolling Update

```bash
# Update one container at a time
docker-compose up -d --no-deps --scale fast-embedding=3 --force-recreate fast-embedding
```

### Canary Deployment

Use nginx to route percentage of traffic to new version.

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: docker build -t fast-embedding:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          docker tag fast-embedding:${{ github.sha }} registry.example.com/fast-embedding:latest
          docker push registry.example.com/fast-embedding:latest
      
      - name: Deploy
        run: |
          ssh user@server 'docker-compose pull && docker-compose up -d'
```

## 🔒 SSL/TLS Configuration

### Using Let's Encrypt with Nginx

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Obtain certificate
certbot --nginx -d yourdomain.com

# Auto-renewal (cron)
0 12 * * * certbot renew --quiet
```

### Update nginx.conf for HTTPS (uncomment HTTPS server block)

## 🧪 Testing Production Build

### 1. Build the image

```bash
docker build -t fast-embedding:test --target production .
```

### 2. Run tests

```bash
# Start container
docker run -d --name test-api -p 8000:8000 fast-embedding:test

# Wait for startup
sleep 30

# Run tests
pytest test_api.py -v

# Cleanup
docker stop test-api && docker rm test-api
```

## 📊 Performance Tuning for Production

### 1. CPU Optimization

```bash
# Set workers based on CPU cores
THREAD_POOL_WORKERS=8  # For 8-core machine

# Docker CPU limits
docker run --cpus=4 ...
```

### 2. Memory Optimization

```bash
# Adjust cache size
MAX_CACHED_MODELS=10  # If you have RAM

# Docker memory limits
docker run --memory=4g ...
```

### 3. Network Optimization

- Use nginx for connection pooling
- Enable gzip compression (in nginx.conf)
- Use HTTP/2 (in nginx.conf)

## 🆘 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs fast-embedding

# Common issues:
# 1. Models downloading (wait 1-2 minutes)
# 2. Port already in use (change PORT)
# 3. Insufficient memory (increase limits)
```

### Out of Memory

```bash
# Reduce cache
MAX_CACHED_MODELS=2

# Increase Docker memory limit
docker-compose down
# Edit docker-compose.yml: memory: 8G
docker-compose up -d
```

### Slow Startup

```bash
# Models are downloaded on first start
# Subsequent starts are much faster

# Use volume to persist models
docker run -v model_cache:/app/.cache/fastembed ...
```

## 📋 Production Checklist

- [ ] Set specific `CORS_ORIGINS` (not `*`)
- [ ] Enable `RATE_LIMIT`
- [ ] Set `ALLOWED_MODELS` whitelist
- [ ] Configure proper `LOG_LEVEL`
- [ ] Set resource limits (CPU, memory)
- [ ] Enable HTTPS with valid certificate
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation
- [ ] Set up automated backups (if needed)
- [ ] Test health check endpoint
- [ ] Test metrics endpoint
- [ ] Configure firewall rules
- [ ] Set up automated updates
- [ ] Document deployment procedure
- [ ] Create disaster recovery plan

## 🌐 Cloud Deployment

### AWS ECS/Fargate

```bash
# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.region.amazonaws.com
docker tag fast-embedding:latest <account>.dkr.ecr.region.amazonaws.com/fast-embedding:latest
docker push <account>.dkr.ecr.region.amazonaws.com/fast-embedding:latest

# Deploy to ECS (use task definition)
```

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/fast-embedding

# Deploy
gcloud run deploy fast-embedding \
  --image gcr.io/PROJECT-ID/fast-embedding \
  --platform managed \
  --memory 4Gi \
  --cpu 4
```

### Azure Container Instances

```bash
# Push to ACR
az acr build --registry myregistry --image fast-embedding:latest .

# Deploy
az container create \
  --resource-group myResourceGroup \
  --name fast-embedding \
  --image myregistry.azurecr.io/fast-embedding:latest \
  --cpu 4 \
  --memory 4
```


---

**Last Updated**: 2025-09-30  
**Recommended for**: Production deployments with Docker