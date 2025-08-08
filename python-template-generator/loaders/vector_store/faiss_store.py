"""FAISS vector store implementation."""

from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import numpy as np
import pickle
import time
import logging

from .base_store import BaseVectorStore
from .models import (
    VectorStoreConfig,
    SearchResult,
    IndexMetadata,
    DistanceMetric,
    VectorStoreType,
)

# Set up logging
logger = logging.getLogger(__name__)


class FAISSVectorStore(BaseVectorStore):
    """Vector store implementation using FAISS.
    
    FAISS (Facebook AI Similarity Search) is a library for efficient
    similarity search and clustering of dense vectors.
    
    This implementation supports:
    - Multiple index types (Flat, IVF, HNSW)
    - L2 and cosine similarity
    - Persistence to disk
    - Metadata storage alongside vectors
    """
    
    def __init__(
        self,
        config: Optional[VectorStoreConfig] = None,
        index_type: Optional[str] = None
    ):
        """Initialize FAISS vector store.
        
        Args:
            config: Vector store configuration
            index_type: Override index type from config
                Options: 'Flat', 'IVF', 'HNSW', 'LSH'
        """
        # Set default config if not provided
        if config is None:
            config = VectorStoreConfig(
                store_type=VectorStoreType.FAISS,
                index_type=index_type or "Flat"
            )
        elif index_type:
            config.index_type = index_type
        
        # Store references before calling parent init
        self.index = None
        self.id_to_idx = {}  # Map from our IDs to FAISS indices
        self.idx_to_id = {}  # Map from FAISS indices to our IDs
        self.metadata_store = {}  # Store metadata by our IDs
        self.next_idx = 0  # Next FAISS index to use
        
        super().__init__(config)
    
    def _initialize_store(self) -> None:
        """Initialize the FAISS index."""
        try:
            import faiss
        except ImportError:
            raise ImportError(
                "faiss-cpu is not installed. "
                "Install it with: uv add faiss-cpu"
            )
        
        self.faiss = faiss
        index_type = self.config.index_type or "Flat"
        
        logger.info(f"Initializing FAISS index: {index_type}, dimension: {self.dimension}")
        
        # Create appropriate index based on type
        if index_type == "Flat":
            # Exact search with L2 distance
            if self.distance_metric == DistanceMetric.COSINE:
                # For cosine similarity, we normalize vectors and use inner product
                self.index = faiss.IndexFlatIP(self.dimension)
                self.normalize = True  # Force normalization for cosine
            else:
                self.index = faiss.IndexFlatL2(self.dimension)
                
        elif index_type == "IVF":
            # Inverted file index for faster search on large datasets
            nlist = self.config.additional_params.get("nlist", 100)
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            
        elif index_type == "HNSW":
            # Hierarchical Navigable Small World graph
            M = self.config.additional_params.get("M", 32)
            self.index = faiss.IndexHNSWFlat(self.dimension, M)
            
        elif index_type == "LSH":
            # Locality Sensitive Hashing
            nbits = self.config.additional_params.get("nbits", self.dimension * 8)
            self.index = faiss.IndexLSH(self.dimension, nbits)
            
        else:
            raise ValueError(f"Unknown index type: {index_type}")
        
        logger.info(f"FAISS index initialized: {self.index}")
    
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
        start_time = time.time()
        
        # Validate and prepare vector
        vector = self._validate_vector(vector)
        
        # Generate ID if not provided
        if vector_id is None:
            vector_id = self._generate_id()
        
        # Check if we need to train the index (for IVF)
        if hasattr(self.index, 'is_trained') and not self.index.is_trained:
            # For IVF, we need some vectors before we can add
            # Just train with this single vector for now
            self.index.train(vector.reshape(1, -1))
        
        # Add to FAISS index
        faiss_idx = self.next_idx
        self.index.add(vector.reshape(1, -1))
        
        # Update mappings
        self.id_to_idx[vector_id] = faiss_idx
        self.idx_to_id[faiss_idx] = vector_id
        self.next_idx += 1
        
        # Store metadata
        if metadata:
            self.metadata_store[vector_id] = metadata
        else:
            self.metadata_store[vector_id] = {}
        
        # Update metrics
        add_time = (time.time() - start_time) * 1000
        self.metrics.update_add_time(add_time)
        
        return vector_id
    
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
        start_time = time.time()
        
        # Convert to numpy array
        if isinstance(vectors, list):
            vectors = np.array(vectors)
        
        # Validate dimensions
        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Vector dimension {vectors.shape[1]} doesn't match "
                f"index dimension {self.dimension}"
            )
        
        # Normalize if needed
        if self.normalize:
            vectors = np.array([self._normalize_vector(v) for v in vectors])
        
        # Generate IDs if not provided
        if ids is None:
            ids = [self._generate_id() for _ in range(len(vectors))]
        
        # Check if we need to train the index (for IVF)
        if hasattr(self.index, 'is_trained') and not self.index.is_trained:
            # Train with these vectors
            self.index.train(vectors)
        
        # Add to FAISS index
        start_idx = self.next_idx
        self.index.add(vectors)
        
        # Update mappings and metadata
        for i, vector_id in enumerate(ids):
            faiss_idx = start_idx + i
            self.id_to_idx[vector_id] = faiss_idx
            self.idx_to_id[faiss_idx] = vector_id
            
            if metadata and i < len(metadata):
                self.metadata_store[vector_id] = metadata[i]
            else:
                self.metadata_store[vector_id] = {}
        
        self.next_idx = start_idx + len(vectors)
        
        # Update metrics
        add_time = (time.time() - start_time) * 1000
        for _ in range(len(vectors)):
            self.metrics.update_add_time(add_time / len(vectors))
        
        return ids
    
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
            filter_metadata: Optional metadata filters (not implemented yet)
            include_vectors: Whether to include vectors in results
            
        Returns:
            List of search results
        """
        start_time = time.time()
        
        # Validate and prepare query vector
        query_vector = self._validate_vector(query_vector)
        
        # Ensure k doesn't exceed number of vectors
        k = min(k, self.index.ntotal)
        
        if k == 0:
            return []
        
        # Search in FAISS
        distances, indices = self.index.search(query_vector.reshape(1, -1), k)
        
        # Convert results
        results = []
        for i in range(len(indices[0])):
            faiss_idx = indices[0][i]
            distance = distances[0][i]
            
            # Skip if invalid index
            if faiss_idx == -1:
                continue
            
            # Get our ID
            if faiss_idx not in self.idx_to_id:
                continue
                
            vector_id = self.idx_to_id[faiss_idx]
            
            # Get metadata
            meta = self.metadata_store.get(vector_id, {})
            
            # Apply metadata filter if provided
            if filter_metadata:
                skip = False
                for key, value in filter_metadata.items():
                    if key not in meta or meta[key] != value:
                        skip = True
                        break
                if skip:
                    continue
            
            # Get vector if requested
            vector = None
            if include_vectors:
                vector_array = self.index.reconstruct(int(faiss_idx))
                vector = vector_array.tolist()
            
            # Convert distance to similarity score if using cosine
            if self.distance_metric == DistanceMetric.COSINE:
                # Inner product of normalized vectors = cosine similarity
                score = float(distance)
            else:
                # For L2 distance, convert to similarity (smaller is better)
                score = 1.0 / (1.0 + float(distance))
            
            result = SearchResult(
                vector_id=vector_id,
                score=score,
                metadata=meta,
                vector=vector
            )
            results.append(result)
        
        # Update metrics
        search_time = (time.time() - start_time) * 1000
        self.metrics.update_search_time(search_time)
        
        return results
    
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
        if vector_id not in self.id_to_idx:
            return None
        
        faiss_idx = self.id_to_idx[vector_id]
        metadata = self.metadata_store.get(vector_id, {})
        
        vector = None
        if include_vector:
            vector_array = self.index.reconstruct(int(faiss_idx))
            vector = vector_array.tolist()
        
        return (vector, metadata)
    
    def delete(self, vector_id: str) -> bool:
        """Delete a vector by ID.
        
        Note: FAISS doesn't support deletion directly, so this
        just removes from our mappings. The vector remains in
        the index but won't be returned in searches.
        
        Args:
            vector_id: ID of the vector to delete
            
        Returns:
            True if deleted, False if not found
        """
        if vector_id not in self.id_to_idx:
            return False
        
        faiss_idx = self.id_to_idx[vector_id]
        
        # Remove from mappings
        del self.id_to_idx[vector_id]
        del self.idx_to_id[faiss_idx]
        del self.metadata_store[vector_id]
        
        self.metrics.total_deletes += 1
        
        return True
    
    def clear(self) -> None:
        """Clear all vectors from the store."""
        # Re-initialize the index
        self._initialize_store()
        
        # Clear mappings
        self.id_to_idx.clear()
        self.idx_to_id.clear()
        self.metadata_store.clear()
        self.next_idx = 0
    
    def save(self, path: Union[str, Path]) -> None:
        """Save the index to disk.
        
        Args:
            path: Path to save the index
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_path = path / "index.faiss"
        self.faiss.write_index(self.index, str(index_path))
        
        # Save metadata and mappings
        metadata_path = path / "metadata.pkl"
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'id_to_idx': self.id_to_idx,
                'idx_to_id': self.idx_to_id,
                'metadata_store': self.metadata_store,
                'next_idx': self.next_idx,
                'config': self.config.dict(),
                'metrics': self.metrics.dict()
            }, f)
        
        logger.info(f"Index saved to {path}")
    
    def load(self, path: Union[str, Path]) -> None:
        """Load the index from disk.
        
        Args:
            path: Path to load the index from
        """
        path = Path(path)
        
        # Load FAISS index
        index_path = path / "index.faiss"
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        
        self.index = self.faiss.read_index(str(index_path))
        
        # Load metadata and mappings
        metadata_path = path / "metadata.pkl"
        if metadata_path.exists():
            with open(metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.id_to_idx = data['id_to_idx']
                self.idx_to_id = data['idx_to_id']
                self.metadata_store = data['metadata_store']
                self.next_idx = data['next_idx']
                
                # Update metrics if available
                if 'metrics' in data:
                    for key, value in data['metrics'].items():
                        if hasattr(self.metrics, key):
                            setattr(self.metrics, key, value)
        
        logger.info(f"Index loaded from {path}")
    
    def get_metadata_dict(self) -> IndexMetadata:
        """Get metadata about the index.
        
        Returns:
            Index metadata
        """
        # Calculate storage size (approximate)
        storage_size = 0
        if self.index:
            # Each vector takes dimension * 4 bytes (float32)
            storage_size = self.index.ntotal * self.dimension * 4
        
        return IndexMetadata(
            total_vectors=len(self.id_to_idx),
            dimension=self.dimension,
            index_type=self.config.index_type or "Flat",
            distance_metric=self.distance_metric,
            storage_size_bytes=storage_size,
            is_trained=getattr(self.index, 'is_trained', True) if self.index else False,
            additional_info={
                "faiss_ntotal": self.index.ntotal if self.index else 0,
                "orphaned_indices": self.index.ntotal - len(self.id_to_idx) if self.index else 0
            }
        )