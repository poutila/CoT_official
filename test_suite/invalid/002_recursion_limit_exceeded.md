## 🧠 Reasoning Trace (Chain-of-Thought)

```yaml
schema: chain_of_thought/v7.0.0
validation: required
runtime_contract: 2.0.0
recursion_depth: 3
```

**Context Level**: Full File Access
**Available Tools**: Prompt generation

### Decision: Generate a prompt to generate a prompt to analyze code

#### Risk Assessment:
- **Change Type**: Multi-level prompt generation
- **Risk Level**: Low
- **Impact Scope**: Analysis only
- **Reversibility**: N/A

#### Evidence Collection:
1. **Source**: `complex_analysis_requirements.md:12`
   **Quote**: "Need meta-meta-analysis capabilities"
   **Relevance**: Justifies deep recursion need
   **Timestamp**:
     - Created: 2024-01-26T10:00:00Z
     - Modified: 2024-01-26T10:00:00Z
     - Accessed: 2024-01-26T12:00:00Z
   **Freshness**: current (score: 1.0)

#### Analysis:
- **Primary rationale**: Complex analysis requires multiple abstraction levels
- **Alternative considered**: Direct analysis
- **Alternative rejected because**: Insufficient abstraction

#### Meta-Reasoning Trace:
Recursion stack:
- Level 0: Generate top-level prompt generator
- Level 1: Generate mid-level analyzer prompt
- Level 2: Generate base analysis prompt
- Level 3: Actual analysis execution

#### Validation:
- [✓] Evidence cited
- [✓] No assumptions made
- [✗] Recursion depth exceeds limit (3 > 2)
- [✓] Meta-trace included

#### Action:
→ Therefore, I will: ERROR - RECURSION_LIMIT_EXCEEDED