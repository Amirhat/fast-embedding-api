"""Tests for configuration module."""

import pytest
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Settings, CommaSeparatedList


class TestCommaSeparatedList:
    """Test cases for CommaSeparatedList custom type."""

    def test_string_parsing(self):
        """Test parsing comma-separated string."""
        result = CommaSeparatedList._validate("a,b,c")
        assert result == ["a", "b", "c"]

    def test_string_with_spaces(self):
        """Test parsing with extra spaces."""
        result = CommaSeparatedList._validate("a , b , c ")
        assert result == ["a", "b", "c"]

    def test_empty_string(self):
        """Test parsing empty string."""
        result = CommaSeparatedList._validate("")
        assert result == []

    def test_list_input(self):
        """Test that list input is preserved."""
        result = CommaSeparatedList._validate(["a", "b", "c"])
        assert result == ["a", "b", "c"]

    def test_single_item(self):
        """Test single item."""
        result = CommaSeparatedList._validate("single")
        assert result == ["single"]


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        assert isinstance(settings.required_models, list)
        assert len(settings.required_models) > 0
        assert settings.model_cache_ttl == 3600
        assert settings.max_cached_models == 5
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000

    def test_custom_settings(self):
        """Test creating settings with custom values."""
        settings = Settings(
            model_cache_ttl=1800,
            max_cached_models=3,
            port=9000,
            debug=True,
        )
        assert settings.model_cache_ttl == 1800
        assert settings.max_cached_models == 3
        assert settings.port == 9000
        assert settings.debug is True

    def test_required_models_parsing(self):
        """Test required_models parsing from string."""
        settings = Settings(required_models="model1,model2,model3")
        assert settings.required_models == ["model1", "model2", "model3"]

    def test_cors_origins_parsing(self):
        """Test CORS origins parsing."""
        settings = Settings(cors_origins="http://localhost:3000,http://example.com")
        assert "http://localhost:3000" in settings.cors_origins
        assert "http://example.com" in settings.cors_origins

    def test_allowed_models_none(self):
        """Test that allowed_models can be None."""
        settings = Settings(allowed_models=None)
        assert settings.allowed_models is None

    def test_allowed_models_list(self):
        """Test setting allowed_models as list."""
        allowed = ["model1", "model2"]
        settings = Settings(allowed_models=allowed)
        assert settings.allowed_models == allowed

    def test_performance_settings(self):
        """Test performance-related settings."""
        settings = Settings(
            thread_pool_workers=8,
            max_text_length=16384,
            max_batch_size=64,
            request_timeout=600,
        )
        assert settings.thread_pool_workers == 8
        assert settings.max_text_length == 16384
        assert settings.max_batch_size == 64
        assert settings.request_timeout == 600

    def test_security_settings(self):
        """Test security-related settings."""
        settings = Settings(
            enable_cors=False,
            enable_rate_limit=True,
            rate_limit_requests=100,
        )
        assert settings.enable_cors is False
        assert settings.enable_rate_limit is True
        assert settings.rate_limit_requests == 100

    def test_monitoring_settings(self):
        """Test monitoring settings."""
        settings = Settings(
            enable_metrics=False,
            log_level="DEBUG",
        )
        assert settings.enable_metrics is False
        assert settings.log_level == "DEBUG"

    def test_cleanup_interval(self):
        """Test cleanup interval setting."""
        settings = Settings(cleanup_interval=30)
        assert settings.cleanup_interval == 30

    def test_max_request_size(self):
        """Test max request size setting."""
        settings = Settings(max_request_size=5 * 1024 * 1024)  # 5MB
        assert settings.max_request_size == 5 * 1024 * 1024
