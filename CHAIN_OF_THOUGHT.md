# 🧠 CHAIN_OF_THOUGHT.md

**Version**: 7.0.0
**Status**: Official Standard
**Authority**: [CoT Standards Committee](COT_STANDARD_AUTHORITY.md)
**Contract**: [Runtime Contract v2.0.0](COT_RUNTIME_CONTRACT.json)
**Interoperability**: [Integration Guide](COT_INTEROPERABILITY.md)

## 🎯 Purpose

This document defines the **mandatory Chain-of-Thought (CoT)** reasoning requirements for AI assistants performing analytical, development, or decision-making tasks.

**CORE PRINCIPLE**: AI is strictly forbidden from making assumptions, inferring unspecified intentions, or bypassing the reasoning process. Every decision must be traceable to explicit evidence.

**CoT is MANDATORY** in all phases involving:
- Code generation or modification
- Architectural decisions
- Plan creation or updates
- File/function reorganization
- Dependency analysis
- Document generation
- Problem solving
- Any task requiring justified decisions

---

## 🔍 Chain-of-Thought Definition

**Chain-of-Thought (CoT)** is a structured reasoning methodology with these **non-negotiable requirements**:

### 1. Reference Specific Inputs (R1)
- **MUST** cite exact file paths and line numbers
- **MUST** quote relevant text verbatim
- **MUST** use format: `filename.ext:line_number` or `document_name § section`
- **FORBIDDEN**: Vague references like "the code suggests" or "it seems like"

### 2. Explain Decisions with Evidence (R2)
Each decision **MUST** include:
- **What**: The specific action being taken
- **Why**: Direct evidence supporting this action (minimum 2 sources)
- **Why Not**: Why alternative approaches were rejected
- **Impact**: What this change affects

### 3. Justify Using Exact Citations (R3)
- **MUST** quote the exact text that justifies the action
- **MUST** preserve original wording in quotes
- **MUST** indicate modifications with [...]
- **FORBIDDEN**: Paraphrasing evidence or summarizing loosely

### 4. Defer When Evidence Is Insufficient (R4)
**Deferral is REQUIRED** when:
- Fewer than 2 corroborating sources exist
- Sources conflict without resolution path
- Intent cannot be determined from explicit text
- Dynamic behavior might differ from static analysis

### 5. Every file in project needs to be read from top to bottom (R5)
- **MUST** Have knowledge of every file's content in project directory

**Deferral Format**:
```
⚠️ DEFERRED: [Specific issue]
- Available evidence: [What we know]
- Missing evidence: [What we need]
- Recommended action: [How to proceed]
```

---

## ✅ Required Output Format

### Structure Requirements

Every CoT output **MUST** follow this exact structure:

### Standardized Trace Header Template

The `cot_trace_header` block provides a machine-parseable header for all traces:

```yaml
cot_trace_header:
  # Specification compliance
  specification:
    schema: chain_of_thought/v7.0.0
    validation: required
    runtime_contract: 2.0.0

  # Context information
  context:
    level: full_file_access
    tools: [file_reading, grep_search, ast_parsing]
    timestamp: 2024-01-26T12:00:00Z
    session_id: optional-session-identifier

  # Risk and requirements
  risk_profile:
    risk_level: medium
    evidence_required: 2
    evidence_provided: 3

  # Optional: Recursion control
  recursion:
    enabled: false
    current_depth: 0
    max_depth: 2

  # Optional: Token management
  token_management:
    current_usage: 1500
    limit: 4000
    fallback: summarize

  # Optional: Performance hints
  performance:
    estimated_complexity: 0.75
    expected_duration_ms: 500
```

This header can be parsed independently from the markdown content for automated processing.

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

```yaml
# Required fields matching runtime contract
schema: chain_of_thought/v7.0.0
validation: required
runtime_contract: 2.0.0

# Optional fields from contract
context_level: full_file_access  # Enum: full_file_access|summary_only|chat_context|mixed|undefined
risk_level: medium               # Enum: low|medium|high|critical
output_format: markdown          # Enum: markdown|json|yaml

# Recursion fields (if applicable)
recursion_allowed: false         # Default: false
recursion_depth: 0              # Current depth (max: 2)
reasoning_compound_type: flat    # Enum: flat|layered

# Token management (if approaching limits)
token_usage: 1500               # Current token count
token_limit: 4000               # Maximum allowed
fallback_strategy: summarize    # Enum: summarize|defer_partial|split_trace

# Evidence requirements (based on risk)
min_evidence_required: 2        # Low:1, Medium:2, High:3, Critical:5
evidence_count: 3               # Actual count in this trace
```

**Context Level**: [Full File Access / Summary Only / Chat Context / Mixed / Undefined]
**Available Tools**: [List available tools/access levels]

### Decision: [Specific action to be taken]

#### Risk Assessment:
- **Change Type**: [Delete file / Modify API / Move function / etc.]
- **Risk Level**: [Low/Medium/High/Critical]
- **Impact Scope**: [Single file / Module / System-wide]
- **Reversibility**: [Easily reversible / Difficult / Irreversible]

#### Evidence Collection:
1. **Source**: `filename.py:123-125`
   **Quote**: "exact text from source"
   **Relevance**: How this supports the decision
   **Timestamp**:
     - Created: 2024-01-01T10:00:00Z
     - Modified: 2024-01-20T15:30:00Z
     - Accessed: 2024-01-26T09:00:00Z
   **Freshness**: current (score: 0.95)

2. **Source**: `requirements_document.md § 4.2`
   **Quote**: "exact requirement text"
   **Relevance**: Why this mandates the action

#### Analysis:
- **Primary rationale**: [Main reason with evidence refs]
- **Alternative considered**: [What else was evaluated]
- **Alternative rejected because**: [Specific reason with evidence]

