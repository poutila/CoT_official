# Chain-of-Thought Test Suite

## Overview

This test suite provides validation examples for Chain-of-Thought reasoning traces. Each test case includes:
- Input reasoning trace (Markdown)
- Expected validation result (JSON)
- Test metadata

## Test Categories

1. **Valid Traces** - Should pass validation
   - `001_basic_reasoning.md` - Standard reasoning with all required fields
   - `002_recursive_reasoning.md` - Recursive prompt generation within limits
   - `003_token_limit_fallback.md` - Token limit approached with fallback

2. **Invalid Traces** - Should fail with specific errors
   - `001_missing_timestamp.md` - Missing required timestamp fields
   - `002_recursion_limit_exceeded.md` - Recursion depth exceeds maximum

3. **Edge Cases** - Boundary conditions and special scenarios
   - `001_large_trace.md` - Large trace with 15 evidence items
   - `002_legacy_format.md` - Legacy format requiring conversion

4. **Version Compatibility** - Multi-version support tests (planned)

## Running Tests

```bash
# Run all tests
cot-validate --test-suite ./test_suite/

# Run specific category
cot-validate --test-suite ./test_suite/valid/

# Run single test
cot-validate --trace ./test_suite/valid/001_basic_reasoning.md --expect-pass
```

## Test Case Format

Each test case consists of two files:
- `XXX_description.md` - The reasoning trace
- `XXX_description.json` - Expected validation result

## Test Results

Results are categorized as:
- ✅ **PASS** - Validation succeeded as expected
- ❌ **FAIL** - Validation failed when it should pass
- ⚠️ **UNEXPECTED** - Different error than expected