---
name: getting-started
description: Bootstrap skill - READ THIS FIRST in every session. Teaches skill discovery and mandatory usage.
bootstrap_token: e28604705b8e2934
---

# Getting Started with Arsenal

> **Editing this file?** Keep it concise. This file teaches *when* to use skills, not *how*.
> The "how" belongs in each skill's SKILL.md. If you're adding details about how to do something,
> put them in the relevant skill and just add a trigger here that routes to it.

## 🔥 Four Foundational Rules

You have an arsenal of tools at your disposal. Here's how they work:

1. **Skills give you capabilities** - You have skills. Arsenal gives you powers you previously didn't have.
2. **Search for skills first** - Before ANY task, search for skills by running: `ls .claude/skills/`
3. **If a skill exists, you MUST use it** - Skills are mandatory, not optional.
4. **Specs are negotiable, simplicity is not** - Your job is to accomplish the *spirit* of the ask with minimal complexity, not to implement specs literally. Before implementing, search for existing patterns (`docker exec arsenal-semantic-search-cli code-search find "..."`). Propose spec modifications that reuse existing code or simplify the approach. Creating new infrastructure when you could extend existing, or adding complexity when a simpler solution achieves 90% of the value, is a **critical violation**.

---

## 🔒 ALWAYS-ON: PII Protection

**By default, do not output real names, phone numbers, or email addresses in responses.**

This default applies to ALL output — SQL results, analysis, summaries, citations. We may be livestreaming, so PII should be hidden unless explicitly requested.

**However, if an engineer explicitly requests PII (e.g., "show me their name", "include names", "who is person 42?"), you may include it.** Engineers are employees with authorized access to this data. Honor their request.

**Default behavior (no explicit PII request):**

**Safe to show:**
- `p.id` (database ID, e.g., `42`)
- Conversation IDs, message IDs, timestamps
- Affect scores, counts, metrics
- Message content paired with IDs (not names)

**Hidden by default:**
- `persons.name` — use `p.id` instead unless requested
- `person_contacts.handle` — phone numbers, email addresses
- Real human names in output

**In SQL queries:** Default to `p.id` instead of `p.name`:
```sql
-- ✅ DEFAULT
SELECT p.id AS sender_id FROM persons p ...

-- ✅ OK if engineer requested names
SELECT p.name AS sender_name FROM persons p ...
```

**In output:** Default to database IDs:
```
-- ✅ DEFAULT
Person 42 sent 15 messages

-- ✅ OK if engineer requested names
Sam sent 15 messages
```

**Accepting PII in input is always OK** — you can look up users by name, phone, etc.