#### Validation:
- [ ] Minimum 2 evidence sources cited
- [ ] No assumptions made beyond quoted text
- [ ] All affected files identified
- [ ] Edge cases addressed or deferred

#### Action:
→ Therefore, I will: [Specific, measurable action]
```

### Minimum Requirements Checklist
- **✓ At least 3 evidence citations** (except for trivial operations)
- **✓ Maximum 5 reasoning steps** (break complex decisions into parts)
- **✓ Every claim backed by quote**
- **✓ Explicit handling of null/missing cases**

---

## 🛑 What Is NOT Allowed

### Forbidden Patterns (Automatic Rejection)

1. **Assumption-Based Reasoning**
   - ❌ "This probably means..."
   - ❌ "It's common practice to..."
   - ❌ "The developer likely intended..."
   - ✅ "Line 45 explicitly states..."

2. **Scope Creep**
   - ❌ "While I'm here, I'll also fix..."
   - ❌ "This could be improved by..."
   - ❌ "Added bonus optimization..."
   - ✅ "The plan specifically requires..."

3. **Unjustified Decisions**
   - ❌ "Moving to improve structure"
   - ❌ "Refactoring for clarity"
   - ❌ "Following best practices"
   - ✅ "Moving parse() because requirements.md §3 states 'extract parsing to dedicated module'"

4. **Vague Deferral**
   - ❌ "This is unclear"
   - ❌ "Need more information"
   - ❌ "Can't determine intent"
   - ✅ "DEFERRED: Cannot determine if dynamic import at line 78 loads this module"

5. **Surface-Level Conclusions**
   - ❌ "X appears to be unused"
   - ❌ "No references found, so it's redundant"
   - ❌ "Seems unnecessary based on current code"
   - ✅ "After checking: direct imports (0), dynamic imports (0), config references (0), external tool requirements (pending)"

---

## 📊 Examples

### ✅ GOOD: Complete Reasoning Trace

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

```yaml
schema: chain_of_thought/v7.0.0
validation: required
runtime_contract: 2.0.0
```

**Context Level**: Full File Access
**Available Tools**: File reading, grep search, directory listing

### Decision: Extract parse_data() from processor.py to new parser.py

#### Risk Assessment:
- **Change Type**: Move function to new module
- **Risk Level**: Medium
- **Impact Scope**: Module (requires import updates)
- **Reversibility**: Easily reversible

#### Evidence Collection:
1. **Source**: `technical_review.md:47-49`
   **Quote**: "processor.py violates SRP by combining parsing and processing"
   **Relevance**: Identifies the specific violation requiring separation
   **Timestamp**:
     - Created: 2024-01-20T14:00:00Z
     - Modified: 2024-01-20T14:00:00Z
     - Accessed: 2024-01-26T10:00:00Z
   **Freshness**: current (score: 0.98)

2. **Source**: `architecture_plan.md § 4.1`
   **Quote**: "Create parser.py and move all parsing logic from processor.py"
   **Relevance**: Provides explicit instruction for the refactor
   **Timestamp**:
     - Created: 2024-01-15T09:00:00Z
     - Modified: 2024-01-19T16:30:00Z
     - Accessed: 2024-01-26T10:00:00Z
     - Version: 1.2.0
   **Freshness**: current (score: 0.95)

3. **Source**: `processor.py:23-45`
   **Quote**: "def parse_data(self, content: str) -> DataStructure:"
   **Relevance**: Identifies the exact function to be moved
   **Timestamp**:
     - Created: 2023-12-01T12:00:00Z
     - Modified: 2024-01-15T11:00:00Z
     - Accessed: 2024-01-26T10:00:00Z
   **Freshness**: recent (score: 0.85)

#### Analysis:
- **Primary rationale**: SRP violation confirmed by review + explicit architecture instruction
- **Alternative considered**: Keep in processor.py with better organization
- **Alternative rejected because**: architecture_plan.md § 4.1 mandates separate file

#### Validation:
- [✓] Minimum 2 evidence sources cited (have 3)
- [✓] No assumptions made beyond quoted text
- [✓] All affected files identified (processor.py, new parser.py)
- [✓] Edge cases addressed (import updates covered in plan § 4.2)
- [✓] Reasoning chains: 2/5 (within limit)
- [✓] Evidence sources: 3/10 (within limit)

#### Action:
→ Therefore, I will: Move parse_data() method from processor.py:23-45 to new file parser.py
```

### ❌ BAD: Insufficient Reasoning

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

Moving parsing logic to improve code organization per plan.
This will make the code cleaner and easier to maintain.
```
**Rejection Reasons**:
- No specific evidence citations
- No line numbers or quotes
- Vague justification
- Missing validation checklist

### ⚠️ GOOD: Proper Deferral

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: DEFERRED - Cannot determine if utility_module.py should be removed

#### Evidence Collection:
1. **Source**: `utility_module.py:1-200`
   **Quote**: "class UtilityHelper: # Legacy implementation"
   **Relevance**: Suggests deprecated status but not definitive

2. **Source**: `grep -r "UtilityHelper" --include="*.py"`
   **Quote**: No import statements found
   **Relevance**: No static imports, but dynamic imports possible

#### Analysis:
⚠️ DEFERRED: Insufficient evidence for safe removal
- Available evidence: No static imports, marked as "Legacy"
- Missing evidence: Dynamic import check, configuration file usage
- Recommended action:
  1. Search for dynamic imports: `__import__`, `importlib`
  2. Check configuration files for class name references
  3. Verify with codebase owner about legacy status
```

### ⚠️ EXAMPLE: Undefined Context Handling

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

```yaml
schema: chain_of_thought/v7.0.0
validation: required
runtime_contract: 2.0.0
```

