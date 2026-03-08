# yjd

Your job is done when the code is DRY with the rest of the codebase, no regressions were introduced, the code is clean, readable and not overly verbose/defensive, and most importantly all quality checks pass.

**Validation workflow:**
1. Use **test-runner skill** (ruff → lint → test-all-mocked)
2. If tests fail, use **test-fixer skill** to iterate until passing
3. Continue until all checks pass

**DRY Verification Checklist:**
Before considering your work complete, verify no duplicate functionality exists:
1. For each new function/class, run semantic search: `docker exec arsenal-semantic-search-cli code-search find "description of what it does"`
2. Review search results (score > 0.4 indicates potentially similar code)
3. If similar code exists, reuse/refactor instead of duplicating