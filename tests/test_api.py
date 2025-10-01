"""
Legacy API endpoint tests using requests library.

Note: These tests require a running server. For better integration tests
that don't require a running server, see test_integration.py which uses
Litestar's test client.

To run these tests:
1. Start the server: python -m src.main
2. Run: pytest tests/test_api.py
"""

import pytest


class TestAPIEndpointsWithRunningServer:
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
