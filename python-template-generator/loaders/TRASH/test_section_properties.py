#!/usr/bin/env python3
"""Test section properties to understand the data structure."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from context_fixed_enricher import ContextFixedEnricher

# Create a simple test file
test_file = Path("test_props.md")
test_content = """# Main Title
Main content here.

## Subsection
Sub content here.
"""
test_file.write_text(test_content)

try:
    enricher = ContextFixedEnricher(test_file)
    doc = enricher.extract_rich_doc()
    
    if doc.sections:
        section = doc.sections[0]
        print("Section properties:")
        print(f"  - level: {getattr(section, 'level', 'N/A')}")
        print(f"  - title: {getattr(section, 'title', 'N/A')}")
        print(f"  - content: {getattr(section, 'content', 'N/A')}")
        print(f"  - slug: {getattr(section, 'slug', 'N/A')}")
        
        # Check for text content
        if hasattr(section, 'content'):
            print(f"\nSection content type: {type(section.content)}")
            print(f"Section content: '{section.content}'")
            
finally:
    test_file.unlink()