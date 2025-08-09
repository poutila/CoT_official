---
name: "PTOOL Integration Standard for Context Engineering"
description: "Establishes PTOOL (Project Paths Tool) as the standard for all path management in context engineering projects"
version: "1.0.0"
status: "APPROVED"
last_updated: "2025-08-09"
package_name: "path-tool"
installation: "uv add path-tool --editable"
---

## Purpose

**GOAL**: Establish PTOOL as the mandatory standard for all path management in context engineering projects, ensuring type-safe, validated, and maintainable path handling across all templates and generated code.

**VISION**: Every context engineering project should leverage PTOOL to:
- Eliminate hardcoded paths and path-related bugs
- Enable running scripts and tests from any directory
- Provide type-safe path access with IDE support
- Validate all paths at startup
- Support custom validators for domain-specific needs

## Core Principles

1. **No Hardcoded Paths**: All paths must be defined in `pyproject.toml`
2. **Type Safety**: Full IDE support with autocomplete for paths
3. **Validation First**: All paths validated at startup
4. **Auto-Discovery**: Scripts work from any directory in the project
5. **Custom Validators**: Support for domain-specific path validation
6. **Single Source of Truth**: All paths configured in one place

## Standard Implementation Pattern

### 1. Project Configuration (pyproject.toml)

Every project MUST include PTOOL configuration:

```toml
[tool.project_paths.paths]
# Base directories
base_dir = "."
src_dir = "src"
tests_dir = "tests"
docs_dir = "docs"

# Module-specific paths
module_core = "src/core"
module_utils = "src/utils"
module_validators = "src/validators"

# Test paths
test_fixtures = "tests/fixtures"
test_integration = "tests/integration"
test_unit = "tests/unit"

# Output paths
coverage_dir = "htmlcov"
build_dir = "build"
dist_dir = "dist"

[tool.project_paths.files]
# Important files
readme = "README.md"
changelog = "CHANGELOG.md"
license = "LICENSE"

[tool.uv.sources]
path-tool = { path = "../path-tool", editable = true }
```

### 2. Standard Import Pattern

All Python files should use this import pattern:

```python
# Use PTOOL for path management
from project_paths import create_project_paths_auto

# Get paths using auto-discovery
paths = create_project_paths_auto()

# Add source directory to path if needed
import sys
if hasattr(paths, 'src_dir'):
    sys.path.insert(0, str(paths.src_dir))
```

### 3. Test Configuration (conftest.py)

Standard pytest configuration with PTOOL:

```python
"""Pytest configuration using PTOOL for path management."""

import sys
from pathlib import Path
import pytest

# Use PTOOL for path management
from project_paths import create_project_paths_auto

# Get paths using auto-discovery
paths = create_project_paths_auto()

# Add source directory to path for imports
if hasattr(paths, 'src_dir'):
    sys.path.insert(0, str(paths.src_dir))


@pytest.fixture
def project_paths():
    """Provide PTOOL paths to tests."""
    return paths


@pytest.fixture
def test_data_dir() -> Path:
    """Path to test data directory using PTOOL."""
    if hasattr(paths, 'test_fixtures'):
        return Path(paths.test_fixtures)
    # Fallback if not configured
    return Path(__file__).parent / "fixtures"
```

### 4. Custom Validators

For domain-specific validation (e.g., markdown files):

```python
from project_paths import BasePathValidator, create_project_paths

class MarkdownValidator(BasePathValidator):
    """Validator for markdown files."""
    
    def validate_paths(self, paths_instance):
        """Validate markdown-specific paths."""
        docs_dir = getattr(paths_instance, 'docs_dir', None)
        if docs_dir and Path(docs_dir).exists():
            md_files = list(Path(docs_dir).glob('**/*.md'))
            if not md_files:
                self.logger.warning(f"No markdown files found in {docs_dir}")
            else:
                # Validate markdown structure
                for md_file in md_files:
                    self._validate_markdown_file(md_file)
    
    def _validate_markdown_file(self, file_path: Path):
        """Validate individual markdown file."""
        content = file_path.read_text()
        if not content.strip():
            self.logger.warning(f"Empty markdown file: {file_path}")

# Use with custom validator
validator = MarkdownValidator()
paths = create_project_paths_auto(validator=validator)
```

## Migration Guide

### Step 1: Install PTOOL

```bash
# For development (editable install)
uv add ../path-tool --editable

# Or from PyPI (when available)
uv add path-tool
```

### Step 2: Configure Paths

Add `[tool.project_paths]` section to `pyproject.toml`:

```toml
[tool.project_paths.paths]
base_dir = "."
# Add all your project paths here
```

### Step 3: Update Imports

Replace hardcoded paths:

```python
# ❌ OLD (fragile)
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
data_dir = Path(__file__).parent / "data"

# ✅ NEW (robust)
from project_paths import create_project_paths_auto
paths = create_project_paths_auto()
sys.path.insert(0, str(paths.src_dir))
data_dir = paths.test_fixtures
```

### Step 4: Run Migration Script

Create and run a migration script to identify files needing updates:

