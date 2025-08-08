# 📝 DOCUMENTATION STANDARDS

> "Knowledge is cheap, disc space is cheaper, lost context is expensive."

**MANDATORY READING**: This document defines non-negotiable documentation requirements for all project work.

## 🚨 CORE PRINCIPLE: NO UNDOCUMENTED WORK

**Every piece of work MUST be documented - NO EXCEPTIONS**

This includes:
- Every coding session (even 5 minutes)
- Every completed task (even 1-liners)
- Every bug fix (even typos)
- Every decision (even "obvious" ones)
- Every learning (even "common knowledge")

## 📋 MANDATORY DOCUMENTATION TYPES

### 1. Session Summaries (REQUIRED)

**When**: At the end of EVERY work session
**Where**: `summaries/SESSION_YYYY-MM-DD_HHMM.md`
**Template**: See `summaries/README.md`

#### Required Sections:
- [ ] Session Duration
- [ ] Completed Work (with task IDs)
- [ ] Current State (metrics before/after)
- [ ] Known Issues (with file:line references)
- [ ] Modified Files
- [ ] Next Steps (prioritized)
- [ ] Commands for next session

#### Validation:
```bash
python scripts/check_session_summary.py
```

#### Enforcement:
- AI assistants MUST create before session end
- CI/CD can check for recent summaries
- Exit code 1 if non-compliant

---

### 2. Task Completion Summaries (REQUIRED)

**When**: EVERY task marked as "✅ Completed"
**Where**: `planning/completions/T-XXX_COMPLETION.md`

#### Templates by Size:
- **Tasks ≥3 points**: Use `planning/TASK_COMPLETION_TEMPLATE.md`
- **Tasks 1-2 points**: Use `planning/TASK_COMPLETION_MINIMAL.md`

#### Minimum Required Content:
- [ ] What was done (specific files/changes)
- [ ] Time spent vs estimated
- [ ] Lessons learned (REQUIRED - even if "none")
- [ ] Metrics achieved vs target
- [ ] Next recommended task

#### Validation:
```bash
python scripts/check_task_completions.py
```

#### Enforcement:
- Task CANNOT be marked complete without summary
- PR reviews should check for summaries
- Exit code 1 if missing summaries

---

### 3. Code Documentation (REQUIRED)

#### Every Python File MUST Have:
- [ ] Module-level docstring
- [ ] Class docstrings (Google style)
- [ ] Function docstrings for public methods
- [ ] Inline comments for complex logic
- [ ] Type hints for all parameters/returns

#### Every Test File MUST Have:
- [ ] Test class docstring
- [ ] Test method docstrings explaining:
  - What is being tested
  - Why it matters
  - Expected behavior

---

### 4. Decision Documentation (REQUIRED)

#### Architecture Decision Records (ADRs):
- **When**: Any architectural decision
- **Where**: `docs/architecture/decisions/ADR-XXX.md`
- **Template**: Use ADR template

#### Inline Decision Comments:
```python
# Decision: Using mock instead of real file I/O
# Reason: Tests run 10x faster, no cleanup needed
# Trade-off: Less integration coverage
# Date: 2025-08-08
```

---

## 🔍 WHAT TO DOCUMENT

### Even "Trivial" Changes:
```markdown
## T-099: Fix Typo in README
**Time**: 2 minutes
**What**: Changed "teh" to "the" in line 42
**Why This Matters**: 
- Professional documentation
- Shows attention to detail
- Quick wins maintain momentum
**Learning**: VS Code spell checker would have caught this
```

### Even "Obvious" Decisions:
```markdown
## Decision: Use pytest over unittest
**Reasoning**: 
- Better fixture system
- Cleaner test syntax
- Team already familiar
**Considered unittest because**: Built-in to Python
**Rejected because**: More verbose, less features
```

### Even Failed Attempts:
```markdown
## Tried: Async processing for validators
**Result**: Failed - made code 3x more complex
**Time Lost**: 2 hours
**Learning**: Premature optimization is evil
**Future**: Revisit only if performance becomes issue
```

---

## 📊 WHY DOCUMENT EVERYTHING?

