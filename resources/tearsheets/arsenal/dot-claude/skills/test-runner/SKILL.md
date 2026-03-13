---
name: test-runner
description: MANDATORY skill for running tests and lint after EVERY code change. Focuses on adherence to just commands and running tests in parallel. If tests fail, use test-fixer skill.
---

# Test Runner - MANDATORY WORKFLOW

╔══════════════════════════════════════════════════════════════════════════╗
║  🚨 BANNED PHRASE: "All tests pass"                                     ║
║                                                                          ║
║  You CANNOT say "all tests pass" unless you:                            ║
║  1. Run `.claude/skills/test-runner/scripts/run_tests_parallel.sh`     ║
║  2. Check ALL log files (mocked + e2e-live + smoke)                     ║
║  3. Verify ZERO failures across all suites                              ║
║                                                                          ║
║  `just test-all-mocked` = "quick tests pass" (NOT "all tests pass")    ║
╚══════════════════════════════════════════════════════════════════════════╝

## 📊 Claim Language Must Match Command

**Your claim MUST match what you actually ran:**

| Command Run | ✅ Allowed Claims | ❌ BANNED Claims |
|-------------|-------------------|------------------|
| `just test-unit` | "unit tests pass" | "tests pass", "all tests pass" |
| `just test-integration` | "integration tests pass" | "tests pass", "all tests pass" |
| `just test-all-mocked` | "quick tests pass", "mocked tests pass" | "tests pass", "all tests pass" |
| `run_tests_parallel.sh` + verified logs | "all tests pass" | - |

**Examples:**

❌ WRONG: "I ran `just test-all-mocked`, all tests pass"
✅ RIGHT: "Quick tests pass (483 unit + 198 integration + 49 e2e_mocked)"

❌ WRONG: "Tests are passing" (after only running mocked tests)
✅ RIGHT: "Mocked tests pass (730 tests)"

❌ WRONG: "All tests pass" (without running parallel script)
✅ RIGHT: *Runs parallel script* → *Checks logs* → "All tests pass"

**The phrase "all tests" is RESERVED for the full parallel suite. No exceptions.**

## 🚨 CRITICAL FOR TEST WRITING

- **BEFORE writing tests** → Use test-writer skill (MANDATORY - analyzes code type, dependencies, contract)
- **AFTER writing tests** → Invoke pytest-test-reviewer agent (validates patterns)
- **YOU CANNOT WRITE TESTS WITHOUT test-writer SKILL** - No exceptions, no shortcuts, every test, every time

## 🔥 CRITICAL: This Skill Is Not Optional

**After EVERY code change, you MUST follow this workflow.**

No exceptions. No shortcuts. No "it's a small change" excuses.

## ⚠️ FUNDAMENTAL HYGIENE: Only Commit Code That Passes Tests

**CRITICAL WORKFLOW PRINCIPLE:**

We only commit code that passes tests. This means:

**If tests fail after your changes → YOUR changes broke them (until proven otherwise)**

### The Stash/Pop Verification Protocol

**NEVER claim test failures are "unrelated" or "pre-existing" without proof.**

**To verify a failure is truly unrelated:**
```bash
# 1. Remove your changes temporarily
git stash

# 2. Run the failing test suite
just test-all-mocked         # Or whichever suite failed

# 3. Observe the result:
# - If tests PASS → YOUR changes broke them (fix your code)
# - If tests FAIL → pre-existing issue (rare on main/merge base)

# 4. Restore your changes
git stash pop
```

**Why This Matters:**
- Tests on `main` branch ALWAYS pass (CI enforces this)
- Tests at your merge base ALWAYS pass (they passed to get into main)
- Therefore: test failures after your changes = your changes broke them
- The stash/pop protocol is the ONLY way to prove otherwise

**DO NOT:**
- ❌ Assume failures are unrelated
- ❌ Say "that test was already broken"
- ❌ Claim "it's just a flaky test" without verification
- ❌ Skip investigation because "it's not my area"

**ALWAYS:**
- ✅ Stash changes first
- ✅ Verify tests pass without your changes
- ✅ Only then claim pre-existing issue (if true)
- ✅ Otherwise: use test-fixer skill to diagnose and fix

