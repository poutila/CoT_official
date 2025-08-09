"""Custom validators for the loaders module using refactored PTOOL.

This module demonstrates how to create domain-specific validators that can be
injected into the refactored PTOOL system for path management.
"""

import sys
from pathlib import Path
from typing import Any, List
import logging

# Add PTOOL to path
ptool_path = Path(__file__).parent.parent / "PTOOL" / "src"
sys.path.insert(0, str(ptool_path))

from project_paths import BasePathValidator, ValidationError

logger = logging.getLogger(__name__)


class RAGStructureValidator(BasePathValidator):
    """Validator for RAG pipeline structure."""
    
    def __init__(self, strict: bool = False):
        super().__init__(strict)
        self.name = "RAGStructureValidator"
    
    def validate_paths(self, paths_instance: Any) -> None:
        """Validate RAG module structure."""
        self.clear_messages()
        
        # Critical RAG components
        required_modules = [
            ('core', "Core RAG pipeline module"),
            ('chunker', "Chunking module"),
            ('embeddings', "Embeddings module"), 
            ('vector_store', "Vector storage module"),
        ]
        
        for attr_name, description in required_modules:
            if hasattr(paths_instance, attr_name):
                module_path = getattr(paths_instance, attr_name)
                if not module_path.exists():
                    self.add_error(f"Missing {description}: {module_path}")
                else:
                    # Check for __init__.py
                    init_file = module_path / "__init__.py"
                    if not init_file.exists():
                        self.add_warning(f"No __init__.py in {description}")
        
        # Check for key files
        key_files = [
            ('api_reference', "API documentation"),
            ('architecture', "Architecture documentation"),
            ('readme', "README file"),
        ]
        
        for attr_name, description in key_files:
            if hasattr(paths_instance, attr_name):
                file_path = getattr(paths_instance, attr_name)
                if not file_path.exists():
                    self.add_warning(f"Missing {description}: {file_path}")


class TestResultsValidator(BasePathValidator):
    """Validator for test results structure."""
    
    def __init__(self, strict: bool = False):
        super().__init__(strict)
        self.name = "TestResultsValidator"
    
    def validate_paths(self, paths_instance: Any) -> None:
        """Validate test results structure."""
        self.clear_messages()
        
        # Check test directories exist
        test_attrs = ['tests', 'test_results', 'test_results_after']
        
        for attr_name in test_attrs:
            if hasattr(paths_instance, attr_name):
                test_path = getattr(paths_instance, attr_name)
                if test_path.exists():
                    logger.debug(f"Found test directory: {test_path}")
                    
                    # If it's a test results directory, check for expected files
                    if 'test_results' in attr_name:
                        self._validate_test_results_content(test_path)
                else:
                    if attr_name == 'tests':
                        self.add_error(f"Critical: Tests directory missing: {test_path}")
                    else:
                        self.add_warning(f"Test results missing: {test_path}")
    
    def _validate_test_results_content(self, results_dir: Path) -> None:
        """Validate test results directory content."""
        expected_files = [
            'test_results.json',
            'SUMMARY_REPORT.md', 
            'query_results.md'
        ]
        
        for file_name in expected_files:
            file_path = results_dir / file_name
            if not file_path.exists():
                self.add_warning(f"Missing test result file: {file_name}")


class DevelopmentValidator(BasePathValidator):
    """Validator for development environment - creates missing directories."""
    
    def __init__(self, create_missing: bool = True):
        super().__init__(strict=False)
        self.name = "DevelopmentValidator"
        self.create_missing = create_missing
    
    def validate_paths(self, paths_instance: Any) -> None:
        """Validate and optionally create development paths."""
        self.clear_messages()
        
        # Core directories that should exist in development
        dev_dirs = ['core', 'enrichers', 'validators', 'utils', 'scripts', 'tests']
        
        for attr_name in dev_dirs:
            if hasattr(paths_instance, attr_name):
                dir_path = getattr(paths_instance, attr_name)
                
                if not dir_path.exists() and self.create_missing:
                    logger.info(f"Creating development directory: {dir_path}")
                    dir_path.mkdir(parents=True, exist_ok=True)
                    
                    # Create __init__.py for Python modules
                    if attr_name != 'tests':  # Don't create __init__.py in tests
                        init_file = dir_path / "__init__.py"
                        if not init_file.exists():
                            init_content = f'"""{attr_name.title()} module for RAG pipeline."""\n'
                            init_file.write_text(init_content)
                            logger.info(f"Created __init__.py in {attr_name}")


