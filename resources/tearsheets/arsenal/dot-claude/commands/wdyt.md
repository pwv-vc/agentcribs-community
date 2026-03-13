# wdyt

Review the current commit changes for quality and make critical improvements.

## Instructions

1. Run `git diff HEAD > ./commit.diff` to save current changes
2. Run `ls` to confirm the file was created
3. Read `./commit.diff` to review the changes

Then analyze in priority order:

1. **LOC (Lines of Code)**:
   - Are they concise/elegant or overly verbose?
   - Clean & readable without extra unnecessary code?
   - We prefer "cutting corners" to simplify code and align user experiences
   - OK to interpret spec in a way that simplifies implementation

2. **DRY**: Are the changes DRY with the rest of the codebase? Reuse existing functions?
   - For each new function/class, run: `docker exec arsenal-semantic-search-cli code-search find "what it does"`
   - Check for similar code (score > 0.4)

3. **Non-defensive**:
   - Avoid patterns like try/except
   - Don't catch edge cases that never actually happen in the logic

4. **Regressions**: Do they introduce regressions? How do they change the business logic?

5. **SPEC alignment**: Are they aligned with the SPEC? (@CURRENT_SPEC.md)

6. **Test alignment**: Are tests aligned with docs/TEST_PATTERNS.md and ./tests/README.md?

This diff comes from an inexperienced dev. Please make any critical improvements.