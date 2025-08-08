"""Embeddings Module for RAG Pipeline.

This module provides embedding generation capabilities for the RAG system.
It supports multiple embedding providers with a unified interface.
"""

from .base_provider import BaseEmbeddingProvider
from .models import (
    EmbeddingBatch,
    EmbeddingMetadata,
    EmbeddingProviderConfig,
    EmbeddingProviderType,
    EmbeddingResult,
)
from .sentence_transformer_provider import SentenceTransformerProvider

__all__ = [
    "EmbeddingResult",
    "EmbeddingBatch",
    "EmbeddingMetadata",
    "EmbeddingProviderConfig",
    "EmbeddingProviderType",
    "BaseEmbeddingProvider",
    "SentenceTransformerProvider",
]

__version__ = "0.1.0"
