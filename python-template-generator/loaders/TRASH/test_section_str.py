#!/usr/bin/env python3
"""Test what happens when we call str() on a section."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from context_fixed_enricher import ContextFixedEnricher

print("Testing section str() conversion...")

# Create a simple test file
test_file = Path("test_section.md")
test_content = """# Section 1
This is section 1 content.

## Section 2
This is section 2 content.
"""
test_file.write_text(test_content)

try:
    print("\n1. Creating enricher...")
    enricher = ContextFixedEnricher(test_file)
    
    print("\n2. Extracting document...")
    doc = enricher.extract_rich_doc()
    
    print(f"\n3. Document has {len(doc.sections)} sections")
    
    print("\n4. Testing str() on each section...")
    for i, section in enumerate(doc.sections):
        print(f"\n   Section {i}:")
        print(f"   - Type: {type(section)}")
        print(f"   - Has __str__: {hasattr(section, '__str__')}")
        
        # Try to convert to string
        try:
            section_str = str(section)
            print(f"   - str() length: {len(section_str)}")
            print(f"   - Preview: {section_str[:100]}..." if len(section_str) > 100 else f"   - Content: {section_str}")
        except Exception as e:
            print(f"   - str() failed: {e}")
            import traceback
            traceback.print_exc()
            
finally:
    # Clean up
    test_file.unlink()

print("\n✅ Test complete!")