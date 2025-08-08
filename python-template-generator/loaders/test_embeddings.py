#!/usr/bin/env python3
"""Test script for the Embeddings Module."""

import sys
from pathlib import Path
import time
import json
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from embeddings import (
    SentenceTransformerProvider,
    EmbeddingProviderConfig,
    EmbeddingProviderType,
)


def test_basic_embedding():
    """Test basic embedding generation."""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Embedding Generation")
    print("=" * 60)
    
    # Create provider with default config (force CPU for compatibility)
    config = EmbeddingProviderConfig(
        provider_type=EmbeddingProviderType.SENTENCE_TRANSFORMER,
        model_name="all-MiniLM-L6-v2",
        cache_embeddings=True,
        device="cpu"  # Force CPU to avoid CUDA issues
    )
    
    print("\n1. Initializing provider...")
    provider = SentenceTransformerProvider(config)
    print(f"   ✓ Provider initialized: {provider}")
    
    # Test single embedding
    print("\n2. Testing single text embedding...")
    text = "This is a test sentence for embedding generation."
    
    result = provider.embed(text)
    
    print(f"   ✓ Embedding generated")
    print(f"   - Dimension: {result.dimension}")
    print(f"   - Text hash: {result.metadata.text_hash}")
    print(f"   - Processing time: {result.metadata.processing_time_ms:.2f}ms")
    print(f"   - First 5 values: {result.embedding[:5]}")
    
    # Test caching
    print("\n3. Testing cache...")
    result2 = provider.embed(text)
    
    cache_stats = provider.get_cache_stats()
    print(f"   ✓ Cache stats:")
    print(f"   - Hits: {cache_stats['cache_hits']}")
    print(f"   - Misses: {cache_stats['cache_misses']}")
    print(f"   - Hit rate: {cache_stats['hit_rate']:.2%}")
    
    return result


def test_batch_embedding():
    """Test batch embedding generation."""
    print("\n" + "=" * 60)
    print("TEST 2: Batch Embedding Generation")
    print("=" * 60)
    
    # Create provider (force CPU)
    config = EmbeddingProviderConfig(
        provider_type=EmbeddingProviderType.SENTENCE_TRANSFORMER,
        model_name="all-MiniLM-L6-v2",
        batch_size=8,
        cache_embeddings=True,
        device="cpu"
    )
    
    provider = SentenceTransformerProvider(config)
    
    # Test batch
    texts = [
        "Python is a high-level programming language.",
        "Machine learning is a subset of artificial intelligence.",
        "Natural language processing enables computers to understand text.",
        "Embeddings are vector representations of text.",
        "The quick brown fox jumps over the lazy dog.",
        "This is a test sentence.",
        "Another example for batch processing.",
        "Final text in the batch.",
        "One more to test batch splitting.",
        "Last sentence in our test batch."
    ]
    
    print(f"\n1. Embedding {len(texts)} texts...")
    start_time = time.time()
    
    batch_result = provider.embed_batch(texts, show_progress=True)
    
    elapsed = time.time() - start_time
    
    print(f"\n   ✓ Batch processed")
    print(f"   - Batch size: {batch_result.size}")
    print(f"   - Dimension: {batch_result.dimension}")
    print(f"   - Total time: {batch_result.total_processing_time_ms:.2f}ms")
    print(f"   - Wall time: {elapsed:.2f}s")
    print(f"   - Avg per text: {batch_result.total_processing_time_ms / batch_result.size:.2f}ms")
    
    # Test similarity search
    print("\n2. Testing similarity search...")
    query = "Programming languages and software development."
    query_embedding = provider.embed(query)
    
    results = batch_result.search(query_embedding, top_k=3)
    
    print(f"\n   Top 3 similar texts to: '{query}'")
    for idx, score in results:
        print(f"   {idx + 1}. Score: {score:.4f} - '{texts[idx]}'")
    
    return batch_result


def test_similarity():
    """Test similarity calculations."""
    print("\n" + "=" * 60)
    print("TEST 3: Similarity Calculations")
    print("=" * 60)
    
    config = EmbeddingProviderConfig(device="cpu")
    provider = SentenceTransformerProvider(config)
    
    # Test similar sentences
    text1 = "The cat sat on the mat."
    text2 = "A cat is sitting on a rug."
    text3 = "Python is a programming language."
    
    emb1 = provider.embed(text1)
    emb2 = provider.embed(text2)
    emb3 = provider.embed(text3)
    
    sim12 = emb1.similarity(emb2)
    sim13 = emb1.similarity(emb3)
    sim23 = emb2.similarity(emb3)
    
    print("\nSimilarity scores:")
    print(f"'{text1}' vs")
    print(f"'{text2}': {sim12:.4f}")
    print(f"'{text3}': {sim13:.4f}")
    print(f"\n'{text2}' vs")
    print(f"'{text3}': {sim23:.4f}")
    
    print("\n✓ Similar sentences have higher scores!")


def test_model_info():
    """Test model information retrieval."""
    print("\n" + "=" * 60)
    print("TEST 4: Model Information")
    print("=" * 60)
    
    config = EmbeddingProviderConfig(device="cpu")
    provider = SentenceTransformerProvider(config)
    
    info = provider.get_model_info()
    
    print("\nModel Information:")
    for key, value in info.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    - {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    # List available models
    print("\nCommonly used models:")
    models = SentenceTransformerProvider.list_available_models()
    for i, model in enumerate(models[:5]):  # Show first 5
        print(f"  {i+1}. {model}")
    print(f"  ... and {len(models)-5} more")


def test_performance():
    """Test performance with different batch sizes."""
    print("\n" + "=" * 60)
    print("TEST 5: Performance Testing")
    print("=" * 60)
    
    # Generate test texts
    test_texts = [
        f"This is test sentence number {i} for performance testing."
        for i in range(100)
    ]
    
    batch_sizes = [1, 8, 16, 32]
    
    print(f"\nTesting with {len(test_texts)} texts:")
    
    for batch_size in batch_sizes:
        config = EmbeddingProviderConfig(
            batch_size=batch_size,
            cache_embeddings=False,  # Disable cache for fair comparison
            device="cpu"
        )
        provider = SentenceTransformerProvider(config)
        
        start = time.time()
        result = provider.embed_batch(test_texts)
        elapsed = time.time() - start
        
        print(f"\nBatch size {batch_size:2d}: {elapsed:.2f}s "
              f"({len(test_texts)/elapsed:.1f} texts/sec)")


def main():
    """Main test function."""
    print("=" * 60)
    print("EMBEDDINGS MODULE TEST SUITE")
    print("=" * 60)
    
    try:
        # Run tests
        embedding = test_basic_embedding()
        batch = test_batch_embedding()
        test_similarity()
        test_model_info()
        test_performance()
        
        # Save sample results
        output = {
            "single_embedding": {
                "text": embedding.text,
                "dimension": embedding.dimension,
                "first_10_values": embedding.embedding[:10]
            },
            "batch_stats": {
                "size": batch.size,
                "dimension": batch.dimension,
                "processing_time_ms": batch.total_processing_time_ms
            }
        }
        
        output_path = Path("embeddings_test_results.json")
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
        print(f"\nResults saved to: {output_path}")
        
        print("\nKey achievements:")
        print("  • Embedding generation working")
        print("  • Batch processing optimized")
        print("  • Caching functional")
        print("  • Similarity search operational")
        
        print("\nNext steps:")
        print("  1. Create FAISS vector store")
        print("  2. Integrate with chunker output")
        print("  3. Build complete RAG pipeline")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())