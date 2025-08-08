# CLAUDE.md Canonical Standard (v2.1.0 - PROPOSAL)

## 🛡️ PROTECTED DOCUMENT - DO NOT MODIFY
**This file is the golden standard. NEVER modify this file directly.**
- All changes require formal review and version increment
- Modifications must be proposed via ADR (Architecture Decision Record)
- This is the definitive reference for evaluating CLAUDE.md files

This is the definitive reference for evaluating, constructing, and enforcing CLAUDE.md files in AI coding environments. All projects must comply unless explicitly exempted by ADR.

## 🔄 PROPOSED CHANGES
**This is a proposal for v2.1.0 based on ADR-006 and NO-CODE-006**
- Added Core Requirement 0: "No Silent Assumptions" as foundational principle (the "golden egg")
- Enhanced all sections to incorporate assumption validation requirements
- Added explicit configuration checking requirements throughout
- Cross-referenced NO-CODE-006 principle in multiple sections

## Purpose
Define what constitutes a high-quality CLAUDE.md that effectively guides AI coding assistants to produce excellent code.

## Core Requirements for CLAUDE.md

### 0. 🥚 No Silent Assumptions (The Golden Egg)
**Why**: Silent assumptions introduce fragile behavior that only surfaces during runtime failures or edge conditions. This is the foundational principle that all other requirements build upon.

#### Must Have:
- **Explicit Assumption Validation Requirements**
  - All code must validate input structure, types, and availability
  - Configuration files must be checked before making compatibility decisions
  - Environment variables and file paths must be verified
  - API response fields must be validated before use
  - Project's configuration (pyproject.toml, package.json, etc.) must be validated

- **AI-Specific Mandates**
  - ❌ Bad: "Fix compatibility issues" (assumes version)
  - ✅ Good: "Check pyproject.toml `requires-python` field, then fix compatibility for that version"
  - AI MUST explicitly state all assumptions in output
  - AI MUST ask clarifying questions when context is ambiguous
  - AI MUST check project configuration files before version/compatibility changes

- **Enforcement**
  - Code Review: Reject implicit assumptions in logic or API use
  - CI Gate: Static check for missing validations on user input, environment vars, or file IO
  - AI Review: Reject outputs that omit assumptions when behavior is inferred or guessed

- **Cross-Reference**: This implements NO-CODE-006 principles throughout the document

### 1. 🎯 Clarity & Unambiguity
**Why**: AI takes instructions literally - ambiguity leads to inconsistent results

#### Must Have:
- **Concrete Examples** for every rule
  - ❌ Bad: "Write good tests"
  - ✅ Good: "Test naming: `test_<method>_<condition>_<expected_result>`"

- **Specific Thresholds** not vague guidance
  - ❌ Bad: "Keep files short"
  - ✅ Good: "Files MUST NOT exceed 500 lines"

- **Clear Consequences**
  - ❌ Bad: "Try to avoid print statements"
  - ✅ Good: "NEVER use print() - CI will reject. Use logging instead"

- **No Assumption Examples**
  - ❌ Bad: "Use appropriate Python features"
  - ✅ Good: "Check pyproject.toml for Python version, then use features available in that version"

### 2. 🔒 Completeness of Constraints
**Why**: Every gap is a place where AI might hallucinate or make poor choices

