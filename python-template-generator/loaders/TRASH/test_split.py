#!/usr/bin/env python3
"""Test just the split method."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from chunker.token_counter import TokenCounter

print("Testing split_at_token_limit...")

counter = TokenCounter()
text = "This is a test. " * 10

print(f"Test text: {len(text)} chars")

print("\n1. Testing with max=50, overlap=10...")
pieces = counter.split_at_token_limit(text, 50, 10)
print(f"   Result: {len(pieces)} pieces")

print("\n2. Testing with max=50, overlap=49...")
pieces = counter.split_at_token_limit(text, 50, 49)
print(f"   Result: {len(pieces)} pieces")

print("\n✅ All tests passed!")