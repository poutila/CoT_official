# RAG Pipeline Quick Start Guide

Get up and running with the RAG pipeline in 5 minutes!

## 1️⃣ Installation (30 seconds)

```bash
# Install required dependencies
uv add tiktoken sentence-transformers faiss-cpu

# Verify installation
uv run python -c "import faiss, sentence_transformers, tiktoken; print('✅ All dependencies installed')"
```

## 2️⃣ Basic Usage (1 minute)

Create a file `quickstart.py`:

```python
from rag_pipeline import RAGPipeline
from rag_models import Document

# Initialize pipeline with defaults
pipeline = RAGPipeline()

# Create some test documents
docs = [
    Document(
        page_content="Python is a high-level programming language known for its simplicity.",
        metadata={"source": "intro.md", "topic": "python"}
    ),
    Document(
        page_content="Machine learning uses algorithms to learn patterns from data.",
        metadata={"source": "ml.md", "topic": "ai"}
    ),
    Document(
        page_content="RAG combines retrieval with generation for better AI responses.",
        metadata={"source": "rag.md", "topic": "ai"}
    )
]

# Index documents
result = pipeline.index_documents(documents=docs)
print(f"✅ Indexed {result.total_chunks} chunks")

# Search
query = "What is Python?"
results = pipeline.retrieve(query, k=2)

print(f"\n🔍 Query: {query}")
for doc, score in zip(results.documents, results.scores):
    print(f"  Score: {score:.3f} | Source: {doc.metadata['source']}")
    print(f"  Content: {doc.page_content}\n")
```

Run it:
```bash
uv run python quickstart.py
```

## 3️⃣ Index Your Documentation (2 minutes)

```python
from rag_pipeline import RAGPipeline
from pathlib import Path

# Create pipeline
pipeline = RAGPipeline()

# Index all markdown files in a directory
docs_path = Path("../")  # Your docs directory
md_files = list(docs_path.glob("*.md"))

print(f"Found {len(md_files)} markdown files")
result = pipeline.index_documents(paths=md_files)

print(f"✅ Processed {result.total_documents} documents")
print(f"✅ Created {result.total_chunks} chunks")
print(f"✅ Generated {result.total_embeddings} embeddings")

# Save for later use
pipeline.save("my_knowledge_base")
print("✅ Saved to my_knowledge_base/")
```

## 4️⃣ Interactive Search (1 minute)

Create `search.py`:

```python
from rag_pipeline import RAGPipeline

# Load existing index
pipeline = RAGPipeline()
pipeline.load("my_knowledge_base")

print("📚 Knowledge base loaded! Type 'quit' to exit.\n")

while True:
    query = input("🔍 Search: ")
    if query.lower() == 'quit':
        break
    
    results = pipeline.retrieve(query, k=3)
    
    if results.documents:
        print(f"\nFound {len(results.documents)} results:\n")
        for i, (doc, score) in enumerate(zip(results.documents, results.scores), 1):
            print(f"{i}. [{score:.2f}] {doc.metadata.get('source', 'Unknown')}")
            print(f"   {doc.page_content[:150]}...\n")
    else:
        print("No results found.\n")
```

## 5️⃣ Common Patterns

### Pattern 1: Filter by Metadata
```python
# Only search in specific categories
results = pipeline.retrieve(
    "error handling",
    filter_metadata={"category": "security"}
)
```

### Pattern 2: Batch Processing
```python
# Process multiple queries at once
queries = [
    {"query": "authentication"},
    {"query": "database setup"},
    {"query": "API endpoints"}
]
all_results = pipeline.batch(queries)
```

### Pattern 3: Custom Configuration
```python
from rag_models import RAGConfig

# Optimize for accuracy
accurate_config = RAGConfig(
    chunk_size=1000,      # Larger chunks
    chunk_overlap=200,    # More overlap
    embedding_model="all-mpnet-base-v2",  # Better model
    k=10                  # More results
)

# Optimize for speed
fast_config = RAGConfig(
    chunk_size=256,       # Smaller chunks
    chunk_overlap=25,     # Less overlap
    embedding_model="all-MiniLM-L6-v2",  # Faster model
    index_type="HNSW"     # Approximate search
)
```

### Pattern 4: LangChain Integration
```python
from rag_adapters import ChainAdapter

# Make it LangChain compatible
chain = ChainAdapter(pipeline)

# Now use with LangChain patterns
response = chain.invoke({"query": "How to configure?"})
```

## 🎯 Next Steps

1. **Explore Components**: Check individual component examples:
   - `test_chunker.py` - Advanced chunking options
   - `test_embeddings.py` - Embedding models comparison
   - `test_vector_store.py` - Vector store operations

2. **Run Full Test Suite**: 
   ```bash
   uv run python test_rag_pipeline.py
   ```

3. **Read Full Documentation**: See [README.md](README.md) for:
   - Complete API reference
   - Performance optimization tips
   - Troubleshooting guide
   - Advanced configurations

## 💡 Tips

- **Start Small**: Test with a few documents first
- **Monitor Performance**: Use `verbose=True` in config
- **Cache Embeddings**: Saves time on repeated texts
- **Use Persistence**: Save and load to avoid re-indexing
- **Choose Right Model**: Balance quality vs speed for your use case

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Out of memory | Reduce `chunk_size` and batch size |
| Slow indexing | Use `index_type="HNSW"` instead of "Flat" |
| GPU errors | Set `embedding_device="cpu"` in config |
| Poor results | Increase `chunk_overlap` and use better embedding model |
| No results | Lower `score_threshold` or increase `k` |

---

Ready to build? Check out the [full documentation](README.md) for more!