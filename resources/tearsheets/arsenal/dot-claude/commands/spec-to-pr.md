---
description: Generate code implementation from a feature spec and create a GitHub PR
---

# Spec to PR Command

**Purpose:** Transform a feature spec markdown file into working code and create a GitHub pull request.

## When to Use

Use this command to implement a feature spec:
- **After /question-to-spec:** Creates spec → /spec-to-pr creates PR
- **Manual specs:** You wrote a spec → /spec-to-pr implements it
- **Automated workflow:** Cron job creates specs → cron job creates PRs

**Target cron usage:**
```bash
# Step 1: 9am - Create spec from question
0 9 * * * claude -p "/question-to-spec 'Was there any user feedback in the last 24 hours?'"

# Step 2: 9:15am - Create PR from any new specs
15 9 * * * claude -p "/spec-to-pr"
```

## Workflow

**🚨 CRITICAL: Work completely autonomously. This workflow generates real code and creates real PRs. Do NOT ask questions - just execute the workflow.**

### Step 0: Find or Specify Spec File

**Execute immediately (DO NOT ASK):**

**If user provided a filename argument:**
- Use the specified file
- Example: `/spec-to-pr user-feedback-2025-11-14.md`

**If NO filename argument provided:**
- Automatically find the most recent spec in this order:
  ```bash
  # Search in order of preference:
  # 1. FINAL_SPEC.md (from /eng-prioritize workflow) - HIGHEST PRIORITY
  # 2. Most recent dated spec in docs/temp/specs/
  # 3. Most recent dated spec in project root
  # 4. Most recent dated spec in docs/specifications/

  if [ -f docs/temp/specs/FINAL_SPEC.md ]; then
    echo "docs/temp/specs/FINAL_SPEC.md"
  else
    ls -t docs/temp/specs/*-20*.md 2>/dev/null | head -1 || \
    ls -t *-20*.md 2>/dev/null | head -1 || \
    ls -t docs/specifications/*-20*.md 2>/dev/null | head -1
  fi
  ```
- Announce what you found: "Found spec: {filename}"
- Proceed immediately to Step 1

**If no spec files found anywhere:**
- Report error: "No spec files found. Run /question-to-spec or /proposal-to-spec first."
- Exit (DO NOT ask user to choose)

**IMPORTANT:**
- `FINAL_SPEC.md` from `/eng-prioritize` IS implementation-ready - proceed with implementation
- Spec will be automatically copied to `docs/specifications/` and committed with the PR

### Step 1: Read and Understand the Spec

1. **Read the spec file completely**
   - Problem: What are we solving?
   - Solution: What's the approach?
   - Implementation: What files need changes?
   - Testing: What test cases are needed?
   - Phases: If multi-phase spec, identify Phase 0 or Phase 1

2. **Extract key information:**
   - Title and feature name
   - Priority and effort estimate
   - Files to modify
   - New files to create
   - Dependencies and blockers
   - Acceptance criteria
   - **If multi-phase:** Identify the first implementable phase

3. **Validate the spec:**
   - ✅ Has Problem section with evidence
   - ✅ Has Solution with user experience
   - ✅ Has Implementation with file paths
   - ✅ Has Testing with test cases
   - ✅ **Accept all effort sizes:** XS, S, M, L, XL (do NOT reject L/XL specs)
   - ✅ **Accept multi-phase specs:** Implement first phase if spec has phases
   - ❌ If incomplete (missing required sections), ask user to improve spec first

**🚨 DO NOT REJECT SPECS based on:**
- Effort size (L, XL are acceptable - implement first phase)
- Number of phases (multi-phase is acceptable - implement Phase 0 or Phase 1)
- Source workflow (specs from /eng-prioritize are implementation-ready)

### Step 2: Plan the Implementation

**🚨 CRITICAL: DO NOT ask about scope, size, or phases. Just create the plan and proceed to implementation.**

**Automatically create an implementation plan (NO USER QUESTIONS):**

