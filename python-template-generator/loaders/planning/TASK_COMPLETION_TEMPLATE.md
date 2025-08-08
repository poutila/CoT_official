# Task Completion Summary Template

## Purpose
This template ensures consistent documentation when tasks are completed, capturing lessons learned and implementation details for future reference.

## When to Use
- **ALWAYS** - When marking ANY task as "✅ Completed" in TASK.md
- **NO EXCEPTIONS** - Every completed task gets a summary
- **ALL TASK SIZES** - From 1-point fixes to 8-point epics
- **ALL TASK TYPES** - Features, bugs, docs, refactoring, maintenance

---

## TASK COMPLETION SUMMARY

### Task ID: [T-XXX]
### Task Title: [Brief Title]
### Completed Date: [YYYY-MM-DD HH:MM]
### Completed By: [Name/Handle]
### Story Points: [X]
### Time Spent: [Actual hours vs estimated]

---

## 📊 Implementation Metrics

| Metric | Target | Achieved | Delta |
|--------|--------|----------|-------|
| Test Coverage | X% | Y% | +Z% |
| Tests Written | A | B | +C |
| Lines of Code | - | XXX | - |
| Files Modified | - | Y | - |
| Performance | <Xms | Yms | -Zms |

---

## 🎯 What Was Done

### Acceptance Criteria Status
- [x] Criterion 1 - How it was met
- [x] Criterion 2 - How it was met
- [x] Criterion 3 - How it was met
- [ ] Criterion 4 - Why it was descoped (if any)

### Key Implementation Details
1. **Approach Taken**: Brief description of solution approach
2. **Technologies Used**: Libraries, frameworks, patterns
3. **Files Created/Modified**:
   - `path/to/file1.py` - Purpose of changes
   - `path/to/file2.py` - Purpose of changes
   - `tests/test_file.py` - Tests added

### Code Snippets (if valuable)
```python
# Example of key pattern or solution
def important_pattern():
    """Document any reusable patterns discovered."""
    pass
```

---

## 💡 Lessons Learned

### What Went Well
- Success point 1
- Success point 2

### Challenges Encountered
1. **Challenge**: Description
   - **Solution**: How it was resolved
   - **Time Impact**: +X hours

### Discoveries
- Unexpected finding 1
- New pattern or approach that worked well
- Tool or library that proved useful

---

## 🔄 Impact on Other Tasks

### Dependencies Resolved
- Unblocked task T-XXX
- Enabled task T-YYY

### New Tasks Discovered
- [ ] T-NEW: Description (X points)
- [ ] T-NEW2: Description (Y points)

### Technical Debt Created/Resolved
- **Created**: Description (if any)
- **Resolved**: Description (if any)

---

## 📝 Documentation Updates

### Files Updated
- [ ] README.md
- [ ] CHANGELOG.md
- [ ] API documentation
- [ ] Code comments
- [ ] Architecture diagrams

### Knowledge Base Entries
- Link to wiki/docs if created
- Key commands documented

---

## ✅ Post-Completion Checklist

- [ ] All tests passing
- [ ] Coverage target met
- [ ] Documentation updated
- [ ] PR merged (PR #XXX)
- [ ] Task marked complete in TASK.md
- [ ] Completion summary added
- [ ] Next task identified

---

## 🚀 Recommendations for Next Steps

1. **Immediate Next Task**: T-XXX because...
2. **Related Improvements**: Consider...
3. **Refactoring Opportunities**: Note for future...

---

## 📊 Sprint Impact

**Sprint Velocity Impact**:
- Points completed: X/Y total
- Sprint progress: XX% → YY%
- Confidence in sprint completion: High/Medium/Low

**Risk Assessment**:
- New risks identified: Description
- Risks mitigated: Description

---

## Example Commands

```bash
# Commands that were particularly useful
uv run pytest tests/test_specific.py -xvs

# How to verify the implementation
python -m module.name --verify

# Debugging approach that worked
PYTHONPATH=src python -m pdb script.py
```

---

## AI Assistant Note
If you're an AI completing this task, include:
- Assumptions made and validated
- Patterns recognized from codebase
- Suggestions for human review

---

*Template Version: 1.0.0*
*Last Updated: 2025-08-08*