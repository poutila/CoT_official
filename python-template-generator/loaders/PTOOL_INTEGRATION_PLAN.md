# 🛠️ PTOOL Integration Plan for Loaders Module

## Overview
Integrate PTOOL (path-tool v0.2.0) into the loaders module to provide centralized, type-safe path management before executing FINALIZING_PLAN.md.

## Benefits of PTOOL Integration
- **Centralized Path Management**: All paths defined in pyproject.toml
- **Type Safety**: Path objects with validation
- **Custom Validators**: Environment-specific path validation
- **No Hardcoded Paths**: All paths come from configuration
- **Better Testing**: Easy path mocking for tests

## Integration Steps

### Step 1: Define Loaders Paths in pyproject.toml ✅
Already configured in `/home/lasse/Documents/CoT_official/pyproject.toml`:
```toml
[tool.project_paths.paths]
loaders_core = "python-template-generator/loaders/core"
loaders_enrichers = "python-template-generator/loaders/enrichers"
loaders_validators = "python-template-generator/loaders/validators"
loaders_utils = "python-template-generator/loaders/utils"
loaders_scripts = "python-template-generator/loaders/scripts"
loaders_chunker = "python-template-generator/loaders/chunker"
loaders_embeddings = "python-template-generator/loaders/embeddings"
loaders_vector_store = "python-template-generator/loaders/vector_store"
loaders_tests = "python-template-generator/loaders/tests"
loaders_docs = "python-template-generator/loaders/docs"
```

### Step 2: Create Loaders-Specific Validators
Create custom validators for the loaders module requirements:

```python
# loaders/validators/path_validators.py
from project_paths import BasePathValidator, ValidationError

class LoadersPathValidator(BasePathValidator):
    """Validator for loaders module paths."""
    
    def validate_paths(self, paths_instance):
        self.clear_messages()
        
        # Check required directories exist
        required_dirs = [
            'loaders_core', 
            'loaders_enrichers',
            'loaders_validators',
            'loaders_chunker',
            'loaders_embeddings',
            'loaders_vector_store'
        ]
        
        for dir_name in required_dirs:
            dir_path = getattr(paths_instance, dir_name)
            if not dir_path.exists():
                if self.strict:
                    self.add_error(f"Required directory {dir_name} does not exist: {dir_path}")
                else:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.add_warning(f"Created missing directory: {dir_name}")
        
        # Check test directory
        if not paths_instance.loaders_tests.exists():
            self.add_warning("Test directory missing - will affect test coverage")

class DevelopmentPathValidator(BasePathValidator):
    """Development environment validator."""
    
    def validate_paths(self, paths_instance):
        self.clear_messages()
        # Lenient validation for development
        self.add_warning("Development mode - creating missing directories")
        for attr_name in dir(paths_instance):
            if attr_name.startswith('loaders_') and not attr_name.startswith('_'):
                path = getattr(paths_instance, attr_name)
                if not path.exists() and attr_name.endswith('_dir'):
                    path.mkdir(parents=True, exist_ok=True)

class ProductionPathValidator(BasePathValidator):
    """Production environment validator."""
    
    def validate_paths(self, paths_instance):
        self.clear_messages()
        # Strict validation for production
        self.strict = True
        
        # All paths must exist
        for attr_name in dir(paths_instance):
            if attr_name.startswith('loaders_'):
                path = getattr(paths_instance, attr_name)
                if not path.exists():
                    self.add_error(f"Missing required path in production: {attr_name}")
```

### Step 3: Create Path Management Module
Create a central path management module for loaders:

```python
# loaders/paths.py
"""Centralized path management for loaders module using PTOOL."""

import os
from pathlib import Path
from typing import Optional

from project_paths import create_project_paths, BasePathValidator
from .validators.path_validators import (
    LoadersPathValidator,
    DevelopmentPathValidator,
    ProductionPathValidator
)

def get_environment() -> str:
    """Get current environment."""
    return os.getenv("ENVIRONMENT", "development")

def create_loaders_paths(validator: Optional[BasePathValidator] = None):
    """Create ProjectPaths with appropriate validator for environment."""
    
    if validator is None:
        env = get_environment()
        if env == "production":
            validator = ProductionPathValidator(strict=True)
        elif env == "development":
            validator = DevelopmentPathValidator(strict=False)
        else:
            validator = LoadersPathValidator(strict=False)
    
    return create_project_paths(validator=validator)

# Singleton instance
ProjectPaths = create_loaders_paths()
paths = ProjectPaths()

# Export commonly used paths
CORE_DIR = paths.loaders_core
ENRICHERS_DIR = paths.loaders_enrichers
VALIDATORS_DIR = paths.loaders_validators
UTILS_DIR = paths.loaders_utils
SCRIPTS_DIR = paths.loaders_scripts
CHUNKER_DIR = paths.loaders_chunker
EMBEDDINGS_DIR = paths.loaders_embeddings
VECTOR_STORE_DIR = paths.loaders_vector_store
TESTS_DIR = paths.loaders_tests
DOCS_DIR = paths.loaders_docs

# Test artifacts paths (dynamic)
TEST_ARTIFACTS_DIR = paths.base_dir / "python-template-generator/loaders/test_artifacts"
TEST_RESULTS_DIR = paths.base_dir / "python-template-generator/loaders/TEST_RUN_RESULTS"
```

