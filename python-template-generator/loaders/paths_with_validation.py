#!/usr/bin/env python3
"""Enhanced path management with validator injection support.

This module demonstrates how to create a path management system that accepts
custom validators, similar to how an enhanced path-tool package might work.
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Protocol, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PathValidator(Protocol):
    """Protocol for path validators."""
    
    def validate_paths(self, paths_instance: Any) -> None:
        """Validate the paths instance."""
        ...


@dataclass
class ValidatedLoadersPaths:
    """LoadersPaths with validator injection support."""
    
    # Base directory for the project
    base_dir: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official"))
    
    # Auto-generated paths from pyproject.toml
    api_reference: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/API_REFERENCE.md"))
    architecture: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/ARCHITECTURE.md"))
    chunker: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/chunker"))
    core: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/core"))
    docs: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/docs"))
    embeddings: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/embeddings"))
    enrichers: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/enrichers"))
    finalizing_plan: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/FINALIZING_PLAN.md"))
    readme: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/README.md"))
    reorganization_plan: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/REORGANIZATION_PLAN.md"))
    scripts: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/scripts"))
    test_results: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/TEST_RUN_RESULTS"))
    test_results_after: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/TEST_RUN_RESULTS_AFTER_REORG"))
    tests: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/tests"))
    trash: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/TRASH"))
    utils: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/utils"))
    validators: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/validators"))
    vector_store: Path = field(default_factory=lambda: Path("/home/lasse/Documents/CoT_official/python-template-generator/loaders/vector_store"))
    
    # Class-level validator storage
    _validators: List[PathValidator] = field(default_factory=list, init=False, repr=False)
    
    def __post_init__(self):
        """Run validators after initialization."""
        for validator in self._validators:
            validator.validate_paths(self)
    
    @classmethod
    def with_validator(cls, validator: PathValidator) -> type:
        """Create a new class with the specified validator.
        
        Args:
            validator: Validator to use
            
        Returns:
            New class with validator injected
        """
        class ValidatedPaths(cls):
            def __post_init__(self):
                validator.validate_paths(self)
                super().__post_init__()
        
        return ValidatedPaths
    
    @classmethod
    def with_validators(cls, *validators: PathValidator) -> type:
        """Create a new class with multiple validators.
        
        Args:
            validators: Validators to use
            
        Returns:
            New class with validators injected
        """
        class MultiValidatedPaths(cls):
            def __post_init__(self):
                for validator in validators:
                    validator.validate_paths(self)
                super().__post_init__()
        
        return MultiValidatedPaths
    
    def add_validator(self, validator: PathValidator) -> None:
        """Add a validator to this instance.
        
        Args:
            validator: Validator to add
        """
        self._validators.append(validator)
        validator.validate_paths(self)
    
    def __getitem__(self, key: str) -> Path:
        """Allow dictionary-style access to paths."""
        return getattr(self, key)
    
    def to_dict(self) -> Dict[str, Path]:
        """Convert all paths to a dictionary."""
        return {
            field_name: getattr(self, field_name)
            for field_name in self.__dataclass_fields__
            if not field_name.startswith('_')
        }


# Global validator injection (similar to path-tool)
_global_validators: List[PathValidator] = []


def inject_validator(validator: PathValidator) -> None:
    """Inject a validator globally for all new paths instances.
    
    Args:
        validator: Validator to inject globally
    """
    _global_validators.append(validator)
    logger.info(f"Injected validator: {validator.__class__.__name__}")


def clear_validators() -> None:
    """Clear all global validators."""
    _global_validators.clear()
    logger.info("Cleared all global validators")


def create_paths_with_validation(validator: Optional[PathValidator] = None) -> ValidatedLoadersPaths:
    """Create a paths instance with optional custom validator.
    
    Args:
        validator: Optional custom validator. If None, uses global validators.
        
    Returns:
        ValidatedLoadersPaths instance
    """
    paths = ValidatedLoadersPaths()
    
    # Apply global validators
    for global_validator in _global_validators:
        paths.add_validator(global_validator)
    
    # Apply custom validator if provided
    if validator:
        paths.add_validator(validator)
    
    return paths


# Example validators
class ExistenceValidator:
    """Simple validator that checks if paths exist."""
    
    def validate_paths(self, paths: Any) -> None:
        """Check that critical paths exist."""
        critical = ['core', 'enrichers', 'validators', 'utils', 'scripts']
        for attr in critical:
            if hasattr(paths, attr):
                path = getattr(paths, attr)
                if not path.exists():
                    logger.warning(f"Path does not exist: {attr} -> {path}")


class CreateMissingValidator:
    """Validator that creates missing directories."""
    
    def validate_paths(self, paths: Any) -> None:
        """Create missing directories."""
        for attr_name in dir(paths):
            if attr_name.startswith('_'):
                continue
            
            attr = getattr(paths, attr_name, None)
            if isinstance(attr, Path) and not attr.suffix:  # It's a directory
                if not attr.exists():
                    logger.info(f"Creating missing directory: {attr}")
                    attr.mkdir(parents=True, exist_ok=True)


def demo_validator_injection():
    """Demonstrate different ways to inject validators."""
    print("=" * 60)
    print("Validator Injection Demonstration")
    print("=" * 60)
    
    # Method 1: Global injection
    print("\n1. Global Validator Injection:")
    print("-" * 30)
    inject_validator(ExistenceValidator())
    paths1 = create_paths_with_validation()
    print(f"Created paths with {len(_global_validators)} global validator(s)")
    
    # Method 2: Instance-specific validator
    print("\n2. Instance-Specific Validator:")
    print("-" * 30)
    clear_validators()
    paths2 = create_paths_with_validation(validator=CreateMissingValidator())
    print("Created paths with custom validator")
    
    # Method 3: Class-level injection
    print("\n3. Class-Level Validator:")
    print("-" * 30)
    ValidatedClass = ValidatedLoadersPaths.with_validator(ExistenceValidator())
    paths3 = ValidatedClass()
    print("Created paths with class-level validator")
    
    # Method 4: Multiple validators
    print("\n4. Multiple Validators:")
    print("-" * 30)
    MultiValidatedClass = ValidatedLoadersPaths.with_validators(
        ExistenceValidator(),
        CreateMissingValidator()
    )
    paths4 = MultiValidatedClass()
    print("Created paths with multiple validators")
    
    # Method 5: Runtime validator addition
    print("\n5. Runtime Validator Addition:")
    print("-" * 30)
    paths5 = ValidatedLoadersPaths()
    paths5.add_validator(ExistenceValidator())
    print("Added validator to existing instance")
    
    print("\n" + "=" * 60)
    print("✅ All injection methods demonstrated successfully!")


if __name__ == "__main__":
    # Import custom validators
    from loaders_validators import create_validator
    
    print("Testing Enhanced Path System with Validators")
    print("=" * 60)
    
    # Use our custom loaders validator
    validator = create_validator("default")
    paths = create_paths_with_validation(validator=validator)
    
    print(f"\nExample paths:")
    print(f"  Core: {paths.core}")
    print(f"  Tests: {paths.tests}")
    print(f"  Docs: {paths.docs}")
    
    # Run demonstration
    print("\n")
    demo_validator_injection()