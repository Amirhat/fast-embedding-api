"""Test suite for the Fast Embedding API."""

import pytest
import asyncio
from typing import List
from model_manager import ModelCache


class TestModelCache:
    """Test cases for ModelCache."""

    @pytest.fixture
    async def cache(self):
        """Create a model cache instance for testing."""
        cache = ModelCache(cache_ttl=10, max_cached=2, thread_pool_workers=2)
        await cache.start()
        yield cache
        await cache.stop()

    @pytest.mark.asyncio
    async def test_model_loading(self, cache):
        """Test that models can be loaded."""
        model_name = "BAAI/bge-small-en-v1.5"
        model = await cache.get_model(model_name)
        assert model is not None
        assert model_name in cache._models

    @pytest.mark.asyncio
    async def test_model_caching(self, cache):
        """Test that models are cached after first load."""
        model_name = "BAAI/bge-small-en-v1.5"

        # First load
        model1 = await cache.get_model(model_name)

        # Second load (should use cache)
        model2 = await cache.get_model(model_name)

        assert model1 is model2  # Same instance

    @pytest.mark.asyncio
    async def test_lru_eviction(self, cache):
        """Test that LRU eviction works when cache is full."""
        models = [
            "BAAI/bge-small-en-v1.5",
            "BAAI/bge-base-en-v1.5",
            "sentence-transformers/all-MiniLM-L6-v2",
        ]

        # Load first model
        await cache.get_model(models[0])
        assert models[0] in cache._models

        # Load second model
        await cache.get_model(models[1])
        assert models[1] in cache._models

        # Load third model (should evict first)
        await cache.get_model(models[2])
        assert models[2] in cache._models
        assert models[0] not in cache._models  # Evicted

    @pytest.mark.asyncio
    async def test_embedding_generation(self, cache):
        """Test that embeddings can be generated."""
        model_name = "BAAI/bge-small-en-v1.5"
        text = "This is a test"

        embedding = await cache.embed(model_name, text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.asyncio
    async def test_batch_embedding(self, cache):
        """Test batch embedding generation."""
        model_name = "BAAI/bge-small-en-v1.5"
        texts = ["Test 1", "Test 2", "Test 3"]

        embeddings = await cache.embed_batch(model_name, texts)

        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)
        assert all(isinstance(emb, list) for emb in embeddings)

    @pytest.mark.asyncio
    async def test_timeout(self, cache):
        """Test that timeout works for embeddings."""
        model_name = "BAAI/bge-small-en-v1.5"
        text = "Test"

        # This should work
        embedding = await cache.embed(model_name, text, timeout=30)
        assert embedding is not None

        # Very short timeout should fail
        with pytest.raises(TimeoutError):
            await cache.embed(model_name, text, timeout=0.001)

    @pytest.mark.asyncio
    async def test_model_validation(self, cache):
        """Test model validation."""
        # Valid model
        is_valid = await cache.validate_model("BAAI/bge-small-en-v1.5")
        assert is_valid is True

        # Invalid model
        is_valid = await cache.validate_model("invalid/model-name-xyz")
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_warm_up_models(self, cache):
        """Test warming up multiple models."""
        models = ["BAAI/bge-small-en-v1.5", "BAAI/bge-base-en-v1.5"]

        results = await cache.warm_up_models(models)

        assert len(results) == len(models)
        for model in models:
            assert model in cache._models  # Should be cached

    @pytest.mark.asyncio
    async def test_cache_info(self, cache):
        """Test cache info retrieval."""
        model_name = "BAAI/bge-small-en-v1.5"
        await cache.get_model(model_name)

        info = cache.get_cache_info()

        assert "cached_models" in info
        assert model_name in info["cached_models"]
        assert info["num_cached"] == 1

    @pytest.mark.asyncio
    async def test_model_info(self, cache):
        """Test model info retrieval."""
        model_name = "BAAI/bge-small-en-v1.5"
        await cache.get_model(model_name)

        info = cache.get_model_info(model_name)

        assert info is not None
        assert info["is_cached"] is True
        assert "load_time" in info
        assert "last_used" in info

    @pytest.mark.asyncio
    async def test_ttl_cleanup(self, cache):
        """Test that TTL cleanup removes old models."""
        model_name = "BAAI/bge-small-en-v1.5"

        # Load model
        await cache.get_model(model_name)
        assert model_name in cache._models

        # Manually set last_used to past (simulate old model)
        cache._last_used[model_name] = 0

        # Trigger cleanup
        await cache._cleanup_old_models()

        # Model should be removed
        assert model_name not in cache._models


class TestAPIEndpoints:
    """Test cases for API endpoints (requires running server)."""

    @pytest.fixture
    def base_url(self):
        """Base URL for the API."""
        return "http://localhost:8000"

    def test_health_endpoint(self, base_url):
        """Test health check endpoint."""
        import requests

        response = requests.get(f"{base_url}/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "cache_info" in data

    def test_models_endpoint(self, base_url):
        """Test models list endpoint."""
        import requests

        response = requests.get(f"{base_url}/models")

        assert response.status_code == 200
        data = response.json()
        assert "required_models" in data
        assert "cached_models" in data

    def test_embed_endpoint(self, base_url):
        """Test single embedding endpoint."""
        import requests

        payload = {"model_name": "BAAI/bge-small-en-v1.5", "text": "This is a test"}

        response = requests.post(f"{base_url}/embed", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "embedding" in data
        assert "dimension" in data
        assert "processing_time_ms" in data

    def test_batch_embed_endpoint(self, base_url):
        """Test batch embedding endpoint."""
        import requests

        payload = {
            "model_name": "BAAI/bge-small-en-v1.5",
            "texts": ["Test 1", "Test 2", "Test 3"],
        }

        response = requests.post(f"{base_url}/embed/batch", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "embeddings" in data
        assert len(data["embeddings"]) == 3
        assert data["count"] == 3

    def test_model_info_endpoint(self, base_url):
        """Test model info endpoint."""
        import requests

        model_name = "BAAI/bge-small-en-v1.5"
        response = requests.get(f"{base_url}/models/{model_name}")

        assert response.status_code == 200
        data = response.json()
        assert data["model_name"] == model_name
        assert "is_cached" in data

    def test_metrics_endpoint(self, base_url):
        """Test metrics endpoint."""
        import requests

        response = requests.get(f"{base_url}/metrics")

        # Will work if metrics are enabled
        if response.status_code == 200:
            data = response.json()
            assert "total_requests" in data
            assert "total_embeddings" in data

    def test_input_validation(self, base_url):
        """Test that input validation works."""
        import requests

        # Text too long (if max_text_length is set)
        payload = {
            "model_name": "BAAI/bge-small-en-v1.5",
            "text": "x" * 100000,  # Very long text
        }

        response = requests.post(f"{base_url}/embed", json=payload)
        # Should fail with validation error
        assert response.status_code in [400, 422]

    def test_batch_size_validation(self, base_url):
        """Test batch size validation."""
        import requests

        # Batch too large
        payload = {
            "model_name": "BAAI/bge-small-en-v1.5",
            "texts": ["test"] * 1000,  # Very large batch
        }

        response = requests.post(f"{base_url}/embed/batch", json=payload)
        # Should fail with validation error
        assert response.status_code in [400, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
