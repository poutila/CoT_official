#!/usr/bin/env python3
"""Simple test to find where the hang occurs."""

print("1. Starting test...")

import sys
from pathlib import Path

print("2. Imports done...")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
print("3. Path updated...")

print("4. Importing TokenCounter...")
from chunker.token_counter import TokenCounter

print("5. TokenCounter imported...")

print("6. Creating TokenCounter instance...")
counter = TokenCounter()
print("7. TokenCounter created!")

print("✅ Test complete - no hang!")