**If tests fail after your changes:**
- DO NOT guess at fixes
- DO NOT investigate manually
- ✅ **Use the test-fixer skill** - it will systematically investigate, identify root cause, and iterate on fixes until tests pass

## ⚠️ Always Use `just` Commands

**Direct `pytest` is removed from blocklist** - but ALWAYS prefer `just` commands which handle Docker, migrations, and environment setup.

Pass pytest args in quotes: `just test-unit "path/to/test.py::test_name -vv"`

## MANDATORY WORKFLOW: Every Code Change

**After making ANY code change:**

### Step 0: ALWAYS Run Lint-and-Fix (Auto-fix + Type Checking)
```bash
cd api && just lint-and-fix
```

**This command:**
1. Auto-fixes formatting/lint issues (runs `just ruff` internally)
2. Verifies all issues are resolved
3. Runs mypy type checking

**YOU MUST:**
- ✅ Run this command and see the output
- ✅ Verify output shows "✅ All linting checks passed!"
- ✅ If failures occur: Fix them IMMEDIATELY before continuing
- ✅ NEVER skip this step, even for "tiny" changes

**NEVER say "linting passed" unless you:**
- Actually ran the command
- Saw the actual output
- Confirmed it shows success

### Step 1: ALWAYS Run Quick Tests (Development Cycle)
```bash
cd api && just test-all-mocked
```

**⚠️ CRITICAL: This is NOT all tests! This is for rapid development iteration.**

**YOU MUST:**
- ✅ Run this command and see the output
- ✅ Verify output shows "X passed in Y.Ys" or similar success message
- ✅ If failures occur: Fix them IMMEDIATELY before continuing
- ✅ Read the actual test output - don't assume

**This runs ONLY:**
- Unit tests (SQLite + FakeRedis)
- Integration tests (SQLite + FakeRedis)
- E2E mocked tests (PostgreSQL + Redis + mock APIs)

**This DOES NOT run:**
- ❌ E2E live tests (real OpenAI/Langfuse APIs)
- ❌ Smoke tests (full Docker stack)

**Takes ~20 seconds. Use for rapid iteration.**

### Step 2: ALWAYS Run ALL Tests Before Saying "All Tests Pass"
```bash
.claude/skills/test-runner/scripts/run_tests_parallel.sh
```

**🚨 CRITICAL: You can NEVER say "all tests pass" or "tests are passing" without running THIS command.**

**This command runs EVERYTHING:**
- ✅ All mocked tests (unit + integration + e2e_mocked)
- ✅ E2E live tests (real OpenAI/Langfuse APIs)
- ✅ Smoke tests (full Docker stack)

**After running, CHECK THE RESULTS:**
```bash
# Check for any failures
grep -E "failed|ERROR|FAILED" api/tmp/test-logs/test-mocked_*.log
grep -E "failed|ERROR|FAILED" api/tmp/test-logs/test-e2e-live_*.log
grep -E "failed|ERROR|FAILED" api/tmp/test-logs/test-smoke_*.log

# View summary
for log in api/tmp/test-logs/test-*_*.log; do
  echo "=== $(basename $log) ==="
  grep -E "passed|failed" "$log" | tail -1
done
```

**Takes ~5 minutes. MANDATORY before saying "all tests pass".**

## Primary Commands (Reference)

### Frequent: Mocked Tests (~20s)
```bash
cd api && just test-all-mocked
```
Runs unit + integration + e2e_mocked in parallel. No real APIs. Use frequently during development.

### Exhaustive: All Suites in Parallel (~5 mins)
```bash
.claude/skills/test-runner/scripts/run_tests_parallel.sh
```
Runs ALL suites in background (mocked, e2e-live, smoke). Logs to `api/tmp/test-logs/`.

