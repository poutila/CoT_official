# Test Case: Trace Degraded Summary

## Test Metadata
- **Test ID**: 003_trace_degraded_summary
- **Category**: Edge Cases
- **Description**: Tests compression Level 2 (Semantic Compression) when approaching token limits
- **Expected Behavior**: Trace should degrade gracefully to summary format

---

## 🧠 Reasoning Trace (Chain-of-Thought) - COMPRESSED

```yaml
schema: chain_of_thought/v7.0.0
validation: required
runtime_contract: 2.0.0
compression_level: 2
original_size: 4523
compressed_size: 487
compression_ratio: 0.89
fallback_strategy: semantic_compress
token_usage: 3850
token_limit: 4000
```

**Context Level**: Full File Access [DEGRADED TO SUMMARY]
**Compression Applied**: Level 2 - Semantic Compression

### Compressed Decision Record

```
DECISION[refactor_large_module] RISK[high] EVIDENCE[5] CONFIDENCE[0.92]
RATIONALE[srp_violation+cyclomatic_complexity+test_coverage_low]
AFFECTED[user_auth.py,session_manager.py,token_handler.py]
ACTION[split_into_three_modules] REVERSIBLE[moderate_effort]
TRACE_HASH[sha256:a7b9c2d4e5f6789012345678901234567890abcdef123456]
```

### Summary Evidence Chain
1. `auth_module.py:1523` → "class exceeds 1000 lines" → SRP violation
2. `metrics_report.md:45` → "complexity score: 47" → High complexity
3. `test_coverage.xml:112` → "coverage: 42%" → Below threshold
4. `architecture_review.md:89` → "split recommended" → Expert opinion
5. `performance_log.json:234` → "response time: 1.2s" → Performance impact

### Compressed Analysis
PRIMARY[module_too_large] ALTERNATIVE[refactor_in_place] 
REJECTED[does_not_address_root_cause] IMPACT[3_modules_affected]
VALIDATION[all_checks_passed] CONFIDENCE[high]

### Decompression Instructions
Full trace available at: `traces/full/refactor_large_module_20240126_143022.md`
Retrieve via: `cot-validate --decompress sha256:a7b9c2d4e5f6789012345678901234567890abcdef123456`

### Compression Metadata
- **Compression Trigger**: Token usage exceeded 80% of limit
- **Information Loss**: Detailed quotes, intermediate reasoning steps
- **Preserved Elements**: Decision, risk level, evidence count, action
- **Semantic Integrity**: Core reasoning chain maintained
- **Validation Status**: Passes compressed trace validation

---

## Validation Notes

This trace demonstrates proper degradation when approaching token limits:

1. **Automatic Trigger**: At 3850/4000 tokens (96%), compression activated
2. **Semantic Preservation**: Key decision elements retained
3. **Hash Reference**: Full trace can be retrieved using hash
4. **Structured Format**: Machine-parseable compressed format
5. **Compliance**: Still validates against v7.0.0 schema in compressed mode

### Expected Validation Results
```json
{
  "valid": true,
  "compression_applied": true,
  "compression_level": 2,
  "information_completeness": 0.75,
  "decision_preserved": true,
  "evidence_preserved": true,
  "action_preserved": true,
  "decompression_available": true
}
```