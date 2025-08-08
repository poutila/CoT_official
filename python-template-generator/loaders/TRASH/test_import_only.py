#!/usr/bin/env python3
"""Test just the imports to find where it hangs."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports one by one...")

print("\n1. Import ChunkingConfig...")
try:
    from chunker.models import ChunkingConfig
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

print("\n2. Import TokenCounter...")
try:
    from chunker.token_counter import TokenCounter
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

print("\n3. Import BaseChunker...")
try:
    from chunker.base_chunker import BaseChunker
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

print("\n4. Import SemanticChunker...")
try:
    from chunker.semantic_chunker import SemanticChunker
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

print("\n✅ All imports successful!")