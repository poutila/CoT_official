# 🧠 RFC-001: CoT Applicability Heuristics

## Purpose

Define criteria and thresholds for when Chain-of-Thought (CoT) reasoning is required, optional, or unnecessary.

## Motivation

Blindly applying CoT to every task can result in unnecessary complexity, latency, and cost. This RFC proposes a decision matrix for applying CoT based on context and risk level.

## CoT Applicability Levels

| Risk Level   | CoT Required? | Example Use Case |
|--------------|---------------|------------------|
| High         | ✅ Always     | Refactor plans, deletions, irreversible mutations |
| Medium       | ✅ If time allows | Naming conventions, optional transformations |
| Low          | ❌ Avoid      | Linting, formatting, docstring padding |

## Decision Criteria

1. **Irreversibility**: If action cannot be undone → Apply CoT.
2. **Impact Surface**: If >1 module is affected → Apply CoT.
3. **User-visible Behavior**: If behavior or API changes → Apply CoT.
4. **Security/Validation Path**: If security logic is touched → Always CoT.