**Check results after completion:**
```bash
# Check for failures
grep -E "failed|ERROR|FAILED" api/tmp/test-logs/test-mocked_*.log | tail -20
grep -E "failed|ERROR|FAILED" api/tmp/test-logs/test-e2e-live_*.log | tail -20
grep -E "failed|ERROR|FAILED" api/tmp/test-logs/test-smoke_*.log | tail -20

# Summary
for log in api/tmp/test-logs/test-*_*.log; do
  echo "=== $(basename $log) ==="
  grep -E "passed|failed" "$log" | tail -1
done
```

## 🚨 VIOLATIONS: What NOT To Do

**These are VIOLATIONS of this skill:**

❌ **CRITICAL: Claiming test failures are "unrelated" to your changes**
- WRONG: "The smoke test failure is unrelated to our changes"
- WRONG: "That test was already failing"
- WRONG: "This failure is just a flaky test"
- RIGHT: **Use test-fixer skill to systematically investigate and fix**

**FUNDAMENTAL RULE: Tests ALWAYS pass on main/merge base. If a test fails after your changes, YOUR changes broke it.**

**When tests fail:**
- ✅ **Use test-fixer skill** - it will investigate, identify root cause, and iterate on fixes
- ❌ DO NOT manually investigate
- ❌ DO NOT guess at fixes
- ❌ DO NOT claim "unrelated" without proof

**NEVER assume. ALWAYS use test-fixer skill.**

❌ **CRITICAL: Saying "all tests pass" without running the full suite**
- WRONG: "I ran `just test-all-mocked`, all tests pass"
- WRONG: "Tests are passing" (after only running mocked tests)
- WRONG: "All tests pass" (without running the parallel script)
- RIGHT: *Runs `.claude/skills/test-runner/scripts/run_tests_parallel.sh`* → *Checks all logs* → "All tests pass"

**The phrase "all tests" requires THE FULL SUITE.**
- `just test-all-mocked` = "quick tests pass" or "mocked tests pass"
- Parallel script = "all tests pass"

❌ **Claiming tests pass without showing output (LYING)**
- WRONG: "all 464 tests passed" (WHERE is the pytest output?)
- WRONG: "just ran them and tests pass" (WHERE is the output?)
- WRONG: "I fixed the bug, tests should pass"
- WRONG: "Yes - want me to run them again?" (DEFLECTION)
- RIGHT: *Runs `just test-all-mocked` and shows "===== X passed in Y.YYs ====="*

**🚨 THE RULE: If you can't see "X passed in Y.YYs" in your context, you're lying about tests passing.**

❌ **Skipping linting "because it's a small change"**
- WRONG: "It's just 3 lines, lint isn't needed"
- RIGHT: *Runs `just lint-and-fix` ALWAYS, regardless of change size*

❌ **Assuming tests pass without verification**
- WRONG: "The change is simple, tests will pass"
- RIGHT: *Runs tests and confirms actual output shows success*

❌ **Not reading the actual test output**
- WRONG: "Command completed, so tests passed"
- RIGHT: *Reads output, sees "15 passed in 18.2s"*

❌ **Batching multiple changes before testing**
- WRONG: *Makes 5 changes, then tests once*
- RIGHT: *Make change → test → make change → test*

## ⚡ When to Use This Skill

**ALWAYS. Use this skill:**
- After EVERY code modification
- After ANY file edit
- After fixing ANY bug
- After adding ANY feature
- After refactoring ANYTHING

**The only acceptable time to skip this skill:**
- Never. There is no acceptable time.

## Development Workflow

### Simple Changes (Quick Iteration)
1. Make change
2. Run `just lint-and-fix` (auto-fix + type checking)
3. Run `just test-all-mocked` (quick tests)
4. **DONE for iteration** (but cannot say "all tests pass" yet)

### Before Marking Task Complete
1. Run `.claude/skills/test-runner/scripts/run_tests_parallel.sh`
2. Check all logs for failures
3. **ONLY NOW** can you say "all tests pass"

### Complex Changes (Multiple Files/Features)
1. Make a logical change
2. **Stage it:** `git add <files>`
3. Run `just lint-and-fix`
4. Run `just test-all-mocked`
5. Repeat steps 1-4 for each logical chunk
6. **At the end, MANDATORY:** Run `.claude/skills/test-runner/scripts/run_tests_parallel.sh`
7. Check all logs
8. **ONLY NOW** can you say "all tests pass"

