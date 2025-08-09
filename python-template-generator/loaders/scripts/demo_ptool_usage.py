#!/usr/bin/env python3
"""Demonstrate PTOOL usage in the loaders module.

This script shows how PTOOL enables running scripts from any directory
with type-safe, validated paths.
"""

from pathlib import Path
from project_paths import create_project_paths_auto, find_project_root

def demonstrate_ptool_features():
    """Show various PTOOL features for the loaders module."""
    
    print("=" * 60)
    print("🚀 PTOOL Demo for Loaders Module")
    print("=" * 60)
    
    # 1. Auto-discovery finds project from anywhere
    print("\n1️⃣ Auto-discovery")
    print("-" * 40)
    
    root = find_project_root()
    print(f"Found project root: {root}")
    print(f"Running from: {Path.cwd()}")
    
    # 2. Create paths with auto-discovery
    print("\n2️⃣ Type-safe Paths")
    print("-" * 40)
    
    paths = create_project_paths_auto()
    
    # Access loaders-specific paths
    if hasattr(paths, 'loaders_dir'):
        print(f"✓ Loaders directory: {paths.loaders_dir}")
    
    if hasattr(paths, 'loaders_tests'):
        print(f"✓ Tests directory: {paths.loaders_tests}")
        
    if hasattr(paths, 'loaders_enrichers'):
        print(f"✓ Enrichers: {paths.loaders_enrichers}")
        
    if hasattr(paths, 'loaders_docs'):
        print(f"✓ Documentation: {paths.loaders_docs}")
    
    # 3. Check if paths exist
    print("\n3️⃣ Path Validation")
    print("-" * 40)
    
    paths_to_check = [
        ('loaders_dir', 'Main loaders directory'),
        ('loaders_chunker', 'Chunker module'),
        ('loaders_enrichers', 'Enrichers module'),
        ('loaders_vector_store', 'Vector store module'),
        ('loaders_tests', 'Tests directory'),
    ]
    
    for attr_name, description in paths_to_check:
        if hasattr(paths, attr_name):
            path = getattr(paths, attr_name)
            exists = "✅" if Path(path).exists() else "❌"
            print(f"{exists} {description}: {path}")
    
    # 4. Benefits demonstration
    print("\n4️⃣ Benefits")
    print("-" * 40)
    
    print("✨ Run this script from ANY directory:")
    print("   - From project root")
    print("   - From loaders/")
    print("   - From tests/")
    print("   - From a temp directory")
    print("\n✨ All paths are:")
    print("   - Type-safe (IDE autocomplete)")
    print("   - Validated at startup")
    print("   - Consistent across the project")
    
    # 5. Integration with tests
    print("\n5️⃣ Test Integration")
    print("-" * 40)
    
    print("Tests can now:")
    print("✓ Run from any directory")
    print("✓ Use validated fixture paths")
    print("✓ No more sys.path hacks")
    print("✓ Clean imports everywhere")
    
    # 6. Script usage
    print("\n6️⃣ Script Usage")
    print("-" * 40)
    
    print("Example: Processing all markdown files")
    if hasattr(paths, 'loaders_docs'):
        docs_path = Path(paths.loaders_docs)
        if docs_path.exists():
            md_files = list(docs_path.glob('**/*.md'))
            print(f"Found {len(md_files)} markdown files in docs")
            
            # Show first few
            for md_file in md_files[:3]:
                rel_path = md_file.relative_to(docs_path)
                print(f"  - {rel_path}")
    
    print("\n" + "=" * 60)
    print("✅ PTOOL Integration Complete!")
    print("\nThe loaders module now has:")
    print("• Type-safe path management")
    print("• Auto-discovery from any directory")
    print("• Validated paths at startup")
    print("• Clean, maintainable code")
    

def show_import_examples():
    """Show how to import loaders modules from anywhere."""
    
    print("\n" + "=" * 60)
    print("📦 Import Examples")
    print("=" * 60)
    
    print("\nBefore PTOOL (fragile):")
    print("```python")
    print("import sys")
    print("from pathlib import Path")
    print("sys.path.insert(0, str(Path(__file__).parent.parent))")
    print("from enrichers.markdown_validator import MarkdownDocEnricher")
    print("```")
    
    print("\nWith PTOOL (robust):")
    print("```python")
    print("from project_paths import create_project_paths_auto")
    print("paths = create_project_paths_auto()")
    print("")
    print("# Add to path if needed")
    print("import sys")
    print("sys.path.insert(0, str(paths.loaders_dir))")
    print("from enrichers.markdown_validator import MarkdownDocEnricher")
    print("```")
    
    print("\nOr use the loaders.paths module:")
    print("```python")
    print("from python_template_generator.loaders.paths import get_paths")
    print("paths = get_paths()")
    print("# All paths available as attributes")
    print("```")


if __name__ == "__main__":
    try:
        demonstrate_ptool_features()
        show_import_examples()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Make sure you have:")
        print("1. PTOOL installed (pip install -e /path/to/PTOOL)")
        print("2. pyproject.toml with [tool.project_paths] configuration")
        print("3. Run from within the project directory tree")