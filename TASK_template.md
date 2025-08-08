# 📋 TASK Template Framework
**Version**: 2.0.0  
**Purpose**: Comprehensive task execution framework for Chain-of-Thought reasoning

---

## 🎯 Task Metadata

| Field | Value | Required |
|-------|-------|----------|
| **Task ID** | `TASK-YYYY-MMDD-XXX` | ✅ |
| **Timestamp** | ISO 8601 format | ✅ |
| **Category** | `[Bug Fix | Feature | Refactor | Analysis | Architecture]` | ✅ |
| **Complexity** | `[Simple | Medium | Complex | Critical]` | ✅ |
| **Estimated Time** | `XX minutes` | ✅ |
| **Risk Level** | `[Low | Medium | High | Critical]` | ✅ |
| **CoT Version** | `[Light | Standard | Full v7.0.0]` | ✅ |

---

## 📝 Task Definition

### Task Statement
> **Clear, specific description of what needs to be accomplished**

### Context
- **Current State**: What exists now
- **Desired State**: What should exist after completion
- **Constraints**: Limitations or requirements
- **Dependencies**: Related systems or components

### Success Criteria
- [ ] Criterion 1: Specific, measurable outcome
- [ ] Criterion 2: Specific, measurable outcome
- [ ] Criterion 3: Specific, measurable outcome

---

## 🔍 Evidence Gathering

### Required Evidence Sources
| Source Type | Minimum Count | Status |
|------------|---------------|---------|
| Code Files | 1-3 | ⏳ |
| Documentation | 1-2 | ⏳ |
| Requirements | 1 | ⏳ |
| Tests | 0-2 | ⏳ |

### Evidence Collection Checklist
- [ ] Identify relevant code files
- [ ] Review existing documentation
- [ ] Check requirements/specifications
- [ ] Examine related tests
- [ ] Search for similar patterns in codebase
- [ ] Verify no conflicting implementations

### Collected Evidence
```markdown
1. **Source**: `filename:line_numbers`
   **Content**: "exact quote from source"
   **Relevance**: How this supports the task
   
2. **Source**: `document.md § section`
   **Content**: "exact quote from document"
   **Relevance**: Why this is important
```

---

## ⚖️ Complexity Analysis

### Complexity Score Calculation
```
Base Score: [0-100]
- Stakeholder Impact: ___ x 10 = ___
- Reversibility Cost: ___ x 20 = ___
- Evidence Sources: ___ x 5 = ___
- Conflict Potential: ___ x 15 = ___
- Regulatory Impact: ___ x 25 = ___
- Time Criticality: ___ x 10 = ___
- Precedent Setting: ___ x 15 = ___

Total Score: ___/100
```

### Complexity Determination
| Score | Level | CoT Approach | Evidence Required |
|-------|-------|--------------|-------------------|
| 0-20 | Simple | Minimal/Skip | 1 source |
| 21-40 | Low | Light CoT | 1-2 sources |
| 41-60 | Medium | Standard CoT | 2-3 sources |
| 61-80 | High | Full CoT | 3-4 sources |
| 81-100 | Critical | Full v7.0.0 + Review | 4+ sources |

**Determined Level**: ___

---

## 🚨 Risk Assessment

### Risk Matrix
| Factor | Level | Impact | Mitigation |
|--------|-------|--------|------------|
| **Change Scope** | `[Single file | Module | System-wide]` | | |
| **Breaking Changes** | `[None | Internal | External API]` | | |
| **Data Impact** | `[None | Read-only | Modification | Migration]` | | |
| **Security Impact** | `[None | Low | Medium | High]` | | |
| **Performance Impact** | `[None | Negligible | Moderate | Significant]` | | |

### Risk Summary
- **Overall Risk Level**: `[Low | Medium | High | Critical]`
- **Reversibility**: `[Easy | Moderate | Difficult | Impossible]`
- **Rollback Strategy**: Description of how to undo if needed

---

## 🧠 Chain-of-Thought Reasoning

### CoT Level Selection
Based on complexity score of ___ and risk level of ___, using: **[Light | Standard | Full]** CoT

### Reasoning Trace
```markdown
## 🧠 Reasoning Trace

### Decision: [Specific action to be taken]

#### Evidence:
1. **Source**: `file:line`
   **Quote**: "exact text"
   **Relevance**: Why this matters

2. **Source**: `doc § section`
   **Quote**: "exact text"  
   **Relevance**: Why this matters

#### Analysis:
- **Primary rationale**: Main reason with evidence
- **Alternative considered**: What else was evaluated
- **Alternative rejected because**: Specific reason

#### Validation:
- [ ] Minimum evidence sources met
- [ ] No assumptions made beyond evidence
- [ ] All affected components identified
- [ ] Edge cases addressed

#### Action:
→ Therefore, I will: [Specific, measurable action]
```

---

## 📋 Implementation Plan

