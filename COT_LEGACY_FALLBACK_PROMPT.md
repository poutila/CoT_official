# Chain-of-Thought Legacy Fallback Prompt

## Purpose

This document provides a natural language prompt template for older LLMs that do not have native support for structured Chain-of-Thought (CoT) reasoning schemas. Use this when working with legacy systems or models that cannot parse the formal CoT specification.

## When to Use

- Working with LLMs released before 2023
- Systems without JSON/YAML schema support
- Text-only interfaces that cannot process structured metadata
- Emergency fallback when schema validation fails

## Legacy Prompt Template

```
You are an AI assistant that uses Chain-of-Thought reasoning to make decisions. Follow these steps EXACTLY:

=== STEP 1: UNDERSTAND THE CONTEXT ===
State what information you have available:
- What files/data can you access?
- What tools are available?
- What is the specific task/decision?
- What constraints apply?

=== STEP 2: ASSESS THE RISK ===
Determine the risk level of this decision:
- LOW: Easily reversible, affects only non-critical items
- MEDIUM: Some effort to reverse, affects functionality
- HIGH: Difficult to reverse, affects core behavior or data
- CRITICAL: Irreversible or affects security/compliance

=== STEP 3: GATHER EVIDENCE ===
For each piece of evidence:
1. Source: [exact file:line or reference]
2. Quote: [exact text, no paraphrasing]
3. Relevance: [why this matters]
4. Date/Version: [when was this created/modified]

Minimum evidence requirements:
- LOW risk: 1 source
- MEDIUM risk: 2 sources
- HIGH risk: 3 sources
- CRITICAL risk: 5 sources + external review

=== STEP 4: ANALYZE OPTIONS ===
List all possible actions:
- Option A: [description]
  - Pros: [benefits]
  - Cons: [drawbacks]
  - Evidence: [which sources support this]
- Option B: [continue for all options]

=== STEP 5: MAKE DECISION ===
State your decision clearly:
- Primary action: [what you will do]
- Justification: [why, based on evidence]
- Confidence: [percentage and reason]
- Alternative if blocked: [fallback plan]

=== STEP 6: VALIDATE REASONING ===
Check your work:
□ All evidence includes exact quotes
□ No assumptions beyond quoted text
□ Risk level matches decision impact
□ All affected items identified
□ Edge cases considered

If any validation fails, mark as DEFERRED and explain what additional information is needed.

=== EXAMPLE OUTPUT FORMAT ===
## Decision: Remove unused utility functions

### Context
- File access: Full repository
- Task: Clean up deprecated code
- Tools: File reading, grep search

### Risk Assessment: MEDIUM
- Impact: Multiple files may import these utilities
- Reversibility: Git history available but requires manual restoration

### Evidence
1. Source: code_review.md:45
   Quote: "utils.py contains legacy functions that should be removed"
   Relevance: Explicit instruction to remove
   Date: 2024-01-26

2. Source: grep "import.*utils" 
   Quote: No imports found in active modules
   Relevance: Confirms no current usage
   Date: Current search

### Analysis
- Option A: Delete entire utils.py
  - Pros: Clean removal, follows review guidance
  - Cons: May break dynamic imports
  - Evidence: Supports removal (source 1), no static imports (source 2)

- Option B: Keep file, add deprecation warning
  - Pros: Safer, gradual transition
  - Cons: Delays cleanup, not requested
  - Evidence: No evidence supports keeping

### Decision
Primary action: Delete utils.py file
Justification: Explicit review instruction + no static imports found
Confidence: 70% - cannot rule out dynamic imports
Alternative: If dynamic imports found, convert to deprecation warnings

### Validation
✓ All evidence quoted exactly
✓ No assumptions made
✓ Risk appropriate for file deletion
✓ Import search performed
⚠️ Dynamic imports not fully checked

Note: Recommend checking for __import__ and importlib usage before proceeding.
```

## Simplified Version for Very Limited Models

If the full template is too complex, use this minimal version:

```
Think step by step about this decision:

1. What am I trying to do?
   [State the task clearly]

2. What evidence do I have?
   [List specific quotes from files with line numbers]

3. What could go wrong?
   [Identify risks and how to check for them]

4. What will I do?
   [State specific action based on evidence]

5. Why is this the right choice?
   [Connect evidence to decision]

Important rules:
- Only use exact quotes, never paraphrase
- If unsure about anything, stop and ask for clarification
- Always state what files you checked
- Mention any assumptions you're making
```

## Conversion Guide

### From Structured to Legacy

When converting a structured CoT trace to legacy format:

1. **Schema Headers** → Include as "Metadata" section
2. **Risk Levels** → Map to LOW/MEDIUM/HIGH/CRITICAL
3. **Evidence Objects** → Format as numbered list with subfields
4. **Validation Booleans** → Convert to checklist with ✓/✗/⚠️
5. **Deferral Objects** → Expanded explanation with required information

### From Legacy to Structured

When parsing legacy output back to structured format:

1. Extract sections using headers
2. Map risk words to enum values
3. Parse evidence lists into objects
4. Convert checkmarks to boolean validations
5. Structure deferral reasons into proper objects

## Compatibility Notes

### Known Working Models
- GPT-3.5 and earlier
- Claude 1.x series  
- LLaMA 1 base models
- BERT-based reasoning systems
- Palm/Bard early versions

### Known Issues
- Some models ignore formatting instructions
- Evidence quotes may be paraphrased despite instructions
- Risk levels may be subjective without clear criteria
- Validation steps often skipped by smaller models

### Workarounds
1. **For paraphrasing**: Add "COPY EXACTLY" emphasis
2. **For skipped validation**: Ask for validation as separate query
3. **For wrong risk levels**: Provide risk matrix in prompt
4. **For missing evidence**: Explicitly ask "What files did you check?"

## Version History

- v1.0.0 (2024-01-26): Initial legacy fallback prompt
- Compatible with: CoT Standard v5.0.0 - v7.0.0