# RAG Pipeline Test Suite

Comprehensive test suite for the RAG Pipeline system with unit and integration tests.

## 📁 Structure

```
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_chunker_models.py
│   ├── test_token_counter.py
│   ├── test_embeddings_models.py
│   ├── test_vector_store_models.py
│   └── test_rag_models.py
├── integration/             # Integration tests (end-to-end)
│   ├── test_rag_pipeline_integration.py
│   ├── test_enricher_integration.py
│   └── test_full_system.py
├── fixtures/               # Test data and fixtures
│   ├── sample_docs/
│   └── test_data.json
├── conftest.py            # Shared fixtures and configuration
├── pytest.ini             # Pytest configuration
├── run_tests.py           # Test runner script
└── README.md              # This file
```

## 🚀 Quick Start

### Install Dependencies
```bash
# Install test dependencies
uv add --dev pytest pytest-cov pytest-mock pytest-asyncio

# Or using pip
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

### Run All Tests
```bash
# Using the test runner
python tests/run_tests.py

# Or directly with pytest
pytest tests/

# With coverage
pytest tests/ --cov=.. --cov-report=term-missing
```

### Run Specific Test Types
```bash
# Unit tests only (fast)
python tests/run_tests.py unit

# Integration tests only
python tests/run_tests.py integration

# Skip slow tests
python tests/run_tests.py --quick
```

## 🧪 Test Categories

### Unit Tests
Fast, isolated tests for individual components:
- **Models**: Pydantic model validation
- **Utils**: Utility function testing
- **Components**: Individual class testing with mocks

### Integration Tests
End-to-end tests with real components:
- **Pipeline**: Complete RAG pipeline flow
- **Persistence**: Save/load functionality
- **Performance**: Throughput and latency tests

## 📊 Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| Models | 100% | - |
| Core Logic | 90% | - |
| Integration | 80% | - |
| Overall | 85% | - |

## 🏷️ Test Markers

```python
@pytest.mark.unit          # Fast unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.slow          # Tests > 1 second
@pytest.mark.requires_model # Needs ML models
@pytest.mark.requires_gpu  # Needs GPU
```

### Run Tests by Marker
```bash
# Run only unit tests
pytest -m unit

# Run integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run only model-dependent tests
pytest -m requires_model
```

## 🔧 Configuration

### pytest.ini Settings
- **Minimum coverage**: 80%
- **Test discovery**: `test_*.py` files
- **Default markers**: unit, integration, slow
- **Coverage exclusions**: test files, TRASH directory

### Environment Variables
```bash
# Set test data directory
export TEST_DATA_DIR=/path/to/test/data

# Enable debug output
export TEST_DEBUG=1

# Use GPU for tests
export TEST_USE_GPU=1
```

## 📝 Writing Tests

### Unit Test Example
```python
import pytest
from unittest.mock import Mock

def test_component_behavior():
    """Test specific component behavior."""
    # Arrange
    mock_dep = Mock()
    component = MyComponent(mock_dep)
    
    # Act
    result = component.process("input")
    
    # Assert
    assert result == expected
    mock_dep.method.assert_called_once()
```

### Integration Test Example
```python
@pytest.mark.integration
def test_end_to_end_flow():
    """Test complete system flow."""
    # Setup
    pipeline = RAGPipeline()
    docs = load_test_documents()
    
    # Execute
    pipeline.index_documents(docs)
    results = pipeline.retrieve("query")
    
    # Verify
    assert len(results) > 0
    assert results[0].score > 0.5
```

## 🐛 Debugging Tests

### Verbose Output
```bash
# Maximum verbosity
pytest -vvv tests/

# Show print statements
pytest -s tests/

# Show local variables on failure
pytest -l tests/
```

### Run Specific Test
```bash
# Run single test file
pytest tests/unit/test_chunker_models.py

# Run single test class
pytest tests/unit/test_chunker_models.py::TestChunkType

# Run single test method
pytest tests/unit/test_chunker_models.py::TestChunkType::test_chunk_types
```

### Debug with pdb
```python
def test_something():
    import pdb; pdb.set_trace()  # Debugger breakpoint
    # Test code here
```

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install uv
      - run: uv sync
      - run: uv run pytest tests/ --cov
```

## 📈 Metrics

### Test Execution Time
- Unit tests: < 5 seconds
- Integration tests: < 30 seconds
- Full suite: < 1 minute

### Coverage Requirements
- New code: 90% minimum
- Modified code: 85% minimum
- Overall: 80% minimum

## 🤝 Contributing

### Adding New Tests
1. Create test file in appropriate directory (unit/ or integration/)
2. Follow naming convention: `test_<component>.py`
3. Use appropriate markers (@pytest.mark.unit, etc.)
4. Include docstrings for test purpose
5. Ensure tests are independent and reproducible

### Test Review Checklist
- [ ] Tests pass locally
- [ ] Coverage meets requirements
- [ ] No hardcoded paths or data
- [ ] Proper use of fixtures
- [ ] Clear test names and docstrings
- [ ] Appropriate markers used

## 🆘 Troubleshooting

### Common Issues

**ImportError**: Add parent directory to path
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Fixture not found**: Check conftest.py is in test directory

**Slow tests**: Use `@pytest.mark.slow` and skip with `-m "not slow"`

**Model download**: Mock model loading for unit tests

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Pytest Mock](https://pytest-mock.readthedocs.io/)
- [Testing Best Practices](https://testdriven.io/blog/pytest-best-practices/)