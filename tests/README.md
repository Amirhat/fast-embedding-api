# Test Suite Documentation

This directory contains comprehensive tests for the Fast Embedding API.

## Test Structure

```tree
tests/
├── conftest.py              # Shared pytest fixtures
├── test_config.py           # Unit tests for configuration
├── test_model_manager.py    # Unit tests for ModelCache
├── test_integration.py      # Integration tests for API endpoints
├── test_api.py             # Legacy endpoint tests (kept for compatibility)
└── example_client.py        # Example client demonstrating API usage
```

## Test Categories

### 1. Unit Tests

#### `test_config.py`

Tests for the configuration module:

- CommaSeparatedList custom type parsing
- Settings validation and defaults
- Environment variable handling
- Configuration edge cases

#### `test_model_manager.py`

Tests for the ModelCache class:

- Model loading and caching
- LRU eviction policy
- Embedding generation (single and batch)
- Timeout handling
- Model validation
- TTL cleanup
- Concurrent access
- Cache information retrieval

### 2. Integration Tests

#### `test_integration.py`

End-to-end API tests using Litestar's test client:

- Health check endpoint
- Models listing endpoint
- Model info endpoint
- Single embedding endpoint
- Batch embedding endpoint
- Metrics endpoint
- Error handling
- Input validation
- CORS functionality
- Performance characteristics

## Running Tests

### Run All Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term
```

### Run Specific Test Categories

```bash
# Run only unit tests
pytest tests/test_config.py tests/test_model_manager.py

# Run only integration tests
pytest tests/test_integration.py

# Run specific test class
pytest tests/test_integration.py::TestEmbedEndpoint

# Run specific test
pytest tests/test_integration.py::TestEmbedEndpoint::test_embed_text_success
```

### Run with Different Output Formats

```bash
# Show test progress with markers
pytest -v --tb=short

# Run with minimal output
pytest -q

# Show local variables in tracebacks
pytest -l

# Stop at first failure
pytest -x

# Run last failed tests only
pytest --lf
```

## Test Fixtures

The `conftest.py` file provides shared fixtures:

- `event_loop`: Session-scoped event loop for async tests
- `test_settings`: Test configuration with smaller limits
- `model_cache`: Fresh ModelCache instance for each test
- `app`: Litestar application with test settings
- `test_client`: Async test client for API testing
- `sample_texts`: Pre-defined sample texts
- `sample_model_name`: Default model name for testing

## Writing New Tests

### Example: Adding a Unit Test

```python
# tests/test_model_manager.py
@pytest.mark.asyncio
async def test_new_feature(model_cache, sample_model_name):
    """Test description."""
    # Your test code here
    result = await model_cache.some_method(sample_model_name)
    assert result is not None
```

### Example: Adding an Integration Test

```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_new_endpoint(test_client):
    """Test description."""
    response = await test_client.get("/new-endpoint")
    assert response.status_code == 200
```

## Test Coverage

To generate a detailed coverage report:

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

Target coverage: **> 90%**

Current coverage areas:

- ✅ Configuration module
- ✅ Model manager
- ✅ API endpoints
- ✅ Request validation
- ✅ Error handling
- ✅ Cache management

## Continuous Integration

Tests run automatically on:

- Pull requests
- Commits to main branch
- Scheduled daily runs

See `.github/workflows/ci.yml` for CI configuration.

## Performance Testing

For load testing, see:

- `benchmarks/benchmark.py` - Python-based benchmarks
- `benchmarks/k6-load-test.js` - K6 load testing script

## Test Data

Tests use the following models:

- `BAAI/bge-small-en-v1.5` (primary test model - small and fast)
- `sentence-transformers/all-MiniLM-L6-v2` (secondary test model)

These models are chosen for:

- Small size (fast downloads)
- Good performance
- Wide compatibility
- Fast inference

## Troubleshooting

### Tests Fail with "Model not found"

Ensure the test model is accessible:

```bash
python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5')"
```

### Tests Timeout

Increase timeout values in `pytest.ini`:

```ini
[pytest]
timeout = 300
```

Or skip slow tests:

```bash
pytest -m "not slow"
```

### Memory Issues

Run tests with smaller batch sizes:

```bash
pytest --maxfail=1  # Stop after first failure
```

## Best Practices

1. **Use fixtures**: Leverage shared fixtures from `conftest.py`
2. **Async tests**: Mark async tests with `@pytest.mark.asyncio`
3. **Descriptive names**: Use clear, descriptive test names
4. **Test independence**: Each test should be independent
5. **Clean up**: Fixtures handle cleanup automatically
6. **Documentation**: Add docstrings to test functions
7. **Edge cases**: Test both happy path and error cases
8. **Assertions**: Use specific assertions with clear messages

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain > 90% coverage
4. Update this README if needed
5. Run linters: `ruff check .` and `black .`

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Litestar Testing Guide](https://docs.litestar.dev/latest/usage/testing.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
