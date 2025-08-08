#!/usr/bin/env python3
"""
Chain-of-Thought Bundle Validator

Validates the integrity and completeness of a CoT specification bundle.
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
from datetime import datetime
import subprocess


class BundleValidator:
    """Validates CoT specification bundles."""
    
    def __init__(self, bundle_path: Path):
        self.bundle_path = bundle_path
        self.bundle_dir = bundle_path.parent
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        
    def validate(self) -> bool:
        """Run all validation checks."""
        print(f"🔍 Validating bundle: {self.bundle_path}")
        print("=" * 60)
        
        # Load bundle manifest
        try:
            with open(self.bundle_path, 'r') as f:
                self.bundle = json.load(f)
        except Exception as e:
            self.errors.append(f"Failed to load bundle: {e}")
            return False
            
        # Run validation steps
        self._validate_schema()
        self._validate_files_exist()
        self._validate_file_hashes()
        self._validate_versions()
        self._validate_json_syntax()
        self._validate_cross_references()
        self._validate_gpg_signature()
        
        # Report results
        self._report_results()
        
        return len(self.errors) == 0
        
    def _validate_schema(self):
        """Validate bundle against its schema."""
        self.info.append("✓ Checking bundle schema compliance")
        
        required_fields = ["$schema", "name", "version", "bundle", "dependencies"]
        for field in required_fields:
            if field not in self.bundle:
                self.errors.append(f"Missing required field: {field}")
                
    def _validate_files_exist(self):
        """Check all referenced files exist."""
        self.info.append("✓ Checking file existence")
        
        for category in ["core", "rfcs", "supporting"]:
            if category not in self.bundle.get("bundle", {}):
                continue
                
            for item_name, item_data in self.bundle["bundle"][category].items():
                file_path = self.bundle_dir / item_data["file"]
                if not file_path.exists():
                    self.errors.append(f"File not found: {item_data['file']}")
                else:
                    self.info.append(f"  ✓ Found: {item_data['file']}")
                    
    def _validate_file_hashes(self):
        """Validate file integrity using SHA256."""
        self.info.append("✓ Validating file hashes")
        
        for category in ["core", "rfcs", "supporting"]:
            if category not in self.bundle.get("bundle", {}):
                continue
                
            for item_name, item_data in self.bundle["bundle"][category].items():
                file_path = self.bundle_dir / item_data["file"]
                if not file_path.exists():
                    continue
                    
                # Calculate actual hash
                actual_hash = self._calculate_hash(file_path)
                expected_hash = item_data.get("hash", "")
                
                if "[pending]" in expected_hash:
                    self.warnings.append(f"Hash pending for: {item_data['file']}")
                elif expected_hash and actual_hash != expected_hash:
                    self.errors.append(
                        f"Hash mismatch for {item_data['file']}: "
                        f"expected {expected_hash}, got {actual_hash}"
                    )
                    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return f"sha256:{sha256_hash.hexdigest()}"
        
    def _validate_versions(self):
        """Validate version consistency."""
        self.info.append("✓ Checking version consistency")
        
        bundle_version = self.bundle.get("version")
        
        # Check core specification version matches
        spec_version = self.bundle.get("bundle", {}).get("core", {}).get("specification", {}).get("version")
        if spec_version != bundle_version:
            self.warnings.append(
                f"Version mismatch: bundle {bundle_version} vs spec {spec_version}"
            )
            
    def _validate_json_syntax(self):
        """Validate JSON files are properly formatted."""
        self.info.append("✓ Validating JSON syntax")
        
        json_files = [
            self.bundle_dir / "COT_RUNTIME_CONTRACT.json",
            self.bundle_path
        ]
        
        for json_file in json_files:
            if json_file.exists():
                try:
                    with open(json_file, 'r') as f:
                        json.load(f)
                    self.info.append(f"  ✓ Valid JSON: {json_file.name}")
                except json.JSONDecodeError as e:
                    self.errors.append(f"Invalid JSON in {json_file.name}: {e}")
                    
    def _validate_cross_references(self):
        """Validate cross-references between documents."""
        self.info.append("✓ Checking cross-references")
        
        # Check if RFCs referenced in CHAIN_OF_THOUGHT.md exist
        chain_of_thought = self.bundle_dir / "CHAIN_OF_THOUGHT.md"
        if chain_of_thought.exists():
            content = chain_of_thought.read_text()
            
            # Check RFC references
            if "RFC-001" in content:
                rfc_001 = self.bundle_dir / "RFC-001_CoT_Applicability.md"
                if not rfc_001.exists():
                    self.errors.append("RFC-001 referenced but not found")
                    
    def _validate_gpg_signature(self):
        """Validate GPG signature if present."""
        self.info.append("✓ Checking GPG signature")
        
        sig_file = self.bundle_path.with_suffix('.json.sig')
        if sig_file.exists():
            try:
                result = subprocess.run(
                    ["gpg", "--verify", str(sig_file), str(self.bundle_path)],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.info.append("  ✓ GPG signature valid")
                else:
                    self.errors.append(f"GPG signature invalid: {result.stderr}")
            except FileNotFoundError:
                self.warnings.append("GPG not installed, skipping signature verification")
        else:
            self.warnings.append("No GPG signature file found")
            
    def _report_results(self):
        """Print validation report."""
        print("\n📊 Validation Report")
        print("=" * 60)
        
        if self.info:
            print("\n✅ Info:")
            for msg in self.info:
                print(f"  {msg}")
                
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for msg in self.warnings:
                print(f"  - {msg}")
                
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for msg in self.errors:
                print(f"  - {msg}")
        else:
            print("\n✅ All validations passed!")
            
        print("\n" + "=" * 60)
        print(f"Summary: {len(self.errors)} errors, {len(self.warnings)} warnings")
        
    def generate_report_dict(self) -> Dict:
        """Generate validation report as a dictionary."""
        return {
            "metadata": {
                "bundle_path": str(self.bundle_path),
                "validation_timestamp": datetime.now().isoformat(),
                "validator_version": "2.0.0",
                "bundle_version": self.bundle.get("version", "unknown")
            },
            "results": {
                "success": len(self.errors) == 0,
                "error_count": len(self.errors),
                "warning_count": len(self.warnings),
                "info_count": len(self.info)
            },
            "details": {
                "info": self.info,
                "warnings": self.warnings,
                "errors": self.errors
            },
            "summary": {
                "message": "All validations passed!" if len(self.errors) == 0 else f"{len(self.errors)} validation errors found",
                "recommendation": "Bundle is valid and ready for use" if len(self.errors) == 0 else "Fix errors before using bundle"
            }
        }
        

def generate_hashes(bundle_path: Path):
    """Generate hashes for all files in bundle."""
    print("🔐 Generating file hashes...")
    
    bundle_dir = bundle_path.parent
    with open(bundle_path, 'r') as f:
        bundle = json.load(f)
        
    # Update hashes
    for category in ["core", "rfcs", "supporting"]:
        if category not in bundle.get("bundle", {}):
            continue
            
        for item_name, item_data in bundle["bundle"][category].items():
            file_path = bundle_dir / item_data["file"]
            if file_path.exists():
                validator = BundleValidator(bundle_path)
                hash_value = validator._calculate_hash(file_path)
                item_data["hash"] = hash_value
                print(f"  ✓ {item_data['file']}: {hash_value}")
                
    # Save updated bundle
    with open(bundle_path, 'w') as f:
        json.dump(bundle, f, indent=2)
    print("✓ Bundle updated with hashes")


def main():
    parser = argparse.ArgumentParser(
        description="Chain-of-Thought Bundle Validator - Validate CoT specification bundles",
        epilog="Examples:\n"
               "  %(prog)s bundle.json                    # Validate bundle\n"
               "  %(prog)s bundle.json --generate-hashes  # Update hashes\n"
               "  %(prog)s bundle.json --verify-trace trace.md  # Validate trace\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "bundle",
        type=Path,
        help="Path to chain_of_thought.bundle.json"
    )
    
    parser.add_argument(
        "--generate-hashes",
        action="store_true",
        help="Generate and update file hashes in bundle"
    )
    
    parser.add_argument(
        "--verify-trace",
        type=Path,
        help="Validate a specific reasoning trace against the bundle"
    )
    
    parser.add_argument(
        "--check-signature",
        action="store_true",
        help="Verify GPG signature (requires .sig file)"
    )
    
    parser.add_argument(
        "--output-format",
        choices=["text", "json", "junit"],
        default="text",
        help="Output format for validation results"
    )
    
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings (not just errors)"
    )
    
    parser.add_argument(
        "--sign",
        action="store_true",
        help="Sign the validation report with GPG"
    )
    
    parser.add_argument(
        "--generate-signed-report",
        type=Path,
        help="Generate a signed validation report file"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0 (CoT v7.0.0)"
    )
    
    args = parser.parse_args()
    
    if not args.bundle.exists():
        print(f"❌ Bundle file not found: {args.bundle}")
        sys.exit(1)
        
    if args.generate_hashes:
        generate_hashes(args.bundle)
        
    # Run validation
    validator = BundleValidator(args.bundle)
    success = validator.validate()
    
    # Generate signed report if requested
    if args.sign or args.generate_signed_report:
        report_data = validator.generate_report_dict()
        report_json = json.dumps(report_data, indent=2)
        
        if args.generate_signed_report:
            # Write report to file
            report_path = args.generate_signed_report
            report_path.write_text(report_json)
            print(f"\n📄 Report written to: {report_path}")
            
            if args.sign:
                # Sign the report file
                sig_path = report_path.with_suffix(report_path.suffix + '.sig')
                try:
                    result = subprocess.run(
                        ["gpg", "--detach-sign", "--armor", str(report_path)],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print(f"✅ Report signed: {sig_path}")
                        # Add metadata to signature file
                        sig_content = sig_path.read_text()
                        metadata_lines = [
                            "-----BEGIN PGP SIGNATURE-----",
                            "Comment: sig_algo GPG+SHA256",
                            f"Comment: sig_issued_at {datetime.now().isoformat()}",
                            "Comment: CoT Validation Report Signature",
                            f"Comment: Bundle Version {report_data['metadata']['bundle_version']}",
                            f"Comment: Validator Version {report_data['metadata']['validator_version']}",
                            ""
                        ]
                        sig_lines = sig_content.split('\n')
                        new_sig = '\n'.join(metadata_lines + sig_lines[1:])
                        sig_path.write_text(new_sig)
                    else:
                        print(f"❌ Failed to sign report: {result.stderr}")
                except FileNotFoundError:
                    print("⚠️  GPG not installed, cannot sign report")
        
        elif args.sign:
            # Print signed report to stdout
            print("\n📄 Signed Validation Report")
            print("=" * 60)
            print(report_json)
            print("=" * 60)
            print("\n🔏 Generating GPG signature...")
            
            # Create temporary file for signing
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                tmp.write(report_json)
                tmp_path = tmp.name
            
            try:
                # Sign the temporary file
                result = subprocess.run(
                    ["gpg", "--detach-sign", "--armor", tmp_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    sig_path = Path(tmp_path + ".asc")
                    if sig_path.exists():
                        print("\n-----BEGIN PGP SIGNATURE-----")
                        print("Comment: sig_algo GPG+SHA256")
                        print(f"Comment: sig_issued_at {datetime.now().isoformat()}")
                        print("Comment: CoT Validation Report Signature")
                        sig_content = sig_path.read_text()
                        # Skip the first line (BEGIN PGP SIGNATURE)
                        print('\n'.join(sig_content.split('\n')[1:]))
                        sig_path.unlink()
                else:
                    print(f"❌ Failed to sign report: {result.stderr}")
            except FileNotFoundError:
                print("⚠️  GPG not installed, cannot sign report")
            finally:
                # Clean up temporary file
                Path(tmp_path).unlink(missing_ok=True)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()