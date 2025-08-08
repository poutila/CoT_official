# RAG Pipeline API Reference

Complete API documentation for all components of the RAG pipeline system.

## Table of Contents
- [Core Pipeline](#core-pipeline)
- [Models](#models)
- [Chunker Module](#chunker-module)
- [Embeddings Module](#embeddings-module)
- [Vector Store Module](#vector-store-module)
- [Adapters](#adapters)
- [Document Enricher](#document-enricher)

---

## Core Pipeline

### `RAGPipeline`

Main orchestration class for the RAG workflow.

```python
from rag_pipeline import RAGPipeline
from rag_models import RAGConfig

pipeline = RAGPipeline(config: Optional[RAGConfig] = None)
```

#### Methods

##### `index_documents`
```python
def index_documents(
    documents: Optional[List[Document]] = None,
    paths: Optional[Union[Path, List[Path]]] = None
) -> IndexingResult
```
Index documents into the vector store.

**Parameters:**
- `documents`: Pre-loaded Document objects to index
- `paths`: File paths to load and index

**Returns:** `IndexingResult` with statistics

**Example:**
```python
result = pipeline.index_documents(paths=["doc1.md", "doc2.md"])
print(f"Indexed {result.total_chunks} chunks in {result.time_elapsed:.2f}s")
```

##### `retrieve`
```python
def retrieve(
    query: str,
    k: Optional[int] = None,
    filter_metadata: Optional[Dict[str, Any]] = None
) -> RetrievalResult
```
Retrieve relevant documents for a query.

**Parameters:**
- `query`: Search query text
- `k`: Number of results (overrides config)
- `filter_metadata`: Metadata filters

**Returns:** `RetrievalResult` with documents and scores

##### `invoke`
```python
def invoke(inputs: Dict[str, Any], **kwargs) -> Dict[str, Any]
```
LangChain-compatible invocation.

**Parameters:**
- `inputs`: Must contain 'query' or 'question' key
- `**kwargs`: Additional arguments (k, include_answer, etc.)

##### `save` / `load`
```python
def save(path: Union[str, Path]) -> None
def load(path: Union[str, Path]) -> None
```
Persist and restore pipeline state.

---

## Models

### `RAGConfig`

Configuration for the RAG pipeline.

```python
from rag_models import RAGConfig

config = RAGConfig(
    # Chunking
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    
    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2",
    embedding_dimension: int = 384,
    embedding_device: str = "cpu",
    
    # Vector Store
    index_type: str = "Flat",
    distance_metric: str = "cosine",
    persist_directory: Optional[Path] = None,
    
    # Retrieval
    k: int = 4,
    search_type: str = "similarity",
    score_threshold: Optional[float] = None,
    
    # Performance
    cache_embeddings: bool = True,
    verbose: bool = False
)
```

### `Document`

LangChain-compatible document model.

```python
from rag_models import Document

doc = Document(
    page_content: str,
    metadata: Dict[str, Any] = {}
)
```

**Properties:**
- `content`: Alias for page_content
- `to_dict()`: Convert to dictionary

### `IndexingResult`

Result from document indexing.

```python
class IndexingResult:
    total_documents: int
    total_chunks: int
    total_embeddings: int
    time_elapsed: float
    errors: List[str]
    metadata: Dict[str, Any]
```

### `RetrievalResult`

Result from retrieval operation.

```python
class RetrievalResult:
    query: str
    documents: List[Document]
    scores: List[float]
    metadata: Dict[str, Any]
```

**Properties:**
- `context`: Concatenated document content
- `source_documents`: Alias for documents

---

## Chunker Module

### `SemanticChunker`

Intelligently chunks text while preserving semantic boundaries.

```python
from chunker import SemanticChunker, ChunkingConfig

config = ChunkingConfig(
    max_tokens: int = 512,
    overlap_tokens: int = 50,
    respect_sentence_boundaries: bool = True,
    respect_paragraph_boundaries: bool = True,
    preserve_code_blocks: bool = True,
    min_chunk_size: int = 100
)

chunker = SemanticChunker(config)
```

#### Methods

##### `chunk_text`
```python
def chunk_text(
    text: str,
    source_file: str = "unknown"
) -> List[Chunk]
```
Split text into semantic chunks.

### `Chunk`

Single chunk of text with metadata.

```python
class Chunk:
    content: str
    chunk_id: str
    source_file: str
    chunk_type: ChunkType
    token_count: int
    metadata: ChunkMetadata
```

### `TokenCounter`

Token counting utilities using tiktoken.

```python
from chunker.token_counter import TokenCounter

counter = TokenCounter(model="cl100k_base")
tokens = counter.count_tokens(text)
chunks = counter.split_at_token_limit(text, max_tokens=500)
```

---

## Embeddings Module

### `SentenceTransformerProvider`

Generate embeddings using sentence-transformers.

```python
from embeddings import SentenceTransformerProvider, EmbeddingProviderConfig

config = EmbeddingProviderConfig(
    model_name: str = "all-MiniLM-L6-v2",
    device: str = "cpu",
    cache_embeddings: bool = True,
    cache_size: int = 10000,
    batch_size: int = 32,
    show_progress: bool = False
)

provider = SentenceTransformerProvider(config)
```

#### Methods

##### `embed`
```python
def embed(text: str) -> EmbeddingResult
```
Generate embedding for single text.

**Returns:**
```python
class EmbeddingResult:
    embedding: List[float]
    numpy: np.ndarray
    dimension: int
    model: str
    cached: bool
```

##### `embed_batch`
```python
def embed_batch(
    texts: List[str],
    show_progress: bool = False
) -> EmbeddingBatch
```
Generate embeddings for multiple texts.

##### `get_cache_stats`
```python
def get_cache_stats() -> Dict[str, Any]
```
Get cache statistics.

### Supported Models

| Model | Dimensions | Speed | Quality | Use Case |
|-------|------------|-------|---------|----------|
| all-MiniLM-L6-v2 | 384 | Fast | Good | General purpose |
| all-mpnet-base-v2 | 768 | Medium | Excellent | High quality |
| all-MiniLM-L12-v2 | 384 | Medium | Good | Balanced |
| multi-qa-mpnet-base-dot-v1 | 768 | Medium | Excellent | Q&A tasks |
| all-distilroberta-v1 | 768 | Slow | Excellent | Best quality |

---

## Vector Store Module

### `FAISSVectorStore`

FAISS-based vector storage and retrieval.

```python
from vector_store import FAISSVectorStore, VectorStoreConfig, DistanceMetric

config = VectorStoreConfig(
    dimension: int = 384,
    distance_metric: DistanceMetric = DistanceMetric.COSINE,
    index_type: str = "Flat",
    persist_directory: Optional[Path] = None,
    enable_gpu: bool = False
)

store = FAISSVectorStore(config, index_type="Flat")
```

#### Methods

##### `add` / `add_batch`
```python
def add(
    vector: np.ndarray,
    metadata: Optional[Dict[str, Any]] = None
) -> str

def add_batch(
    vectors: List[np.ndarray],
    metadata_list: Optional[List[Dict[str, Any]]] = None
) -> List[str]
```
Add vectors to the store.

##### `search`
```python
def search(
    query_vector: np.ndarray,
    k: int = 5,
    filter_metadata: Optional[Dict[str, Any]] = None,
    include_vectors: bool = False
) -> List[SearchResult]
```
Search for similar vectors.

**Returns:**
```python
class SearchResult:
    id: str
    score: float
    metadata: Dict[str, Any]
    vector: Optional[np.ndarray]
```

##### `save` / `load`
```python
def save(directory: Union[str, Path]) -> None
def load(directory: Union[str, Path]) -> None
```
Persist and restore vector store.

### Index Types

| Type | Description | Speed | Accuracy | Memory |
|------|-------------|-------|----------|---------|
| Flat | Exact search | Slow | Perfect | High |
| IVF | Inverted file | Fast | Good | Medium |
| HNSW | Hierarchical graph | Very Fast | Good | High |
| LSH | Locality-sensitive hashing | Fast | Moderate | Low |

---

## Adapters

### `ChainAdapter`

Make pipeline LangChain-compatible.

```python
from rag_adapters import ChainAdapter

chain = ChainAdapter(pipeline)
result = chain.invoke({"query": "search text"})
```

### `BaseTextSplitterAdapter`

Adapt chunker for LangChain.

```python
from rag_adapters import BaseTextSplitterAdapter

splitter = BaseTextSplitterAdapter(chunker)
chunks = splitter.split_documents(documents)
```

### `BaseEmbeddingsAdapter`

Adapt embeddings for LangChain.

```python
from rag_adapters import BaseEmbeddingsAdapter

embeddings = BaseEmbeddingsAdapter(provider)
vectors = embeddings.embed_documents(texts)
```

### `BaseVectorStoreAdapter`

Adapt vector store for LangChain.

```python
from rag_adapters import BaseVectorStoreAdapter

vectorstore = BaseVectorStoreAdapter(store, embeddings)
docs = vectorstore.similarity_search(query, k=5)
```

---

## Document Enricher

### `ContextFixedEnricher`

Extract rich information from markdown documents.

```python
from context_fixed_enricher import ContextFixedEnricher

enricher = ContextFixedEnricher("document.md")
doc = enricher.extract_rich_doc()
```

### Extracted Information

```python
class MarkdownDocExtendedRich:
    title: str
    sections: List[Section]
    requirements: List[Requirement]
    code_blocks: List[CodeBlock]
    examples: List[CodeExample]
    tables: List[Table]
    links: List[Link]
    lists: List[ListBlock]
    metadata: DocumentMetadata
```

### `Section`
```python
class Section:
    title: str
    level: int
    content: str
    slug: str
    subsections: List[Section]
    code_blocks: List[CodeBlock]
```

### `CodeBlock`
```python
class CodeBlock:
    content: str
    language: str
    section_slug: str
    line_start: Optional[int]
```

### `CodeExample`
```python
class CodeExample:
    code: str
    language: str
    example_type: ExampleType  # GOOD, BAD, NEUTRAL
    context_before: str
    context_after: str
    patterns_found: List[str]
```

---

## Error Handling

All methods may raise:

- `ValueError`: Invalid configuration or input
- `FileNotFoundError`: Missing files or directories
- `RuntimeError`: Processing errors
- `ImportError`: Missing dependencies

Example error handling:

```python
try:
    result = pipeline.index_documents(paths=["missing.md"])
except FileNotFoundError as e:
    print(f"File not found: {e}")
except Exception as e:
    print(f"Indexing failed: {e}")
```

---

## Performance Optimization

### Batching
```python
# Optimal batch sizes
config = RAGConfig(
    chunk_size=512,      # Balance quality and speed
    batch_size=32        # For embedding generation
)
```

### Caching
```python
# Enable all caching
config = RAGConfig(
    cache_embeddings=True,
    cache_size=10000
)

# Check cache stats
stats = pipeline.embeddings.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.2%}")
```

### Index Selection
```python
# For < 10K vectors: use Flat (exact)
config = RAGConfig(index_type="Flat")

# For 10K-100K vectors: use IVF
config = RAGConfig(index_type="IVF")

# For > 100K vectors: use HNSW
config = RAGConfig(index_type="HNSW")
```

---

## Complete Example

```python
from rag_pipeline import RAGPipeline
from rag_models import RAGConfig, Document
from pathlib import Path

# Configure pipeline
config = RAGConfig(
    chunk_size=1000,
    chunk_overlap=100,
    embedding_model="all-mpnet-base-v2",
    index_type="HNSW",
    k=10,
    verbose=True
)

# Initialize
pipeline = RAGPipeline(config)

# Index documents
docs = Path("docs").glob("**/*.md")
result = pipeline.index_documents(paths=list(docs))
print(f"Indexed {result.total_chunks} chunks")

# Save index
pipeline.save("knowledge_base")

# Later: Load and search
pipeline = RAGPipeline(config)
pipeline.load("knowledge_base")

# Search with filtering
results = pipeline.retrieve(
    query="error handling",
    k=5,
    filter_metadata={"category": "security"}
)

# Process results
for doc, score in zip(results.documents, results.scores):
    print(f"[{score:.3f}] {doc.metadata['source']}")
    print(f"{doc.page_content[:200]}...\n")
```

---

For more examples and patterns, see [QUICKSTART.md](QUICKSTART.md) and [README.md](README.md).