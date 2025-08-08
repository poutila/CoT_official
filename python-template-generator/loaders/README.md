# RAG Pipeline for Markdown Documentation

A complete Retrieval-Augmented Generation (RAG) system for processing, indexing, and querying markdown documentation with semantic search capabilities.

## 🚀 Quick Start

```python
from rag_pipeline import RAGPipeline
from rag_models import RAGConfig

# Create pipeline
config = RAGConfig(
    chunk_size=512,
    embedding_model="all-MiniLM-L6-v2",
    k=5
)
pipeline = RAGPipeline(config)

# Index documents
pipeline.index_documents(paths=["docs/README.md", "docs/API.md"])

# Query
result = pipeline.retrieve("How do I configure the system?")
for doc in result.documents:
    print(f"Found: {doc.page_content[:100]}...")
```

## 📦 Components

### 1. Document Enrichment (`context_fixed_enricher.py`)
Extracts rich semantic information from markdown:
- Sections with hierarchy
- Code blocks with language detection
- Tables and lists
- Requirements and metadata
- Example detection (good/bad patterns)

### 2. Chunking System (`chunker/`)
Intelligently splits documents while preserving semantic units:
- **Token-aware chunking** using tiktoken
- **Semantic boundaries** preservation
- **Code block integrity** maintenance
- **Configurable overlap** for context

### 3. Embeddings (`embeddings/`)
Generates vector representations of text:
- **Local models** via sentence-transformers
- **Batch processing** optimization
- **Built-in caching** for efficiency
- **Multiple model support**

### 4. Vector Store (`vector_store/`)
Efficient storage and retrieval using FAISS:
- **Multiple index types** (Flat, IVF, HNSW, LSH)
- **Metadata management**
- **Persistence support**
- **Similarity metrics** (cosine, L2)

### 5. RAG Pipeline (`core/pipeline.py`)
Orchestrates the complete workflow:
- Document loading and processing
- Chunking and embedding generation
- Vector storage and indexing
- Semantic search and retrieval
- LangChain-compatible interfaces

## 🎯 Features

- **🔍 Semantic Search**: Find relevant content using natural language queries
- **📝 Context Preservation**: Maintains document structure and relationships
- **⚡ High Performance**: Optimized for speed (200+ queries/sec)
- **💾 Persistence**: Save and load indexed knowledge bases
- **🔗 LangChain Compatible**: Drop-in replacement for LangChain components
- **🎨 Flexible Configuration**: Customize every aspect of the pipeline

## 📊 Architecture

```
Document → Enricher → Chunker → Embeddings → Vector Store → Retrieval
    ↓         ↓          ↓           ↓            ↓            ↓
Markdown  Sections   Chunks    Vectors      FAISS      Results
          Code blocks Overlap   Caching      Index      Ranking
          Examples   Tokens     Batching     Metadata   Scores
```

## 🛠️ Installation

### Required Dependencies
```bash
# Core dependencies (already in pyproject.toml)
uv add markdown-it-py pydantic numpy

# RAG dependencies
uv add tiktoken sentence-transformers faiss-cpu
```

### Optional Dependencies
```bash
# For GPU acceleration
uv add faiss-gpu

# For alternative embeddings
uv add openai cohere

# For cloud vector stores
uv add pinecone-client weaviate-client
```

## 📖 Usage Examples

### Basic Document Indexing
```python
from rag_pipeline import RAGPipeline
from pathlib import Path

# Initialize pipeline
pipeline = RAGPipeline()

# Index a directory of markdown files
docs_dir = Path("documentation")
md_files = list(docs_dir.glob("**/*.md"))
result = pipeline.index_documents(paths=md_files)

print(f"Indexed {result.total_documents} documents")
print(f"Created {result.total_chunks} chunks")
print(f"Generated {result.total_embeddings} embeddings")
```

### Advanced Configuration
```python
from rag_models import RAGConfig

config = RAGConfig(
    # Chunking settings
    chunk_size=1000,        # Max tokens per chunk
    chunk_overlap=100,      # Overlap between chunks
    
    # Embedding settings
    embedding_model="all-mpnet-base-v2",  # Larger model
    embedding_device="cuda",              # GPU acceleration
    
    # Vector store settings
    index_type="HNSW",      # Approximate nearest neighbor
    distance_metric="cosine",
    
    # Retrieval settings
    k=10,                   # Return top 10 results
    score_threshold=0.7,    # Minimum similarity score
    
    # Performance settings
    cache_embeddings=True,
    verbose=True
)

pipeline = RAGPipeline(config)
```

### Semantic Search with Filtering
```python
# Search with metadata filtering
result = pipeline.retrieve(
    query="error handling patterns",
    k=5,
    filter_metadata={"category": "security"}
)

for doc, score in zip(result.documents, result.scores):
    print(f"Score: {score:.3f}")
    print(f"Source: {doc.metadata['source']}")
    print(f"Content: {doc.page_content[:200]}...\n")
```

### LangChain Integration
```python
from rag_adapters import ChainAdapter

# Wrap pipeline for LangChain compatibility
chain = ChainAdapter(pipeline)

# Use with LangChain patterns
response = chain.invoke({
    "query": "What are the best practices?"
})

# Batch processing
queries = [
    {"query": "How to configure?"},
    {"query": "API endpoints"},
    {"query": "Error codes"}
]
results = chain.batch(queries)
```

