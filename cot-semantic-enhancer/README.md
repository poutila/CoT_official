# CoT Semantic Enhancement Library

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Advanced semantic similarity and document processing for Chain-of-Thought reasoning systems.

## Features

- 🚀 **Multi-Provider Embeddings**: Support for Sentence Transformers, OpenAI, Cohere, and more
- 🔍 **Vector Search**: Integration with FAISS, Pinecone, Weaviate, Qdrant, and ChromaDB
- 📄 **Document Intelligence**: Markdown enrichment with requirement extraction and semantic chunking
- ⚡ **Performance Optimized**: Caching, batching, and async operations throughout
- 🔌 **Plugin Architecture**: Loosely coupled integration with any CoT framework
- 🌍 **Cross-lingual Support**: Multilingual embeddings for global reasoning

## Installation

```bash
# Basic installation
pip install cot-semantic-enhancer

# With specific providers
pip install cot-semantic-enhancer[openai]      # OpenAI embeddings
pip install cot-semantic-enhancer[sentence-transformers]  # Local models
pip install cot-semantic-enhancer[faiss]       # FAISS vector store
pip install cot-semantic-enhancer[pinecone]    # Pinecone cloud store

# Full installation with all providers
pip install cot-semantic-enhancer[all]
```

## Quick Start

### Basic Semantic Search

```python
from cot_semantic_enhancer import SemanticEngine
from cot_semantic_enhancer.providers import SentenceTransformerProvider
from cot_semantic_enhancer.stores import FAISSVectorStore
from cot_semantic_enhancer.core import VectorStoreConfig

# Initialize components
embedding_provider = SentenceTransformerProvider(
    model_name="all-MiniLM-L6-v2",
    dimension=384
)

vector_store = FAISSVectorStore(
    config=VectorStoreConfig(dimension=384)
)

engine = SemanticEngine(
    embedding_provider=embedding_provider,
    vector_store=vector_store
)

# Add knowledge
texts = [
    "The capital of France is Paris.",
    "Python is a programming language.",
    "Machine learning requires data.",
]

await engine.add_knowledge(texts)

# Semantic search
results = await engine.semantic_search(
    query="What is the capital city of France?",
    k=3,
    threshold=0.7
)

for match in results:
    print(f"Text: {match.text}")
    print(f"Score: {match.score:.3f}")
```

### Document Processing with Markdown Enrichment

```python
from cot_semantic_enhancer import DocumentEnricher
from pathlib import Path

# Initialize enricher
enricher = DocumentEnricher()

# Process a markdown document
doc = enricher.extract_semantic_units(Path("requirements.md"))

# Access structured data
print(f"Requirements found: {len(doc.requirements)}")
for req in doc.get_requirements_by_type("MUST"):
    print(f"- {req.rule_text}")

print(f"Checklist completion: {doc.completion_rate:.1%}")

# Create semantic chunks
chunks = enricher.chunk_intelligently(doc)
for chunk in chunks:
    print(f"Type: {chunk.type}, Content: {chunk.content[:100]}...")
```

### Contradiction Detection

```python
from cot_semantic_enhancer.analysis import ContradictionDetector

detector = ContradictionDetector()

statements = [
    "All birds can fly",
    "Penguins are birds that cannot fly",
    "The sky is blue",
    "The sky is never blue"
]

contradictions = await engine.detect_contradictions(statements)

for c in contradictions:
    print(f"Contradiction found (confidence: {c.confidence:.2f}):")
    print(f"  Statement 1: {c.statement1}")
    print(f"  Statement 2: {c.statement2}")
    print(f"  Type: {c.type}")
    print(f"  Explanation: {c.explanation}")
```

## Architecture

### Plugin System

The library uses a plugin architecture for easy integration:

```python
from cot_semantic_enhancer.integration import CoTPlugin

class MyCoTSystem:
    def __init__(self):
        # Initialize your CoT system
        self.semantic_plugin = CoTPlugin(
            embedding_provider="sentence-transformers",
            vector_store="faiss"
        )
    
    async def reason(self, query):
        # Use semantic enhancement in reasoning
        context = await self.semantic_plugin.get_relevant_context(query)
        contradictions = await self.semantic_plugin.check_contradictions(context)
        # ... continue reasoning
```

