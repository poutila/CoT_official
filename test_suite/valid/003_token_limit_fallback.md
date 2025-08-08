## 🧠 Reasoning Trace (Chain-of-Thought)

```yaml
schema: chain_of_thought/v7.0.0
validation: required
runtime_contract: 2.0.0
token_usage: 3500
token_limit: 4000
fallback_strategy: summarize
```

**Context Level**: Full File Access
**Available Tools**: File reading, grep search

### Decision: Refactor large module into smaller components

#### Token Usage:
- **Current**: 3,500 tokens (87.5%)
- **Remaining**: 500 tokens
- **Action**: Applying summarization fallback

#### Risk Assessment:
- **Change Type**: Split large module
- **Risk Level**: High
- **Impact Scope**: Module-wide
- **Reversibility**: Moderate effort

#### Evidence Collection (Summarized):
Total evidence items: 8
Showing top 3 by relevance:

1. **Source**: `code_review.md:102-150`
   **Quote**: "payments.py has grown to 2,500 lines..."
   **Relevance**: Primary justification for split
   **Timestamp**: 
     - Modified: 2024-01-25T10:00:00Z
   **Freshness**: current (0.99)

2. **Source**: `sonarqube_report.json:45`
   **Quote**: "Cyclomatic complexity: 47 (threshold: 10)"
   **Relevance**: Exceeds complexity limits
   **Timestamp**:
     - Created: 2024-01-26T08:00:00Z
   **Freshness**: current (1.0)

3. **Source**: `architecture_guidelines.md § 2.1`
   **Quote**: "Modules should not exceed 500 lines"
   **Relevance**: Violates size guidelines
   **Timestamp**:
     - Version: 3.0.0
   **Freshness**: current (0.95)

[5 additional evidence items omitted for token conservation]

#### Analysis Summary:
- Split into: payment_processing.py, payment_validation.py, payment_reporting.py
- Dependencies mapped
- Migration path defined

#### Validation:
- [✓] Evidence threshold met (8 > 3 required)
- [✓] Token budget managed
- [✓] Fallback applied successfully

#### Action:
→ Therefore, I will: Execute module split per summarized plan

### Reasoning Envelope Applied:
- Strategy: summarize
- Full trace hash: sha256:a7b9c2d4e5f6...