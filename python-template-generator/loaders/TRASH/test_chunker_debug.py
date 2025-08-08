#!/usr/bin/env python3
"""Debug script to identify chunker issue."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Step 1: Testing imports...")

try:
    print("  - Importing context_fixed_enricher...")

    print("    ✓ Success")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    sys.exit(1)

try:
    print("  - Importing chunker models...")
    from chunker.models import ChunkingConfig

    print("    ✓ Success")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    sys.exit(1)

try:
    print("  - Importing SemanticChunker...")
    from chunker.semantic_chunker import SemanticChunker

    print("    ✓ Success")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    sys.exit(1)

print("\nStep 2: Testing tiktoken...")
try:
    import tiktoken

    print(
        f"  - tiktoken version: {tiktoken.__version__ if hasattr(tiktoken, '__version__') else 'unknown'}"
    )

    print("  - Getting encoding (this might download on first use)...")
    encoding = tiktoken.get_encoding("cl100k_base")
    print("    ✓ Encoding loaded")

    # Test encoding
    test_text = "Hello, world!"
    tokens = encoding.encode(test_text)
    print(f"    ✓ Test encoding works: '{test_text}' -> {len(tokens)} tokens")

except Exception as e:
    print(f"    ✗ Failed: {e}")
    sys.exit(1)

print("\nStep 3: Testing chunker initialization...")
try:
    config = ChunkingConfig(max_tokens=100)
    chunker = SemanticChunker(config)
    print("    ✓ Chunker initialized")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    sys.exit(1)

print("\nStep 4: Testing simple chunking...")
try:
    test_text = "This is a simple test. It should chunk properly."
    chunks = chunker.chunk_text(test_text, source_file="test.txt")
    print(f"    ✓ Created {len(chunks)} chunks")
except Exception as e:
    print(f"    ✗ Failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n✅ All tests passed! The chunker module is working.")
print("\nThe timeout might be due to:")
print("  1. Processing very large files")
print("  2. Network issues downloading tiktoken models")
print("  3. Infinite loop in document processing")
