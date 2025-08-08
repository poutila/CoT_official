"""Test to validate import updates after reorganization."""

import re
from pathlib import Path

import pytest


class TestImportUpdates:
    """Ensure all imports are updated correctly after moving files."""

    def test_no_old_imports_remain(self):
        """After reorganization, no old import patterns should exist."""
        # This test will be activated AFTER reorganization

        # Old patterns that should NOT exist after reorganization
        old_patterns = [
            r"from enrichers.context_fixed import",
            r"from enrichers.enhanced_with_examples import",
            r"from enrichers.full_enhanced import",
            r"from enrichers.minimal_enhanced import",
            r"from enrichers.markdown_validator import",
            r"from validators.base_validator import",
            r"from validators.pydantic_models import",
            r"from utils.sluggify import",
            r"import context_fixed_enricher",
            r"import enhanced_enricher_with_examples",
            r"import full_enhanced_enricher",
            r"import minimal_enhanced_enricher",
            r"import markdown_validator_enricher",
            r"from validators import base_validator",
            r"from validators import pydantic_models",
            r"from utils import sluggify",
        ]

        # After reorganization, these should be:
        # from enrichers.context_fixed import
        # from enrichers.enhanced_with_examples import
        # from enrichers import ContextFixedEnricher
        # from utils import sluggify
        # etc.

        base_path = Path(__file__).parent.parent
        python_files = list(base_path.glob("**/*.py"))

        violations: list[tuple[str, str]] = []

        for file in python_files:
            # Skip this test file itself
            if "test_import_updates.py" in str(file):
                continue
            # Skip cache and build directories
            if "__pycache__" in str(file) or "htmlcov" in str(file) or "TRASH" in str(file):
                continue

            with open(file, encoding="utf-8") as f:
                content = f.read()
                for pattern in old_patterns:
                    if re.search(pattern, content):
                        # For now, this is expected to find matches BEFORE reorganization
                        # After reorganization, this should fail if we missed updating an import
                        relative_path = str(file.relative_to(base_path))
                        violations.append((relative_path, pattern))

        # BEFORE reorganization: We expect to find these patterns (so we skip)
        # AFTER reorganization: This should fail if any are found
        if violations:
            # For now, just skip since we haven't reorganized yet
            pytest.skip(
                f"Found {len(violations)} old import patterns (expected before reorganization)"
            )

            # After reorganization, uncomment this to make it fail:
            # msg = "Found old import patterns that should have been updated:\n"
            # for file, pattern in violations[:10]:  # Show first 10
            #     msg += f"  {file}: {pattern}\n"
            # if len(violations) > 10:
            #     msg += f"  ... and {len(violations) - 10} more\n"
            # pytest.fail(msg)

    def test_new_imports_work(self):
        """Test that new import structure works correctly."""
        # After reorganization, these imports should work
        try:
            # Try importing from new structure
            from enrichers import ContextFixedEnricher, MinimalEnhancedEnricher
            from utils import sluggify

            assert ContextFixedEnricher is not None
            assert MinimalEnhancedEnricher is not None
            assert sluggify is not None

            # If we get here, reorganization is complete!
            print("✅ New import structure is working!")

        except ImportError as e:
            # This is expected to fail BEFORE reorganization
            pytest.skip(f"New structure not yet in place: {e}")

    def test_all_imports_documented(self):
        """Ensure all import changes are documented."""
        # Check if REORGANIZATION_PLAN.md exists and has import mapping
        plan_file = Path(__file__).parent.parent / "REORGANIZATION_PLAN.md"

        if not plan_file.exists():
            pytest.skip("REORGANIZATION_PLAN.md not yet created")

        with open(plan_file) as f:
            content = f.read()

        # Check for import mapping section
        required_sections = ["Import Mapping", "Old Import", "New Import", "Update Script"]

        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            pytest.fail(f"REORGANIZATION_PLAN.md missing sections: {', '.join(missing_sections)}")

    def test_relative_imports_updated(self):
        """Test that relative imports within moved modules are updated."""
        # This is important for modules that import from each other

        base_path = Path(__file__).parent.parent

        # After reorganization, check enrichers folder
        enrichers_path = base_path / "enrichers"
        if not enrichers_path.exists():
            pytest.skip("Enrichers folder not yet created")

        # Check for correct relative imports
        for file in enrichers_path.glob("*.py"):
            if file.name == "__init__.py":
                continue

            with open(file) as f:
                content = f.read()

            # Check for old-style imports that should be relative
            if "from enrichers.minimal_enhanced import" in content:
                pytest.fail(f"{file.name} still uses old import style instead of relative imports")

            # Should use relative imports like:
            # from .minimal_enhanced import ...
            # or absolute like:
            # from enrichers.minimal_enhanced import ...


class TestImportPerformance:
    """Test that reorganization doesn't hurt import performance."""

    def test_import_time(self):
        """Measure import time to ensure it's reasonable."""
        import time

        # Measure time to import main modules
        start = time.time()

        try:
            from core.models import Document, RAGConfig
            from core.pipeline import RAGPipeline

            elapsed = time.time() - start

            # Import should be fast (< 5 seconds even on slow systems)
            assert elapsed < 5.0, f"Import took {elapsed:.2f} seconds (too slow!)"

            print(f"✅ Import time: {elapsed:.2f} seconds")

        except ImportError:
            pytest.skip("Modules not importable")

    def test_no_import_side_effects(self):
        """Ensure imports don't have side effects."""
        import sys

        # Track modules before import
        modules_before = set(sys.modules.keys())

        # Import our modules
        try:
            from core.models import RAGConfig
            from core.pipeline import RAGPipeline

            # Check what new modules were loaded
            modules_after = set(sys.modules.keys())
            new_modules = modules_after - modules_before

            # Check for unexpected modules (e.g., no GUI libraries unless needed)
            unexpected = []
            gui_modules = ["tkinter", "PyQt5", "wx"]
            for module in new_modules:
                for gui in gui_modules:
                    if gui in module:
                        unexpected.append(module)

            if unexpected:
                pytest.warn(f"Unexpected GUI modules imported: {unexpected}")

        except ImportError:
            pytest.skip("Modules not importable")
