# RAG Pipeline Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RAG Pipeline System                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  📄 Input                 🔄 Processing              📊 Output      │
│                                                                      │
│  Markdown     ──────►  Enricher  ──────►  Enhanced Document         │
│  Documents              ▼                      ▼                    │
│                    Extract Rich              Sections               │
│                    Semantics                 Code Blocks            │
│                         ▼                    Examples               │
│                    Chunker  ──────►  Semantic Chunks                │
│                         ▼                      ▼                    │
│                    Embeddings  ──────►  Vector Representations      │
│                         ▼                      ▼                    │
│                    Vector Store  ──────►  Indexed Knowledge Base    │
│                         ▼                      ▼                    │
│  User Query   ──────►  Retrieval  ──────►  Relevant Documents      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Layer 1: Document Processing
```
┌──────────────────────────────────────────────────────────┐
│                   Document Enricher                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │  Markdown   │  │   Pattern    │  │    Context     │ │
│  │   Parser    │──►   Detector   │──►   Extractor    │ │
│  └─────────────┘  └──────────────┘  └────────────────┘ │
│         │                │                    │         │
│         ▼                ▼                    ▼         │
│  ┌─────────────────────────────────────────────────┐   │
│  │           MarkdownDocExtendedRich               │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ • Sections (hierarchical)                       │   │
│  │ • Code Blocks (with language)                   │   │
│  │ • Examples (classified as good/bad)             │   │
│  │ • Requirements (detected)                       │   │
│  │ • Tables, Lists, Links                          │   │
│  │ • Metadata & Context                            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Layer 2: Chunking System
```
┌──────────────────────────────────────────────────────────┐
│                    Semantic Chunker                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │   Token     │  │  Boundary    │  │    Overlap     │ │
│  │  Counter    │──►  Detector    │──►   Manager      │ │
│  └─────────────┘  └──────────────┘  └────────────────┘ │
│                                                          │
│  Rules:                                                  │
│  • Max tokens: 512 (configurable)                       │
│  • Preserve: Code blocks, sentences, paragraphs         │
│  • Overlap: 50 tokens for context                       │
│  • Output: List[Chunk] with metadata                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Layer 3: Embedding Generation
```
┌──────────────────────────────────────────────────────────┐
│                 Embedding Provider                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │  Sentence   │  │   Batching   │  │    Caching     │ │
│  │ Transformer │──►   Engine     │──►    System      │ │
│  └─────────────┘  └──────────────┘  └────────────────┘ │
│                                                          │
│  Models:                                                 │
│  • all-MiniLM-L6-v2 (384 dims, fast)                   │
│  • all-mpnet-base-v2 (768 dims, quality)               │
│  • Custom models via config                             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Layer 4: Vector Storage
```
┌──────────────────────────────────────────────────────────┐
│                    FAISS Vector Store                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │   Index     │  │   Metadata   │  │  Persistence   │ │
│  │   Manager   │──►   Storage    │──►    Handler     │ │
│  └─────────────┘  └──────────────┘  └────────────────┘ │
│                                                          │
│  Index Types:                                            │
│  • Flat: Exact search (small datasets)                  │
│  • IVF: Inverted file (medium datasets)                 │
│  • HNSW: Graph-based (large datasets)                   │
│  • LSH: Hash-based (memory efficient)                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Layer 5: Retrieval Pipeline
```
┌──────────────────────────────────────────────────────────┐
│                    RAG Pipeline                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│     Query ──► Embedding ──► Search ──► Ranking          │
│                                │                         │
│                                ▼                         │
│                         Vector Store                     │
│                                │                         │
│                                ▼                         │
│                     Retrieved Documents                  │
│                                │                         │
│                                ▼                         │
│                    [Optional: Reranking]                 │
│                                │                         │
│                                ▼                         │
│                         Final Results                    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Indexing Flow
```
Document.md
    │
    ▼
[Enricher] ──► Sections, Code, Examples
    │
    ▼
[Chunker] ──► Semantic Chunks (with overlap)
    │
    ▼
[Embeddings] ──► Vector Representations
    │
    ▼
[Vector Store] ──► Indexed & Persisted
```

### 2. Query Flow
```
User Query
    │
    ▼
[Embed Query] ──► Query Vector
    │
    ▼
[Vector Search] ──► Similar Vectors
    │
    ▼
[Metadata Lookup] ──► Original Content
    │
    ▼
[Ranking] ──► Sorted Results
    │
    ▼
Response with Documents & Scores
```

## Class Hierarchy

```
MarkdownDocEnricher (Original)
    │
    └── ContextFixedEnricher (Enhanced)
            │
            ├── Extracts: Sections, Code, Tables
            ├── Detects: Examples, Requirements
            └── Preserves: Context, Relationships

