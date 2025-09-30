"""Configuration for the embedding API."""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings."""

    # List of models that must be pre-installed and validated
    required_models: List[str] = [
        "BAAI/bge-small-en-v1.5",
        "BAAI/bge-base-en-v1.5",
        "sentence-transformers/all-MiniLM-L6-v2",
    ]

    # Allowed models (if set, only these models can be used)
    # If empty, any model can be requested (security risk in production)
    allowed_models: Optional[List[str]] = None

    # Model cache settings
    model_cache_ttl: int = (
        3600  # Time in seconds before unused models are offloaded (1 hour)
    )
    max_cached_models: int = 5  # Maximum number of models to keep in memory
    cleanup_interval: int = 60  # Cleanup check interval in seconds

    # Performance settings
    thread_pool_workers: int = 4  # Number of workers for CPU-intensive tasks
    max_text_length: int = 8192  # Maximum text length in characters
    max_batch_size: int = 32  # Maximum number of texts in a batch request
    request_timeout: int = 300  # Request timeout in seconds

    # API settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Security settings
    enable_cors: bool = True
    cors_origins: List[str] = ["*"]  # Configure properly in production
    max_request_size: int = 10 * 1024 * 1024  # 10MB

    # Rate limiting (requests per minute per IP)
    enable_rate_limit: bool = False
    rate_limit_requests: int = 60
    rate_limit_window: int = 60

    # Monitoring
    enable_metrics: bool = True
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
