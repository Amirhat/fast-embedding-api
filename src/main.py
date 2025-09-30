"""Fast embedding API using Litestar and fastembed."""

import logging
import time
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from litestar import Litestar, get, post, Response, Request
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from litestar.config.cors import CORSConfig
from litestar.datastructures import State
from litestar.exceptions import HTTPException
from litestar.middleware.rate_limit import RateLimitConfig
from pydantic import BaseModel, Field, field_validator

from src.model_manager import ModelCache
from src.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Request/Response models
class EmbedRequest(BaseModel):
    """Request model for embedding endpoint."""

    model_name: str = Field(..., description="Name of the embedding model to use")
    text: str = Field(..., description="Text to embed", min_length=1)

    @field_validator("text")
    @classmethod
    def validate_text_length(cls, v: str) -> str:
        if len(v) > settings.max_text_length:
            raise ValueError(
                f"Text length {len(v)} exceeds maximum allowed length of {settings.max_text_length}"
            )
        return v

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        # If allowed_models is set, enforce it
        if settings.allowed_models and v not in settings.allowed_models:
            raise ValueError(
                f"Model '{v}' is not in the allowed models list: {settings.allowed_models}"
            )
        return v


class BatchEmbedRequest(BaseModel):
    """Request model for batch embedding endpoint."""

    model_name: str = Field(..., description="Name of the embedding model to use")
    texts: List[str] = Field(..., description="List of texts to embed", min_length=1)

    @field_validator("texts")
    @classmethod
    def validate_batch_size(cls, v: List[str]) -> List[str]:
        if len(v) > settings.max_batch_size:
            raise ValueError(
                f"Batch size {len(v)} exceeds maximum allowed size of {settings.max_batch_size}"
            )
        for text in v:
            if len(text) > settings.max_text_length:
                raise ValueError(
                    f"Text length exceeds maximum allowed length of {settings.max_text_length}"
                )
        return v

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        if settings.allowed_models and v not in settings.allowed_models:
            raise ValueError(
                f"Model '{v}' is not in the allowed models list: {settings.allowed_models}"
            )
        return v


class EmbedResponse(BaseModel):
    """Response model for embedding endpoint."""

    embedding: List[float] = Field(..., description="The embedding vector")
    model_name: str = Field(..., description="Name of the model used")
    dimension: int = Field(..., description="Dimension of the embedding")
    text_length: int = Field(..., description="Length of the input text")
    processing_time_ms: float = Field(
        ..., description="Time taken to generate embedding in milliseconds"
    )


class BatchEmbedResponse(BaseModel):
    """Response model for batch embedding endpoint."""

    embeddings: List[List[float]] = Field(..., description="List of embedding vectors")
    model_name: str = Field(..., description="Name of the model used")
    dimension: int = Field(..., description="Dimension of the embeddings")
    count: int = Field(..., description="Number of embeddings generated")
    processing_time_ms: float = Field(
        ..., description="Time taken to generate embeddings in milliseconds"
    )


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    cache_info: Dict[str, Any]
    uptime_seconds: float


class ModelsResponse(BaseModel):
    """Response model for available models."""

    required_models: List[str]
    cached_models: List[str]
    allowed_models: Optional[List[str]] = None


class ModelInfoResponse(BaseModel):
    """Response model for model information."""

    model_name: str
    is_cached: bool
    load_time: Optional[float] = None
    loaded_at: Optional[float] = None
    last_used: Optional[float] = None


class MetricsResponse(BaseModel):
    """Response model for metrics."""

    total_requests: int
    total_embeddings: int
    cache_info: Dict[str, Any]
    uptime_seconds: float


# Global metrics
class Metrics:
    """Simple metrics tracking."""

    def __init__(self):
        self.total_requests = 0
        self.total_embeddings = 0
        self.start_time = time.time()

    def record_request(self):
        self.total_requests += 1

    def record_embeddings(self, count: int):
        self.total_embeddings += count

    def get_uptime(self) -> float:
        return time.time() - self.start_time


