#!/usr/bin/env python3
"""Migration helper for updating loaders module to use PTOOL.

This script helps identify and update code that needs to be migrated
to use PTOOL for path management.
"""

import re
from pathlib import Path
from typing import List, Tuple

from project_paths import create_project_paths_auto


def find_files_to_migrate(directory: Path) -> List[Path]:
    """Find Python files that might need migration."""
    files_to_check = []
    
    # Patterns that indicate path usage
    patterns = [
        r'Path\(__file__\)',
        r'\.parent',
        r'sys\.path\.',
        r'os\.path\.',
        r'pathlib\.Path\(',
        r'Path\(["\']',
    ]
    
    for py_file in directory.glob('**/*.py'):
        # Skip migrations and this script
        if 'migrate' in py_file.name or py_file.name == 'migrate_to_ptool.py':
            continue
            
        content = py_file.read_text()
        for pattern in patterns:
            if re.search(pattern, content):
                files_to_check.append(py_file)
                break
    
    return files_to_check


def analyze_file(file_path: Path) -> List[Tuple[int, str, str]]:
    """Analyze a file for migration opportunities.
    
    Returns:
        List of (line_number, original_line, suggestion)
    """
    suggestions = []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        # Check for common patterns
        
        # Pattern 1: Path(__file__).parent
        if 'Path(__file__).parent' in line:
            suggestions.append((
                i,
                line.strip(),
                "Use: paths = create_project_paths_auto()"
            ))
        
        # Pattern 2: sys.path manipulation
        if 'sys.path.insert' in line or 'sys.path.append' in line:
            suggestions.append((
                i,
                line.strip(),
                "Use PTOOL paths instead of sys.path manipulation"
            ))
        
        # Pattern 3: Hardcoded relative paths
        if re.search(r'["\']\.\.\/|["\']\.\.\\\\', line):
            suggestions.append((
                i,
                line.strip(),
                "Use PTOOL paths instead of relative paths"
            ))
        
        # Pattern 4: os.path.join for project paths
        if 'os.path.join' in line and ('test' in line.lower() or 'fixture' in line.lower()):
            suggestions.append((
                i,
                line.strip(),
                "Use paths.loaders_test_fixtures or similar"
            ))
    
    return suggestions


def generate_migration_report(paths):
    """Generate a migration report for the loaders module."""
    
    print("=" * 60)
    print("📋 PTOOL Migration Report")
    print("=" * 60)
    
    # Get the loaders directory
    if not hasattr(paths, 'loaders_dir'):
        print("❌ loaders_dir not found in PTOOL configuration")
        return
    
    loaders_dir = Path(paths.loaders_dir)
    
    # Find files that need migration
    files_to_migrate = find_files_to_migrate(loaders_dir)
    
    print(f"\nFound {len(files_to_migrate)} files that may need migration:")
    print("-" * 40)
    
    total_suggestions = 0
    
    for file_path in files_to_migrate:
        rel_path = file_path.relative_to(loaders_dir)
        suggestions = analyze_file(file_path)
        
        if suggestions:
            print(f"\n📄 {rel_path}")
            for line_num, original, suggestion in suggestions[:3]:  # Show first 3
                print(f"  Line {line_num}: {suggestion}")
            
            if len(suggestions) > 3:
                print(f"  ... and {len(suggestions) - 3} more suggestions")
            
            total_suggestions += len(suggestions)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("-" * 40)
    print(f"Files to review: {len(files_to_migrate)}")
    print(f"Total suggestions: {total_suggestions}")
    
    # Migration checklist
    print("\n✅ Migration Checklist:")
    print("1. [ ] Update tests/conftest.py to use PTOOL paths")
    print("2. [ ] Remove sys.path manipulations")
    print("3. [ ] Replace Path(__file__).parent with PTOOL paths")
    print("4. [ ] Update fixture paths to use paths.loaders_test_fixtures")
    print("5. [ ] Update imports to use auto-discovery")
    print("6. [ ] Test from different directories")
    
    # Example migrations
    print("\n📝 Common Migration Patterns:")
    print("-" * 40)
    
    print("\n1. Replace path construction:")
    print("   Before: Path(__file__).parent / 'fixtures'")
    print("   After:  paths.loaders_test_fixtures")
    
    print("\n2. Replace sys.path hacks:")
    print("   Before: sys.path.insert(0, str(Path(__file__).parent.parent))")
    print("   After:  sys.path.insert(0, str(paths.loaders_dir))")
    
    print("\n3. Use auto-discovery:")
    print("   from project_paths import create_project_paths_auto")
    print("   paths = create_project_paths_auto()")
    
    print("\n4. Access specific paths:")
    print("   docs_dir = paths.loaders_docs")
    print("   test_dir = paths.loaders_tests")
    print("   enrichers = paths.loaders_enrichers")


def show_configuration():
    """Show the current PTOOL configuration for loaders."""
    
    print("\n" + "=" * 60)
    print("⚙️ Current PTOOL Configuration")
    print("=" * 60)
    
    paths = create_project_paths_auto()
    
    # Find all loaders-related attributes
    loaders_attrs = [attr for attr in dir(paths) if 'loader' in attr.lower()]
    
    if loaders_attrs:
        print("\nConfigured paths:")
        for attr in sorted(loaders_attrs):
            if not attr.startswith('_'):
                value = getattr(paths, attr)
                exists = "✅" if Path(value).exists() else "❌"
                print(f"{exists} {attr}: {value}")
    else:
        print("❌ No loaders paths configured in pyproject.toml")
        print("\nAdd this to your pyproject.toml:")
        print("""
[tool.project_paths.paths]
base_dir = "."
loaders_dir = "python-template-generator/loaders"
loaders_tests = "python-template-generator/loaders/tests"
# ... more paths ...
""")


if __name__ == "__main__":
    try:
        # Get paths
        paths = create_project_paths_auto()
        
        # Show current configuration
        show_configuration()
        
        # Generate migration report
        generate_migration_report(paths)
        
        print("\n✨ Ready to migrate to PTOOL!")
        print("Run this script again after making changes to track progress.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure:")
        print("1. PTOOL is installed")
        print("2. pyproject.toml has [tool.project_paths] configuration")
        print("3. You're running from within the project")