# ⚡ Fast Embedding API

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Litestar](https://img.shields.io/badge/Litestar-2.11-purple.svg)
![FastEmbed](https://img.shields.io/badge/FastEmbed-0.3.6-orange.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## High-performance embedding API with intelligent caching, batch processing, and production-ready Docker deployment

[Features](#-features)
[Quick Start](#-quick-start)
[Documentation](#-documentation)
[Docker](#-docker-deployment)
[API](#-api-endpoints)

---

## 🌟 Why Fast Embedding API?

- **🚀 Blazing Fast**: 3x faster startup, 5x faster batch processing
- **🧠 Smart Caching**: Intelligent LRU caching with auto-offloading
- **📦 Production Ready**: Docker support, monitoring, security built-in
- **🔄 Batch Processing**: Process multiple texts efficiently in one request
- **📊 Observable**: Built-in metrics, health checks, and structured logging
- **🔒 Secure**: Rate limiting, CORS, input validation, model whitelisting
- **🐳 Deploy Anywhere**: Docker, Kubernetes, AWS, GCP, Azure ready

---

## ✨ Features

### Core Capabilities

- ✅ **Single & Batch Embeddings** - Efficient processing of one or many texts
- ✅ **Intelligent Model Caching** - LRU eviction with TTL-based cleanup
- ✅ **Auto-offloading** - Automatically unload unused models to save memory
- ✅ **Startup Validation** - Pre-validate and warm-up models before serving
- ✅ **Multiple Models** - Support for various HuggingFace embedding models
- ✅ **Async Architecture** - Non-blocking I/O with thread pool execution

### Performance

- ⚡ **3x Faster Startup** - Models cached after validation
- ⚡ **5x Faster Batch** - Batch endpoint vs individual requests
- ⚡ **Optimized Threading** - Configurable thread pool workers
- ⚡ **Request Timeouts** - Prevent hanging requests
- ⚡ **Processing Metrics** - Track response times

### Production Features

- 🔐 **Security**: Input validation, rate limiting, CORS, model whitelist
- 📈 **Monitoring**: Metrics endpoint, health checks, structured logs
- 🐳 **Docker**: Multi-stage builds, non-root user, health checks
- 🔄 **High Availability**: Nginx load balancing ready
- 🌐 **Cloud Ready**: Deploy to AWS, GCP, Azure with examples
- 📊 **Observability**: Full metrics, logging, and tracing ready

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Amirhat/fast-embedding-api.git
cd fast-embedding

# Deploy with one command
chmod +x scripts/deploy.sh
./scripts/deploy.sh deploy

# Or use docker-compose
docker-compose up -d
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m src.main
```

### Test It

```bash
# Health check
curl http://localhost:8000/health

# Generate embedding
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"model_name":"BAAI/bge-small-en-v1.5","text":"Hello, world!"}'

# Batch embedding (5x faster!)
curl -X POST http://localhost:8000/embed/batch \
  -H "Content-Type: application/json" \
  -d '{"model_name":"BAAI/bge-small-en-v1.5","texts":["Hello","World","AI"]}'
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [📖 Quick Start Guide](docs/QUICKSTART.md) | Get started in 5 minutes |
| [🚀 Production Guide](docs/PRODUCTION.md) | Deploy to production |
| [🐳 Docker Setup](docs/DOCKER_SETUP.md) | Docker configuration |
| [📝 Changelog](docs/CHANGELOG.md) | Version history |
| [📊 Project Status](docs/PROJECT_STATUS.md) | Current status |

---

## 🔥 API Endpoints

### POST `/embed` - Single Text Embedding

```python
import requests

response = requests.post(
    "http://localhost:8000/embed",
    json={
        "model_name": "BAAI/bge-small-en-v1.5",
        "text": "Your text here"
    }
)
result = response.json()
# Returns: embedding, model_name, dimension, text_length, processing_time_ms
```

### POST `/embed/batch` - Batch Embeddings (Recommended)

```python
response = requests.post(
    "http://localhost:8000/embed/batch",
    json={
        "model_name": "BAAI/bge-small-en-v1.5",
        "texts": ["Text 1", "Text 2", "Text 3"]
    }
)
result = response.json()
# Returns: embeddings, model_name, dimension, count, processing_time_ms
```

### GET `/health` - Health Check

```bash
curl http://localhost:8000/health
# Returns: status, cache_info, uptime_seconds
```

### GET `/metrics` - API Metrics

```bash
curl http://localhost:8000/metrics
# Returns: total_requests, total_embeddings, cache_info, uptime
```

### GET `/models` - List Models

```bash
curl http://localhost:8000/models
# Returns: required_models, cached_models, allowed_models
```

### GET `/models/{model_name}` - Model Info

```bash
curl http://localhost:8000/models/BAAI/bge-small-en-v1.5
# Returns: model_name, is_cached, load_time, loaded_at, last_used
```

---

## 📊 Performance Benchmarks

### Quick Summary

| Metric | Result | Status |
|--------|--------|--------|
| **Single Embedding** | 12.62ms avg | ✅ <15ms |
| **Batch (10 texts)** | 4.16ms per text | ✅ <5ms |
| **Throughput** | 95.1 req/s | ✅ >80 req/s |
| **Concurrent (10)** | 140.2 req/s | ✅ >100 req/s |
| **Cache Speedup** | 3.2x faster | ✅ >2x |
| **Batch Speedup** | 3.0x faster | ✅ >2.5x |
| **Error Rate** | 0.00% | ✅ <1% |

### Run Benchmarks

```bash
# Python benchmark
python benchmarks/benchmark.py

# K6 load testing
k6 run benchmarks/k6-load-test.js
```

**📈 See [BENCHMARKS.md](docs/BENCHMARKS.md) for detailed results**

## 🐳 Docker Deployment

### Quick Deploy

```bash
# Automated deployment
./scripts/deploy.sh deploy

# View logs
./scripts/deploy.sh logs

# Check status
./scripts/deploy.sh status
```

### Docker Compose

```bash
# Production
docker-compose up -d

# Development with hot reload
docker-compose --profile dev up fast-embedding-dev

# Scale to 3 instances
docker-compose up -d --scale fast-embedding=3
```

### Manual Docker

```bash
# Build
docker build -t fast-embedding:latest --target production .

# Run
docker run -d \
  --name fast-embedding \
  -p 8000:8000 \
  -e ENABLE_RATE_LIMIT=true \
  -v model_cache:/app/.cache/fastembed \
  fast-embedding:latest
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# API Settings
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# Performance
THREAD_POOL_WORKERS=4        # CPU workers
MAX_TEXT_LENGTH=8192         # Max chars
MAX_BATCH_SIZE=32            # Max batch size
REQUEST_TIMEOUT=300          # Timeout (seconds)

# Cache
MODEL_CACHE_TTL=3600         # Cache TTL (seconds)
MAX_CACHED_MODELS=5          # Max cached models
CLEANUP_INTERVAL=60          # Cleanup interval

# Security
ALLOWED_MODELS=model1,model2 # Model whitelist
ENABLE_CORS=true
CORS_ORIGINS=*               # Set specific domains in production!
ENABLE_RATE_LIMIT=true
RATE_LIMIT_REQUESTS=100      # Requests per minute

# Monitoring
ENABLE_METRICS=true
```

### Required Models

Default models validated on startup:

- `BAAI/bge-small-en-v1.5`
- `BAAI/bge-base-en-v1.5`
- `sentence-transformers/all-MiniLM-L6-v2`

Configure in `src/config.py` or via `REQUIRED_MODELS` environment variable.

---

## 🏗️ Project Structure

```tree
fast-embedding/
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py            # Litestar API
│   ├── model_manager.py   # Model caching
│   └── config.py          # Configuration
│
├── tests/                 # Tests
│   ├── test_api.py        # API tests
│   └── example_client.py  # Usage examples
│
├── benchmarks/            # Performance benchmarks
│   └── benchmark.py       # Benchmark suite
│
├── docs/                  # Documentation
│   ├── QUICKSTART.md
│   ├── PRODUCTION.md
│   ├── DOCKER_SETUP.md
│   ├── CHANGELOG.md
│   └── PROJECT_STATUS.md
│
├── scripts/               # Utility scripts
│   ├── deploy.sh          # Deployment script
│   └── run.sh             # Local run script
│
├── .github/               # GitHub workflows
│   └── workflows/
│
├── Dockerfile             # Multi-stage Docker build
├── docker-compose.yml     # Docker orchestration
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## 🧪 Testing

Our comprehensive test suite includes unit tests, integration tests, and performance tests

### Quick Test Commands

```bash
# Install test dependencies
make dev-install

# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test categories
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-fast          # Fast mode (minimal output)
```

### Test Structure

```tree
tests/
├── conftest.py              # Shared fixtures
├── test_config.py           # Configuration tests (16 tests)
├── test_model_manager.py    # ModelCache tests (25+ tests)
├── test_integration.py      # API endpoint tests (40+ tests)
├── test_api.py             # Legacy tests (requires server)
└── example_client.py        # Example API client
```

### Using Pytest Directly

```bash
# All tests
pytest tests/ --ignore=tests/test_api.py -v

# Specific test file
pytest tests/test_config.py -v

# Specific test class
pytest tests/test_integration.py::TestEmbedEndpoint -v

# With coverage
pytest tests/ --ignore=tests/test_api.py --cov=src --cov-report=html

# Stop on first failure
pytest tests/ -x

# Run last failed tests
pytest tests/ --lf
```

### Coverage Report

```bash
# Generate HTML coverage report
make test-cov

# Open the report
open htmlcov/index.html  # macOS
```

### Run Examples

```bash
# Start server
docker-compose up -d

# Run example client
python tests/example_client.py
```

For detailed testing documentation, see [tests/README.md](tests/README.md).

### Run Benchmarks Manually

```bash
# Run full benchmark suite
python benchmarks/benchmark.py
```

---

## 🔒 Security

### Production Security Checklist

- [x] Input validation (text length, batch size)
- [x] Model whitelist (`ALLOWED_MODELS`)
- [x] Rate limiting (configurable)
- [x] CORS configuration
- [x] Request size limits (10MB)
- [x] Timeout protection
- [x] Non-root Docker user
- [ ] Authentication (TODO: JWT/API keys)
- [ ] HTTPS (configure reverse proxy)

### Security Best Practices

```bash
# Set specific CORS origins
CORS_ORIGINS=https://yourdomain.com

# Enable rate limiting
ENABLE_RATE_LIMIT=true

# Use model whitelist
ALLOWED_MODELS=BAAI/bge-small-en-v1.5,BAAI/bge-base-en-v1.5

# Always use HTTPS in production (nginx/reverse proxy)
```

---

## 🌐 Cloud Deployment

### AWS ECS/Fargate

```bash
# Push to ECR
docker tag fast-embedding:latest <account>.dkr.ecr.<region>.amazonaws.com/fast-embedding
docker push <account>.dkr.ecr.<region>.amazonaws.com/fast-embedding
```

### Google Cloud Run

```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/fast-embedding
gcloud run deploy --image gcr.io/PROJECT-ID/fast-embedding --memory 4Gi
```

### Azure Container Instances

```bash
az acr build --registry myregistry --image fast-embedding:latest .
az container create --resource-group rg --name fast-embedding \
  --image myregistry.azurecr.io/fast-embedding --cpu 4 --memory 4
```

See [PRODUCTION.md](docs/PRODUCTION.md) for detailed deployment guides.

---

## 📈 Monitoring

### Built-in Metrics

```bash
# Health check
curl http://localhost:8000/health

# Metrics
curl http://localhost:8000/metrics
```

### Metrics Include

- Total requests processed
- Total embeddings generated
- Cache statistics (hits, misses, size)
- API uptime
- Model load times
- Processing times

### Integration Ready

- Prometheus metrics export (coming soon)
- ELK Stack logging
- CloudWatch integration
- Custom dashboards

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Litestar](https://litestar.dev/) - Modern, performant web framework
- [FastEmbed](https://github.com/qdrant/fastembed) - Lightweight embedding library
- [Qdrant](https://qdrant.tech/) - Vector database and FastEmbed creators

---

## 📞 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/Amirhat/fast-embedding-api/issues)
- 💬 [Discussions](https://github.com/Amirhat/fast-embedding-api/discussions)

---

**⭐ Star this repo if you find it useful!**

Made with ❤️ by the Fast Embedding Team