# Application lifespan
@asynccontextmanager
async def lifespan(app: Litestar):
    """
    Application lifespan manager.
    Validates required models on startup and manages model cache.
    """
    logger.info("Starting Fast Embedding API...")

    # Initialize metrics
    metrics = Metrics()
    app.state.metrics = metrics

    # Initialize model cache
    model_cache = ModelCache(
        cache_ttl=settings.model_cache_ttl,
        max_cached=settings.max_cached_models,
        cleanup_interval=settings.cleanup_interval,
        thread_pool_workers=settings.thread_pool_workers,
    )
    app.state.model_cache = model_cache

    # Start background cleanup task
    await model_cache.start()

    # Validate and warm up required models
    logger.info(f"Validating {len(settings.required_models)} required models...")
    validation_results = await model_cache.warm_up_models(settings.required_models)

    # Check if all required models are valid
    failed_models = [name for name, valid in validation_results.items() if not valid]
    if failed_models:
        logger.error(f"Failed to validate required models: {failed_models}")
        await model_cache.stop()
        raise RuntimeError(
            f"Required models failed validation: {failed_models}. "
            "Please ensure all required models are properly installed."
        )

    logger.info("All required models validated and cached successfully!")
    logger.info(f"API ready on http://{settings.host}:{settings.port}")

    yield

    # Cleanup on shutdown
    logger.info("Shutting down...")
    await model_cache.stop()
    logger.info("Shutdown complete")


