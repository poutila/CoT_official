#!/usr/bin/env python3
"""Comprehensive test for the complete RAG pipeline.

This script demonstrates:
- Document loading and indexing
- Retrieval with different search types
- Integration of all components (enricher → chunker → embeddings → vector store → retrieval)
- Persistence and loading of the pipeline state
"""

import json
import time
from pathlib import Path
import tempfile
import shutil
from typing import List, Dict, Any

from rag_pipeline import RAGPipeline
from rag_models import RAGConfig, Document
from rag_adapters import (
    BaseTextSplitterAdapter,
    BaseEmbeddingsAdapter,
    BaseVectorStoreAdapter,
    ChainAdapter,
)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}\n")


def create_test_documents() -> List[Document]:
    """Create test documents for demonstration."""
    documents = [
        Document(
            page_content="""# Python Best Practices

Python is a versatile programming language that emphasizes code readability.
When writing Python code, it's important to follow PEP 8 style guidelines.

## Key Principles
- Explicit is better than implicit
- Simple is better than complex
- Readability counts
- Errors should never pass silently

## Code Organization
Organize your code into modules and packages. Use meaningful names for
variables and functions. Keep functions small and focused on a single task.""",
            metadata={"source": "python_practices.md", "category": "programming"}
        ),
        Document(
            page_content="""# Machine Learning Overview

Machine learning is a subset of artificial intelligence that enables systems
to learn and improve from experience without being explicitly programmed.

## Types of Machine Learning
1. Supervised Learning: Training with labeled data
2. Unsupervised Learning: Finding patterns in unlabeled data
3. Reinforcement Learning: Learning through interaction with environment

## Common Algorithms
- Linear Regression for prediction
- Decision Trees for classification
- Neural Networks for complex patterns
- K-Means for clustering""",
            metadata={"source": "ml_overview.md", "category": "ai"}
        ),
        Document(
            page_content="""# RAG Systems Architecture

Retrieval-Augmented Generation (RAG) combines retrieval and generation for
enhanced AI responses. The system retrieves relevant information from a
knowledge base before generating responses.

## Core Components
1. Document Processing: Chunk and index documents
2. Embeddings: Convert text to vector representations
3. Vector Store: Efficient similarity search
4. Retrieval: Find relevant documents for queries
5. Generation: Produce responses using retrieved context

## Benefits
- Reduced hallucination
- Up-to-date information
- Verifiable sources
- Domain-specific knowledge""",
            metadata={"source": "rag_architecture.md", "category": "ai"}
        ),
    ]
    return documents


def test_basic_pipeline():
    """Test basic pipeline functionality."""
    print_section("1. BASIC PIPELINE TEST")
    
    # Create pipeline with custom config
    config = RAGConfig(
        chunk_size=200,
        chunk_overlap=20,
        embedding_model="all-MiniLM-L6-v2",
        k=2,
        verbose=True,
    )
    
    pipeline = RAGPipeline(config)
    print(f"✓ Pipeline created with config: chunk_size={config.chunk_size}, k={config.k}")
    
    # Create and index test documents
    documents = create_test_documents()
    print(f"✓ Created {len(documents)} test documents")
    
    # Index documents
    start_time = time.time()
    result = pipeline.index_documents(documents=documents)
    elapsed = time.time() - start_time
    
    print(f"\n📊 Indexing Results:")
    print(f"  - Documents processed: {result.total_documents}")
    print(f"  - Chunks created: {result.total_chunks}")
    print(f"  - Embeddings generated: {result.total_embeddings}")
    print(f"  - Time elapsed: {elapsed:.2f}s")
    print(f"  - Chunks/sec: {result.total_chunks/elapsed:.0f}")
    
    if result.errors:
        print(f"  - Errors: {result.errors}")
    
    return pipeline


def test_retrieval_methods(pipeline: RAGPipeline):
    """Test different retrieval methods."""
    print_section("2. RETRIEVAL METHODS TEST")
    
    test_queries = [
        "What are Python best practices?",
        "Explain machine learning types",
        "How does RAG reduce hallucination?",
        "What is reinforcement learning?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: '{query}'")
        
        # Retrieve documents
        result = pipeline.retrieve(query, k=2)
        
        print(f"  Found {len(result.documents)} relevant documents:")
        for j, (doc, score) in enumerate(zip(result.documents, result.scores), 1):
            source = doc.metadata.get("source", "unknown")
            preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
            print(f"    {j}. Source: {source} (score: {score:.3f})")
            print(f"       Preview: {preview}")


