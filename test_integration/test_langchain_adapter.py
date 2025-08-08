#!/usr/bin/env python3
"""
Integration tests for LangChain CoT adapter

Tests the CoTReasoningTool to ensure it produces valid traces.
"""

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
import sys
import hashlib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "examples"))

from langchain_integration import CoTReasoningTool


class TestCoTReasoningTool(unittest.TestCase):
    """Test cases for CoT reasoning tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = CoTReasoningTool(cot_version="7.0.0")
        
    def test_risk_assessment_low(self):
        """Test low risk assessment."""
        risk = self.tool._assess_risk("update documentation")
        self.assertEqual(risk, "low")
        
    def test_risk_assessment_medium(self):
        """Test medium risk assessment."""
        risk = self.tool._assess_risk("refactor the user module")
        self.assertEqual(risk, "medium")
        
    def test_risk_assessment_high(self):
        """Test high risk assessment."""
        risk = self.tool._assess_risk("delete the authentication system")
        self.assertEqual(risk, "high")
        
    def test_trace_generation_structure(self):
        """Test that generated trace has required structure."""
        trace = self.tool._run(
            task="Update configuration file",
            context={"access_level": "full_file_access"}
        )
        
        # Check required sections
        required_sections = [
            "## 🧠 Reasoning Trace (Chain-of-Thought)",
            "```yaml",
            "schema: chain_of_thought/v7.0.0",
            "Risk Assessment:",
            "Evidence Collection:",
            "Analysis:",
            "Validation:",
            "Action:"
        ]
        
        for section in required_sections:
            self.assertIn(section, trace, f"Missing required section: {section}")
            
    def test_yaml_header_validity(self):
        """Test YAML header is valid."""
        trace = self.tool._run("Test task", {})
        
        # Extract YAML block
        yaml_start = trace.find("```yaml") + 7
        yaml_end = trace.find("```", yaml_start)
        yaml_content = trace[yaml_start:yaml_end]
        
        # Parse YAML (simplified check)
        self.assertIn("schema: chain_of_thought/v7.0.0", yaml_content)
        self.assertIn("validation: required", yaml_content)
        self.assertIn("runtime_contract: 2.0.0", yaml_content)
        
    def test_evidence_collection_format(self):
        """Test evidence collection format."""
        evidence = self.tool._gather_evidence("test task", {})
        
        self.assertIsInstance(evidence, list)
        self.assertGreater(len(evidence), 0)
        
        for item in evidence:
            # Check required fields
            self.assertIn("source", item)
            self.assertIn("quote", item)
            self.assertIn("relevance", item)
            self.assertIn("timestamp", item)
            self.assertIn("freshness", item)
            self.assertIn("freshness_score", item)
            
            # Check timestamp structure
            self.assertIn("created", item["timestamp"])
            self.assertIn("modified", item["timestamp"])
            self.assertIn("accessed", item["timestamp"])
            
    def test_validation_success(self):
        """Test trace validation succeeds for valid trace."""
        trace = self.tool._run("Valid task", {})
        result = self.tool._validate_trace(trace)
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)
        
    def test_validation_failure(self):
        """Test trace validation fails for invalid trace."""
        invalid_trace = "This is not a valid trace"
        result = self.tool._validate_trace(invalid_trace)
        
        self.assertFalse(result["valid"])
        self.assertGreater(len(result["errors"]), 0)
        
    def test_minimum_evidence_requirements(self):
        """Test minimum evidence requirements by risk level."""
        test_cases = [
            ("low", 1),
            ("medium", 2),
            ("high", 3),
            ("critical", 5)
        ]
        
        for risk_level, expected_min in test_cases:
            min_evidence = self.tool._get_min_evidence(risk_level)
            self.assertEqual(min_evidence, expected_min)
            
    def test_freshness_score_range(self):
        """Test freshness scores are in valid range."""
        evidence = self.tool._gather_evidence("test", {})
        
        for item in evidence:
            score = item["freshness_score"]
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
            
    def test_trace_output_format(self):
        """Test trace can be saved and loaded."""
        trace = self.tool._run("Save test", {})
        
        # Save to temporary file
        temp_path = Path("test_trace_output.md")
        try:
            with open(temp_path, "w") as f:
                f.write(trace)
                
            # Verify file was written
            self.assertTrue(temp_path.exists())
            
            # Read back and verify
            content = temp_path.read_text()
            self.assertEqual(content, trace)
            
        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()


class TestTraceCompliance(unittest.TestCase):
    """Test trace compliance with v7.0.0 specification."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = CoTReasoningTool()
        
    def test_timestamp_requirement(self):
        """Test v7.0.0 timestamp requirements."""
        trace = self.tool._run("Timestamp test", {})
        
        # Check for timestamp fields in evidence
        self.assertIn("Timestamp:", trace)
        self.assertIn("Created:", trace)
        self.assertIn("Modified:", trace)
        self.assertIn("Accessed:", trace)
        
    def test_freshness_calculation(self):
        """Test freshness score calculation."""
        trace = self.tool._run("Freshness test", {})
        
        # Check for freshness indicators
        self.assertIn("Freshness:", trace)
        self.assertIn("score:", trace)
        
    def test_risk_appropriate_evidence(self):
        """Test evidence count matches risk level."""
        # High risk task
        trace = self.tool._run("Delete critical security module", {})
        
        # Extract evidence count from YAML header
        self.assertIn("risk_level: high", trace)
        self.assertIn("evidence_count:", trace)
        
        # Verify minimum 3 evidence items for high risk
        evidence_section = trace[trace.find("Evidence Collection:"):]
        evidence_count = evidence_section.count("**Source**:")
        self.assertGreaterEqual(evidence_count, 3)


