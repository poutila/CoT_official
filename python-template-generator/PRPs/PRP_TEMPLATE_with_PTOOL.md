---
name: "PROJECT_NAME - Context Engineering Specification"
description: "Brief description of what this project/package does"
version: "1.0.0"
status: "DRAFT|APPROVED|IMPLEMENTED"
last_updated: "YYYY-MM-DD"
package_name: "package-name"
installation: "uv add package-name"
---

## Purpose

**GOAL**: Clear, specific goal of what this project/package achieves.

**VISION**: The end state when this is successfully implemented.

## Core Principles

1. **Principle 1**: Description
2. **Principle 2**: Description
3. **Path Management**: All paths managed through PTOOL (mandatory)
4. **Type Safety**: Full type hints and validation
5. **Testing**: Minimum 90% test coverage

## Requirements

### Functional Requirements
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] PTOOL integration for all path management

### Non-Functional Requirements
- [ ] Performance targets
- [ ] Security requirements
- [ ] Documentation standards

## Path Management (PTOOL)

### Configuration
All projects MUST include PTOOL configuration in `pyproject.toml`:

```toml
[tool.project_paths.paths]
# Base directories
base_dir = "."
src_dir = "src"
tests_dir = "tests"
docs_dir = "docs"

# Module-specific paths (customize for your project)
module_core = "src/core"
module_utils = "src/utils"

# Test paths
test_fixtures = "tests/fixtures"
test_unit = "tests/unit"
test_integration = "tests/integration"

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

### Usage Pattern
All Python modules MUST use this import pattern:

```python
# Standard PTOOL import
from project_paths import create_project_paths_auto

# Get paths using auto-discovery
paths = create_project_paths_auto()

# Use paths for all file operations
import sys
if hasattr(paths, 'src_dir'):
    sys.path.insert(0, str(paths.src_dir))
```

### Custom Validators (if needed)
```python
from project_paths import BasePathValidator

class CustomValidator(BasePathValidator):
    """Domain-specific path validation."""
    
    def validate_paths(self, paths_instance):
        # Add custom validation logic
        pass

# Use with validator
validator = CustomValidator()
paths = create_project_paths_auto(validator=validator)
```

## Project Structure

```
project-name/
├── pyproject.toml                  # With PTOOL configuration
├── LICENSE
├── README.md
├── CHANGELOG.md
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── core/
│       ├── utils/
│       └── validators/
├── tests/
│   ├── conftest.py                # With PTOOL fixtures
│   ├── fixtures/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── api/
│   └── guides/
├── scripts/
│   └── setup_paths.py            # PTOOL setup utility
└── examples/
    └── basic_usage.py
```

### Test Configuration (conftest.py)
```python
"""Pytest configuration with PTOOL."""

from project_paths import create_project_paths_auto
import pytest
import sys

# Get paths using auto-discovery
paths = create_project_paths_auto()

# Add source to path
if hasattr(paths, 'src_dir'):
    sys.path.insert(0, str(paths.src_dir))

@pytest.fixture
def project_paths():
    """Provide PTOOL paths to tests."""
    return paths

@pytest.fixture
def test_data_dir():
    """Test fixtures directory."""
    if hasattr(paths, 'test_fixtures'):
        return paths.test_fixtures
    return Path(__file__).parent / "fixtures"  # Fallback
```

## Implementation Plan

### Phase 1: Setup (Day 1)
- [ ] Create project structure
- [ ] Configure PTOOL in pyproject.toml
- [ ] Set up test infrastructure with PTOOL
- [ ] Create base validators if needed

### Phase 2: Core Implementation (Days 2-X)
- [ ] Implement core functionality
- [ ] Use PTOOL for all path operations
- [ ] Write comprehensive tests
- [ ] Document API

### Phase 3: Integration (Days X-Y)
- [ ] Create integration examples
- [ ] Test from multiple directories
- [ ] Validate all paths work correctly
- [ ] Performance optimization

### Phase 4: Documentation (Day Y)
- [ ] API documentation
- [ ] Usage guides
- [ ] Migration guide (if applicable)
- [ ] CHANGELOG updates

## Testing Requirements

### Unit Tests
- Minimum 90% coverage
- Use PTOOL fixtures for test data
- Test all path operations

### Integration Tests
- Test from different working directories
- Validate PTOOL auto-discovery
- Test custom validators (if any)

### Path Validation Tests
```python
def test_all_paths_exist():
    """Ensure all configured paths exist."""
    paths = create_project_paths_auto()
    for attr in dir(paths):
        if not attr.startswith('_'):
            path = getattr(paths, attr)
            assert Path(path).exists(), f"Path {attr}={path} does not exist"
```

## Documentation Requirements

### Required Documentation
1. **README.md**: Overview and quick start
2. **API Reference**: Complete API documentation
3. **PTOOL Usage**: How paths are managed
4. **Migration Guide**: For existing projects
5. **Examples**: Working code examples

### Documentation Template
```markdown
# Project Name

## Installation
```bash
uv add package-name
```

## Quick Start
```python
from package_name import MainClass
from project_paths import create_project_paths_auto

# Paths are automatically configured
paths = create_project_paths_auto()

# Use the package
instance = MainClass()
```

## Path Management
This project uses PTOOL for path management. All paths are configured in `pyproject.toml` and validated at startup.
```

## Success Criteria

### Technical Criteria
- [ ] All paths managed through PTOOL
- [ ] No hardcoded paths in code
- [ ] Tests run from any directory
- [ ] 90%+ test coverage
- [ ] All paths validated at startup

### Quality Criteria
- [ ] Clean, maintainable code
- [ ] Comprehensive documentation
- [ ] Working examples
- [ ] CI/CD integration

## Migration Guide (for existing projects)

### Step 1: Install PTOOL
```bash
uv add path-tool --editable
```

### Step 2: Configure paths
Add `[tool.project_paths]` to pyproject.toml

### Step 3: Update imports
Replace all `Path(__file__)` with PTOOL

### Step 4: Run migration check
```python
from project_paths import create_project_paths_auto
paths = create_project_paths_auto()
# Validates all paths
```

## Anti-Patterns to Avoid

### ❌ DON'T: Hardcode paths
```python
# Bad
config = "/home/user/project/config.yaml"
```

### ❌ DON'T: Use Path(__file__)
```python
# Bad
Path(__file__).parent.parent / "data"
```

### ❌ DON'T: Assume working directory
```python
# Bad
with open("config.yaml") as f:
    config = yaml.load(f)
```

### ✅ DO: Use PTOOL
```python
# Good
paths = create_project_paths_auto()
config_path = paths.config_file
with open(config_path) as f:
    config = yaml.load(f)
```

## Validation Checklist

Before marking as complete:
- [ ] PTOOL configuration in pyproject.toml
- [ ] No hardcoded paths in code
- [ ] All tests use PTOOL fixtures
- [ ] Scripts work from any directory
- [ ] Documentation includes PTOOL usage
- [ ] Migration guide if applicable
- [ ] CI/CD validates paths

## Notes

Additional project-specific notes and considerations.

---

*This PRP follows the PTOOL Integration Standard defined in `ptool_integration_standard_PRP.md`*