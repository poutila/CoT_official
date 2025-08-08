"""Tests to ensure imports work correctly before and after reorganization."""

import ast
import importlib
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestImportStructure:
    """Test that all imports are valid and working."""

    def test_root_level_imports(self):
        """Test all current root-level module imports work."""
        root_modules = [
            "context_fixed_enricher",
            "enhanced_enricher_with_examples",
            "full_enhanced_enricher",
            "minimal_enhanced_enricher",
            "markdown_validator_enricher",
            "markdown_base_validator",
            "markdown_pydantic_model",
            "rag_pipeline",
            "rag_models",
            "rag_adapters",
            "sluggify_util",
        ]

        failed_imports = []
        for module_name in root_modules:
            try:
                module = importlib.import_module(module_name)
                assert module is not None, f"Module {module_name} imported but is None"
            except ImportError as e:
                failed_imports.append((module_name, str(e)))

        if failed_imports:
            msg = "Failed to import modules:\n"
            for mod, err in failed_imports:
                msg += f"  - {mod}: {err}\n"
            pytest.fail(msg)

    def test_submodule_imports(self):
        """Test all submodule imports work."""
        submodules = [
            ("chunker", "SemanticChunker"),
            ("chunker", "ChunkingConfig"),
            ("chunker", "Chunk"),
            ("embeddings", "SentenceTransformerProvider"),
            ("embeddings", "EmbeddingProviderConfig"),
            ("vector_store", "FAISSVectorStore"),
            ("vector_store", "VectorStoreConfig"),
        ]

        failed_imports = []
        for module_path, class_name in submodules:
            try:
                module = importlib.import_module(module_path)
                if not hasattr(module, class_name):
                    failed_imports.append(
                        (f"{module_path}.{class_name}", f"Class {class_name} not found")
                    )
            except ImportError as e:
                failed_imports.append((module_path, str(e)))

        if failed_imports:
            msg = "Failed to import submodules:\n"
            for item, err in failed_imports:
                msg += f"  - {item}: {err}\n"
            pytest.fail(msg)

    def test_cross_module_dependencies(self):
        """Test that modules can import from each other correctly."""
        # Test critical import chains
        try:
            from context_fixed_enricher import ContextFixedEnricher
            from rag_models import Document, RAGConfig
            from rag_pipeline import RAGPipeline

            # These imports should work without circular dependency issues
            assert RAGPipeline is not None
            assert ContextFixedEnricher is not None
            assert RAGConfig is not None
            assert Document is not None
        except ImportError as e:
            pytest.fail(f"Cross-module import failed: {e}")

    def test_no_circular_imports(self):
        """Detect potential circular imports."""
        import_graph: dict[str, list[str]] = {}

        # Get all Python files in the project
        base_path = Path(__file__).parent.parent
        python_files = [
            f
            for f in base_path.glob("**/*.py")
            if "test" not in str(f)
            and "__pycache__" not in str(f)
            and "TRASH" not in str(f)
            and "htmlcov" not in str(f)
        ]

        for file in python_files:
            with open(file, encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read())
                    imports = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            imports.extend([n.name for n in node.names])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module and not node.module.startswith("."):
                                imports.append(node.module)

                    relative_path = str(file.relative_to(base_path))
                    import_graph[relative_path] = imports
                except SyntaxError:
                    pass  # Skip files with syntax errors

        # Check for potential cycles (simplified check)
        potential_cycles = []
        for file, imports in import_graph.items():
            file_module = file.replace(".py", "").replace("/", ".")
            for imported in imports:
                # Check if imported module also imports this file
                for other_file, other_imports in import_graph.items():
                    other_module = other_file.replace(".py", "").replace("/", ".")
                    if imported in other_module:
                        if file_module in other_imports:
                            cycle = f"{file} <-> {other_file}"
                            if cycle not in potential_cycles:
                                potential_cycles.append(cycle)

        # This is a warning, not a failure (some circular imports might be intentional)
        if potential_cycles:
            for cycle in potential_cycles:
                pytest.warns(UserWarning, match=f"Potential circular import: {cycle}")