# Route handlers
@post("/embed")
async def embed_text(
    data: EmbedRequest,
    state: State,
) -> Response[EmbedResponse]:
    """
    Generate embeddings for the provided text using the specified model.

    Args:
        data: Request containing model name and text
        state: Application state

    Returns:
        Embedding vector and metadata
    """
    start_time = time.time()

    try:
        model_cache: ModelCache = state.model_cache
        metrics: Metrics = state.metrics

        # Generate embedding
        embedding = await model_cache.embed(
            data.model_name, data.text, timeout=settings.request_timeout
        )

        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        # Update metrics
        if settings.enable_metrics:
            metrics.record_request()
            metrics.record_embeddings(1)

        # Prepare response
        response = EmbedResponse(
            embedding=embedding,
            model_name=data.model_name,
            dimension=len(embedding),
            text_length=len(data.text),
            processing_time_ms=round(processing_time, 2),
        )

        logger.info(
            f"Generated embedding for model '{data.model_name}' in {processing_time:.2f}ms",
            extra={
                "model_name": data.model_name,
                "text_length": len(data.text),
                "processing_time_ms": processing_time,
            },
        )

        return Response(
            content=response,
            status_code=HTTP_200_OK,
        )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            detail=str(e),
            status_code=HTTP_400_BAD_REQUEST,
        )
    except TimeoutError as e:
        logger.error(f"Timeout error: {e}")
        raise HTTPException(
            detail=str(e),
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        logger.error(f"Error generating embedding: {e}", exc_info=True)
        raise HTTPException(
            detail=f"Failed to generate embedding: {str(e)}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


@post("/embed/batch")
async def embed_batch(
    data: BatchEmbedRequest,
    state: State,
) -> Response[BatchEmbedResponse]:
    """
    Generate embeddings for multiple texts using the specified model.

    Args:
        data: Request containing model name and list of texts
        state: Application state

    Returns:
        List of embedding vectors and metadata
    """
    start_time = time.time()

    try:
        model_cache: ModelCache = state.model_cache
        metrics: Metrics = state.metrics

        # Generate embeddings
        embeddings = await model_cache.embed_batch(
            data.model_name, data.texts, timeout=settings.request_timeout
        )

        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        # Update metrics
        if settings.enable_metrics:
            metrics.record_request()
            metrics.record_embeddings(len(data.texts))

        # Prepare response
        response = BatchEmbedResponse(
            embeddings=embeddings,
            model_name=data.model_name,
            dimension=len(embeddings[0]) if embeddings else 0,
            count=len(embeddings),
            processing_time_ms=round(processing_time, 2),
        )

        logger.info(
            f"Generated {len(embeddings)} embeddings for model '{data.model_name}' in {processing_time:.2f}ms",
            extra={
                "model_name": data.model_name,
                "batch_size": len(data.texts),
                "processing_time_ms": processing_time,
            },
        )

        return Response(
            content=response,
            status_code=HTTP_200_OK,
        )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            detail=str(e),
            status_code=HTTP_400_BAD_REQUEST,
        )
    except TimeoutError as e:
        logger.error(f"Timeout error: {e}")
        raise HTTPException(
            detail=str(e),
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}", exc_info=True)
        raise HTTPException(
            detail=f"Failed to generate embeddings: {str(e)}",
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        )


@get("/health")
async def health_check(state: State) -> Response[HealthResponse]:
    """
    Health check endpoint with cache information.

    Args:
        state: Application state

    Returns:
        Health status and cache info
    """
    model_cache: ModelCache = state.model_cache
    metrics: Metrics = state.metrics

    cache_info = model_cache.get_cache_info()

    response = HealthResponse(
        status="healthy",
        cache_info=cache_info,
        uptime_seconds=round(metrics.get_uptime(), 2),
    )

    return Response(
        content=response,
        status_code=HTTP_200_OK,
    )


@get("/models")
async def list_models(state: State) -> Response[ModelsResponse]:
    """
    List required and currently cached models.

    Args:
        state: Application state

    Returns:
        Model information
    """
    model_cache: ModelCache = state.model_cache
    cache_info = model_cache.get_cache_info()

    response = ModelsResponse(
        required_models=settings.required_models,
        cached_models=cache_info["cached_models"],
        allowed_models=settings.allowed_models,
    )

    return Response(
        content=response,
        status_code=HTTP_200_OK,
    )


@get("/models/{model_name:str}")
async def get_model_info(
    model_name: str,
    state: State,
) -> Response[ModelInfoResponse]:
    """
    Get information about a specific model.

    Args:
        model_name: Name of the model
        state: Application state

    Returns:
        Model metadata
    """
    model_cache: ModelCache = state.model_cache
    info = model_cache.get_model_info(model_name)

    if info:
        response = ModelInfoResponse(
            model_name=model_name,
            is_cached=info["is_cached"],
            load_time=info.get("load_time"),
            loaded_at=info.get("loaded_at"),
            last_used=info.get("last_used"),
        )
    else:
        response = ModelInfoResponse(
            model_name=model_name,
            is_cached=False,
        )

    return Response(
        content=response,
        status_code=HTTP_200_OK,
    )


@get("/metrics")
async def get_metrics(state: State) -> Response[MetricsResponse]:
    """
    Get API metrics.

    Args:
        state: Application state

    Returns:
        Metrics information
    """
    if not settings.enable_metrics:
        raise HTTPException(
            detail="Metrics are disabled",
            status_code=HTTP_403_FORBIDDEN,
        )

    model_cache: ModelCache = state.model_cache
    metrics: Metrics = state.metrics

    cache_info = model_cache.get_cache_info()

    response = MetricsResponse(
        total_requests=metrics.total_requests,
        total_embeddings=metrics.total_embeddings,
        cache_info=cache_info,
        uptime_seconds=round(metrics.get_uptime(), 2),
    )

    return Response(
        content=response,
        status_code=HTTP_200_OK,
    )


# Configure CORS
cors_config = None
if settings.enable_cors:
    cors_config = CORSConfig(
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

# Configure rate limiting
rate_limit_config = None
if settings.enable_rate_limit:
    rate_limit_config = RateLimitConfig(
        rate_limit=("minute", settings.rate_limit_requests),
        exclude=["/health", "/metrics"],
    )

# Create Litestar app
app = Litestar(
    route_handlers=[
        embed_text,
        embed_batch,
        health_check,
        list_models,
        get_model_info,
        get_metrics,
    ],
    lifespan=[lifespan],
    cors_config=cors_config,
    middleware=[rate_limit_config.middleware] if rate_limit_config else [],
    debug=settings.debug,
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
