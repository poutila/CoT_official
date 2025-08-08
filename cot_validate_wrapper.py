#!/usr/bin/env python3
"""
CLI wrapper for cot-validate command.

This provides an explicit wrapper module for the validation CLI.
"""

import sys
from validate_bundle import main

if __name__ == "__main__":
    sys.exit(main())