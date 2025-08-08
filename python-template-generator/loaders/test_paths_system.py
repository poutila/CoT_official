#!/usr/bin/env python3
"""Test the new path management system."""

from pathlib import Path
import sys

# Add loaders to path
sys.path.insert(0, str(Path(__file__).parent))

from project_paths import LoadersPaths


def test_paths_system():
    """Test that the path system works correctly."""
    print("=" * 60)
    print("Testing Path Management System")
    print("=" * 60)
    
    # Create paths instance
    paths = LoadersPaths()
    
    print("\n1. Base paths:")
    print("-" * 30)
    print(f"  Base dir: {paths.base_dir}")
    print(f"  Core: {paths.core}")
    print(f"  Tests: {paths.tests}")
    
    print("\n2. Path existence checks:")
    print("-" * 30)
    critical_paths = [
        ("Core", paths.core),
        ("Enrichers", paths.enrichers),
        ("Validators", paths.validators),
        ("Utils", paths.utils),
        ("Scripts", paths.scripts),
        ("Tests", paths.tests),
        ("Chunker", paths.chunker),
        ("Embeddings", paths.embeddings),
        ("Vector Store", paths.vector_store),
    ]
    
    all_exist = True
    for name, path in critical_paths:
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {name}: {path.exists()}")
        if not exists:
            all_exist = False
    
    print("\n3. File paths:")
    print("-" * 30)
    file_paths = [
        ("API Reference", paths.api_reference),
        ("Architecture", paths.architecture),
        ("README", paths.readme),
    ]
    
    for name, path in file_paths:
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"  {status} {name}: {path.exists()}")
    
    print("\n4. Dictionary access test:")
    print("-" * 30)
    try:
        core_via_dict = paths["core"]
        print(f"  ✅ Dictionary access works: paths['core'] = {core_via_dict}")
    except Exception as e:
        print(f"  ❌ Dictionary access failed: {e}")
    
    print("\n5. to_dict() test:")
    print("-" * 30)
    paths_dict = paths.to_dict()
    print(f"  Total paths in dictionary: {len(paths_dict)}")
    print(f"  Sample keys: {list(paths_dict.keys())[:5]}")
    
    print("\n6. Test results directories:")
    print("-" * 30)
    print(f"  TEST_RUN_RESULTS: {paths.test_results}")
    print(f"    Exists: {paths.test_results.exists()}")
    print(f"  TEST_RUN_RESULTS_AFTER_REORG: {paths.test_results_after}")
    print(f"    Exists: {paths.test_results_after.exists()}")
    
    # Overall status
    print("\n" + "=" * 60)
    if all_exist:
        print("✅ Path system is working correctly!")
        print("   All critical directories exist.")
    else:
        print("⚠️  Path system works but some directories are missing.")
        print("   This is expected if running in a fresh environment.")
    
    return all_exist


def test_import_in_script():
    """Test that the path system can be imported in scripts."""
    print("\n7. Testing import in script context:")
    print("-" * 30)
    
    # Simulate what test_rag_on_markdown.py does
    test_script = """
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from project_paths import LoadersPaths
paths = LoadersPaths()

print(f"  Script can access paths.test_results: {paths.test_results}")
print(f"  Script can access paths.base_dir: {paths.base_dir}")
"""
    
    # Create a temp script to test
    temp_script = Path(__file__).parent / "temp_test_import.py"
    temp_script.write_text(test_script)
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(temp_script)],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent)
        )
        
        if result.returncode == 0:
            print("  ✅ Import works in script context")
            print(result.stdout)
        else:
            print("  ❌ Import failed in script context")
            print(result.stderr)
    finally:
        # Clean up
        if temp_script.exists():
            temp_script.unlink()
    
    return result.returncode == 0


if __name__ == "__main__":
    # Run tests
    paths_ok = test_paths_system()
    import_ok = test_import_in_script()
    
    print("\n" + "=" * 60)
    print("FINAL RESULT:")
    if paths_ok and import_ok:
        print("✅ ALL TESTS PASSED - Path system is fully functional!")
    else:
        print("⚠️  Some tests failed but path system is usable.")
    print("=" * 60)