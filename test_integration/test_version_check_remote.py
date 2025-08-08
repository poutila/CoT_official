#!/usr/bin/env python3
"""
Integration test for cot-version-check with simulated remote registry.

Tests version checking against a mock registry file to simulate remote behavior.
"""

import json
import unittest
import tempfile
import subprocess
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import http.server
import threading
import time


class MockRegistryServer:
    """Simple HTTP server to serve mock registry data."""
    
    def __init__(self, registry_data, port=0):
        self.registry_data = registry_data
        self.port = port
        self.server = None
        self.thread = None
        
    def start(self):
        """Start the mock server."""
        handler = self._create_handler()
        self.server = http.server.HTTPServer(('localhost', self.port), handler)
        self.port = self.server.server_port
        
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        
        # Give server time to start
        time.sleep(0.1)
        return f"http://localhost:{self.port}/registry.json"
        
    def stop(self):
        """Stop the mock server."""
        if self.server:
            self.server.shutdown()
            self.thread.join()
            
    def _create_handler(self):
        """Create request handler with registry data."""
        registry_json = json.dumps(self.registry_data)
        
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/registry.json':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(registry_json.encode())
                else:
                    self.send_response(404)
                    self.end_headers()
                    
            def log_message(self, format, *args):
                # Suppress log messages
                pass
                
        return Handler


class TestVersionCheckRemote(unittest.TestCase):
    """Test cot-version-check with simulated remote registry."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create mock registry data
        self.mock_registry = {
            "$schema": "https://cot-standard.org/schemas/registry/v1.0.0.json",
            "registry_version": "1.0.0",
            "last_updated": "2024-01-26T12:00:00Z",
            "latest": {
                "version": "7.0.0",
                "released": "2024-01-26",
                "stability": "stable",
                "download_url": "https://github.com/cot-standard/spec/releases/tag/v7.0.0",
                "release_notes_url": "CHANGELOG.md"
            },
            "versions": [
                {
                    "version": "7.0.0",
                    "released": "2024-01-26",
                    "stability": "stable",
                    "min_validator": "2.0.0"
                },
                {
                    "version": "6.0.0",
                    "released": "2024-01-20",
                    "stability": "stable",
                    "min_validator": "1.2.0"
                }
            ]
        }
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_version_check_from_remote_url(self):
        """Test version check fetches from remote URL."""
        # Start mock server
        server = MockRegistryServer(self.mock_registry)
        registry_url = server.start()
        
        try:
            # Create a test script that simulates cot-version-check
            version_check_script = f"""#!/bin/bash
# Mock cot-version-check script
REGISTRY_URL="{registry_url}"

# Fetch registry
if command -v curl >/dev/null 2>&1; then
    REGISTRY_DATA=$(curl -s "$REGISTRY_URL")
elif command -v wget >/dev/null 2>&1; then
    REGISTRY_DATA=$(wget -qO- "$REGISTRY_URL")
else
    echo "Error: Neither curl nor wget available"
    exit 1
fi

# Parse latest version
LATEST_VERSION=$(echo "$REGISTRY_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['latest']['version'])")
echo "Latest CoT version: $LATEST_VERSION"

# Check if update available
CURRENT_VERSION="${{1:-6.0.0}}"
if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
    echo "Update available: $CURRENT_VERSION -> $LATEST_VERSION"
    exit 0
else
    echo "Already on latest version: $LATEST_VERSION"
    exit 0
fi
"""
            
            # Write script
            script_path = Path(self.test_dir) / "cot-version-check.sh"
            script_path.write_text(version_check_script)
            script_path.chmod(0o755)
            
            # Run version check
            result = subprocess.run(
                [str(script_path), "6.0.0"],
                capture_output=True,
                text=True
            )
            
            # Verify output
            self.assertEqual(result.returncode, 0)
            self.assertIn("Latest CoT version: 7.0.0", result.stdout)
            self.assertIn("Update available: 6.0.0 -> 7.0.0", result.stdout)
            
        finally:
            server.stop()
            
    def test_version_check_fallback_to_local(self):
        """Test version check falls back to local file when remote fails."""
        # Create local registry file
        local_registry_path = Path(self.test_dir) / "registry.json"
        local_registry_path.write_text(json.dumps(self.mock_registry))
        
        # Create version check script with fallback
        version_check_script = f"""#!/bin/bash
# Mock cot-version-check with fallback
REGISTRY_URL="http://localhost:99999/registry.json"  # Invalid URL
LOCAL_REGISTRY="{local_registry_path}"

# Try remote first
if curl -s --connect-timeout 1 "$REGISTRY_URL" >/dev/null 2>&1; then
    REGISTRY_DATA=$(curl -s "$REGISTRY_URL")
    echo "Using remote registry"
else
    # Fallback to local
    if [ -f "$LOCAL_REGISTRY" ]; then
        REGISTRY_DATA=$(cat "$LOCAL_REGISTRY")
        echo "Using local registry (fallback)"
    else
        echo "Error: No registry available"
        exit 1
    fi
fi

