# 📁 Project Structure Standards

**Purpose**: Single source of truth for project organization and file structure requirements.  
**Status**: Authoritative - All other documents should reference this file.  
**Last Updated**: 2025-07-10

## 📋 Quick Reference

| Structure Type | When to Use | Key Directories |
|----------------|-------------|-----------------|
| **Domain-Driven Design** | Complex web applications | domain/, services/, api/ |
| **Non-DDD Structure** | CLI tools, simple projects | module-based organization |
| **Agent Structure** | AI agent projects | agents/, tools/, prompts/ |

## 🏗️ Structure Options

### Option 1: Domain-Driven Design (Complex Projects)

For complex web applications with business logic, persistence, and events:

```
project/
├── src/
│   ├── <project_name>/              # Root package (e.g., "docpipe")
│   │   ├── domain/                  # Core business logic
│   │   │   ├── entities/            # Business entities
│   │   │   ├── value_objects/       # Value objects
│   │   │   ├── repositories/        # Repository interfaces
│   │   │   └── exceptions.py        # Domain exceptions
│   │   ├── services/                # Application services
│   │   │   ├── auth_service.py      # Authentication
│   │   │   ├── user_service.py      # User management
│   │   │   └── __init__.py
│   │   ├── api/                     # External interfaces
│   │   │   ├── rest/                # REST endpoints
│   │   │   ├── graphql/             # GraphQL schema
│   │   │   └── cli/                 # CLI commands
│   │   ├── database/                # Persistence layer
│   │   │   ├── models/              # ORM models
│   │   │   ├── migrations/          # Schema migrations
│   │   │   └── repositories/        # Repository implementations
│   │   ├── events/                  # Event-driven architecture
│   │   │   ├── handlers/            # Event handlers
│   │   │   ├── publishers/          # Event publishers
│   │   │   └── schemas.py           # Event schemas
│   │   ├── utils/                   # Shared utilities
│   │   ├── config/                  # Configuration
│   │   └── __init__.py
│   └── __init__.py
├── tests/                           # Mirror src structure
├── docs/                            # Documentation
├── scripts/                         # Utility scripts
├── pyproject.toml
└── README.md
```

### Option 2: Non-DDD Structure (Simple Projects)

For CLI tools, scripts, and projects without complex business domains:

```
project/
├── src/
│   ├── <project_name>/              # Package name (e.g., "docpipe")
│   │   ├── analyzers/               # Feature module 1
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── specific.py
│   │   ├── cli/                     # Feature module 2
│   │   │   ├── __init__.py
│   │   │   └── commands.py
│   │   ├── core/                    # Core functionality
│   │   │   ├── __init__.py
│   │   │   └── engine.py
│   │   ├── models/                  # Data structures
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   ├── utils/                   # Utilities
│   │   │   └── __init__.py
│   │   ├── __init__.py              # Package init
│   │   └── main.py                  # Entry point
├── tests/                           # Mirror src structure
│   ├── analyzers/
│   ├── cli/
│   ├── core/
│   └── models/
├── docs/
├── scripts/
├── pyproject.toml
└── README.md
```

### Option 3: Agent-Specific Structure

For AI agent projects with tools and prompts:

```
project/
├── agents/
│   ├── <agent_name>/
│   │   ├── agent.py                 # Main agent (<200 lines)
│   │   ├── tools.py                 # Tool implementations (<300 lines)
│   │   ├── prompts.py               # System prompts
│   │   ├── config.py                # Agent configuration
│   │   └── __init__.py              # Public interface
│   └── shared/                      # Shared agent utilities
├── src/
│   └── <project_name>/              # Core project code
├── tests/
├── docs/
└── pyproject.toml
```

## 📏 Structure Rules

### File Organization
1. **Source code** in `src/<project_name>/`
2. **Tests mirror source** structure exactly
3. **Documentation** in `docs/`
4. **Scripts** in `scripts/`
5. **Configuration** at project root

### Naming Conventions
- **Packages**: lowercase, no underscores preferred
- **Modules**: lowercase with underscores
- **Classes**: PascalCase
- **Functions**: snake_case
- **Constants**: UPPER_SNAKE_CASE

### File Size Limits
- **Python files**: Maximum 500 lines
- **Config files**: Maximum 200 lines
- **Documentation**: Reasonable length for topic

### Required Files
```
project/
├── README.md                        # Project overview
├── LICENSE                          # License file
├── CHANGELOG.md                     # Version history
├── CONTRIBUTING.md                  # Contribution guide
├── pyproject.toml                   # Project configuration
├── .gitignore                       # Git exclusions
├── .pre-commit-config.yaml          # Pre-commit hooks
└── noxfile.py                       # Task automation
```

## 📂 Directory Standards

### `/src`
- Contains all source code
- One main package directory
- No non-Python files (except `py.typed`)

### `/tests`
- Mirrors `/src` structure exactly
- Test files named `test_<module>.py`
- Fixtures in `conftest.py`
- Test data in `tests/data/`

### `/docs`
```
docs/
├── api/                             # API documentation
├── architecture/                    # System design
├── guides/                          # User guides
├── standards/                       # This document and others
└── _static/                         # Images, diagrams
```

### `/scripts`
```
scripts/
├── deployment/                      # Deploy scripts
├── maintenance/                     # Cleanup, fixes
├── testing/                         # Test utilities
└── utilities/                       # General tools
```

## 🚫 Anti-Patterns

### Never Do These
- ❌ Mix source and tests in same directory
- ❌ Put scripts in package directory
- ❌ Create deeply nested structures (>4 levels)
- ❌ Use `src/` for non-Python files
- ❌ Ignore the chosen structure pattern

### Always Do These
- ✅ Keep related code together
- ✅ Follow consistent naming
- ✅ Document non-obvious organization
- ✅ Create `__init__.py` for packages
- ✅ Use relative imports within package

## 🔍 Structure Validation

### Check Structure Compliance

```python
# Run structure validation
python scripts/test_coverage_tool.py

# Expected output:
# ✅ Source files in src/<project_name>/
# ✅ Tests mirror source structure
# ✅ No stale test files
# ✅ Coverage meets requirements
```

### Common Issues
1. **Missing `__init__.py`** - Makes directory a package
2. **Tests not mirroring source** - Hard to find tests
3. **Deep nesting** - Difficult navigation
4. **Mixed concerns** - Unclear organization

## 📝 When to Use Each Structure

### Use DDD When:
- Building web applications
- Complex business logic
- Multiple bounded contexts
- Need for event sourcing
- Team familiar with DDD

### Use Non-DDD When:
- Building CLI tools
- Simple scripts or utilities
- Data processing pipelines
- No complex domain logic
- Small team or project

### Use Agent Structure When:
- Building AI agents
- Tool-based architectures
- Prompt engineering focus
- LLM integration

## 🔗 Migration Guide

### From Non-DDD to DDD:
1. Create domain directory
2. Extract entities from models
3. Move business logic to domain
4. Create service layer
5. Refactor imports

### From DDD to Non-DDD:
1. Flatten domain into features
2. Merge services into core
3. Simplify repository pattern
4. Update imports
5. Remove unused abstractions

## 🔗 References

This document consolidates structure requirements from:
- CLAUDE.md Module Organization section
- planning/PLANNING.md directory structure
- PROJECT_STRUCTURE_AUDIT.md findings
- Industry best practices

All other project documents should reference this file for structure standards.

---

**Note**: Choose one structure pattern and stick to it. Mixing patterns leads to confusion and maintenance issues.