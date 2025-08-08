# Contributing to Chain-of-Thought Standard

Thank you for your interest in contributing to the Chain-of-Thought (CoT) reasoning standard! This document outlines the process for contributing and participating in governance.

## Quick Links

- **Specification**: [CHAIN_OF_THOUGHT.md](CHAIN_OF_THOUGHT.md)
- **Governance**: [COT_STANDARD_AUTHORITY.md](COT_STANDARD_AUTHORITY.md)
- **Issues**: https://github.com/cot-standard/spec/issues
- **Discussions**: https://github.com/cot-standard/spec/discussions

## Types of Contributions

### 1. Bug Reports and Issues
- Use the issue tracker for bugs in the specification
- Include version number and specific section references
- Provide examples demonstrating the issue

### 2. Feature Requests (RFCs)
- Submit as RFC (Request for Comments) via GitHub issues
- Use template: `.github/ISSUE_TEMPLATE/rfc.md`
- Include motivation, specification changes, and examples

### 3. Implementation Feedback
- Share experiences implementing the standard
- Report ambiguities or practical challenges
- Suggest clarifications or improvements

### 4. Documentation Improvements
- Fix typos, improve clarity, add examples
- Submit via pull request
- Does not require RFC process

## Contribution Process

### For Minor Changes (Typos, Clarifications)

1. Fork the repository
2. Create a branch: `fix/description-of-change`
3. Make your changes
4. Submit a pull request
5. Requires 2 approvers (7-day review period)

### For Feature Changes (RFCs)

1. **Draft RFC**
   ```markdown
   # RFC-XXX: Title
   
   ## Summary
   Brief description of the change
   
   ## Motivation
   Why is this change needed?
   
   ## Specification
   Detailed changes to the standard
   
   ## Examples
   Before/after examples
   
   ## Backwards Compatibility
   Impact on existing implementations
   
   ## Security Considerations
   Any security implications
   ```

2. **Submit as Issue**
   - Label: `rfc`
   - Title: `RFC: Your Feature Name`
   - Allow 30 days for comments

3. **Committee Review**
   - Simple majority (4/7) for minor features
   - Supermajority (5/7) for breaking changes
   - Security veto: Any 2 members can block

4. **Implementation**
   - Once approved, submit PR with changes
   - Update version numbers
   - Add to changelog

### For Security Issues

**DO NOT** open public issues for security vulnerabilities.

Email: security@cot-standard.org (PGP available)

Include:
- Affected versions
- Description of vulnerability
- Proof of concept (if applicable)
- Suggested fix

## Governance Participation

### Becoming a Committee Member

Per [COT_STANDARD_AUTHORITY.md](COT_STANDARD_AUTHORITY.md#membership-criteria):

1. **Demonstrate Expertise**
   - Published work on AI reasoning or formal methods
   - Significant contributions to CoT implementations
   - Active participation in RFC discussions

2. **Apply for Membership**
   - Email: committee@cot-standard.org
   - Include:
     - CV/Resume
     - Links to relevant work
     - Statement of interest
     - Conflict of interest declaration

3. **Selection Process**
   - Existing committee votes
   - Simple majority required
   - Annual membership review

### Committee Responsibilities

- Review and vote on RFCs
- Maintain specification quality
- Ensure backward compatibility
- Respond to security issues
- Guide community contributions

## Code of Conduct

### Our Standards

- **Respectful Communication**: Professional and constructive
- **Inclusive Environment**: Welcome all contributors
- **Technical Focus**: Keep discussions technical
- **Good Faith**: Assume positive intent
- **Transparency**: Decisions made openly

### Unacceptable Behavior

- Personal attacks or harassment
- Discriminatory language or actions
- Off-topic or inflammatory comments
- Violation of security policies
- Bad faith contributions

### Enforcement

Reports to: conduct@cot-standard.org

Committee will review and may:
- Issue warnings
- Temporarily ban from discussions
- Permanently ban from project

## Development Setup

### Prerequisites

```bash
# Python 3.8+
python3 --version

# Git
git --version

# GPG (for signed commits)
gpg --version
```

### Clone Repository

```bash
git clone https://github.com/cot-standard/spec.git
cd spec
```

### Install Dependencies

```bash
# Validation tools
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Validate bundle
python validate_bundle.py chain_of_thought.bundle.json

# Run integration tests
cd test_integration
./run_tests.sh

# Check specific trace
python validate_bundle.py bundle.json --verify-trace my_trace.md
```

## Pull Request Guidelines

### PR Title Format
- `fix: Brief description` (bug fixes)
- `feat: Brief description` (new features)
- `docs: Brief description` (documentation)
- `refactor: Brief description` (code changes)
- `test: Brief description` (test changes)

### PR Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Changelog entry added
- [ ] No breaking changes (or RFC approved)
- [ ] Signed commits (GPG)

### Review Process
1. Automated checks must pass
2. Two approvers required
3. No unresolved discussions
4. Merge after review period

## Version Management

### Version Format
`MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes, clarifications

### Release Process
1. Update version in all files
2. Update CHANGELOG.md
3. Create git tag
4. Sign release with committee key
5. Update registry.json
6. Announce on mailing list

## Resources

### Documentation
- [README.md](README.md) - Overview
- [CHAIN_OF_THOUGHT.md](CHAIN_OF_THOUGHT.md) - Specification
- [COT_INTEROPERABILITY.md](COT_INTEROPERABILITY.md) - Integration guide

### Tools
- [validate_bundle.py](validate_bundle.py) - Validation tool
- [cot-version-check.sh](cot-version-check.sh) - Version checker
- [examples/](examples//README.md) - Implementation examples

### Community
- GitHub Discussions: Questions and ideas
- Mailing List: announcements@cot-standard.org
- IRC: #cot-standard on Libera.Chat

## Recognition

Contributors are recognized in:
- CHANGELOG.md (per release)
- Annual contributors report
- Committee membership (for significant contributors)

## Questions?

- General: info@cot-standard.org
- Security: security@cot-standard.org
- Committee: committee@cot-standard.org

Thank you for helping improve the Chain-of-Thought standard!