**Context Level**: Undefined
**Available Tools**: Unknown/Uncertain

⚠️ CONTEXT UNCERTAINTY DETECTED
- Operating in conservative mode
- Elevated evidence requirements active
- Deferral threshold lowered
- All actions require additional verification

### Decision: DEFERRED - Cannot verify context for safe refactoring

#### Risk Assessment:
- **Change Type**: Unknown scope
- **Risk Level**: High (elevated due to context uncertainty)
- **Impact Scope**: Cannot determine
- **Reversibility**: Unknown

#### Evidence Collection:
1. **Source**: `provided text claiming to be config.py`
   **Quote**: "DATABASE_URL = 'localhost'"
   **Relevance**: May indicate configuration that needs updating
   **Context**: Unable to verify source authenticity

2. **Source**: `user instruction`
   **Quote**: "update all database references"
   **Relevance**: Indicates scope of change
   **Context**: Direct instruction but cannot verify codebase state

#### Analysis:
⚠️ DEFERRED: Insufficient context for safe execution
- Available evidence: User instruction only
- Missing evidence: Cannot verify file contents, cannot confirm tools
- Recommended action:
  1. Request explicit file content verification
  2. Confirm available tool access
  3. Clarify scope of database references
```

---

## 🔒 Enforcement & Validation

### Automated Validation Rules

1. **Structural Compliance**
   - MUST contain `## 🧠 Reasoning Trace` header
   - MUST have all required sections
   - MUST include validation checklist

2. **Evidence Quality Metrics**
   - Each citation must include source + quote + relevance
   - Quotes must be >10 characters (prevent empty citations)
   - File paths must exist in repository

3. **Rejection Triggers**
   - Missing citations → Immediate rejection
   - Assumptions without evidence → Immediate rejection
   - Scope creep → Immediate rejection
   - Incomplete validation checklist → Return for completion

### Manual Review Criteria

Reviewers will verify:
1. Evidence actually supports the stated decision
2. Alternatives were genuinely considered
3. Edge cases are addressed or properly deferred
4. No hidden assumptions in reasoning

---

## 📐 Decision Flowchart

```
Start → Collect Evidence → Enough Evidence (≥2 sources)?
                               ↓ No            ↓ Yes
                          Defer Action    Analyze Evidence
                                              ↓
                                    Conflicts Found?
                                    ↓ Yes      ↓ No
                              Defer Action   Document Decision
                                              ↓
                                       Validate Checklist
                                              ↓
                                        Format Output
```

---

## ⚖️ Risk-Based Requirements

### Risk Levels and Evidence Requirements

| Risk Level | Impact | Min. Sources | Examples | Deferral Threshold |
|------------|--------|--------------|----------|-------------------|
| **Low** | Minimal, reversible | 1 source | Rename variable, add comment | Never defer |
| **Medium** | Local module changes | 2 sources | Move function, refactor class | Defer if conflicting |
| **High** | Cross-module impact | 3 sources | Change API, modify interface | Defer if <3 sources |
| **Critical** | System-wide/Breaking | 4 sources | Delete module, change architecture | Defer if any uncertainty |

### Risk Assessment Required in Reasoning

```markdown
#### Risk Assessment:
- **Change Type**: [Delete file / Modify API / Move function / etc.]
- **Risk Level**: [Low/Medium/High/Critical]
- **Impact Scope**: [Single file / Module / System-wide]
- **Reversibility**: [Easily reversible / Difficult / Irreversible]
```

---

## ⏰ Temporal Reasoning

### Evidence Freshness Requirements

All evidence MUST include temporal context:

1. **File Evidence**:
   ```
   **Source**: `config.py:45` (last modified: 2024-01-15)
   **Quote**: "DATABASE_URL = 'localhost:5432'"
   **Freshness**: Current as of analysis date
   ```

2. **Documentation Evidence**:
   ```
   **Source**: `API_GUIDE.md § 3.2` (version: 2.1.0, dated: 2023-12-01)
   **Quote**: "All endpoints require authentication"
   **Freshness**: May be outdated - verify against current implementation
   ```

### Freshness Score Calculation

Calculate evidence freshness score (0.0-1.0) using:

```python
def calculate_freshness_score(evidence_timestamp, context):
    """
    Calculate freshness score based on evidence age and type.

    Returns:
        float: 0.0 (completely stale) to 1.0 (current)
    """
    now = datetime.now(timezone.utc)
    age_days = (now - evidence_timestamp.modified).days

    # Base score from age
    if age_days <= 1:
        base_score = 1.0
    elif age_days <= 7:
        base_score = 0.95
    elif age_days <= 30:
        base_score = 0.85
    elif age_days <= 90:
        base_score = 0.70
    else:
        base_score = max(0.5 - (age_days - 90) / 365, 0.0)

    # Adjust for evidence type
    if context.evidence_type == "security_policy":
        # Security evidence degrades faster
        return base_score * 0.8
    elif context.evidence_type == "architecture_decision":
        # Architecture decisions are more stable
        return min(base_score * 1.1, 1.0)

    return base_score
```

### Staleness Indicators

Evidence is considered **potentially stale** when:
- File modified >30 days ago without recent commits (score < 0.85)
- Documentation version >2 major versions behind
- Comments reference deprecated systems
- No recent test coverage
- Freshness score < 0.7

**Required Action for Stale Evidence**:
```
⚠️ STALE EVIDENCE WARNING:
- Source last updated: [date]
- Recommend verification via: [specific check]
- Alternative evidence sources: [list options]
```

---

## 🔧 Machine-Readable Validation