**If spec has multiple phases:**
- Identify Phase 0 or Phase 1 (first implementable phase)
- Plan ONLY that phase for this PR
- Note remaining phases in PR description for future work

**If spec is single-phase:**
- Plan the entire spec

1. **Break down the work (for the phase being implemented):**
   - Backend changes (models, API, logic)
   - Frontend changes (UI, components, styling)
   - Database migrations (if needed)
   - Tests (unit, integration, e2e)
   - Documentation updates

2. **Identify dependencies:**
   - What existing code/infrastructure is needed?
   - Any blockers mentioned in the spec?
   - Required external services or APIs?

3. **Determine implementation order:**
   1. Database schema changes (if any)
   2. Backend logic
   3. API endpoints
   4. Frontend integration
   5. Tests
   6. Documentation

**Announce the plan to user (then proceed immediately to Step 3):**
```
📋 Implementation plan for "{Feature Title}":
{If multi-phase: "Implementing Phase 0/1: {phase description}"}

Backend:
- [ ] Add streak_count, last_active_date to User model
- [ ] Create update_streaks() function
- [ ] Add cron job to run daily at 12:01am UTC

Frontend:
- [ ] Add streak display to user profile
- [ ] Add notification for streak milestones

Testing:
- [ ] Unit tests for update_streaks()
- [ ] Integration test for streak notification
- [ ] E2E test for 7-day streak flow

{If multi-phase:
Estimated time for Phase 0/1: {phase effort}
Remaining phases: Phase 2, Phase 3, Phase 4 (will be implemented in future PRs)
}
{If single-phase:
Estimated time: {effort from spec}
}
```

### Step 3: Implement the Code

**🚨 CRITICAL: Proceed directly to implementation. DO NOT ask if user wants to implement, DO NOT ask about phases, DO NOT ask about scope. The spec says what to build - build it.**

**Follow the project's coding standards from CLAUDE.md/AGENTS.md:**