class TestIntegrationScenarios(unittest.TestCase):
    """End-to-end integration scenarios."""
    
    def test_refactoring_scenario(self):
        """Test complete refactoring decision scenario."""
        tool = CoTReasoningTool()
        
        # Simulate refactoring decision
        result = tool._run(
            task="Refactor payment processing module to improve maintainability",
            context={
                "access_level": "full_file_access",
                "tools": ["File reading", "AST parsing", "Dependency analysis"],
                "module_info": {
                    "size": 1500,
                    "complexity": 45,
                    "last_modified": "2024-01-15"
                }
            }
        )
        
        # Verify it's a valid trace
        validation = tool._validate_trace(result)
        self.assertTrue(validation["valid"])
        
        # Check risk assessment
        self.assertIn("risk_level: medium", result)
        
        # Check action recommendation
        self.assertIn("Therefore, I will:", result)
        
    def test_deletion_scenario(self):
        """Test file deletion decision scenario."""
        tool = CoTReasoningTool()
        
        result = tool._run(
            task="Delete unused utility file legacy_helpers.py",
            context={
                "file_info": {
                    "last_modified": "2023-01-01",
                    "size_bytes": 5000,
                    "import_count": 0
                }
            }
        )
        
        # Should be marked as medium/high risk
        self.assertIn("risk_level:", result)
        self.assertNotIn("risk_level: low", result)
        
        # Should have multiple evidence sources
        evidence_count = result.count("**Source**:")
        self.assertGreaterEqual(evidence_count, 2)