### JSON Schema for CoT Validation

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Chain-of-Thought Reasoning Trace v7.0",
  "type": "object",
  "required": ["decision", "evidence_collection", "analysis", "validation", "action"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["mode", "complexity_score"],
      "properties": {
        "mode": {"enum": ["standard", "fast-path", "streaming", "recursive"]},
        "complexity_score": {"type": "number", "minimum": 0, "maximum": 100},
        "parent_decision": {"type": "string"},
        "compression_level": {"type": "integer", "minimum": 0, "maximum": 3},
        "streaming_version": {"type": "integer", "minimum": 0}
      }
    },
    "decision": {
      "type": "string",
      "minLength": 10,
      "description": "Specific action to be taken"
    },
    "risk_assessment": {
      "type": "object",
      "required": ["change_type", "risk_level", "impact_scope"],
      "properties": {
        "change_type": {"type": "string"},
        "risk_level": {"enum": ["Low", "Medium", "High", "Critical"]},
        "impact_scope": {"type": "string"},
        "reversibility": {"type": "string"}
      }
    },
    "evidence_collection": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["source", "quote", "relevance", "timestamp"],
        "properties": {
          "source": {
            "type": "string",
            "pattern": "^.+:(\\d+(-\\d+)?|§.+)$|^.+\\s+\\(.*\\)$"
          },
          "quote": {"type": "string", "minLength": 10},
          "relevance": {"type": "string", "minLength": 20},
          "timestamp": {
            "type": "object",
            "required": ["created"],
            "properties": {
              "created": {"type": "string", "format": "date-time"},
              "modified": {"type": "string", "format": "date-time"},
              "accessed": {"type": "string", "format": "date-time"},
              "version": {"type": "string"}
            }
          },
          "freshness": {
            "type": "string",
            "enum": ["current", "recent", "stale", "unknown"],
            "description": "Computed freshness based on timestamp"
          },
          "freshness_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "0.0 = stale, 1.0 = current"
          }
        }
      }
    },
    "analysis": {
      "type": "object",
      "required": ["primary_rationale", "alternative_considered", "alternative_rejected_because"],
      "properties": {
        "primary_rationale": {"type": "string", "minLength": 30},
        "alternative_considered": {"type": "string", "minLength": 20},
        "alternative_rejected_because": {"type": "string", "minLength": 20},
        "conflict_resolution": {
          "type": "object",
          "properties": {
            "strategy": {"enum": ["weighted_consensus", "authority_cascade", "temporal_precedence"]},
            "evidence_weights": {"type": "array", "items": {"type": "number"}},
            "minority_report": {"type": "string"}
          }
        }
      }
    },
    "validation": {
      "type": "object",
      "required": ["minimum_sources_met", "no_assumptions_made", "affected_files_identified", "edge_cases_addressed"],
      "properties": {
        "minimum_sources_met": {"type": "boolean"},
        "no_assumptions_made": {"type": "boolean"},
        "affected_files_identified": {"type": "boolean"},
        "edge_cases_addressed": {"type": "boolean"}
      }
    },
    "action": {
      "type": "string",
      "pattern": "^→ Therefore, I will: .+",
      "minLength": 25
    }
  },
  "if": {
    "properties": {
      "risk_assessment": {
        "properties": {
          "risk_level": {"const": "Critical"}
        }
      }
    }
  },
  "then": {
    "properties": {
      "evidence_collection": {
        "minItems": 4
      }
    }
  }
}
```

### Validation Example (Python)

```python
import json
import jsonschema

def validate_cot_reasoning(reasoning_dict):
    """Validate a Chain-of-Thought reasoning trace against the schema."""
    with open('cot_schema.json', 'r') as f:
        schema = json.load(f)

    try:
        jsonschema.validate(reasoning_dict, schema)
        return True, "Valid reasoning trace"
    except jsonschema.ValidationError as e:
        return False, f"Invalid: {e.message}"
```

---

## 🔄 Context-Aware Citation Formats

### Citation Formats by AI Context

1. **Full File Access** (Default):
   ```
   **Source**: `module.py:123-125`
   **Quote**: "exact code from file"
   ```

2. **Limited Context (Summaries Only)**:
   ```
   **Source**: `module.py summary`
   **Quote**: "Module description states: handles user authentication"
   **Context**: Limited to file summary, not full content
   ```

3. **Chat/Conversation Context**:
   ```
   **Source**: `User message (2024-01-20 14:30 UTC)`
   **Quote**: "Please refactor the authentication system"
   **Context**: Direct user instruction
   ```

4. **API/Tool Response**:
   ```
   **Source**: `grep tool output`
   **Quote**: "Found 5 matches for 'authenticate' in src/"
   **Context**: Tool-generated evidence
   ```

5. **Documentation without Line Numbers**:
   ```
   **Source**: `README section "Installation"`
   **Quote**: "Requires Python 3.8 or higher"
   **Context**: Section-based reference
   ```

### Context Declaration Required

Every reasoning trace MUST declare its context level:

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

**Context Level**: [Full File Access / Summary Only / Chat Context / Mixed / Undefined]
**Available Tools**: [List available tools/access levels]
```

---

## 🔍 Context Uncertainty Protocol

### When Context is Undefined

If the AI cannot determine its context level or available tools, it MUST:

1. **Declare Context as Undefined**:
   ```
   **Context Level**: Undefined
   **Available Tools**: Unknown/Uncertain
   ```

2. **Apply Conservative Evidence Requirements**:
   - Treat all changes as **High Risk** minimum
   - Require 3+ evidence sources
   - Prefer deferral over action
   - Explicitly state uncertainty in reasoning

3. **Use Defensive Citations**:
   ```
   **Source**: `claimed to be from processor.py` (cannot verify)
   **Quote**: "parse_data function exists" (as provided, unverified)
   **Context**: Unable to confirm source authenticity
   ```

