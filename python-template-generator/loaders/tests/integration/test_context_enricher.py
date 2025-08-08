#!/usr/bin/env python3
"""Test context_fixed_enricher import and usage."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing context_fixed_enricher...")

print("\n1. Import ContextFixedEnricher...")
try:
    from enrichers.context_fixed import ContextFixedEnricher

    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n2. Create enricher with small test file...")
try:
    # Create a tiny test file
    test_file = Path("test_tiny.md")
    test_file.write_text("# Test\nHello world")

    enricher = ContextFixedEnricher(test_file)
    print("   ✓ Enricher created")

    # Clean up
    test_file.unlink()

except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n3. Test extract_rich_doc...")
try:
    # Create test file again
    test_file = Path("test_tiny.md")
    test_file.write_text("# Test\nHello world")

    enricher = ContextFixedEnricher(test_file)
    doc = enricher.extract_rich_doc()
    print(f"   ✓ Document extracted: {len(doc.sections)} sections")

    # Clean up
    test_file.unlink()

except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n✅ ContextFixedEnricher works!")
