#!/usr/bin/env python3
"""Test the token counter for infinite loop issue."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from chunker.token_counter import TokenCounter

def test_split_at_token_limit():
    """Test the split_at_token_limit method for infinite loops."""
    
    counter = TokenCounter()
    
    # Test normal case
    print("Test 1: Normal case (max=50, overlap=10)")
    text = "This is a test sentence. " * 20
    try:
        pieces = counter.split_at_token_limit(text, 50, 10)
        print(f"  ✓ Success: {len(pieces)} pieces")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Test edge case: overlap >= max_tokens
    print("\nTest 2: Edge case (max=50, overlap=50)")
    try:
        pieces = counter.split_at_token_limit(text, 50, 50)
        print(f"  ✓ Success: {len(pieces)} pieces")
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Test edge case: overlap > max_tokens
    print("\nTest 3: Bad case (max=50, overlap=60)")
    try:
        pieces = counter.split_at_token_limit(text, 50, 60)
        print(f"  ✓ Success: {len(pieces)} pieces")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

if __name__ == "__main__":
    test_split_at_token_limit()