### Uncertainty Indicators

Context should be marked "Undefined" when:
- Cannot determine if seeing full file or summary
- Unsure about tool availability
- Token window limitations unclear
- Source verification impossible
- Mixed or inconsistent information

### Default Behavior for Undefined Context

```markdown
⚠️ CONTEXT UNCERTAINTY DETECTED
- Operating in conservative mode
- Elevated evidence requirements active
- Deferral threshold lowered
- All actions require additional verification
```

---

## 🎯 Reasoning Efficiency

### Reasoning Bounds and Limits

To prevent excessive reasoning and token exhaustion:

1. **Maximum Reasoning Chains**: 5 per decision
2. **Maximum Evidence Sources**: 10 per decision
3. **Maximum Analysis Depth**: 3 levels of "why"
4. **Token Budget Awareness**: Stop before 80% token limit

### Complex Task Decomposition

When hitting reasoning limits:

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: DECOMPOSED - Task too complex for single reasoning

#### Decomposition:
1. **Sub-decision 1**: Analyze file dependencies (separate trace)
2. **Sub-decision 2**: Evaluate removal safety (separate trace)
3. **Sub-decision 3**: Plan migration path (separate trace)

#### Current Focus: Sub-decision 1 only
```

### Efficiency Indicators

Include efficiency metrics in validation:

```markdown
#### Validation:
- [✓] Minimum 2 evidence sources cited (have 3)
- [✓] No assumptions made beyond quoted text
- [✓] All affected files identified
- [✓] Edge cases addressed or deferred
- [✓] Reasoning chains: 3/5 (within limit)
- [✓] Token usage: ~40% (healthy margin)
```

---

## ❌ Failure Modes and Recovery

### Common Failure Scenarios

1. **Invalid Citations**
   ```markdown
   ❌ CITATION FAILURE
   - Attempted: `nonexistent.py:999`
   - Error: File not found
   - Recovery: DEFER with investigation request
   ```

2. **Hallucinated Quotes**
   ```markdown
   ❌ QUOTE VERIFICATION FAILURE
   - Claimed quote not found in source
   - Recovery: DEFER and request source verification
   ```

3. **Schema Validation Failure**
   ```markdown
   ❌ VALIDATION FAILURE
   ```yaml
   schema: chain_of_thought/v4.0.0
   validation: failed
   errors:
     - Missing required field: risk_assessment
     - Invalid evidence count: 0
   ```
   - Recovery: Return structured error, do not proceed
   ```

### Structured Failure Response

When CoT generation fails:

```markdown
## 🚫 Chain-of-Thought Generation Failed

```yaml
schema: chain_of_thought/v4.0.0
validation: failed
failure_mode: [InvalidCitation|HallucinatedQuote|SchemaViolation|ReasoningOverflow]
```

### Failure Report:
- **What failed**: [Specific failure description]
- **Why it failed**: [Root cause if known]
- **Attempted**: [What was tried]
- **Recommendation**: [How to proceed]

### DO NOT:
- Retry automatically
- Proceed with partial reasoning
- Make assumptions to fill gaps
```

### Recovery Protocols

1. **No Automatic Retries**: Failures must be reported, not retried
2. **Graceful Degradation**: Return safe defaults or defer
3. **Explicit Error Propagation**: Make failures visible
4. **Human Intervention Points**: Clear handoff when stuck

---

## 🔄 Post-Deferral Escalation

### Escalation Hierarchy

When a decision is DEFERRED, it enters the escalation pipeline:

1. **Level 1 - Enhanced Context Retry** (Automatic, <1 minute)
   - Gather additional context if available
   - Retry with expanded tool access
   - Re-evaluate with lowered risk threshold

2. **Level 2 - Senior Agent Review** (Automatic, <5 minutes)
   - Route to specialized or senior AI agent
   - Provide full reasoning trace + context
   - May request human clarification

3. **Level 3 - Human Review** (Manual, <1 hour)
   - Notify designated human reviewer
   - Include full context and recommendations
   - Human provides additional evidence or decision

4. **Level 4 - Committee Decision** (Manual, <24 hours)
   - Escalate to technical committee
   - For precedent-setting decisions
   - Results documented for future reference

### Deferral Tracking

Each deferral MUST include:

```markdown
#### Deferral Metadata:
- **Deferral ID**: DEFER-2024-0120-001
- **Initial Timestamp**: 2024-01-20T14:30:00Z
- **Escalation Level**: 1
- **Timeout**: 60 seconds
- **Next Review**: 2024-01-20T14:31:00Z
- **Escalation Path**: Enhanced Context → Senior Agent → Human
```

### Escalation Triggers

Automatic escalation occurs when:
- Timeout reached at current level
- Additional context insufficient
- Confidence remains below threshold
- Explicit escalation requested

### Resolution Recording

When resolved, update the trace:

```markdown
#### Resolution:
- **Resolved At**: Level 2 (Senior Agent)
- **Resolution Time**: 3 minutes 27 seconds
- **Additional Evidence**: [What enabled resolution]
- **Final Decision**: [Action taken or maintained deferral]
- **Lessons Learned**: [For pattern recognition]
```

---

## 💰 Token Budget Enforcement

> **Reference**: For operational limits and fallback strategies under constrained environments, see [CoT Reasoning Envelope Specification](CoT_REASONING_ENVELOPE.md)

### Hard Token Limits

Token usage MUST be monitored and enforced:

1. **Pre-Flight Estimation**:
   ```python
   estimated_tokens = estimate_reasoning_complexity(task)
   if estimated_tokens > TOKEN_LIMIT * 0.6:
       return decompose_task(task)
   ```

2. **Runtime Monitoring**:
   ```markdown
   #### Token Usage:
   - **Estimated**: 2,500 tokens
   - **Current**: 1,847 tokens (74%)
   - **Remaining**: 653 tokens
   - **Action**: Continue with constraints
   ```

3. **Automatic Decomposition Triggers**:
   - Token usage exceeds 60% of limit
   - Reasoning chains exceed 5
   - Evidence sources exceed 10
   - Cyclomatic complexity >15

### Decomposition Strategy

When token budget exceeded:

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

### Decision: AUTO-DECOMPOSED - Token budget exceeded

#### Decomposition Plan:
1. **Phase 1**: Dependency analysis (30% tokens)
2. **Phase 2**: Risk assessment (30% tokens)
3. **Phase 3**: Implementation planning (30% tokens)
4. **Reserve**: Error handling (10% tokens)

#### Current Execution: Phase 1 only
[Continue with Phase 1 reasoning...]
```