### Pre-Implementation Checklist
- [ ] All evidence gathered
- [ ] Risk assessment complete
- [ ] CoT reasoning validated
- [ ] Dependencies identified
- [ ] Test strategy defined

### Implementation Steps
1. **Step 1**: Specific action with file/line reference
2. **Step 2**: Specific action with file/line reference
3. **Step 3**: Specific action with file/line reference
4. **Step 4**: Validation and testing

### Affected Files
- `file1.ext` - Description of changes
- `file2.ext` - Description of changes
- `file3.ext` - Description of changes

---

## ✅ Validation & Testing

### Validation Checklist
- [ ] Code changes match specification
- [ ] No unintended side effects
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Edge cases handled

### Test Coverage
| Test Type | Required | Status |
|-----------|----------|---------|
| Unit Tests | ✅ | ⏳ |
| Integration Tests | ❓ | ⏳ |
| Edge Cases | ✅ | ⏳ |
| Performance | ❓ | ⏳ |

### Test Commands
```bash
# Run tests
pytest tests/test_feature.py

# Check coverage
pytest --cov=module tests/

# Lint checks
ruff check .
mypy .
```

---

## 📊 Semantic Layer Integration

### Relevant Facts
```json
{
  "type": "Fact",
  "statement": "Verifiable truth relevant to task",
  "source": "Documentation or code",
  "is_verifiable": true
}
```

### Active Assumptions
```json
{
  "type": "Assumption",
  "statement": "Unverified premise accepted for this task",
  "scope": "Task-specific",
  "risk_if_wrong": "Impact description"
}
```

### Claims to Validate
```json
{
  "type": "Claim",
  "statement": "Statement that needs verification",
  "confidence": 0.7,
  "validation_method": "How to verify"
}
```

---

## 🎯 Task Completion

### Completion Checklist
- [ ] All success criteria met
- [ ] Implementation complete
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] Risk mitigations in place

### Metrics
- **Actual Time**: ___ minutes
- **Token Usage**: ___ tokens
- **Files Modified**: ___
- **Tests Added**: ___
- **Lines Changed**: +___ / -___

### Lessons Learned
- What worked well:
- What could improve:
- Patterns to reuse:

---

## 📚 Examples

### Example 1: Simple Bug Fix
```markdown
**Task ID**: TASK-2024-0120-001
**Category**: Bug Fix
**Complexity**: Simple (Score: 15)
**Risk Level**: Low
**CoT Version**: Light

**Task**: Fix NullPointerException in UserService.validateUser()

**Evidence**:
1. `UserService.java:45` - Missing null check before `user.getName()`

**Solution**: Add null guard: `if (user == null || user.getName() == null)`

**Risk**: Low - Isolated fix, easily reversible
```

### Example 2: Medium Feature Addition
```markdown
**Task ID**: TASK-2024-0120-002
**Category**: Feature
**Complexity**: Medium (Score: 55)
**Risk Level**: Medium
**CoT Version**: Standard

**Task**: Add caching layer to user profile queries

**Evidence**:
1. `performance.log` - Profile queries avg 234ms
2. `UserController.java:34-45` - No caching present
3. `pom.xml:67` - Redis available

**Analysis**: 
- Problem: Expensive repeated queries
- Solution: Redis cache with 5min TTL
- Pattern: Similar to ProductCache.java

**Implementation**:
1. Add @Cacheable annotation
2. Configure TTL in application.yml
3. Add cache invalidation on updates
```

### Example 3: Complex Architecture Change
```markdown
**Task ID**: TASK-2024-0120-003
**Category**: Architecture
**Complexity**: Complex (Score: 75)
**Risk Level**: High
**CoT Version**: Full v7.0.0

**Task**: Migrate from REST to GraphQL API

**Evidence**:
1. `requirements.md § 3.1` - "Move to GraphQL"
2. `performance-report.md` - "40% over-fetching"
3. `team-notes.md` - "Frontend requests GraphQL"
4. `package.json` - Apollo server available

**Risk Assessment**:
- Breaking changes for all clients
- Data migration required
- Performance impact unknown

**Mitigation**:
- Versioned API approach
- Gradual migration plan
- Maintain REST for 3 months
```

---

## 🔗 Quick Reference

### Complexity Quick Score
- **Simple** (0-20): Single file, obvious fix, < 30 min
- **Medium** (21-60): Multiple files, clear solution, < 2 hours
- **Complex** (61-100): System-wide, multiple options, > 2 hours

### Evidence Requirements by Risk
- **Low Risk**: 1 source minimum
- **Medium Risk**: 2 sources minimum
- **High Risk**: 3 sources minimum
- **Critical Risk**: 4+ sources minimum

### CoT Version Selection
- **Light**: Bug fixes, simple features, low risk
- **Standard**: Refactoring, medium features, medium risk
- **Full v7.0.0**: Architecture changes, breaking changes, high risk

---

**Template Version**: 2.0.0  
**Last Updated**: 2025-08-08  
**Compatibility**: CoT v7.0.0, CoT Light v1.0.0