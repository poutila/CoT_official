"""Abstract base class for vector stores."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple, Union
from enum import Enum
import numpy as np
from dataclasses import dataclass
from datetime import datetime


class DistanceMetric(Enum):
    """Supported distance metrics for similarity search."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"


@dataclass
class SearchResult:
    """Result from a vector search operation."""
    id: str
    score: float
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None


@dataclass
class VectorStoreConfig:
    """Configuration for vector store."""
    dimension: int
    metric: DistanceMetric = DistanceMetric.COSINE
    index_type: Optional[str] = None
    namespace: Optional[str] = None
    batch_size: int = 100
    connection_params: Optional[Dict[str, Any]] = None


class VectorStore(ABC):
    """Abstract base class for vector stores.
    
    Provides a unified interface for storing and searching embeddings
    across different backends (FAISS, Pinecone, Weaviate, etc.).
    """
    
    def __init__(self, config: VectorStoreConfig):
        """Initialize vector store.
        
        Args:
            config: Vector store configuration
        """
        self.config = config
        self.dimension = config.dimension
        self.metric = config.metric
        self.namespace = config.namespace or "default"
        
    @abstractmethod
    async def add(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add embeddings to the store.
        
        Args:
            embeddings: Array of embeddings to add
            metadata: List of metadata dictionaries for each embedding
            ids: Optional list of IDs (generated if not provided)
            
        Returns:
            List of IDs for added embeddings
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        include_embeddings: bool = False
    ) -> List[SearchResult]:
        """Search for similar embeddings.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            filter: Optional metadata filter
            include_embeddings: Whether to include embeddings in results
            
        Returns:
            List of search results sorted by similarity
        """
        pass
    
    @abstractmethod
    async def delete(self, ids: List[str]) -> bool:
        """Delete embeddings by ID.
        
        Args:
            ids: List of IDs to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def update(
        self,
        ids: List[str],
        embeddings: Optional[np.ndarray] = None,
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Update existing embeddings and/or metadata.
        
        Args:
            ids: List of IDs to update
            embeddings: Optional new embeddings
            metadata: Optional new metadata
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get(
        self,
        ids: List[str],
        include_embeddings: bool = False
    ) -> List[Optional[SearchResult]]:
        """Retrieve embeddings by ID.
        
        Args:
            ids: List of IDs to retrieve
            include_embeddings: Whether to include embeddings
            
        Returns:
            List of results (None for missing IDs)
        """
        pass
    
    @abstractmethod
    async def count(self, filter: Optional[Dict[str, Any]] = None) -> int:
        """Count embeddings in the store.
        
        Args:
            filter: Optional metadata filter
            
        Returns:
            Number of embeddings matching filter
        """
        pass
    
    @abstractmethod
    async def clear(self, namespace: Optional[str] = None) -> bool:
        """Clear all embeddings from store.
        
        Args:
            namespace: Optional namespace to clear (all if None)
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    async def batch_add(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        batch_size: Optional[int] = None
    ) -> List[str]:
        """Add embeddings in batches.
        
        Args:
            embeddings: Array of embeddings
            metadata: List of metadata dictionaries
            ids: Optional list of IDs
            batch_size: Override default batch size
            
        Returns:
            List of IDs for added embeddings
        """
        batch_size = batch_size or self.config.batch_size
        all_ids = []
        
        for i in range(0, len(embeddings), batch_size):
            batch_embeddings = embeddings[i:i + batch_size]
            batch_metadata = metadata[i:i + batch_size]
            batch_ids = ids[i:i + batch_size] if ids else None
            
            result_ids = await self.add(batch_embeddings, batch_metadata, batch_ids)
            all_ids.extend(result_ids)
        
        return all_ids
    
    async def similarity_search(
        self,
        query_embedding: np.ndarray,
        threshold: float = 0.7,
        k: int = 100,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search with similarity threshold.
        
        Args:
            query_embedding: Query embedding
            threshold: Minimum similarity score
            k: Maximum results to consider
            filter: Optional metadata filter
            
        Returns:
            Results above threshold, sorted by similarity
        """
        results = await self.search(query_embedding, k, filter)
        return [r for r in results if r.score >= threshold]
    
    async def hybrid_search(
        self,
        query_embedding: np.ndarray,
        keywords: List[str],
        k: int = 5,
        embedding_weight: float = 0.7
    ) -> List[SearchResult]:
        """Hybrid search combining embeddings and keywords.
        
        Args:
            query_embedding: Query embedding
            keywords: Keywords to match in metadata
            k: Number of results
            embedding_weight: Weight for embedding similarity (0-1)
            
        Returns:
            Combined search results
        """
        # Get embedding-based results
        embedding_results = await self.search(query_embedding, k * 2)
        
        # Filter by keywords in metadata
        keyword_matches = []
        for result in embedding_results:
            # Check if any keyword appears in metadata values
            metadata_text = " ".join(str(v) for v in result.metadata.values())
            keyword_score = sum(
                1 for keyword in keywords 
                if keyword.lower() in metadata_text.lower()
            ) / len(keywords) if keywords else 0
            
            # Combine scores
            combined_score = (
                embedding_weight * result.score +
                (1 - embedding_weight) * keyword_score
            )
            
            keyword_matches.append(SearchResult(
                id=result.id,
                score=combined_score,
                metadata=result.metadata,
                embedding=result.embedding
            ))
        
        # Sort by combined score and return top k
        keyword_matches.sort(key=lambda x: x.score, reverse=True)
        return keyword_matches[:k]
    
    @abstractmethod
    async def create_index(
        self,
        index_type: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Create or optimize the vector index.
        
        Args:
            index_type: Type of index to create
            **kwargs: Additional index parameters
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store.
        
        Returns:
            Dictionary with store statistics
        """
        pass
    
    def calculate_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """Calculate similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score based on configured metric
        """
        if self.metric == DistanceMetric.COSINE:
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            return dot_product / (norm1 * norm2 + 1e-8)
        
        elif self.metric == DistanceMetric.EUCLIDEAN:
            distance = np.linalg.norm(embedding1 - embedding2)
            # Convert distance to similarity (0-1)
            return 1 / (1 + distance)
        
        elif self.metric == DistanceMetric.DOT_PRODUCT:
            return np.dot(embedding1, embedding2)
        
        elif self.metric == DistanceMetric.MANHATTAN:
            distance = np.sum(np.abs(embedding1 - embedding2))
            # Convert distance to similarity (0-1)
            return 1 / (1 + distance)
        
        else:
            raise ValueError(f"Unsupported metric: {self.metric}")