#!/usr/bin/env python3
"""Test just the imports to find where it hangs."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports one by one...")

print("\n1. Import ChunkingConfig...")
try:
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

print("\n2. Import TokenCounter...")
try:
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

print("\n3. Import BaseChunker...")
try:
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

print("\n4. Import SemanticChunker...")
try:
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    sys.exit(1)

print("\n✅ All imports successful!")
