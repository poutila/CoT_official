"""Central path management using PTOOL with markdown validation.

This module provides type-safe, validated path management for the loaders module
using PTOOL with custom enricher-based validators for markdown content validation.
"""

from pathlib import Path
from typing import Any, Optional
import logging

# Import PTOOL from installed package with new discovery features
from project_paths import (
    create_project_paths,
    create_project_paths_auto,  # New auto-discovery
    BasePathValidator,
    ValidationError
)

# Set up logging
logger = logging.getLogger(__name__)


class MarkdownEnricherValidator(BasePathValidator):
    """Production validator that uses enrichers to validate markdown files.
    
    This validator provides dual validation:
    1. Path validation - ensures required paths exist
    2. Content validation - uses enrichers to validate markdown structure
    """
    
    def __init__(self, strict: bool = False, validate_content: bool = True):
        """Initialize the markdown validator.
        
        Args:
            strict: If True, raise errors instead of warnings
            validate_content: If True, validate markdown content (not just paths)
        """
        super().__init__(strict=strict)
        self.validate_content = validate_content
        self._enricher_class = None
        
    def _get_enricher_class(self):
        """Lazy load enricher class to avoid circular imports."""
        if self._enricher_class is None:
            try:
                from enrichers.context_fixed import ContextFixedEnricher
                self._enricher_class = ContextFixedEnricher
            except ImportError:
                logger.warning("Could not import ContextFixedEnricher, falling back to basic enricher")
                try:
                    from enrichers.markdown_validator import MarkdownDocEnricher
                    self._enricher_class = MarkdownDocEnricher
                except ImportError:
                    logger.error("No enricher available for markdown validation")
                    self._enricher_class = None
        return self._enricher_class
    
    def validate_paths(self, paths_instance: Any) -> None:
        """Validate paths and optionally markdown content.
        
        Args:
            paths_instance: ProjectPaths instance with configured paths
        """
        self.clear_messages()
        
        # Basic path validation
        self._validate_required_paths(paths_instance)
        
        # Content validation if enabled
        if self.validate_content:
            self._validate_markdown_content(paths_instance)
    
    def _validate_required_paths(self, paths_instance: Any) -> None:
        """Validate that required paths exist.
        
        Args:
            paths_instance: ProjectPaths instance
        """
        # Check for critical directories
        required_dirs = [
            ('base_dir', 'Project base directory'),
            ('loaders_dir', 'Loaders module directory'),
        ]
        
        for attr_name, description in required_dirs:
            if hasattr(paths_instance, attr_name):
                path = getattr(paths_instance, attr_name)
                if not path.exists():
                    self.add_error(f"{description} does not exist: {path}")
                elif not path.is_dir():
                    self.add_error(f"{description} is not a directory: {path}")
            else:
                self.add_warning(f"Missing attribute: {attr_name}")
        
        # Check for documentation
        if hasattr(paths_instance, 'loaders_docs'):
            docs_dir = paths_instance.loaders_docs
            if not docs_dir.exists():
                self.add_warning(f"Documentation directory missing: {docs_dir}")
                # In development, we might want to create it
                if not self.strict:
                    logger.info(f"Creating documentation directory: {docs_dir}")
                    docs_dir.mkdir(parents=True, exist_ok=True)
    
    def _validate_markdown_content(self, paths_instance: Any) -> None:
        """Validate markdown file content using enrichers.
        
        Args:
            paths_instance: ProjectPaths instance
        """
        EnricherClass = self._get_enricher_class()
        if not EnricherClass:
            self.add_warning("No enricher available, skipping content validation")
            return
        
        # Find markdown files to validate
        md_files = []
        
        # Check loaders docs
        if hasattr(paths_instance, 'loaders_docs') and paths_instance.loaders_docs.exists():
            md_files.extend(paths_instance.loaders_docs.glob('**/*.md'))
        
        # Check for README
        if hasattr(paths_instance, 'loaders_dir'):
            readme = paths_instance.loaders_dir / "README.md"
            if readme.exists():
                md_files.append(readme)
        
        # Check for FINALIZING_PLAN
        if hasattr(paths_instance, 'loaders_dir'):
            plan = paths_instance.loaders_dir / "FINALIZING_PLAN.md"
            if plan.exists():
                md_files.append(plan)
        
        # Validate each file
        for md_file in md_files:
            self._validate_single_markdown(md_file, EnricherClass)
    
    def _validate_single_markdown(self, md_file: Path, EnricherClass) -> None:
        """Validate a single markdown file.
        
        Args:
            md_file: Path to markdown file
            EnricherClass: Enricher class to use for validation
        """
        try:
            # Parse with enricher
            enricher = EnricherClass(md_file)
            doc = enricher.parse_md()
            
            # Validation checks
            issues = []
            
            # Structure checks
            if not doc.sections:
                issues.append("No sections found")
            
            # Content checks
            empty_sections = []
            for section in doc.sections:
                if not section.content.strip():
                    empty_sections.append(section.title)
            
            if empty_sections:
                issues.append(f"Empty sections: {', '.join(empty_sections[:3])}")
            
            # Link validation
            if hasattr(doc, 'links'):
                broken_links = self._check_links(doc.links, md_file)
                if broken_links:
                    issues.append(f"{len(broken_links)} broken links")
            
            # Code example validation for enhanced enrichers
            if hasattr(doc, 'code_blocks') and doc.code_blocks:
                # Check for good/bad examples
                if hasattr(doc, 'full_examples'):
                    from enrichers.full_enhanced import ExampleType
                    good_count = sum(1 for e in doc.full_examples if e.example_type == ExampleType.GOOD)
                    bad_count = sum(1 for e in doc.full_examples if e.example_type == ExampleType.BAD)
                    
                    if doc.code_blocks and not (good_count or bad_count):
                        issues.append("Code blocks without good/bad examples")
            
            # Report results
            rel_path = md_file.relative_to(Path.cwd()) if md_file.is_absolute() else md_file
            
            if issues:
                msg = f"{rel_path}: {', '.join(issues)}"
                if self.strict:
                    self.add_error(msg)
                else:
                    self.add_warning(msg)
            else:
                # Success message
                stats = f"{len(doc.sections)} sections"
                if hasattr(doc, 'code_blocks'):
                    stats += f", {len(doc.code_blocks)} code blocks"
                self.add_warning(f"✓ {rel_path}: Valid ({stats})")
                
        except Exception as e:
            msg = f"Failed to validate {md_file.name}: {str(e)[:100]}"
            if self.strict:
                self.add_error(msg)
            else:
                self.add_warning(msg)
    
    def _check_links(self, links: list, md_file: Path) -> list:
        """Check for broken internal links.
        
        Args:
            links: List of links from document
            md_file: Path to the markdown file
            
        Returns:
            List of broken link targets
        """
        broken = []
        
        for link in links:
            if not link:
                continue
                
            # Handle different link formats
            if isinstance(link, tuple) and len(link) > 0:
                target = link[0]
            elif isinstance(link, str):
                target = link
            else:
                continue
            
            # Check relative links
            if target and not target.startswith(('http://', 'https://', '#')):
                # Resolve relative to markdown file location
                link_path = md_file.parent / target
                if not link_path.exists():
                    broken.append(target)
        
        return broken


