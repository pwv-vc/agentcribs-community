# Langfuse Prompt Iterator - Comprehensive Workflow

Complete test-driven prompt iteration workflow with reproducible test cases and feedback loops.

## Quick Start

### 1. Setup a test case

**From existing trace:**
```bash
cd .claude/skills/langfuse-prompt-iterator
uv run python setup_test_case.py PROMPT_NAME --from-trace TRACE_ID
```

**From scratch:**
```bash
uv run python setup_test_case.py PROMPT_NAME
# Then edit the generated test case file
```

### 2. Run baseline test

```bash
uv run python test_prompt.py PROMPT_NAME path/to/test_case.json --baseline
```

### 3. Iterate on the prompt

Edit the prompt file in `docs/cached_prompts/PROMPT_NAME_production.txt`

### 4. Push updated version

```bash
cd .claude/skills/update-langfuse-staging-server-prompt
uv run python push_to_staging.py PROMPT_NAME
```

### 5. Test new version

```bash
cd .claude/skills/langfuse-prompt-iterator
uv run python test_prompt.py PROMPT_NAME path/to/test_case.json --version NEW_VERSION
```

### 6. Compare results

```bash
uv run python compare_outputs.py result1.json result2.json
```

## Advanced Usage

### Bulk Testing

Run same test multiple times:
```bash
uv run python bulk_test_runner.py PROMPT_NAME test_case.json --runs 5
```

Run multiple test cases:
```bash
uv run python bulk_test_runner.py PROMPT_NAME test_cases/*.json
```

### Compare Traces Directly

```bash
uv run python compare_outputs.py --trace-ids TRACE_1 TRACE_2
```

## Workflow Overview

1. **Setup** - Establish environment, identify prompt version
2. **Baseline** - Create reproducible test case, run initial test
3. **Iterate** - Review output, suggest changes, implement, re-test
4. **Compare** - Side-by-side analysis of outputs
5. **Bulk Test** - Validate consistency across multiple runs

## Environment Setup

Required in `arsenal/.env`:
```bash
LANGFUSE_PUBLIC_KEY_STAGING=pk-lf-...  # pragma: allowlist-secret
LANGFUSE_SECRET_KEY_STAGING=sk-lf-...  # pragma: allowlist-secret
LANGFUSE_HOST_STAGING=https://langfuse.staging.cncorp.io
OPENAI_API_KEY=sk-...  # pragma: allowlist-secret
```

## File Structure

```
.claude/skills/langfuse-prompt-iterator/
├── SKILL.md                  # Main skill definition (for Claude)
├── README.md                 # This file (for humans)
├── setup_test_case.py        # Create test cases
├── test_prompt.py            # Execute single test
├── bulk_test_runner.py       # Run multiple tests
├── compare_outputs.py        # Compare two results
├── env_loader.py             # Environment loading
└── pyproject.toml            # Dependencies
```

## Generated Files

Test cases:
- `docs/prompt_test_cases/test_case_*.json`

Test results:
- `docs/prompt_test_results/test_case_*_baseline_*.json`
- `docs/prompt_test_results/test_case_*_v*_*.json`
- `docs/prompt_test_results/bulk_results_*.json`
- `docs/prompt_test_results/bulk_results_*.md`

Comparisons:
- `docs/prompt_comparisons/comparison_*.md`

## Tips

- **Always establish baseline first** - You need a reference point
- **One change at a time** - Easier to understand what helped
- **Save test cases** - They're reusable for regression testing
- **Version control everything** - Track prompt changes in git
- **Use bulk tests before production** - Check consistency

## Integration with Other Skills

This skill works alongside:
- **langfuse-prompt-viewer** - For fetching and viewing prompts (read-only)
- **update-langfuse-staging-server-prompt** - For pushing changes (write)

The iterator orchestrates the full workflow using both skills.
