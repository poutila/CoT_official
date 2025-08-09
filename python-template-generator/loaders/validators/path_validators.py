"""Path validators for loaders module using PTOOL."""

from pathlib import Path
from typing import Any

from project_paths import BasePathValidator, ValidationError


class LoadersPathValidator(BasePathValidator):
    """Validator for loaders module paths."""
    
    def validate_paths(self, paths_instance: Any) -> None:
        """Validate that required loaders directories exist.
        
        Args:
            paths_instance: ProjectPaths instance to validate
        """
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
            if hasattr(paths_instance, dir_name):
                dir_path = getattr(paths_instance, dir_name)
                if not dir_path.exists():
                    if self.strict:
                        self.add_error(f"Required directory {dir_name} does not exist: {dir_path}")
                    else:
                        dir_path.mkdir(parents=True, exist_ok=True)
                        self.add_warning(f"Created missing directory: {dir_name}")
        
        # Check test directory
        if hasattr(paths_instance, 'loaders_tests'):
            if not paths_instance.loaders_tests.exists():
                self.add_warning("Test directory missing - will affect test coverage")


class DevelopmentPathValidator(BasePathValidator):
    """Development environment validator - creates missing directories."""
    
    def validate_paths(self, paths_instance: Any) -> None:
        """Validate paths for development environment.
        
        Creates missing directories automatically.
        
        Args:
            paths_instance: ProjectPaths instance to validate
        """
        self.clear_messages()
        # Lenient validation for development
        self.add_warning("Development mode - creating missing directories")
        
        created_dirs = []
        for attr_name in dir(paths_instance):
            if attr_name.startswith('loaders_') and not attr_name.startswith('_'):
                path = getattr(paths_instance, attr_name)
                if isinstance(path, Path) and not path.exists():
                    # Only create if it looks like a directory path
                    if not path.suffix:  # No file extension
                        path.mkdir(parents=True, exist_ok=True)
                        created_dirs.append(attr_name)
        
        if created_dirs:
            self.add_warning(f"Created directories: {', '.join(created_dirs)}")


class ProductionPathValidator(BasePathValidator):
    """Production environment validator - strict checking."""
    
    def validate_paths(self, paths_instance: Any) -> None:
        """Validate paths for production environment.
        
        All required paths must exist, no automatic creation.
        
        Args:
            paths_instance: ProjectPaths instance to validate
        
        Raises:
            ValidationError: If any required path is missing
        """
        self.clear_messages()
        # Strict validation for production
        self.strict = True
        
        # All required paths must exist
        required_attrs = [
            'loaders_core',
            'loaders_enrichers', 
            'loaders_validators',
            'loaders_chunker',
            'loaders_embeddings',
            'loaders_vector_store',
            'loaders_utils',
            'loaders_scripts'
        ]
        
        missing_paths = []
        for attr_name in required_attrs:
            if hasattr(paths_instance, attr_name):
                path = getattr(paths_instance, attr_name)
                if isinstance(path, Path) and not path.exists():
                    missing_paths.append(f"{attr_name}: {path}")
                    self.add_error(f"Missing required path in production: {attr_name}")
        
        if missing_paths:
            error_msg = "Production validation failed. Missing paths:\n" + "\n".join(missing_paths)
            if self.strict:
                raise ValidationError(
                    message=error_msg,
                    errors=self.errors,
                    warnings=self.warnings
                )


class TestPathValidator(BasePathValidator):
    """Test environment validator - uses temp directories."""
    
    def validate_paths(self, paths_instance: Any) -> None:
        """Validate paths for test environment.
        
        Very lenient, allows temp directories.
        
        Args:
            paths_instance: ProjectPaths instance to validate
        """
        self.clear_messages()
        self.add_warning("Test mode - using temporary directories")