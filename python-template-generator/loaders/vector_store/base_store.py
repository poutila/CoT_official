"""Base vector store interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import time
import numpy as np
import uuid

from .models import (
    VectorStoreConfig,
    SearchResult,
    SearchBatch,
    IndexMetadata,
    StorageMetrics,
    VectorBatch,
)


class BaseVectorStore(ABC):
    """Abstract base class for vector stores.
    
    All vector store implementations should inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, config: Optional[VectorStoreConfig] = None):
        """Initialize the vector store.
        
        Args:
            config: Vector store configuration
        """
        self.config = config or VectorStoreConfig()
        self.dimension = self.config.dimension
        self.distance_metric = self.config.distance_metric
        self.normalize = self.config.normalize_embeddings
        
        # Initialize metrics
        self.metrics = StorageMetrics()
        
        # Initialize the actual store
        self._initialize_store()
    
    @abstractmethod
    def _initialize_store(self) -> None:
        """Initialize the underlying vector store.
        
        This method should set up the actual storage backend.
        """
        pass
    
    @abstractmethod
    def add(
        self, 
        vector: Union[List[float], np.ndarray],
        metadata: Optional[Dict[str, Any]] = None,
        vector_id: Optional[str] = None
    ) -> str:
        """Add a single vector to the store.
        
        Args:
            vector: Vector to add
            metadata: Optional metadata
            vector_id: Optional ID (will be generated if not provided)
            
        Returns:
            ID of the added vector
        """
        pass
    
    @abstractmethod
    def add_batch(
        self,
        vectors: Union[List[List[float]], np.ndarray],
        metadata: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add multiple vectors to the store.
        
        Args:
            vectors: Vectors to add
            metadata: Optional metadata for each vector
            ids: Optional IDs (will be generated if not provided)
            
        Returns:
            List of IDs for added vectors
        """
        pass
    
    @abstractmethod
    def search(
        self,
        query_vector: Union[List[float], np.ndarray],
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
        include_vectors: bool = False
    ) -> List[SearchResult]:
        """Search for similar vectors.
        
        Args:
            query_vector: Query vector
            k: Number of results to return
            filter_metadata: Optional metadata filters
            include_vectors: Whether to include vectors in results
            
        Returns:
            List of search results
        """
        pass
    
    @abstractmethod
    def get(
        self,
        vector_id: str,
        include_vector: bool = True
    ) -> Optional[Tuple[List[float], Dict[str, Any]]]:
        """Get a vector by ID.
        
        Args:
            vector_id: ID of the vector
            include_vector: Whether to include the vector
            
        Returns:
            Tuple of (vector, metadata) or None if not found
        """
        pass
    
    @abstractmethod
    def delete(self, vector_id: str) -> bool:
        """Delete a vector by ID.
        
        Args:
            vector_id: ID of the vector to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all vectors from the store."""
        pass
    
    @abstractmethod
    def save(self, path: Union[str, Path]) -> None:
        """Save the index to disk.
        
        Args:
            path: Path to save the index
        """
        pass
    
    @abstractmethod
    def load(self, path: Union[str, Path]) -> None:
        """Load the index from disk.
        
        Args:
            path: Path to load the index from
        """
        pass
    
    @abstractmethod
    def get_metadata_dict(self) -> IndexMetadata:
        """Get metadata about the index.
        
        Returns:
            Index metadata
        """
        pass
    
    def search_batch(
        self,
        queries: List[str],
        query_vectors: Union[List[List[float]], np.ndarray],
        k: int = 5,
        include_vectors: bool = False
    ) -> List[SearchBatch]:
        """Search for multiple queries.
        
        Args:
            queries: Original query texts
            query_vectors: Query vectors
            k: Number of results per query
            include_vectors: Whether to include vectors
            
        Returns:
            List of search batches
        """
        results = []
        
        for query, query_vector in zip(queries, query_vectors):
            start_time = time.time()
            
            search_results = self.search(
                query_vector,
                k=k,
                include_vectors=include_vectors
            )
            
            search_time = (time.time() - start_time) * 1000
            
            batch = SearchBatch(
                query=query,
                results=search_results,
                query_vector=query_vector if include_vectors else None,
                search_time_ms=search_time,
                total_results=len(search_results)
            )
            
            results.append(batch)
            self.metrics.update_search_time(search_time)
        
        return results
    
    def add_with_embeddings(
        self,
        embeddings: List[Any],  # EmbeddingResult objects
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """Add vectors from embedding results.
        
        Args:
            embeddings: List of EmbeddingResult objects
            metadata: Optional additional metadata
            
        Returns:
            List of vector IDs
        """
        vectors = []
        combined_metadata = []
        
        for i, embedding in enumerate(embeddings):
            # Extract vector
            if hasattr(embedding, 'numpy'):
                vector = embedding.numpy
            elif hasattr(embedding, 'embedding'):
                vector = embedding.embedding
            else:
                vector = np.array(embedding)
            
            vectors.append(vector)
            
            # Combine metadata
            meta = {}
            
            # Add embedding metadata
            if hasattr(embedding, 'text'):
                meta['text'] = embedding.text
            if hasattr(embedding, 'metadata'):
                meta.update(embedding.metadata.dict() if hasattr(embedding.metadata, 'dict') else embedding.metadata)
            
            # Add additional metadata if provided
            if metadata and i < len(metadata):
                meta.update(metadata[i])
            
            combined_metadata.append(meta)
        
        return self.add_batch(vectors, combined_metadata)
    
    def _generate_id(self) -> str:
        """Generate a unique ID for a vector.
        
        Returns:
            Unique ID string
        """
        return str(uuid.uuid4())
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize a vector to unit length.
        
        Args:
            vector: Vector to normalize
            
        Returns:
            Normalized vector
        """
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm
    
    def _validate_vector(self, vector: Union[List[float], np.ndarray]) -> np.ndarray:
        """Validate and convert vector to numpy array.
        
        Args:
            vector: Vector to validate
            
        Returns:
            Validated numpy array
            
        Raises:
            ValueError: If vector dimension doesn't match
        """
        if isinstance(vector, list):
            vector = np.array(vector)
        
        if len(vector) != self.dimension:
            raise ValueError(
                f"Vector dimension {len(vector)} doesn't match "
                f"index dimension {self.dimension}"
            )
        
        if self.normalize:
            vector = self._normalize_vector(vector)
        
        return vector
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get storage metrics.
        
        Returns:
            Dictionary with metrics
        """
        return {
            "total_adds": self.metrics.total_adds,
            "total_searches": self.metrics.total_searches,
            "total_deletes": self.metrics.total_deletes,
            "avg_add_time_ms": self.metrics.avg_add_time_ms,
            "avg_search_time_ms": self.metrics.avg_search_time_ms,
            "cache_hit_rate": self.metrics.cache_hit_rate,
        }
    
    @property
    def size(self) -> int:
        """Get the number of vectors in the store.
        
        Returns:
            Number of vectors
        """
        metadata = self.get_metadata_dict()
        return metadata.total_vectors
    
    @property
    def is_empty(self) -> bool:
        """Check if the store is empty.
        
        Returns:
            True if empty
        """
        return self.size == 0
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"dimension={self.dimension}, "
            f"size={self.size}, "
            f"metric={self.distance_metric.value})"
        )