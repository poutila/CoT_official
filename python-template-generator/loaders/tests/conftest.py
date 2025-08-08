"""Pytest configuration and shared fixtures for all tests."""

import shutil

# Add parent directory to path for imports
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ================== Path Fixtures ==================


@pytest.fixture
def test_data_dir() -> Path:
    """Path to test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.fixture
def sample_markdown_file(temp_dir) -> Path:
    """Create a sample markdown file for testing."""
    content = """# Test Document

## Section 1
This is test content with **bold** and *italic* text.

### Subsection 1.1
Here's a code block:

```python
def hello():
    return "world"
```

## Section 2
Some more content with a [link](https://example.com).

```bash
echo "test"
```

### Requirements
- REQ-001: System must be fast
- REQ-002: System must be secure
"""
    file_path = temp_dir / "test.md"
    file_path.write_text(content)
    return file_path


# ================== Model Fixtures ==================


@pytest.fixture
def sample_chunk_config():
    """Create a sample chunking configuration."""
    from chunker.models import ChunkingConfig

    return ChunkingConfig(
        max_tokens=100,
        overlap_tokens=10,
        respect_sentence_boundaries=True,
        preserve_code_blocks=True,
    )


@pytest.fixture
def sample_embedding_config():
    """Create a sample embedding configuration."""
    from embeddings.models import EmbeddingProviderConfig

    return EmbeddingProviderConfig(
        model_name="all-MiniLM-L6-v2",
        device="cpu",
        cache_embeddings=True,
        cache_size=100,
        batch_size=8,
    )


@pytest.fixture
def sample_vector_store_config():
    """Create a sample vector store configuration."""
    from vector_store.models import DistanceMetric, VectorStoreConfig

    return VectorStoreConfig(
        dimension=384, distance_metric=DistanceMetric.COSINE, index_type="Flat"
    )


@pytest.fixture
def sample_rag_config():
    """Create a sample RAG pipeline configuration."""
    from rag_models import RAGConfig

    return RAGConfig(
        chunk_size=200, chunk_overlap=20, embedding_model="all-MiniLM-L6-v2", k=5, verbose=False
    )


# ================== Data Fixtures ==================


@pytest.fixture
def sample_text() -> str:
    """Sample text for testing."""
    return """Python is a high-level programming language.
It emphasizes code readability and simplicity.
Python supports multiple programming paradigms."""


@pytest.fixture
def sample_texts() -> list[str]:
    """Sample texts for batch testing."""
    return [
        "Python is great for data science.",
        "Machine learning uses algorithms to learn patterns.",
        "Natural language processing analyzes text data.",
        "Deep learning uses neural networks.",
        "Computer vision processes images.",
    ]


@pytest.fixture
def sample_vector() -> np.ndarray:
    """Create a sample vector for testing."""
    np.random.seed(42)
    return np.random.randn(384).astype(np.float32)


@pytest.fixture
def sample_vectors() -> list[np.ndarray]:
    """Create sample vectors for batch testing."""
    np.random.seed(42)
    return [np.random.randn(384).astype(np.float32) for _ in range(10)]


@pytest.fixture
def sample_metadata() -> dict[str, Any]:
    """Sample metadata for testing."""
    return {
        "source": "test.md",
        "section": "introduction",
        "type": "text",
        "timestamp": "2024-01-01T00:00:00Z",
    }


# ================== Mock Fixtures ==================


@pytest.fixture
def mock_embedding_provider(mocker):
    """Mock embedding provider for testing."""
    from embeddings.models import EmbeddingResult

    mock = mocker.Mock()
    mock.embed.return_value = EmbeddingResult(
        text="test",
        embedding=[0.1] * 384,
        numpy=np.array([0.1] * 384),
        dimension=384,
        model="mock-model",
        cached=False,
    )
    return mock


@pytest.fixture
def mock_vector_store(mocker):
    """Mock vector store for testing."""
    from vector_store.models import SearchResult

    mock = mocker.Mock()
    mock.size = 0
    mock.add.return_value = "mock-id-123"
    mock.search.return_value = [
        SearchResult(id="mock-id-123", score=0.95, metadata={"text": "test"}, vector=None)
    ]
    return mock


@pytest.fixture
def mock_chunker(mocker):
    """Mock chunker for testing."""
    from chunker.models import Chunk, ChunkMetadata, ChunkType

    mock = mocker.Mock()
    mock.chunk_text.return_value = [
        Chunk(
            content="Test chunk",
            chunk_id="chunk-001",
            source_file="test.md",
            chunk_type=ChunkType.TEXT,
            token_count=10,
            metadata=ChunkMetadata(chunk_index=0),
        )
    ]
    return mock


# ================== Component Fixtures ==================


@pytest.fixture
def token_counter():
    """Create a token counter instance."""
    from chunker.token_counter import TokenCounter

    return TokenCounter()


@pytest.fixture
def semantic_chunker(sample_chunk_config):
    """Create a semantic chunker instance."""
    from chunker.semantic_chunker import SemanticChunker

    return SemanticChunker(sample_chunk_config)


@pytest.fixture
def embedding_provider(sample_embedding_config):
    """Create an embedding provider instance."""
    from embeddings.sentence_transformer_provider import SentenceTransformerProvider

    return SentenceTransformerProvider(sample_embedding_config)


@pytest.fixture
def vector_store(sample_vector_store_config):
    """Create a vector store instance."""
    from vector_store.faiss_store import FAISSVectorStore

    return FAISSVectorStore(sample_vector_store_config)


@pytest.fixture
def rag_pipeline(sample_rag_config):
    """Create a RAG pipeline instance."""
    from rag_pipeline import RAGPipeline

    return RAGPipeline(sample_rag_config)


# ================== Document Fixtures ==================


@pytest.fixture
def sample_document():
    """Create a sample document for testing."""
    from rag_models import Document

    return Document(
        page_content="This is test content.", metadata={"source": "test.md", "section": "intro"}
    )


@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    from rag_models import Document

    return [
        Document(
            page_content="Python programming basics.",
            metadata={"source": "python.md", "topic": "programming"},
        ),
        Document(
            page_content="Machine learning fundamentals.",
            metadata={"source": "ml.md", "topic": "ai"},
        ),
        Document(
            page_content="Data science techniques.", metadata={"source": "ds.md", "topic": "data"}
        ),
    ]


# ================== Test Markers ==================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "requires_model: marks tests that require ML models")
