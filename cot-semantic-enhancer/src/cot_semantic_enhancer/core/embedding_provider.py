"""Abstract base class for embedding providers."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
import numpy as np
import hashlib
import json
from cachetools import TTLCache
import asyncio
from concurrent.futures import ThreadPoolExecutor


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers.
    
    Provides a unified interface for generating embeddings from various sources
    including local models (Sentence Transformers) and cloud APIs (OpenAI, Cohere).
    """
    
    def __init__(
        self,
        model_name: str,
        dimension: int,
        cache_ttl: int = 3600,
        cache_size: int = 1000,
        batch_size: int = 32,
        **kwargs
    ):
        """Initialize embedding provider.
        
        Args:
            model_name: Name/identifier of the embedding model
            dimension: Expected dimension of embeddings
            cache_ttl: Cache time-to-live in seconds
            cache_size: Maximum number of cached embeddings
            batch_size: Default batch size for processing
            **kwargs: Additional provider-specific configuration
        """
        self.model_name = model_name
        self.dimension = dimension
        self.batch_size = batch_size
        self.config = kwargs
        
        # Initialize cache
        self._cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)
        
        # Thread pool for sync operations
        self._executor = ThreadPoolExecutor(max_workers=4)
        
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(f"{self.model_name}:{text}".encode()).hexdigest()
    
    def _get_from_cache(self, texts: List[str]) -> Dict[str, np.ndarray]:
        """Retrieve cached embeddings."""
        cached = {}
        for text in texts:
            key = self._get_cache_key(text)
            if key in self._cache:
                cached[text] = self._cache[key]
        return cached
    
    def _add_to_cache(self, text_embeddings: Dict[str, np.ndarray]) -> None:
        """Add embeddings to cache."""
        for text, embedding in text_embeddings.items():
            key = self._get_cache_key(text)
            self._cache[key] = embedding
    
    @abstractmethod
    async def embed_async(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings asynchronously.
        
        Args:
            texts: Single text or list of texts to embed
            
        Returns:
            Array of embeddings with shape (n_texts, dimension)
        """
        pass
    
    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Synchronous embedding generation.
        
        Args:
            texts: Single text or list of texts to embed
            
        Returns:
            Array of embeddings with shape (n_texts, dimension)
        """
        try:
            loop = asyncio.get_running_loop()
            # If already in async context, create task
            return asyncio.create_task(self.embed_async(texts))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(self.embed_async(texts))
    
    def validate_dimension(self, embeddings: np.ndarray) -> bool:
        """Validate embedding dimensions.
        
        Args:
            embeddings: Embeddings to validate
            
        Returns:
            True if dimensions match expected, False otherwise
        """
        if len(embeddings.shape) == 1:
            return embeddings.shape[0] == self.dimension
        elif len(embeddings.shape) == 2:
            return embeddings.shape[1] == self.dimension
        return False
    
    async def embed_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        show_progress: bool = False
    ) -> np.ndarray:
        """Embed texts in batches for efficiency.
        
        Args:
            texts: List of texts to embed
            batch_size: Override default batch size
            show_progress: Show progress bar if available
            
        Returns:
            Array of embeddings
        """
        batch_size = batch_size or self.batch_size
        
        # Check cache first
        cached = self._get_from_cache(texts)
        uncached_texts = [t for t in texts if t not in cached]
        
        if not uncached_texts:
            # All texts were cached
            return np.array([cached[t] for t in texts])
        
        # Process uncached texts in batches
        embeddings = []
        for i in range(0, len(uncached_texts), batch_size):
            batch = uncached_texts[i:i + batch_size]
            batch_embeddings = await self.embed_async(batch)
            embeddings.append(batch_embeddings)
            
            # Add to cache
            batch_dict = {
                text: emb for text, emb in zip(batch, batch_embeddings)
            }
            self._add_to_cache(batch_dict)
        
        # Combine cached and new embeddings in original order
        all_embeddings = {}
        all_embeddings.update(cached)
        
        if embeddings:
            combined_new = np.vstack(embeddings) if len(embeddings) > 1 else embeddings[0]
            for text, emb in zip(uncached_texts, combined_new):
                all_embeddings[text] = emb
        
        # Return in original order
        return np.array([all_embeddings[t] for t in texts])
    
    def normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """Normalize embeddings to unit length.
        
        Args:
            embeddings: Embeddings to normalize
            
        Returns:
            Normalized embeddings
        """
        norms = np.linalg.norm(embeddings, axis=-1, keepdims=True)
        return embeddings / (norms + 1e-8)  # Add epsilon to avoid division by zero
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model.
        
        Returns:
            Dictionary with model metadata
        """
        pass
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        return {
            "size": len(self._cache),
            "max_size": self._cache.maxsize,
            "ttl": self._cache.ttl,
            "hit_rate": self._calculate_hit_rate() if hasattr(self, "_cache_hits") else 0
        }
    
    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if not hasattr(self, "_cache_hits") or not hasattr(self, "_cache_misses"):
            return 0.0
        total = self._cache_hits + self._cache_misses
        return self._cache_hits / total if total > 0 else 0.0