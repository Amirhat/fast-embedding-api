"""Shared pytest fixtures for all tests."""

import pytest
import asyncio
import sys
import os
from typing import AsyncGenerator
from litestar import Litestar
from litestar.testing import AsyncTestClient

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model_manager import ModelCache
from src.config import Settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Create test settings with smaller limits."""
    return Settings(
        required_models=["BAAI/bge-small-en-v1.5"],
        allowed_models=None,
        model_cache_ttl=10,
        max_cached_models=2,
        cleanup_interval=5,
        thread_pool_workers=2,
        max_text_length=1000,
        max_batch_size=10,
        request_timeout=30,
        enable_metrics=True,
        enable_cors=True,
        enable_rate_limit=False,
        debug=True,
        log_level="INFO",
    )


@pytest.fixture
async def model_cache() -> AsyncGenerator[ModelCache, None]:
    """Create a model cache instance for testing."""
    cache = ModelCache(cache_ttl=10, max_cached=2, thread_pool_workers=2)
    await cache.start()
    yield cache
    await cache.stop()


@pytest.fixture
async def app(test_settings, monkeypatch) -> Litestar:
    """Create a Litestar app instance for testing."""
    # Patch settings
    monkeypatch.setattr("src.config.settings", test_settings)

    # Import app after patching settings
    from src.main import app

    return app


@pytest.fixture
async def test_client(app: Litestar) -> AsyncGenerator[AsyncTestClient, None]:
    """Create an async test client."""
    async with AsyncTestClient(app=app) as client:
        yield client


@pytest.fixture
def sample_texts():
    """Sample texts for testing."""
    return [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is transforming artificial intelligence",
        "Python is a versatile programming language",
        "Embeddings capture semantic meaning of text",
        "Natural language processing enables human-computer interaction",
    ]


@pytest.fixture
def sample_model_name():
    """Default model name for testing."""
    return "BAAI/bge-small-en-v1.5"
