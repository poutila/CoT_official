# 🔒 Security Standards

**Purpose**: Single source of truth for all security requirements and practices.  
**Status**: Authoritative - All other documents should reference this file.  
**Last Updated**: 2025-07-10

## 📋 Quick Reference

| Requirement | Standard | Enforcement |
|-------------|----------|-------------|
| **Secrets Management** | Never in code/logs | gitleaks, pre-commit |
| **Input Validation** | All inputs sanitized | Code review, bandit |
| **Authentication** | JWT 15-min tokens | API middleware |
| **HTTPS** | Required in production | Load balancer config |
| **Vulnerability Scanning** | Before each release | CI/CD pipeline |
| **OWASP Compliance** | ASVS Level 2 | Security audit |

## 🚨 Critical Security Rules

### NO-SEC-001: Never Commit Secrets
- **NEVER** commit secrets, API keys, passwords, or sensitive data
- Use environment variables for ALL secrets
- Rotate immediately if exposed
- **Enforcement**: `gitleaks` in pre-push hooks

### NO-SEC-002: Never Log Sensitive Data
- **NEVER** log passwords, tokens, PII, or financial data
- Implement PII redaction in logging middleware
- Use structured logging with field filtering
- **Enforcement**: Log scanning in CI/CD

### NO-SEC-003: Always Validate Input
- Validate ALL inputs at API boundaries
- Use parameterized queries (no SQL concatenation)
- Escape user input before rendering
- **Enforcement**: `bandit` security linting

### NO-SEC-004: Security Vulnerability Reporting
- Report vulnerabilities privately (never public issues)
- Use security@[your-org] email
- Follow responsible disclosure timeline
- **Enforcement**: Security policy, issue templates

## 🛡️ Security Implementation

### Authentication & Authorization

#### JWT Security Requirements
```python
JWT_CONFIG = {
    "ACCESS_TOKEN_LIFETIME": 15,  # minutes
    "REFRESH_TOKEN_LIFETIME": 10080,  # 7 days
    "ALGORITHM": "RS256",
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}
```

#### Session Management
- Secure session cookies (httpOnly, secure, sameSite)
- Session timeout after 30 minutes of inactivity
- Proper session invalidation on logout
- Rate limiting: 100 requests/minute per IP

### Data Protection

#### Encryption Requirements
- **At Rest**: AES-256 for sensitive data
- **In Transit**: TLS 1.3 minimum
- **Key Management**: Use dedicated key management service
- **Password Storage**: bcrypt with cost factor 12+

#### PII Handling
```python
# Example PII redaction
import re

def redact_pii(text: str) -> str:
    """Redact personally identifiable information."""
    # Email addresses
    text = re.sub(r'\b[\w._%+-]+@[\w.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    # Phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    # SSN
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    return text
```

### Security Headers

Required HTTP security headers:
```python
SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
```

## 🔍 Security Scanning Tools

### Required in Development
```bash
# Python security linting
bandit -r src/

# Dependency vulnerability scanning
safety check
pip-audit

# Secret detection
gitleaks detect
```

### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/PyCQA/bandit
    rev: '1.7.5'
    hooks:
      - id: bandit
        args: ['-r', 'src/']
        
  - repo: https://github.com/zricethezav/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

### CI/CD Security Pipeline
```yaml
security-scan:
  script:
    - bandit -r src/ -f json -o bandit-report.json
    - safety check --json > safety-report.json
    - pip-audit --format json > audit-report.json
  artifacts:
    reports:
      - "*-report.json"
```

## 🏗️ Secure Development Practices

### API Security
- Input validation using Pydantic models
- Output encoding to prevent XSS
- CSRF tokens for state-changing operations
- API rate limiting and throttling

### Database Security
- Use ORM to prevent SQL injection
- Principle of least privilege for DB users
- Regular security patches
- Encrypted connections

### Third-Party Dependencies
- Regular dependency updates
- Automated vulnerability scanning
- Review licenses for compliance
- Vendor security assessments

## 📊 OWASP ASVS Level 2 Compliance

Key requirements we implement:
- V2: Authentication Verification
- V3: Session Management
- V4: Access Control
- V5: Validation, Sanitization and Encoding
- V7: Error Handling and Logging
- V8: Data Protection
- V9: Communication Security

## 🚨 Incident Response

### Security Incident Checklist
1. **Detect** - Identify the security issue
2. **Contain** - Isolate affected systems
3. **Assess** - Determine scope and impact
4. **Notify** - Alert stakeholders
5. **Remediate** - Fix the vulnerability
6. **Document** - Create incident report
7. **Review** - Update procedures

### Emergency Contacts
- Security Team: security@[your-org]
- On-call Engineer: [Phone]
- CISO: [Contact]

## 🔗 References

This document consolidates security requirements from:
- Previous CLAUDE.md security section
- NO.md security rules
- Industry best practices (OWASP, NIST)

All other project documents should reference this file for security standards.

---

**Compliance**: These standards are mandatory and enforced through automated tools and code review.