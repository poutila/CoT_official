# Changelog

All notable changes to the Chain-of-Thought (CoT) specification will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [7.0.0-rc4] - 2024-01-26

### Added
- `sig_algo` metadata field in signature files for algorithm transparency (Issue #1)
- `sig_issued_at`, `sig_expires_at`, and RFC3161 timestamp metadata (Issue #3)
- CLI entry points via setuptools for easier tool installation (Issue #2)
- Golden output test suite for `langchain_integration.py` with snapshot testing (Issue #4)
- Enhanced `langchain_integration.py` to output both `.md` and `.json` formats
- Simulated live registry fallback in `cot-version-check.sh` via GitHub mirror (Issue #5)
- `trace_degraded_summary.md` test case for compression scenarios
- Structured data extraction example in LangChain integration
- Python wrapper `cot_version_check.py` for CLI consistency
- Comprehensive test file `test_golden_output.py` for deterministic output validation

### Changed
- `validate_bundle.py` now installable as `cot-validate` CLI command
- Version check script now attempts: primary registry → GitHub mirror → local file
- Improved error messages when network connectivity is limited
- Signature metadata now includes expiration and timestamp authority information

### Fixed
- Missing algorithm specification in GPG signature metadata
- Incomplete example outputs in LangChain integration
- Version check script error handling for offline scenarios
- CLI entry point verification and wrapper creation

### Security
- Added signature algorithm transparency for better security auditing
- Enhanced validation of cryptographic signatures with expiration tracking
- RFC3161 timestamp support for non-repudiation

### Documentation
- Created `COT_FIXES_REPORT.md` documenting all implemented fixes
- Updated examples with golden output standards
- Added test documentation for snapshot comparison

## [7.0.0] - 2024-01-26

### Added
- Applicability heuristics for determining when full CoT is required
- Conflict adjudication logic for contradictory evidence
- Compression strategies (Levels 0-3) for token management
- Recursive CoT handling with parent-child relationships
- Live/streaming input support for real-time systems
- Comprehensive freshness scoring for evidence evaluation
- Machine-readable validation schemas
- Post-deferral escalation hierarchy
- Token budget enforcement with automatic decomposition

### Changed
- Evidence now requires timestamp metadata (breaking change)
- Risk assessment is mandatory in all reasoning traces
- Minimum evidence requirements now risk-based (Low:1, Medium:2, High:3, Critical:5)
- Context uncertainty protocol for undefined environments
- Reasoning bounds to prevent token exhaustion

### Deprecated
- Version 5.0.0 support ends 2024-12-01
- Legacy trace formats without timestamp metadata

### Security
- Mandatory timestamp validation for all evidence
- Enhanced context verification requirements
- Stricter validation of evidence sources

## [6.0.0] - 2024-01-20

### Added
- Standard authority governance model
- Runtime contracts for cross-system compatibility
- Post-deferral escalation protocols
- Token budget management
- Interoperability guidelines

### Changed
- Formalized as official standard under CoT Standards Committee
- Enhanced validation requirements
- Improved error handling specifications

## [5.0.0] - 2023-12-01

### Added
- Context uncertainty handling
- Schema declarations
- Failure modes documentation
- Reasoning bounds specifications

### Changed
- Made context-aware with multiple citation formats
- Enhanced validation rules
- Improved deferral mechanisms

## [4.0.0] - 2023-11-01

### Added
- Machine-readable JSON schema
- Temporal reasoning requirements
- Risk-based evidence requirements
- Context-aware citations

### Changed
- Evidence quality metrics
- Validation automation
- Citation format standardization

## [3.0.0] - 2023-10-01

### Changed
- Made generic and project-independent
- Removed project-specific examples
- Standardized format requirements

## [2.0.0] - 2023-09-01

### Changed
- Complete refactor for bulletproof enforcement
- Enhanced validation requirements
- Stricter evidence standards

## [1.0.0] - 2023-08-01

### Added
- Initial Chain-of-Thought requirements
- Basic reasoning trace format
- Evidence collection guidelines
- Validation checklist

[7.0.0-rc4]: https://github.com/cot-standard/spec/compare/v7.0.0...v7.0.0-rc4
[7.0.0]: https://github.com/cot-standard/spec/compare/v6.0.0...v7.0.0
[6.0.0]: https://github.com/cot-standard/spec/compare/v5.0.0...v6.0.0
[5.0.0]: https://github.com/cot-standard/spec/compare/v4.0.0...v5.0.0
[4.0.0]: https://github.com/cot-standard/spec/compare/v3.0.0...v4.0.0
[3.0.0]: https://github.com/cot-standard/spec/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/cot-standard/spec/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/cot-standard/spec/releases/tag/v1.0.0