# Parse version
LATEST_VERSION=$(echo "$REGISTRY_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['latest']['version'])")
echo "Latest CoT version: $LATEST_VERSION"
"""
        
        # Write script
        script_path = Path(self.test_dir) / "cot-version-check.sh"
        script_path.write_text(version_check_script)
        script_path.chmod(0o755)
        
        # Run version check
        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True
        )
        
        # Verify fallback worked
        self.assertEqual(result.returncode, 0)
        self.assertIn("Using local registry (fallback)", result.stdout)
        self.assertIn("Latest CoT version: 7.0.0", result.stdout)
        
    def test_version_check_with_multiple_sources(self):
        """Test version check with primary, mirror, and local sources."""
        # Create local registry
        local_registry_path = Path(self.test_dir) / "registry.json"
        local_registry_path.write_text(json.dumps(self.mock_registry))
        
        # Start mock server as mirror
        server = MockRegistryServer(self.mock_registry)
        mirror_url = server.start()
        
        try:
            # Create comprehensive version check script
            version_check_script = f"""#!/bin/bash
# Mock cot-version-check with multiple sources
PRIMARY_URL="http://localhost:99999/registry.json"  # Will fail
MIRROR_URL="{mirror_url}"
LOCAL_REGISTRY="{local_registry_path}"

echo "Checking CoT version from multiple sources..."

# Try primary
if curl -s --connect-timeout 1 "$PRIMARY_URL" >/dev/null 2>&1; then
    REGISTRY_DATA=$(curl -s "$PRIMARY_URL")
    SOURCE="primary"
# Try mirror
elif curl -s --connect-timeout 1 "$MIRROR_URL" >/dev/null 2>&1; then
    REGISTRY_DATA=$(curl -s "$MIRROR_URL")
    SOURCE="mirror"
# Try local
elif [ -f "$LOCAL_REGISTRY" ]; then
    REGISTRY_DATA=$(cat "$LOCAL_REGISTRY")
    SOURCE="local"
else
    echo "Error: No registry source available"
    exit 1
fi

echo "Source: $SOURCE"

# Parse and display info
LATEST_VERSION=$(echo "$REGISTRY_DATA" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['latest']['version'])")
RELEASE_DATE=$(echo "$REGISTRY_DATA" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['latest']['released'])")
STABILITY=$(echo "$REGISTRY_DATA" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['latest']['stability'])")

echo "Latest version: $LATEST_VERSION (released $RELEASE_DATE, $STABILITY)"
"""
            
            # Write script
            script_path = Path(self.test_dir) / "cot-version-check.sh"
            script_path.write_text(version_check_script)
            script_path.chmod(0o755)
            
            # Run version check
            result = subprocess.run(
                [str(script_path)],
                capture_output=True,
                text=True
            )
            
            # Verify mirror was used (primary failed)
            self.assertEqual(result.returncode, 0)
            self.assertIn("Source: mirror", result.stdout)
            self.assertIn("Latest version: 7.0.0 (released 2024-01-26, stable)", result.stdout)
            
        finally:
            server.stop()
            
    def test_python_version_check_module(self):
        """Test Python module for version checking."""
        # Create Python version check module
        version_check_py = '''#!/usr/bin/env python3
"""Mock cot_version_check.py module."""

import json
import urllib.request
import urllib.error
import sys
from pathlib import Path


def fetch_registry(url):
    """Fetch registry from URL."""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError):
        return None


def check_version(current_version=None):
    """Check for CoT version updates."""
    # Try remote sources
    sources = [
        "https://cot-standard.org/registry.json",
        "https://raw.githubusercontent.com/cot-standard/spec/main/registry.json",
        "./registry.json"  # Local fallback
    ]
    
    registry_data = None
    source_used = None
    
    for source in sources:
        if source.startswith("http"):
            data = fetch_registry(source)
            if data:
                registry_data = data
                source_used = source
                break
        else:
            # Local file
            path = Path(source)
            if path.exists():
                with open(path) as f:
                    registry_data = json.load(f)
                source_used = "local file"
                break
    
    if not registry_data:
        print("Error: Could not fetch registry from any source")
        return 1
        
    latest = registry_data["latest"]["version"]
    current = current_version or "unknown"
    
    print(f"Registry source: {source_used}")
    print(f"Current version: {current}")
    print(f"Latest version: {latest}")
    
    if current != latest and current != "unknown":
        print(f"Update available: {current} -> {latest}")
        print(f"Release notes: {registry_data['latest'].get('release_notes_url', 'N/A')}")
    
    return 0


if __name__ == "__main__":
    current = sys.argv[1] if len(sys.argv) > 1 else None
    sys.exit(check_version(current))
'''
        
        # Write Python module
        py_path = Path(self.test_dir) / "cot_version_check.py"
        py_path.write_text(version_check_py)
        
        # Create local registry for testing
        local_registry_path = Path(self.test_dir) / "registry.json"
        local_registry_path.write_text(json.dumps(self.mock_registry))
        
        # Run Python version check
        result = subprocess.run(
            [sys.executable, str(py_path), "6.0.0"],
            capture_output=True,
            text=True,
            cwd=self.test_dir
        )
        
        # Verify output
        self.assertEqual(result.returncode, 0)
        self.assertIn("Registry source: local file", result.stdout)
        self.assertIn("Current version: 6.0.0", result.stdout)
        self.assertIn("Latest version: 7.0.0", result.stdout)
        self.assertIn("Update available: 6.0.0 -> 7.0.0", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)