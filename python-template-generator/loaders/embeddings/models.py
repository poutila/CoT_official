"""Models for the embeddings module."""

from typing import List, Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field
import numpy as np
from datetime import datetime


class EmbeddingProviderType(str, Enum):
    """Supported embedding provider types."""
    SENTENCE_TRANSFORMER = "sentence_transformer"
    OPENAI = "openai"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"


class EmbeddingProviderConfig(BaseModel):
    """Configuration for embedding providers."""
    
    model_config = {"protected_namespaces": ()}
    
    provider_type: EmbeddingProviderType = Field(
        default=EmbeddingProviderType.SENTENCE_TRANSFORMER,
        description="Type of embedding provider"
    )
    model_name: str = Field(
        default="all-MiniLM-L6-v2",
        description="Model name or path"
    )
    dimension: Optional[int] = Field(
        default=None,
        description="Embedding dimension (auto-detected if not provided)"
    )
    batch_size: int = Field(
        default=32,
        description="Batch size for encoding"
    )
    normalize: bool = Field(
        default=True,
        description="Whether to normalize embeddings"
    )
    device: Optional[str] = Field(
        default=None,
        description="Device to use (cuda/cpu/auto)"
    )
    cache_embeddings: bool = Field(
        default=True,
        description="Whether to cache embeddings"
    )
    max_seq_length: Optional[int] = Field(
        default=None,
        description="Maximum sequence length"
    )
    additional_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional provider-specific parameters"
    )


class EmbeddingMetadata(BaseModel):
    """Metadata for an embedding."""
    
    model_config = {"protected_namespaces": ()}
    
    text_hash: str = Field(
        description="Hash of the input text"
    )
    model_name: str = Field(
        description="Model used for embedding"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the embedding was created"
    )
    token_count: Optional[int] = Field(
        default=None,
        description="Number of tokens in input"
    )
    truncated: bool = Field(
        default=False,
        description="Whether input was truncated"
    )
    processing_time_ms: Optional[float] = Field(
        default=None,
        description="Time taken to generate embedding"
    )
    custom_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom metadata"
    )


class EmbeddingResult(BaseModel):
    """Result of embedding generation."""
    
    embedding: List[float] = Field(
        description="The embedding vector"
    )
    text: str = Field(
        description="Original text that was embedded"
    )
    metadata: EmbeddingMetadata = Field(
        description="Embedding metadata"
    )
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return len(self.embedding)
    
    @property
    def numpy(self) -> np.ndarray:
        """Get embedding as numpy array."""
        return np.array(self.embedding)
    
    def similarity(self, other: Union['EmbeddingResult', List[float], np.ndarray]) -> float:
        """Calculate cosine similarity with another embedding.
        
        Args:
            other: Another embedding to compare with
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        if isinstance(other, EmbeddingResult):
            other_vec = other.numpy
        elif isinstance(other, list):
            other_vec = np.array(other)
        else:
            other_vec = other
            
        # Calculate cosine similarity
        dot_product = np.dot(self.numpy, other_vec)
        norm_a = np.linalg.norm(self.numpy)
        norm_b = np.linalg.norm(other_vec)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return float(dot_product / (norm_a * norm_b))


class EmbeddingBatch(BaseModel):
    """Batch of embedding results."""
    
    model_config = {"protected_namespaces": ()}
    
    embeddings: List[EmbeddingResult] = Field(
        description="List of embedding results"
    )
    model_name: str = Field(
        description="Model used for all embeddings"
    )
    total_processing_time_ms: float = Field(
        description="Total time for batch processing"
    )
    
    @property
    def size(self) -> int:
        """Get batch size."""
        return len(self.embeddings)
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        if self.embeddings:
            return self.embeddings[0].dimension
        return 0
    
    def to_numpy(self) -> np.ndarray:
        """Convert all embeddings to numpy array.
        
        Returns:
            Numpy array of shape (batch_size, dimension)
        """
        if not self.embeddings:
            return np.array([])
            
        return np.vstack([e.numpy for e in self.embeddings])
    
    def search(
        self, 
        query: Union[EmbeddingResult, List[float], np.ndarray],
        top_k: int = 5
    ) -> List[tuple[int, float]]:
        """Search for most similar embeddings in batch.
        
        Args:
            query: Query embedding
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        similarities = []
        for i, embedding in enumerate(self.embeddings):
            score = embedding.similarity(query)
            similarities.append((i, score))
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]


class EmbeddingCache(BaseModel):
    """Cache for storing embeddings."""
    
    cache: Dict[str, EmbeddingResult] = Field(
        default_factory=dict,
        description="Cache storage"
    )
    max_size: int = Field(
        default=10000,
        description="Maximum cache size"
    )
    hits: int = Field(
        default=0,
        description="Number of cache hits"
    )
    misses: int = Field(
        default=0,
        description="Number of cache misses"
    )
    
    def get(self, key: str) -> Optional[EmbeddingResult]:
        """Get embedding from cache.
        
        Args:
            key: Cache key (usually text hash)
            
        Returns:
            Cached embedding or None
        """
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def put(self, key: str, embedding: EmbeddingResult) -> None:
        """Put embedding in cache.
        
        Args:
            key: Cache key
            embedding: Embedding to cache
        """
        # Simple FIFO eviction if cache is full
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = embedding
    
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total
    
    @property
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)