### Immediate Benefits:
1. **Context switching** - Pick up exactly where you left off
2. **Debugging** - "When did this break?" has an answer
3. **Code reviews** - Reviewers understand the "why"
4. **Estimation** - Real data beats guessing

### Long-term Benefits:
1. **Pattern recognition** - Spot recurring issues
2. **Knowledge transfer** - New team members self-onboard
3. **Architecture evolution** - See how system grew
4. **Metrics-driven decisions** - Data beats opinions

### Hidden Benefits:
1. **Rubber duck effect** - Writing clarifies thinking
2. **Celebration record** - See progress over time
3. **Learning repository** - Personal growth tracking
4. **CYA documentation** - "Yes, we considered that"

---

## 🚫 ANTI-PATTERNS TO AVOID

### ❌ BAD: "Self-documenting code"
```python
def process_data(data):
    return data * 2  # "Obviously" doubles the data
```

### ✅ GOOD: Documented code
```python
def process_data(data: float) -> float:
    """
    Double the input data for visualization scaling.
    
    Context: UI team needs all metrics doubled for display
    per decision in Sprint 3 planning (2025-01-08).
    
    Args:
        data: Raw metric value from sensor
        
    Returns:
        Doubled value for UI display
    """
    return data * 2
```

### ❌ BAD: "Will document later"
Never happens. Document AS YOU WORK.

### ✅ GOOD: Documentation-first
Write the summary template BEFORE starting work.

---

## 🤖 AI ASSISTANT REQUIREMENTS

### MUST Do:
1. Create session summary at EVERY session end
2. Create task summary for EVERY completed task
3. Check for summaries at session start
4. Update summaries with new information
5. Refuse to mark tasks complete without documentation

### MUST NOT Do:
1. End session without summary
2. Mark task complete without summary
3. Skip documentation for "trivial" tasks
4. Delete or reduce existing documentation
5. Claim "self-documenting" excuses

### Sample AI Behavior:
```
User: "Thanks, bye"
AI: "Before ending, I'll create the session summary..."
[Creates comprehensive summary]
AI: "Session summary created at summaries/SESSION_2025-08-08_1430.md"
```

---

## 📈 MEASUREMENT & COMPLIANCE

### Metrics to Track:
- Documentation coverage (files with docs / total files)
- Summary compliance (tasks with summaries / completed tasks)
- Session regularity (summaries per week)
- Documentation quality (required sections present)

### Automation:
```bash
# Add to CI/CD pipeline
python scripts/check_session_summary.py 168  # Within 1 week
python scripts/check_task_completions.py
python scripts/check_no_compliance.py
```

### Review Checklist:
- [ ] Does PR include task completion summary?
- [ ] Are decisions documented?
- [ ] Is complex code commented?
- [ ] Are test purposes clear?
- [ ] Would a new developer understand?

---

## 🎯 GETTING STARTED

### For New Sessions:
1. Read latest session summary
2. Check task completion summaries
3. Continue from documented next steps

### For New Tasks:
1. Create task in TASK.md
2. Start completion summary immediately
3. Update as you work
4. Finalize when complete

### For Debugging:
1. Check session summaries for when issue introduced
2. Read task summaries for implementation details
3. Review decision records for context

---

## 📚 TEMPLATES & RESOURCES

- [Session Summary Template](../../summaries/README.md)
- [Task Completion Template](../../planning/TASK_COMPLETION_TEMPLATE.md)
- [Minimal Task Template](../../planning/TASK_COMPLETION_MINIMAL.md)
- [Completed Examples](../../planning/completions/)

---

## ⚠️ ENFORCEMENT

### This is NOT Optional:
- Code without docs = PR rejected
- Tasks without summaries = Not complete
- Sessions without summaries = Work not recognized
- Decisions without records = Technical debt

### Remember:
> "The palest ink is better than the best memory." - Chinese Proverb

> "Documentation is a love letter that you write to your future self." - Damian Conway

> "Knowledge is cheap, disc space is cheaper, lost context is expensive." - This Project

---

*Document Version: 1.0.0*
*Last Updated: 2025-08-08*
*Status: MANDATORY - IMMEDIATE EFFECT*