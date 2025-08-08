# 🧠 Lightweight CoT for AI Coding

**Version**: 1.0.0  
**Purpose**: Practical Chain-of-Thought reasoning for AI coding tasks

## 🎯 Core Principle

**Think before you code.** Every coding decision should be justified with evidence from the codebase, requirements, or established patterns.

---

## 📋 Quick Reference

### When to Use CoT

**Always use for:**
- Refactoring existing code
- Adding new features
- Changing APIs or interfaces
- Debugging complex issues
- Architecture decisions

**Optional for:**
- Simple bug fixes
- Adding comments
- Formatting changes
- Obvious implementations

### Complexity Levels

| Task | CoT Level | Requirements |
|------|-----------|--------------|
| **Simple** (bug fix, add method) | **Minimal** | 1 evidence source |
| **Medium** (refactor, new feature) | **Standard** | 2+ evidence sources |
| **Complex** (architecture change) | **Full** | 3+ evidence sources + alternatives |

---

## 🔄 CoT Formats

### Minimal CoT (Simple Tasks)

```markdown
## 🧠 Quick Reasoning

**Task**: Fix null pointer exception in UserService.validate()
**Evidence**: `UserService.java:45` - missing null check before `user.getName().length()`
**Solution**: Add `if (user == null || user.getName() == null)` guard
**Risk**: Low - isolated fix, easily reversible
```

### Standard CoT (Medium Tasks)

```markdown
## 🧠 Reasoning

### Task: Extract authentication logic to separate service

#### Evidence:
1. **`AuthController.java:23-67`**: Auth logic mixed with HTTP handling
2. **`UserController.java:89-120`**: Duplicate auth checks
3. **`requirements.md`**: "Separate concerns for better testability"

#### Analysis:
- **Why**: Code duplication + requirements mandate separation
- **Impact**: 2 controllers need import changes
- **Risk**: Medium - API stays same, internal refactor only

#### Solution:
Create `AuthService.java` and extract common methods
```

### Full CoT (Complex Tasks)

```markdown
## 🧠 Full Reasoning

### Task: Migrate from REST to GraphQL API

#### Evidence:
1. **`api-requirements.md § 3.1`**: "Move to GraphQL for flexible queries"
2. **`performance-report.md`**: "REST over-fetching causes 40% waste"
3. **`team-meeting-notes.md`**: "Frontend team requests GraphQL"
4. **`package.json`**: Already has `apollo-server` dependency

#### Analysis:
- **Primary reason**: Official requirement + performance + team request
- **Alternative considered**: Optimize existing REST endpoints
- **Alternative rejected**: Requirements explicitly mandate GraphQL
- **Risk**: High - breaking change for all clients
- **Mitigation**: Versioned API, gradual migration plan

#### Implementation Plan:
1. Create GraphQL schema alongside REST
2. Implement resolvers for core entities
3. Update frontend incrementally
4. Deprecate REST endpoints after 3 months

#### Validation:
- ✓ Multiple evidence sources (4)
- ✓ Requirements explicitly support this
- ✓ Migration plan addresses risks
- ✓ Backwards compatibility considered
```

---

## 🎯 Evidence Requirements

### What Counts as Evidence

**Strong Evidence:**
- Direct quotes from requirements/specs
- Existing code patterns in the codebase
- Comments/documentation in code
- Error messages or logs
- Test failures

**Weak Evidence:**
- "It's a best practice"
- "This is cleaner"
- "I think this is better"
- General principles without specific context

### Citation Format

**For Code:**
```
**Source**: `filename.js:line-number(s)`
**Content**: "actual code or comment"
```

**For Documentation:**
```
**Source**: `document.md § section`  
**Content**: "exact quote from document"
```

**For Requirements:**
```
**Source**: `requirements/feature-x.md`
**Content**: "specific requirement text"
```

---

## ⚖️ Risk Assessment

### Risk Levels

**Low Risk:**
- Single file changes
- Adding new code without modifying existing
- Internal implementation changes
- Easily reversible changes

**Medium Risk:**
- Multiple file changes
- Changing existing APIs
- Database schema changes
- Dependency updates

**High Risk:**
- Breaking changes
- Architecture modifications
- Security-related changes
- Data migration required

### Risk Indicators

