# 📋 PROJECT PLANNING - docpipe

**READ THIS FIRST**: This document provides essential context for understanding the project's architecture, goals, constraints, and development approach. All contributors and AI assistants should review this before starting work.

**Last Updated**: 2025-01-08
**Project Status**: MVP / Early Development
**Current Version**: 0.1.0

## 📑 Table of Contents
- [🚦 Project Health Scorecard](#-project-health-scorecard)
- [🎯 Project Overview](#-project-overview)
- [🏗️ Architecture & Technology](#-architecture--technology)
- [📁 Project Structure](#-project-structure)
- [🔧 Development Standards](#-development-standards)
- [🚨 Constraints & Requirements](#-constraints--requirements)
- [🧪 Testing Strategy](#-testing-strategy)
- [🔄 Development Workflow](#-development-workflow)
- [📊 Monitoring & Observability](#-monitoring--observability)
- [🤝 Team & Collaboration](#-team--collaboration)
- [📚 References & Resources](#-references--resources)
- [📌 Decision Log](#-decision-log-optional)
- [📘 Glossary](#-glossary)
- [🗂️ Sprint Tracking](#-sprint-tracking-optional)
- [🔄 Document Maintenance](#-document-maintenance)

## 🚦 PROJECT HEALTH SCORECARD - ACTUAL STATE
*Reality check performed: 2025-01-08*

| Metric | Owner | Target | Current | Status | Notes |
|------------------------|---------|------------|---------|--------|-------|
| Code Coverage | Dev | >90% | **70%** | 🟡 | 23 tests created, significant progress! |
| Bug Escape Rate | Dev | <2/month | Unknown | ⚫ | No tracking system in place |
| Deployment Frequency | Dev | >1/week | Manual | 🔴 | No CI/CD configured |
| MTTR (Mean Time to Recovery) | Dev | <6 hours | N/A | ⚫ | No production deployment |
| Technical Debt Items | Dev | <5 open | Unknown | ⚫ | Not tracked |
| Security Scan Results | Dev | 0 critical | Not run | 🔴 | No security scanning configured |
| Performance | Dev | <200ms | ~100ms | ✅ | Validation runs in reasonable time |
| Functional Status | Dev | Working | Working | ✅ | Core enrichment and validation operational |

**Reality**: Project has working functionality but lacks all supporting infrastructure
**Git Status**: Single commit ("Initial commit") - project just beginning

---

## 🔍 REALITY CHECK - WHAT ACTUALLY EXISTS

### Working Components ✅
1. **Document Enrichment Pipeline**
   - `MarkdownDocEnricher` successfully processes markdown files
   - Extracts sections, links, metadata
   - Generates enriched JSON output

2. **Semantic Validation**
   - Document-level and section-level validators operational
   - Uses sentence-transformers for similarity scoring
   - Successfully detects divergence (51% similarity between docs)

3. **Rule Extraction**
   - Extracts validation rules from reference documents
   - Supports document and section-level rules

4. **Main Entry Point**
   - `src/docpipe/main.py` provides CLI interface
   - Can validate documents against references
   - Fixed to use CPU mode (no GPU required)

### Missing Infrastructure ❌
1. **Testing**: ZERO tests exist (empty `tests/` directory)
2. **CI/CD**: No GitHub Actions or automation
3. **Documentation**: Aspirational rather than accurate
4. **Quality Gates**: Tools installed but not enforced
5. **Version Control**: Only 1 commit in history

### File Count
- **Python modules**: 30+ files in `src/docpipe/`
- **Test files**: 0
- **Test coverage**: 0%

---

## 🎯 PROJECT OVERVIEW

### Vision & Goals
**Primary Objective**: Docpipe is a comprehensive document validation framework designed to validate markdown documents against reference standards and return enriched version of markdown document.

**Success Criteria**:
- [x] Read markdown document and return enriched version - **WORKING** (`enricher_test.py`)
- [x] Semantically validate markdown against reference - **WORKING** (51% similarity detected)
- [ ] Enhance validation methods - **IN PROGRESS**

**Target Users**:
- **Primary**: Developer/myself - internal tool for validating documentation standards

### Project Scope
**In Scope**:
- Enhance validation methods

**Explicitly Out of Scope**:
- Nothing "in case we need this in the future"

---

## 🏗️ ARCHITECTURE & TECHNOLOGY

### Technology Stack
**Core Technologies (Actually Implemented)**:
```
Language:    Python 3.12
Packages:    UV package manager
Models:      Pydantic for data validation
ML:          sentence-transformers (all-MiniLM-L6-v2)
Testing:     Pytest + Coverage (installed but UNUSED - 0 tests)
```

**Infrastructure**:
- **CI/CD**: ❌ None configured (empty `.github/workflows/`)
- **Version Control**: Git (1 commit only)
- **Pre-commit**: Config exists but likely not active

### System Architecture
**Architecture Style**: Monolith

**High-Level Design**:
```
Markdown document → Semantic enricher   →   Rules   →   Validation report
                            ↓
                    Enriched document
                            ↓
                    Processsor (AI...)
```

**Key Components**:
- **Document Enricher**: Returns Enriched document
- **Rules layer**: Provides rules for validation
- **Validation Layer**: Returns validation report

**Data Flow**:
1. Markdown passed to enricher
2. Rules and enriched document passed to validators
3. Validation report and enriched document

## 🔧 DEVELOPMENT STANDARDS

### SOLID Principles
All architecture and refactoring decisions should adhere to the SOLID principles:
- **S - Single Responsibility**: Each class/module has one reason to change
- **O - Open/Closed**: Software entities open for extension, closed for modification
- **L - Liskov Substitution**: Derived classes must be substitutable for base classes
- **I - Interface Segregation**: Clients shouldn't depend on methods they don't use
- **D - Dependency Inversion**: Depend on abstractions, not concretions

Applied consistently across services, domain models, and infrastructure modules. See [CLAUDE.md](../CLAUDE.md) for detailed examples and enforcement rules.

### Code Quality Enforcement Tools
**Installed but NOT Enforced**:
- **Type Checking**: mypy - ⚠️ Installed, not running
- **Linting**: ruff - ⚠️ Installed, not running
- **Testing**: pytest + pytest-cov - 🔴 **0% coverage, zero tests**
- **Mutation Testing**: Not configured
- **Security Scanning**: bandit + safety - ⚠️ Installed, not running
- **Complexity Analysis**: radon - Not configured
- **Dependency Health**: Not monitored

**Reality**: Tools installed via `uv sync --all-extras` but no automation or enforcement exists.

### AI Code Assistance Policy
- See **AI BEHAVIOR RULES** in [CLAUDE.md](../CLAUDE.md) for detailed requirements

### AI Contributor Scope
**Core Workflow Documents**:
- 📋 [TASK.md](./TASK.md) - Active task tracking and specifications
- 🤖 [CLAUDE.md](../CLAUDE.md) - AI behavior rules and development standards
- 🤖 [CHAIN_OF_THOUGHT_LIGHT.md](../CHAIN_OF_THOUGHT_LIGHT.md) - Description of CoT

**AI Assistants Are REQUIRED To**:
- ✅ **Create test files for ALL Python modules** - no exceptions
- ✅ **Verify 90%+ test coverage** before marking tasks complete
- ✅ **Write tests using CLAUDE.md naming conventions**
- ✅ **Include happy path, edge cases, and failure scenarios**
- ✅ **Run test suite and confirm passing** before completion

**AI Assistants Are Authorized To**:
- ✅ **Draft new features** from [TASK.md](../TASK.md) following established patterns
- ✅ **Refactor code** for SOLID principles, DRY compliance, YAGNI principle, KISS principle and maintainability
- ✅ **Write comprehensive tests** with proper coverage and edge cases
- ✅ **Update documentation** to reflect code changes
- ✅ **Fix bugs** following established debugging patterns
- ✅ **Optimize performance** within existing architectural boundaries

**AI Assistants CANNOT Mark Tasks Complete Without**:
- ❌ **Corresponding test files** for all Python modules
- ❌ **Verified test coverage report** showing 90%+ coverage
- ❌ **Passing test suite execution** confirmation

**AI Assistants Must NOT**:
- ❌ **Make architectural decisions** without explicit human review and approval
- ❌ **Add third-party dependencies** without team consensus via RFC process
- ❌ **Modify security configurations** or authentication mechanisms
- ❌ **Change database schemas** without migration review
- ❌ **Deploy to production** or modify CI/CD pipelines
- ❌ **Make breaking API changes** without stakeholder approval
- ❌ **Create code that is not needed now** without human approval

**Human Maintainers Are Responsible For**:
- 🔒 **All production deployments** and release coordination
- 🛡️ **Security reviews** and vulnerability patch triage
- 🏗️ **Final architecture approval** and design decisions
- 👥 **Team coordination** and stakeholder communication

**AI Assistants May Support These Activities But Not Own Them**

---

## 🤖 AUTOMATION DESIGN OVERVIEW

> **Strategic Automation**: The project implements comprehensive automation to reduce manual overhead, ensure consistency, and maintain compliance while preserving human oversight and decision-making authority.

### Automation Philosophy
**Human-Centric Automation**: All automation serves to amplify human productivity and decision-making rather than replace human judgment. Critical decisions, security changes, and architectural choices remain under human control.

**Fail-Safe Design**: Automation systems include human override capabilities, error recovery procedures, and graceful degradation when systems fail.

**Audit-Compliant**: All automated actions maintain complete audit trails for regulatory compliance and retrospective analysis.

### Core Automation Systems

#### **Task Management Automation**
**Bidirectional GitHub Integration**: Seamless synchronization between GitHub issues/PRs and TASK.md files.

**Key Features**:
- **Real-time Status Sync**: Task status updates automatically when GitHub issues/PRs change state
- **Review Status Tracking**: PR reviews automatically update task review status (✔️/🔍/⚠️/🚀)
- **Label Synchronization**: GitHub labels mirror TASK.md priorities and types
- **Task ID Linkage**: `task_id: T-XXX` references create automatic bidirectional connections

**Benefits**: Eliminates manual sync overhead, ensures consistency, provides single source of truth

#### **Sprint File Management**
**Automated Sprint Transitions**: Complete sprint boundary management with archival and new sprint initialization.

**Process Flow**:
1. **Archive Trigger**: Manual workflow dispatch or scheduled sprint end
2. **File Versioning**: Current TASK.md archived as immutable compliance record
3. **New Sprint Creation**: Fresh TASK.md generated from template with updated sprint metadata
4. **Archive Indexing**: Automatic update of sprint archive navigation

**Compliance Value**: Immutable audit trails, regulatory compliance, historical analysis capability

#### **Quality Assurance Automation**
**Continuous Quality Gates**: Automated enforcement of CLAUDE.md standards without human intervention.

**Validation Pipeline**:
- **Task Validation**: Automated TASK.md format and consistency checking
- **Code Quality**: Type checking, linting, formatting, security scanning
- **Test Coverage**: Automated coverage reporting and mutation testing
- **Documentation**: Link validation and cross-reference checking

**Standards Enforcement**: Zero-tolerance automation ensures consistent adherence to governance standards

#### **Metadata & Metrics Automation**
**Real-time Dashboard Updates**: Automatic calculation and display of project health metrics.

**Automated Metrics**:
- **Sprint Progress**: Task completion rates and burndown calculations
- **Quality Indicators**: Code coverage, test success rates, security scan results
- **Process Metrics**: Review cycle times, deployment frequency, incident response
- **Health Scoring**: Overall project health based on multiple indicators

**Executive Value**: Real-time visibility without manual reporting overhead

### Automation Architecture

#### **Technology Stack**
```yaml
Platform: GitHub Actions
Languages: Python 3.11+, Bash, YAML
Key Libraries:
  - Validation: pydantic, tabulate
  - GitHub API: @octokit/rest
  - Configuration: PyYAML, jq
  - Task Execution: nox, pytest
  - Security: bandit, safety
```

#### **Workflow Architecture**
```mermaid
graph TD
    A[GitHub Events] --> B[Workflow Triggers]
    B --> C[Validation Layer]
    C --> D[Business Logic]
    D --> E[File Updates]
    E --> F[Notification System]
    F --> G[Audit Logging]

    H[Configuration Files] --> D
    I[Human Overrides] --> D
    J[Error Recovery] --> D
```

#### **Configuration Management**
**Centralized Configuration**: All automation settings managed through version-controlled configuration files.

**Key Configuration Sources**:
- **sprint.config.json**: Sprint metadata and parameters
- **labels.yml**: GitHub label definitions and synchronization rules
- **workflow files**: GitHub Actions automation logic
- **validation schemas**: TASK.md and document structure requirements

**Change Management**: All configuration changes require peer review and validation testing

### Implementation Phases

#### **Phase 1: Foundation** *(Partial)*
- ✅ **Core Documentation**: CLAUDE.md, PLANNING.md, TASK.md exist
- ❌ **Basic Automation**: No CI/CD pipeline exists
- ❌ **Quality Gates**: No automated testing (0 tests)

#### **Phase 2: Task Integration** *(Not Started)*
- ❌ **GitHub Sync**: Not implemented
- ❌ **Label Management**: Not configured
- ❌ **File Validation**: Manual only

#### **Phase 3: Sprint Management** *(Not Started)*
- ❌ **Automated Archival**: Not implemented
- ❌ **Metadata Updates**: Manual only
- ❌ **Configuration Management**: Basic config files exist

#### **Phase 4: Advanced Features** *(Not Started)*
- ❌ **Error Recovery**: Not implemented
- ❌ **Audit Compliance**: Not implemented  
- ❌ **Performance Monitoring**: Not implemented


### Future Roadmap

#### **Short-term Enhancements** *(Next 3 months)*
- **Enhanced Metrics**: More sophisticated project health indicators
- **Smart Notifications**: Intelligent alerting based on context and priority
- **Integration Expansion**: Additional external service integrations

#### **Medium-term Vision** *(6-12 months)*
- **Predictive Analytics**: Trend analysis and proactive issue identification
- **AI-Enhanced Automation**: Machine learning for improved decision support
- **Cross-Project Integration**: Shared automation across multiple projects

#### **Long-term Strategy** *(1-2 years)*
- **Self-Healing Systems**: Automated detection and resolution of common issues
- **Adaptive Workflows**: Automation that learns and improves from team patterns
- **Enterprise Integration**: Organization-wide governance automation platform

### Documentation & Support

#### **Automation Documentation**
- **[Task Automation Implementation Plan](docs/automation/task_automation_plan.md)**: Complete technical implementation guide
- **[TECHNICAL_REGISTRY.md](planning/TECHNICAL_REGISTRY.md)**: Comprehensive file and script inventory
- **[Workflow Troubleshooting Guide](docs/automation/troubleshooting.md)**: Common issues and resolution procedures
- **[Override Procedures](docs/governance/overrides.md)**: Human intervention protocols

#### **Training & Support**
- **Documentation Maintenance**: Continuous updates to manuals as project evolves

This automation design provides the strategic foundation for efficient, compliant, and human-controlled project governance at enterprise scale.

### Project-Specific Pattern examples
**Service Layer Pattern**:
```python
# Services orchestrate domain logic and external calls
class UserRegistrationService:
    def __init__(self, user_repo: UserRepository, email_service: EmailService):
        self.user_repo = user_repo
        self.email_service = email_service

    def register_user(self, user_data: UserRegistrationData) -> User:
        # Validation, business logic, external calls
        pass
```

**Repository Pattern**:
```python
# Data access abstraction
class UserRepository(Protocol):
    def save(self, user: User) -> User: ...
    def find_by_email(self, email: str) -> Optional[User]: ...
```

**Configuration Management**:
```python
# Centralized config with environment-specific overrides
class Settings(BaseSettings):
    database_url: str
    redis_url: str
    api_secret_key: SecretStr

    class Config:
        env_file = ".env"
```

**CI/CD Pipeline**:
1. Unit tests (parallel execution)
2. Integration tests (with test DB)
3. E2E tests (against staging environment)
4. Performance tests (load testing key endpoints)

### Testing Service-Level Objectives
**Development Workflow SLAs**:
- **Pull request review cycle**: < 24 hours (business days)
- **All tests execution time**: < 5 minutes (local and CI)
- **Mutation testing score**: > 80% for business logic modules
- **Flaky test remediation**: Quarantined within 1 sprint, fixed within 2 sprints
- **Test data setup**: < 30 seconds for integration test suite
- **Coverage report generation**: < 2 minutes

**Mutation Testing Protocol**:
- **Tracking**: Results stored in `tests/mutants/{module_name}.json` per module
- **Thresholds**: Business logic (80%+), utilities (70%+), integrations (60%+)
- **Quarantine Policy**: Tests failing >3 times in 48 hours are auto-quarantined
- **Reintroduction**: Quarantined tests reviewed weekly, fixed tests re-enabled after 2 consecutive passes

**Quality Gates**:
- Zero failing tests before merge
- No reduction in coverage percentage
- All security scans pass
- Performance tests within acceptable thresholds

### Story Points Estimation Framework
**Purpose**: Story points provide relative effort estimation independent of individual developer speed or calendar time.

**Fibonacci-Based Scale**:
| Points | Complexity | Time Range | Description | Examples |
|--------|------------|------------|-------------|----------|
| **1** | Trivial | < 2 hours | Simple config changes, documentation fixes | Update README, change environment variable |
| **2** | Small | 2-4 hours | Minor features, simple bug fixes | Add validation rule, fix CSS styling |
| **3** | Moderate | 4-8 hours (≤1 day) | Standard features, typical bug fixes | Create API endpoint, implement form validation |
| **5** | Complex | 1-3 days | Multi-step features, complex integrations | User authentication flow, third-party API integration |
| **8** | Large | 3-5 days | Significant features, major refactoring | Payment processing system, complex data migration |
| **13** | Epic | 1-2 weeks | Major features, architectural changes | New user dashboard, microservice extraction |
| **21** | Epic+ | > 2 weeks | Large initiatives requiring breakdown | Complete redesign, new product module |

**Estimation Guidelines**:
- **Relative Sizing**: Compare against previously completed tasks
- **Include All Work**: Development + testing + documentation + review time
- **Account for Unknowns**: Add points for research, learning, or uncertainty
- **Team Calibration**: Regularly review completed tasks to align estimation

**Epic Breakdown Rules**:
- **13+ Points**: Consider breaking into smaller tasks
- **21+ Points**: Must be broken down into 3-8 point sub-tasks
- **Epic Tracking**: Use separate `epics/E-XXX.md` files for large initiatives

**Velocity Calculation**:
- **Sprint Velocity**: Total points completed in a sprint
- **Team Velocity**: Average points per sprint over last 3-6 sprints
- **Capacity Planning**: Use velocity to plan future sprint commitments

---

## 🔄 DEVELOPMENT WORKFLOW

### Git Strategy
**Recommended Branch Model**: GitHub Flow (lightweight, continuous deployment friendly)
- `main` - Production-ready code, protected branch
- `feature/feature-name` - Feature development branches
- `hotfix/issue-description` - Critical production fixes

**Alternative Models**:
- **GitFlow**: For projects with scheduled releases and longer development cycles
- **Custom**: For complex multi-service environments

**Detailed Strategy**: See [docs/development/git-strategy.md](docs/development/git-strategy.md) for branch protection rules, merge policies, and release procedures.

### Release Process
**Version Strategy**: Semantic Versioning (MAJOR.MINOR.PATCH)
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, security updates

**Deployment Targets**:
- **Development**: Auto-deploy from `develop` branch (continuous deployment)
- **Staging**: Manual promotion from `develop` (feature testing and QA)
- **Production**: Tagged release from `main` branch (controlled release)

**Release Checklist**:
- [ ] All tests pass
- [ ] Security scan clean
- [ ] Performance benchmarks meet targets
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Staging deployment successful
- [ ] Migration scripts tested

**Environment Promotion Flow**:
```
feature/branch → develop → staging → main → production
     ↓              ↓         ↓        ↓         ↓
   CI tests    Auto-deploy  Manual   Tag    Production
                           promotion release   deploy
```

---

## 📚 REFERENCES & RESOURCES

### Documentation Links
- [Deployment Guide](docs/deployment/README.md)
- [Troubleshooting Guide](docs/troubleshooting.md)

### Architecture Decision Records (ADRs)
All significant architectural changes must be proposed as an ADR using the `docs/adr/` template. Each ADR should be:
- **Reviewed** by at least one senior developer or tech lead before implementation
- **Linked** in relevant pull requests that implement the decision
- **Assigned** a unique ID (ADR-001, ADR-002, etc.) and summarized in CHANGELOG.md when merged
- **Status tracked**: Proposed → Accepted/Rejected → Implemented/Superseded

**ADR Template**: Use `docs/adr/template.md` for consistency across all architectural decisions.


## 📘 GLOSSARY

**Technical Terms**:
- **ADR**: Architecture Decision Record - documented design decisions with rationale
- **API**: Application Programming Interface - contract for software communication
- **CI/CD**: Continuous Integration / Continuous Deployment - automated development pipeline
- **DDD**: Domain-Driven Design - software design approach focused on business domain
- **DRY**: Don't Repeat Yourself - principle of reducing code duplication
- **MTTR**: Mean Time to Recovery - average time to restore service after failure
- **RPS**: Requests Per Second - measure of API throughput capacity
- **SLA**: Service-Level Agreement - commitment to specific performance standards
- **SOLID**: Software design principles (Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion)

**Business Terms**:
- **Sprint**: Time-boxed development iteration (typically 1-2 weeks)
- **Velocity**: Amount of work completed per sprint (measured in story points)
- **Technical Debt**: Code that needs refactoring for long-term maintainability
- **Stakeholder**: Person or team with interest in project outcomes

**Quality Metrics**:
- **Code Coverage**: Percentage of code executed during tests
- **Mutation Score**: Percentage of code mutations detected by tests
- **Cyclomatic Complexity**: Measure of code path complexity

---

## 🗂️ SPRINT TRACKING (Optional)

*Use this section to log sprint outcomes and learnings. Update after each sprint retrospective.*

### Sprint [Number] - [YYYY-MM-DD to YYYY-MM-DD]

**Completed**:
- [ ] [Feature A] - Live in staging, user testing in progress
- [ ] [Refactor B] - Merged to develop, 15% performance improvement measured
- [ ] [Bug Fix C] - Resolved critical auth issue, deployed to production

**Blockers Encountered**:
- [ ] [Service Y rate limiting] - Pending vendor feedback on quota increase
- [ ] [Database migration delay] - Compatibility issue found, workaround implemented
- [ ] [Third-party integration] - API documentation outdated, reverse-engineering required

**Lessons Learned**:
- **Performance**: Offloading cache logic improved API latency by 40%
- **Testing**: Mutation testing caught 3 critical bugs that unit tests missed
- **Architecture**: Service layer separation made feature development 25% faster
- **Process**: Daily async standups worked better than video calls for this sprint

**Metrics This Sprint**:
- Velocity: [Story points completed]
- Bug escape rate: [Bugs found in production]
- Code coverage: [Percentage achieved]
- Deployment frequency: [Number of deployments]

**Action Items for Next Sprint**:
- [ ] Investigate Service Y alternatives - [Owner] - [Due Date]
- [ ] Implement circuit breaker pattern - [Owner] - [Due Date]
- [ ] Schedule knowledge sharing session on new patterns - [Owner] - [Due Date]

---

*Previous sprint summaries archived in `docs/sprint-summaries/`*

---

## 🔄 DOCUMENT MAINTENANCE

**Review Schedule**: As needed based on project progress
**Update Triggers**:
- Major architecture changes
- New technology adoptions
- Significant constraint changes
- Reality checks revealing discrepancies

**Owner**: Project Developer
**Last Reviewed**: 2025-01-08 (Major reality check - removed fictional metrics)
**Next Review**: When testing infrastructure is added

---

## ⚠️ IMPORTANT NOTICE

**This document was refactored on 2025-01-08 to reflect ACTUAL project state rather than aspirational goals.**

Previous version contained fictional metrics (92% test coverage when 0 tests exist, 2.1 deployments/week with no CI/CD, etc.). This version accurately represents:
- What actually works (document enrichment, validation)
- What doesn't exist (tests, CI/CD, automation)
- Realistic next steps rather than imaginary achievements

*This document now serves as an honest project baseline. Future updates should maintain this accuracy.*