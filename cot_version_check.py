#!/usr/bin/env python3
"""
Python wrapper for cot-version-check functionality.

This provides the Python entry point for the version check CLI command.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Main entry point for cot-version-check command."""
    # Get the shell script path
    script_path = Path(__file__).parent / "cot-version-check.sh"
    
    if not script_path.exists():
        print(f"Error: Version check script not found at {script_path}")
        sys.exit(1)
    
    # Make sure it's executable
    script_path.chmod(0o755)
    
    # Pass all arguments to the shell script
    cmd = [str(script_path)] + sys.argv[1:]
    
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error running version check: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()