Include in your reasoning:
```markdown
**Risk Level**: Medium
**Impact**: 3 files, 2 API endpoints
**Reversibility**: Moderate - requires rollback script
**Testing**: Unit tests cover 80% of changes
```

---

## 🚫 What to Avoid

### Don't Do This:
```markdown
// Bad CoT
I'm going to refactor this code to make it cleaner and follow better patterns.
```

### Do This Instead:
```markdown
// Good CoT
**Task**: Extract validation logic from UserController
**Evidence**: `UserController.java:45-89` contains business logic mixed with HTTP handling
**Reason**: Violates SRP as noted in `code-review-comments.md:12`
```

### Common Mistakes:
- ❌ Making assumptions about what "should" be done
- ❌ Referencing non-existent files or line numbers  
- ❌ Changing scope mid-task without justification
- ❌ Ignoring existing code patterns without explanation

---

## 🔧 Practical Examples

### Example 1: Simple Bug Fix

```markdown
## 🧠 Quick Reasoning

**Bug**: NullPointerException in OrderCalculator.calculateTotal()
**Evidence**: `error.log:1423` - "NPE at OrderCalculator.java:67"
**Root Cause**: `OrderCalculator.java:67` - `item.getPrice()` called without null check
**Fix**: Add null guard: `if (item == null || item.getPrice() == null) continue;`
**Test**: Add test case for null items in order
```

### Example 2: Feature Addition

```markdown
## 🧠 Reasoning

### Task: Add user profile caching

#### Evidence:
1. **`performance-metrics.md`**: "User profile queries: 234ms avg, called 1000x/min"
2. **`UserController.java:34-45`**: Profile loaded on every request
3. **`pom.xml:67`**: Redis dependency already available

#### Analysis:
- **Problem**: Expensive DB queries repeated frequently
- **Solution**: Cache profiles in Redis with 5min TTL
- **Pattern**: Other entities use similar caching (`ProductCache.java`)

#### Implementation:
- Add `@Cacheable("user-profiles")` to `UserService.getProfile()`
- Configure cache TTL in `application.yml`
- Add cache invalidation on profile updates
```

### Example 3: Refactoring Decision

```markdown
## 🧠 Reasoning

### Task: Should we extract PaymentProcessor interface?

#### Evidence:
1. **`PaymentService.java:1-150`**: 150 lines, handles Stripe + PayPal + Bitcoin
2. **`requirements.md § 4.3`**: "Support additional payment providers quarterly"
3. **`StripePaymentService.java`**: Already exists but not used consistently
4. **`team-standup-notes.md`**: "Apple Pay integration needed next sprint"

#### Analysis:
- **Current state**: Monolithic payment handling
- **Future need**: Multiple payment providers
- **Existing pattern**: Some services already extracted
- **Urgency**: New provider needed soon

#### Decision: Yes, extract interface
- Create `PaymentProcessor` interface
- Refactor existing providers to implement it
- Use strategy pattern in `PaymentService`
- Enables easy Apple Pay addition
```

---

## 📏 Guidelines for Each Complexity Level

### Simple Tasks (1-2 minutes thinking)
- One clear evidence source
- Obvious solution
- Low risk
- Quick validation

### Medium Tasks (2-5 minutes thinking)
- Multiple evidence sources
- Consider one alternative
- Assess impact on related code
- Plan basic testing

### Complex Tasks (5-15 minutes thinking)
- Comprehensive evidence gathering
- Multiple alternatives considered
- Risk analysis and mitigation
- Implementation planning
- Stakeholder impact assessment

---

## 🎯 Success Criteria

**Good CoT should:**
- ✅ Be proportional to task complexity
- ✅ Reference actual code/docs (not generalities)
- ✅ Explain *why* not just *what*
- ✅ Consider alternatives when appropriate
- ✅ Identify risks and impacts
- ✅ Be actionable and specific

**Time Investment:**
- **Simple**: 30 seconds - 2 minutes
- **Medium**: 2-5 minutes  
- **Complex**: 5-15 minutes

The goal is better decisions and code, not perfect documentation.

---

## 🚀 Quick Start

1. **Identify task complexity** (Simple/Medium/Complex)
2. **Gather evidence** from code, docs, requirements
3. **Choose appropriate CoT format**
4. **Write reasoning** with specific citations
5. **Validate** your logic before coding
6. **Code with confidence**

Remember: **CoT is thinking time invested upfront to save debugging time later.**
