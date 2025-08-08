#!/usr/bin/env python3
"""Validate that all imports still work after reorganization."""
import sys
import importlib

modules_to_test = [
    "rag_pipeline",
    "rag_adapters", 
    "rag_models",
    "context_fixed_enricher",
    "enhanced_enricher_with_examples",
    "full_enhanced_enricher",
    "minimal_enhanced_enricher",
    "markdown_validator_enricher",
    "markdown_base_validator",
    "markdown_pydantic_model",
    "sluggify_util",
]

failed = []
for module in modules_to_test:
    try:
        importlib.import_module(module)
        print(f"✓ {module}")
    except ImportError as e:
        print(f"✗ {module}: {e}")
        failed.append(module)

if failed:
    print(f"\n❌ {len(failed)} modules failed to import")
    sys.exit(1)
else:
    print(f"\n✅ All {len(modules_to_test)} modules imported successfully")