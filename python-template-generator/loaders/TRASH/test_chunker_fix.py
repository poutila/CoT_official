#!/usr/bin/env python3
"""Test to identify the exact issue with chunker."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing chunker issue...")

# First, let's try importing and creating the chunker directly
from chunker.models import ChunkingConfig
from chunker.base_chunker import BaseChunker
from chunker.token_counter import TokenCounter

print("\n1. Testing TokenCounter directly...")
try:
    counter = TokenCounter()
    test_text = "Hello world"
    tokens = counter.count(test_text)
    print(f"   ✓ TokenCounter works: '{test_text}' = {tokens} tokens")
except Exception as e:
    print(f"   ✗ TokenCounter failed: {e}")
    import traceback
    traceback.print_exc()

print("\n2. Testing BaseChunker initialization...")
try:
    config = ChunkingConfig(max_tokens=100, overlap_tokens=10)
    
    # BaseChunker is abstract, so we need to check if that's the issue
    from chunker.semantic_chunker import SemanticChunker
    
    chunker = SemanticChunker(config)
    print(f"   ✓ Chunker initialized")
    
    # Check if the token_counter is initialized
    print(f"   - Token counter type: {type(chunker.token_counter)}")
    print(f"   - Config max tokens: {chunker.config.max_tokens}")
    
except Exception as e:
    print(f"   ✗ Chunker init failed: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Testing the actual chunking...")
try:
    # Use a very simple text
    simple_text = "Hello world."
    
    print(f"   Testing with: '{simple_text}'")
    
    # Call chunk_text directly
    chunks = chunker.chunk_text(simple_text, source_file="test.txt")
    
    print(f"   ✓ Chunking succeeded: {len(chunks)} chunks")
    
except Exception as e:
    print(f"   ✗ Chunking failed: {e}")
    import traceback
    traceback.print_exc()

print("\n4. Testing _simple_text_chunking directly...")
try:
    # Try calling the internal method directly
    chunks = chunker._simple_text_chunking("Test text", "test.txt")
    print(f"   ✓ _simple_text_chunking works: {len(chunks)} chunks")
except Exception as e:
    print(f"   ✗ _simple_text_chunking failed: {e}")
    import traceback
    traceback.print_exc()

print("\n5. Testing split_at_token_limit...")
try:
    # Try the token counter's split method directly
    text_pieces = chunker.token_counter.split_at_token_limit(
        "This is a test sentence. " * 10,
        50,  # max tokens
        5    # overlap
    )
    print(f"   ✓ split_at_token_limit works: {len(text_pieces)} pieces")
except Exception as e:
    print(f"   ✗ split_at_token_limit failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Diagnosis complete!")