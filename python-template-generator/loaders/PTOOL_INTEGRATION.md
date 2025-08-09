# PTOOL Integration in Loaders Module

## Overview

The loaders module has been refactored to use PTOOL (Project Paths Tool) for type-safe, validated path management. This enables running scripts and tests from any directory while maintaining clean, maintainable code.

## Features

### 🚀 Auto-Discovery
- Scripts and tests work from ANY directory in the project
- No need to remember specific working directories
- Automatic project root detection

### 🔒 Type-Safe Paths
- All paths are validated at startup
- IDE autocomplete for path attributes
- No more runtime path errors

### 🧪 Better Testing
- Tests run from any location
- Clean fixture management
- No sys.path hacks needed

### 📦 Clean Imports
- Consistent import patterns
- No relative path confusion
- Works with modern Python packaging

## Configuration

The PTOOL configuration is in `pyproject.toml`:

```toml
[tool.project_paths.paths]
base_dir = "."
loaders_dir = "python-template-generator/loaders"
loaders_tests = "python-template-generator/loaders/tests"
loaders_enrichers = "python-template-generator/loaders/enrichers"
# ... more paths
```

## Usage Examples

### In Scripts

```python
from project_paths import create_project_paths_auto

# Auto-discover project root and create paths
paths = create_project_paths_auto()

# Access typed paths
docs_dir = paths.loaders_docs
test_fixtures = paths.loaders_test_fixtures
enrichers = paths.loaders_enrichers
```

### In Tests

```python
# tests/conftest.py
from project_paths import create_project_paths_auto

paths = create_project_paths_auto()

@pytest.fixture
def test_data_dir():
    """Provide test data directory."""
    return paths.loaders_test_fixtures
```

### With Loaders Module

```python
from python_template_generator.loaders.paths import get_paths

# Get paths with enricher validation
paths = get_paths("development")
```

## Available Paths

All paths are available as attributes on the paths object:

### Core Modules
- `loaders_dir` - Main loaders directory
- `loaders_core` - Core module
- `loaders_enrichers` - Enrichers module
- `loaders_validators` - Validators module
- `loaders_utils` - Utilities module

### Sub-modules
- `loaders_chunker` - Text chunking module
- `loaders_embeddings` - Embedding providers
- `loaders_vector_store` - Vector storage

### Testing
- `loaders_tests` - Main test directory
- `loaders_test_fixtures` - Test fixtures
- `loaders_test_integration` - Integration tests
- `loaders_test_unit` - Unit tests

### Documentation
- `loaders_docs` - Documentation root
- `loaders_docs_adr` - Architecture Decision Records
- `loaders_docs_architecture` - Architecture docs

### Output
- `loaders_test_results` - Test results
- `loaders_test_artifacts` - Test artifacts
- `loaders_htmlcov` - Coverage reports

## Migration Guide

### Before (Fragile)

```python
# Old way - breaks if run from wrong directory
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
test_data = Path(__file__).parent / "fixtures"
```

### After (Robust)

```python
# New way - works from anywhere
from project_paths import create_project_paths_auto

paths = create_project_paths_auto()
sys.path.insert(0, str(paths.loaders_dir))
test_data = paths.loaders_test_fixtures
```

## Tools & Scripts

### Demo Script
```bash
# Run from anywhere in the project
uv run python python-template-generator/loaders/scripts/demo_ptool_usage.py
```

### Migration Helper
```bash
# Identify files that need updating
uv run python python-template-generator/loaders/scripts/migrate_to_ptool.py
```

## Benefits

1. **Developer Experience**
   - Run scripts from any directory
   - No working directory confusion
   - Clean, readable code

2. **Reliability**
   - Paths validated at startup
   - Type-safe with IDE support
   - No runtime path errors

3. **Maintainability**
   - Single source of truth for paths
   - Easy to reorganize structure
   - Clear dependencies

4. **Testing**
   - Tests work from any location
   - Consistent fixture paths
   - Simplified CI/CD setup

## Integration with Enrichers

The loaders module also integrates enrichers as PTOOL validators:

```python
from python_template_generator.loaders.paths import MarkdownEnricherValidator

# Create validator that checks markdown files
validator = MarkdownEnricherValidator(strict=False)

# Use with PTOOL
from project_paths import create_project_paths_auto
paths = create_project_paths_auto(validator=validator)
```

This provides:
- Automatic markdown validation
- Link checking
- Structure validation
- Content verification

## Troubleshooting

### "No pyproject.toml found"
- Ensure you're running from within the project directory tree
- Check that pyproject.toml has `[tool.project_paths]` section

### Import errors
- Use `create_project_paths_auto()` for automatic discovery
- Add `paths.loaders_dir` to sys.path if needed

### Path not found
- Check the path is configured in pyproject.toml
- Verify the directory/file actually exists
- Use `paths.<tab>` for autocomplete to see available paths

## Next Steps

1. Complete migration of remaining files
2. Remove all `Path(__file__).parent` patterns
3. Update CI/CD to leverage PTOOL
4. Add more validators for different file types
5. Create project-wide PTOOL adoption

## Summary

The loaders module now showcases modern PTOOL usage with:
- ✅ Type-safe path management
- ✅ Auto-discovery from any directory
- ✅ Enricher-based validation
- ✅ Clean, maintainable code
- ✅ Excellent developer experience

This refactoring makes the loaders module more robust, maintainable, and pleasant to work with!