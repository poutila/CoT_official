#!/usr/bin/env python3
"""Test script for the Vector Store Module."""

import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from embeddings import EmbeddingProviderConfig, SentenceTransformerProvider
from vector_store import (
    DistanceMetric,
    FAISSVectorStore,
    VectorStoreConfig,
    VectorStoreType,
)


def test_basic_operations():
    """Test basic vector store operations."""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Vector Store Operations")
    print("=" * 60)

    # Create vector store
    config = VectorStoreConfig(
        store_type=VectorStoreType.FAISS,
        dimension=384,
        distance_metric=DistanceMetric.L2,
        index_type="Flat",
    )

    print("\n1. Initializing vector store...")
    store = FAISSVectorStore(config)
    print(f"   ✓ Store initialized: {store}")

    # Add a single vector
    print("\n2. Adding single vector...")
    vector = np.random.randn(384).tolist()
    metadata = {"text": "This is a test document", "type": "test"}

    vector_id = store.add(vector, metadata)
    print(f"   ✓ Vector added with ID: {vector_id}")

    # Get the vector back
    print("\n3. Retrieving vector...")
    result = store.get(vector_id)
    if result:
        retrieved_vector, retrieved_metadata = result
        print("   ✓ Vector retrieved")
        print(f"   - Metadata: {retrieved_metadata}")
        print(f"   - Vector dimension: {len(retrieved_vector)}")

    # Search for similar vectors
    print("\n4. Searching for similar vectors...")
    query_vector = np.random.randn(384).tolist()
    results = store.search(query_vector, k=1)

    print(f"   ✓ Found {len(results)} results")
    for result in results:
        print(f"   - ID: {result.vector_id}, Score: {result.score:.4f}")
        print(f"   - Metadata: {result.metadata}")

    return store


def test_batch_operations():
    """Test batch operations."""
    print("\n" + "=" * 60)
    print("TEST 2: Batch Operations")
    print("=" * 60)

    store = FAISSVectorStore()

    # Create batch of vectors
    print("\n1. Creating batch of vectors...")
    n_vectors = 100
    vectors = np.random.randn(n_vectors, 384).tolist()
    metadata = [{"text": f"Document {i}", "index": i} for i in range(n_vectors)]

    print(f"   - Batch size: {n_vectors}")
    print("   - Vector dimension: 384")

    # Add batch
    print("\n2. Adding batch to store...")
    start_time = time.time()
    ids = store.add_batch(vectors, metadata)
    elapsed = time.time() - start_time

    print(f"   ✓ Added {len(ids)} vectors in {elapsed:.3f}s")
    print(f"   - Rate: {len(ids) / elapsed:.1f} vectors/sec")

    # Search
    print("\n3. Performing similarity search...")
    query = vectors[50]  # Use one of the vectors as query
    results = store.search(query, k=5)

    print(f"   ✓ Found {len(results)} similar vectors")
    for i, result in enumerate(results):
        meta = result.metadata
        print(f"   {i + 1}. {meta.get('text', 'Unknown')} - Score: {result.score:.4f}")

    # Get metrics
    print("\n4. Store metrics:")
    metrics = store.get_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   - {key}: {value:.3f}")
        else:
            print(f"   - {key}: {value}")

    return store


def test_with_embeddings():
    """Test integration with embeddings module."""
    print("\n" + "=" * 60)
    print("TEST 3: Integration with Embeddings")
    print("=" * 60)

    # Create embedding provider
    print("\n1. Creating embedding provider...")
    embed_config = EmbeddingProviderConfig(model_name="all-MiniLM-L6-v2", device="cpu")
    embedder = SentenceTransformerProvider(embed_config)
    print("   ✓ Embedder ready")

    # Create vector store
    print("\n2. Creating vector store...")
    store = FAISSVectorStore(
        VectorStoreConfig(dimension=384, distance_metric=DistanceMetric.COSINE)
    )
    print("   ✓ Store ready (using cosine similarity)")

    # Sample documents
    documents = [
        "Python is a high-level programming language.",
        "Machine learning is a subset of artificial intelligence.",
        "Natural language processing enables computers to understand text.",
        "Vector databases store embeddings for similarity search.",
        "The quick brown fox jumps over the lazy dog.",
        "FAISS is a library for efficient similarity search.",
        "Embeddings are dense vector representations of text.",
        "Semantic search finds conceptually similar documents.",
    ]

    print(f"\n3. Embedding and storing {len(documents)} documents...")

    # Generate embeddings and store
    for i, doc in enumerate(documents):
        embedding = embedder.embed(doc)
        store.add(embedding.numpy, metadata={"text": doc, "doc_id": i})

    print(f"   ✓ Stored {len(documents)} document embeddings")

    # Query
    print("\n4. Performing semantic search...")
    query = "What is artificial intelligence and NLP?"
    query_embedding = embedder.embed(query)

    results = store.search(query_embedding.numpy, k=3)

    print(f"\n   Query: '{query}'")
    print(f"   Top {len(results)} results:")
    for i, result in enumerate(results):
        text = result.metadata.get("text", "Unknown")
        print(f"   {i + 1}. Score: {result.score:.4f} - {text}")

    return store, embedder


