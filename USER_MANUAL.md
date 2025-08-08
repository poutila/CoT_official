# Chain-of-Thought (CoT) Definitive User Manual v7.0.0

## Table of Contents

1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Complete Specification](#complete-specification)
4. [Implementation Guide](#implementation-guide)
5. [Advanced Features](#advanced-features)
6. [Tool Ecosystem](#tool-ecosystem)
7. [Integration Patterns](#integration-patterns)
8. [Troubleshooting](#troubleshooting)
9. [Governance & Standards](#governance--standards)
10. [Reference Documentation](#reference-documentation)

## Introduction

Chain-of-Thought (CoT) is a formal specification for structured reasoning in AI systems. Version 7.0.0 introduces timestamp requirements, recursive reasoning support, token management, and comprehensive interoperability.

### Why CoT?

- **Transparency**: Every decision is traceable to explicit evidence
- **Reliability**: Prevents assumptions and hallucinations
- **Auditability**: Complete reasoning traces for review
- **Consistency**: Standardized format across all AI systems

### When CoT is Mandatory

CoT reasoning is **required** for:
- Code generation or modification
- Architectural decisions
- Plan creation or updates
- File/function reorganization
- Dependency analysis
- Document generation
- Problem solving
- Any task requiring justified decisions

## Core Concepts

### The Four Pillars (R1-R4)

#### R1: Reference Specific Inputs
```markdown
**Source**: `module.py:123-125`
**Quote**: "def process_data(input: str) -> dict:"
**Relevance**: Identifies the exact function to be modified
```

Requirements:
- MUST cite exact file paths and line numbers
- MUST quote relevant text verbatim
- Format: `filename.ext:line_number` or `document_name § section`
- FORBIDDEN: Vague references like "the code suggests"

#### R2: Explain Decisions with Evidence
Each decision MUST include:
- **What**: The specific action being taken
- **Why**: Direct evidence supporting this action (minimum 2 sources)
- **Why Not**: Why alternative approaches were rejected
- **Impact**: What this change affects

#### R3: Justify Using Exact Citations
- MUST quote the exact text that justifies the action
- MUST preserve original wording in quotes
- MUST indicate modifications with [...]
- FORBIDDEN: Paraphrasing evidence or summarizing loosely

#### R4: Defer When Evidence Is Insufficient
Deferral is REQUIRED when:
- Fewer than 2 corroborating sources exist
- Sources conflict without resolution path
- Intent cannot be determined from explicit text
- Dynamic behavior might differ from static analysis

### Risk Assessment Framework

| Risk Level | Impact | Min. Sources | Examples | Deferral Threshold |
|------------|--------|--------------|----------|-------------------|
| **Low** | Minimal, reversible | 1 source | Rename variable, add comment | Never defer |
| **Medium** | Local module changes | 2 sources | Move function, refactor class | Defer if conflicting |
| **High** | Cross-module impact | 3 sources | Change API, modify interface | Defer if <3 sources |
| **Critical** | System-wide/Breaking | 4 sources | Delete module, change architecture | Defer if any uncertainty |

## Complete Specification

### Required Output Format

```markdown
## 🧠 Reasoning Trace (Chain-of-Thought)

```yaml
schema: chain_of_thought/v7.0.0
validation: required
runtime_contract: 2.0.0
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

**Context Level**: Full File Access
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

### Timestamp Requirements

All evidence MUST include temporal context:

```markdown
**Timestamp**:
  - Created: 2024-01-01T10:00:00Z
  - Modified: 2024-01-20T15:30:00Z
  - Accessed: 2024-01-26T09:00:00Z
  - Version: 1.2.0
**Freshness**: current (score: 0.95)
```

Freshness scoring:
- 1.0 = Current (≤1 day old)
- 0.95 = Recent (≤7 days)
- 0.85 = Valid (≤30 days)
- 0.70 = Aging (≤90 days)
- <0.70 = Stale (requires verification)

### Forbidden Patterns

❌ **NEVER USE**:
- "This probably means..."
- "It's common practice to..."
- "The developer likely intended..."
- "While I'm here, I'll also fix..."
- "This could be improved by..."
- "Following best practices..."

✅ **ALWAYS USE**:
- "Line 45 explicitly states..."
- "The plan specifically requires..."
- "requirements.md §3 states..."

## Implementation Guide

### Python Implementation

```python
from cot_validator import ChainOfThoughtReasoner
from datetime import datetime

class MyCoTReasoner:
    def __init__(self, version="7.0.0"):
        self.reasoner = ChainOfThoughtReasoner(version=version)
        
    def analyze_code_change(self, file_path, change_type):
        # Collect evidence
        evidence = []
        
        # Read file and collect timestamps
        with open(file_path, 'r') as f:
            content = f.read()
            stat = os.stat(file_path)
            
        evidence.append({
            "source": f"{file_path}:1-{len(content.splitlines())}",
            "quote": content[:200] + "...",
            "relevance": "Target file for modification",
            "timestamp": {
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat() + "Z",
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z",
                "accessed": datetime.now().isoformat() + "Z"
            },
            "freshness": self.calculate_freshness(stat.st_mtime)
        })
        
        # Generate reasoning trace
        trace = self.reasoner.reason(
            decision=f"{change_type} in {file_path}",
            evidence=evidence,
            risk_level=self.assess_risk(change_type),
            context_level="full_file_access"
        )
        
        # Validate
        if not self.reasoner.validate(trace):
            return self.handle_validation_failure(trace)
            
        return trace
        
    def calculate_freshness(self, mtime):
        age_days = (datetime.now().timestamp() - mtime) / 86400
        if age_days <= 1:
            return 1.0
        elif age_days <= 7:
            return 0.95
        elif age_days <= 30:
            return 0.85
        elif age_days <= 90:
            return 0.70
        else:
            return max(0.5 - (age_days - 90) / 365, 0.0)
```

### Command Line Usage

```bash
# Basic validation
python validate_bundle.py chain_of_thought.bundle.json

# Validate with specific version
python validate_bundle.py --cot-version 7.0.0 chain_of_thought.bundle.json

# Generate file hashes
python validate_bundle.py chain_of_thought.bundle.json --generate-hashes

# Verify reasoning trace
python validate_bundle.py chain_of_thought.bundle.json --verify-trace reasoning.md

# Check signature
python validate_bundle.py chain_of_thought.bundle.json --check-signature

# Generate signed validation report
python validate_bundle.py chain_of_thought.bundle.json --sign --gpg-key your@email.com
```

## Advanced Features

### Token Management

When approaching token limits:

```yaml
token_usage: 3500               # Current usage
token_limit: 4000              # Hard limit
fallback_strategy: summarize   # Action when near limit
```

Fallback strategies:
1. **summarize**: Compress reasoning to key points
2. **defer_partial**: Return validated portions only
3. **split_trace**: Continue in new prompt

### Recursive Reasoning

For complex, multi-layered decisions:

```yaml
recursion_allowed: true
recursion_depth: 1        # Currently at depth 1
max_recursion_depth: 2    # Maximum allowed
parent_decision: "DECIDE-2024-001"
```

Example hierarchy:
```
DECIDE-2024-001 (root)
├── DECIDE-2024-001.1 (analyze dependencies)
│   ├── DECIDE-2024-001.1.1 (check imports)
│   └── DECIDE-2024-001.1.2 (check configs)
└── DECIDE-2024-001.2 (plan migration)
```

### Streaming Mode

For real-time systems:

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

### Conflict Resolution

When evidence conflicts:

```markdown
#### Conflict Resolution: Weighted Consensus
- Source A (weight: 0.8): "Use async pattern"
- Source B (weight: 0.3): "Use sync pattern"
- Source C (weight: 0.7): "Use async pattern"
→ Decision: Async pattern (total weight: 1.5 vs 0.3)

#### Minority Report
**Alternative**: Use sync pattern
**Support Weight**: 0.3 (vs 1.5 for async)
**Key Arguments**: Simpler implementation
**Risk if Wrong**: Medium - performance impact
```

### Context Uncertainty Handling

When context is unclear:

```markdown
**Context Level**: Undefined
**Available Tools**: Unknown/Uncertain

⚠️ CONTEXT UNCERTAINTY DETECTED
- Operating in conservative mode
- Elevated evidence requirements active
- Deferral threshold lowered
- All actions require additional verification
```

## Tool Ecosystem

### Core Tools

1. **validate_bundle.py**
   - Bundle integrity verification
   - Reasoning trace validation
   - Hash generation and checking
   - Signature verification

2. **cot_version_check.py**
   - Version compatibility checking
   - Update notifications
   - Migration assistance

3. **Test Suite** (`test_suite/`)
   - Valid trace examples
   - Invalid trace examples
   - Edge cases
   - Golden outputs

### Integration Tools

1. **LangChain Adapter**
   ```python
   from langchain_cot import CoTReasoningTool
   tool = CoTReasoningTool(version="7.0.0")
   ```

2. **OpenAI Function Calling**
   ```python
   cot_function = {
       "name": "chain_of_thought_reasoning",
       "parameters": {
           "type": "object",
           "properties": {
               "decision": {"type": "string"},
               "evidence": {"type": "array"},
               "risk_level": {"enum": ["low", "medium", "high", "critical"]}
           }
       }
   }
   ```

3. **REST API Schema**
   ```yaml
   openapi: 3.0.0
   paths:
     /v1/cot/reason:
       post:
         requestBody:
           content:
             application/json:
               schema:
                 $ref: '#/components/schemas/CoTRequest'
   ```

## Integration Patterns

### Framework Integration

#### LangChain
```python
from langchain.tools import Tool
from cot_validator import ChainOfThoughtReasoner

class CoTReasoningTool(Tool):
    name = "chain_of_thought_reasoning"
    description = "Apply structured CoT reasoning"
    
    def __init__(self, version="7.0.0"):
        self.reasoner = ChainOfThoughtReasoner(version=version)
    
    def _run(self, task: str, context: dict = None) -> str:
        trace = self.reasoner.reason(
            decision=task,
            context=context,
            risk_level="auto"
        )
        return trace.to_markdown() if self.reasoner.validate(trace) else f"DEFERRED: {trace.failure_reason}"
```

#### AutoGPT/AutoGen
```python
class CoTAgent:
    def __init__(self, llm, version="7.0.0"):
        self.llm = llm
        self.cot_version = version
        
    def think(self, task):
        prompt = f"""
        Apply CoT v{self.cot_version} reasoning to: {task}
        
        Follow all requirements:
        - R1: Reference specific inputs
        - R2: Explain with evidence
        - R3: Justify with citations
        - R4: Defer when uncertain
        """
        return self.llm.complete(prompt)
```

### Custom Implementations

#### Web Service
```python
from flask import Flask, request, jsonify
from cot_validator import ChainOfThoughtReasoner

app = Flask(__name__)
reasoner = ChainOfThoughtReasoner()

@app.route('/api/v1/cot/reason', methods=['POST'])
def reason():
    data = request.json
    trace = reasoner.reason(
        decision=data['decision'],
        evidence=data.get('evidence', []),
        risk_level=data.get('risk_level', 'medium')
    )
    
    if reasoner.validate(trace):
        return jsonify({
            'status': 'success',
            'trace': trace.to_dict(),
            'markdown': trace.to_markdown()
        })
    else:
        return jsonify({
            'status': 'deferred',
            'reason': trace.failure_reason,
            'suggestions': trace.suggestions
        }), 400
```

#### CLI Tool
```python
import click
from cot_validator import ChainOfThoughtReasoner

@click.command()
@click.option('--decision', prompt='What decision?')
@click.option('--risk', default='medium', type=click.Choice(['low', 'medium', 'high', 'critical']))
@click.option('--version', default='7.0.0')
def cot_cli(decision, risk, version):
    """Interactive CoT reasoning CLI."""
    reasoner = ChainOfThoughtReasoner(version=version)
    
    # Collect evidence interactively
    evidence = []
    while True:
        source = click.prompt('Evidence source (empty to finish)', default='')
        if not source:
            break
        quote = click.prompt('Quote')
        relevance = click.prompt('Relevance')
        evidence.append({
            'source': source,
            'quote': quote,
            'relevance': relevance
        })
    
    # Generate and validate trace
    trace = reasoner.reason(
        decision=decision,
        evidence=evidence,
        risk_level=risk
    )
    
    if reasoner.validate(trace):
        click.echo(trace.to_markdown())
    else:
        click.echo(f"DEFERRED: {trace.failure_reason}", err=True)
```

## Troubleshooting

### Common Issues

#### 1. Validation Failures

**Problem**: Trace fails validation
```
Error: Missing required field 'risk_assessment'
```

**Solution**: Ensure all required fields are present:
```python
trace = reasoner.reason(
    decision="...",
    risk_assessment={
        "change_type": "Modify API",
        "risk_level": "medium",
        "impact_scope": "Module",
        "reversibility": "Difficult"
    }
)
```

#### 2. Evidence Conflicts

**Problem**: Sources disagree
```
Source A says use async, Source B says use sync
```

**Solution**: Apply conflict resolution:
```python
trace.apply_conflict_resolution(
    strategy="weighted_consensus",
    weights={"source_a": 0.8, "source_b": 0.3}
)
```

#### 3. Token Limit Exceeded

**Problem**: Reasoning too long
```
Token usage: 4500/4000 (exceeded)
```

**Solution**: Apply compression or decomposition:
```python
if trace.token_usage > 0.8 * trace.token_limit:
    trace = trace.compress(level=1)  # Structured summary
    # or
    sub_traces = trace.decompose(max_tokens=2000)
```

#### 4. Context Uncertainty

**Problem**: Can't determine context
```
Context Level: Undefined
```

**Solution**: Apply conservative mode:
```python
if trace.context_level == "undefined":
    trace.risk_level = max(trace.risk_level, "high")
    trace.min_evidence_required += 1
```

### Debugging Tips

1. **Enable verbose logging**:
   ```python
   reasoner = ChainOfThoughtReasoner(debug=True)
   ```

2. **Check version compatibility**:
   ```bash
   python cot_version_check.py --current 6.0.0 --target 7.0.0
   ```

3. **Validate incrementally**:
   ```python
   # Validate structure first
   reasoner.validate_structure(trace)
   # Then evidence
   reasoner.validate_evidence(trace)
   # Finally, completeness
   reasoner.validate_completeness(trace)
   ```

4. **Use test suite**:
   ```bash
   # Run all tests
   python -m pytest test_suite/
   
   # Run specific test
   python -m pytest test_suite/valid/001_basic_reasoning.py
   ```

## Governance & Standards

### Version Management

- **Current**: v7.0.0 (2024-01-26)
- **Supported**: v7.0.0, v6.0.0, v5.0.0
- **Deprecated**: v4.0.0 and below
- **EOL Policy**: 12 months after deprecation

### Compliance Requirements

To claim CoT v7.0.0 compliance:

1. Support all mandatory features
2. Pass official test suite (>95%)
3. Implement runtime contract validation
4. Support standard interoperability formats
5. Handle all defined failure modes
6. Respect token budget constraints
7. Implement escalation protocols
8. Support complexity scoring and routing
9. Handle evidence conflicts with adjudication
10. Implement compression/decompression (Level 0-1 minimum)
11. Support recursive decision trees
12. Enable streaming mode for real-time systems

### Certification Process

1. **Self-Assessment**:
   ```bash
   python validate_bundle.py --self-assess implementation.py
   ```

2. **Submit for Review**:
   - Email: certification@cot-standard.org
   - Include test results and implementation

3. **Certification Levels**:
   - **Bronze**: Basic compliance (mandatory features)
   - **Silver**: Full compliance + interoperability
   - **Gold**: Full compliance + advanced features + contributions

### Contributing

1. **Submit RFCs**: Via GitHub issues
2. **Propose Changes**: Following RFC template
3. **Test Coverage**: >90% for new features
4. **Documentation**: Required for all changes

### Security

- **Report Issues**: security@cot-standard.org
- **PGP Key**: Available on website
- **CVE Process**: Coordinated disclosure
- **Updates**: Via security mailing list

## Reference Documentation

### Specifications
- `CHAIN_OF_THOUGHT.md` - Main specification
- `COT_RUNTIME_CONTRACT.json` - Machine-readable contract
- `COT_STANDARD_AUTHORITY.md` - Governance model

### RFCs
- `RFC-001_CoT_Applicability.md` - When to use CoT
- `RFC-002_Recursive_Reasoning.md` - Recursion bounds

### Supporting Documents
- `CoT_REASONING_ENVELOPE.md` - Token budgets
- `COT_INTEROPERABILITY.md` - Integration guide
- `COT_LEGACY_FALLBACK_PROMPT.md` - Backward compatibility

### Examples
- `examples/golden_output_trace.md` - Perfect example
- `test_suite/valid/` - Valid traces
- `test_suite/invalid/` - What to avoid

### Tools
- `validate_bundle.py` - Validation tool
- `cot_version_check.py` - Version checker
- `cot_validate_wrapper.py` - Validation wrapper

## Appendices

### A. JSON Schema

Full validation schema available at:
- `COT_RUNTIME_CONTRACT.json`
- Online: https://cot-standard.org/schemas/v7.0.0

### B. Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| E001 | Missing evidence | Add required sources |
| E002 | Invalid citation format | Use correct format |
| E003 | Insufficient evidence | Add more sources or defer |
| E004 | Token limit exceeded | Compress or split |
| E005 | Version mismatch | Update to compatible version |

### C. Glossary

- **Evidence**: Direct quotes from source files
- **Citation**: Source reference with proper format
- **Deferral**: Explicit declaration of insufficient evidence
- **Trace**: Complete reasoning output
- **Freshness**: Temporal validity score (0.0-1.0)
- **Context Level**: AI's information access level
- **Risk Level**: Impact categorization
- **Token Budget**: Maximum reasoning length
- **Recursion Depth**: Nested reasoning level
- **Streaming Mode**: Real-time incremental reasoning

---

*This manual covers CoT v7.0.0. For updates, visit cot-standard.org*