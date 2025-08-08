# 🧪 Testing Standards

**Purpose**: Single source of truth for all testing requirements across the project.  
**Status**: Authoritative - All other documents should reference this file.  
**Last Updated**: 2025-07-10

## 📋 Quick Reference

| Requirement | Value | Enforcement |
|-------------|-------|-------------|
| **Minimum Coverage** | 90% | CI/CD fails below threshold |
| **Test File Naming** | `test_<module_name>.py` | Pre-commit hook |
| **Test Function Naming** | `test_<method>_<condition>_<expected_result>` | Code review |
| **Required Test Types** | Unit, Integration, Edge cases, Error conditions | Test templates |

## 🎯 Core Requirements

### 1. Coverage Requirements

- **Minimum 90% code coverage** enforced via `pytest-cov`
- CI/CD pipeline fails if coverage drops below threshold
- Run coverage check: `pytest --cov=. --cov-fail-under=90`

### 2. Test File Organization

Every Python file (except `__init__.py` and `__version__.py`) MUST have a corresponding test file:

```
src/docpipe/module.py → tests/docpipe/test_module.py
src/docpipe/utils/helper.py → tests/docpipe/utils/test_helper.py
```

### 3. Test Naming Convention

Use descriptive names following this pattern:
```python
def test_<method>_<condition>_<expected_result>():
    """Test description."""
    
# Examples:
def test_calculate_total_valid_input_returns_sum():
def test_parse_config_missing_file_raises_error():
def test_connect_database_timeout_retries_three_times():
```

### 4. Required Test Categories

Every module must include:

#### Unit Tests (Minimum 1 per public method)
```python
def test_analyzer_init_valid_config_succeeds():
    """Test analyzer initializes with valid configuration."""
    config = AnalysisConfig(check_compliance=True)
    analyzer = DocumentAnalyzer(config)
    assert analyzer.config.check_compliance is True
```

#### Edge Case Tests (Minimum 2 per module)
```python
def test_parser_empty_document_returns_empty_result():
    """Test parser handles empty documents gracefully."""
    result = parse_document("")
    assert result == ParseResult(content=[], errors=[])

def test_analyzer_max_file_size_enforces_limit():
    """Test analyzer respects maximum file size."""
    large_content = "x" * (MAX_FILE_SIZE + 1)
    with pytest.raises(FileSizeError):
        analyze_content(large_content)
```

#### Error Condition Tests (Minimum 1 per module)
```python
def test_loader_invalid_path_raises_file_not_found():
    """Test loader raises appropriate error for missing files."""
    with pytest.raises(FileNotFoundError) as exc_info:
        load_document("/nonexistent/path.md")
    assert "not found" in str(exc_info.value)
```

#### Integration Tests (When applicable)
```python
def test_full_analysis_pipeline_valid_project_succeeds():
    """Test complete analysis pipeline with real project structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup test project
        create_test_project(tmpdir)
        
        # Run full analysis
        results = analyze_project(tmpdir)
        
        # Verify results
        assert results.compliance_score >= 80
        assert len(results.issues) == 0
```

## 🔧 Testing Tools & Configuration

### Required Testing Dependencies
```txt
pytest==8.3.4
pytest-cov==6.0.0
pytest-xdist==3.6.0    # Parallel execution
hypothesis==6.103.1    # Property-based testing
```

### Pytest Configuration (pyproject.toml)
```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = [
    "--strict-markers",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-fail-under=90",
]
```

## 📊 Advanced Testing Patterns

### Fixtures for Common Test Data
```python
@pytest.fixture
def sample_config():
    """Provide standard configuration for tests."""
    return AnalysisConfig(
        check_compliance=True,
        similarity_threshold=0.8
    )

@pytest.fixture
def mock_document():
    """Provide mock document for testing."""
    return Document(
        path="test.md",
        content="# Test Document\n\nContent here."
    )
```

### Property-Based Testing (For Complex Logic)
```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers(), min_size=1))
def test_statistics_mean_always_between_min_and_max(numbers):
    """Test that mean is always between min and max values."""
    result = calculate_statistics(numbers)
    assert min(numbers) <= result.mean <= max(numbers)
```

### Performance Testing (For Critical Paths)
```python
def test_analyzer_performance_under_200ms():
    """Test analyzer completes within performance budget."""
    start_time = time.time()
    analyze_document("sample.md")
    elapsed = time.time() - start_time
    assert elapsed < 0.2  # 200ms requirement
```

## 🚫 Testing Anti-Patterns to Avoid

### ❌ Don't Use Bare Assertions
```python
# Bad
assert result

# Good  
assert result is not None, "Expected result but got None"
```

### ❌ Don't Test Implementation Details
```python
# Bad - Testing private method
def test_analyzer_private_method():
    analyzer._internal_process()

# Good - Test public interface
def test_analyzer_process_document():
    result = analyzer.process("doc.md")
```

### ❌ Don't Write Vague Test Names
```python
# Bad
def test_analyzer():
def test_error():

# Good
def test_analyzer_valid_markdown_returns_parsed_content():
def test_analyzer_invalid_syntax_raises_parse_error():
```

## 🔍 Mutation Testing (For Critical Modules)

For business-critical modules, use mutation testing:

```bash
mutmut run --paths-to-mutate=src/docpipe/analyzers/compliance.py
mutmut results
```

Target: Mutation score > 80% for critical modules

## 📝 Test Documentation

Every test should have:
1. Clear docstring explaining what is being tested
2. Arrange-Act-Assert structure
3. Meaningful variable names

```python
def test_config_parser_invalid_yaml_provides_helpful_error():
    """Test that parser provides actionable error message for invalid YAML.
    
    Users should receive clear guidance on fixing configuration errors.
    """
    # Arrange
    invalid_yaml = "invalid:\n  - no closing bracket ["
    
    # Act
    with pytest.raises(ConfigurationError) as exc_info:
        parse_config(invalid_yaml)
    
    # Assert
    error_message = str(exc_info.value)
    assert "line 2" in error_message
    assert "closing bracket" in error_message
```

## 🔗 References

This document consolidates testing requirements from:
- Previous CLAUDE.md testing section
- CONTRIBUTING.md test requirements
- Industry best practices

All other project documents should reference this file for testing standards.

---

**Enforcement**: These standards are enforced through pre-commit hooks, CI/CD pipelines, and code review. Non-compliant code will be automatically rejected.