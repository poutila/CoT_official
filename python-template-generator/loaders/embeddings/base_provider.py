"""Base embedding provider interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Union, Dict, Any
import hashlib
import time
import numpy as np

from .models import (
    EmbeddingResult,
    EmbeddingBatch,
    EmbeddingMetadata,
    EmbeddingProviderConfig,
    EmbeddingCache,
)


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers.
    
    All embedding providers should inherit from this class and implement
    the required methods.
    """
    
    def __init__(self, config: Optional[EmbeddingProviderConfig] = None):
        """Initialize the embedding provider.
        
        Args:
            config: Provider configuration
        """
        self.config = config or EmbeddingProviderConfig()
        self.model_name = self.config.model_name
        self.dimension = self.config.dimension
        self.normalize = self.config.normalize
        
        # Initialize cache if enabled
        self.cache = EmbeddingCache() if self.config.cache_embeddings else None
        
        # Initialize the actual model
        self._initialize_model()
    
    @abstractmethod
    def _initialize_model(self) -> None:
        """Initialize the underlying embedding model.
        
        This method should set up the actual model used for embedding.
        """
        pass
    
    @abstractmethod
    def _encode_single(self, text: str) -> np.ndarray:
        """Encode a single text to embedding.
        
        Args:
            text: Text to encode
            
        Returns:
            Embedding as numpy array
        """
        pass
    
    @abstractmethod
    def _encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode a batch of texts to embeddings.
        
        Args:
            texts: List of texts to encode
            
        Returns:
            Embeddings as numpy array of shape (batch_size, dimension)
        """
        pass
    
    def embed(self, text: str, **kwargs) -> EmbeddingResult:
        """Generate embedding for a single text.
        
        Args:
            text: Text to embed
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Embedding result with metadata
        """
        # Check cache first
        text_hash = self._hash_text(text)
        if self.cache:
            cached = self.cache.get(text_hash)
            if cached:
                return cached
        
        # Generate embedding
        start_time = time.time()
        embedding_vector = self._encode_single(text)
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Normalize if requested
        if self.normalize:
            embedding_vector = self._normalize(embedding_vector)
        
        # Create metadata
        metadata = EmbeddingMetadata(
            text_hash=text_hash,
            model_name=self.model_name,
            processing_time_ms=processing_time,
            truncated=self._check_truncation(text),
            custom_metadata=kwargs
        )
        
        # Create result
        result = EmbeddingResult(
            embedding=embedding_vector.tolist(),
            text=text,
            metadata=metadata
        )
        
        # Cache if enabled
        if self.cache:
            self.cache.put(text_hash, result)
        
        return result
    
    def embed_batch(
        self, 
        texts: List[str],
        show_progress: bool = False,
        **kwargs
    ) -> EmbeddingBatch:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            show_progress: Whether to show progress bar
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Batch of embedding results
        """
        start_time = time.time()
        results = []
        
        # Process in batches for efficiency
        batch_size = self.config.batch_size
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Check cache for each text
            cached_indices = []
            uncached_texts = []
            uncached_indices = []
            
            for j, text in enumerate(batch_texts):
                text_hash = self._hash_text(text)
                if self.cache:
                    cached = self.cache.get(text_hash)
                    if cached:
                        results.append(cached)
                        cached_indices.append(i + j)
                        continue
                
                uncached_texts.append(text)
                uncached_indices.append(i + j)
            
            # Generate embeddings for uncached texts
            if uncached_texts:
                batch_embeddings = self._encode_batch(uncached_texts)
                
                # Normalize if requested
                if self.normalize:
                    batch_embeddings = np.array([
                        self._normalize(emb) for emb in batch_embeddings
                    ])
                
                # Create results for uncached texts
                for j, (text, embedding) in enumerate(zip(uncached_texts, batch_embeddings)):
                    text_hash = self._hash_text(text)
                    
                    metadata = EmbeddingMetadata(
                        text_hash=text_hash,
                        model_name=self.model_name,
                        truncated=self._check_truncation(text),
                        custom_metadata=kwargs
                    )
                    
                    result = EmbeddingResult(
                        embedding=embedding.tolist(),
                        text=text,
                        metadata=metadata
                    )
                    
                    # Cache if enabled
                    if self.cache:
                        self.cache.put(text_hash, result)
                    
                    results.append(result)
            
            if show_progress:
                progress = min(i + batch_size, len(texts))
                print(f"Processed {progress}/{len(texts)} texts...")
        
        # Sort results back to original order
        # (they might be out of order due to caching)
        results_dict = {r.text: r for r in results}
        sorted_results = [results_dict[text] for text in texts]
        
        total_time = (time.time() - start_time) * 1000
        
        return EmbeddingBatch(
            embeddings=sorted_results,
            model_name=self.model_name,
            total_processing_time_ms=total_time
        )
    
    async def embed_async(self, text: str, **kwargs) -> EmbeddingResult:
        """Async version of embed (can be overridden for async providers).
        
        Args:
            text: Text to embed
            **kwargs: Additional parameters
            
        Returns:
            Embedding result
        """
        # Default implementation just calls sync version
        return self.embed(text, **kwargs)
    
    async def embed_batch_async(
        self,
        texts: List[str],
        **kwargs
    ) -> EmbeddingBatch:
        """Async version of embed_batch.
        
        Args:
            texts: Texts to embed
            **kwargs: Additional parameters
            
        Returns:
            Batch of embeddings
        """
        # Default implementation just calls sync version
        return self.embed_batch(texts, **kwargs)
    
    def _hash_text(self, text: str) -> str:
        """Generate hash for text (for caching).
        
        Args:
            text: Text to hash
            
        Returns:
            Hash string
        """
        return hashlib.md5(text.encode()).hexdigest()
    
    def _normalize(self, embedding: np.ndarray) -> np.ndarray:
        """Normalize embedding to unit length.
        
        Args:
            embedding: Embedding vector
            
        Returns:
            Normalized embedding
        """
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm
    
    def _check_truncation(self, text: str) -> bool:
        """Check if text will be truncated.
        
        Args:
            text: Text to check
            
        Returns:
            True if text will be truncated
        """
        if self.config.max_seq_length:
            # Simple character-based check (providers can override)
            return len(text) > self.config.max_seq_length * 4
        return False
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        if self.cache:
            self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        if not self.cache:
            return {"cache_enabled": False}
        
        return {
            "cache_enabled": True,
            "cache_size": self.cache.size,
            "cache_hits": self.cache.hits,
            "cache_misses": self.cache.misses,
            "hit_rate": self.cache.hit_rate,
            "max_size": self.cache.max_size
        }
    
    @property
    def is_initialized(self) -> bool:
        """Check if the provider is initialized.
        
        Returns:
            True if initialized and ready
        """
        return self.dimension is not None
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"model='{self.model_name}', "
            f"dimension={self.dimension}, "
            f"cache={self.config.cache_embeddings})"
        )