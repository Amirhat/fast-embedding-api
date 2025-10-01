# Performance Benchmarks

Complete benchmark results for Fast Embedding API running on Docker.

## 🎯 Executive Summary

| Metric | Result | Status |
|--------|--------|--------|
| **Single Embedding** | 12.62ms avg | ✅ <15ms |
| **Batch (10 texts)** | 4.16ms per text | ✅ <5ms |
| **Sequential Throughput** | 79.3 req/s | ✅ >50 req/s |
| **Concurrent Throughput** | 140.2 req/s | ✅ >100 req/s |
| **K6 Load Test Throughput** | 95.1 req/s | ✅ >80 req/s |
| **Cache Speedup** | 3.2x faster | ✅ >2x |
| **Batch Speedup** | 3.0x faster | ✅ >2.5x |
| **Error Rate** | 0.00% | ✅ <1% |
| **P95 Response Time** | 90.79ms | ✅ <100ms |
| **P99 Response Time** | N/A | - |

---

## 📊 Python Benchmark Results

### Test Environment

- **Date**: 2025-10-01 13:56:26
- **API**: http://localhost:8000 (Docker)
- **Model**: BAAI/bge-small-en-v1.5
- **Text Length**: 100 characters (default)

### 1️⃣ Single Embedding Performance

Sequential requests with single text embedding.

```text
Requests:      100
Average:       12.62ms
Median:        10.83ms
Min:           8.63ms
Max:           28.71ms
P95:           20.85ms
P99:           28.71ms
Throughput:    79.3 req/s
```

**Key Insights:**

- Consistent sub-15ms latency for typical text
- Low variance (median close to average)
- Excellent for real-time applications

### 2️⃣ Batch Embedding Performance

Batch processing with 10 texts per request.

```text
Requests:      50 batches
Batch Size:    10 texts
Average:       41.57ms per batch
Per Text:      4.16ms per text
Median:        38.46ms
Min:           33.68ms
Max:           54.62ms
P95:           54.12ms
Throughput:    240.6 embeddings/s
```

**Speedup vs Single:** 🚀 **3.0x faster per text**

**Key Insights:**

- Dramatic efficiency gains with batching
- Ideal for bulk processing scenarios
- Minimal overhead per additional text in batch

### 3️⃣ Concurrent Requests

100 concurrent requests with 10 concurrent workers.

```text
Total Requests:  100
Concurrency:     10
Total Time:      713ms
Avg Latency:     68.51ms
Median:          69.38ms
Min:             22.15ms
Max:             125.97ms
P95:             92.50ms
Throughput:      140.2 req/s
```

**Key Insights:**

- Handles concurrent load efficiently
- 77% higher throughput vs sequential
- Graceful scaling under concurrent load

### 4️⃣ Text Size Impact

Performance across different text lengths.

| Text Length (chars) | Avg Time (ms) | Median (ms) | Overhead |
|---------------------|---------------|-------------|----------|
| 50                  | 8.61          | 8.20        | baseline |
| 100                 | 12.12         | 11.24       | 1.4x     |
| 500                 | 23.96         | 21.86       | 2.8x     |
| 1000                | 41.96         | 37.75       | 4.9x     |
| 2000                | 88.40         | 89.22       | 10.3x    |
| 4000                | 112.46        | 110.00      | 13.1x    |

**Key Insights:**

- Near-linear scaling with text length
- Minimal overhead for short texts (<500 chars)
- Optimized for typical use cases

### 5️⃣ Cache Performance

Model caching effectiveness.

```text
Cold Cache (first load):  26.72ms
Warm Cache (subsequent):   8.23ms
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Speedup: 3.2x faster! 🔥
```

**Key Insights:**

- Models stay in memory after first use
- Significant performance boost after warm-up
- TTL-based offloading (1 hour default)

---

## ⚡ K6 Load Test Results

### Test Configuration

- **Duration**: 3.5 minutes
- **Stages**
  - Ramp 0→10 users (30s)
  - Hold 10 users (1m)
  - Ramp 10→20 users (30s)
  - Hold 20 users (1m)
  - Ramp 20→0 users (30s)
- **Request Mix**: 70% single, 30% batch (3-7 texts)

### Overall Metrics

```text
Total Requests:        19,988
Test Duration:         210s
Throughput:            95.1 req/s
Total Data Received:   364 MB
Total Data Sent:       6.4 MB
Success Rate:          100% ✓
Error Rate:            0.00% ✓
```

### Response Times

```text
Min:           5.14ms
Average:       33.62ms
Median:        24.34ms
P90:           74.73ms
P95:           90.79ms ✓ (threshold: <500ms)
Max:           242.07ms
```

### Request Type Breakdown

#### Single Embedding Requests (70%)

```text
Average Duration:  25.53ms
Min:               5.14ms
Median:            16.99ms
Max:               208.54ms
P90:               58.71ms
P95:               70.74ms
```

