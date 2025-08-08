## 🧠 Reasoning Trace (Chain-of-Thought)

```yaml
schema: chain_of_thought/v7.0.0
validation: required
runtime_contract: 2.0.0
recursion_depth: 1
```

**Context Level**: Full File Access
**Available Tools**: File reading, grep search, prompt generation

### Decision: Generate a prompt to analyze code complexity

#### Risk Assessment:
- **Change Type**: Generate analysis prompt
- **Risk Level**: Low
- **Impact Scope**: Single analysis task
- **Reversibility**: N/A (read-only analysis)

#### Evidence Collection:
1. **Source**: `PROMPT_FOR_PROMPT_GENERATION.md:14`
   **Quote**: "Goal: Generate a prompt that creates prompts without external file references"
   **Relevance**: Confirms recursive prompt generation is supported
   **Timestamp**:
     - Created: 2024-01-26T08:00:00Z
     - Modified: 2024-01-26T11:00:00Z
     - Accessed: 2024-01-26T12:00:00Z
   **Freshness**: current (score: 1.0)

2. **Source**: `RFC-002_Recursive_Reasoning.md:21-23`
   **Quote**: "recursion_depth_max: Maximum depth of prompt-generating-prompt"
   **Relevance**: Validates recursion is allowed with depth limits
   **Timestamp**:
     - Created: 2024-01-26T09:00:00Z
     - Modified: 2024-01-26T09:00:00Z
     - Accessed: 2024-01-26T12:00:00Z
   **Freshness**: current (score: 1.0)

#### Analysis:
- **Primary rationale**: Need to generate a specialized analysis prompt
- **Alternative considered**: Use direct analysis without prompt generation
- **Alternative rejected because**: Specialized prompt ensures consistent analysis

#### Meta-Reasoning Trace:
This is a recursive reasoning task (depth 1 of max 2):
- Level 0: Decision to generate prompt
- Level 1: The generated prompt itself (not yet created)

#### Validation:
- [✓] Minimum 2 evidence sources cited
- [✓] No assumptions made beyond quoted text
- [✓] Recursion depth within limits (1 < 2)
- [✓] Meta-trace included for recursion

#### Action:
→ Therefore, I will: Generate a prompt template for analyzing code complexity that includes:
1. Metrics to calculate (cyclomatic complexity, nesting depth)
2. Thresholds for concern (>10 complexity, >3 nesting)
3. Output format (markdown report)
4. No external dependencies