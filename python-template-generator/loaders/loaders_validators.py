"""Custom validators for the loaders module paths.

This module demonstrates how custom validators could be injected into a path-tool
style system for domain-specific validation rules.
"""

from pathlib import Path
from typing import Self, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class LoadersPathValidator:
    """Custom validator for loaders module paths.
    
    This validator ensures that the loaders module structure is valid
    and creates missing directories with appropriate warnings.
    """
    
    def validate_paths(self, paths_instance: Any) -> None:
        """Main validation method called after path initialization.
        
        Args:
            paths_instance: Instance of LoadersPaths to validate
        """
        self._validate_core_modules(paths_instance)
        self._validate_test_structure(paths_instance)
        self._validate_documentation(paths_instance)
        self._check_import_consistency(paths_instance)
    
    def _validate_core_modules(self, paths: Any) -> None:
        """Ensure core module directories exist."""
        core_modules = ['core', 'enrichers', 'validators', 'utils', 'scripts']
        
        for module in core_modules:
            if hasattr(paths, module):
                module_path = getattr(paths, module)
                if not module_path.exists():
                    logger.warning(f"Core module missing: {module} at {module_path}")
                    # In production, might want to raise an error
                    # raise ValueError(f"Critical path missing: {module}")
                else:
                    # Check for __init__.py
                    init_file = module_path / "__init__.py"
                    if not init_file.exists():
                        logger.warning(f"Missing __init__.py in {module}")
    
    def _validate_test_structure(self, paths: Any) -> None:
        """Validate test directories and results."""
        if hasattr(paths, 'tests') and paths.tests.exists():
            # Check for expected test structure
            expected_dirs = ['unit', 'integration', 'fixtures']
            for dir_name in expected_dirs:
                test_dir = paths.tests / dir_name
                if not test_dir.exists():
                    logger.info(f"Test directory {dir_name} not found - might be expected")
        
        # Check test results
        if hasattr(paths, 'test_results'):
            if paths.test_results.exists():
                # Look for result files
                result_files = ['test_results.json', 'SUMMARY_REPORT.md', 'query_results.md']
                for file_name in result_files:
                    file_path = paths.test_results / file_name
                    if not file_path.exists():
                        logger.debug(f"Test result file {file_name} not found")
    
    def _validate_documentation(self, paths: Any) -> None:
        """Ensure key documentation files exist."""
        required_docs = ['api_reference', 'architecture', 'readme']
        
        for doc in required_docs:
            if hasattr(paths, doc):
                doc_path = getattr(paths, doc)
                if not doc_path.exists():
                    logger.warning(f"Missing documentation: {doc} at {doc_path}")
    
    def _check_import_consistency(self, paths: Any) -> None:
        """Check that import structure is consistent."""
        # Check that core __init__.py has backward compatibility imports if needed
        if hasattr(paths, 'core'):
            core_init = paths.core / "__init__.py"
            if core_init.exists():
                content = core_init.read_text()
                # Check for key exports
                expected_exports = ['RAGPipeline', 'Document', 'RAGConfig']
                for export in expected_exports:
                    if export not in content:
                        logger.debug(f"Export {export} not found in core/__init__.py")


class StrictLoadersValidator(LoadersPathValidator):
    """Strict validator that raises errors instead of warnings."""
    
    def _validate_core_modules(self, paths: Any) -> None:
        """Ensure core module directories exist - strict mode."""
        core_modules = ['core', 'enrichers', 'validators', 'utils', 'scripts']
        
        for module in core_modules:
            if hasattr(paths, module):
                module_path = getattr(paths, module)
                if not module_path.exists():
                    raise ValueError(f"Critical path missing: {module} at {module_path}")
                
                # Require __init__.py
                init_file = module_path / "__init__.py"
                if not init_file.exists():
                    raise ValueError(f"Missing __init__.py in {module}")


class DevelopmentValidator(LoadersPathValidator):
    """Development validator that creates missing directories."""
    
    def _validate_core_modules(self, paths: Any) -> None:
        """Ensure core module directories exist - create if missing."""
        core_modules = ['core', 'enrichers', 'validators', 'utils', 'scripts']
        
        for module in core_modules:
            if hasattr(paths, module):
                module_path = getattr(paths, module)
                if not module_path.exists():
                    logger.info(f"Creating missing module directory: {module}")
                    module_path.mkdir(parents=True, exist_ok=True)
                    
                    # Create __init__.py
                    init_file = module_path / "__init__.py"
                    if not init_file.exists():
                        init_file.write_text('"""Auto-generated __init__.py"""\n')
                        logger.info(f"Created __init__.py in {module}")


class TestEnvironmentValidator(LoadersPathValidator):
    """Validator for test environments."""
    
    def validate_paths(self, paths_instance: Any) -> None:
        """Minimal validation for test environments."""
        # Only validate that base paths exist
        if hasattr(paths_instance, 'base_dir'):
            if not paths_instance.base_dir.exists():
                raise ValueError(f"Base directory does not exist: {paths_instance.base_dir}")
        
        # Don't enforce other requirements in tests
        logger.info("Running in test mode - minimal validation")


def create_validator(mode: str = "default") -> LoadersPathValidator:
    """Factory function to create appropriate validator based on mode.
    
    Args:
        mode: One of "default", "strict", "development", "test"
        
    Returns:
        Appropriate validator instance
    """
    validators = {
        "default": LoadersPathValidator,
        "strict": StrictLoadersValidator,
        "development": DevelopmentValidator,
        "test": TestEnvironmentValidator,
    }
    
    validator_class = validators.get(mode, LoadersPathValidator)
    return validator_class()


# Example of how this could be integrated with path-tool style system
def inject_validator_into_paths(paths_class, validator):
    """Inject a validator into a paths class.
    
    This demonstrates how we could modify the paths class to use custom validation.
    """
    original_init = paths_class.__init__
    
    def new_init(self, *args, **kwargs):
        # Call original init
        original_init(self, *args, **kwargs)
        # Run custom validation
        validator.validate_paths(self)
    
    # Replace init method
    paths_class.__init__ = new_init
    return paths_class


if __name__ == "__main__":
    # Example usage
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    
    from project_paths import LoadersPaths
    
    # Create validator
    validator = create_validator("default")
    
    # Test validation
    paths = LoadersPaths()
    validator.validate_paths(paths)
    
    print("Validation complete!")