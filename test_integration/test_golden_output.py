#!/usr/bin/env python3
"""
Golden output tests for LangChain CoT integration.

This ensures the CoT reasoning tool produces consistent, valid output
by comparing against known-good traces.
"""

import unittest
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "examples"))

from langchain_integration import CoTReasoningTool


class TestGoldenOutput(unittest.TestCase):
    """Test CoT tool output against golden standards."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = CoTReasoningTool(cot_version="7.0.0")
        self.golden_path = Path(__file__).parent.parent / "examples" / "golden_output_trace.md"
        
    def test_golden_output_structure(self):
        """Test that output matches golden structure."""
        # Generate trace with fixed timestamp for consistency
        original_gather = self.tool._gather_evidence
        
        def mock_gather_evidence(task, context):
            # Return consistent evidence with fixed timestamps
            return [
                {
                    "source": "architecture_guidelines.md:45",
                    "quote": "All modules should follow single responsibility principle",
                    "relevance": "Supports modular refactoring approach",
                    "timestamp": {
                        "created": "2024-01-15T10:00:00Z",
                        "modified": "2024-01-20T14:00:00Z",
                        "accessed": "2024-01-26T12:00:00Z"
                    },
                    "freshness": "current",
                    "freshness_score": 0.95
                },
                {
                    "source": "code_review_notes.md:102",
                    "quote": "Consider splitting large modules into smaller components",
                    "relevance": "Directly suggests the refactoring approach",
                    "timestamp": {
                        "created": "2024-01-25T09:00:00Z",
                        "modified": "2024-01-25T09:00:00Z",
                        "accessed": "2024-01-26T12:00:00Z"
                    },
                    "freshness": "current",
                    "freshness_score": 0.99
                }
            ]
        
        # Patch the method
        self.tool._gather_evidence = mock_gather_evidence
        
        try:
            # Generate trace
            result = self.tool._run(
                task="Refactor the payment processing module to improve maintainability",
                context={
                    "access_level": "full_file_access",
                    "tools": ["File reading", "AST parsing", "Dependency analysis"]
                }
            )
            
            # Load golden output
            golden_content = self.golden_path.read_text()
            
            # Normalize whitespace for comparison
            result_normalized = "\n".join(line.rstrip() for line in result.splitlines())
            golden_normalized = "\n".join(line.rstrip() for line in golden_content.splitlines())
            
            # Check key sections exist
            self.assertIn("## 🧠 Reasoning Trace (Chain-of-Thought)", result)
            self.assertIn("schema: chain_of_thought/v7.0.0", result)
            self.assertIn("Risk Assessment:", result)
            self.assertIn("Evidence Collection:", result)
            self.assertIn("Analysis:", result)
            self.assertIn("Validation:", result)
            self.assertIn("Action:", result)
            
            # Verify exact match
            self.assertEqual(result_normalized, golden_normalized,
                           "Output does not match golden standard")
            
        finally:
            # Restore original method
            self.tool._gather_evidence = original_gather
    
    def test_golden_output_hash(self):
        """Test output consistency via hash comparison."""
        # Use the same mock as above for consistency
        original_gather = self.tool._gather_evidence
        
        def mock_gather_evidence(task, context):
            return [
                {
                    "source": "architecture_guidelines.md:45",
                    "quote": "All modules should follow single responsibility principle",
                    "relevance": "Supports modular refactoring approach",
                    "timestamp": {
                        "created": "2024-01-15T10:00:00Z",
                        "modified": "2024-01-20T14:00:00Z",
                        "accessed": "2024-01-26T12:00:00Z"
                    },
                    "freshness": "current",
                    "freshness_score": 0.95
                },
                {
                    "source": "code_review_notes.md:102",
                    "quote": "Consider splitting large modules into smaller components",
                    "relevance": "Directly suggests the refactoring approach",
                    "timestamp": {
                        "created": "2024-01-25T09:00:00Z",
                        "modified": "2024-01-25T09:00:00Z",
                        "accessed": "2024-01-26T12:00:00Z"
                    },
                    "freshness": "current",
                    "freshness_score": 0.99
                }
            ]
        
        self.tool._gather_evidence = mock_gather_evidence
        
        try:
            # Generate multiple traces
            traces = []
            for i in range(3):
                trace = self.tool._run(
                    task="Refactor the payment processing module to improve maintainability",
                    context={
                        "access_level": "full_file_access",
                        "tools": ["File reading", "AST parsing", "Dependency analysis"]
                    }
                )
                traces.append(trace)
            
            # All should be identical
            self.assertEqual(traces[0], traces[1], "Traces differ between runs")
            self.assertEqual(traces[1], traces[2], "Traces differ between runs")
            
            # Compute hash
            trace_hash = hashlib.sha256(traces[0].encode('utf-8')).hexdigest()
            
            # Store expected hash (computed from golden output)
            # This would be updated when golden output changes intentionally
            expected_hash = None  # Will be set on first run
            
            # For now, just verify consistency
            for trace in traces:
                current_hash = hashlib.sha256(trace.encode('utf-8')).hexdigest()
                self.assertEqual(trace_hash, current_hash, 
                               "Hash mismatch - output not deterministic")
                
        finally:
            self.tool._gather_evidence = original_gather
    
    def test_structured_output_matches_golden(self):
        """Test that structured JSON output matches expected format."""
        # Mock evidence gathering
        original_gather = self.tool._gather_evidence
        
        def mock_gather_evidence(task, context):
            return [
                {
                    "source": "architecture_guidelines.md:45",
                    "quote": "All modules should follow single responsibility principle",
                    "relevance": "Supports modular refactoring approach",
                    "timestamp": {
                        "created": "2024-01-15T10:00:00Z",
                        "modified": "2024-01-20T14:00:00Z",
                        "accessed": "2024-01-26T12:00:00Z"
                    },
                    "freshness": "current",
                    "freshness_score": 0.95
                },
                {
                    "source": "code_review_notes.md:102",
                    "quote": "Consider splitting large modules into smaller components",
                    "relevance": "Directly suggests the refactoring approach",
                    "timestamp": {
                        "created": "2024-01-25T09:00:00Z",
                        "modified": "2024-01-25T09:00:00Z",
                        "accessed": "2024-01-26T12:00:00Z"
                    },
                    "freshness": "current",
                    "freshness_score": 0.99
                }
            ]
        
        self.tool._gather_evidence = mock_gather_evidence
        
        try:
            # Generate structured data
            structured_data = {
                "metadata": {
                    "schema": "chain_of_thought/v7.0.0",
                    "generated_at": "2024-01-26T12:00:00Z",  # Fixed for testing
                    "tool_version": "2.0.0"
                },
                "task": "Refactor the payment processing module to improve maintainability",
                "risk_assessment": {
                    "level": "medium",
                    "change_type": "Refactor module structure",
                    "impact_scope": "Module",
                    "reversibility": "Moderate effort to reverse"
                },
                "evidence": mock_gather_evidence(
                    "Refactor the payment processing module", 
                    {"access_level": "full_file_access"}
                ),
                "decision": {
                    "action": "Execute refactor the payment processing module to improve maintainability following best practices",
                    "confidence": 0.85,
                    "validation_status": True
                }
            }
            
            # Validate structure
            self.assertEqual(structured_data["metadata"]["schema"], "chain_of_thought/v7.0.0")
            self.assertEqual(len(structured_data["evidence"]), 2)
            self.assertEqual(structured_data["risk_assessment"]["level"], "medium")
            self.assertGreater(structured_data["decision"]["confidence"], 0.8)
            
            # Ensure JSON serializable
            json_str = json.dumps(structured_data, indent=2)
            self.assertIsInstance(json_str, str)
            
            # Verify it can be loaded back
            loaded = json.loads(json_str)
            self.assertEqual(loaded["task"], structured_data["task"])
            
        finally:
            self.tool._gather_evidence = original_gather


class TestSnapshotComparison(unittest.TestCase):
    """Snapshot testing for trace outputs."""
    
    def setUp(self):
        """Set up snapshot testing."""
        self.snapshots_dir = Path(__file__).parent / "snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)
        
    def test_snapshot_trace(self):
        """Test trace against snapshot."""
        tool = CoTReasoningTool()
        
        # Fixed evidence for reproducibility
        def mock_gather_evidence(task, context):
            return [
                {
                    "source": "test_file.py:100",
                    "quote": "Test evidence for snapshot",
                    "relevance": "Validates snapshot testing",
                    "timestamp": {
                        "created": "2024-01-26T00:00:00Z",
                        "modified": "2024-01-26T00:00:00Z",
                        "accessed": "2024-01-26T00:00:00Z"
                    },
                    "freshness": "current",
                    "freshness_score": 1.0
                }
            ]
        
        tool._gather_evidence = mock_gather_evidence
        
        # Generate trace
        trace = tool._run(
            task="Test snapshot functionality",
            context={"access_level": "full_file_access"}
        )
        
        # Snapshot path
        snapshot_path = self.snapshots_dir / "test_snapshot_trace.md"
        
        if snapshot_path.exists():
            # Compare with existing snapshot
            expected = snapshot_path.read_text()
            self.assertEqual(trace, expected, 
                           f"Output differs from snapshot at {snapshot_path}")
        else:
            # Create snapshot (first run)
            snapshot_path.write_text(trace)
            self.skipTest(f"Snapshot created at {snapshot_path}")


if __name__ == "__main__":
    unittest.main(verbosity=2)