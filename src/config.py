"""Configuration for the embedding API."""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ConfigDict, GetCoreSchemaHandler
from pydantic_core import core_schema
from typing import List, Optional, Union, Any
import json


class CommaSeparatedList:
    """Custom type for comma-separated lists."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.union_schema(
                [core_schema.str_schema(), core_schema.list_schema(core_schema.str_schema())]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: ",".join(x) if isinstance(x, list) else str(x),
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def _validate(cls, value: Any) -> List[str]:
        """Validate and convert comma-separated string to list."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        elif isinstance(value, list):
            return value
        else:
            return []


class Settings(BaseSettings):
    """Application settings."""

    # List of models that must be pre-installed and validated
    required_models: CommaSeparatedList = Field(
        default=[
            "BAAI/bge-small-en-v1.5",
            "BAAI/bge-base-en-v1.5",
            "sentence-transformers/all-MiniLM-L6-v2",
        ],
        description="Comma-separated list of required models",
    )

    # Allowed models (if set, only these models can be used)
    # If empty, any model can be requested (security risk in production)
    allowed_models: Optional[List[str]] = None

    # Model cache settings
    model_cache_ttl: int = 3600  # Time in seconds before unused models are offloaded (1 hour)
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
    cors_origins: CommaSeparatedList = Field(
        default=["*"], description="Comma-separated list of CORS origins"
    )
    max_request_size: int = 10 * 1024 * 1024  # 10MB

    # Rate limiting (requests per minute per IP)
    enable_rate_limit: bool = False
    rate_limit_requests: int = 60
    rate_limit_window: int = 60

    # Monitoring
    enable_metrics: bool = True
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", protected_namespaces=("settings_",)
    )


settings = Settings()