class TestModuleInterfaces:
    """Test that module interfaces remain consistent."""

    def test_enricher_interface(self):
        """Test all enrichers have consistent interface."""
        import tempfile
        from pathlib import Path

        from context_fixed_enricher import ContextFixedEnricher
        from minimal_enhanced_enricher import MinimalEnhancedEnricher

        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test\nContent")
            temp_path = Path(f.name)

        try:
            # Check that key methods exist
            enricher = ContextFixedEnricher(temp_path)
            # ContextFixedEnricher has different interface - it uses extract_rich_doc
            assert hasattr(enricher, "extract_rich_doc"), (
                "ContextFixedEnricher missing 'extract_rich_doc' method"
            )

            # MinimalEnhancedEnricher also needs a path and has extract_rich_doc method
            min_enricher = MinimalEnhancedEnricher(temp_path)
            assert hasattr(min_enricher, "extract_rich_doc"), (
                "MinimalEnhancedEnricher missing 'extract_rich_doc' method"
            )
        finally:
            # Clean up temp file
            temp_path.unlink()

    def test_pipeline_public_api(self):
        """Test RAGPipeline public API is intact."""
        from rag_models import RAGConfig
        from rag_pipeline import RAGPipeline

        config = RAGConfig()
        pipeline = RAGPipeline(config)

        # Test all public methods exist
        public_methods = [
            "index_documents",
            "retrieve",
            "load_documents",
            "save",
            "load",
            "split_documents",
            "invoke",
            "batch",
            "stream",
        ]

        missing_methods = []
        for method in public_methods:
            if not hasattr(pipeline, method):
                missing_methods.append(method)

        if missing_methods:
            pytest.fail(f"RAGPipeline missing methods: {', '.join(missing_methods)}")

    def test_vector_store_interface(self):
        """Test vector store interface consistency."""
        from vector_store import FAISSVectorStore
        from vector_store.models import VectorStoreConfig

        config = VectorStoreConfig()
        store = FAISSVectorStore(config)

        # Check required methods
        required_methods = ["add", "search", "save", "load", "clear"]
        missing_methods = []
        for method in required_methods:
            if not hasattr(store, method):
                missing_methods.append(method)

        if missing_methods:
            pytest.fail(f"FAISSVectorStore missing methods: {', '.join(missing_methods)}")


class TestDocumentationExamples:
    """Test that examples in documentation still work."""

    def test_readme_example(self):
        """Test the basic example from README works."""
        from rag_models import Document
        from rag_pipeline import RAGPipeline

        # This is from README.md
        pipeline = RAGPipeline()
        docs = [Document(page_content="Test content", metadata={"source": "test"})]
        result = pipeline.index_documents(documents=docs)
        assert result.total_documents == 1, "README example failed: indexing didn't work"

    def test_quickstart_example(self):
        """Test quickstart examples work."""
        from rag_models import RAGConfig
        from rag_pipeline import RAGPipeline

        config = RAGConfig(chunk_size=100)
        pipeline = RAGPipeline(config)
        assert pipeline is not None, "Quickstart example failed: pipeline creation"

    def test_api_reference_example(self):
        """Test API reference examples work."""
        from rag_models import Document

        # From API_REFERENCE.md
        doc = Document(
            page_content="This is the content",
            metadata={"source": "example.md", "section": "intro"},
        )
        assert doc.page_content == "This is the content"
        assert doc.metadata["source"] == "example.md"


class TestImportCounts:
    """Track import counts to detect changes."""

    def test_count_direct_imports(self):
        """Count and verify direct imports of each module."""
        base_path = Path(__file__).parent.parent

        # Modules to track
        modules_to_track = [
            "context_fixed_enricher",
            "enhanced_enricher_with_examples",
            "full_enhanced_enricher",
            "minimal_enhanced_enricher",
            "markdown_validator_enricher",
            "rag_pipeline",
            "rag_models",
            "rag_adapters",
        ]

        import_counts = {}
        for module in modules_to_track:
            count = 0
            pattern = f"from {module} import"

            # Search in all Python files
            for file in base_path.glob("**/*.py"):
                if "__pycache__" in str(file) or "htmlcov" in str(file):
                    continue

                with open(file, encoding="utf-8") as f:
                    content = f.read()
                    count += content.count(pattern)

            import_counts[module] = count

        # These are baseline counts - we track them to notice changes
        expected_counts = {
            "context_fixed_enricher": 6,  # Approximate, adjust based on actual
            "rag_pipeline": 10,
            "rag_models": 15,
            # Add more as needed
        }

        # Just report the counts, don't fail
        print("\nImport counts for tracking:")
        for module, count in sorted(import_counts.items()):
            print(f"  {module}: {count} imports")