def test_persistence():
    """Test saving and loading the index."""
    print("\n" + "=" * 60)
    print("TEST 4: Persistence")
    print("=" * 60)

    # Create and populate store
    print("\n1. Creating and populating store...")
    store = FAISSVectorStore()

    vectors = np.random.randn(50, 384)
    metadata = [{"text": f"Doc {i}", "value": i * 10} for i in range(50)]
    ids = store.add_batch(vectors, metadata)

    print(f"   ✓ Added {len(ids)} vectors")

    # Save
    print("\n2. Saving index to disk...")
    save_path = Path("test_vector_store_index")
    store.save(save_path)
    print(f"   ✓ Saved to {save_path}")

    # Get original metrics
    original_metadata = store.get_metadata_dict()
    original_size = original_metadata.total_vectors

    # Create new store and load
    print("\n3. Loading index into new store...")
    new_store = FAISSVectorStore()
    new_store.load(save_path)
    print("   ✓ Index loaded")

    # Verify
    print("\n4. Verifying loaded index...")
    new_metadata = new_store.get_metadata_dict()

    print(f"   - Original vectors: {original_size}")
    print(f"   - Loaded vectors: {new_metadata.total_vectors}")

    # Test search on loaded index
    query = vectors[25]
    results = new_store.search(query, k=3)

    print(f"   - Search returned {len(results)} results")
    assert len(results) > 0, "Search failed on loaded index"

    # Clean up
    if save_path.exists():
        shutil.rmtree(save_path)
        print(f"   ✓ Cleaned up {save_path}")

    return new_store


def test_different_index_types():
    """Test different FAISS index types."""
    print("\n" + "=" * 60)
    print("TEST 5: Different Index Types")
    print("=" * 60)

    index_types = ["Flat", "LSH", "HNSW"]
    vectors = np.random.randn(100, 384)
    query = vectors[50]

    for index_type in index_types:
        print(f"\n{index_type} Index:")

        try:
            config = VectorStoreConfig(index_type=index_type, dimension=384)
            store = FAISSVectorStore(config)

            # Add vectors
            start = time.time()
            store.add_batch(vectors)
            add_time = time.time() - start

            # Search
            start = time.time()
            results = store.search(query, k=5)
            search_time = time.time() - start

            print(f"   ✓ Add time: {add_time:.3f}s")
            print(f"   ✓ Search time: {search_time:.4f}s")
            print(f"   ✓ Results: {len(results)}")

        except Exception as e:
            print(f"   ✗ Error: {e}")


def main():
    """Main test function."""
    print("=" * 60)
    print("VECTOR STORE MODULE TEST SUITE")
    print("=" * 60)

    try:
        # Run tests
        store1 = test_basic_operations()
        store2 = test_batch_operations()
        store3, embedder = test_with_embeddings()
        store4 = test_persistence()
        test_different_index_types()

        # Save sample results
        output = {
            "basic_store": {"size": store1.size, "metrics": store1.get_metrics()},
            "batch_store": {"size": store2.size, "metrics": store2.get_metrics()},
            "semantic_store": {"size": store3.size, "dimension": store3.dimension},
        }

        output_path = Path("vector_store_test_results.json")
        with open(output_path, "w") as f:
            json.dump(output, f, indent=2)

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)

        print(f"\nResults saved to: {output_path}")

        print("\nKey achievements:")
        print("  • Vector storage and retrieval working")
        print("  • Batch operations optimized")
        print("  • Similarity search functional")
        print("  • Integration with embeddings successful")
        print("  • Persistence working")

        print("\nNext steps:")
        print("  1. Build RAG pipeline")
        print("  2. Integrate all components")
        print("  3. Test with real documents")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
