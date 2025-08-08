"""
Semantic Layer Integration for Chain-of-Thought Reasoning
Version: 1.0.0
Purpose: Bridge FACT/CLAIM/ASSUMPTION models with CoT reasoning system
"""

import json
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

# Import semantic models
from FACT.fact_model import Fact
from CLAIM.claim_model import Claim
from ASSUMPTION.assumption_model import Assumption


class ConflictType(Enum):
    """Types of conflicts that can occur between semantic objects."""
    DIRECT_CONTRADICTION = "direct_contradiction"
    SCOPE_CONFLICT = "scope_conflict"
    TEMPORAL_CONFLICT = "temporal_conflict"
    CONFIDENCE_CONFLICT = "confidence_conflict"
    SOURCE_CONFLICT = "source_conflict"


class EvidenceType(Enum):
    """Types of evidence in CoT reasoning."""
    FACT = "fact"
    CLAIM = "claim"
    ASSUMPTION = "assumption"
    EXTERNAL = "external"


@dataclass
class SemanticEvidence:
    """Evidence item that bridges semantic objects with CoT reasoning."""
    type: EvidenceType
    content: str
    source: str
    relevance: str
    confidence: float = 1.0
    timestamp: Optional[datetime] = None
    semantic_object: Optional[Any] = None
    
    def to_cot_format(self) -> Dict[str, Any]:
        """Convert to CoT evidence format."""
        return {
            "source": self.source,
            "quote": self.content,
            "relevance": self.relevance,
            "type": self.type.value,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


@dataclass
class Conflict:
    """Represents a conflict between semantic objects."""
    type: ConflictType
    object1: Any
    object2: Any
    description: str
    severity: str  # low, medium, high, critical
    resolution_strategy: Optional[str] = None


class SemanticIntegration:
    """
    Integrates FACT/CLAIM/ASSUMPTION semantic layer with CoT reasoning.
    
    Key responsibilities:
    1. Convert semantic objects to CoT evidence
    2. Validate claims against facts
    3. Check assumption boundaries
    4. Detect contradictions
    5. Cross-reference semantic objects
    """
    
    def __init__(self):
        self.facts: List[Fact] = []
        self.claims: List[Claim] = []
        self.assumptions: List[Assumption] = []
        self.conflicts: List[Conflict] = []
        self.cross_references: Dict[str, List[str]] = {}
    
    # ==================== FACT → CoT Integration ====================
    
    def fact_to_evidence(self, fact: Fact) -> SemanticEvidence:
        """
        Convert a Fact to CoT evidence.
        
        Facts provide the highest confidence evidence (1.0) as they are
        verifiable and objective.
        """
        return SemanticEvidence(
            type=EvidenceType.FACT,
            content=fact.statement,
            source=fact.source or "Verified Fact",
            relevance=f"Objective, verifiable fact{f' in context: {fact.context}' if fact.context else ''}",
            confidence=1.0,
            timestamp=datetime.now(timezone.utc),
            semantic_object=fact
        )
    
    def integrate_fact_with_cot(self, fact: Fact, cot_decision: str) -> Dict[str, Any]:
        """
        Example integration showing how a Fact strengthens CoT reasoning.
        """
        evidence = self.fact_to_evidence(fact)
        
        return {
            "decision": cot_decision,
            "evidence_collection": [evidence.to_cot_format()],
            "analysis": {
                "primary_rationale": f"Based on verified fact: {fact.statement}",
                "confidence_boost": "High confidence due to objective evidence",
                "fact_verification": {
                    "is_verifiable": fact.is_verifiable,
                    "is_objective": fact.is_objective
                }
            },
            "validation": {
                "fact_based": True,
                "minimum_sources_met": True,
                "no_assumptions_made": True
            }
        }
    
    # ==================== CLAIM → CoT Integration ====================
    
    def claim_to_evidence(self, claim: Claim) -> SemanticEvidence:
        """
        Convert a Claim to CoT evidence.
        
        Claims provide variable confidence evidence based on their
        confidence score.
        """
        return SemanticEvidence(
            type=EvidenceType.CLAIM,
            content=claim.statement,
            source=claim.source or "Unverified Claim",
            relevance=f"Claim requiring validation{f' in context: {claim.context}' if claim.context else ''}",
            confidence=claim.confidence if claim.confidence else 0.5,
            timestamp=datetime.now(timezone.utc),
            semantic_object=claim
        )
    
    def validate_claim_with_facts(self, claim: Claim) -> Tuple[bool, List[Fact]]:
        """
        Validate a claim against available facts.
        
        Returns:
            (is_validated, supporting_facts)
        """
        supporting_facts = []
        
        for fact in self.facts:
            # Simple keyword matching (can be enhanced with semantic similarity)
            claim_keywords = set(claim.statement.lower().split())
            fact_keywords = set(fact.statement.lower().split())
            
            overlap = claim_keywords.intersection(fact_keywords)
            if len(overlap) > 2:  # At least 3 common keywords
                supporting_facts.append(fact)
        
        is_validated = len(supporting_facts) > 0
        return is_validated, supporting_facts
    
    def integrate_claim_with_cot(self, claim: Claim, cot_decision: str) -> Dict[str, Any]:
        """
        Example integration showing how a Claim triggers evidence gathering in CoT.
        """
        evidence = self.claim_to_evidence(claim)
        is_validated, supporting_facts = self.validate_claim_with_facts(claim)
        
        fact_evidence = [self.fact_to_evidence(f).to_cot_format() 
                        for f in supporting_facts]
        
        return {
            "decision": cot_decision,
            "evidence_collection": [evidence.to_cot_format()] + fact_evidence,
            "analysis": {
                "primary_rationale": f"Evaluating claim: {claim.statement}",
                "claim_validation": {
                    "validated": is_validated,
                    "supporting_facts_count": len(supporting_facts),
                    "confidence": claim.confidence
                },
                "evidence_gathering_triggered": True
            },
            "validation": {
                "claim_validated": is_validated,
                "minimum_sources_met": len(fact_evidence) >= 2,
                "requires_further_evidence": not is_validated
            }
        }
    
    # ==================== ASSUMPTION → CoT Integration ====================
    
    def assumption_to_evidence(self, assumption: Assumption) -> SemanticEvidence:
        """
        Convert an Assumption to CoT evidence.
        
        Assumptions provide low confidence evidence (0.3) as they are
        unverified premises.
        """
        return SemanticEvidence(
            type=EvidenceType.ASSUMPTION,
            content=assumption.statement,
            source="Assumption (Unverified)",
            relevance=f"Operating assumption{f' within scope: {assumption.scope}' if assumption.scope else ''}",
            confidence=0.3,
            timestamp=datetime.now(timezone.utc),
            semantic_object=assumption
        )
    
    def check_assumption_boundaries(self, assumption: Assumption, context: str) -> bool:
        """
        Check if an assumption is valid within the given context.
        """
        if not assumption.scope:
            return True  # Global assumption
        
        # Check if context matches assumption scope
        return assumption.scope.lower() in context.lower()
    
    def integrate_assumption_with_cot(self, assumption: Assumption, cot_decision: str, context: str) -> Dict[str, Any]:
        """
        Example integration showing how Assumptions define reasoning boundaries in CoT.
        """
        evidence = self.assumption_to_evidence(assumption)
        in_bounds = self.check_assumption_boundaries(assumption, context)
        
        return {
            "decision": cot_decision,
            "evidence_collection": [evidence.to_cot_format()],
            "analysis": {
                "primary_rationale": f"Based on assumption: {assumption.statement}",
                "assumption_check": {
                    "within_boundaries": in_bounds,
                    "scope": assumption.scope,
                    "risk_acknowledged": True
                },
                "confidence_impact": "Reduced confidence due to unverified assumption"
            },
            "validation": {
                "assumption_based": True,
                "boundaries_checked": in_bounds,
                "requires_verification": True,
                "risk_level": "medium" if in_bounds else "high"
            }
        }
    
    # ==================== Contradiction Detection ====================
    
    def detect_contradictions(self) -> List[Conflict]:
        """
        Detect contradictions between all semantic objects.
        """
        conflicts = []
        
        # Check Fact vs Fact contradictions
        for i, fact1 in enumerate(self.facts):
            for fact2 in self.facts[i+1:]:
                conflict = self._check_direct_contradiction(fact1, fact2)
                if conflict:
                    conflicts.append(conflict)
        
        # Check Claim vs Fact contradictions
        for claim in self.claims:
            for fact in self.facts:
                conflict = self._check_claim_fact_contradiction(claim, fact)
                if conflict:
                    conflicts.append(conflict)
        
        # Check Assumption vs Fact contradictions
        for assumption in self.assumptions:
            for fact in self.facts:
                conflict = self._check_assumption_fact_contradiction(assumption, fact)
                if conflict:
                    conflicts.append(conflict)
        
        self.conflicts = conflicts
        return conflicts
    
    def _check_direct_contradiction(self, obj1: Any, obj2: Any) -> Optional[Conflict]:
        """Check for direct contradiction between two objects."""
        # Simple negation check
        if "not" in obj1.statement.lower() and obj2.statement.lower() in obj1.statement.lower():
            return Conflict(
                type=ConflictType.DIRECT_CONTRADICTION,
                object1=obj1,
                object2=obj2,
                description=f"Direct contradiction: '{obj1.statement}' vs '{obj2.statement}'",
                severity="critical",
                resolution_strategy="Fact takes precedence"
            )
        return None
    
    def _check_claim_fact_contradiction(self, claim: Claim, fact: Fact) -> Optional[Conflict]:
        """Check if a claim contradicts a fact."""
        # Check for semantic opposition (simplified)
        claim_words = set(claim.statement.lower().split())
        fact_words = set(fact.statement.lower().split())
        
        # Look for opposing terms
        opposites = [("true", "false"), ("yes", "no"), ("always", "never")]
        for opp1, opp2 in opposites:
            if (opp1 in claim_words and opp2 in fact_words) or \
               (opp2 in claim_words and opp1 in fact_words):
                return Conflict(
                    type=ConflictType.DIRECT_CONTRADICTION,
                    object1=claim,
                    object2=fact,
                    description=f"Claim contradicts fact: '{claim.statement}' vs '{fact.statement}'",
                    severity="high",
                    resolution_strategy="Fact overrides claim"
                )
        return None
    
    def _check_assumption_fact_contradiction(self, assumption: Assumption, fact: Fact) -> Optional[Conflict]:
        """Check if an assumption contradicts a fact."""
        # Similar to claim-fact check but with different severity
        assumption_words = set(assumption.statement.lower().split())
        fact_words = set(fact.statement.lower().split())
        
        opposites = [("true", "false"), ("yes", "no"), ("always", "never")]
        for opp1, opp2 in opposites:
            if (opp1 in assumption_words and opp2 in fact_words) or \
               (opp2 in assumption_words and opp1 in fact_words):
                return Conflict(
                    type=ConflictType.DIRECT_CONTRADICTION,
                    object1=assumption,
                    object2=fact,
                    description=f"Assumption contradicts fact: '{assumption.statement}' vs '{fact.statement}'",
                    severity="critical",
                    resolution_strategy="Fact invalidates assumption"
                )
        return None
    
    # ==================== Cross-Referencing System ====================
    
    def add_cross_reference(self, obj1_id: str, obj2_id: str):
        """Add a cross-reference between two semantic objects."""
        if obj1_id not in self.cross_references:
            self.cross_references[obj1_id] = []
        if obj2_id not in self.cross_references:
            self.cross_references[obj2_id] = []
        
        self.cross_references[obj1_id].append(obj2_id)
        self.cross_references[obj2_id].append(obj1_id)
    
    def get_related_objects(self, obj_id: str) -> List[str]:
        """Get all objects related to the given object ID."""
        return self.cross_references.get(obj_id, [])
    
    def build_semantic_graph(self) -> Dict[str, Any]:
        """Build a graph representation of semantic relationships."""
        nodes = []
        edges = []
        
        # Add nodes for each semantic object
        for fact in self.facts:
            nodes.append({
                "id": fact.id or hashlib.md5(fact.statement.encode()).hexdigest(),
                "type": "fact",
                "label": fact.statement[:50] + "..." if len(fact.statement) > 50 else fact.statement
            })
        
        for claim in self.claims:
            nodes.append({
                "id": claim.id or hashlib.md5(claim.statement.encode()).hexdigest(),
                "type": "claim",
                "label": claim.statement[:50] + "..." if len(claim.statement) > 50 else claim.statement
            })
        
        for assumption in self.assumptions:
            nodes.append({
                "id": assumption.id or hashlib.md5(assumption.statement.encode()).hexdigest(),
                "type": "assumption",
                "label": assumption.statement[:50] + "..." if len(assumption.statement) > 50 else assumption.statement
            })
        
        # Add edges for cross-references
        for source, targets in self.cross_references.items():
            for target in targets:
                edges.append({
                    "source": source,
                    "target": target,
                    "type": "reference"
                })
        
        # Add edges for conflicts
        for conflict in self.conflicts:
            obj1_id = conflict.object1.id or hashlib.md5(conflict.object1.statement.encode()).hexdigest()
            obj2_id = conflict.object2.id or hashlib.md5(conflict.object2.statement.encode()).hexdigest()
            edges.append({
                "source": obj1_id,
                "target": obj2_id,
                "type": "conflict",
                "conflict_type": conflict.type.value
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_nodes": len(nodes),
                "facts": len(self.facts),
                "claims": len(self.claims),
                "assumptions": len(self.assumptions),
                "conflicts": len(self.conflicts),
                "cross_references": len(self.cross_references)
            }
        }
    
    # ==================== Validation Pipeline ====================
    
    def validate_cot_with_semantics(self, cot_trace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a CoT reasoning trace against semantic objects.
        
        This is the main entry point for semantic validation of CoT reasoning.
        """
        validation_results = {
            "is_valid": True,
            "issues": [],
            "semantic_support": {
                "facts_used": 0,
                "claims_validated": 0,
                "assumptions_checked": 0,
                "conflicts_detected": 0
            },
            "recommendations": []
        }
        
        # Extract evidence from CoT trace
        evidence_items = cot_trace.get("evidence_collection", [])
        
        # Check each evidence item against semantic layer
        for evidence in evidence_items:
            quote = evidence.get("quote", "")
            
            # Check against facts
            fact_match = self._find_matching_fact(quote)
            if fact_match:
                validation_results["semantic_support"]["facts_used"] += 1
            
            # Check against claims
            claim_match = self._find_matching_claim(quote)
            if claim_match:
                is_validated, _ = self.validate_claim_with_facts(claim_match)
                if is_validated:
                    validation_results["semantic_support"]["claims_validated"] += 1
                else:
                    validation_results["issues"].append(
                        f"Unvalidated claim used as evidence: {claim_match.statement}"
                    )
            
            # Check against assumptions
            assumption_match = self._find_matching_assumption(quote)
            if assumption_match:
                validation_results["semantic_support"]["assumptions_checked"] += 1
                validation_results["recommendations"].append(
                    f"Consider verifying assumption: {assumption_match.statement}"
                )
        
        # Check for conflicts
        conflicts = self.detect_contradictions()
        if conflicts:
            validation_results["semantic_support"]["conflicts_detected"] = len(conflicts)
            validation_results["is_valid"] = False
            for conflict in conflicts:
                validation_results["issues"].append(
                    f"{conflict.type.value}: {conflict.description}"
                )
        
        # Generate overall assessment
        if validation_results["semantic_support"]["facts_used"] < 2:
            validation_results["recommendations"].append(
                "Consider adding more fact-based evidence for stronger reasoning"
            )
        
        if validation_results["semantic_support"]["assumptions_checked"] > 2:
            validation_results["recommendations"].append(
                "High number of assumptions detected - consider gathering more facts"
            )
        
        return validation_results
    
    def _find_matching_fact(self, text: str) -> Optional[Fact]:
        """Find a fact that matches the given text."""
        for fact in self.facts:
            if fact.statement.lower() in text.lower() or text.lower() in fact.statement.lower():
                return fact
        return None
    
    def _find_matching_claim(self, text: str) -> Optional[Claim]:
        """Find a claim that matches the given text."""
        for claim in self.claims:
            if claim.statement.lower() in text.lower() or text.lower() in claim.statement.lower():
                return claim
        return None
    
    def _find_matching_assumption(self, text: str) -> Optional[Assumption]:
        """Find an assumption that matches the given text."""
        for assumption in self.assumptions:
            if assumption.statement.lower() in text.lower() or text.lower() in assumption.statement.lower():
                return assumption
        return None


# ==================== Usage Examples ====================

def example_fact_integration():
    """Example: How Facts integrate with CoT reasoning."""
    integration = SemanticIntegration()
    
    # Create a fact
    fact = Fact(
        statement="The parse_data function is located in processor.py at line 23",
        is_verifiable=True,
        is_objective=True,
        source="processor.py:23"
    )
    integration.facts.append(fact)
    
    # Integrate with CoT decision
    cot_result = integration.integrate_fact_with_cot(
        fact,
        "Move parse_data function to new parser.py file"
    )
    
    print("FACT → CoT Integration Example:")
    print(json.dumps(cot_result, indent=2))
    return cot_result


def example_claim_integration():
    """Example: How Claims trigger evidence gathering in CoT."""
    integration = SemanticIntegration()
    
    # Add supporting facts
    fact1 = Fact(
        statement="processor.py contains 500+ lines of code",
        is_verifiable=True,
        is_objective=True,
        source="wc -l processor.py"
    )
    fact2 = Fact(
        statement="Single Responsibility Principle states one class should have one reason to change",
        is_verifiable=True,
        is_objective=True,
        source="SOLID principles documentation"
    )
    integration.facts.extend([fact1, fact2])
    
    # Create a claim
    claim = Claim(
        statement="processor.py violates Single Responsibility Principle",
        confidence=0.8,
        source="code review"
    )
    integration.claims.append(claim)
    
    # Integrate with CoT
    cot_result = integration.integrate_claim_with_cot(
        claim,
        "Refactor processor.py to separate concerns"
    )
    
    print("\nCLAIM → CoT Integration Example:")
    print(json.dumps(cot_result, indent=2, default=str))
    return cot_result


def example_assumption_integration():
    """Example: How Assumptions define boundaries in CoT reasoning."""
    integration = SemanticIntegration()
    
    # Create an assumption
    assumption = Assumption(
        statement="Performance optimization is not a priority",
        scope="MVP development phase"
    )
    integration.assumptions.append(assumption)
    
    # Integrate with CoT
    cot_result = integration.integrate_assumption_with_cot(
        assumption,
        "Use simple bubble sort algorithm for now",
        "MVP development phase"
    )
    
    print("\nASSUMPTION → CoT Integration Example:")
    print(json.dumps(cot_result, indent=2, default=str))
    return cot_result


def example_contradiction_detection():
    """Example: How contradictions are detected and halt reasoning."""
    integration = SemanticIntegration()
    
    # Add conflicting semantic objects
    fact = Fact(
        statement="Database must use PostgreSQL",
        is_verifiable=True,
        is_objective=True,
        source="requirements.md"
    )
    
    claim = Claim(
        statement="Database must use MySQL",
        confidence=0.9,
        source="team discussion"
    )
    
    integration.facts.append(fact)
    integration.claims.append(claim)
    
    # Detect contradictions
    conflicts = integration.detect_contradictions()
    
    print("\nContradiction Detection Example:")
    for conflict in conflicts:
        print(f"- {conflict.type.value}: {conflict.description}")
        print(f"  Severity: {conflict.severity}")
        print(f"  Resolution: {conflict.resolution_strategy}")
    
    return conflicts


def example_validation_pipeline():
    """Example: Complete validation of CoT trace with semantic layer."""
    integration = SemanticIntegration()
    
    # Setup semantic layer
    integration.facts.append(Fact(
        statement="API must be RESTful",
        is_verifiable=True,
        is_objective=True,
        source="api_spec.md"
    ))
    
    integration.claims.append(Claim(
        statement="GraphQL would improve performance",
        confidence=0.7,
        source="performance analysis"
    ))
    
    integration.assumptions.append(Assumption(
        statement="Team has GraphQL expertise",
        scope="development team"
    ))
    
    # Mock CoT trace
    cot_trace = {
        "decision": "Migrate from REST to GraphQL",
        "evidence_collection": [
            {
                "quote": "API must be RESTful",
                "source": "api_spec.md"
            },
            {
                "quote": "GraphQL would improve performance",
                "source": "analysis"
            },
            {
                "quote": "Team has GraphQL expertise",
                "source": "assumption"
            }
        ]
    }
    
    # Validate
    validation_result = integration.validate_cot_with_semantics(cot_trace)
    
    print("\nValidation Pipeline Example:")
    print(json.dumps(validation_result, indent=2))
    
    return validation_result


if __name__ == "__main__":
    print("=" * 60)
    print("SEMANTIC LAYER → CoT INTEGRATION EXAMPLES")
    print("=" * 60)
    
    example_fact_integration()
    example_claim_integration()
    example_assumption_integration()
    example_contradiction_detection()
    example_validation_pipeline()
    
    print("\n" + "=" * 60)
    print("Integration examples completed successfully!")