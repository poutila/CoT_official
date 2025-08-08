# ⏳ CoT_REASONING_ENVELOPE.md

## Purpose

Define operational limits and fallback strategies for CoT reasoning under constrained environments (e.g., limited token budgets, live agents, or partial context).

## Fields

| Field | Description |
|-------|-------------|
| `token_budget_soft` | Soft warning threshold in tokens |
| `token_budget_hard` | Hard cutoff for reasoning trace |
| `fallback_strategy` | How to degrade reasoning if space runs out |

## Degradation Modes

- `summarize`: Replace full trace with compressed summary + hash
- `defer_partial`: Return only validated trace steps, defer remainder
- `split_trace`: Chunk reasoning into continuation prompts

## Example Envelope

```yaml
reasoning_envelope:
  token_budget_soft: 3000
  token_budget_hard: 4000
  fallback_strategy: summarize
```