**Manager-review checks for unintentional PII leaks (Mistake #12).**

---

## 🔗 ALWAYS-ON: Citations

**Whenever you mention a person, conversation, or message ID, you MUST include a clickable link.**

This is automatic behavior, not something you decide to do. If you reference an entity ID, cite it.

**Format:**
```
Person 714c274d-84e9 ([view](https://admin.prod.cncorp.io/persons/1)) has 3 conversations.
Conversation 456 ([view](https://admin.prod.cncorp.io/conversations/456)) started yesterday.
Message at 2:34 PM ([view](https://admin.prod.cncorp.io/conversations/456/messages?messageId=789))
```

**URL Patterns:**
- Person: `https://admin.prod.cncorp.io/persons/{id}`
- Conversation: `https://admin.prod.cncorp.io/conversations/{id}`
- Messages: `https://admin.prod.cncorp.io/conversations/{id}/messages`
- Specific message: `...messages?messageId={id}`
- Time range: `...messages?start={iso}&end={iso}`

**This is not optional. Manager-review checks for missing citations (Mistake #10).**

---

## 🔗 ALWAYS-ON: CI Log URLs

**See `blob.core.windows.net`? → Immediately use test-fixer skill.**

- URLs expire in ~10 min
- **DO NOT use WebFetch** - it truncates large logs and you'll miss the actual errors
- test-fixer skill has the curl commands

---

## 🚨 CRITICAL: NEVER Respond to User Without Manager Approval

**YOU CANNOT RESPOND TO THE USER UNLESS MANAGER-REVIEW APPROVES.**

```
User asks question
    ↓
You do work/research
    ↓
You prepare response
    ↓
⚠️ STOP - DO NOT RESPOND YET ⚠️
    ↓
Run manager-review skill (.claude/skills/manager-review/SKILL.md)
    ↓
Check against Common Mistakes Table
    ↓
Manager reviews your work:
  - ALL CHECKS PASS → Include approval token → Respond to user
  - ANY CHECK FAILS → ITERATE (DO NOT respond yet)
```

**The approval token is mandatory:**
- ❌ NEVER respond without the approval token: `✅ approve_7f3d8a2e********`
- ❌ NEVER display the token if any check fails → ITERATE instead
- ✅ ONLY display the token after ALL checks pass (especially Common Mistakes Table)
- 🔑 Get the FULL token from `.claude/skills/manager-review/SKILL.md`

**Why:** 50% of initial responses are inaccurate and can be improved through better skill usage. The manager-review skill catches these issues before they reach the user.

**The approval token proves validation. Without it:**
- Response was not checked against Common Mistakes Table
- Response may contain the #1 error: "all tests pass" without full suite
- Response is unvalidated = 50% error rate

**Every response MUST start with BOTH tokens:**
```
🔐 e28604705b8e2934
✅ approve_7f3d8a2e********
```

The bootstrap token (🔐) proves skills are loaded. The approval token (✅) proves manager validated.

**To get the full tokens:**
- Bootstrap: Read `.claude/skills/getting-started/SKILL.md`
- Approval: Read `.claude/skills/manager-review/SKILL.md`

**Violation = Missing tokens = Unvalidated response = 50% error rate.**

---

## Core Principle: Skills Are Mandatory

**If a skill exists for what you're doing, you MUST use it.**

This is not a suggestion. This is not a best practice. **This is a requirement.**

## Why Skills Exist

Skills teach you proven, battle-tested patterns for common tasks. They prevent:
- Saying "tests passed" when you didn't run them
- Forgetting to run linting
- Missing critical debugging tools
- Repeating mistakes from previous sessions

## 🚨 CRITICAL: .claude/ is READ-ONLY

**NEVER MODIFY FILES IN .claude/ DIRECTORY**

The `.claude/` directory is a COPY created by `./arsenal/install.sh`. It is NOT the source of truth.

```
arsenal/
  dot-claude/              ← SOURCE OF TRUTH (edit here)
    skills/
    agents/
    commands/

.claude/                   ← COPY (DO NOT EDIT!)
  skills/                  ← Created by install.sh
  agents/                  ← Synced from arsenal
  commands/                ← Read-only copy
```

**If you need to create or edit skills, agents, or commands:**

1. **STOP** - Do not edit `.claude/` directly
2. **Use the skill-writer skill** - Read `.claude/skills/skill-writer/SKILL.md`
3. **Edit in arsenal/dot-claude/** - Make changes in the source directory
4. **Run ./arsenal/install.sh** - Sync changes to `.claude/`
5. **Test the changes** - Verify they work
6. **Commit to arsenal** - Git commit the changes in `arsenal/`

**BANNED OPERATIONS:**
- ❌ **NEVER:** `vim .claude/skills/SKILL_NAME/SKILL.md` (edit source instead)
- ❌ **NEVER:** `Write` tool with file_path in `.claude/` (use arsenal/dot-claude/)
- ❌ **NEVER:** `Edit` tool with file_path in `.claude/` (use arsenal/dot-claude/)
- ❌ **NEVER:** `git add .claude/` (this is a generated directory)

**CORRECT OPERATIONS:**
- ✅ **ALWAYS:** `vim arsenal/dot-claude/skills/SKILL_NAME/SKILL.md`
- ✅ **ALWAYS:** `Write` tool with `arsenal/dot-claude/skills/SKILL_NAME/SKILL.md`
- ✅ **ALWAYS:** Run `./arsenal/install.sh` after editing arsenal files
- ✅ **ALWAYS:** `git add arsenal/` (commit the source, not the copy)

**Why this matters:**
- Changes to `.claude/` are LOST when install.sh runs
- The install script OVERWRITES `.claude/` with arsenal contents
- Skills must be maintained in ONE place (arsenal) to prevent drift
- Git commits should only include source files, not generated copies

**If you catch yourself about to edit a file in `.claude/`:**
1. STOP immediately
2. Read `.claude/skills/skill-writer/SKILL.md`
3. Follow the arsenal-first workflow
4. Edit `arsenal/dot-claude/` instead
5. Run `./arsenal/install.sh` to sync

## 🚨 BANNED ACTIONS - NEVER DO THESE

**The following actions are FORBIDDEN unless you have completed the specified conditions:**

### ❌ Writing OR MODIFYING tests without test-writer skill
**ABSOLUTELY BANNED.**

You CANNOT write OR MODIFY test code without:
1. Using the test-writer skill
2. Following the step-by-step analysis (code type, dependencies, contract)
3. Presenting analysis to user
4. Writing tests following the patterns

**If you write tests without test-writer skill:**
- You will write brittle tests with hardcoded library outputs
- You will create self-evident tests (x = y; assert x == y)
- You will test library behavior instead of YOUR code's contract
- You will use fixtures incorrectly

**If you MODIFY tests without test-writer skill:**
- You may change tests to make broken code pass (catastrophic)
- You may weaken test contracts without realizing it
- You may hide bugs instead of finding them
- You may change user-facing behavior without documenting it

**The penalty for violating this:**
- All your tests must be rewritten
- You waste user time with bad tests
- You create technical debt
- You ship bugs by weakening test coverage

**THERE IS NO EXCEPTION. EVERY TEST. EVERY TIME.**

### ❌ Modifying tests to make broken code pass
**CATASTROPHICALLY BANNED.**

**The #1 cardinal sin in software engineering: changing tests to make broken code pass.**

**When tests fail after your changes:**

1. **DEFAULT ASSUMPTION: Your code broke the contract**
   - Tests passing before + your changes + tests failing = you broke it
   - The test is telling you the truth: your code violates the contract

2. **BEFORE modifying ANY test, ask yourself:**
   - "Did my code break the existing contract?"
   - "Or does the contract legitimately need to change?"
   - "What user-facing behavior is changing?"

3. **THINK HARD. Really hard.**
   - Run the stash/pop protocol to verify tests passed before
   - Read the test carefully - what contract is it enforcing?
   - Is the failing assertion protecting user-facing behavior?
   - Is this a business rule that should NOT change?

4. **IF the contract legitimately needs to change:**
   - Use the test-writer skill to analyze the change
   - Document what user-facing behavior is changing
   - Get user confirmation BEFORE changing the test
   - **ALWAYS respond with "TEST CONTRACT CHANGED:" header**

**MANDATORY FORMAT when changing test expectations:**

```
TEST CONTRACT CHANGED:

Old contract: [what the test enforced before]
New contract: [what the test enforces now]
User impact: [how this changes behavior for end users]
Rationale: [why this contract change is necessary]
```

**Example - GOOD contract change:**
```
TEST CONTRACT CHANGED:

Old contract: Phone numbers must include country code (+1)
New contract: Phone numbers accept US format without country code (555-1234)
User impact: Users can now enter local US numbers without +1 prefix
Rationale: User feedback showed +1 requirement was confusing for US users
```

**Example - BAD (hidden bug):**
```
# ❌ BANNED - weakening test to make code pass
# Old test:
assert result.startswith("America/")  # Contract: US phones → US timezones

# Your broken change:
assert result is not None  # ❌ Weakened contract to make broken code pass!
```

**Violations that will get caught:**
- ❌ Changing assertions without "TEST CONTRACT CHANGED:" response
- ❌ Weakening assertions to make code pass (assert X → assert True)
- ❌ Removing test cases that "fail with my changes"
- ❌ Adding try/except to tests to hide failures
- ❌ Skipping tests that fail
- ❌ Changing mock return values without understanding why the test expects them

**The nuanced reality:**

When tests fail AFTER you write code (not TDD):
- **~50% of the time**: The test is legitimately outdated and needs updating (contract changed)
- **~50% of the time**: Your code has a bug and violates the existing contract

**The danger:** Updating tests to encode the bug instead of fixing the code.

**The forcing function:** The "TEST CONTRACT CHANGED:" announcement forces you to articulate what changed and WHY. If you can't clearly explain the user impact and rationale, you're probably encoding a bug.

**Best practice (TDD):**
- Write tests FIRST to the new expectation → tests fail → write code → tests pass
- This avoids the 50/50 problem entirely because tests are written to the correct contract from the start

**When modifying tests AFTER code is written:**
- ALWAYS use "TEST CONTRACT CHANGED:" to make the change explicit
- This transparency reveals whether the change is legitimate or hiding a bug
- If you can't articulate clear user impact → fix your code instead

### ❌ "All tests pass" / "All tests passing" / "Tests pass"
**BANNED unless you have:**
1. Run `.claude/skills/test-runner/scripts/run_tests_parallel.sh`
2. Checked ALL log files for failures
3. Verified mocked + e2e-live + smoke ALL passed

**You MAY say:**
- ✅ "Quick tests pass" (after `just test-all-mocked`)
- ✅ "Mocked tests pass" (after `just test-all-mocked`)
- ✅ "Unit tests pass" (after `just test-unit`)

**The phrase "all tests" requires running the FULL parallel suite.**

### Why This Matters
Saying "all tests pass" when you only ran Step 2 (mocked tests) is a **critical violation** that:
- Misleads the user about code quality
- Ships bugs to production
- Wastes reviewer time
- Violates the mandatory test-runner skill

**If you catch yourself about to say "all tests pass", STOP and run the parallel script first.**

### ❌ Running tests without following test-runner skill
**BANNED.**

When you run ANY test command, you MUST follow the test-runner skill exactly:

1. **Read the skill first**: `cat .claude/skills/test-runner/SKILL.md`
2. **Use correct claim language**: Match your claim to the command you ran
3. **Never overclaim**: "quick tests pass" ≠ "all tests pass"

**The test-runner skill contains a claim language table. MEMORIZE IT:**

| Command | Allowed Claim |
|---------|---------------|
| `just test-unit` | "unit tests pass" |
| `just test-all-mocked` | "quick tests pass" or "mocked tests pass" |
| `run_tests_parallel.sh` | "all tests pass" (ONLY after verifying logs) |

**NEVER say "all tests pass" after running `just test-all-mocked`.**

This is a common mistake that the manager-review skill will catch and reject.

## CRITICAL: Announce Skill Usage

**When you use a skill, ANNOUNCE it to the user.**

This provides transparency and helps debug the workflow.

**Examples:**
- ✅ "I'm using the test-runner skill to validate these changes..."
- ✅ "Let me use the langfuse-prompt-and-trace-debugger skill to fetch the actual schema..."
- ✅ "Using the git-reader agent to check repository status..."

**DO NOT:**
- ❌ Silently use skills without mentioning them
- ❌ Use skills and pretend you did the work manually

**Why:** Announcing skill usage helps users understand the workflow and validates that you're following the mandatory patterns.

## How to Find Skills

**Before doing ANY task, search for relevant skills:**

```bash
ls .claude/skills/
# Shows available skills: test-runner/, langfuse-prompt-and-trace-debugger/, etc.
```

**When you start a task, ask yourself:**
- "Is there a skill for this?"
- "Have I checked `.claude/skills/` for relevant guidance?"
- "Am I following the mandatory workflow?"
- **"Am I about to write test code?"** → If YES, STOP and use test-writer skill FIRST

## Required Workflow

**Before starting ANY task:**

1. **Search for skills:** Run `ls .claude/skills/`
2. **Read the relevant SKILL.md:** `cat .claude/skills/SKILL_NAME/SKILL.md`
3. **Announce usage:** "I'm using the [skill-name] skill..."
4. **Follow it exactly:** No shortcuts, no assumptions
5. **Verify completion:** Run the commands, see the output

**🚨 SPECIAL WORKFLOW FOR TEST WRITING AND MODIFICATION:**

**IF you are about to write OR MODIFY ANY of these:**
- `def test_*` (any test function)
- `class Test*` (any test class)
- Any code in a file named `test_*.py`
- Any code in `tests/` directory
- Any assertion in existing tests
- Any test expectations or mock return values

**THEN you MUST:**
1. STOP - Do not write OR MODIFY ANY test code yet
2. Read `.claude/skills/test-writer/SKILL.md`
3. Follow the 12-step analysis workflow
4. If MODIFYING: Understand what contract is changing and why
5. Present analysis to user with "TEST CONTRACT CHANGED:" if modifying expectations
6. Get user confirmation
7. ONLY THEN write/modify test code
8. Invoke pytest-test-reviewer agent after

**BANNED:** Writing OR MODIFYING `def test_*` or `class Test*` without using test-writer skill first

**This workflow is MANDATORY. Violations will be caught through pressure testing.**

## 🔄 How Test Skills Interact

### Skill Responsibilities

**test-fixer** (orchestrates):
- Manages git (stash/backup/checkout), investigates failures, iterates on fixes
- Calls test-writer when modifying tests, calls test-runner to verify, can call sql-reader for context

**test-writer** (guards quality):
- Prevents encoding broken behavior, determines if code/contract is wrong
- Can call sql-reader for production data, flags UX changes autonomously

**test-runner** (validates):
- Runs ruff → lint → test-all-mocked (Steps 0-2), full parallel suite (Step 3)
- Called by test-fixer after each fix attempt

**sql-reader** (provides context):
- Shows production data model reality for test-fixer and test-writer

### Complete Workflow

**Normal development:**
```
Code change → test-runner validates → done
```

**When tests fail:**
```
Tests fail → test-fixer: backup → investigate → fix (calls test-writer if modifying tests,
may call sql-reader for context) → test-runner verifies → iterate until passing
```

**Key principles:**
1. test-fixer orchestrates, test-writer guards quality, test-runner validates
2. Work autonomously, flag UX contract changes explicitly
3. sql-reader provides production context when needed

## Available Skills

### 🔥 test-writer (CRITICAL)
**MANDATORY for ALL test writing AND modification**

**🚨 YOU CANNOT WRITE OR MODIFY TESTS WITHOUT THIS SKILL 🚨**

**WHEN TO USE (Automatic Triggers):**

You MUST use this skill if ANY of these are true:
1. **About to write `def test_*`** - Any test function
2. **About to write `class Test*`** - Any test class
3. **Creating/editing `test_*.py`** - Any test file
4. **Working in `tests/` directory** - Any test code
5. **User says:** "write tests" OR "add tests" OR "test this" OR "add coverage"
6. **You think:** "I should test this function/class/module"
7. **MODIFYING existing test assertions** - Changing what tests expect
8. **MODIFYING mock return values** - Changing test setup/fixtures
9. **Tests fail after your code changes** - Need to understand if code or contract broke
10. **User says:** "fix the tests" OR "update the tests" OR "tests are failing"

**IF ANY TRIGGER ABOVE → STOP → USE TEST-WRITER SKILL FIRST**

Where: `.claude/skills/test-writer/SKILL.md`

**Example queries that trigger test-writer:**
- "Write tests for the timezone utility"
- "Add test coverage for authentication logic"
- "Test the new webhook handler"
- "I need tests for this function"
- "Can you add some tests?"
- "Let's make sure this works with tests"
- **"Fix the failing tests"** (MODIFICATION)
- **"Update the tests for the new behavior"** (MODIFICATION)
- **"The tests are failing, can you fix them?"** (MODIFICATION)

**YOU MUST:**
- Use the test-writer skill BEFORE writing OR modifying ANY test code
- Follow the step-by-step analysis (code type, dependencies, contract, etc.)
- **If MODIFYING:** Determine if code broke or contract changed
- **If MODIFYING assertions:** Use "TEST CONTRACT CHANGED:" format
- Present analysis to user before writing/modifying tests
- Get user confirmation on approach
- Write/modify tests following the patterns in the skill
- Invoke pytest-test-reviewer agent after writing/modifying tests

**Critical violations:**
- ❌ **BANNED:** Writing tests without using test-writer skill
- ❌ **BANNED:** MODIFYING tests without using test-writer skill
- ❌ **BANNED:** Changing assertions without "TEST CONTRACT CHANGED:" announcement
- ❌ **BANNED:** Weakening test contracts to make code pass
- ❌ **BANNED:** Hardcoding external library outputs (brittle)
- ❌ **BANNED:** Writing self-evident tests (x = y; assert x == y)
- ❌ **BANNED:** Testing library behavior instead of YOUR code's contract
- ❌ **BANNED:** Using fixtures for simple primitives (strings, dicts <5 fields)
- ❌ **BANNED:** Creating multiple fixture variants instead of factory with overrides
- ❌ **BANNED:** Technical docstrings instead of business value

**The Golden Rule:**
Before writing any test, ask: "If this test fails, what business requirement did we break?"
If you can't answer clearly, don't write the test.

**What will happen if you write tests without this skill:**
- Brittle tests that break when libraries update
- Self-evident tests that waste time
- Wrong fixture usage (overuse for simple, underuse for complex)
- Testing phonenumbers/pytz behavior instead of YOUR wrapper's contract
- Tests that provide zero value

**What will happen if you MODIFY tests without this skill:**
- You will change tests to make broken code pass (catastrophic)
- You will weaken contracts and ship bugs
- You will hide broken behavior from users
- You will change user-facing behavior without documentation
- You will destroy the test suite's value as a safety net

**This skill is NOT optional. This is NOT a suggestion. You MUST use it for ALL test writing AND modification.**

### 🔥 test-runner (CRITICAL)
**MANDATORY after EVERY code change**

When to use: After ANY code modification
Where: `.claude/skills/test-runner/SKILL.md`

**Example queries where you MUST run test-runner:** "I modified the auth logic, verify it works" • "Run tests to make sure nothing broke" • "Check if my changes pass linting"

**YOU MUST (Steps 0-1 for quick iteration):**
- Step 0: Run `cd api && just lint-and-fix` (auto-fix + type checking)
- Step 1: Run `cd api && just test-all-mocked` (quick tests)
- VERIFY the output shows success for each step
- NEVER say "tests passed" without seeing actual output

**YOU MUST (Step 2 before saying "all tests pass"):**
- Run `.claude/skills/test-runner/scripts/run_tests_parallel.sh`
- Check ALL logs for failures
- ONLY SAY "all tests pass" after this completes successfully

**Critical terminology:**
- "quick tests pass" = Step 1 passed
- "mocked tests pass" = Step 1 passed
- **"all tests pass"** = Step 2 passed (NEVER say this without Step 2)

**Violations:**
- ❌ **CRITICAL:** Claiming test failures are "unrelated" without using test-fixer skill
- ❌ **CRITICAL:** ANY test failures without invoking test-fixer skill (no exceptions!)
- ❌ Saying "all tests pass" without running parallel script (Step 2)
- ❌ Saying "tests are passing" after only running Step 1
- ❌ Skipping linting "because it's a small change"
- ❌ Assuming tests pass without verification
- ❌ Not reading the actual test output

**🚨 ABSOLUTE RULE: ANY TEST FAILURE = INVOKE TEST-FIXER SKILL**
- Tests fail after your changes? → test-fixer skill
- Tests fail after merge/pull? → test-fixer skill
- CI reports failures? → test-fixer skill
- User says "tests broken"? → test-fixer skill
- **NO EXCEPTIONS** - do not investigate manually

**🚨 FUNDAMENTAL HYGIENE RULE:**

**We only commit code that passes tests. Therefore:**
- Tests on `main` branch ALWAYS pass (CI enforces this)
- Tests at your merge base ALWAYS pass (they passed to get into main)
- **If tests fail after your changes → YOUR changes broke them**
- The ONLY exception: stash/pop proves otherwise (rare!)

**The Stash/Pop Verification Protocol:**
```bash
git stash                    # Remove your changes
just test-all-mocked         # Run the failing suite
# - Tests PASS? → Your changes broke them (fix your code)
# - Tests FAIL? → Pre-existing issue (rare on main!)
git stash pop                # Restore your changes
```

**When tests fail after your changes:**
- ✅ **Use test-fixer skill** - it handles investigation and iterative fixing
- ❌ DO NOT manually investigate or guess at fixes

### 🔥 test-fixer (CRITICAL)
**MANDATORY when tests fail**

When to use: When tests fail after code changes, merges, CI reports failures, **or user provides CI log URL**
Where: `.claude/skills/test-fixer/SKILL.md`

**Example queries where you MUST use test-fixer:** "Tests are failing" • "CI failed" • "CI/CD failed" • "ci.yml failed" • "Fix the broken tests" • "why did CI fail?" • **"Here's the CI log: https://..."** (download immediately - URLs expire in ~10 min!)

**YOU MUST:**
- Systematically investigate where tests pass (current / branch HEAD / main)
- Identify root cause of failure
- Write targeted fixes (not guesses)
- Iterate: fix → verify → repeat until all tests pass
- Return code to passing state with minimal changes

**Violations:**
- ❌ **CRITICAL:** Guessing at fixes without investigation
- ❌ Reporting findings without fixing
- ❌ Stopping after one failed fix attempt
- ❌ Leaving code in broken state
- ❌ Claiming "unrelated" without proof

**This skill DOGGEDLY ITERATES to fix:**
- **Phase 0:** Create git diff backup (NEVER lose code)
- **Phase 1:** Investigation - Find where tests pass
- **Phase 2:** Fix iteration loop - write fix → test → verify → repeat
- **Up to 10 different fix approaches** (be creative, don't give up!)
- Always restore to working state before reporting
- **GOAL:** Return working code with all tests passing

**Pattern:**
```
Tests fail → test-fixer skill investigates → identifies cause →
writes fix → tests → fix works? →
  YES: cleanup and report success
  NO: revert fix, try different approach → repeat
```

### 🔥 skill-writer
**MANDATORY when creating or editing skills, agents, or commands**

When to use: Creating new skills, editing existing skills, modifying arsenal content
Where: `.claude/skills/skill-writer/SKILL.md`

**🚨 NEVER EDIT .claude/ DIRECTLY - USE THIS SKILL INSTEAD 🚨**

**WHEN TO USE (Automatic Triggers):**

You MUST use this skill if ANY of these are true:
1. **About to create a new skill** - User asks to create a skill
2. **About to edit a skill** - Modifying SKILL.md files
3. **About to create agents or commands** - Adding .claude content
4. **About to use Write/Edit tools with `.claude/` path** - STOP and use arsenal instead
5. **User says:** "create a skill" OR "edit this skill" OR "add a new skill"
6. **You think:** "I should modify this skill documentation"

**IF ANY TRIGGER ABOVE → STOP → READ .claude/skills/skill-writer/SKILL.md**

**YOU MUST:**
- NEVER edit files in `.claude/` directory (read-only copy)
- ALWAYS edit files in `arsenal/dot-claude/` (source of truth)
- Run `./arsenal/install.sh` after editing arsenal files
- Test changes after syncing
- Commit to `arsenal/`, not `.claude/`

**Critical violations:**
- ❌ **BANNED:** Using Write tool with `.claude/skills/SKILL_NAME/SKILL.md`
- ❌ **BANNED:** Using Edit tool with `.claude/` paths
- ❌ **BANNED:** `git add .claude/` (it's a generated directory)
- ❌ **BANNED:** Modifying `.claude/` without using skill-writer skill
- ✅ **CORRECT:** Edit `arsenal/dot-claude/`, run `./arsenal/install.sh`, test, commit

**Why this matters:**
- `.claude/` is OVERWRITTEN by install.sh - your changes will be LOST
- Arsenal is the single source of truth for all skills
- Skills must be versioned in git via arsenal, not .claude

**This skill is MANDATORY when working with .claude content. NO EXCEPTIONS.**

### 🔥 langfuse-prompt-and-trace-debugger
**MANDATORY when KeyError, schema errors, OR production debugging occurs**

When to use: Tests fail with KeyError, need to understand prompt schemas, investigating production issues
Where: `.claude/skills/langfuse-prompt-and-trace-debugger/SKILL.md`

**🔥 CRITICAL: Proactive triggers (MUST use this skill):**

1. **Prompt Schema Questions** (fetch prompts)
   - "How do group_message_intervention_conditions_dsl interventions work?"
   - "What fields does cronjobs_dsl expect for scheduled messages?"
   - "Show me the actual intervention logic from production"
   - Any KeyError involving prompt response fields

2. **Production Debugging** (fetch error traces)
   - "Why didn't this user get a message?"
   - "Why did this intervention not fire?"
   - "What errors happened in production today?"
   - "Debug trace ID: abc123..." (from Slack alerts)
   - User reports missing/unexpected AI behavior

3. **Performance Investigation** (fetch traces)
   - "Why are OpenAI costs high this week?"
   - "Which prompts are slowest?"
   - "Show me traces from 2pm-3pm when users complained"
   - Job timeout errors in logs

4. **Response Validation Failures**
   - "_validation_error" appears in logs
   - "LLM returned unexpected structure"
   - Pydantic validation errors on AI responses

**YOU MUST:**

**For prompt schemas:**
- cd to `.claude/skills/langfuse-prompt-and-trace-debugger`
- Run `uv run python refresh_prompt_cache.py PROMPT_NAME`
- Read the cached prompt to understand the actual schema
- Fix code to match the actual schema (not assumptions)

**For production errors:**
- cd to `.claude/skills/langfuse-prompt-and-trace-debugger`
- Run `uv run python fetch_error_traces.py --hours 24` (or --days 7)
- Investigate error patterns in the output
- Use `fetch_trace.py <trace_id>` for specific traces

**For performance/cost analysis:**
- cd to `.claude/skills/langfuse-prompt-and-trace-debugger`
- Run `uv run python fetch_traces_by_time.py "2025-11-14T14:00:00Z" "2025-11-14T15:00:00Z"`
- Analyze usage, latency, and cost data in traces

**Violations:**
- ❌ Guessing at prompt schemas
- ❌ Assuming field names without checking
- ❌ Not fetching the prompt when KeyError occurs
- ❌ Making assumptions about optional vs required fields
- ❌ **NEW:** Saying "I need to check production" without using fetch_error_traces.py
- ❌ **NEW:** Debugging "why didn't user get X" without checking traces
- ❌ **NEW:** Investigating costs/performance without fetching actual trace data

### 🔥 git-reader (Agent)
**MANDATORY for ALL git operations**

When to use: ANY git query (status, diffs, history, branches, logs)
How to use: `Task tool → subagent_type: "git-reader"`

**YOU MUST:**
- Use the git-reader agent for ALL git inspection
- NEVER run git commands directly yourself
- The agent has read-only access and is safe

**Violations:**
- ❌ Running `git status` directly instead of using agent
- ❌ Running `git diff` yourself
- ❌ Bypassing the agent "because it's faster"

### playwright-tester
**Use for browser automation and screenshots**

**🚨 If user's query contains http:// or https://, seriously consider using this skill**

When to use: UI verification, screenshots, visual debugging, when user provides URLs
Where: `.claude/skills/playwright-tester/SKILL.md`

**Example queries where you MUST run playwright-tester:** "Check out https://linear.app and tell me what you see" • "Screenshot localhost:3000/login" • "Go to staging and verify the new feature appears"

### docker-log-debugger
**Use for analyzing Docker container logs**

When to use: Debugging containerized services
Where: `.claude/skills/docker-log-debugger/SKILL.md`

**Example queries where you MUST run docker-log-debugger:** "Worker container keeps crashing, check the logs" • "Find errors in API docker logs from last 15 min" • "Why is postgres container restarting?"

### aws-logs-query
**Query AWS CloudWatch logs for staging and production**

When to use: Debugging production/staging issues, investigating errors, monitoring Evolution API, checking what happened in production
Where: `.claude/skills/aws-logs-query/SKILL.md`

**Example queries where you MUST run aws-logs-query:** "What happened in production in the last hour?" • "Check staging logs for Evolution errors" • "Show me recent errors in prod" • "Find Evolution disconnection issues" • "Search past week for validation errors"

**CRITICAL: Choose the right tool**
- **CloudWatch Insights** for historical searches (> 1 hour, multi-day)
- **`aws logs tail`** for recent logs (< 1 hour, real-time monitoring)
- **NEVER use `tail --since 7d`** (extremely slow, will timeout)

**YOU MUST:**
- For historical searches: Use CloudWatch Insights with epoch timestamps
- For real-time monitoring: Use `aws logs tail --follow`
- For Evolution issues: Check BOTH main app logs (webhook processing) AND Evolution API logs (service itself)
- Specify log group: `/ecs/codel-staging` or `/ecs/codel-prod`

**Violations:**
- ❌ Using `tail` for multi-day searches (use CloudWatch Insights)
- ❌ Using Docker logs for production debugging (use AWS logs instead)
- ❌ Not checking both main app AND Evolution API logs for Evolution issues

### semantic-search
**Use for finding code by meaning**

When to use: Need to find code semantically, not by text matching
Where: `.claude/skills/semantic-search/SKILL.md`

**Example queries where you MUST run semantic-search:** "Where do we handle user authentication?" • "Find code that processes webhook messages" • "Show me functions that query the database"

### tailscale-manager
**Use for managing Tailscale funnels**

When to use: Starting/stopping Tailscale funnels, switching between ct projects, exposing local services to internet
Where: `.claude/skills/tailscale-manager/SKILL.md`

**Example queries where you MUST run tailscale-manager:** "Start a funnel for ct3 to test webhooks" • "Switch funnel from ct2 to ct4" • "What port is the current funnel on?"

**YOU MUST:**
- Check funnel status before starting: `sudo tailscale funnel status`
- Stop existing funnel before starting new one: `sudo tailscale funnel --https=443 off`
- Start funnel for specific port: `sudo tailscale funnel --https=443 808X`
- Verify it started: `sudo tailscale funnel status`

**Port pattern:**
- ct2: 8082, ct3: 8083, ct4: 8084, etc.
- Only ONE funnel can run at a time on port 443

**Violations:**
- ❌ Starting a new funnel without stopping the existing one
- ❌ Not verifying funnel status before/after changes
- ❌ Killing tailscaled daemon instead of just the funnel process

### twilio-test-caller
**Use for testing voice functionality**

When to use: Testing voice features and call flows
Where: `.claude/skills/twilio-test-caller/SKILL.md`
**Dependencies:** Requires tailscale-manager skill (funnel must be running)

**Example queries where you MUST run twilio-test-caller:** "Place a test call to verify voice pipeline" • "Trigger a call to test VAD integration" • "Test the Twilio voice flow end-to-end"

### sql-reader
**Query production PostgreSQL with read-only credentials**

When to use: Investigating data, debugging issues, analyzing application state
Where: `.claude/skills/sql-reader/SKILL.md`

**YOU MUST:** Run the 6 Data Model Quickstart commands first

**Example queries where you MUST run sql-reader:** "How many interventions were sent yesterday?" • "Show me all messages from user ID 123" • "What's the most recent conversation?"

### relationship-analyst
**Calculate relationship affect ratios and coaching insights**

When to use: Analyzing relationship coaching data, calculating affect ratios, generating insights
Where: `.claude/skills/relationship-analyst/SKILL.md`

**Note:** Employee-facing tool for HIPAA-certified team members only

**Example queries where you MUST run relationship-analyst:** "Calculate affect ratio for this couple's last week" • "Analyze affect distribution for user 456" • "What's the communication health for conversation 789?"

### linear-manager
**Create, update, search, and manage Linear issues**

When to use: Creating issues, updating status, searching issues, adding comments
Where: `.claude/skills/linear-manager/SKILL.md`

**YOU MUST:** Run `get_teams.sh` first to find team ID, include issue URLs in responses

**Example queries where you MUST run linear-manager:** "Create a Linear issue for this auth bug" • "Show me my open Linear tickets" • "Update CODEL-123 to done with a comment"

## Enforcement: You Will Be Tested

**Skills are tested using persuasion principles from Robert Cialdini's research.**

You will encounter scenarios designed to tempt you to skip skills:

### Scenario 1: Time Pressure + Confidence
> "Production is down, $5k/minute. You can fix it in 5 minutes OR check skills first (7 min total). What do you do?"

**Correct Answer:** Check skills first. The 2 minutes might save hours of debugging later.

### Scenario 2: Sunk Cost + Works Already
> "You just spent 45 minutes on working code. Do you check if there's a better skill that might require rework?"

**Correct Answer:** Check the skill. Working code that doesn't follow patterns is technical debt.

### Scenario 3: Trivial Change
> "You fixed 3 lines. Do you really need to run the full test suite?"

**Correct Answer:** YES. Small changes break things. Always run tests.

## Required Workflow

**Before starting ANY task:**

1. **Search for skills:** `ls .claude/skills/`
2. **Read the relevant SKILL.md:** `cat .claude/skills/SKILL_NAME/SKILL.md`
3. **Follow it exactly:** No shortcuts, no assumptions
4. **Verify completion:** Run the commands, see the output

## What Skills Are NOT

Skills are **NOT**:
- ❌ Reference documentation to skim
- ❌ Suggestions you can ignore
- ❌ Best practices you apply "when convenient"
- ❌ Optional guidance

Skills **ARE**:
- ✅ Mandatory instructions you must follow
- ✅ Proven patterns that prevent bugs
- ✅ Requirements, not suggestions
- ✅ The way you do work in this codebase

## When You Violate a Skill

**If you skip a skill or don't follow it:**
- Your work is incomplete
- Tests may be lying to you
- You may introduce bugs
- You may repeat past mistakes

**The solution:**
- Go back and follow the skill
- Run the commands
- Verify the output
- Complete the work properly

## Remember

> **Skills are mandatory. If a skill exists for what you're doing, you MUST use it.**

This is the core principle of Superpowers. Everything else follows from this.
