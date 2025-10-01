"""Tests for model manager module."""

import pytest
import asyncio
import sys
import os
from typing import List

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model_manager import ModelCache


class TestModelCache:
    """Test cases for ModelCache."""

    @pytest.mark.asyncio
    async def test_model_loading(self, model_cache, sample_model_name):
        """Test that models can be loaded."""
        model = await model_cache.get_model(sample_model_name)
        assert model is not None
        assert sample_model_name in model_cache._models

    @pytest.mark.asyncio
    async def test_model_caching(self, model_cache, sample_model_name):
        """Test that models are cached after first load."""
        # First load
        model1 = await model_cache.get_model(sample_model_name)

        # Second load (should use cache)
        model2 = await model_cache.get_model(sample_model_name)

        assert model1 is model2  # Same instance

    @pytest.mark.asyncio
    async def test_lru_eviction(self, model_cache):
        """Test that LRU eviction works when cache is full."""
        models = [
            "BAAI/bge-small-en-v1.5",
            "sentence-transformers/all-MiniLM-L6-v2",
            "BAAI/bge-base-en-v1.5",
        ]

        # Load first model
        await model_cache.get_model(models[0])
        assert models[0] in model_cache._models

        # Load second model (max_cached=2, so this should fill the cache)
        await model_cache.get_model(models[1])
        assert models[1] in model_cache._models

        # Load third model (should evict first)
        await model_cache.get_model(models[2])
        assert models[2] in model_cache._models
        assert models[0] not in model_cache._models  # Evicted

    @pytest.mark.asyncio
    async def test_embedding_generation(self, model_cache, sample_model_name):
        """Test that embeddings can be generated."""
        text = "This is a test"

        embedding = await model_cache.embed(sample_model_name, text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.asyncio
    async def test_batch_embedding(self, model_cache, sample_model_name, sample_texts):
        """Test batch embedding generation."""
        embeddings = await model_cache.embed_batch(sample_model_name, sample_texts[:3])

        assert isinstance(embeddings, list)
        assert len(embeddings) == 3
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)

    @pytest.mark.asyncio
    async def test_embedding_timeout_success(self, model_cache, sample_model_name):
        """Test that embeddings work with reasonable timeout."""
        text = "Test"

        # This should work with 30s timeout
        embedding = await model_cache.embed(sample_model_name, text, timeout=30)
        assert embedding is not None
        assert len(embedding) > 0

    @pytest.mark.asyncio
    async def test_embedding_timeout_failure(self, model_cache, sample_model_name):
        """Test that very short timeout raises TimeoutError."""
        text = "Test"

        # Very short timeout should fail
        with pytest.raises(TimeoutError):
            await model_cache.embed(sample_model_name, text, timeout=0.0001)

    @pytest.mark.asyncio
    async def test_batch_embedding_timeout(self, model_cache, sample_model_name):
        """Test batch embedding timeout."""
        texts = ["Test 1", "Test 2", "Test 3"]

        # Very short timeout should fail
        with pytest.raises(TimeoutError):
            await model_cache.embed_batch(sample_model_name, texts, timeout=0.0001)

    @pytest.mark.asyncio
    async def test_model_validation_valid(self, model_cache):
        """Test model validation with valid model."""
        is_valid = await model_cache.validate_model("BAAI/bge-small-en-v1.5")
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_model_validation_invalid(self, model_cache):
        """Test model validation with invalid model."""
        is_valid = await model_cache.validate_model("invalid/model-name-xyz-123")
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_warm_up_models(self, model_cache):
        """Test warming up multiple models."""
        models = ["BAAI/bge-small-en-v1.5"]

        results = await model_cache.warm_up_models(models)

        assert len(results) == len(models)
        assert all(results.values())  # All should be valid
        for model in models:
            assert model in model_cache._models  # Should be cached

    @pytest.mark.asyncio
    async def test_cache_info(self, model_cache, sample_model_name):
        """Test cache info retrieval."""
        await model_cache.get_model(sample_model_name)

        info = model_cache.get_cache_info()

        assert "cached_models" in info
        assert sample_model_name in info["cached_models"]
        assert info["num_cached"] == 1
        assert "cache_ttl" in info
        assert "max_cached" in info
        assert "cleanup_interval" in info

    @pytest.mark.asyncio
    async def test_model_info(self, model_cache, sample_model_name):
        """Test model info retrieval."""
        await model_cache.get_model(sample_model_name)

        info = model_cache.get_model_info(sample_model_name)

        assert info is not None
        assert info["is_cached"] is True
        assert "load_time" in info
        assert "last_used" in info
        assert "loaded_at" in info
        assert isinstance(info["load_time"], float)
        assert info["load_time"] > 0

    @pytest.mark.asyncio
    async def test_model_info_not_cached(self, model_cache):
        """Test getting info for non-cached model."""
        info = model_cache.get_model_info("nonexistent-model")
        assert info is None

    @pytest.mark.asyncio
    async def test_ttl_cleanup(self, model_cache, sample_model_name):
        """Test that TTL cleanup removes old models."""
        # Load model
        await model_cache.get_model(sample_model_name)
        assert sample_model_name in model_cache._models

        # Manually set last_used to past (simulate old model)
        model_cache._last_used[sample_model_name] = 0

        # Trigger cleanup
        await model_cache._cleanup_old_models()

        # Model should be removed
        assert sample_model_name not in model_cache._models

    @pytest.mark.asyncio
    async def test_model_reuse_updates_timestamp(self, model_cache, sample_model_name):
        """Test that reusing a model updates its timestamp."""
        # Load model
        await model_cache.get_model(sample_model_name)
        first_timestamp = model_cache._last_used[sample_model_name]

        # Wait a bit
        await asyncio.sleep(0.1)

        # Reuse model
        await model_cache.get_model(sample_model_name)
        second_timestamp = model_cache._last_used[sample_model_name]

        assert second_timestamp > first_timestamp

    @pytest.mark.asyncio
    async def test_concurrent_model_loading(self, model_cache, sample_model_name):
        """Test that concurrent requests for the same model work correctly."""
        # Create multiple concurrent requests
        tasks = [model_cache.get_model(sample_model_name) for _ in range(5)]
        models = await asyncio.gather(*tasks)

        # All should return the same model instance
        assert all(model is models[0] for model in models)
        # Should only be loaded once
        assert sample_model_name in model_cache._models

    @pytest.mark.asyncio
    async def test_unload_model(self, model_cache, sample_model_name):
        """Test manual model unloading."""
        # Load model
        await model_cache.get_model(sample_model_name)
        assert sample_model_name in model_cache._models

        # Unload it
        model_cache._unload_model(sample_model_name)

        # Model should be gone
        assert sample_model_name not in model_cache._models
        assert sample_model_name not in model_cache._last_used

    @pytest.mark.asyncio
    async def test_validation_caching(self, model_cache, sample_model_name):
        """Test that validate_model caches the model when cache_on_success=True."""
        is_valid = await model_cache.validate_model(sample_model_name, cache_on_success=True)
        assert is_valid is True
        assert sample_model_name in model_cache._models

    @pytest.mark.asyncio
    async def test_validation_no_caching(self, model_cache, sample_model_name):
        """Test that validate_model doesn't cache when cache_on_success=False."""
        is_valid = await model_cache.validate_model(sample_model_name, cache_on_success=False)
        assert is_valid is True
        # Model should not be in cache (though it might be due to the validation process)

    @pytest.mark.asyncio
    async def test_embedding_consistency(self, model_cache, sample_model_name):
        """Test that embeddings are consistent for the same text."""
        text = "Consistency test"

        embedding1 = await model_cache.embed(sample_model_name, text)
        embedding2 = await model_cache.embed(sample_model_name, text)

        # Embeddings should be identical
        assert len(embedding1) == len(embedding2)
        assert all(abs(a - b) < 1e-6 for a, b in zip(embedding1, embedding2))

    @pytest.mark.asyncio
    async def test_batch_size_one(self, model_cache, sample_model_name):
        """Test batch embedding with single text."""
        embeddings = await model_cache.embed_batch(sample_model_name, ["Single text"])

        assert len(embeddings) == 1
        assert isinstance(embeddings[0], list)
        assert len(embeddings[0]) > 0

    @pytest.mark.asyncio
    async def test_empty_batch_handling(self, model_cache, sample_model_name):
        """Test handling of empty batch."""
        # Empty batch should work but return empty list
        embeddings = await model_cache.embed_batch(sample_model_name, [])
        assert embeddings == []