### Fallback Strategies (Reasoning Envelope)

When approaching token limits, apply degradation modes:

1. **Summarize**: Replace full trace with compressed summary + hash
2. **Defer Partial**: Return only validated trace steps, defer remainder
3. **Split Trace**: Chunk reasoning into continuation prompts

Thresholds:
- **Soft Warning**: 3000 tokens (75% of typical limit)
- **Hard Cutoff**: 4000 tokens (must degrade or abort)

### Token Budget Alerts

Include in validation:

```markdown
#### Validation:
- [✓] Token usage: 1,847/2,500 (74% - HEALTHY)
- [⚠️] Token usage: 2,100/2,500 (84% - WARNING)
- [❌] Token usage: 2,400/2,500 (96% - CRITICAL)
```

---

## 🎲 Applicability Heuristics

### When to Apply Full CoT

Not all decisions require full Chain-of-Thought reasoning. Use these heuristics to determine the appropriate level.

> **Reference**: For detailed applicability criteria and risk-based decision matrices, see [RFC-001: CoT Applicability Heuristics](RFC-001_CoT_Applicability.md)

#### Complexity Scoring Algorithm

```python
def calculate_complexity_score(task):
    score = 0

    # Decision factors (0-100 each)
    score += task.stakeholder_count * 10        # More stakeholders = higher complexity
    score += task.reversibility_cost * 20       # Harder to reverse = higher complexity
    score += task.evidence_sources * 5          # More sources = higher complexity
    score += task.conflict_potential * 15       # Conflicting requirements = higher
    score += task.regulatory_impact * 25        # Compliance requirements = higher
    score += task.time_criticality * 10        # Urgent decisions = lower (paradox)
    score += task.precedent_setting * 15       # First time = higher

    return min(score, 100)
```

#### Decision Routing Matrix

| Complexity Score | CoT Level | Requirements |
|-----------------|-----------|--------------|
| 0-20 | Minimal | Simple logging, no formal trace |
| 21-40 | Light | Basic reasoning, 1 evidence source |
| 41-60 | Standard | Full CoT with standard requirements |
| 61-80 | Enhanced | Full CoT + conflict analysis |
| 81-100 | Maximum | Full CoT + committee review |

### Key Decision Criteria (RFC-001)

Apply CoT reasoning based on these criteria:

1. **Irreversibility**: If action cannot be undone → Apply CoT
2. **Impact Surface**: If >1 module is affected → Apply CoT
3. **User-visible Behavior**: If behavior or API changes → Apply CoT
4. **Security/Validation Path**: If security logic is touched → Always CoT

### Fast-Path Conditions

Bypass full CoT when ALL conditions met:

1. **Precedent Exists**: Identical decision made before with positive outcome
2. **Low Risk**: Easily reversible, minimal impact
3. **Clear Evidence**: Single authoritative source, no conflicts
4. **Time Critical**: Delay would cause more harm than imperfect decision
5. **Automated Validation**: Decision can be verified programmatically

### Fast-Path Format

```markdown
## 🏃 Fast-Path Decision

**Decision**: [Action]
**Precedent**: [Previous case reference]
**Risk Level**: Low
**Evidence**: [Single clear source]
**Validation**: [Automated check passed]
**Timestamp**: [ISO 8601]
```

### Heuristic Override

Human or senior agent can always mandate full CoT:

```yaml
override:
  reason: "Regulatory audit requirement"
  mandated_by: "compliance@example.com"
  force_level: "maximum"
```

---

## ⚔️ Conflict Adjudication Logic

### Conflict Detection

Conflicts arise when evidence sources disagree. Detection methods:

1. **Direct Contradiction**: Source A says X, Source B says ¬X
2. **Scope Conflict**: Sources disagree on boundaries
3. **Temporal Conflict**: Sources from different time periods
4. **Authority Conflict**: Equal-weight sources disagree
5. **Interpretation Conflict**: Same evidence, different conclusions

### Evidence Weighting Framework

```python
class EvidenceWeight:
    def calculate(self, source):
        weight = 1.0

        # Temporal decay (newer = higher weight)
        age_days = (datetime.now() - source.date).days
        weight *= math.exp(-age_days / 365)  # Half-life of 1 year

        # Authority multiplier
        weight *= source.authority_score  # 0.1 to 2.0

        # Directness (primary source = 1.0, secondary = 0.7, tertiary = 0.4)
        weight *= source.directness_factor

        # Corroboration bonus
        weight *= 1 + (0.1 * source.corroboration_count)

        return weight
```

### Conflict Resolution Strategies

1. **Weighted Consensus**:
   ```markdown
   #### Conflict Resolution: Weighted Consensus
   - Source A (weight: 0.8): "Use async pattern"
   - Source B (weight: 0.3): "Use sync pattern"
   - Source C (weight: 0.7): "Use async pattern"
   → Decision: Async pattern (total weight: 1.5 vs 0.3)
   ```