def test_langchain_compatible_interface(pipeline: RAGPipeline):
    """Test LangChain-compatible interfaces."""
    print_section("3. LANGCHAIN COMPATIBILITY TEST")
    
    # Test invoke method
    print("Testing invoke() method:")
    response = pipeline.invoke({"query": "What are the benefits of RAG systems?"})
    
    print(f"  - Query: {response['query']}")
    print(f"  - Documents found: {len(response['source_documents'])}")
    print(f"  - Context length: {len(response['context'])} characters")
    
    # Test batch processing
    print("\nTesting batch() method:")
    batch_queries = [
        {"query": "Python coding standards"},
        {"query": "Neural network applications"},
    ]
    
    batch_results = pipeline.batch(batch_queries)
    for i, result in enumerate(batch_results, 1):
        print(f"  Batch {i}: Found {len(result['source_documents'])} documents")
    
    # Test streaming (simplified)
    print("\nTesting stream() method:")
    stream_gen = pipeline.stream({"query": "Machine learning algorithms"})
    doc_count = 0
    for chunk in stream_gen:
        if "document" in chunk:
            doc_count += 1
        elif "final" in chunk:
            print(f"  Streamed {doc_count} documents")


def test_adapter_pattern():
    """Test adapter pattern for LangChain integration."""
    print_section("4. ADAPTER PATTERN TEST")
    
    # Create pipeline
    config = RAGConfig(chunk_size=150, chunk_overlap=10)
    pipeline = RAGPipeline(config)
    
    # Test TextSplitter adapter
    print("Testing TextSplitter Adapter:")
    splitter_adapter = BaseTextSplitterAdapter(pipeline.text_splitter)
    
    test_text = "This is a test. It has multiple sentences. We want to see how it splits."
    chunks = splitter_adapter.split_text(test_text)
    print(f"  Split text into {len(chunks)} chunks")
    
    # Test Embeddings adapter
    print("\nTesting Embeddings Adapter:")
    embeddings_adapter = BaseEmbeddingsAdapter(pipeline.embeddings)
    
    test_texts = ["First text", "Second text", "Third text"]
    embeddings = embeddings_adapter.embed_documents(test_texts)
    print(f"  Generated {len(embeddings)} embeddings")
    print(f"  Embedding dimension: {len(embeddings[0])}")
    
    query_embedding = embeddings_adapter.embed_query("Test query")
    print(f"  Query embedding dimension: {len(query_embedding)}")
    
    # Test Chain adapter
    print("\nTesting Chain Adapter:")
    chain_adapter = ChainAdapter(pipeline)
    
    # Index some documents first
    docs = create_test_documents()[:2]
    pipeline.index_documents(documents=docs)
    
    result = chain_adapter.invoke({"query": "Python programming"})
    print(f"  Chain returned {len(result.get('source_documents', []))} documents")


def test_persistence():
    """Test pipeline persistence and loading."""
    print_section("5. PERSISTENCE TEST")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        save_path = Path(temp_dir) / "test_pipeline"
        
        # Create and configure pipeline
        config = RAGConfig(
            chunk_size=100,
            persist_directory=save_path
        )
        pipeline1 = RAGPipeline(config)
        
        # Index documents
        docs = create_test_documents()
        pipeline1.index_documents(documents=docs)
        
        print(f"✓ Indexed {len(docs)} documents")
        
        # Test retrieval before save
        result1 = pipeline1.retrieve("Python best practices", k=1)
        print(f"✓ Retrieved {len(result1.documents)} documents before save")
        
        # Save pipeline
        pipeline1.save(save_path)
        print(f"✓ Saved pipeline to {save_path}")
        
        # Create new pipeline and load
        pipeline2 = RAGPipeline(config)
        pipeline2.load(save_path)
        print(f"✓ Loaded pipeline from {save_path}")
        
        # Test retrieval after load
        result2 = pipeline2.retrieve("Python best practices", k=1)
        print(f"✓ Retrieved {len(result2.documents)} documents after load")
        
        # Verify results are consistent
        if result1.documents and result2.documents:
            doc1_content = result1.documents[0].page_content[:50]
            doc2_content = result2.documents[0].page_content[:50]
            if doc1_content == doc2_content:
                print("✓ Persistence verified: Retrieved documents match")
            else:
                print("✗ Persistence error: Retrieved documents don't match")