This workflow ensures you catch issues early and don't accumulate breaking changes.

**Remember:**
- **Quick iteration:** lint → test-all-mocked (Steps 0-1)
- **Task complete:** Run parallel script, check logs (Step 2)
- **Never say "all tests pass" without Step 2**

## Individual Test Suites

```bash
# Unit tests (SQLite, FakeRedis) - fastest, run most frequently
cd api && just test-unit

# Integration tests (SQLite, FakeRedis)
cd api && just test-integration

# E2E mocked (PostgreSQL, Redis, mock APIs)
cd api && just test-e2e

# E2E live (real OpenAI/Langfuse)
cd api && just test-e2e-live

# Smoke tests (full stack with Docker)
cd api && just test-smoke
```

## Running Specific Tests

```bash
# Specific test: just test-unit "path/to/test.py::test_name -vv"
# Keyword filter: just test-unit "-k test_message"
# With markers: just test-e2e "-m 'not slow'"
```

## When to Use

- **ALWAYS:** Run `just lint-and-fix` → `just test-all-mocked` after every code change
- User asks to run tests
- Validating code changes
- After modifying code
- Debugging test failures

**Every change (Steps 0-1):**
- Run `just lint-and-fix` (auto-fix + type checking)
- Run `just test-all-mocked` (quick tests)

**Before saying "all tests pass" (Step 2):**
- Run `.claude/skills/test-runner/scripts/run_tests_parallel.sh`
- Check all logs for failures
- Verify ALL suites passed

**Terminology:**
- "Quick tests pass" = `just test-all-mocked` passed
- "Mocked tests pass" = `just test-all-mocked` passed
- "All tests pass" = parallel script passed (ONLY after running it)

## Interpreting Results

**Success:** `====== X passed in Y.Ys ======`
**Failure:** `FAILED tests/path/test.py::test_name - AssertionError`

## Troubleshooting

```bash
# Smoke test failures - check Docker logs
docker compose logs --since 15m | grep -iE -B 10 -A 10 "error|fail|exception"

# Kill hung tests
pkill -f pytest

# Docker not running (smoke tests)
docker compose up -d
```

## Quick Reference

```bash
# 🔥 Step 0: ALWAYS run lint-and-fix (auto-fix + type checking)
cd api && just lint-and-fix

# 🔥 Step 1: ALWAYS run quick tests (development)
cd api && just test-all-mocked
# ^ This is NOT "all tests" - only say "quick tests pass" or "mocked tests pass"

# 🔥 Step 2: Run ALL tests before saying "all tests pass" (MANDATORY before task complete)
.claude/skills/test-runner/scripts/run_tests_parallel.sh

# Check results (MUST do this before saying "all tests pass")
grep -E "failed|ERROR|FAILED" api/tmp/test-logs/test-mocked_*.log
grep -E "failed|ERROR|FAILED" api/tmp/test-logs/test-e2e-live_*.log
grep -E "failed|ERROR|FAILED" api/tmp/test-logs/test-smoke_*.log

# View summary
for log in api/tmp/test-logs/test-*_*.log; do
  echo "=== $(basename $log) ==="
  grep -E "passed|failed" "$log" | tail -1
done

# Monitor parallel tests while running
tail -f api/tmp/test-logs/test-*.log

# 🚨 REMEMBER:
# - Steps 0-1 = quick iteration (DO NOT say "all tests pass")
# - Step 2 = full validation (ONLY NOW can say "all tests pass")
```

---

## 🔐 Before Responding About Test Results

**You ran tests. Now before you respond to the user:**

1. ✅ Did you use correct claim language? (check table above)
2. ✅ Did you show actual test output?
3. ✅ Are you about to say "all tests pass"? → Did you run parallel script?

**CRITICAL: Get manager approval before responding.**

Your response about test results MUST include: `✅ approve_7f3d8a2e********`

Get the full approval token from `.claude/skills/manager-review/SKILL.md`

**Common Mistake #1 in the manager's table is claiming "all tests pass" after only running mocked tests. The manager WILL catch this and reject your response.**