2. **Authority Cascade**:
   ```markdown
   #### Conflict Resolution: Authority Cascade
   1. Legal requirement: MUST use encryption
   2. Security policy: SHOULD use TLS 1.3
   3. Performance guide: MAY use TLS 1.2
   → Decision: Use TLS 1.3 (follows highest authority)
   ```

3. **Temporal Precedence**:
   ```markdown
   #### Conflict Resolution: Temporal Precedence
   - Old spec (2023): "Use REST API"
   - New spec (2024): "Use GraphQL API"
   - No deprecation notice found
   → Decision: Use GraphQL (newer takes precedence)
   ```

### Minority Report

When significant evidence supports alternative:

```markdown
#### Minority Report
**Alternative**: Use microservices architecture
**Support Weight**: 0.4 (vs 0.6 for monolith)
**Key Arguments**:
- Better scalability long-term
- Industry trend alignment
- Team expertise available
**Risk if Wrong**: Medium - refactoring cost ~3 months
```

---

## 🗜️ Reasoning Compression Strategies

### Compression Levels

1. **Level 0 - Full Trace** (No compression)
   - Complete reasoning with all details
   - Used for: Audit, training, critical decisions

2. **Level 1 - Structured Summary** (Lossless)
   ```json
   {
     "decision": "Extract parse_data function",
     "risk": "medium",
     "evidence_count": 3,
     "key_evidence": ["SRP violation", "explicit instruction"],
     "confidence": 0.85,
     "trace_hash": "sha256:abcd1234..."
   }
   ```

3. **Level 2 - Semantic Compression** (Lossy)
   ```markdown
   DECISION[extract_function] BECAUSE[srp_violation, plan_mandate]
   RISK[medium] EVIDENCE[3] CONFIDENCE[0.85]
   ```

4. **Level 3 - Binary Decision** (Maximum compression)
   ```
   APPROVED:extract_parse_data:0.85:sha256:abcd1234
   ```

### Compression Algorithm

```python
def compress_reasoning(trace, target_level):
    if target_level == 0:
        return trace  # No compression

    elif target_level == 1:
        return {
            "decision": extract_decision(trace),
            "risk": extract_risk_level(trace),
            "evidence_count": count_evidence(trace),
            "key_evidence": extract_key_points(trace, max=2),
            "confidence": calculate_confidence(trace),
            "trace_hash": hash_full_trace(trace)
        }

    elif target_level == 2:
        return semantic_compress(trace)

    elif target_level == 3:
        return binary_format(trace)
```

### Decompression Requirements

- Level 1→0: Requires full trace retrieval via hash
- Level 2→1: Requires semantic expansion
- Level 3→2: Requires decision lookup table
- Level 3→0: Full reconstruction may be impossible

### Compression Use Cases

| Use Case | Recommended Level | Rationale |
|----------|-------------------|-----------|
| Real-time display | 2-3 | Speed critical |
| Log storage | 1 | Balance size/info |
| Audit trail | 0 | Full detail required |
| API response | 1-2 | Network efficiency |
| Summary report | 2 | Human readable |

---

## 🔄 Recursive CoT Handling

### Parent-Child Relationships

Complex decisions spawn sub-decisions, creating reasoning trees:

```yaml
reasoning_tree:
  root: "DECIDE-2024-001"
  children:
    - id: "DECIDE-2024-001.1"
      question: "Which files are affected?"
      children:
        - id: "DECIDE-2024-001.1.1"
          question: "Check direct imports"
        - id: "DECIDE-2024-001.1.2"
          question: "Check indirect dependencies"
    - id: "DECIDE-2024-001.2"
      question: "What is the migration path?"
```

### Recursion Limits

- **Maximum Depth**: 5 levels
- **Maximum Breadth**: 10 children per node
- **Total Node Limit**: 50 per root decision
- **Circular Reference**: Forbidden

### Context Inheritance

Child decisions inherit from parent:

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

**Parent Context**: DECIDE-2024-001
**Inherited Risk Level**: High
**Inherited Evidence**: [Parent evidence sources available]
**Local Context**: Analyzing direct imports only
```

### Cycle Detection

```python
def detect_cycle(decision_id, parent_chain):
    if decision_id in parent_chain:
        raise CircularReasoningError(
            f"Cycle detected: {' → '.join(parent_chain)} → {decision_id}"
        )

    # Also check semantic similarity
    if semantic_similarity(decision_id, parent_chain) > 0.9:
        raise PotentialCycleWarning("Similar decision in parent chain")
```

### Aggregation Strategies

Combine child decisions into parent conclusion:

1. **Unanimous Required**: All children must agree
2. **Majority Rules**: >50% agreement sufficient
3. **Weighted Aggregation**: Based on child importance
4. **Veto Power**: Any critical child can block
5. **Custom Logic**: Parent defines aggregation

```markdown
#### Child Decision Summary
- File analysis (1.1): 15 files affected ✓
- Migration path (1.2): Phased approach recommended ✓
- Risk assessment (1.3): Medium overall ✓

#### Parent Conclusion
All child analyses complete. Proceeding with refactoring.
Aggregate confidence: 0.82 (weighted average)
```

---

## 📡 Live/Streaming Input Support

### Incremental Reasoning Protocol

For real-time systems that cannot wait for complete analysis:

```markdown
## 🧠 Streaming Reasoning Trace

**Mode**: STREAMING
**Started**: 2024-01-20T14:30:00Z
**Status**: IN_PROGRESS

### Partial Decision [Confidence: 0.3]
Based on evidence so far: LEAN_TOWARD[approve]

