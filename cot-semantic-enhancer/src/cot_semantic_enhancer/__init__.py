"""CoT Semantic Enhancement Library.

Advanced semantic similarity and document processing for Chain-of-Thought reasoning systems.
"""

__version__ = "1.1.0"
__author__ = "CoT Development Team"

from .core.embedding_provider import EmbeddingProvider
from .core.vector_store import VectorStore
from .core.semantic_engine import SemanticEngine
from .document_processing.markdown_enricher import DocumentEnricher
from .enhanced_search.structured_search import StructuredSearch

__all__ = [
    "EmbeddingProvider",
    "VectorStore", 
    "SemanticEngine",
    "DocumentEnricher",
    "StructuredSearch",
    "__version__",
]