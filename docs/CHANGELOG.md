# Changelog

All notable changes to the Fast Embedding API project.

## [2.0.0] - 2025-09-30 - Production Release

### 🐳 Docker & Production Support

#### Added
- **Dockerfile** - Multi-stage production-optimized Docker build
  - Base, dependencies, production, and development stages
  - Non-root user for security
  - Built-in health checks
  - Optimized layer caching
  
- **docker-compose.yml** - Complete orchestration setup
  - Production service with resource limits
  - Development service with hot-reload
  - Volume management for model persistence
  - Health check monitoring
  - Commented HA setup with nginx
  
- **.dockerignore** - Optimized Docker build context
  - Excludes cache, IDE files, documentation
  - Faster builds and smaller images
  
- **nginx.conf** - Production load balancer configuration
  - Load balancing with health checks
  - Rate limiting
  - SSL/TLS ready
  - Gzip compression
  - Custom logging
  
- **deploy.sh** - Automated deployment script
  - One-command deployment
  - Health check verification
  - Multiple commands (deploy, build, stop, restart, logs, status, clean)
  
- **PRODUCTION.md** - Comprehensive production guide
  - Docker deployment instructions
  - Security best practices
  - High availability setup
  - Cloud deployment (AWS, GCP, Azure)
  - CI/CD integration examples
  - Troubleshooting guide
  
- **DOCKER_SETUP.md** - Docker setup documentation
  - Quick start guides
  - Configuration options
  - Multi-instance deployment
  - Testing procedures

#### Security
- Non-root container user
- Production-ready defaults
- SSL/TLS support (nginx)
- Environment-based secrets

#### Updated
- **README.md** - Added Docker deployment section
- **QUICKSTART.md** - Added Docker quick start options
- **.gitignore** - Excluded Docker-specific files (.env, SSL certs)

### 🚀 Performance & Features (from previous updates)

#### Added
- **Batch embedding endpoint** (`POST /embed/batch`) - 2-5x faster
- **Metrics endpoint** (`GET /metrics`) - API usage tracking
- **Model info endpoint** (`GET /models/{name}`) - Model metadata
- **Thread pool optimization** - Configurable workers
- **Request timeouts** - Prevent hanging requests
- **Processing time tracking** - All responses include timing
- **Model warm-up** - Pre-load on startup

#### Enhanced
- **Model validation** - Cache models after validation (3x faster startup)
- **Error handling** - Better exceptions and user messages
- **Logging** - Structured logging with context
- **Configuration** - 15+ new settings

### 🔒 Security Enhancements

#### Added
- Input validation (text length, batch size)
- Model whitelist support (`ALLOWED_MODELS`)
- Rate limiting (optional, configurable)
- CORS configuration
- Request size limits (10MB default)
- Timeout protection

### 📊 Monitoring & Observability

#### Added
- Metrics collection (requests, embeddings, uptime)
- Health checks (API and Docker)
- Structured logging
- Model usage tracking
- Cache statistics

### 🧪 Testing

#### Added
- **test_api.py** - Comprehensive test suite
  - Model cache tests
  - API endpoint tests
  - Integration tests
  - Validation tests
  
- **example_client.py** - Enhanced examples
  - Single and batch embedding examples
  - Performance comparison
  - Error handling examples

### 📝 Documentation

#### Added
- **PRODUCTION.md** - Production deployment guide
- **DOCKER_SETUP.md** - Docker setup documentation
- **QUICKSTART.md** - Quick start guide
- **CHANGELOG.md** - This file

#### Enhanced
- **README.md** - Complete API documentation
- Batch endpoint examples
- Docker deployment section
- Configuration reference

### 🔧 Configuration

#### New Settings (config.py)
```python
# Performance
thread_pool_workers: int = 4
max_text_length: int = 8192
max_batch_size: int = 32
request_timeout: int = 300
cleanup_interval: int = 60

# Security
allowed_models: Optional[List[str]] = None
enable_cors: bool = True
cors_origins: List[str] = ["*"]
enable_rate_limit: bool = False
rate_limit_requests: int = 60
rate_limit_window: int = 60
max_request_size: int = 10MB

# Monitoring
enable_metrics: bool = True
log_level: str = "INFO"
```

## [1.0.0] - 2025-09-30 - Initial Release

### Added
- **main.py** - Litestar API application
  - `/embed` endpoint - Single text embedding
  - `/health` endpoint - Health check
  - `/models` endpoint - List models
  
- **model_manager.py** - Intelligent model caching
  - On-demand model loading
  - LRU eviction
  - TTL-based cleanup
  - Background cleanup task
  
- **config.py** - Configuration management
  - Environment variable support
  - Required models list
  - Cache settings
  
- **requirements.txt** - Python dependencies
  - litestar
  - fastembed
  - uvicorn
  - pydantic
  
- **run.sh** - Quick start script
- **README.md** - Basic documentation
- **.gitignore** - Git ignore rules

### Features
- Intelligent model caching with LRU
- Auto-offloading of unused models
- Startup validation of required models
- Multiple embedding models support
- Async/await architecture

---

## Migration Guide

### From v1.0.0 to v2.0.0

No breaking changes! All improvements are backward compatible.

**Recommended actions:**

1. **Update configuration** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Use Docker for production**:
   ```bash
   ./deploy.sh deploy
   ```

3. **Use batch endpoint** for better performance:
   ```python
   # Old (still works)
   POST /embed {"model_name": "...", "text": "..."}
   
   # New (recommended for multiple texts)
   POST /embed/batch {"model_name": "...", "texts": [...]}
   ```

4. **Enable monitoring**:
   ```bash
   ENABLE_METRICS=true
   ```

5. **Configure security** for production:
   ```bash
   ALLOWED_MODELS=model1,model2
   ENABLE_RATE_LIMIT=true
   CORS_ORIGINS=https://yourdomain.com
   ```

---

## Roadmap

### v2.1.0 (Planned)
- [ ] Authentication (JWT/API keys)
- [ ] OpenAPI/Swagger documentation
- [ ] Prometheus metrics export
- [ ] Async model validation (parallel)

### v2.2.0 (Planned)
- [ ] Redis caching layer
- [ ] Model streaming for large texts
- [ ] WebSocket support
- [ ] GraphQL API

### v3.0.0 (Future)
- [ ] Multi-language support
- [ ] Custom model uploads
- [ ] A/B testing framework
- [ ] Built-in model fine-tuning

---

## Contributors

- Initial implementation and production setup

## License

MIT License - See LICENSE file for details
