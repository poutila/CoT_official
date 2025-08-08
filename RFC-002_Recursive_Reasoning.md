# 🔁 RFC-002: Recursive Reasoning Contract

## Purpose

Allow CoT-based AI agents to reason about their own reasoning steps without infinite recursion or hallucinated prompt generation.

## Problem

Some tasks require:
- A prompt to generate another prompt
- A plan to reason about a plan
- A validator to review reasoning traces

This recursive behavior must be explicitly bounded.

## Specification

| Field | Type | Description |
|-------|------|-------------|
| `recursion_allowed` | `bool` | Whether recursion is permitted |
| `recursion_depth_max` | `int` | Maximum depth of prompt-generating-prompt |
| `reasoning_compound_type` | `flat` \| `layered` | Whether the reasoning is single-trace or multi-hop |

## Runtime Behavior

- If `recursion_depth_max` exceeded → HALT with `RECURSION_LIMIT_EXCEEDED`
- If CoT is self-bootstrapping → Include meta-trace section explaining the layers