#### Batch Embedding Requests (30%)

```text
Average Duration:  52.01ms
Min:               9.03ms
Median:            43.59ms
Max:               242.08ms
P90:               97.60ms
P95:               111.31ms
```

### Thresholds

| Threshold | Target | Actual | Status |
|-----------|--------|--------|--------|
| P95 Response Time | <500ms | 90.79ms | ✅ Pass |
| Error Rate | <10% | 0.00% | ✅ Pass |
| Failed Requests | <1% | 0.00% | ✅ Pass |

### Virtual Users Progression

```text
Stage 1 (0-30s):    0→10 users   |  1,285 requests
Stage 2 (30-90s):   10 users     |  5,048 requests
Stage 3 (90-120s):  10→20 users  |  2,048 requests
Stage 4 (120-180s): 20 users     |  10,467 requests
Stage 5 (180-210s): 20→0 users   |  1,140 requests
```

---

## 🔬 Analysis

### Strengths

1. **✅ Excellent Latency**: Sub-15ms for typical requests
2. **✅ High Throughput**: 95+ req/s sustained under load
3. **✅ Perfect Reliability**: 0% error rate across 20K+ requests
4. **✅ Efficient Batching**: 3x speedup for batch operations
5. **✅ Smart Caching**: 3.2x faster after model warm-up
6. **✅ Concurrent Handling**: 140 req/s with 10 concurrent workers

### Optimizations Opportunities

1. **Text Length**: Performance degrades for very long texts (>2000 chars)
   - *Recommendation*: Consider text chunking for large documents
2. **Cold Start**: Initial request ~3x slower
   - *Mitigation*: Model pre-warming on startup (already implemented)
3. **Batch Size**: Fixed batch size of 10 in benchmarks
   - *Recommendation*: Test optimal batch sizes 5-32 for your workload

### Performance by Use Case

| Use Case | Recommended Approach | Expected Performance |
|----------|---------------------|---------------------|
| **Real-time Search** | Single requests | ~13ms avg |
| **Bulk Processing** | Batch requests (10+) | ~4ms per text |
| **API Gateway** | Concurrent requests | 140+ req/s |
| **Background Jobs** | Large batches (20-32) | 250+ embeddings/s |

---

## 🚀 Running Benchmarks

### Python Benchmark Suite

```bash
# Start API with Docker
docker-compose up -d

# Run benchmarks
python3 benchmarks/benchmark.py

# Results saved to: benchmarks/benchmark_results.json
```

### K6 Load Testing

```bash
# Install K6 (if not already installed)
# macOS: brew install k6
# Linux: sudo apt-get install k6

# Run load test
k6 run benchmarks/k6-load-test.js

# Custom test duration
k6 run --vus 20 --duration 60s benchmarks/k6-load-test.js

# Results saved to: benchmarks/k6-results.json
```

---

## 📈 Historical Trends

### Version Comparison

| Version | Single (ms) | Batch (ms/text) | Throughput (req/s) | Notes |
|---------|-------------|-----------------|-------------------|-------|
| v1.0.0  | 12.62       | 4.16            | 95.1              | Docker deployment |
| -       | -           | -               | -                 | Baseline |

*Benchmarks will be updated with each major release.*

---

## 🎯 Performance Goals

### Current Status

- ✅ **Latency Goal**: <15ms average (12.62ms achieved)
- ✅ **Throughput Goal**: >80 req/s (95.1 achieved)
- ✅ **Reliability Goal**: >99.9% uptime (100% achieved)
- ✅ **Concurrency Goal**: Handle 20+ concurrent users (passed)

### Future Targets (v2.0)

- 🎯 Target: <10ms average for single embeddings
- 🎯 Target: 150+ req/s sustained throughput
- 🎯 Target: Support 50+ concurrent users
- 🎯 Target: <5s cold start time

---

## 💡 Benchmark Methodology

### Test Setup

1. API running in Docker container (production configuration)
2. Tests run from host machine (simulating external client)
3. No artificial delays or throttling
4. Rate limiting disabled for accurate measurement
5. Models pre-loaded to avoid cold start bias

### Metrics Definitions

- **Latency**: Time from request sent to response received
- **Throughput**: Successful requests per second
- **P95/P99**: 95th/99th percentile response times
- **Error Rate**: Failed requests / total requests

### Reproducibility

All benchmarks are reproducible using the scripts in `benchmarks/`:

- Python script for detailed metrics
- K6 script for load testing
- Same model (`BAAI/bge-small-en-v1.5`) used consistently

---

## 📞 Feedback

Have different performance results? Found optimization opportunities?

- 🐛 [Report an Issue](https://github.com/Amirhat/fast-embedding-api/issues)
- 💬 [Start a Discussion](https://github.com/Amirhat/fast-embedding-api/discussions)
- 🔧 [Submit a PR](https://github.com/Amirhat/fast-embedding-api/pulls)
