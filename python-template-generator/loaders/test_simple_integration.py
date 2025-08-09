#!/usr/bin/env python3
"""Simple integration test for refactored PTOOL factory functions."""

import sys
import os
from pathlib import Path

# Change to project root to find pyproject.toml
project_root = Path(__file__).parent.parent.parent
os.chdir(str(project_root))

# Add PTOOL to path
ptool_src = Path("python-template-generator/PTOOL/src")
sys.path.insert(0, str(ptool_src))

print("Current working directory:", Path.cwd())

class SimpleValidator:
    """Simple validator to test injection."""
    
    def __init__(self, name):
        self.name = name
        self.called = False
    
    def validate_paths(self, paths_instance):
        """Simple validation that just tracks calls."""
        self.called = True
        print(f"    {self.name} validator called")
        
        # Count loaders paths
        loaders_count = sum(1 for attr in dir(paths_instance) 
                           if 'loaders' in attr and not attr.startswith('_'))
        print(f"    Found {loaders_count} loaders-related attributes")


def test_factory_only():
    """Test only the factory functions without original model."""
    print("\n" + "=" * 60)
    print("PTOOL Factory Functions Test")
    print("=" * 60)
    
    # Import only factory functions (avoid model.py issues)
    from project_paths.factory import create_project_paths, inject_validator, clear_validators
    
    # Test 1: Basic factory
    print("\n1. Testing Basic Factory")
    print("-" * 30)
    
    try:
        validator = SimpleValidator("Factory")
        ProjectPaths = create_project_paths(validator=validator)
        paths = ProjectPaths()
        
        if validator.called:
            print("✅ Factory with validator works!")
        else:
            print("❌ Validator was not called")
            
        # Test paths access
        sample_paths = [attr for attr in dir(paths) if 'loaders' in attr][:3]
        print(f"    Sample paths: {sample_paths}")
        
    except Exception as e:
        print(f"❌ Factory test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Global injection  
    print("\n2. Testing Global Injection")
    print("-" * 30)
    
    try:
        clear_validators()
        validator = SimpleValidator("Global")
        inject_validator(validator)
        
        ProjectPaths = create_project_paths()
        paths = ProjectPaths()
        
        if validator.called:
            print("✅ Global injection works!")
        else:
            print("❌ Global validator was not called")
            
        clear_validators()
        
    except Exception as e:
        print(f"❌ Global injection test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Multiple validators
    print("\n3. Testing Multiple Validators")
    print("-" * 30)
    
    try:
        from project_paths.factory import create_project_paths_with_validators
        
        validator1 = SimpleValidator("Multi-1")
        validator2 = SimpleValidator("Multi-2")
        
        ProjectPaths = create_project_paths_with_validators(validator1, validator2)
        paths = ProjectPaths()
        
        if validator1.called and validator2.called:
            print("✅ Multiple validators work!")
        else:
            print("❌ Not all validators were called")
    
    except Exception as e:
        print(f"❌ Multiple validators test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Factory Functions Test Complete!")


if __name__ == "__main__":
    test_factory_only()