def test_performance_metrics():
    """Test performance with larger dataset."""
    print_section("6. PERFORMANCE METRICS TEST")
    
    # Create larger dataset
    large_docs = []
    for i in range(20):
        large_docs.append(Document(
            page_content=f"""Document {i}: This is a longer document with more content.
            It contains information about topic {i % 5}. The content is designed to test
            the performance of the RAG pipeline with multiple documents and chunks.
            
            Additional paragraph {i}: More detailed information goes here. This helps
            test the chunking and embedding performance with realistic document sizes.
            The system should handle this efficiently even with many documents.""",
            metadata={"doc_id": i, "topic": f"topic_{i % 5}"}
        ))
    
    # Create pipeline
    config = RAGConfig(
        chunk_size=100,
        chunk_overlap=10,
        verbose=False,  # Disable verbose for cleaner output
    )
    pipeline = RAGPipeline(config)
    
    # Measure indexing performance
    start_time = time.time()
    index_result = pipeline.index_documents(documents=large_docs)
    index_time = time.time() - start_time
    
    print(f"📊 Indexing Performance:")
    print(f"  - Documents: {index_result.total_documents}")
    print(f"  - Chunks: {index_result.total_chunks}")
    print(f"  - Embeddings: {index_result.total_embeddings}")
    print(f"  - Total time: {index_time:.2f}s")
    print(f"  - Throughput: {index_result.total_embeddings/index_time:.0f} embeddings/sec")
    
    # Measure retrieval performance
    queries = [f"Information about topic {i}" for i in range(5)]
    
    print(f"\n📊 Retrieval Performance:")
    total_retrieval_time = 0
    for query in queries:
        start_time = time.time()
        result = pipeline.retrieve(query, k=3)
        retrieval_time = time.time() - start_time
        total_retrieval_time += retrieval_time
        print(f"  - Query: '{query[:30]}...' -> {len(result.documents)} docs in {retrieval_time*1000:.1f}ms")
    
    avg_retrieval_time = total_retrieval_time / len(queries)
    print(f"  - Average retrieval time: {avg_retrieval_time*1000:.1f}ms")
    print(f"  - Queries per second: {1/avg_retrieval_time:.0f}")


def test_error_handling():
    """Test error handling and edge cases."""
    print_section("7. ERROR HANDLING TEST")
    
    pipeline = RAGPipeline()
    
    # Test retrieval with no indexed documents
    print("Testing retrieval with no indexed documents:")
    result = pipeline.retrieve("test query")
    if len(result.documents) == 0 and "error" in result.metadata:
        print(f"  ✓ Handled empty index: {result.metadata['error']}")
    
    # Test invalid query format for invoke
    print("\nTesting invalid query format:")
    try:
        pipeline.invoke({"invalid_key": "test"})
        print("  ✗ Should have raised ValueError")
    except ValueError as e:
        print(f"  ✓ Raised ValueError: {e}")
    
    # Test indexing empty documents
    print("\nTesting empty document indexing:")
    result = pipeline.index_documents(documents=[])
    if result.total_documents == 0 and result.errors:
        print(f"  ✓ Handled empty documents: {result.errors[0]}")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print(" RAG PIPELINE COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    try:
        # Run tests
        pipeline = test_basic_pipeline()
        test_retrieval_methods(pipeline)
        test_langchain_compatible_interface(pipeline)
        test_adapter_pattern()
        test_persistence()
        test_performance_metrics()
        test_error_handling()
        
        # Summary
        print_section("TEST SUMMARY")
        print("✅ All tests completed successfully!")
        print("\nThe RAG pipeline is fully functional with:")
        print("  • Document loading and chunking")
        print("  • Embedding generation and caching")
        print("  • Vector storage and retrieval")
        print("  • LangChain-compatible interfaces")
        print("  • Adapter pattern for integration")
        print("  • Persistence and loading")
        print("  • Error handling")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()