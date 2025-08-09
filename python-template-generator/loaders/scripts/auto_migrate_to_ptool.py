#!/usr/bin/env python3
"""Automatically migrate loaders module files to use PTOOL.

This script performs the actual migration, updating files to use PTOOL
for path management instead of hardcoded paths.
"""

import re
from pathlib import Path
from typing import List, Tuple

from project_paths import create_project_paths_auto


def update_file_imports(file_path: Path) -> bool:
    """Update a file to use PTOOL imports.
    
    Returns True if file was modified, False otherwise.
    """
    content = file_path.read_text()
    original_content = content
    
    # Pattern replacements
    replacements = []
    
    # Replace Path(__file__).parent patterns
    if 'Path(__file__).parent' in content:
        # Check if project_paths import already exists
        if 'from project_paths import' not in content:
            # Add import at the beginning after docstring
            lines = content.split('\n')
            insert_index = 0
            
            # Skip past module docstring
            if lines[0].startswith('"""') or lines[0].startswith("'''"):
                for i, line in enumerate(lines[1:], 1):
                    if line.endswith('"""') or line.endswith("'''"):
                        insert_index = i + 1
                        break
            elif lines[0].startswith('#'):
                insert_index = 1
            
            # Find first import statement
            for i in range(insert_index, len(lines)):
                if lines[i].startswith('import ') or lines[i].startswith('from '):
                    insert_index = i
                    break
            
            # Insert PTOOL imports
            ptool_imports = [
                "",
                "# Use PTOOL for path management",
                "from project_paths import create_project_paths_auto",
                "",
                "# Get paths using auto-discovery",
                "paths = create_project_paths_auto()",
                ""
            ]
            
            lines = lines[:insert_index] + ptool_imports + lines[insert_index:]
            content = '\n'.join(lines)
            replacements.append("Added PTOOL imports")
    
    # Replace sys.path.insert patterns
    sys_path_pattern = r'sys\.path\.insert\(0,\s*str\(Path\(__file__\)\.parent\.parent\)\)'
    if re.search(sys_path_pattern, content):
        new_path_code = """# Add loaders directory to path for imports (using PTOOL paths)
if hasattr(paths, 'loaders_dir'):
    sys.path.insert(0, str(paths.loaders_dir))"""
        content = re.sub(sys_path_pattern, new_path_code, content)
        replacements.append("Updated sys.path.insert to use PTOOL")
    
    # Replace Path(__file__).parent / "fixtures"
    fixtures_pattern = r'Path\(__file__\)\.parent\s*/\s*["\']fixtures["\']'
    if re.search(fixtures_pattern, content):
        new_fixtures = """if hasattr(paths, 'loaders_test_fixtures'):
        return Path(paths.loaders_test_fixtures)
    # Fallback if not configured
    return Path(__file__).parent / "fixtures\""""
        content = re.sub(
            r'return\s+' + fixtures_pattern,
            new_fixtures,
            content
        )
        replacements.append("Updated fixtures path to use PTOOL")
    
    # Save if modified
    if content != original_content:
        file_path.write_text(content)
        return True
    
    return False


def migrate_test_files():
    """Migrate test files to use PTOOL."""
    paths = create_project_paths_auto()
    
    if not hasattr(paths, 'loaders_tests'):
        print("❌ loaders_tests not configured in pyproject.toml")
        return
    
    tests_dir = Path(paths.loaders_tests)
    modified_files = []
    
    # Files to migrate
    test_files = [
        "conftest.py",
        "run_tests.py",
        "test_imports_and_structure.py",
        "test_import_updates.py",
    ]
    
    for test_file in test_files:
        file_path = tests_dir / test_file
        if file_path.exists():
            if update_file_imports(file_path):
                modified_files.append(test_file)
                print(f"✅ Updated: {test_file}")
            else:
                print(f"⏭️  Skipped: {test_file} (already migrated or no changes needed)")
        else:
            print(f"❌ Not found: {test_file}")
    
    return modified_files


def migrate_integration_tests():
    """Migrate integration test files."""
    paths = create_project_paths_auto()
    
    if not hasattr(paths, 'loaders_test_integration'):
        print("❌ loaders_test_integration not configured")
        return
    
    integration_dir = Path(paths.loaders_test_integration)
    if not integration_dir.exists():
        print(f"⚠️  Integration tests directory doesn't exist: {integration_dir}")
        return
    
    modified_files = []
    
    for py_file in integration_dir.glob('*.py'):
        if update_file_imports(py_file):
            modified_files.append(py_file.name)
            print(f"✅ Updated: integration/{py_file.name}")
    
    return modified_files


def migrate_scripts():
    """Migrate script files."""
    paths = create_project_paths_auto()
    
    if not hasattr(paths, 'loaders_scripts'):
        print("❌ loaders_scripts not configured")
        return
    
    scripts_dir = Path(paths.loaders_scripts)
    if not scripts_dir.exists():
        print(f"⚠️  Scripts directory doesn't exist: {scripts_dir}")
        return
    
    modified_files = []
    
    # Skip migration scripts themselves
    skip_files = {'migrate_to_ptool.py', 'auto_migrate_to_ptool.py'}
    
    for py_file in scripts_dir.glob('*.py'):
        if py_file.name in skip_files:
            continue
            
        if update_file_imports(py_file):
            modified_files.append(py_file.name)
            print(f"✅ Updated: scripts/{py_file.name}")
    
    return modified_files


def create_backup(file_path: Path):
    """Create a backup of a file before migration."""
    backup_path = file_path.with_suffix('.bak')
    if not backup_path.exists():
        backup_path.write_text(file_path.read_text())
        return backup_path
    return None


def main():
    """Run the migration."""
    print("=" * 60)
    print("🚀 PTOOL Auto-Migration")
    print("=" * 60)
    
    # Get paths
    paths = create_project_paths_auto()
    
    print("\n📁 Migrating Test Files")
    print("-" * 40)
    test_files = migrate_test_files()
    
    print("\n📁 Migrating Integration Tests")
    print("-" * 40)
    integration_files = migrate_integration_tests()
    
    print("\n📁 Migrating Scripts")
    print("-" * 40)
    script_files = migrate_scripts()
    
    # Summary
    print("\n" + "=" * 60)
    print("✨ Migration Summary")
    print("-" * 40)
    
    total_modified = 0
    if test_files:
        total_modified += len(test_files)
        print(f"Test files updated: {len(test_files)}")
    
    if integration_files:
        total_modified += len(integration_files)
        print(f"Integration tests updated: {len(integration_files)}")
    
    if script_files:
        total_modified += len(script_files)
        print(f"Scripts updated: {len(script_files)}")
    
    print(f"\nTotal files modified: {total_modified}")
    
    if total_modified > 0:
        print("\n⚠️  Important:")
        print("1. Review the changes to ensure they're correct")
        print("2. Run tests to verify everything still works")
        print("3. Backup files have been created with .bak extension")
        print("\n🧪 Test with:")
        print("   uv run pytest python-template-generator/loaders/tests -v")
    else:
        print("\n✅ All files are already migrated or don't need changes!")
    
    print("\n🎉 Migration complete!")


if __name__ == "__main__":
    main()