### Step 4: Update Existing Code to Use PTOOL
Replace hardcoded paths throughout the loaders module:

#### Before (hardcoded):
```python
# Old approach with hardcoded paths
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHUNKER_DIR = os.path.join(BASE_DIR, "chunker")
```

#### After (PTOOL):
```python
# New approach with PTOOL
from loaders.paths import paths, CHUNKER_DIR

# Or use paths directly
chunk_file = paths.loaders_chunker / "semantic_chunker.py"
```

### Step 5: Update Tests to Use PTOOL
Update test files to use PTOOL for path management:

```python
# tests/conftest.py
import pytest
from pathlib import Path
from project_paths import create_minimal_project_paths

@pytest.fixture
def test_paths(tmp_path):
    """Create test paths using PTOOL."""
    TestPaths = create_minimal_project_paths()
    return TestPaths(
        base_dir=tmp_path,
        loaders_core=tmp_path / "core",
        loaders_tests=tmp_path / "tests"
    )

@pytest.fixture
def mock_paths(monkeypatch, test_paths):
    """Mock the production paths with test paths."""
    import loaders.paths
    monkeypatch.setattr(loaders.paths, 'paths', test_paths)
    return test_paths
```

### Step 6: Create Integration Tests
Test the PTOOL integration:

```python
# tests/test_ptool_integration.py
import pytest
from pathlib import Path
from loaders.paths import paths, create_loaders_paths
from loaders.validators.path_validators import (
    LoadersPathValidator,
    DevelopmentPathValidator,
    ProductionPathValidator
)

def test_paths_are_configured():
    """Test that all required paths are configured."""
    assert paths.loaders_core.is_absolute()
    assert paths.loaders_enrichers.is_absolute()
    assert paths.loaders_validators.is_absolute()

def test_development_validator():
    """Test development validator creates missing directories."""
    validator = DevelopmentPathValidator(strict=False)
    ProjectPaths = create_loaders_paths(validator=validator)
    paths = ProjectPaths()
    
    # Should have warnings but no errors
    assert len(validator.errors) == 0
    
def test_production_validator():
    """Test production validator is strict."""
    validator = ProductionPathValidator(strict=True)
    
    # This might raise ValidationError if dirs don't exist
    try:
        ProjectPaths = create_loaders_paths(validator=validator)
        paths = ProjectPaths()
    except ValidationError as e:
        # Expected in test environment
        assert "Missing required path" in str(e)
```

### Step 7: Migration Checklist

- [ ] Install PTOOL as editable package ✅ (already done)
- [ ] Configure paths in pyproject.toml ✅ (already done)
- [ ] Create path validators for loaders
- [ ] Create central paths.py module
- [ ] Update imports in all modules:
  - [ ] core/
  - [ ] enrichers/
  - [ ] validators/
  - [ ] chunker/
  - [ ] embeddings/
  - [ ] vector_store/
  - [ ] scripts/
  - [ ] tests/
- [ ] Update test fixtures
- [ ] Run all tests to verify
- [ ] Update documentation

## Benefits After Integration

1. **No More Path Errors**: All paths validated at startup
2. **Environment-Specific Behavior**: Different validation for dev/prod
3. **Better Testing**: Easy to mock paths in tests
4. **Type Safety**: IDE autocomplete for all paths
5. **Central Configuration**: All paths in pyproject.toml
6. **Automatic Directory Creation**: In development mode

## Next Steps After PTOOL Integration

Once PTOOL is integrated, proceed with FINALIZING_PLAN.md:
1. Fix failing tests (with proper path management)
2. Implement SemanticEngine
3. Add contradiction detection
4. Increase test coverage
5. Package as standalone module

## Success Criteria

- [ ] All hardcoded paths removed
- [ ] All tests passing with PTOOL paths
- [ ] Path validation working in dev/prod modes
- [ ] Documentation updated
- [ ] No import errors or path resolution issues