class DevelopmentValidator(MarkdownEnricherValidator):
    """Development mode validator - lenient with helpful messages."""
    
    def __init__(self):
        """Initialize development validator with lenient settings."""
        super().__init__(strict=False, validate_content=True)
        

class ProductionValidator(MarkdownEnricherValidator):
    """Production mode validator - strict validation."""
    
    def __init__(self):
        """Initialize production validator with strict settings."""
        super().__init__(strict=True, validate_content=True)


class CIValidator(MarkdownEnricherValidator):
    """CI/CD validator - validates everything strictly."""
    
    def __init__(self):
        """Initialize CI validator for automated testing."""
        super().__init__(strict=True, validate_content=True)


# Factory function for creating paths with appropriate validator
def create_loader_paths(mode: str = "development", use_auto_discovery: bool = True) -> Any:
    """Create ProjectPaths instance with appropriate validator.
    
    Args:
        mode: One of "development", "production", "ci", or "none"
        use_auto_discovery: If True, use auto-discovery to find project root
        
    Returns:
        Configured ProjectPaths class instance
        
    Raises:
        ValueError: If mode is not recognized
    """
    validators = {
        "development": DevelopmentValidator,
        "production": ProductionValidator,
        "ci": CIValidator,
        "none": None,
    }
    
    if mode not in validators:
        raise ValueError(f"Unknown mode: {mode}. Use one of: {list(validators.keys())}")
    
    validator_class = validators[mode]
    validator = validator_class() if validator_class else None
    
    # Use auto-discovery if enabled (recommended)
    if use_auto_discovery:
        try:
            return create_project_paths_auto(validator=validator, fallback_to_cwd=True)
        except Exception as e:
            logger.warning(f"Auto-discovery failed: {e}. Falling back to standard creation.")
    
    # Fallback to standard creation (requires pyproject.toml in cwd)
    ProjectPaths = create_project_paths(validator=validator)
    
    # Return instance
    return ProjectPaths()


# Default paths instance for module-level use
_paths_instance = None


def get_paths(mode: Optional[str] = None) -> Any:
    """Get or create the shared paths instance.
    
    Args:
        mode: Override the default mode (development)
        
    Returns:
        ProjectPaths instance
    """
    global _paths_instance
    
    if _paths_instance is None or mode is not None:
        actual_mode = mode or "development"
        _paths_instance = create_loader_paths(actual_mode)
        
        # Log validation results
        if hasattr(_paths_instance, '__validator__'):
            validator = _paths_instance.__validator__
            if validator and (validator.errors or validator.warnings):
                logger.info(f"Path validation completed with {len(validator.errors)} errors, {len(validator.warnings)} warnings")
                for error in validator.errors:
                    logger.error(f"Validation error: {error}")
                for warning in validator.warnings[:5]:  # Limit warnings in logs
                    logger.debug(f"Validation warning: {warning}")
    
    return _paths_instance


# Module-level convenience attributes
def __getattr__(name):
    """Provide module-level access to paths attributes.
    
    This allows: 
        from loaders.paths import loaders_dir, base_dir
    Instead of:
        from loaders.paths import get_paths
        paths = get_paths()
        loaders_dir = paths.loaders_dir
    """
    paths = get_paths()
    if hasattr(paths, name):
        return getattr(paths, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Export main components
__all__ = [
    'create_loader_paths',
    'get_paths',
    'MarkdownEnricherValidator',
    'DevelopmentValidator',
    'ProductionValidator', 
    'CIValidator',
]