### Persistence and Loading
```python
# Save indexed pipeline
pipeline.save("knowledge_base/my_docs")

# Load in another session
new_pipeline = RAGPipeline()
new_pipeline.load("knowledge_base/my_docs")

# Query immediately without re-indexing
result = new_pipeline.retrieve("search query")
```

## 🔧 Configuration Options

### RAGConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `chunk_size` | int | 512 | Maximum tokens per chunk |
| `chunk_overlap` | int | 50 | Token overlap between chunks |
| `embedding_model` | str | "all-MiniLM-L6-v2" | Sentence transformer model |
| `embedding_device` | str | "cpu" | Device for embeddings (cpu/cuda) |
| `index_type` | str | "Flat" | FAISS index type |
| `distance_metric` | str | "cosine" | Similarity metric |
| `k` | int | 4 | Number of results to retrieve |
| `score_threshold` | float | None | Minimum similarity score |
| `cache_embeddings` | bool | True | Cache computed embeddings |
| `persist_directory` | Path | None | Directory for persistence |
| `verbose` | bool | False | Print progress information |

### Supported Models

#### Embedding Models (via sentence-transformers)
- `all-MiniLM-L6-v2` - Fast, general purpose (384 dims)
- `all-mpnet-base-v2` - Higher quality (768 dims)
- `all-MiniLM-L12-v2` - Balanced (384 dims)
- `multi-qa-mpnet-base-dot-v1` - Optimized for Q&A
- `all-distilroberta-v1` - RoBERTa-based (768 dims)

#### Index Types (FAISS)
- `Flat` - Exact search, best quality
- `IVF` - Inverted file index, faster for large datasets
- `HNSW` - Hierarchical navigable small world, very fast
- `LSH` - Locality-sensitive hashing, memory efficient

## 📈 Performance Benchmarks

Based on testing with real documents:

| Operation | Performance | Notes |
|-----------|------------|--------|
| Document Loading | 50-100 docs/sec | Depends on document size |
| Chunking | 130+ chunks/sec | With semantic preservation |
| Embedding Generation | 1,298 texts/sec | Batch size 32, CPU |
| Vector Indexing | 67,847 vectors/sec | FAISS Flat index |
| Query Retrieval | 200 queries/sec | 5ms average latency |
| Pipeline End-to-End | < 1 sec | For 20 documents |

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
uv run python test_rag_pipeline.py

# Test individual components
uv run python test_chunker.py
uv run python test_embeddings.py
uv run python test_vector_store.py
```

## 🔍 Troubleshooting

### Common Issues

#### 1. CUDA/GPU Errors
```python
# Force CPU usage if GPU issues
config = RAGConfig(embedding_device="cpu")
```

#### 2. Memory Issues with Large Documents
```python
# Reduce batch size and chunk size
config = RAGConfig(
    chunk_size=256,
    chunk_overlap=25
)
```

#### 3. Slow Performance
```python
# Use approximate search for large datasets
config = RAGConfig(
    index_type="HNSW",  # Much faster than Flat
    k=5  # Retrieve fewer results
)
```

## 🤝 Integration Examples

### With Existing Enricher
```python
from context_fixed_enricher import ContextFixedEnricher

# Use enricher directly
enricher = ContextFixedEnricher("document.md")
doc = enricher.extract_rich_doc()

# Access enriched content
for section in doc.sections:
    print(f"Section: {section.title}")
    for code_block in section.code_blocks:
        print(f"  Code ({code_block.language}): {len(code_block.content)} chars")
```

### Custom Processing Pipeline
```python
from chunker import SemanticChunker, ChunkingConfig
from embeddings import SentenceTransformerProvider
from vector_store import FAISSVectorStore

# Build custom pipeline
chunker = SemanticChunker(ChunkingConfig(max_tokens=1000))
embedder = SentenceTransformerProvider()
store = FAISSVectorStore()

# Process documents manually
chunks = chunker.chunk_text(document_text)
embeddings = embedder.embed_batch([c.content for c in chunks])
store.add_batch(embeddings, metadata_list)
```

## 📚 API Reference

### Core Classes

#### `RAGPipeline`
Main orchestration class for the complete RAG workflow.

**Methods:**
- `index_documents(documents, paths)` - Index documents into vector store
- `retrieve(query, k, filter_metadata)` - Retrieve relevant documents
- `invoke(inputs, **kwargs)` - LangChain-compatible invocation
- `save(path)` - Save pipeline state
- `load(path)` - Load pipeline state

#### `RAGConfig`
Configuration class for pipeline settings.

#### `Document`
LangChain-compatible document model.

**Attributes:**
- `page_content` - Main text content
- `metadata` - Associated metadata dict

## 🚦 Roadmap

- [ ] Add support for more embedding providers (OpenAI, Cohere)
- [ ] Implement hybrid search (keyword + semantic)
- [ ] Add document update/delete capabilities
- [ ] Support for incremental indexing
- [ ] Multi-modal embeddings (text + code + tables)
- [ ] Query expansion and rewriting
- [ ] Relevance feedback mechanisms

## 📄 License

This project is part of the python-template-generator toolkit.

## 🙏 Acknowledgments

Built with:
- [sentence-transformers](https://www.sbert.net/) for embeddings
- [FAISS](https://github.com/facebookresearch/faiss) for vector search
- [tiktoken](https://github.com/openai/tiktoken) for token counting
- [markdown-it-py](https://github.com/executablebooks/markdown-it-py) for parsing

---

For more details, see the [ENRICHED_EXTENSION_PLAN.md](ENRICHED_EXTENSION_PLAN.md) for the complete development history and technical decisions.