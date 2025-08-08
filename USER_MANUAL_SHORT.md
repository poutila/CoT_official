# Chain-of-Thought (CoT) Quick Start Guide

## What is CoT?

Chain-of-Thought (CoT) is a structured reasoning methodology that enforces evidence-based decision-making in AI systems. It requires explicit citations, risk assessment, and deferral when evidence is insufficient.

## When to Use CoT

CoT is **mandatory** for:
- Code generation or modification
- Architectural decisions
- File/function reorganization
- Dependency analysis
- Any task requiring justified decisions

## The 4 Core Rules

### R1: Reference Specific Inputs
```markdown
**Source**: `config.py:45`
**Quote**: "DATABASE_URL = 'localhost'"
```

### R2: Explain Decisions with Evidence
- **What**: The action being taken
- **Why**: Evidence supporting it (min. 2 sources)
- **Why Not**: Why alternatives were rejected
- **Impact**: What this affects

### R3: Justify Using Exact Citations
- Quote exact text (no paraphrasing)
- Preserve original wording
- Use [...] for modifications

### R4: Defer When Evidence Is Insufficient
```markdown
⚠️ DEFERRED: Cannot determine if module is used
- Available evidence: No static imports found
- Missing evidence: Dynamic import check needed
- Recommended action: Search for __import__ usage
```

## Quick Template

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: [What you're doing]

#### Risk Assessment:
- **Change Type**: [Delete/Modify/Move/etc.]
- **Risk Level**: [Low/Medium/High/Critical]
- **Impact Scope**: [Single file/Module/System-wide]
- **Reversibility**: [Easy/Difficult/Irreversible]

#### Evidence Collection:
1. **Source**: `filename.py:123`
   **Quote**: "exact text"
   **Relevance**: Why this matters

2. **Source**: `doc.md § 4.2`
   **Quote**: "requirement text"
   **Relevance**: Why this mandates action

#### Analysis:
- **Primary rationale**: Main reason with evidence
- **Alternative considered**: What else you evaluated
- **Alternative rejected because**: Specific reason

#### Action:
→ Therefore, I will: [Specific action]
```

## Risk-Based Evidence Requirements

| Risk | Min. Sources | When to Defer |
|------|--------------|---------------|
| Low | 1 | Never |
| Medium | 2 | If conflicting |
| High | 3 | If <3 sources |
| Critical | 4 | Any uncertainty |

## Validation Tools

```bash
# Validate a CoT bundle
python validate_bundle.py chain_of_thought.bundle.json

# Check your reasoning trace
python validate_bundle.py --verify-trace my_reasoning.md

# Run with specific version
python validate_bundle.py --cot-version 7.0.0
```

## Common Mistakes to Avoid

❌ **DON'T**:
- "This probably means..."
- "Following best practices..."
- "While I'm here, I'll also..."
- Make assumptions without evidence

✅ **DO**:
- "Line 45 explicitly states..."
- "The plan specifically requires..."
- Quote exact evidence
- Defer when uncertain

## Integration Example

```python
from cot_validator import ChainOfThoughtReasoner

reasoner = ChainOfThoughtReasoner(version="7.0.0")
trace = reasoner.reason(
    decision="Remove unused function",
    context={"file_access": "full"},
    risk_level="medium"
)

if reasoner.validate(trace):
    print(trace.to_markdown())
else:
    print(f"Invalid: {trace.errors}")
```

## Quick Checklist

Before proceeding with any decision:
- [ ] Have I cited specific sources?
- [ ] Do I have enough evidence for the risk level?
- [ ] Have I considered alternatives?
- [ ] Am I making any assumptions?
- [ ] Should I defer this decision?

## Resources

- Full Specification: `CHAIN_OF_THOUGHT.md`
- Examples: `examples/` directory
- Validation: `validate_bundle.py`
- Support: cot-standard.org