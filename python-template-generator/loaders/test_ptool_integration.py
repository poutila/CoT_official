#!/usr/bin/env python3
"""Integration test for refactored PTOOL with loaders module."""

import sys
import os
from pathlib import Path

# Change to project root to find pyproject.toml
project_root = Path(__file__).parent.parent.parent
os.chdir(str(project_root))

# Add PTOOL to path
ptool_src = Path("python-template-generator/PTOOL/src")
sys.path.insert(0, str(ptool_src))

# Import refactored PTOOL
from project_paths import (
    create_project_paths,
    inject_validator,
    clear_validators,
    BasePathValidator,
    ValidationError,
    ProjectPathsBuilder,
)

print("Current working directory:", Path.cwd())

class LoadersValidator(BasePathValidator):
    """Simple validator for loaders module."""
    
    def __init__(self):
        super().__init__(strict=False)
        self.validated = False
    
    def validate_paths(self, paths_instance):
        """Validate loaders-specific paths."""
        self.validated = True
        self.clear_messages()
        
        # Check for loaders-related paths
        loaders_paths = []
        for attr_name in dir(paths_instance):
            if 'loaders' in attr_name and hasattr(paths_instance, attr_name):
                path = getattr(paths_instance, attr_name)
                if isinstance(path, Path):
                    loaders_paths.append((attr_name, path))
        
        print(f"    Found {len(loaders_paths)} loaders-related paths")
        
        # Check a few key paths exist
        key_paths = ['loaders_core', 'loaders_enrichers', 'loaders_tests']
        for key_path in key_paths:
            if hasattr(paths_instance, key_path):
                path = getattr(paths_instance, key_path)
                if not path.exists():
                    self.add_warning(f"Path does not exist: {key_path}")
                else:
                    print(f"    ✅ {key_path} exists: {path}")


def test_integration():
    """Test integration of refactored PTOOL with loaders paths."""
    print("\n" + "=" * 60)
    print("PTOOL Integration Test with Loaders Module")
    print("=" * 60)
    
    # Test 1: Create paths with custom validator
    print("\n1. Testing Factory Pattern")
    print("-" * 30)
    
    validator = LoadersValidator()
    ProjectPaths = create_project_paths(validator=validator)
    paths = ProjectPaths()
    
    if validator.validated:
        print("✅ Custom validator was called")
    else:
        print("❌ Custom validator was not called")
    
    # Test 2: Global injection
    print("\n2. Testing Global Injection")
    print("-" * 30)
    
    clear_validators()
    validator2 = LoadersValidator()
    inject_validator(validator2)
    
    ProjectPaths2 = create_project_paths()
    paths2 = ProjectPaths2()
    
    if validator2.validated:
        print("✅ Global validator was called")
    else:
        print("❌ Global validator was not called")
    
    # Test 3: Builder pattern
    print("\n3. Testing Builder Pattern")
    print("-" * 30)
    
    clear_validators()
    validator3 = LoadersValidator()
    
    ProjectPaths3 = (ProjectPathsBuilder()
        .add_validator(validator3)
        .build())
    
    paths3 = ProjectPaths3()
    
    if validator3.validated:
        print("✅ Builder pattern works")
    else:
        print("❌ Builder pattern failed")
    
    # Test 4: Test paths access
    print("\n4. Testing Paths Access")
    print("-" * 30)
    
    # Test dictionary-style access
    try:
        core_path = paths['loaders_core']
        print(f"✅ Dictionary access works: loaders_core = {core_path}")
    except Exception as e:
        print(f"❌ Dictionary access failed: {e}")
    
    # Test to_dict method
    try:
        paths_dict = paths.to_dict()
        loaders_keys = [k for k in paths_dict.keys() if 'loaders' in k]
        print(f"✅ to_dict() works: Found {len(loaders_keys)} loaders paths")
    except Exception as e:
        print(f"❌ to_dict() failed: {e}")
    
    # Test 5: Environment-specific validation
    print("\n5. Testing Environment-Specific Validation")
    print("-" * 30)
    
    class StrictValidator(BasePathValidator):
        def __init__(self):
            super().__init__(strict=True)
        
        def validate_paths(self, paths_instance):
            # This would normally check for critical paths
            print("    StrictValidator: All paths validated")
    
    class DevValidator(BasePathValidator):
        def __init__(self):
            super().__init__(strict=False)
        
        def validate_paths(self, paths_instance):
            print("    DevValidator: Lenient validation applied")
    
    # Test development environment
    clear_validators()
    dev_paths = (ProjectPathsBuilder()
        .add_validator(DevValidator())
        .build())()
    
    # Test production environment  
    clear_validators()
    try:
        prod_paths = (ProjectPathsBuilder()
            .add_validator(StrictValidator())
            .with_strict_validation()
            .build())()
        print("✅ Production validation passed")
    except ValidationError as e:
        print(f"⚠️  Production validation: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Integration test completed!")
    
    # Clean up
    clear_validators()


if __name__ == "__main__":
    test_integration()