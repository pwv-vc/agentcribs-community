# samreview

Review code changes with Sam's perspective. Suggest improvements but don't make them.

Usage: `/samreview pr` or `/samreview commit`

## Instructions

### Step 1: Create diff based on mode

**If argument is "pr":**
1. Get the current branch name: `git branch --show-current`
2. Determine the merge base branch (usually `main` or `origin/main`)
3. Run `git diff <merge-base>...<current-branch> > pr.diff` to create PR-style diff
   - Example: `git diff origin/main...feature-branch > pr.diff`
   - This shows all changes in the current branch compared to where it diverged
4. Run `ls` to confirm the file was created
5. Read `./pr.diff` to review all changes

**If argument is "commit":**
1. Run `git diff HEAD > commit.diff` to create diff of staged + unstaged changes
2. Run `ls` to confirm the file was created
3. Read `./commit.diff` to review all changes

**If no argument provided:**
- Default to "pr" mode

### Step 2: Analyze and report on changes

Evaluate the code on ALL of these criteria in priority order and provide specific feedback for each:

1. **LOC (Lines of Code)**:
   - Are they concise/elegant or overly verbose?
   - Clean & readable without extra unnecessary code?
   - We prefer "cutting corners" to simplify code and align user experiences
   - OK to interpret spec in a way that simplifies implementation and code
   - **Report**: Identify any verbose sections, suggest simplifications

2. **DRY (Don't Repeat Yourself)**:
   - Are the changes DRY with the rest of the codebase?
   - Do they reuse existing functions/patterns?
   - **REQUIRED**: For each new function/class, run semantic search to find similar implementations:
     - `docker exec arsenal-semantic-search-cli code-search find "what this does"`
     - Check results with similarity score > 0.4
   - **Report**:
     - List semantic search queries you ran
     - Show any similar code found (with scores)
     - Point out any duplication and suggest what to reuse

3. **Non-defensive coding**:
   - Avoid patterns like try/except
   - Don't catch edge cases that never actually happen in the logic
   - **Report**: Flag any unnecessary defensive code

4. **Regressions**:
   - Do they introduce regressions?
   - How do they change the business logic?
   - **Report**: Identify potential breaking changes or logic issues

5. **SPEC alignment**:
   - Are they aligned with the SPEC? (check @CURRENT_SPEC.md if it exists)
   - **Report**: Note any deviations from spec

6. **Test alignment**:
   - Are tests aligned with docs/TEST_PATTERNS.md and ./tests/README.md?
   - **Report**: Identify test pattern violations

### Step 3: Provide review report

Structure your review as:

```
# Code Review

## 1. LOC Quality
[Your evaluation and suggestions]

## 2. DRY Analysis
[Your evaluation and suggestions]

## 3. Defensive Coding Check
[Your evaluation and suggestions]

## 4. Regression Analysis
[Your evaluation and suggestions]

## 5. SPEC Alignment
[Your evaluation and suggestions]

## 6. Test Pattern Alignment
[Your evaluation and suggestions]

## Critical Improvements Required
[List only the most important changes, prioritized]

## Optional Suggestions
[Nice-to-have improvements]
```

Remember: This code comes from an inexperienced dev. Be thorough but constructive.

### Step 4: Clean up

After providing the review, remove the diff artifact:
- If you created `pr.diff`, run `rm pr.diff`
- If you created `commit.diff`, run `rm commit.diff`

This prevents diff artifacts from accumulating and being included in future reviews.

## Arguments

$ARGUMENTS
