# Single-Use Function Detection

## Overview

The `check_llm_nits.py` script now detects newly added private functions that are only used once in the codebase.

## How It Works

### Detection Logic

1. **Scans Git Diff**: Analyzes both staged (`git diff --staged`) and unstaged (`git diff HEAD`) changes
2. **Finds New Functions**: Identifies new function definitions matching `+def _function_name(`
3. **Counts Usages**: Searches the entire codebase for calls to each function using ripgrep/grep
4. **Flags Single-Use**: Reports functions where usage_count == 1 (only the definition exists)

### Scope

- **Only checks private functions** (starting with `_`, but not `__`)
  - Public functions might be part of an API or intended for future use
  - Dunder methods (`__init__`, `__str__`, etc.) are excluded

- **Analyzes full codebase usage**
  - Not just the changed file
  - Counts all occurrences of `function_name(`

### Example Output

```
======================================================================
SINGLE-USE FUNCTION ISSUES:
======================================================================
Functions that are only called once should be inlined.
Add '# noqa: SINGLE001' to the function def line if this is intentional.

api/src/cronjobs/processors.py: Function '_get_phone_for_conversation' is only used 1 time(s)
  → Consider inlining this function at its call site
```

## Bypassing the Check

If a single-use function is intentional (e.g., improving readability for complex logic), add a noqa comment:

```python
def _complex_validation_logic(data):  # noqa: SINGLE001
    """
    Intentionally separated for readability despite single use.
    This 50-line validation would clutter the main function.
    """
    # ... complex logic ...
```

## Why This Matters

From `CLAUDE.md`:
> **Avoid single-use functions**: Don't create functions that are only called once. Inline the code instead unless it will be reused elsewhere.

### Benefits of Inlining

1. **Reduces indirection**: Code is easier to follow when logic isn't scattered
2. **Eliminates dead abstractions**: No functions that exist "just in case"
3. **Improves discoverability**: All relevant code is in one place
4. **Simplifies testing**: Fewer functions means fewer test targets

### When Functions Are Justified

- Used 2+ times (actual reuse)
- Part of a public API
- Separates genuinely complex logic (50+ lines)
- Required for testing/mocking purposes

## Integration

The check runs automatically as part of:
- `just lint-and-fix` (via `lint-extras` target)
- Pre-commit hooks (manual stage)
- CI/CD pipelines

## Technical Details

### Search Strategy

1. Tries `ripgrep` first (faster, respects .gitignore)
2. Falls back to `grep` if ripgrep unavailable
3. Searches for pattern: `\bfunction_name\s*\(`
   - Matches: `function_name(`, `self.function_name(`, `obj.function_name(`
   - Word boundary prevents false matches (e.g., `other_function_name`)

### Performance

- Negligible overhead (~1-2 seconds)
- Only runs on new functions in current diff
- Caches not required (searches are fast with ripgrep)

## Testing

To test the detection:

```bash
# 1. Add a single-use function
cat >> api/src/test_module.py << 'EOF'
def _single_use_helper(x):
    return x * 2

def caller():
    return _single_use_helper(5)
EOF

# 2. Run the checker
UV_PROJECT_ENVIRONMENT=.uv/api uv run python .pre-commit-scripts/check_llm_nits.py

# 3. Expected output: SINGLE-USE FUNCTION ISSUES for _single_use_helper

# 4. Clean up
git restore api/src/test_module.py
```

## Limitations

1. **Static analysis only**: Doesn't understand dynamic calls (e.g., `getattr(obj, 'func_name')()`)
2. **Name-based matching**: Could have false positives if multiple functions share a name
3. **No cross-repo detection**: Only searches within checked directories
4. **New functions only**: Doesn't detect existing single-use functions (would be too noisy)

## Future Enhancements

Potential improvements:
- AST-based analysis for more accurate call detection
- Check for unused functions (0 usages)
- Suggest specific inlining locations
- Detect "wrapper functions" that just call another function
