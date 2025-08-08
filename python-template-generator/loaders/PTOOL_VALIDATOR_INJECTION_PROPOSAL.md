# PTOOL Validator Injection Proposal

## Executive Summary

This proposal outlines how to enhance PTOOL to support custom validator injection when used as a package, allowing users to define domain-specific validation rules without modifying PTOOL's source code.

## Problem Statement

Currently, PTOOL hardcodes validators through class inheritance:
```python
class ProjectPaths(DynamicModel, ProjectValidatorTemplate):
```

This makes it difficult for users to add custom validation rules when using PTOOL as a package.

## Proposed Solution

Allow users to inject custom validators through a clean API:

```python
# User's validator file
from path_tool import PathValidator

class MyCustomValidator(PathValidator):
    def validate_paths(self, paths_instance):
        # Custom validation logic
        pass

# User's main script
from my_validators import MyCustomValidator
from path_tool import inject_validator, ProjectPaths

# Inject custom validator
inject_validator(MyCustomValidator)
paths = ProjectPaths()  # Will use custom validator
```

## Implementation Approaches

### 1. Global Injection (Simplest)

```python
# In path_tool/__init__.py
_custom_validators = []

def inject_validator(validator):
    """Inject a validator globally."""
    _custom_validators.append(validator)

def create_project_paths():
    """Create ProjectPaths with injected validators."""
    # Apply all validators
    for validator in _custom_validators:
        # ... apply validator
```

**Pros:**
- Simple API
- Backward compatible
- Minimal changes to PTOOL

**Cons:**
- Global state
- All instances use same validators

### 2. Factory Pattern (Recommended)

```python
# In path_tool/factory.py
def create_paths_class(validators=None):
    """Create ProjectPaths class with custom validators."""
    validators = validators or [ProjectValidatorTemplate]
    
    # Build dynamic model with validators
    class ProjectPaths(DynamicModel, *validators):
        # ... implementation
    
    return ProjectPaths

# Usage
ProjectPaths = create_paths_class(validators=[MyValidator])
paths = ProjectPaths()
```

**Pros:**
- No global state
- Different validators per instance
- Clean separation

**Cons:**
- Slightly more complex API

### 3. Builder Pattern (Most Flexible)

```python
# In path_tool/builder.py
class PathsBuilder:
    def __init__(self):
        self.validators = []
    
    def add_validator(self, validator):
        self.validators.append(validator)
        return self
    
    def build(self):
        # Create class with all validators
        return create_paths_class(self.validators)

# Usage
ProjectPaths = (PathsBuilder()
    .add_validator(Validator1)
    .add_validator(Validator2)
    .build())
```

**Pros:**
- Most flexible
- Fluent interface
- Extensible

**Cons:**
- More complex implementation

## Example Use Cases

### 1. Project Structure Validation

```python
class ProjectStructureValidator:
    def validate_paths(self, paths):
        # Ensure project follows expected structure
        required = ['src', 'tests', 'docs']
        for dir_name in required:
            if hasattr(paths, dir_name):
                path = getattr(paths, dir_name)
                if not path.exists():
                    raise ValueError(f"Required directory missing: {dir_name}")
```

### 2. Development vs Production

```python
# Development validator - creates missing directories
class DevelopmentValidator:
    def validate_paths(self, paths):
        for attr_name in dir(paths):
            attr = getattr(paths, attr_name)
            if isinstance(attr, Path) and not attr.exists():
                attr.mkdir(parents=True, exist_ok=True)

# Production validator - strict checks
class ProductionValidator:
    def validate_paths(self, paths):
        # Fail if any path is missing
        for attr_name in dir(paths):
            attr = getattr(paths, attr_name)
            if isinstance(attr, Path) and not attr.exists():
                raise FileNotFoundError(f"Required path missing: {attr}")
```

### 3. Testing Environment

```python
class TestValidator:
    def validate_paths(self, paths):
        # Minimal validation for tests
        # Use temp directories, don't create real paths
        pass
```

## Implementation in Loaders Module

We've created a proof of concept with:

1. **loaders_validators.py** - Custom validators for loaders module
2. **paths_with_validation.py** - Enhanced path system with injection support

Key features demonstrated:
- Multiple injection methods (global, instance, class-level)
- Validator composition
- Different validators for different environments
- Runtime validator addition

## Benefits

1. **Flexibility** - Users define their own validation rules
2. **Separation of Concerns** - Validation logic separate from path management
3. **Reusability** - Share validators across projects
4. **Testability** - Test validators independently
5. **Environment-Specific** - Different rules for dev/test/prod
6. **Backward Compatible** - Works without custom validators

## Migration Path

1. **Phase 1**: Add validator injection API to PTOOL
2. **Phase 2**: Deprecate hardcoded validators
3. **Phase 3**: Move default validators to separate module
4. **Phase 4**: Full plugin system for validators

## Configuration Support

Future enhancement - validators in pyproject.toml:

```toml
[tool.project_paths.validators]
# Built-in validators
use = ["existence", "json", "permissions"]

# Custom validator modules
custom = ["myproject.validators.CustomValidator"]

# Environment-specific
[tool.project_paths.validators.development]
use = ["create_missing", "warn_only"]

[tool.project_paths.validators.production]
use = ["strict", "security"]
```

## Conclusion

Validator injection would make PTOOL significantly more flexible as a package while maintaining its simplicity for basic use cases. The implementation is straightforward and provides clear benefits for users who need domain-specific validation.

## Files Created for Demonstration

1. **loaders_validators.py** - Example custom validators
2. **paths_with_validation.py** - Enhanced path system with injection
3. **This proposal document** - Design and rationale

## Next Steps

1. Discuss with PTOOL maintainers
2. Choose implementation approach
3. Create pull request with chosen implementation
4. Add tests and documentation
5. Release as new version