class ProductionValidator(BasePathValidator):
    """Strict validator for production environment."""
    
    def __init__(self):
        super().__init__(strict=True)
        self.name = "ProductionValidator"
    
    def validate_paths(self, paths_instance: Any) -> None:
        """Strict validation for production."""
        self.clear_messages()
        
        # All critical paths must exist in production
        critical_paths = [
            'core', 'enrichers', 'validators', 'utils', 'scripts',
            'chunker', 'embeddings', 'vector_store',
            'api_reference', 'readme'
        ]
        
        for attr_name in critical_paths:
            if hasattr(paths_instance, attr_name):
                path = getattr(paths_instance, attr_name)
                if not path.exists():
                    self.add_error(f"CRITICAL: Missing in production: {path}")
        
        # Validate no TRASH or temp directories in production
        if hasattr(paths_instance, 'trash'):
            trash_path = getattr(paths_instance, 'trash')
            if trash_path.exists() and any(trash_path.iterdir()):
                self.add_warning("TRASH directory contains files in production")


class CIValidator(BasePathValidator):
    """Validator for CI/CD environment."""
    
    def __init__(self):
        super().__init__(strict=True)
        self.name = "CIValidator"
    
    def validate_paths(self, paths_instance: Any) -> None:
        """Validate paths for CI/CD."""
        self.clear_messages()
        
        # In CI, we need source code but not necessarily results
        required_source = ['core', 'enrichers', 'validators', 'utils', 'scripts', 'tests']
        
        for attr_name in required_source:
            if hasattr(paths_instance, attr_name):
                path = getattr(paths_instance, attr_name)
                if not path.exists():
                    self.add_error(f"CI: Missing source directory: {path}")
        
        # Check that we have test files
        if hasattr(paths_instance, 'tests'):
            tests_dir = getattr(paths_instance, 'tests')
            if tests_dir.exists():
                test_files = list(tests_dir.glob("**/*test*.py"))
                if not test_files:
                    self.add_error("CI: No test files found")


def create_validator_for_environment(env: str = "development") -> BasePathValidator:
    """Factory function to create appropriate validator for environment.
    
    Args:
        env: Environment name ("development", "production", "ci", "test")
        
    Returns:
        Appropriate validator for the environment
    """
    from project_paths import combine_validators
    
    validators_map = {
        "development": [
            RAGStructureValidator(strict=False),
            TestResultsValidator(strict=False),
            DevelopmentValidator(create_missing=True),
        ],
        "production": [
            RAGStructureValidator(strict=True),
            ProductionValidator(),
        ],
        "ci": [
            RAGStructureValidator(strict=True),
            CIValidator(),
        ],
        "test": [
            RAGStructureValidator(strict=False),
        ],
    }
    
    validators = validators_map.get(env, validators_map["development"])
    
    if len(validators) == 1:
        return validators[0]
    else:
        return combine_validators(*validators, strict=(env in ["production", "ci"]))


if __name__ == "__main__":
    # Demo the validators
    print("=== Loaders PTOOL Validators Demo ===")
    
    # Import our current paths
    sys.path.insert(0, str(Path(__file__).parent))
    from project_paths import LoadersPaths
    
    paths = LoadersPaths()
    
    # Test different validators
    environments = ["development", "production", "ci", "test"]
    
    for env in environments:
        print(f"\n{env.title()} Environment Validation:")
        print("-" * 40)
        
        validator = create_validator_for_environment(env)
        
        try:
            validator.validate_paths(paths)
            print(f"✅ {env} validation passed")
            if validator.has_warnings():
                print(f"⚠️  {len(validator.warnings)} warning(s)")
        except ValidationError as e:
            print(f"❌ {env} validation failed: {e}")
        except Exception as e:
            print(f"💥 {env} validation error: {e}")
    
    print("\n" + "=" * 50)