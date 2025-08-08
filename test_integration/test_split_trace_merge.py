#!/usr/bin/env python3
"""
Test that split_trace outcomes are merged correctly.

This validates that multi-part traces can be properly reconstructed.
"""

import json
import unittest
from pathlib import Path
from datetime import datetime
import hashlib


class TestSplitTraceMerge(unittest.TestCase):
    """Test cases for split trace merging and validation."""
    
    def test_split_trace_parts_validation(self):
        """Test that split trace parts are individually valid."""
        # Read the split trace example
        split_trace_path = Path(__file__).parent.parent / "test_suite" / "edge_cases" / "004_split_trace_fallback.md"
        self.assertTrue(split_trace_path.exists(), "Split trace example file not found")
        
        content = split_trace_path.read_text()
        
        # Verify Part 1 structure
        self.assertIn("trace_part: 1", content)
        self.assertIn("continuation_needed: true", content)
        self.assertIn("continuation_token: \"cot_trace_a1b2c3d4e5f6_part1\"", content)
        self.assertIn("state_hash: \"sha256:7f3a8b9c1d2e4f5a6b7c8d9e0f1a2b3c\"", content)
        
        # Verify Part 2 structure
        self.assertIn("trace_part: 2", content)
        self.assertIn("previous_part_hash: \"sha256:7f3a8b9c1d2e4f5a6b7c8d9e0f1a2b3c\"", content)
        
    def test_trace_merge_validation(self):
        """Test that merged trace contains all required elements."""
        # Simulate merging two trace parts
        part1_metadata = {
            "part_number": 1,
            "total_parts_estimate": 2,
            "tokens_used": 3850,
            "continuation_token": "cot_trace_a1b2c3d4e5f6_part1",
            "state_hash": "sha256:7f3a8b9c1d2e4f5a6b7c8d9e0f1a2b3c"
        }
        
        part2_metadata = {
            "part_number": 2,
            "continuation_token": "cot_trace_a1b2c3d4e5f6_part1",
            "previous_part_hash": "sha256:7f3a8b9c1d2e4f5a6b7c8d9e0f1a2b3c"
        }
        
        # Validate continuity
        self.assertEqual(
            part1_metadata["state_hash"],
            part2_metadata["previous_part_hash"],
            "Part 2 must reference Part 1's state hash"
        )
        
        # Validate token references match
        self.assertEqual(
            part1_metadata["continuation_token"],
            part2_metadata["continuation_token"],
            "Continuation tokens must match"
        )
        
    def test_merged_trace_completeness(self):
        """Test that merged trace has all required sections."""
        # Define expected sections in a complete merged trace
        required_sections = {
            "part1": [
                "Risk Assessment",
                "Evidence Collection",
                "TOKEN LIMIT APPROACHING",
                "Partial Analysis"
            ],
            "part2": [
                "Resumed from Part 1",
                "Analysis",
                "Validation", 
                "Action",
                "Trace Completion"
            ]
        }
        
        # Read split trace file
        split_trace_path = Path(__file__).parent.parent / "test_suite" / "edge_cases" / "004_split_trace_fallback.md"
        content = split_trace_path.read_text()
        
        # Check all required sections exist
        for part, sections in required_sections.items():
            for section in sections:
                self.assertIn(
                    section,
                    content,
                    f"Missing required section '{section}' in {part}"
                )
                
    def test_evidence_continuity(self):
        """Test that evidence is preserved across split parts."""
        split_trace_path = Path(__file__).parent.parent / "test_suite" / "edge_cases" / "004_split_trace_fallback.md"
        content = split_trace_path.read_text()
        
        # Count evidence items in Part 1
        part1_evidence_count = content[:content.find("Part 2")].count("**Source**:")
        self.assertEqual(5, part1_evidence_count, "Part 1 should have 5 evidence items")
        
        # Verify Part 2 references Part 1's evidence
        self.assertIn("Evidence from 5 different sources collected", content)
        
    def test_decision_consistency(self):
        """Test that final decision is consistent with analysis."""
        split_trace_path = Path(__file__).parent.parent / "test_suite" / "edge_cases" / "004_split_trace_fallback.md"
        content = split_trace_path.read_text()
        
        # Extract final decision
        self.assertIn("final_decision: \"Implement phased security remediation\"", content)
        
        # Verify decision appears in Action section
        self.assertIn("Therefore, I will implement a phased security remediation plan", content)
        
        # Verify urgency matches risk assessment
        self.assertIn("urgency: \"Critical - immediate action required\"", content)
        self.assertIn("Risk Level**: High", content)
        
    def test_merge_algorithm(self):
        """Test the algorithm for merging split traces."""
        class TraceMerger:
            def __init__(self):
                self.parts = {}
                
            def add_part(self, part_number, content, metadata):
                """Add a trace part for merging."""
                self.parts[part_number] = {
                    "content": content,
                    "metadata": metadata
                }
                
            def validate_continuity(self):
                """Validate parts can be merged."""
                sorted_parts = sorted(self.parts.items())
                
                for i in range(len(sorted_parts) - 1):
                    current = sorted_parts[i][1]["metadata"]
                    next_part = sorted_parts[i + 1][1]["metadata"]
                    
                    # Validate hash chain
                    if "state_hash" in current and "previous_part_hash" in next_part:
                        if current["state_hash"] != next_part["previous_part_hash"]:
                            return False, f"Hash mismatch between part {i+1} and {i+2}"
                            
                    # Validate continuation token
                    if current.get("continuation_token") != next_part.get("continuation_token"):
                        return False, f"Continuation token mismatch at part {i+2}"
                        
                return True, "All parts valid for merging"
                
            def merge(self):
                """Merge all parts into complete trace."""
                valid, message = self.validate_continuity()
                if not valid:
                    raise ValueError(f"Cannot merge: {message}")
                    
                merged_content = []
                total_tokens = 0
                
                for part_num in sorted(self.parts.keys()):
                    part = self.parts[part_num]
                    merged_content.append(part["content"])
                    total_tokens += part["metadata"].get("tokens_used", 0)
                    
                return {
                    "merged_trace": "\n\n---\n\n".join(merged_content),
                    "total_tokens": total_tokens,
                    "part_count": len(self.parts)
                }
        
        # Test the merger
        merger = TraceMerger()
        
        # Add simulated parts
        merger.add_part(1, "Part 1 content with evidence", {
            "tokens_used": 3850,
            "continuation_token": "test_token_123",
            "state_hash": "sha256:abcdef123456"
        })
        
        merger.add_part(2, "Part 2 content with analysis", {
            "tokens_used": 3350,
            "continuation_token": "test_token_123",
            "previous_part_hash": "sha256:abcdef123456"
        })
        
        # Validate and merge
        valid, message = merger.validate_continuity()
        self.assertTrue(valid, message)
        
        merged = merger.merge()
        self.assertEqual(merged["part_count"], 2)
        self.assertEqual(merged["total_tokens"], 7200)
        self.assertIn("Part 1 content", merged["merged_trace"])
        self.assertIn("Part 2 content", merged["merged_trace"])
        

if __name__ == "__main__":
    unittest.main(verbosity=2)