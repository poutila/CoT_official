#!/usr/bin/env python3
"""Minimal test to reproduce chunker timeout issue."""

import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from chunker import SemanticChunker, ChunkingConfig

def test_with_increasing_sizes():
    """Test chunker with increasing text sizes to find the breaking point."""
    
    # Create chunker with small config to speed up testing
    config = ChunkingConfig(
        max_tokens=100,
        overlap_tokens=10,  # Small overlap
        preserve_code_blocks=True
    )
    chunker = SemanticChunker(config)
    
    # Test with increasing sizes
    sizes = [100, 500, 1000, 2000, 5000]
    
    for size in sizes:
        # Create test text
        test_text = "This is a test sentence. " * size
        
        print(f"\nTesting with {size} repetitions ({len(test_text)} chars)...")
        
        start_time = time.time()
        try:
            chunks = chunker.chunk_text(test_text, source_file=f"test_{size}.txt")
            elapsed = time.time() - start_time
            
            print(f"  ✓ Success: {len(chunks)} chunks in {elapsed:.2f} seconds")
            
            # If it takes more than 5 seconds, that's concerning
            if elapsed > 5:
                print(f"  ⚠️ Warning: Chunking is slow at this size!")
                break
                
        except KeyboardInterrupt:
            print(f"  ✗ Interrupted after {time.time() - start_time:.2f} seconds")
            break
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            break

def test_with_real_file():
    """Test with a real markdown file."""
    
    config = ChunkingConfig(
        max_tokens=512,
        overlap_tokens=50,
        preserve_code_blocks=True
    )
    chunker = SemanticChunker(config)
    
    # Try with a smaller file first
    test_file = Path("ENCODING_ERROR_PREVENTION.md")
    
    if test_file.exists():
        print(f"\nTesting with {test_file} ({test_file.stat().st_size} bytes)...")
        
        text = test_file.read_text(encoding='utf-8')
        
        start_time = time.time()
        try:
            chunks = chunker.chunk_text(text, source_file=str(test_file))
            elapsed = time.time() - start_time
            
            print(f"  ✓ Success: {len(chunks)} chunks in {elapsed:.2f} seconds")
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("CHUNKER PERFORMANCE TEST")
    print("=" * 60)
    
    print("\n1. Testing with synthetic text of increasing sizes...")
    test_with_increasing_sizes()
    
    print("\n2. Testing with real markdown file...")
    test_with_real_file()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("\nIf the test hung at a certain size, the issue is likely:")
    print("  - Inefficient overlap calculation in _add_chunk_relationships")
    print("  - Repeated encoding/decoding of the same text")
    print("  - Missing hashlib import in base_chunker.py")