#### Evidence Stream
1. [14:30:01] Config file indicates feature enabled ✓
2. [14:30:03] No errors in last 24h logs ✓
3. [14:30:05] AWAITING: Database state check...
```

### State Management

```python
class StreamingCoTState:
    def __init__(self):
        self.partial_decision = None
        self.confidence = 0.0
        self.evidence_buffer = []
        self.pending_checks = []
        self.version = 0  # Increments with each update

    def add_evidence(self, evidence):
        self.evidence_buffer.append(evidence)
        self.version += 1
        self.recalculate_decision()

    def get_snapshot(self):
        return {
            "version": self.version,
            "decision": self.partial_decision,
            "confidence": self.confidence,
            "evidence_count": len(self.evidence_buffer),
            "pending": len(self.pending_checks)
        }
```

### Progressive Refinement

```markdown
### Decision Evolution
- [v1] 0.3 confidence: "Likely safe to proceed"
- [v2] 0.5 confidence: "Proceed with monitoring"
- [v3] 0.7 confidence: "Proceed, specific risks identified"
- [v4] 0.85 confidence: "Approved with conditions"
```

### Streaming Validation

Real-time validation requirements:

1. **Monotonic Confidence**: Should generally increase
2. **Consistency Check**: New evidence shouldn't contradict
3. **Timeout Handling**: Max streaming duration
4. **Snapshot Intervals**: Save state every N seconds
5. **Rollback Points**: Can revert to previous state

### Stream Termination

Conditions to finalize streaming reasoning:

```markdown
#### Stream Termination
**Reason**: Confidence threshold reached
**Final Version**: v7
**Duration**: 3.5 seconds
**Evidence Processed**: 12 items
**Final Decision**: APPROVED
**Confidence**: 0.91
```

---

## 📚 Glossary

- **Evidence**: Direct quotes from source files, documentation, or tool outputs
- **Citation**: A source reference with context-appropriate format
- **Deferral**: Explicit declaration that action cannot be taken due to insufficient evidence
- **Validation**: Self-check that all requirements are met
- **Scope Creep**: Any action beyond what evidence explicitly requires
- **Risk Level**: Categorization of change impact (Low/Medium/High/Critical)
- **Freshness**: Temporal validity of evidence
- **Context Level**: AI's access level to information (Full/Summary/Chat/Mixed/Undefined)
- **Staleness**: Evidence that may be outdated based on temporal indicators
- **Schema Declaration**: Required metadata identifying CoT version for validation
- **Reasoning Bounds**: Limits on reasoning complexity to prevent token exhaustion
- **Context Uncertainty**: State when AI cannot determine its operating context
- **Failure Mode**: Structured way to report CoT generation failures
- **Complexity Score**: Numeric measure of decision complexity (0-100)
- **Fast-Path**: Streamlined decision process for low-complexity cases
- **Conflict Adjudication**: Process for resolving contradictory evidence
- **Evidence Weight**: Calculated importance of evidence based on multiple factors
- **Minority Report**: Documentation of significant alternative viewpoints
- **Compression Level**: Degree of reasoning trace summarization (0-3)
- **Reasoning Tree**: Hierarchical structure of parent-child decisions
- **Streaming Mode**: Real-time incremental reasoning updates
- **Progressive Refinement**: Improving decision confidence over time

---

## 📋 Usage Note

This Chain-of-Thought methodology is designed to be project-agnostic. When applying it to your specific context:

- Replace example file names with your actual files
- Adapt document references to your project structure
- Maintain the same rigor in evidence collection and reasoning
- Customize validation criteria as needed for your domain

---

## 📝 Version History

- v7.0.0 (Current): Added applicability heuristics, conflict adjudication, compression strategies, recursive handling, and streaming support
- v6.0.0: Added standard authority, runtime contracts, post-deferral escalation, token budget enforcement, and interoperability
- v5.0.0: Added context uncertainty handling, schema declarations, failure modes, and reasoning bounds
- v4.0.0: Added machine-readable schema, temporal reasoning, risk-based requirements, and context-aware citations
- v3.0.0: Made generic and project-independent
- v2.0.0: Complete refactor for bulletproof enforcement
- v1.0.0: Initial CoT requirements

**Note**: This is now an official standard. See [COT_STANDARD_AUTHORITY.md](COT_STANDARD_AUTHORITY.md) for governance.

---

## 🏛️ Standard Compliance

### Verification

To verify this document's authenticity:

```bash
# Verify signature
curl -s https://cot-standard.org/v7.0.0/CHAIN_OF_THOUGHT.md.sig | gpg --verify

# Check hash
echo "a7b9c2d4e5f6789012345678901234567890abcdef1234567890abcdef123456  CHAIN_OF_THOUGHT.md" | sha256sum -c
```

### Implementation Requirements

To claim CoT v7.0.0 compliance, implementations MUST:

1. **Support all mandatory features** defined in this document
2. **Pass the official test suite** (>95% compliance)
3. **Implement runtime contract validation**
4. **Support standard interoperability formats**
5. **Handle all defined failure modes**
6. **Respect token budget constraints**
7. **Implement escalation protocols**
8. **Support complexity scoring and routing**
9. **Handle evidence conflicts with adjudication**
10. **Implement compression/decompression (Level 0-1 minimum)**
11. **Support recursive decision trees**
12. **Enable streaming mode for real-time systems**

### Certification

For certification information, see:
- Website: https://cot-standard.org/certification
- Email: certification@cot-standard.org

### Runtime Contract Declaration

All CoT-compliant systems MUST accept and validate runtime contracts:

```json
{
  "cot_contract": {
    "specification": "chain_of_thought >= 7.0.0",
    "runtime": "2.0.0",
    "enforcement": "strict",
    "capabilities": {
      "compression": true,
      "streaming": true,
      "recursive": true,
      "conflict_resolution": true,
      "complexity_routing": true
    }
  }
}
```