"""Model manager with intelligent caching and auto-offloading."""

import asyncio
import time
from typing import Dict, List, Optional
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from fastembed import TextEmbedding
import logging

logger = logging.getLogger(__name__)


class ModelCache:
    """Manages model loading, caching, and automatic offloading."""

    def __init__(
        self,
        cache_ttl: int = 3600,
        max_cached: int = 5,
        cleanup_interval: int = 60,
        thread_pool_workers: int = 4,
    ):
        """
        Initialize the model cache.

        Args:
            cache_ttl: Time in seconds before unused models are offloaded
            max_cached: Maximum number of models to keep in memory
            cleanup_interval: Cleanup check interval in seconds
            thread_pool_workers: Number of workers for CPU-intensive tasks
        """
        self._models: OrderedDict[str, TextEmbedding] = OrderedDict()
        self._last_used: Dict[str, float] = {}
        self._cache_ttl = cache_ttl
        self._max_cached = max_cached
        self._cleanup_interval = cleanup_interval
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._executor = ThreadPoolExecutor(max_workers=thread_pool_workers)
        self._model_info: Dict[str, Dict] = {}  # Store model metadata

    async def start(self):
        """Start the background cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Model cache cleanup task started")

    async def stop(self):
        """Stop the background cleanup task and shutdown executor."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Model cache cleanup task stopped")

        # Shutdown thread pool executor
        self._executor.shutdown(wait=True)
        logger.info("Thread pool executor shutdown complete")

    async def _cleanup_loop(self):
        """Background task to periodically clean up unused models."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_old_models()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}", exc_info=True)

    async def _cleanup_old_models(self):
        """Remove models that haven't been used for longer than cache_ttl."""
        async with self._lock:
            current_time = time.time()
            models_to_remove = []

            for model_name, last_used in self._last_used.items():
                if current_time - last_used > self._cache_ttl:
                    models_to_remove.append(model_name)

            for model_name in models_to_remove:
                self._unload_model(model_name)
                logger.info(
                    f"Auto-offloaded model '{model_name}' due to inactivity",
                    extra={"model_name": model_name, "reason": "ttl_expired"},
                )

    def _unload_model(self, model_name: str):
        """Unload a model from cache."""
        if model_name in self._models:
            del self._models[model_name]
            del self._last_used[model_name]
            if model_name in self._model_info:
                del self._model_info[model_name]

    async def _enforce_max_cache_size(self):
        """Ensure cache doesn't exceed max_cached models (LRU eviction)."""
        while len(self._models) >= self._max_cached:
            # Remove the least recently used model
            oldest_model = next(iter(self._models))
            self._unload_model(oldest_model)
            logger.info(
                f"Evicted model '{oldest_model}' to maintain cache size limit",
                extra={"model_name": oldest_model, "reason": "lru_eviction"},
            )

    async def get_model(self, model_name: str) -> TextEmbedding:
        """
        Get a model, loading it if necessary.

        Args:
            model_name: Name of the embedding model

        Returns:
            Loaded TextEmbedding model
        """
        async with self._lock:
            # Update access time
            self._last_used[model_name] = time.time()

            # Return cached model if available
            if model_name in self._models:
                # Move to end (most recently used)
                self._models.move_to_end(model_name)
                logger.debug(f"Using cached model '{model_name}'")
                return self._models[model_name]

            # Enforce cache size limit before loading new model
            await self._enforce_max_cache_size()

            # Load the model
            logger.info(f"Loading model '{model_name}'...")
            start_time = time.time()

            try:
                # Run in thread pool since fastembed loading is blocking
                loop = asyncio.get_event_loop()
                model = await loop.run_in_executor(
                    self._executor, lambda: TextEmbedding(model_name=model_name)
                )
                self._models[model_name] = model

                # Store model metadata
                load_time = time.time() - start_time
                self._model_info[model_name] = {
                    "load_time": load_time,
                    "loaded_at": time.time(),
                }

                logger.info(
                    f"Model '{model_name}' loaded successfully in {load_time:.2f}s",
                    extra={
                        "model_name": model_name,
                        "load_time": load_time,
                    },
                )
                return model
            except Exception as e:
                # Clean up on failure
                if model_name in self._last_used:
                    del self._last_used[model_name]
                logger.error(
                    f"Failed to load model '{model_name}': {e}",
                    extra={"model_name": model_name, "error": str(e)},
                    exc_info=True,
                )
                raise

    async def embed(
        self, model_name: str, text: str, timeout: Optional[float] = None
    ) -> List[float]:
        """
        Generate embeddings for text using the specified model.

        Args:
            model_name: Name of the embedding model
            text: Text to embed
            timeout: Optional timeout in seconds

        Returns:
            List of embedding values
        """
        model = await self.get_model(model_name)

        # Run embedding in thread pool since it's CPU-intensive
        loop = asyncio.get_event_loop()
        try:
            if timeout:
                embeddings = await asyncio.wait_for(
                    loop.run_in_executor(
                        self._executor, lambda: list(model.embed([text]))
                    ),
                    timeout=timeout,
                )
            else:
                embeddings = await loop.run_in_executor(
                    self._executor, lambda: list(model.embed([text]))
                )

            return embeddings[0].tolist()
        except asyncio.TimeoutError:
            logger.error(f"Embedding timeout for model '{model_name}'")
            raise TimeoutError(f"Embedding generation timed out after {timeout}s")

    async def embed_batch(
        self, model_name: str, texts: List[str], timeout: Optional[float] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts using the specified model.

        Args:
            model_name: Name of the embedding model
            texts: List of texts to embed
            timeout: Optional timeout in seconds

        Returns:
            List of embedding vectors
        """
        model = await self.get_model(model_name)

        # Run batch embedding in thread pool
        loop = asyncio.get_event_loop()
        try:
            if timeout:
                embeddings = await asyncio.wait_for(
                    loop.run_in_executor(
                        self._executor, lambda: list(model.embed(texts))
                    ),
                    timeout=timeout,
                )
            else:
                embeddings = await loop.run_in_executor(
                    self._executor, lambda: list(model.embed(texts))
                )

            return [emb.tolist() for emb in embeddings]
        except asyncio.TimeoutError:
            logger.error(f"Batch embedding timeout for model '{model_name}'")
            raise TimeoutError(f"Batch embedding generation timed out after {timeout}s")

    def get_cache_info(self) -> Dict:
        """Get information about the current cache state."""
        return {
            "cached_models": list(self._models.keys()),
            "num_cached": len(self._models),
            "max_cached": self._max_cached,
            "cache_ttl": self._cache_ttl,
            "cleanup_interval": self._cleanup_interval,
        }

    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get metadata about a specific model."""
        if model_name in self._model_info:
            info = self._model_info[model_name].copy()
            info["last_used"] = self._last_used.get(model_name)
            info["is_cached"] = model_name in self._models
            return info
        return None

    async def validate_model(
        self, model_name: str, cache_on_success: bool = True
    ) -> bool:
        """
        Validate that a model can be loaded and used.

        Args:
            model_name: Name of the model to validate
            cache_on_success: If True, keep the model in cache after validation

        Returns:
            True if model is valid, False otherwise
        """
        try:
            logger.info(f"Validating model '{model_name}'...")
            start_time = time.time()

            loop = asyncio.get_event_loop()
            model = await loop.run_in_executor(
                self._executor, lambda: TextEmbedding(model_name=model_name)
            )

            # Test embedding
            list(model.embed(["test"]))

            load_time = time.time() - start_time

            # Cache the validated model if requested
            if cache_on_success:
                async with self._lock:
                    await self._enforce_max_cache_size()
                    self._models[model_name] = model
                    self._last_used[model_name] = time.time()
                    self._model_info[model_name] = {
                        "load_time": load_time,
                        "loaded_at": time.time(),
                    }

            logger.info(
                f"Model '{model_name}' validated successfully in {load_time:.2f}s",
                extra={"model_name": model_name, "load_time": load_time},
            )
            return True
        except Exception as e:
            logger.error(
                f"Model validation failed for '{model_name}': {e}",
                extra={"model_name": model_name, "error": str(e)},
                exc_info=True,
            )
            return False

    async def warm_up_models(self, model_names: List[str]) -> Dict[str, bool]:
        """
        Pre-load and cache multiple models.

        Args:
            model_names: List of model names to warm up

        Returns:
            Dictionary mapping model names to validation success status
        """
        results = {}
        for model_name in model_names:
            results[model_name] = await self.validate_model(
                model_name, cache_on_success=True
            )
        return results