#### Must Cover:
- **Forbidden Patterns** with complete list
  - What patterns to reject (print, eval, # type: ignore, # noqa)
  - Errors must not be suppressed instead code is fixed to pass tests
  - How it's enforced
  - **Assumption**: Never assume a pattern is acceptable without explicit allowance

- **Tool Chain Requirements**
  - Which tools must pass with specific commands and parameters:
    - `mypy src/ --strict --no-error-summary`
    - `ruff check src/ --fix --exit-non-zero-on-fix`
    - `ruff format src/ --check`
    - `pytest --cov=src --cov-fail-under=90 --tb=short`
    - `vulture src/ --min-confidence=70`
    - `bandit -r src/ -f json -o bandit_report.json`
  - In what order to run them
  - What constitutes "passing"
  - Pre-tool cleanup requirements (see section 5.4)
  - **Configuration Check**: Verify tool versions match project requirements

- **Error Handling Patterns**
  - How to handle exceptions
  - What patterns are required
  - What patterns are forbidden
  - **No Silent Failures**: All error paths must be explicit

### 3. 📊 Measurable Standards
**Why**: AI needs concrete success criteria

#### Must Include:
- **Numeric Thresholds**
  - Test coverage: 90%
  - Max complexity: 10
  - Max file lines: 500
  - Max parameters: 7
  - **Source**: These must be verified from project config, not assumed

- **Binary Rules** (allowed/forbidden)
  - Allowed: parameterized queries
  - Forbidden: SQL concatenation
  - Allowed: specific exceptions
  - Forbidden: bare except
  - **Validation**: Check project's security config before applying

- **Enforcement Cross-References**
  - Tool configuration: See section 5 (Tool Integration)
  - CI/CD validation: See section 5.3 (CI/CD Requirements)
  - Pre-commit hooks: See section 5.1 (Pre-commit Configuration)

### 4. 🔗 Internal Consistency
**Why**: Conflicting instructions confuse AI and lead to errors

#### Must Ensure:
- **No Contradictions** between sections
- **No Overlapping Rules** with different requirements
- **Clear Hierarchy** when rules might conflict
- **All References Valid** (linked docs must exist)
- **Assumption Consistency** - same validation approach throughout

### 5. 🛠️ Tool Integration
**Why**: AI must know exactly how to verify its work

#### Must Specify:

- **Pre-execution Verification** (Critical for No Assumptions)
  ```bash
  # MUST run before any compatibility changes:
  echo "Checking Python version..."
  python_version=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['requires-python'])")
  echo "Project requires: $python_version"
  ```

- **Pre-commit Configuration**
  ```yaml
  # Must show exact hooks and order
  - id: mypy
  - id: ruff-check
  - id: pytest
  ```

- **Task Runner Setup**
  ```python
  # Must show nox sessions
  @nox.session
  def tests(session):
      session.run("pytest", "--cov=src", "--cov-fail-under=90")
  ```

- **CI/CD Requirements**
  - What must pass before merge
  - How to run verification
  - Cross-reference: See sections 3 (Measurable Standards) and 6 (Edge Cases) for specific thresholds

- **Pre-Tool Cleanup Requirements**
  - Remove development artifacts before running quality checks:
    - Demo scripts (`demo_*.py`) not in `examples/`
    - Test scripts (`test_*.py`) not in `tests/`
    - Build artifacts (`build/`, `*.egg-info`, `htmlcov/`)
    - Temporary reports (`*_report.json`, `*_sanitized.md`)
    - Generated files not part of the project
  - **Why**: Prevents tools from scanning unnecessary files and ensures accurate results
  - **Verification**: `find . -name "demo_*.py" -o -name "*.egg-info" -o -name "htmlcov"`

### 6. 🚫 Edge Case Coverage
**Why**: AI needs to know what to do in unusual situations

#### Must Address:
- **Exception Cases**
  - When rules don't apply (e.g., __init__.py for tests)
  - Legacy code handling
  - Third-party code
  - **Assumption**: Always ask before applying rules to edge cases

- **Conflict Resolution**
  - What takes precedence
  - How to handle tradeoffs
  - When to ask for clarification
  - **Never assume precedence** - make it explicit

- **Failure Recovery Procedures**
  - How to handle tool failures (network timeouts, missing dependencies)
  - Fallback strategies when primary tools are unavailable
  - Recovery steps for corrupted project state
  - When to continue vs. when to abort the process

### 7. 📁 Structure & Organization
**Why**: AI needs to find information quickly

#### Must Have:
- **Logical Section Order**
  1. Overview & Purpose
  2. No Assumptions Principle (Golden Egg)
  3. Critical Security Rules
  4. Code Quality Standards
  5. Testing Requirements
  6. Development Workflow
  7. Tool Configuration

- **Clear Section Headers**
  - Use consistent emoji markers
  - Descriptive titles
  - Proper hierarchy (##, ###)

- **Quick Reference Sections**
  - Checklists for common tasks
  - Command snippets
  - Common patterns

### 8. 🔄 Self-Reference & Updates
**Why**: Documentation must evolve with the project

#### Must Include:
- **Version/Update Date**
- **Related Documents** with clear purpose
- **How to Propose Changes**
- **What Requires ADR** (Architecture Decision Record)
- **NO-CODE-006 Reference** for assumption handling

### 9. 🔐 Security Requirements
**Why**: Security holes can be catastrophic if AI misses them

#### Must Include:
- **Never commit secrets** to code or logs
- **Input validation** requirements for all external data
- **Secure coding practices** (parameterized queries, escaping, etc.)
- **Security tools** (bandit, safety, gitleaks) and when to run them
- **Vulnerability handling** process
- **Authentication/authorization** patterns
- **Data protection** requirements (encryption, PII handling)
- **Assumption Security**: Never assume data is safe - always validate

### 10. 📂 File & Naming Conventions
**Why**: Consistent structure helps AI organize projects correctly

#### Must Include:
- **File naming patterns**
  - Python: `snake_case.py`
  - Tests: `test_<module>.py`
  - Config: `<tool>file.py` or `.<tool>rc`
- **Directory structure** expectations
- **Acceptable file extensions** in src/
- **Module organization** principles
- **Import conventions** (relative vs absolute)
- **Version-specific patterns** (check Python version first)

### 11. ✅ AI Self-Check Checklist
**Why**: Enables autonomous verification after edits to maintain continuous quality

#### Must Include:
```markdown
## ✅ AI Self-Check After Edit

> ⚠️ This checklist is **mandatory**. It must be run after every code-editing action that affects functionality, structure, security, or documentation. No item is optional unless explicitly exempted via ADR.

### Pre-execution Checks (NEW - No Assumptions)
- [ ] Check project configuration (pyproject.toml, package.json, etc.)
- [ ] Verify Python/Node/etc. version requirements
- [ ] Confirm all dependencies are available
- [ ] State all assumptions explicitly in output

### Quality Checks
- [ ] Clean up all temporary and development artifacts
- [ ] Formatting applied: `ruff format`
- [ ] Type checking passes: `mypy`
- [ ] Linting passes: `ruff check --fix`
- [ ] No unused code: `vulture`
- [ ] Security scan clean: `bandit -r src/`
- [ ] No forbidden patterns in code
- [ ] Test coverage ≥ 90%
- [ ] All functions under 50 lines
- [ ] No files over 500 lines
- [ ] Documentation updated for any API or behavior changes
- [ ] Test file exists for every Python file (except `__init__.py`)
- [ ] All tests pass: `pytest`
- [ ] CHANGELOG.md updated for features/fixes
```

### 12. 🏛️ ADR Approval Policy
**Why**: Ensure human accountability and oversight for critical changes

#### Must Include:
- **Clear governance rules** for Architecture Decision Records (ADRs)
- **Human-only approval requirement** for ADRs
- **Protected document list** requiring ADR approval

#### Required Policy:
```markdown
### ADR Approval Policy (ADR-003)
- **AI CAN create ADR proposals** with status "Proposed"
- **AI CANNOT approve ADRs** - only humans can change status to "Approved"
- **AI MUST verify human approval** before implementing protected document changes
- **Protected documents** requiring ADR approval:
  - CLAUDE_MD_REQUIREMENTS.md (this golden standard)
  - Core CLAUDE.md structural changes
  - Security policies
  - Architecture documents
  - Any document marked as "PROTECTED"
```

### 13. 🔖 Change History Tracking
**Why**: Track evolution of standards and requirements over time

#### Must Include:
- **Version number** at top of document
- **Last updated date**
- **Change summary** for significant updates

#### Change History

- v2.1 (2025-07-12 - PROPOSED): Added "No Silent Assumptions" as Core Requirement 0, integrated NO-CODE-006 principles throughout all sections (ADR-006)
- v2.0 (2025-07-12): Added strict AI checklist output enforcement (ADR-005)
- v1.9 (2025-07-11): Enhanced forbidden patterns (added # noqa), improved AI Self-Check tool ordering, added vulture for unused code detection (ADR-004)
- v1.8 (2025-07-11): Added ADR approval policy requiring human-only approval (ADR-003)
- v1.7 (2025-07-11): Initial addition of ADR approval policy section
- v1.6 (2025-07-11): Added mandatory enforcement language to AI Self-Check checklist
- v1.5 (2025-07-11): Changed AI Self-Check from "Before Commit" to "After Edit" (ADR-002)
- v1.4 (2025-07-11): Added pre-tool cleanup requirements (ADR-001)
- v1.3 (2025-07-10): Added AI Self-Check, Security section, File Structure
- v1.2 (2025-07-01): Enhanced testing requirements, added mutation testing
- v1.1 (2025-06-15): Added forbidden patterns, tool enforcement
- v1.0 (2025-06-01): Initial CLAUDE.md standards

### 14. 🤖 AI Compliance Enforcement
**Why**: Ensure AI-generated code meets all CLAUDE.md quality gates before claiming completion

#### Must Include:

- AI MUST NOT mark work as "complete", "CLAUDE-compliant", or "validated" unless:
  - All items in the AI Self-Check checklist have been executed
  - Each checklist item is individually verified with PASS/FAIL status
  - Output includes full checklist results in the final message or PR

- ✅ Example AI checklist output (REQUIRED):

```text
CLAUDE Checklist Results:
✓ Project config checked (Python 3.12)
✓ All tests pass with ≥90% coverage
✓ Type checking passed (mypy)
✓ Linting passed (ruff)
✓ No unused code (vulture)
✓ No security issues (bandit)
✓ No forbidden patterns
✓ All functions < 50 lines
✓ All files < 500 lines
✓ Test files present
✓ Docs updated ✅
→ CLAUDE COMPLIANCE PASSED
```

- ❌ If any item is missing or skipped, AI MUST respond with:

> CLAUDE checklist incomplete — task is not compliant. Fix required.

#### Enforcement Requirements

Every AI-generated PR or commit MUST include one of the following:

- Output of: `nox -s post_edit_checklist`
- Output of: `pre-commit run --all-files` including `mypy`, `vulture`, `bandit`, `pytest`, etc.
- Full PASS/FAIL checklist block in commit message or PR description

#### Enforcement Consequences

CLAUDE compliance is considered **FAILED** if:
- Any required checklist item is missing
- Tool output is not captured or validated
- AI marks task as "done" without complete validation
- Configuration was not checked before making assumptions

## Section Naming Consistency Guide

For better scanning by both humans and tools, use consistent header patterns:

### Imperative Headers (Preferred)
- ✅ "Define Security Requirements"
- ✅ "Specify Testing Standards"
- ✅ "Set Code Quality Rules"

### Noun Phrases (Acceptable)
- ⚠️ "Security Requirements"
- ⚠️ "Testing Standards"
- ⚠️ "Code Quality Rules"

Choose one style and use consistently throughout.

## Scoring Rubric for CLAUDE.md

### Completeness Score (50 points)
- [ ] No Silent Assumptions principle included (10) **NEW**
- [ ] All forbidden patterns listed (5)
- [ ] All required tools specified (5)
- [ ] Test requirements complete (5)
- [ ] Security rules comprehensive (5)
- [ ] Error handling patterns (5)
- [ ] File/function limits defined (5)
- [ ] Development workflow clear (5)
- [ ] Project structure defined (5)

### Additional Scoring Items (Bonus 10 points)
- [ ] File naming conventions specified (2)
- [ ] AI self-check checklist included (3)
- [ ] Security section with examples (3)
- [ ] Consistent header formatting (2)

### Clarity Score (30 points)
- [ ] Every rule has example (10)
- [ ] No ambiguous language (10)
- [ ] Clear consequences stated (10)

### Consistency Score (20 points)
- [ ] No contradictions (10)
- [ ] All references valid (5)
- [ ] Proper hierarchy (5)

### Enforceability Score (10 points)
- [ ] Tools can verify rules (5)
- [ ] CI/CD can enforce (5)

## Red Flags (Automatic Failures)

### Critical Omissions
- ❌ No assumption validation requirements
- ❌ No test coverage requirement
- ❌ No forbidden patterns list
- ❌ No security guidelines
- ❌ No tool requirements

### Dangerous Patterns
- ❌ Allows silent assumptions
- ❌ Suggests using eval/exec
- ❌ Allows hardcoded secrets
- ❌ Permits bare except
- ❌ No input validation rules

### Ambiguity Issues
- ❌ Uses "should" instead of "must"
- ❌ Uses "try to" instead of "always/never"
- ❌ Missing specific thresholds
- ❌ Vague quality standards

## The Ultimate Test

A perfect CLAUDE.md should enable:
1. **No Silent Assumptions** - Every decision is explicit and validated
2. **Deterministic AI Behavior** - Same input → same output
3. **Self-Verification** - AI can check its own work
4. **No Hallucination Space** - Every decision is guided
5. **Clear Failure Modes** - AI knows when to stop/ask
6. **Evolution Support** - Can be updated without breaking

## Summary

A good CLAUDE.md is:
- **Assumption-Free**: No silent assumptions, everything validated
- **Complete**: Covers all aspects of development
- **Clear**: No ambiguity in instructions
- **Consistent**: No contradictions
- **Enforceable**: Can be automatically verified
- **Practical**: Includes examples and patterns
- **Evolvable**: Supports updates and extensions

The goal: An AI reading CLAUDE.md should be able to produce code that passes all quality gates on the first try, every time, without making silent assumptions about versions, configurations, or requirements.