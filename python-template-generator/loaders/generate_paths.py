#!/usr/bin/env python3
"""Generate static paths dataclass for the loaders module using PTOOL."""

import sys
from pathlib import Path

# Add PTOOL src to path
ptool_src = Path(__file__).parent.parent / "PTOOL" / "src"
sys.path.insert(0, str(ptool_src))

from project_paths.get_paths import write_dataclass_file, generate_static_model_text
from project_paths.builder import build_field_definitions, get_paths_from_pyproject
from project_paths.model import ProjectPaths


def generate_loaders_paths():
    """Generate static paths dataclass for the loaders module."""
    print("=" * 60)
    print("Generating Paths for Loaders Module")
    print("=" * 60)
    
    # Create ProjectPaths instance to test current configuration
    paths = ProjectPaths()
    
    print("\n1. Current ProjectPaths fields (from pyproject.toml):")
    print("-" * 30)
    for field_name, field_value in paths.model_dump().items():
        if "loaders" in field_name:
            print(f"  {field_name}: {field_value}")
    
    print("\n2. Generating static model text...")
    print("-" * 30)
    static_text = generate_static_model_text()
    
    # Check if loaders paths are included
    loaders_paths_found = [line for line in static_text.split('\n') if 'loaders' in line]
    print(f"Found {len(loaders_paths_found)} loaders-related paths")
    for path_line in loaders_paths_found[:5]:  # Show first 5
        print(f"  {path_line.strip()}")
    if len(loaders_paths_found) > 5:
        print(f"  ... and {len(loaders_paths_found) - 5} more")
    
    # Write the static dataclass file
    output_path = Path(__file__).parent / "project_paths.py"
    print(f"\n3. Writing static dataclass to: {output_path}")
    print("-" * 30)
    
    try:
        write_dataclass_file(output_path)
        print(f"✅ Successfully generated {output_path}")
        
        # Verify the generated file
        with open(output_path, 'r') as f:
            content = f.read()
        
        # Count loaders-specific paths
        loaders_count = content.count('loaders')
        print(f"\n4. Verification:")
        print("-" * 30)
        print(f"  Total lines: {len(content.splitlines())}")
        print(f"  Loaders references: {loaders_count}")
        print(f"  File size: {len(content)} bytes")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error generating paths: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = generate_loaders_paths()
    if result:
        print(f"\n✅ Path generation complete! Use 'from project_paths import ProjectPaths' to access paths.")
    else:
        print("\n❌ Path generation failed!")
        sys.exit(1)