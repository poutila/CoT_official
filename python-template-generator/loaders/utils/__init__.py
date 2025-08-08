"""Shared utilities."""
from .sluggify import *

# Backward compatibility
import sys
sys.modules['sluggify_util'] = sys.modules['utils.sluggify']