"""Models for the vector store module."""

from typing import List, Dict, Any, Optional, Tuple, Union
from enum import Enum
from pydantic import BaseModel, Field
import numpy as np
from datetime import datetime
from pathlib import Path


class VectorStoreType(str, Enum):
    """Supported vector store types."""
    FAISS = "faiss"
    CHROMA = "chroma"
    PINECONE = "pinecone"
    QDRANT = "qdrant"
    WEAVIATE = "weaviate"
    CUSTOM = "custom"


class DistanceMetric(str, Enum):
    """Distance metrics for similarity search."""
    L2 = "l2"  # Euclidean distance
    COSINE = "cosine"  # Cosine similarity
    DOT_PRODUCT = "dot_product"  # Dot product similarity
    INNER_PRODUCT = "inner_product"  # Inner product


class VectorStoreConfig(BaseModel):
    """Configuration for vector stores."""
    
    model_config = {"protected_namespaces": ()}
    
    store_type: VectorStoreType = Field(
        default=VectorStoreType.FAISS,
        description="Type of vector store"
    )
    dimension: int = Field(
        default=384,
        description="Dimension of vectors"
    )
    distance_metric: DistanceMetric = Field(
        default=DistanceMetric.L2,
        description="Distance metric for similarity"
    )
    index_type: Optional[str] = Field(
        default=None,
        description="Specific index type (e.g., 'Flat', 'IVF', 'HNSW')"
    )
    persist_directory: Optional[Path] = Field(
        default=None,
        description="Directory for persisting the index"
    )
    batch_size: int = Field(
        default=100,
        description="Batch size for bulk operations"
    )
    normalize_embeddings: bool = Field(
        default=False,
        description="Whether to normalize embeddings before storing"
    )
    additional_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional store-specific parameters"
    )


class SearchResult(BaseModel):
    """Single search result."""
    
    model_config = {"protected_namespaces": ()}
    
    vector_id: str = Field(
        description="ID of the matched vector"
    )
    score: float = Field(
        description="Similarity score (distance or similarity)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata associated with the vector"
    )
    vector: Optional[List[float]] = Field(
        default=None,
        description="The actual vector (if requested)"
    )
    
    @property
    def content(self) -> Optional[str]:
        """Get content from metadata if available."""
        return self.metadata.get("content")
    
    @property
    def chunk_id(self) -> Optional[str]:
        """Get chunk ID from metadata if available."""
        return self.metadata.get("chunk_id")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vector_id": self.vector_id,
            "score": self.score,
            "metadata": self.metadata,
            "vector": self.vector
        }


class SearchBatch(BaseModel):
    """Batch of search results."""
    
    model_config = {"protected_namespaces": ()}
    
    query: str = Field(
        description="Original query text"
    )
    results: List[SearchResult] = Field(
        description="List of search results"
    )
    query_vector: Optional[List[float]] = Field(
        default=None,
        description="Query vector used for search"
    )
    search_time_ms: float = Field(
        description="Time taken for search in milliseconds"
    )
    total_results: int = Field(
        description="Total number of results found"
    )
    
    @property
    def top_result(self) -> Optional[SearchResult]:
        """Get the top result."""
        return self.results[0] if self.results else None
    
    @property
    def top_k(self) -> int:
        """Get the number of results returned."""
        return len(self.results)
    
    def get_contents(self) -> List[str]:
        """Get all content from results."""
        return [r.content for r in self.results if r.content]
    
    def get_metadata_list(self) -> List[Dict[str, Any]]:
        """Get all metadata from results."""
        return [r.metadata for r in self.results]


class IndexMetadata(BaseModel):
    """Metadata about the vector index."""
    
    model_config = {"protected_namespaces": ()}
    
    total_vectors: int = Field(
        default=0,
        description="Total number of vectors in the index"
    )
    dimension: int = Field(
        description="Dimension of vectors"
    )
    index_type: str = Field(
        description="Type of index being used"
    )
    distance_metric: DistanceMetric = Field(
        description="Distance metric being used"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="When the index was created"
    )
    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="When the index was last updated"
    )
    storage_size_bytes: Optional[int] = Field(
        default=None,
        description="Size of the index in bytes"
    )
    is_trained: bool = Field(
        default=False,
        description="Whether the index has been trained (for some index types)"
    )
    additional_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional index-specific information"
    )


class StorageMetrics(BaseModel):
    """Metrics for vector storage operations."""
    
    model_config = {"protected_namespaces": ()}
    
    total_adds: int = Field(
        default=0,
        description="Total number of vectors added"
    )
    total_searches: int = Field(
        default=0,
        description="Total number of searches performed"
    )
    total_deletes: int = Field(
        default=0,
        description="Total number of vectors deleted"
    )
    avg_add_time_ms: float = Field(
        default=0.0,
        description="Average time to add a vector"
    )
    avg_search_time_ms: float = Field(
        default=0.0,
        description="Average search time"
    )
    cache_hits: int = Field(
        default=0,
        description="Number of cache hits (if caching enabled)"
    )
    cache_misses: int = Field(
        default=0,
        description="Number of cache misses"
    )
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total
    
    def update_add_time(self, time_ms: float) -> None:
        """Update add time statistics."""
        self.total_adds += 1
        # Running average
        self.avg_add_time_ms = (
            (self.avg_add_time_ms * (self.total_adds - 1) + time_ms) 
            / self.total_adds
        )
    
    def update_search_time(self, time_ms: float) -> None:
        """Update search time statistics."""
        self.total_searches += 1
        # Running average
        self.avg_search_time_ms = (
            (self.avg_search_time_ms * (self.total_searches - 1) + time_ms)
            / self.total_searches
        )


class VectorBatch(BaseModel):
    """Batch of vectors for bulk operations."""
    
    vectors: List[List[float]] = Field(
        description="List of vectors"
    )
    ids: List[str] = Field(
        description="List of vector IDs"
    )
    metadata: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of metadata for each vector"
    )
    
    @property
    def size(self) -> int:
        """Get batch size."""
        return len(self.vectors)
    
    @property
    def dimension(self) -> int:
        """Get vector dimension."""
        if self.vectors:
            return len(self.vectors[0])
        return 0
    
    def to_numpy(self) -> np.ndarray:
        """Convert vectors to numpy array."""
        if not self.vectors:
            return np.array([])
        return np.array(self.vectors)
    
    def validate(self) -> bool:
        """Validate batch consistency."""
        if not self.vectors:
            return True
            
        # Check all lists have same length
        if not (len(self.ids) == len(self.vectors) == len(self.metadata or [])):
            return False
            
        # Check all vectors have same dimension
        dim = len(self.vectors[0])
        return all(len(v) == dim for v in self.vectors)