#### General Guidelines
- **DRY (Don't Repeat Yourself):** Reuse existing patterns
- **Type hints:** Use modern Python 3.9+ generics (`list[str]`, `dict[str, Any]`)
- **No defensive programming:** Let errors surface (except for external APIs)
- **Imports at top:** All imports at file top (unless TYPE_CHECKING)
- **No try/except:** Unless handling external API errors
- **Testing strategy:** Integration tests > unit tests (focus on robust e2e)

#### For This Codebase Specifically

**From CLAUDE.md:**
- Avoid single-use functions (inline code unless reused)
- Use Alembic for database migrations (don't generate manually)
- Follow async architecture (use `@job` decorators for async processing)
- Use modern type hints
- Test files should use fixtures from api/tests/AGENTS.md patterns

**Implementation steps:**

1. **Backend changes:**
   - Modify existing files per spec
   - Create new files per spec
   - Add type hints to all functions
   - Follow existing patterns in codebase

2. **Database migrations (if needed):**
   - **DO NOT generate migration files**
   - Provide the command for user to run:
     ```bash
     docker exec -it codel-api alembic revision --autogenerate -m "Description"
     docker exec -it codel-api alembic upgrade head
     ```

3. **Tests:**
   - Follow patterns from api/tests/AGENTS.md
   - Use composable factory-style fixtures
   - Focus on integration/e2e tests (not brittle unit tests)
   - Test happy path + edge cases from spec

4. **Documentation:**
   - Update relevant README files (if needed)
   - Add docstrings to new functions
   - Comment complex logic (sparingly)

### Step 4: Run Quality Checks

**MANDATORY: Use the test-runner skill**

Before creating PR, verify code quality:

```bash
# Step 0: Auto-fix + type check
cd api && just lint-and-fix

# Step 1: Run tests
cd api && just test-all-mocked
```

**If any step fails:**
1. Fix the issues
2. Re-run the failing step
3. Continue only when all pass

**DO NOT create PR if quality checks fail.**

### Step 5: Copy Spec to docs/specifications/

**IMPORTANT: Specs must be committed to the repository as part of the PR.**

```bash
# Copy spec from top-level to docs/specifications/
cp {spec-file} docs/specifications/

# Example:
cp user-feedback-2025-11-14.md docs/specifications/
```

This ensures the spec is version-controlled with the implementation.

### Step 6: Create GitHub PR

**Use git commands to create PR:**

1. **Create feature branch:**
   ```bash
   git checkout -b feature/{feature-slug}
   ```

2. **Stage and commit changes (including spec):**
   ```bash
   git add {files changed} docs/specifications/{spec-filename}
   git commit -m "{commit message}

   {Brief description of changes}

   Implements: docs/specifications/{YYYY-MM-DD-feature-slug}.md

   🤖 Generated with Claude Code
   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

3. **Push to remote:**
   ```bash
   git push -u origin feature/{feature-slug}
   ```

4. **Create PR using gh CLI:**
   ```bash
   gh pr create \
     --title "{Feature Title}" \
     --body "$(cat <<'EOF'
   ## Feature: {Title}

   **Spec:** docs/specifications/{YYYY-MM-DD-feature-slug}.md
   **Priority:** {P0/P1/P2/P3}
   **Effort:** {XS/S/M/L/XL}

   ## Problem
   {Summary from spec}

   ## Solution
   {Summary from spec}

   ## Changes Made
   - {Change 1}
   - {Change 2}
   - {Change 3}

   ## Testing
   - [x] Tests pass locally (`just test-all-mocked`)
   - [x] Linting and formatting pass (`just lint-and-fix`)

   ## Acceptance Criteria
   {Copy from spec}

   ---
   🤖 Auto-generated from spec by /spec-to-pr command
   EOF
   )"
   ```

5. **Capture PR URL**

### Step 7: Update Spec File

Append to BOTH spec files (top-level and docs/specifications/):

```markdown
---

## Pull Request Created

✅ **PR:** https://github.com/{org}/{repo}/pull/{number}

**Branch:** `feature/{feature-slug}`
**Status:** Open
**Created:** {YYYY-MM-DD HH:MM}

**Next steps:**
1. Review the PR
2. Run additional tests if needed
3. Merge when ready
```

**Update both:**
- Top-level spec file (for local reference)
- `docs/specifications/{spec-filename}` (committed version)

### Step 8: Output Summary

**For cron job logs:**

```
✅ PR created from spec

📋 Spec: docs/specifications/user-feedback-2025-11-14.md (committed with PR)
🎯 Feature: Build 7-day streak for new users
⚙️ Priority: P1 (High)
📏 Effort: M (1 sprint)

🔧 Changes made:
- Modified 3 files
- Created 2 new files
- Added 15 tests
- Committed spec to docs/specifications/

✅ Quality checks:
- Formatting: ✅ Pass
- Type checking: ✅ Pass
- Tests: ✅ Pass (127/127 passed)

🔀 Pull Request:
Branch: feature/7-day-streak
URL: https://github.com/odio/ct3/pull/456

---
Next: Review and merge PR
```

## Examples

### Example 1: Auto-find most recent spec

```bash
$ claude -p "/spec-to-pr"

Finding most recent spec in specs/...
Found: specs/user-feedback-2025-11-14.md

Reading spec: "Build 7-day streak for new users"
Priority: P1, Effort: M (1 sprint)

📋 Implementation plan:
Backend:
- Add streak_count, last_active_date to User model
- Create update_streaks() function
- Add cron job

Frontend:
- Add streak display to profile
- Add streak notifications

Testing:
- 5 unit tests
- 3 integration tests
- 1 e2e test

Implementing backend changes...
[Writes code to specified files]

Implementing frontend changes...
[Writes code to specified files]

Creating tests...
[Writes test files]

Running quality checks...
✅ Formatting: Pass
✅ Type checking: Pass
✅ Tests: Pass (127/127)

Creating PR...
Branch: feature/7-day-streak
Commit: "Add 7-day streak for new user onboarding"
Push: ✅ Success

PR created: https://github.com/odio/ct3/pull/456

✅ PR created from spec

📋 Spec: docs/specifications/user-feedback-2025-11-14.md (committed)
🎯 Feature: Build 7-day streak for new users
🔀 PR: https://github.com/odio/ct3/pull/456

---
Next: Review and merge PR
```

### Example 2: Specify spec file

```bash
$ claude -p "/spec-to-pr funnel-2025-11-13.md"

Reading spec: "Fix partner invitation email delivery"
Priority: P0 (Critical), Effort: S (1-2 days)

Copying spec to docs/specifications/...
✅ Spec copied to docs/specifications/funnel-2025-11-13.md

[Implementation workflow...]

✅ PR created from spec

📋 Spec: docs/specifications/funnel-2025-11-13.md (committed)
🎯 Feature: Fix partner invitation email delivery
🔀 PR: https://github.com/odio/ct3/pull/455

---
Next: Review and merge PR immediately (P0)
```

## Configuration

### Spec File Location
```bash
# Default: Find most recent in current directory
/spec-to-pr

# Specify file (deterministic filename for cron)
/spec-to-pr user-feedback-2025-11-14.md

# Spec will be automatically copied to docs/specifications/ and committed with the PR
```

### Branch Naming
```bash
# Default: feature/{slug}
/spec-to-pr

# Custom branch prefix
/spec-to-pr --branch-prefix=implement-

# Results in: implement-7-day-streak
```

## Edge Cases

### Spec File Not Found
**Action:** Return error with instructions
```
❌ Spec file not found

Searched: ./ (project root)
No specs found matching *-YYYY-MM-DD.md

Did you mean:
- Run /question-to-spec first to create a spec
- Specify file: /spec-to-pr spec-filename.md
```

### Multiple Recent Specs
**Action:** Implement the most recent, list others
```
Found 3 specs from today:
1. user-feedback-2025-11-14.md (most recent)
2. funnel-2025-11-14.md
3. retention-2025-11-14.md

Implementing most recent: user-feedback-2025-11-14.md

To implement others:
- /spec-to-pr funnel-2025-11-14.md
- /spec-to-pr retention-2025-11-14.md
```

### Quality Checks Fail
**Action:** DO NOT create PR, report errors
```
❌ Quality checks failed - PR not created

✅ Formatting: Pass
❌ Type checking: 3 errors
  - api/src/models/user.py:42: Missing type hint
  - api/src/cron/streaks.py:15: Incompatible types
  - api/src/cron/streaks.py:23: Undefined name 'datetime'

❌ Tests: 2 failures
  - test_update_streaks_daily
  - test_streak_notification_sent

Fix these issues and run /spec-to-pr again.
```

### Database Migration Needed
**Action:** Provide commands, DO NOT create migration
```
⚠️ Database migration needed

This spec requires schema changes:
- Add columns: streak_count, last_active_date to users table

Run these commands to create and apply migration:

docker exec -it codel-api alembic revision --autogenerate -m "Add streak fields to User"
docker exec -it codel-api alembic upgrade head

After migration is created, re-run: /spec-to-pr
```

## Skills Used

1. **test-runner** (skill) - Run quality checks (ruff, lint, tests)
2. **Project patterns** (from CLAUDE.md/AGENTS.md) - Coding standards

## Notes

- **Specs are committed:** Always copy spec to docs/specifications/ and include in PR
- **Code quality matters:** Always run test-runner before creating PR
- **Follow existing patterns:** Look at similar code in the codebase
- **Don't over-engineer:** Implement exactly what the spec says (no extras)
- **Type everything:** All functions need type hints
- **Test thoroughly:** Cover happy path + edge cases from spec
- **Commit messages:** Include spec reference (docs/specifications/) and emoji
- **PR descriptions:** Link to spec in docs/specifications/, include summary, list changes
- **Both copies updated:** Update both top-level spec (local) and docs/specifications/ (committed) with PR info

Remember: The goal is to turn a **feature spec** into **working code** with a **reviewable PR** that includes the spec in version control.
