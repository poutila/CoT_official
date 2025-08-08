"""Chunker Module for RAG Pipeline.

This module provides intelligent document chunking for RAG applications.
It ensures code examples are never split and maintains semantic boundaries.
"""

from .base_chunker import BaseChunker
from .models import Chunk, ChunkingConfig, ChunkMetadata, ChunkType
from .semantic_chunker import SemanticChunker
from .token_counter import TokenCounter

__all__ = [
    "Chunk",
    "ChunkMetadata",
    "ChunkType",
    "ChunkingConfig",
    "BaseChunker",
    "SemanticChunker",
    "TokenCounter",
]

__version__ = "0.1.0"
