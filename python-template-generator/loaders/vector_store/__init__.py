"""Vector Store Module for RAG Pipeline.

This module provides vector storage and retrieval capabilities for the RAG system.
It supports multiple vector store backends with a unified interface.
"""

from .models import (
    VectorStoreConfig,
    VectorStoreType,
    DistanceMetric,
    SearchResult,
    SearchBatch,
    IndexMetadata,
    StorageMetrics,
)
from .base_store import BaseVectorStore
from .faiss_store import FAISSVectorStore

__all__ = [
    "VectorStoreConfig",
    "VectorStoreType",
    "DistanceMetric",
    "SearchResult",
    "SearchBatch",
    "IndexMetadata",
    "StorageMetrics",
    "BaseVectorStore",
    "FAISSVectorStore",
]

__version__ = "0.1.0"