# Quick Start Guide

Get the Fast Embedding API running in minutes!

## 🚀 5-Minute Setup

Choose your preferred deployment method:

### Option A: Docker (Recommended for Production)

```bash
# Quick deploy
./deploy.sh

# Or use docker-compose
docker-compose up -d

# Check status
curl http://localhost:8000/health
```

The API will start on `http://localhost:8000`

### Option B: Local Development

#### Step 1: Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Start the Server

```bash
# Quick start (uses defaults)
python -m src.main

# Or use the convenience script
chmod +x run.sh
./run.sh
```

The API will start on `http://localhost:8000`

#### Step 3: Test It

```bash
# In another terminal, run the example client
python example_client.py
```

Or use curl:

```bash
curl -X POST "http://localhost:8000/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "BAAI/bge-small-en-v1.5",
    "text": "Hello, world!"
  }'
```

## 📊 What Happens on Startup

1. ✅ API starts
2. ✅ Model cache initializes
3. ✅ Required models are validated and pre-loaded (this takes ~30-60s on first run)
4. ✅ Background cleanup task starts
5. ✅ API is ready to serve requests

**Note**: First startup takes longer as models are downloaded. Subsequent starts are much faster!

## 🎯 Common Use Cases

### 1. Single Text Embedding

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
embedding = result["embedding"]  # List of floats
```

### 2. Batch Embeddings (Recommended for Multiple Texts)

```python
import requests

response = requests.post(
    "http://localhost:8000/embed/batch",
    json={
        "model_name": "BAAI/bge-small-en-v1.5",
        "texts": ["Text 1", "Text 2", "Text 3"]
    }
)
result = response.json()
embeddings = result["embeddings"]  # List of embedding vectors
```

### 3. Check Health & Cache Status

```bash
curl http://localhost:8000/health
```

### 4. View Metrics

```bash
curl http://localhost:8000/metrics
```

## ⚙️ Basic Configuration

Create a `.env` file:

```bash
# Copy example
cp .env.example .env

# Edit with your preferences
nano .env
```

Essential settings:

```env
# API
PORT=8000
DEBUG=false

# Performance
THREAD_POOL_WORKERS=4  # Adjust based on CPU cores
MAX_CACHED_MODELS=5

# Security (for production)
ALLOWED_MODELS=BAAI/bge-small-en-v1.5,BAAI/bge-base-en-v1.5
CORS_ORIGINS=https://yourdomain.com
ENABLE_RATE_LIMIT=true
```

## 🔍 Troubleshooting

### Models Not Loading?

**Issue**: "Failed to validate required models"

**Solution**:

1. Check internet connection (models download from HuggingFace)
2. Wait for download to complete (first time only)
3. Check disk space (models are ~100-500MB each)
4. Check logs for specific error messages

### Out of Memory?

**Issue**: API crashes or slows down

**Solution**:

1. Reduce `MAX_CACHED_MODELS` in config
2. Reduce `MODEL_CACHE_TTL` to free memory faster
3. Use smaller models (e.g., `bge-small` instead of `bge-large`)
4. Increase available RAM

### Slow Performance?

**Issue**: Requests are slow

**Solution**:

1. Use `/embed/batch` for multiple texts (2-5x faster)
2. Increase `THREAD_POOL_WORKERS` (match CPU cores)
3. Ensure models are cached (check `/health` endpoint)
4. Use multiple uvicorn workers: `uvicorn main:app --workers 4`

### Port Already in Use?

**Issue**: "Address already in use"

**Solution**:

1. Change port in `.env`: `PORT=8001`
2. Or kill process using port 8000: `lsof -ti:8000 | xargs kill`

## 🐳 Docker Commands

### Using deploy.sh (Recommended)

```bash
# Deploy
./deploy.sh deploy

# View logs
./deploy.sh logs

# Restart
./deploy.sh restart

# Stop
./deploy.sh stop

# Clean up
./deploy.sh clean
```

### Using docker-compose

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

### Manual Docker Commands

```bash
# Build
docker build -t fast-embedding:latest --target production .

# Run
docker run -d --name fast-embedding -p 8000:8000 fast-embedding:latest

# Logs
docker logs -f fast-embedding

# Stop
docker stop fast-embedding
```

## 📚 Next Steps

1. **Read the full README**: [README.md](README.md)
2. **Production deployment**: [PRODUCTION.md](PRODUCTION.md)
3. **Run tests**: `pytest test_api.py -v`
4. **Configure for production**: Edit `.env` with your settings

## 💡 Pro Tips

1. **Always use batch endpoint** for multiple texts (much faster!)
2. **Monitor metrics** to understand usage patterns
3. **Pre-warm models** by calling `/embed` on startup
4. **Adjust thread pool** based on CPU cores for best performance
5. **Enable rate limiting** in production to prevent abuse

## 🆘 Getting Help

- Check logs: Look at console output for detailed error messages
- Test endpoints: Use `example_client.py` to verify functionality
- Health check: `curl http://localhost:8000/health`
- Metrics: `curl http://localhost:8000/metrics`

## 📝 Quick Reference

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `POST /embed` | Single embedding | `{"model_name": "...", "text": "..."}` |
| `POST /embed/batch` | Batch embeddings | `{"model_name": "...", "texts": [...]}` |
| `GET /health` | Health check | - |
| `GET /models` | List models | - |
| `GET /models/{name}` | Model info | - |
| `GET /metrics` | API metrics | - |

---

Happy embedding! 🚀
