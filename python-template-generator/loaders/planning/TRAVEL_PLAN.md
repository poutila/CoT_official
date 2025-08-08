# Docpipe Test Coverage Travel Plan

## Purpose
Systematic tracking of test creation for all Python modules in the docpipe project, ensuring every file has adequate test coverage per CLAUDE.md requirements.

## Progress Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Total Python Files** | 30 | 30 | 📊 |
| **Files with Tests** | 2 | 30 | 🟡 |
| **Files >90% Coverage** | 10 | 27 | 🟡 |
| **Overall Coverage** | 70% | 100% | 🟢 |

*Note: `__init__.py` files excluded from 90% coverage requirement*

## Test Creation Priority

### 🎯 Priority 1: Core Functionality (Sprint 1)
These align with TASK.md Sprint 1 goals (T-002, T-003)

| File | Lines | Status | Coverage | Test File | Notes |
|------|-------|--------|----------|-----------|-------|
| `loaders/markdown_validator_enricher.py` | ~200 | ✅ TESTED | 93% | test_markdown_enricher.py | Core enrichment logic |
| `validators/document_level_semantic_validator.py` | 19 | ❌ No tests | 0% | - | Key validator |
| `validators/section_level_semantic_validator.py` | ~30 | ❌ No tests | 0% | - | Has bug to fix (T-004) |
| `validators/semantic_validator_base.py` | 15 | ❌ No tests | 0% | - | Base class, CPU fix applied |
| `main.py` | 128 | ✅ TESTED | 92% | test_main.py | Entry point, CLI interface |

### 🔧 Priority 2: Supporting Components (Sprint 2)
| File | Lines | Status | Coverage | Test File |
|------|-------|--------|----------|-----------|
| `extractors/rule_extractor.py` | 72 | ❌ No tests | 0% | - |
| `factories/validator_factory.py` | ~50 | ❌ No tests | 0% | - |
| `factories/ruleset_factory.py` | ~40 | ❌ No tests | 0% | - |
| `loaders/markdown_pydantic_model.py` | 67 | ❌ No tests | 0% | - |
| `models/rule.py` | ~30 | ❌ No tests | 0% | - |

### 📦 Priority 3: Protocols & Models (Sprint 3)
| File | Status | Notes |
|------|--------|-------|
| `protocols/document_protocol.py` | ❌ No tests | Interface definition |
| `protocols/validator_protocol.py` | ❌ No tests | Interface definition |
| `protocols/rule.py` | ❌ No tests | Protocol definition |
| `loaders/markdown_base_validator.py` | ❌ No tests | Base class |
| `validators/structural.py` | ❌ No tests | Additional validator |

### 🔄 Priority 4: Utilities (Future)
| File | Status | Notes |
|------|--------|-------|
| `json_utils/json_utils.py` | ❌ No tests | JSON handling |
| `loaders/sluggify_util.py` | ❌ No tests | Slug generation |
| `loaders/yaml_loader.py` | ❌ No tests | YAML support |
| `enricher_test.py` | N/A | Test script, not a module |

### ⚠️ Files to Review/Refactor
| File | Issue | Action Needed |
|------|-------|---------------|
| `loaders/yxxxAST_model.py.py` | Weird naming | Consider renaming/removing |
| `loaders/yxxxdocument_validator.py` | Appears unused | Consider removing |
| `xx__main__.py` | Unclear purpose | Review and possibly remove |

### ✅ Completed Files

| File | Coverage | Test File | Date Completed | Notes |
|------|----------|-----------|----------------|-------|
| `main.py` | 92% | `test_main.py` | 2025-01-08 | 8 tests with mocking |
| `models/rule.py` | 90% | via test_main | 2025-01-08 | Covered indirectly |
| `loaders/markdown_pydantic_model.py` | 92% | via test_main | 2025-01-08 | Covered indirectly |
| `loaders/sluggify_util.py` | 100% | via test_main | 2025-01-08 | Full coverage |
| Multiple `__init__.py` files | 100% | via imports | 2025-01-08 | Import coverage |

---

## Sprint Alignment

This travel plan supports the Sprint 1 tasks from TASK.md:
- **T-002**: Test Document Enricher → Priority 1 files
- **T-003**: Test Validators → Priority 1 validator files
- **T-004**: Fix SectionValidator Bug → Tracked in Priority 1

## Success Criteria

Each file should have:
- [ ] Corresponding test file in `tests/` directory
- [ ] Minimum 90% coverage (except `__init__.py`)
- [ ] Tests for success cases
- [ ] Tests for failure cases
- [ ] Edge case tests
- [ ] Proper test naming: `test_<module>_<condition>_<result>`

## Tracking Guidelines

When completing a file:
1. Move from priority section to "Completed Files"
2. Record actual coverage achieved
3. Note any issues or limitations
4. Update overall progress metrics

## Usage

This document complements TASK.md by providing:
1. **File-level granularity** for test tracking
2. **Priority grouping** aligned with sprint goals  
3. **Coverage targets** for each module
4. **Visual progress** of test creation effort

Update this document as test files are created to maintain visibility of overall test coverage progress.

---

*Last Updated: 2025-01-08 - Refactored for docpipe project*