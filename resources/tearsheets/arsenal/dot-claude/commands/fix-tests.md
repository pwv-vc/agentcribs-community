---
description: Run test-fixer skill to systematically fix all failing tests (project)
---

# Fix Tests Command

**Purpose:** Invoke the test-fixer skill to systematically investigate and fix all failing tests until the test suite passes.

**Workflow:** Run AFTER code changes (like `/spec-to-pr`) to ensure tests pass before PR review.

## Usage

```bash
# Fix tests in current directory
/fix-tests

# Fix specific test suite
/fix-tests --suite unit

# Fix with verbose output
/fix-tests --verbose
```

## Workflow

**🚨 CRITICAL: Work completely autonomously. DO NOT ask questions. DO NOT explain the workflow. Just execute it.**

### Step 1: Run Tests to Identify Failures

Execute test suite to find failures:

```bash
cd api && just test-all-mocked
```

If all tests pass:
- Report success and exit
- No fixes needed

If tests fail:
- Capture error output
- Proceed to Step 2

### Step 2: Invoke test-fixer Skill

**Execute immediately (DO NOT ASK):**

Use the test-fixer skill to systematically fix failures:

```
I'm using the test-fixer skill to systematically fix all test failures...
```

The test-fixer skill will:
1. Create git diff backup (never lose code)
2. Investigate where tests pass (current / branch HEAD / main)
3. Identify root cause of failures
4. Write targeted fixes
5. Iterate: fix → verify → repeat (up to 10 approaches)
6. Return code to passing state

### Step 3: Verify All Tests Pass

After test-fixer completes:

```bash
cd api && just test-all-mocked
```

If tests still fail:
- Report remaining failures
- Suggest manual intervention needed

If tests pass:
- Report success
- Proceed to Step 4

### Step 4: Output Summary

```
✅ All tests passing

🔧 Fixes applied:
- {Fix 1 description}
- {Fix 2 description}

📊 Test results:
- Unit tests: ✓ PASS
- Integration tests: ✓ PASS
- E2E tests: ✓ PASS

💾 Code changes preserved in git diff backup

Next step: Review PR and merge when ready
```

## Example Usage

### Example: Fixing Tests After PR Generation

```bash
$ /fix-tests

Running test suite to identify failures...
$ cd api && just test-all-mocked

❌ Found 3 failing tests:
  - test_format_phone_number: AssertionError
  - test_validate_timezone: KeyError
  - test_send_message: AttributeError

Using test-fixer skill to systematically fix failures...

[Test-Fixer Investigation Phase]
✓ Tests pass on main branch
✓ Tests fail on current branch
✓ Root cause: Recent changes to phone formatting

[Test-Fixer Fix Iteration 1]
Approach: Update test expectations to match new phone format
$ cd api && just test-all-mocked
Result: 2 tests pass, 1 still failing

[Test-Fixer Fix Iteration 2]
Approach: Fix timezone validation to handle None values
$ cd api && just test-all-mocked
Result: All tests pass ✓

✅ All tests passing

🔧 Fixes applied:
- Updated phone format tests to expect stripped +1 prefix
- Added None handling to timezone validation

📊 Test results:
- Unit tests: ✓ PASS (123 tests)
- Integration tests: ✓ PASS (45 tests)
- E2E tests: ✓ PASS (12 tests)

💾 Code changes preserved in git diff backup

Next step: Review PR and merge when ready
```

## Notes

- **Autonomous execution**: No user interaction required
- **Systematic approach**: test-fixer uses git to isolate issues
- **Up to 10 fix attempts**: Tries different approaches until tests pass
- **Safe**: Always creates git diff backup before modifying code
- **Read-only on success**: If tests pass initially, no changes made
- **For cron jobs**: Use with `--dangerously-skip-permissions` flag

## Skills Used

1. **test-fixer** - Systematically investigate and fix test failures
2. **test-runner** - Verify tests pass after fixes applied

## When to Use

- **After /spec-to-pr**: Ensure generated PRs have passing tests
- **After merges**: Fix any test conflicts from main branch
- **CI failures**: Investigate and fix broken tests automatically
- **Before review**: Clean up test suite before requesting PR review
