#!/usr/bin/env python3
"""
Chain-of-Thought Validator
Version: 1.0.0
Purpose: Validate CoT reasoning traces against schema and quality standards
"""

import json
import re
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path
import argparse
import sys

# Try to import jsonschema for validation
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not installed. Schema validation will be limited.")

# Import semantic integration if available
try:
    from semantic_integration import SemanticIntegration
    HAS_SEMANTIC = True
except ImportError:
    HAS_SEMANTIC = False
    print("Warning: semantic_integration not available. Semantic validation disabled.")


class CoTValidator:
    """
    Validates Chain-of-Thought reasoning traces for:
    1. Schema compliance
    2. Evidence quality
    3. Reasoning completeness
    4. Token usage estimation
    5. Contradiction detection
    """
    
    # CoT v7.0.0 Schema (simplified for Python validation)
    COT_SCHEMA = {
        "required_sections": [
            "decision",
            "evidence_collection",
            "analysis",
            "validation",
            "action"
        ],
        "evidence_min_length": 10,
        "quote_min_length": 10,
        "relevance_min_length": 20,
        "rationale_min_length": 30,
        "action_pattern": r"^→ Therefore, I will: .+",
        "source_pattern": r"^.+:(\d+(-\d+)?|§.+)$|^.+\s+\(.*\)$"
    }
    
    # Risk-based evidence requirements
    EVIDENCE_REQUIREMENTS = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4
    }
    
    # Token estimation factors
    TOKEN_FACTORS = {
        "text_chars_per_token": 4,  # Approximate
        "metadata_overhead": 100,   # Base tokens for structure
        "evidence_per_item": 50,    # Tokens per evidence item
    }
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator.
        
        Args:
            strict_mode: If True, enforce all requirements strictly
        """
        self.strict_mode = strict_mode
        self.validation_errors = []
        self.validation_warnings = []
        self.semantic_integration = SemanticIntegration() if HAS_SEMANTIC else None
    
    def validate_cot_trace(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation entry point.
        
        Args:
            trace: CoT reasoning trace to validate
            
        Returns:
            Validation results dictionary
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        results = {
            "is_valid": True,
            "schema_compliance": self._check_schema_compliance(trace),
            "evidence_quality": self._score_evidence_quality(trace),
            "complexity_score": self._calculate_complexity(trace),
            "token_usage": self._predict_token_usage(trace),
            "contradictions": self._detect_contradictions(trace),
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Check for critical errors
        if self.validation_errors:
            results["is_valid"] = False
            results["errors"] = self.validation_errors
        
        results["warnings"] = self.validation_warnings
        
        # Generate recommendations
        results["recommendations"] = self._generate_recommendations(results)
        
        return results
    
    def _check_schema_compliance(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """Check if trace complies with CoT schema."""
        compliance = {
            "has_required_sections": True,
            "valid_structure": True,
            "proper_formatting": True,
            "details": {}
        }
        
        # Check required sections
        for section in self.COT_SCHEMA["required_sections"]:
            if section not in trace:
                compliance["has_required_sections"] = False
                compliance["details"][section] = "Missing"
                self.validation_errors.append(f"Missing required section: {section}")
            else:
                compliance["details"][section] = "Present"
        
        # Validate decision
        if "decision" in trace:
            if not isinstance(trace["decision"], str) or len(trace["decision"]) < 10:
                self.validation_errors.append("Decision must be a string with at least 10 characters")
                compliance["valid_structure"] = False
        
        # Validate evidence collection
        if "evidence_collection" in trace:
            evidence_items = trace["evidence_collection"]
            if not isinstance(evidence_items, list):
                self.validation_errors.append("Evidence collection must be a list")
                compliance["valid_structure"] = False
            elif len(evidence_items) == 0:
                self.validation_errors.append("Evidence collection cannot be empty")
            else:
                for i, item in enumerate(evidence_items):
                    self._validate_evidence_item(item, i)
        
        # Validate analysis
        if "analysis" in trace:
            analysis = trace["analysis"]
            if not isinstance(analysis, dict):
                self.validation_errors.append("Analysis must be a dictionary")
                compliance["valid_structure"] = False
            else:
                required_analysis = ["primary_rationale", "alternative_considered", "alternative_rejected_because"]
                for field in required_analysis:
                    if field not in analysis:
                        self.validation_errors.append(f"Analysis missing required field: {field}")
        
        # Validate action format
        if "action" in trace:
            action = trace["action"]
            if not re.match(self.COT_SCHEMA["action_pattern"], action):
                self.validation_errors.append("Action must start with '→ Therefore, I will: '")
                compliance["proper_formatting"] = False
        
        return compliance
    
    def _validate_evidence_item(self, item: Dict[str, Any], index: int):
        """Validate individual evidence item."""
        required_fields = ["source", "quote", "relevance"]
        
        for field in required_fields:
            if field not in item:
                self.validation_errors.append(f"Evidence item {index} missing field: {field}")
        
        # Check source format
        if "source" in item:
            source = item["source"]
            if not re.match(self.COT_SCHEMA["source_pattern"], source):
                self.validation_warnings.append(f"Evidence item {index} source format may be invalid: {source}")
        
        # Check quote length
        if "quote" in item:
            quote = item["quote"]
            if len(quote) < self.COT_SCHEMA["quote_min_length"]:
                self.validation_errors.append(f"Evidence item {index} quote too short (min {self.COT_SCHEMA['quote_min_length']} chars)")
        
        # Check relevance length
        if "relevance" in item:
            relevance = item["relevance"]
            if len(relevance) < self.COT_SCHEMA["relevance_min_length"]:
                self.validation_warnings.append(f"Evidence item {index} relevance description too brief")
    
    def _score_evidence_quality(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """Score the quality of evidence in the trace."""
        quality_score = {
            "total_score": 0.0,
            "evidence_count": 0,
            "has_timestamps": False,
            "has_freshness": False,
            "diverse_sources": False,
            "details": []
        }
        
        if "evidence_collection" not in trace:
            return quality_score
        
        evidence_items = trace["evidence_collection"]
        quality_score["evidence_count"] = len(evidence_items)
        
        sources = set()
        total_item_score = 0.0
        
        for item in evidence_items:
            item_score = 0.0
            detail = {"source": item.get("source", "unknown")}
            
            # Score based on completeness
            if "quote" in item and len(item["quote"]) > 20:
                item_score += 0.3
            if "relevance" in item and len(item["relevance"]) > 30:
                item_score += 0.3
            if "timestamp" in item:
                item_score += 0.2
                quality_score["has_timestamps"] = True
            if "freshness" in item:
                item_score += 0.2
                quality_score["has_freshness"] = True
            
            # Track source diversity
            if "source" in item:
                sources.add(item["source"].split(":")[0])
            
            detail["score"] = item_score
            quality_score["details"].append(detail)
            total_item_score += item_score
        
        # Calculate overall score
        if quality_score["evidence_count"] > 0:
            quality_score["total_score"] = total_item_score / quality_score["evidence_count"]
        
        # Check source diversity
        if len(sources) >= 3:
            quality_score["diverse_sources"] = True
            quality_score["total_score"] = min(1.0, quality_score["total_score"] + 0.1)
        
        # Check against risk-based requirements
        risk_level = trace.get("risk_assessment", {}).get("risk_level", "medium").lower()
        required_evidence = self.EVIDENCE_REQUIREMENTS.get(risk_level, 2)
        
        if quality_score["evidence_count"] < required_evidence:
            self.validation_errors.append(
                f"Insufficient evidence for {risk_level} risk: {quality_score['evidence_count']}/{required_evidence}"
            )
        
        return quality_score
    
    def _calculate_complexity(self, trace: Dict[str, Any]) -> float:
        """Calculate complexity score of the reasoning task."""
        complexity = 0.0
        
        # Factor 1: Evidence count (more evidence = more complex)
        evidence_count = len(trace.get("evidence_collection", []))
        complexity += min(evidence_count * 5, 30)  # Cap at 30
        
        # Factor 2: Risk level
        risk_level = trace.get("risk_assessment", {}).get("risk_level", "medium").lower()
        risk_scores = {"low": 10, "medium": 30, "high": 50, "critical": 70}
        complexity += risk_scores.get(risk_level, 30)
        
        # Factor 3: Analysis depth (alternatives considered)
        analysis = trace.get("analysis", {})
        if "alternative_considered" in analysis:
            complexity += 10
        if "alternative_rejected_because" in analysis:
            complexity += 10
        
        # Factor 4: Scope
        impact_scope = trace.get("risk_assessment", {}).get("impact_scope", "")
        if "system-wide" in impact_scope.lower():
            complexity += 20
        elif "module" in impact_scope.lower():
            complexity += 10
        
        return min(complexity, 100)  # Cap at 100
    
    def _predict_token_usage(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """Predict approximate token usage for the trace."""
        token_estimate = {
            "estimated_tokens": 0,
            "breakdown": {},
            "percentage_of_limit": 0.0,
            "warning": None
        }
        
        # Convert trace to string for character counting
        trace_str = json.dumps(trace, indent=2)
        base_chars = len(trace_str)
        
        # Estimate tokens
        text_tokens = base_chars // self.TOKEN_FACTORS["text_chars_per_token"]
        metadata_tokens = self.TOKEN_FACTORS["metadata_overhead"]
        evidence_tokens = len(trace.get("evidence_collection", [])) * self.TOKEN_FACTORS["evidence_per_item"]
        
        total_tokens = text_tokens + metadata_tokens + evidence_tokens
        token_estimate["estimated_tokens"] = total_tokens
        
        token_estimate["breakdown"] = {
            "text": text_tokens,
            "metadata": metadata_tokens,
            "evidence": evidence_tokens
        }
        
        # Calculate percentage of typical limit (4000 tokens)
        typical_limit = 4000
        percentage = (total_tokens / typical_limit) * 100
        token_estimate["percentage_of_limit"] = percentage
        
        # Add warnings
        if percentage > 90:
            token_estimate["warning"] = "CRITICAL: Approaching token limit"
            self.validation_warnings.append("Token usage critically high")
        elif percentage > 75:
            token_estimate["warning"] = "WARNING: High token usage"
            self.validation_warnings.append("Token usage is high")
        
        return token_estimate
    
    def _detect_contradictions(self, trace: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect potential contradictions in the reasoning."""
        contradictions = []
        
        evidence_items = trace.get("evidence_collection", [])
        
        # Simple contradiction detection based on opposing terms
        opposites = [
            ("true", "false"), ("yes", "no"), ("always", "never"),
            ("must", "must not"), ("should", "should not"),
            ("increase", "decrease"), ("add", "remove")
        ]
        
        for i, item1 in enumerate(evidence_items):
            quote1 = item1.get("quote", "").lower()
            
            for j, item2 in enumerate(evidence_items[i+1:], i+1):
                quote2 = item2.get("quote", "").lower()
                
                # Check for opposite terms
                for opp1, opp2 in opposites:
                    if (opp1 in quote1 and opp2 in quote2) or (opp2 in quote1 and opp1 in quote2):
                        contradictions.append({
                            "type": "opposing_evidence",
                            "item1": i,
                            "item2": j,
                            "description": f"Potential contradiction between evidence {i} and {j}"
                        })
        
        # Check if decision contradicts evidence
        decision = trace.get("decision", "").lower()
        for i, item in enumerate(evidence_items):
            quote = item.get("quote", "").lower()
            
            for opp1, opp2 in opposites:
                if (opp1 in decision and opp2 in quote) or (opp2 in decision and opp1 in quote):
                    contradictions.append({
                        "type": "decision_evidence_mismatch",
                        "evidence_item": i,
                        "description": f"Decision may contradict evidence {i}"
                    })
        
        if contradictions:
            self.validation_errors.append(f"Detected {len(contradictions)} potential contradictions")
        
        return contradictions
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Schema compliance recommendations
        if not results["schema_compliance"]["has_required_sections"]:
            recommendations.append("Add all required sections to the reasoning trace")
        
        # Evidence quality recommendations
        evidence_quality = results["evidence_quality"]
        if evidence_quality["total_score"] < 0.7:
            recommendations.append("Improve evidence quality by adding timestamps and better relevance descriptions")
        
        if not evidence_quality["diverse_sources"]:
            recommendations.append("Use more diverse evidence sources for stronger reasoning")
        
        # Complexity recommendations
        complexity = results["complexity_score"]
        if complexity > 60 and evidence_quality["evidence_count"] < 3:
            recommendations.append("High complexity task requires more evidence sources")
        
        # Token usage recommendations
        token_usage = results["token_usage"]
        if token_usage["percentage_of_limit"] > 75:
            recommendations.append("Consider decomposing the task to reduce token usage")
        
        # Contradiction recommendations
        if results["contradictions"]:
            recommendations.append("Resolve contradictions before proceeding with the decision")
        
        return recommendations
    
    def validate_file(self, filepath: str) -> Dict[str, Any]:
        """Validate a CoT trace from a file."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Try to extract JSON from markdown if present
            trace = self._extract_trace_from_content(content)
            
            if not trace:
                return {
                    "is_valid": False,
                    "errors": ["Could not extract valid CoT trace from file"],
                    "filepath": filepath
                }
            
            results = self.validate_cot_trace(trace)
            results["filepath"] = filepath
            return results
            
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"Error reading file: {str(e)}"],
                "filepath": filepath
            }
    
    def _extract_trace_from_content(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract CoT trace from markdown or JSON content."""
        # First try direct JSON parsing
        try:
            return json.loads(content)
        except:
            pass
        
        # Try to extract JSON from markdown code blocks
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                trace = json.loads(match)
                if "decision" in trace or "evidence_collection" in trace:
                    return trace
            except:
                continue
        
        # Try to parse markdown format into structured trace
        return self._parse_markdown_trace(content)
    
    def _parse_markdown_trace(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse markdown-formatted CoT trace into structured format."""
        trace = {}
        
        # Extract decision
        decision_pattern = r'### Decision: (.+?)(?:\n|$)'
        decision_match = re.search(decision_pattern, content)
        if decision_match:
            trace["decision"] = decision_match.group(1).strip()
        
        # Extract risk assessment
        risk_pattern = r'Risk Level[:\s]+(\w+)'
        risk_match = re.search(risk_pattern, content, re.IGNORECASE)
        if risk_match:
            trace["risk_assessment"] = {"risk_level": risk_match.group(1).lower()}
        
        # Extract evidence (simplified)
        evidence_pattern = r'\*\*Source\*\*: (.+?)\n.*?\*\*Quote\*\*: "(.+?)".*?\*\*Relevance\*\*: (.+?)(?:\n|$)'
        evidence_matches = re.findall(evidence_pattern, content, re.DOTALL)
        
        if evidence_matches:
            trace["evidence_collection"] = [
                {
                    "source": match[0].strip(),
                    "quote": match[1].strip(),
                    "relevance": match[2].strip()
                }
                for match in evidence_matches
            ]
        
        # Extract analysis
        analysis_pattern = r'\*\*Primary rationale\*\*: (.+?)(?:\n|$)'
        analysis_match = re.search(analysis_pattern, content)
        if analysis_match:
            trace["analysis"] = {
                "primary_rationale": analysis_match.group(1).strip(),
                "alternative_considered": "Not specified",
                "alternative_rejected_because": "Not specified"
            }
        
        # Extract action
        action_pattern = r'→ Therefore, I will: (.+?)(?:\n|$)'
        action_match = re.search(action_pattern, content)
        if action_match:
            trace["action"] = f"→ Therefore, I will: {action_match.group(1).strip()}"
        
        # Basic validation
        validation_pattern = r'\[([✓x])\] (.+?)(?:\n|$)'
        validation_matches = re.findall(validation_pattern, content)
        if validation_matches:
            trace["validation"] = {
                match[1].strip().lower().replace(" ", "_"): match[0] == "✓"
                for match in validation_matches
            }
        
        return trace if trace else None


def main():
    """Command-line interface for CoT validator."""
    parser = argparse.ArgumentParser(description="Validate Chain-of-Thought reasoning traces")
    parser.add_argument("input", help="Input file path or JSON string")
    parser.add_argument("--strict", action="store_true", help="Enable strict validation mode")
    parser.add_argument("--output", help="Output file for results (JSON)")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    validator = CoTValidator(strict_mode=args.strict)
    
    # Check if input is a file or JSON string
    if Path(args.input).exists():
        results = validator.validate_file(args.input)
    else:
        try:
            trace = json.loads(args.input)
            results = validator.validate_cot_trace(trace)
        except json.JSONDecodeError:
            print(f"Error: Input is neither a valid file nor valid JSON", file=sys.stderr)
            sys.exit(1)
    
    # Format output
    if args.format == "json":
        output = json.dumps(results, indent=2)
    else:
        output = format_results_text(results)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)
    
    # Exit code based on validation
    sys.exit(0 if results.get("is_valid", False) else 1)


def format_results_text(results: Dict[str, Any]) -> str:
    """Format validation results as human-readable text."""
    lines = [
        "=" * 60,
        "Chain-of-Thought Validation Results",
        "=" * 60,
        f"Valid: {'✓' if results.get('is_valid') else '✗'}",
        ""
    ]
    
    # Schema compliance
    if "schema_compliance" in results:
        compliance = results["schema_compliance"]
        lines.append("Schema Compliance:")
        lines.append(f"  Required sections: {'✓' if compliance.get('has_required_sections') else '✗'}")
        lines.append(f"  Valid structure: {'✓' if compliance.get('valid_structure') else '✗'}")
        lines.append(f"  Proper formatting: {'✓' if compliance.get('proper_formatting') else '✗'}")
        lines.append("")
    
    # Evidence quality
    if "evidence_quality" in results:
        quality = results["evidence_quality"]
        lines.append("Evidence Quality:")
        lines.append(f"  Score: {quality.get('total_score', 0):.2f}/1.00")
        lines.append(f"  Evidence count: {quality.get('evidence_count', 0)}")
        lines.append(f"  Diverse sources: {'✓' if quality.get('diverse_sources') else '✗'}")
        lines.append("")
    
    # Complexity and tokens
    lines.append(f"Complexity Score: {results.get('complexity_score', 0):.1f}/100")
    
    if "token_usage" in results:
        tokens = results["token_usage"]
        lines.append(f"Token Usage: {tokens.get('estimated_tokens', 0)} ({tokens.get('percentage_of_limit', 0):.1f}% of limit)")
        if tokens.get("warning"):
            lines.append(f"  ⚠️ {tokens['warning']}")
    lines.append("")
    
    # Errors
    if results.get("errors"):
        lines.append("Errors:")
        for error in results["errors"]:
            lines.append(f"  ✗ {error}")
        lines.append("")
    
    # Warnings
    if results.get("warnings"):
        lines.append("Warnings:")
        for warning in results["warnings"]:
            lines.append(f"  ⚠️ {warning}")
        lines.append("")
    
    # Contradictions
    if results.get("contradictions"):
        lines.append(f"Contradictions Detected: {len(results['contradictions'])}")
        for contradiction in results["contradictions"]:
            lines.append(f"  - {contradiction['description']}")
        lines.append("")
    
    # Recommendations
    if results.get("recommendations"):
        lines.append("Recommendations:")
        for rec in results["recommendations"]:
            lines.append(f"  → {rec}")
        lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


if __name__ == "__main__":
    main()