# 🔄 Development Workflow Standards

**Purpose**: Single source of truth for Git workflow, development processes, and collaboration standards.  
**Status**: Authoritative - All other documents should reference this file.  
**Last Updated**: 2025-07-10

## 📋 Quick Reference

| Process | Standard | Tools |
|---------|----------|-------|
| **Version Control** | Git with Conventional Commits | git, pre-commit |
| **Branch Strategy** | GitFlow-inspired | main, develop, feature/* |
| **Code Review** | Required for all changes | GitHub PRs |
| **Quality Gates** | Must pass before merge | nox, pytest, ruff |
| **Deployment** | Automated via CI/CD | GitHub Actions |

## 🌳 Branching Strategy

### Protected Branches

| Branch | Purpose | Deployment | Merge Requirements |
|--------|---------|------------|-------------------|
| `main` | Production code | Auto → Production | Reviews + All tests pass |
| `develop` | Integration | Auto → Staging | Reviews + Tests pass |

### Branch Naming Convention

```
type/short-description

Examples:
feat/user-authentication
fix/database-timeout
docs/api-reference
chore/update-dependencies
```

### Branch Types
- **feat/** - New features
- **fix/** - Bug fixes
- **docs/** - Documentation only
- **style/** - Code style changes
- **refactor/** - Code refactoring
- **test/** - Test additions/changes
- **chore/** - Maintenance tasks

## 📝 Commit Standards

### Conventional Commits Format

```
type(scope): description

[optional body]

[optional footer(s)]
```

### Examples
```bash
feat(api): add user authentication endpoint
fix(database): resolve connection pool exhaustion
docs(readme): update installation instructions
test(auth): add JWT validation tests
refactor(core): simplify error handling logic
```

### Commit Rules
1. **Atomic** - One logical change per commit
2. **Present tense** - "add" not "added"
3. **Imperative mood** - "fix" not "fixes"
4. **No period** at end of subject
5. **50 char limit** for subject line
6. **72 char limit** for body lines
7. **Reference issues** - Include T-XXX from TASK.md

## 🔄 Development Process

### 1. Start New Work

```bash
# Update local develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feat/your-feature

# Link to task T-XXX from TASK.md
```

### 2. Development Cycle

```bash
# Write tests first (TDD)
# Implement feature
# Run quality checks
nox -s lint tests format

# Commit frequently with meaningful messages
git add -p  # Stage selectively
git commit -m "feat(module): add specific capability"
```

### 3. Keep Branch Updated

```bash
# Regularly sync with develop
git fetch origin
git rebase origin/develop

# Resolve conflicts if any
# Re-run tests after rebase
nox -s tests
```

### 4. Prepare Pull Request

```bash
# Clean commit history
git rebase -i origin/develop

# Ensure all quality gates pass
nox  # Runs all sessions

# Push branch
git push origin feat/your-feature
```

### 5. Pull Request Process

**PR Must Include:**
- [ ] Task reference (T-XXX)
- [ ] Clear description of changes
- [ ] Test results screenshot/log
- [ ] Breaking changes noted
- [ ] Documentation updates

**PR Template:**
```markdown
## Description
Brief description of changes

## Related Task
Closes T-XXX

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows CLAUDE.md standards
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No secrets committed
- [ ] No assumptions made
```

## 🔍 Code Review Process

### Reviewer Checklist
- Execute [CODE REVIEW PROMPT](../../refactor_pipe/CODE_REVIEW_PROMPT.md)
- [ ] Code follows project standards
- [ ] Tests are comprehensive
- [ ] No security vulnerabilities
- [ ] Performance acceptable
- [ ] Documentation updated
- [ ] No code duplication

### Review Timeline
- **First review**: Within 24 hours
- **Follow-up**: Within 12 hours
- **Approval**: 2 reviewers for main, 1 for develop

### Review Comments
```markdown
# Suggestions (non-blocking)
suggestion: Consider using a constant here

# Required changes (blocking)
change requested: This needs input validation

# Questions
question: Why this approach over [alternative]?

# Approval
LGTM! 🎉
```

## 🚀 Quality Gates

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: Ruff linting
        entry: ruff check
        language: system
        types: [python]
        
      - id: ruff-format
        name: Ruff formatting
        entry: ruff format
        language: system
        types: [python]
        
      - id: mypy
        name: Type checking
        entry: mypy
        language: system
        types: [python]
        
      - id: tests
        name: Run tests
        entry: pytest
        language: system
        pass_filenames: false
```

### Required Checks

```bash
# Run all checks with nox
nox

# Individual checks
nox -s lint      # Type checking and linting
nox -s tests     # Unit tests with coverage
nox -s format    # Code formatting
nox -s security  # Security scanning
```

### CI/CD Pipeline

All PRs must pass:
1. **Linting** - ruff, mypy
2. **Tests** - pytest with 90% coverage
3. **Security** - bandit, safety
4. **Build** - Package builds successfully
5. **Docs** - Documentation builds

## 🏷️ Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

### Release Workflow

1. **Create Release Branch**
   ```bash
   git checkout -b release/v1.2.0 develop
   ```

2. **Prepare Release**
   - Update CHANGELOG.md
   - Update version in pyproject.toml
   - Run full test suite
   - Build documentation

3. **Merge to Main**
   ```bash
   git checkout main
   git merge --no-ff release/v1.2.0
   git tag -a v1.2.0 -m "Release version 1.2.0"
   ```

4. **Back-merge to Develop**
   ```bash
   git checkout develop
   git merge --no-ff release/v1.2.0
   ```

## 🛠️ Development Tools

### Required Setup

```bash
# Clone repository
git clone https://github.com/[your-org]/[repo].git
cd [repo]

# Create virtual environment (using uv for speed)
uv venv
source .venv/bin/activate  # or: uv shell

# Install dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Recommended Git Configuration

```bash
# Better diffs
git config diff.algorithm patience

# Helpful aliases
git config alias.co checkout
git config alias.br branch
git config alias.st status
git config alias.cm "commit -m"
git config alias.unstage "reset HEAD --"

# Always rebase on pull
git config pull.rebase true
```

## 🚫 Anti-Patterns

### Never Do These
- ❌ Force push to shared branches
- ❌ Commit directly to main/develop
- ❌ Merge without reviews
- ❌ Commit secrets or credentials
- ❌ Use `git add .` without review
- ❌ Ignore failing tests
- ❌ Skip pre-commit hooks

### Always Do These
- ✅ Write descriptive commit messages
- ✅ Keep commits atomic
- ✅ Review your own PR first
- ✅ Update documentation
- ✅ Add tests for new features
- ✅ Check for secrets before pushing
- ✅ Respond to reviews promptly

## 🔗 References

This document consolidates workflow standards from:
- Previous git-strategy.md
- CLAUDE.md Git & Version Control section
- CONTRIBUTING.md development workflow
- Industry best practices

All other project documents should reference this file for development workflow standards.

---

**Enforcement**: These standards are enforced through branch protection rules, pre-commit hooks, and CI/CD pipelines.