### Provider Switching

Easily switch between embedding providers:

```python
# Local model (no API costs)
from cot_semantic_enhancer.providers import SentenceTransformerProvider
provider = SentenceTransformerProvider("all-mpnet-base-v2")

# OpenAI (high quality, API costs)
from cot_semantic_enhancer.providers import OpenAIProvider
provider = OpenAIProvider(api_key="your-key", model="text-embedding-ada-002")

# Cohere (good multilingual support)
from cot_semantic_enhancer.providers import CohereProvider
provider = CohereProvider(api_key="your-key", model="embed-english-v3.0")
```

## Advanced Features

### Structured Search

Search within specific document structures:

```python
from cot_semantic_enhancer.enhanced_search import StructuredSearch

search = StructuredSearch(enricher, engine)

# Search only in requirements
req_results = await search.search(
    query="security validation",
    doc_paths=[Path("security.md"), Path("api.md")],
    mode="requirements"
)

# Search in checklists
checklist_results = await search.search(
    query="deployment steps",
    doc_paths=[Path("deployment.md")],
    mode="checklists"
)
```

### Hybrid Search

Combine semantic and keyword search:

```python
results = await vector_store.hybrid_search(
    query_embedding=query_emb,
    keywords=["python", "async"],
    k=5,
    embedding_weight=0.7  # 70% semantic, 30% keyword
)
```

### Performance Optimization

```python
# Batch processing for large datasets
embeddings = await provider.embed_batch(
    texts=large_text_list,
    batch_size=64,
    show_progress=True
)

# Caching configuration
provider = SentenceTransformerProvider(
    model_name="all-MiniLM-L6-v2",
    cache_ttl=3600,      # 1 hour cache
    cache_size=10000    # Store 10k embeddings
)

# Get cache statistics
stats = provider.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.1%}")
```

## Configuration

### Environment Variables

```bash
# API Keys (if using cloud providers)
export OPENAI_API_KEY="your-openai-key"
export COHERE_API_KEY="your-cohere-key"
export PINECONE_API_KEY="your-pinecone-key"

# Performance tuning
export COT_SEMANTIC_BATCH_SIZE=32
export COT_SEMANTIC_CACHE_TTL=3600
export COT_SEMANTIC_MAX_WORKERS=4
```

### Configuration File

```python
# config.py
from cot_semantic_enhancer.config import Settings

settings = Settings(
    # Embedding settings
    default_provider="sentence-transformers",
    default_model="all-MiniLM-L6-v2",
    embedding_dimension=384,
    
    # Vector store settings
    default_store="faiss",
    vector_index_type="IVF",
    
    # Performance settings
    batch_size=32,
    cache_ttl=3600,
    max_concurrent_requests=10,
    
    # Search settings
    default_k=5,
    default_threshold=0.7
)
```

## Examples

See the `examples/` directory for complete working examples:

- `basic_semantic_search.py` - Simple similarity search
- `contradiction_detection.py` - Finding logical conflicts
- `markdown_document_search.py` - Document processing and search
- `requirement_extraction.py` - Extract and validate requirements
- `multi_provider_comparison.py` - Compare different embedding providers
- `cache_optimization.py` - Performance optimization strategies

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cot_semantic_enhancer --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Citation

If you use this library in your research, please cite:

```bibtex
@software{cot_semantic_enhancer,
  title = {CoT Semantic Enhancement Library},
  author = {CoT Development Team},
  year = {2024},
  url = {https://github.com/cot-team/cot-semantic-enhancer}
}
```

## Support

- Documentation: [https://cot-semantic-enhancer.readthedocs.io](https://cot-semantic-enhancer.readthedocs.io)
- Issues: [GitHub Issues](https://github.com/cot-team/cot-semantic-enhancer/issues)
- Discussions: [GitHub Discussions](https://github.com/cot-team/cot-semantic-enhancer/discussions)