```python
#!/usr/bin/env python3
"""Identify files that need PTOOL migration."""

import re
from pathlib import Path
from project_paths import create_project_paths_auto

def find_files_to_migrate(directory: Path):
    """Find Python files using old path patterns."""
    patterns = [
        r'Path\(__file__\)',
        r'\.parent',
        r'sys\.path\.',
        r'os\.path\.',
    ]
    
    files_to_migrate = []
    for py_file in directory.glob('**/*.py'):
        content = py_file.read_text()
        for pattern in patterns:
            if re.search(pattern, content):
                files_to_migrate.append(py_file)
                break
    
    return files_to_migrate

# Run migration check
paths = create_project_paths_auto()
files = find_files_to_migrate(Path(paths.base_dir))
print(f"Found {len(files)} files to migrate")
```

## Benefits

### For Developers
- **Run from anywhere**: No more "must run from project root"
- **IDE support**: Full autocomplete for paths
- **Less debugging**: Path errors caught at startup
- **Clean code**: No path manipulation logic

### For CI/CD
- **Simplified setup**: No working directory confusion
- **Consistent paths**: Same paths in all environments
- **Validation**: Paths checked before tests run
- **Portable**: Works across different OS platforms

### For Maintenance
- **Single source of truth**: All paths in pyproject.toml
- **Easy refactoring**: Change paths in one place
- **Clear dependencies**: Explicit path relationships
- **Documentation**: Self-documenting configuration

## Template Integration

All generated templates should include PTOOL configuration:

### Template Structure
```
template-project/
├── pyproject.toml          # With [tool.project_paths] section
├── src/
│   └── __init__.py
├── tests/
│   ├── conftest.py        # With PTOOL fixtures
│   └── fixtures/
└── scripts/
    └── setup_paths.py     # Path setup utility
```

### Generated conftest.py Template
```python
"""Pytest configuration for {{ project_name }}."""

# Standard PTOOL setup
from project_paths import create_project_paths_auto
paths = create_project_paths_auto()

import sys
if hasattr(paths, 'src_dir'):
    sys.path.insert(0, str(paths.src_dir))

# Project-specific configuration below...
```

## Validation Requirements

### Pre-commit Hook
Add PTOOL validation to pre-commit:

```yaml
- repo: local
  hooks:
    - id: validate-paths
      name: Validate PTOOL paths
      entry: python -c "from project_paths import create_project_paths_auto; paths = create_project_paths_auto()"
      language: system
      pass_filenames: false
```

### CI/CD Integration
Include path validation in CI:

```yaml
- name: Validate paths
  run: |
    python -c "
    from project_paths import create_project_paths_auto
    paths = create_project_paths_auto()
    print(f'Validated {len(dir(paths))} paths')
    "
```

## Anti-Patterns to Avoid

### ❌ DON'T: Hardcode Paths
```python
# Bad
config_file = "/home/user/project/config.yaml"
test_data = "./tests/fixtures/data.json"
```

### ❌ DON'T: Use Relative Path Navigation
```python
# Bad
Path(__file__).parent.parent.parent / "data"
"../../../config/settings.py"
```

### ❌ DON'T: Assume Working Directory
```python
# Bad
with open("data/input.txt") as f:  # Assumes CWD
    data = f.read()
```

### ❌ DON'T: Mix Path Systems
```python
# Bad - mixing os.path and pathlib
import os
config = os.path.join(Path(__file__).parent, "config")
```

## Success Metrics

A project successfully implements PTOOL when:
1. ✅ No `Path(__file__)` in codebase (except PTOOL itself)
2. ✅ All paths defined in pyproject.toml
3. ✅ Tests run from any directory
4. ✅ Scripts work from any location
5. ✅ Zero hardcoded paths
6. ✅ Path validation in CI/CD
7. ✅ Custom validators for domain needs

## Example Projects

### Minimal Setup
```toml
[tool.project_paths.paths]
base_dir = "."
src = "src"
tests = "tests"
```

### Full Featured Setup
```toml
[tool.project_paths.paths]
# Directories
base_dir = "."
src_dir = "src"
tests_dir = "tests"
docs_dir = "docs"
scripts_dir = "scripts"
data_dir = "data"

# Sub-modules
core_module = "src/core"
utils_module = "src/utils"
api_module = "src/api"

# Test organization
unit_tests = "tests/unit"
integration_tests = "tests/integration"
test_fixtures = "tests/fixtures"

# Output
build_dir = "build"
dist_dir = "dist"
coverage_html = "htmlcov"

[tool.project_paths.files]
readme = "README.md"
changelog = "CHANGELOG.md"
license = "LICENSE"
requirements = "requirements.txt"
```

## Enforcement

### Required for All:
1. New projects MUST use PTOOL from inception
2. Existing projects MUST migrate when refactored
3. Templates MUST include PTOOL configuration
4. PRPs MUST specify PTOOL usage

### Review Checklist:
- [ ] pyproject.toml has [tool.project_paths] section
- [ ] No hardcoded paths in code
- [ ] Tests use PTOOL fixtures
- [ ] Scripts use auto-discovery
- [ ] CI validates paths

## Summary

PTOOL is now the standard for all path management in context engineering projects. This ensures:
- **Consistency**: Same pattern across all projects
- **Reliability**: Validated paths prevent runtime errors
- **Maintainability**: Single source of truth for paths
- **Developer Experience**: Work from any directory
- **Type Safety**: Full IDE support

By adopting PTOOL as a standard, we eliminate an entire class of path-related bugs and make our projects more robust and maintainable.