BaseVectorStore (Abstract)
    │
    └── FAISSVectorStore (Implementation)
            │
            ├── IndexFlatL2
            ├── IndexIVFFlat
            ├── IndexHNSWFlat
            └── IndexLSH

BaseEmbeddingProvider (Abstract)
    │
    └── SentenceTransformerProvider (Implementation)
            │
            ├── Model Loading
            ├── Batch Processing
            └── Caching

BaseChunker (Abstract)
    │
    └── SemanticChunker (Implementation)
            │
            ├── TokenCounter
            ├── BoundaryDetector
            └── OverlapManager
```

## Configuration Flow

```yaml
RAGConfig:
  chunking:
    chunk_size: 512
    overlap: 50
    preserve_boundaries: true
    
  embeddings:
    model: "all-MiniLM-L6-v2"
    device: "cpu"
    cache: true
    
  vector_store:
    type: "FAISS"
    index: "Flat"
    metric: "cosine"
    
  retrieval:
    k: 5
    threshold: 0.7
    rerank: false
```

## LangChain Compatibility Layer

```
Native Components          Adapters                LangChain Interface
─────────────────         ─────────               ─────────────────

SemanticChunker      ──►  TextSplitterAdapter  ──►  TextSplitter
EmbeddingProvider    ──►  EmbeddingsAdapter    ──►  Embeddings
FAISSVectorStore     ──►  VectorStoreAdapter   ──►  VectorStore
RAGPipeline          ──►  ChainAdapter         ──►  Chain
```

## Performance Characteristics

### Bottlenecks & Optimizations

```
Component         Bottleneck           Optimization
─────────         ──────────           ────────────
Enricher          Tree traversal       Cache parsed trees
Chunker           Token counting       Batch processing
Embeddings        Model inference      GPU + Caching
Vector Store      Similarity search    Approximate indices
Pipeline          Multiple passes      Streaming mode
```

### Scaling Considerations

```
Documents    Index Type    Embedding Cache    Query Time
─────────    ──────────    ───────────────    ──────────
< 1K         Flat          Memory (all)       < 10ms
1K-10K       IVF           Memory (LRU)       < 50ms
10K-100K     HNSW          Disk + Memory      < 100ms
> 100K       HNSW/LSH      Disk only          < 200ms
```

## Extension Points

### Custom Enricher
```python
class MyEnricher(ContextFixedEnricher):
    def _extract_custom(self):
        # Add custom extraction logic
        pass
```

### Custom Chunker
```python
class MyChunker(SemanticChunker):
    def _split_logic(self):
        # Custom splitting rules
        pass
```

### Custom Embeddings
```python
class OpenAIProvider(BaseEmbeddingProvider):
    def embed(self, text):
        # Use OpenAI API
        pass
```

### Custom Store
```python
class PineconeStore(BaseVectorStore):
    def search(self, vector, k):
        # Use Pinecone cloud
        pass
```

## Deployment Architecture

### Single Machine
```
Application
    │
    ├── Enricher (CPU)
    ├── Chunker (CPU)
    ├── Embeddings (GPU/CPU)
    └── Vector Store (Memory/Disk)
```

### Distributed
```
Load Balancer
    │
    ├── API Servers (N instances)
    │       │
    │       ├── Enricher
    │       └── Chunker
    │
    ├── Embedding Service (GPU cluster)
    │
    └── Vector Store Service (Dedicated)
            │
            └── FAISS/Pinecone/Weaviate
```

### Microservices
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Enricher   │────►│   Chunker    │────►│  Embeddings  │
│   Service    │     │   Service    │     │   Service    │
└──────────────┘     └──────────────┘     └──────────────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Search     │◄────│ Vector Store │◄────│   Indexer    │
│   Service    │     │   Service    │     │   Service    │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Monitoring Points

```
Metric                    Component         Alert Threshold
──────                    ─────────         ───────────────
Parse Time                Enricher          > 5 seconds
Chunk Size                Chunker           > 1000 tokens
Embedding Latency         Embeddings        > 100ms/text
Index Size                Vector Store      > 80% capacity
Query Latency             Pipeline          > 500ms
Cache Hit Rate            All               < 50%
Memory Usage              All               > 80% available
```

---

For implementation details, see:
- [README.md](README.md) - User guide
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation
- [ENRICHER_DOCUMENTATION.md](ENRICHER_DOCUMENTATION.md) - Enricher details
- [QUICKSTART.md](QUICKSTART.md) - Getting started