class TestOutputSnapshot(unittest.TestCase):
    """Test output snapshot functionality for regression testing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = CoTReasoningTool()
        self.snapshot_dir = Path(__file__).parent / "snapshots"
        self.snapshot_dir.mkdir(exist_ok=True)
        
    def _generate_snapshot_key(self, task: str, context: dict) -> str:
        """Generate deterministic key for snapshot."""
        key_data = {
            "task": task,
            "context": context,
            "version": self.tool.cot_version
        }
        key_json = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_json.encode()).hexdigest()[:8]
    
    def _get_snapshot_path(self, key: str) -> Path:
        """Get path for snapshot file."""
        return self.snapshot_dir / f"trace_snapshot_{key}.json"
    
    def _normalize_trace(self, trace: str) -> dict:
        """Normalize trace for comparison (remove timestamps)."""
        # Extract key sections while removing dynamic content
        sections = {
            "schema_present": "schema: chain_of_thought/v7.0.0" in trace,
            "risk_level": "medium" if "risk_level: medium" in trace else 
                         "high" if "risk_level: high" in trace else 
                         "low" if "risk_level: low" in trace else "unknown",
            "evidence_count": trace.count("**Source**:"),
            "has_analysis": "#### Analysis:" in trace,
            "has_validation": "#### Validation:" in trace,
            "has_action": "Therefore, I will:" in trace,
            "structure_hash": hashlib.md5(
                # Hash structure without timestamps
                trace.replace(datetime.now().strftime("%Y-%m-%d"), "DATE")
                     .replace(datetime.now().strftime("%H:%M:%S"), "TIME")
                     .encode()
            ).hexdigest()
        }
        return sections
    
    def test_snapshot_consistency(self):
        """Test that output remains consistent for same inputs."""
        test_cases = [
            {
                "task": "Update configuration file",
                "context": {"access_level": "full_file_access"}
            },
            {
                "task": "Refactor payment module",
                "context": {
                    "module_info": {"size": 1000, "complexity": 30}
                }
            }
        ]
        
        for test_case in test_cases:
            with self.subTest(task=test_case["task"]):
                # Generate trace
                trace = self.tool._run(
                    task=test_case["task"],
                    context=test_case["context"]
                )
                
                # Normalize for comparison
                normalized = self._normalize_trace(trace)
                
                # Generate snapshot key
                key = self._generate_snapshot_key(
                    test_case["task"], 
                    test_case["context"]
                )
                snapshot_path = self._get_snapshot_path(key)
                
                if snapshot_path.exists():
                    # Compare with existing snapshot
                    with open(snapshot_path, 'r') as f:
                        saved_snapshot = json.load(f)
                    
                    # Check structural consistency
                    self.assertEqual(
                        normalized["schema_present"],
                        saved_snapshot["schema_present"],
                        "Schema presence changed"
                    )
                    self.assertEqual(
                        normalized["risk_level"],
                        saved_snapshot["risk_level"],
                        "Risk level changed for same input"
                    )
                    self.assertEqual(
                        normalized["evidence_count"],
                        saved_snapshot["evidence_count"],
                        "Evidence count changed"
                    )
                else:
                    # Save new snapshot
                    with open(snapshot_path, 'w') as f:
                        json.dump(normalized, f, indent=2)
                    print(f"Created new snapshot: {snapshot_path}")
    
    def test_snapshot_validation(self):
        """Test that all snapshots pass validation."""
        snapshots = list(self.snapshot_dir.glob("trace_snapshot_*.json"))
        
        if not snapshots:
            self.skipTest("No snapshots found to validate")
        
        for snapshot_path in snapshots:
            with self.subTest(snapshot=snapshot_path.name):
                with open(snapshot_path, 'r') as f:
                    snapshot_data = json.load(f)
                
                # Verify snapshot structure
                required_keys = [
                    "schema_present", "risk_level", "evidence_count",
                    "has_analysis", "has_validation", "has_action"
                ]
                for key in required_keys:
                    self.assertIn(key, snapshot_data, f"Missing key: {key}")
                
                # Verify values are reasonable
                self.assertTrue(snapshot_data["schema_present"])
                self.assertIn(snapshot_data["risk_level"], 
                            ["low", "medium", "high", "critical"])
                self.assertGreater(snapshot_data["evidence_count"], 0)
                self.assertTrue(snapshot_data["has_analysis"])
                self.assertTrue(snapshot_data["has_validation"])
    
    def test_output_determinism(self):
        """Test that multiple runs produce consistent structure."""
        task = "Test deterministic output"
        context = {"test_mode": True}
        
        # Run multiple times
        traces = []
        for i in range(3):
            trace = self.tool._run(task, context)
            normalized = self._normalize_trace(trace)
            traces.append(normalized)
        
        # Compare all traces
        for i in range(1, len(traces)):
            self.assertEqual(
                traces[0]["risk_level"],
                traces[i]["risk_level"],
                f"Risk level inconsistent between run 0 and {i}"
            )
            self.assertEqual(
                traces[0]["evidence_count"],
                traces[i]["evidence_count"],
                f"Evidence count inconsistent between run 0 and {i}"
            )
            self.assertEqual(
                traces[0]["structure_hash"],
                traces[i]["structure_hash"],
                f"Structure hash inconsistent between run 0 and {i}"
            )


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)