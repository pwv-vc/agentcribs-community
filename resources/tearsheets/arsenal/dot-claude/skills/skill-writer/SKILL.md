---
name: skill-writer
description: "INVOKE when: creating new skills, editing SKILL.md files, modifying .claude/ content. NEVER edit .claude/ directly - this skill shows the arsenal-first workflow."
---

# skill-writer Skill

## 🎯 Purpose

This skill explains how to create and edit Claude Code skills in the arsenal repository.

**Use this skill when:**
- Creating a new skill
- Editing existing skill documentation
- Understanding the skill development workflow
- Setting up skill metadata and structure

---

## Core Principle: Arsenal-First Development

**ALL skill code and documentation lives in `./arsenal/dot-claude/`**

The `.claude/` directory in the project root is a COPY, not the source of truth.

```
arsenal/
  dot-claude/              ← Source of truth (edit here)
    skills/
      getting-started/
        SKILL.md
      test-writer/
        SKILL.md
      your-new-skill/      ← Create new skills here
        SKILL.md

.claude/                   ← Copy (created by install.sh)
  skills/                  ← DO NOT edit directly!
    getting-started/
    test-writer/
    your-new-skill/
```

**Workflow:**
1. Edit files in `arsenal/dot-claude/skills/`
2. Run `./arsenal/install.sh` to sync changes to `.claude/`
3. Test the skill
4. Commit changes to arsenal (git add, git commit)

---

## Step 1: Understand Skill Structure

### Minimal Skill Structure

Every skill MUST have:
```
arsenal/dot-claude/skills/SKILL_NAME/
  SKILL.md              ← Main skill documentation (REQUIRED)
```

### Optional Components

Skills MAY have:
```
arsenal/dot-claude/skills/SKILL_NAME/
  SKILL.md              ← Main documentation (REQUIRED)
  scripts/              ← Shell scripts, Python scripts, etc.
    run_something.sh
    helper.py
  node_modules/         ← Auto-installed if package.json exists
  package.json          ← Node.js dependencies (optional)
  PRESSURE_TESTS.md     ← Tests to verify skill compliance (optional)
  README.md             ← Additional documentation (optional)
  .env.example          ← Environment template (optional)
```

### Skill Metadata

The SKILL.md should start with frontmatter metadata:

```markdown
---
name: skill-name
description: Brief one-line description shown in skill list
---

# skill-name Skill

## Purpose
...
```

**Important:** The `name` field is used in the skill registry and should match the directory name.

---

## Step 2: Plan Your Skill

Before creating a skill, answer these questions:

### Question 1: What problem does this skill solve?
- What task will users perform?
- What common mistakes does this prevent?
- Why is a skill needed instead of just documentation?

### Question 2: When should this skill be used?
- What triggers should activate this skill?
- Is it mandatory or optional?
- Should it be proactively suggested?

### Question 3: What tools/commands does it need?
- Shell scripts?
- Python scripts?
- Node.js dependencies?
- External CLI tools?
- Environment variables?

### Question 4: How will you test compliance?
- What are the success criteria?
- What are common violations?
- Do you need pressure tests?

---

## Step 3: Create the Skill Directory

```bash
# Create the skill directory in arsenal
mkdir -p arsenal/dot-claude/skills/YOUR_SKILL_NAME

# Create the main SKILL.md file
touch arsenal/dot-claude/skills/YOUR_SKILL_NAME/SKILL.md
```

**Naming conventions:**
- Use lowercase with hyphens: `test-writer`, `git-reader`, `skill-writer`
- Be specific and action-oriented: `update-langfuse-staging-server-prompt` not just `langfuse`
- Avoid generic names: prefer `playwright-tester` over `browser`

---

## Step 4: Write the SKILL.md

### Template Structure

```markdown
---
name: your-skill-name
description: One-line description (appears in skill lists)
---

# your-skill-name Skill

## 🎯 Purpose

Explain what this skill does and why it exists.

**Use this skill when:**
- Trigger condition 1
- Trigger condition 2
- Trigger condition 3

---

## Step 1: [First Major Step]

Clear, actionable instructions.

### Substep 1.1: [Specific Action]

```bash
# Command example
command --flag value
```

**Expected output:**
```
Show what success looks like
```

---

## Step 2: [Second Major Step]

Continue with clear steps...

---

## Common Violations

Document what NOT to do:
- ❌ **BANNED:** Specific anti-pattern to avoid
- ❌ **CRITICAL:** Another violation with explanation
- ✅ **CORRECT:** Show the right way

---

## Troubleshooting

**Problem:** Common error message
**Cause:** Why this happens
**Solution:** How to fix it

---

## Success Criteria

You've completed this skill when:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
```

### Writing Guidelines

**DO:**
- ✅ Use clear, imperative language ("Run this command", "Check the output")
- ✅ Provide copy-pasteable commands
- ✅ Show expected output
- ✅ Include troubleshooting sections
- ✅ Use emojis for visual hierarchy (🎯 🚨 ✅ ❌)
- ✅ Mark mandatory vs optional steps clearly
- ✅ Provide examples of when to use the skill

**DON'T:**
- ❌ Be vague or hand-wavy ("configure appropriately")
- ❌ Assume knowledge ("as you know...")
- ❌ Skip error cases
- ❌ Forget edge cases
- ❌ Make skills too long (split into multiple skills if needed)

---

## Step 5: Add Supporting Files (Optional)

### Shell Scripts

If your skill needs automation:

```bash
# Create scripts directory
mkdir -p arsenal/dot-claude/skills/YOUR_SKILL_NAME/scripts

# Create script
cat > arsenal/dot-claude/skills/YOUR_SKILL_NAME/scripts/run_task.sh << 'EOF'
#!/bin/bash
set -e

echo "Running task..."
# Your commands here
EOF

# Make executable
chmod +x arsenal/dot-claude/skills/YOUR_SKILL_NAME/scripts/run_task.sh
```

### Python Scripts

```bash
cat > arsenal/dot-claude/skills/YOUR_SKILL_NAME/scripts/helper.py << 'EOF'
#!/usr/bin/env python3
"""Helper script for YOUR_SKILL_NAME skill."""
import sys

def main():
    print("Helper running...")
    # Your code here

if __name__ == "__main__":
    main()
EOF

chmod +x arsenal/dot-claude/skills/YOUR_SKILL_NAME/scripts/helper.py
```

### Node.js Dependencies

If your skill needs Node packages:

```bash
cd arsenal/dot-claude/skills/YOUR_SKILL_NAME

# Create package.json
cat > package.json << 'EOF'
{
  "name": "your-skill-name",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "some-package": "^1.0.0"
  }
}
EOF

# Install dependencies (install.sh will do this automatically)
npm install
```

**Note:** The install script automatically runs `npm install` for any skill with a `package.json`.

---

## Step 6: Test Your Skill

### Manual Testing

```bash
# 1. Sync to .claude directory
./arsenal/install.sh

# 2. Verify it appears in skill list
ls .claude/skills/

# 3. Read the skill as Claude would
cat .claude/skills/YOUR_SKILL_NAME/SKILL.md

# 4. Test any scripts
.claude/skills/YOUR_SKILL_NAME/scripts/run_task.sh

# 5. Start a new Claude Code session and use the skill
# The skill should be available via the Skill tool
```

### Automated Testing (Optional)

Create pressure tests to verify compliance:

```bash
cat > arsenal/dot-claude/skills/YOUR_SKILL_NAME/PRESSURE_TESTS.md << 'EOF'
# Pressure Tests for YOUR_SKILL_NAME

## Test 1: [Scenario Name]

**Setup:**
- Condition 1
- Condition 2

**Expected Behavior:**
- Agent should do X
- Agent should NOT do Y

**Violation:**
- If agent does Z, test fails

---

## Test 2: [Another Scenario]

...
EOF
```

---

## Step 7: Document in CLAUDE.md

After creating your skill, add it to the skill registry in `arsenal/system-prompts/CLAUDE.md`:

```markdown
### your-skill-name
**Description of what it does**

When to use: [Trigger conditions]
Where: `.claude/skills/your-skill-name/SKILL.md`

**Example queries where you MUST run your-skill-name:** "Example 1" • "Example 2" • "Example 3"

**YOU MUST:**
- Step 1
- Step 2
- Step 3

**Violations:**
- ❌ Anti-pattern 1
- ❌ Anti-pattern 2
```

Then sync to project root:

```bash
./arsenal/install.sh
```

---

## Step 8: Commit to Arsenal

Skills are part of the arsenal repository, so commit them properly:

```bash
# Stage your changes
git add arsenal/dot-claude/skills/YOUR_SKILL_NAME/
git add arsenal/system-prompts/CLAUDE.md  # If you updated it

# Commit with descriptive message
git commit -m "Add YOUR_SKILL_NAME skill for [purpose]

- Provides [key benefit 1]
- Prevents [common mistake]
- Includes [scripts/automation/etc]"

# Push to arsenal (if it's a separate repo)
cd arsenal
git push
cd ..
```

---

## Editing Existing Skills

### Workflow

```bash
# 1. Edit the skill in arsenal (source of truth)
vim arsenal/dot-claude/skills/EXISTING_SKILL/SKILL.md

# 2. Sync changes to .claude
./arsenal/install.sh

# 3. Test the changes
cat .claude/skills/EXISTING_SKILL/SKILL.md

# 4. Commit to arsenal
git add arsenal/dot-claude/skills/EXISTING_SKILL/
git commit -m "Update EXISTING_SKILL: [what changed]"
```

### Common Edits

**Adding a new step:**
- Insert it in the SKILL.md with clear numbering
- Update any "Success Criteria" checklists
- Test that the new step works

**Fixing a command:**
- Update the command in SKILL.md
- Test it works as expected
- Document in commit message what was broken and how you fixed it

**Adding examples:**
- Add to "Example queries" section
- Show both good and bad patterns
- Link to real code if relevant

---

## Best Practices

### Make Skills Mandatory, Not Optional

**Good:**
```markdown
**YOU MUST use this skill when:**
- Writing any test code
- BEFORE writing `def test_*`
```

**Bad:**
```markdown
**You might want to consider using this skill if:**
- You feel like it
```

### Provide Clear Success Criteria

**Good:**
```markdown
## Success Criteria

You've completed this skill when:
- [ ] All tests in `just test-all-mocked` pass
- [ ] Output shows "✓ 42 passed"
- [ ] No error messages in output
```

**Bad:**
```markdown
You're done when things work.
```

### Show Expected Output

**Good:**
```markdown
Run the command:
```bash
just test-unit
```

**Expected output:**
```
============================= test session starts ==============================
collected 42 items

tests/unit/test_foo.py ..................                            [ 42%]
tests/unit/test_bar.py ........................                       [100%]

============================== 42 passed in 2.31s ===============================
```
```

**Bad:**
```markdown
Run `just test-unit` and check if it works.
```

### Document Common Violations

Every skill should have a "Violations" or "Common Mistakes" section:

```markdown
## Common Violations

- ❌ **BANNED:** Running tests without `just ruff` first
  - **Why:** Formatting errors cause test failures
  - **Fix:** Always run `just ruff` before testing

- ❌ **CRITICAL:** Saying "all tests pass" without running parallel suite
  - **Why:** Misleads user about code quality
  - **Fix:** Run `.claude/skills/test-runner/scripts/run_tests_parallel.sh`
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Editing .claude Directly

**WRONG:**
```bash
# ❌ DON'T DO THIS
vim .claude/skills/test-writer/SKILL.md
git add .claude/
```

**RIGHT:**
```bash
# ✅ DO THIS
vim arsenal/dot-claude/skills/test-writer/SKILL.md
./arsenal/install.sh
git add arsenal/
```

**Why:** `.claude/` is a copy created by install.sh. Changes will be overwritten.

### Anti-Pattern 2: Creating Skills in Project Root

**WRONG:**
```bash
# ❌ DON'T DO THIS
mkdir .claude/skills/my-new-skill
```

**RIGHT:**
```bash
# ✅ DO THIS
mkdir arsenal/dot-claude/skills/my-new-skill
./arsenal/install.sh
```

### Anti-Pattern 3: Vague Trigger Conditions

**WRONG:**
```markdown
Use this skill when you need to test stuff.
```

**RIGHT:**
```markdown
Use this skill when:
- ✅ User asks "write tests for X"
- ✅ You're creating a new `test_*.py` file
- ✅ You're about to write `def test_*`
- ✅ User says "add test coverage"
```

### Anti-Pattern 4: Missing Automation

If users run the same commands repeatedly, create a script:

**WRONG:**
```markdown
1. Run `cd api && just lint-and-fix`
2. Run `cd api && just test-all-mocked`
3. Check all outputs for failures
```

**RIGHT:**
```markdown
1. Run the automated script:
```bash
.claude/skills/test-runner/scripts/run_tests_parallel.sh
```

2. Check the log files for results:
```bash
cat test-results/*.log
```
```

---

## Skill Lifecycle

### Development Cycle

```
1. Identify need
   ↓
2. Create skill in arsenal/dot-claude/skills/
   ↓
3. Run ./arsenal/install.sh
   ↓
4. Test skill manually
   ↓
5. Refine based on testing
   ↓
6. Add to CLAUDE.md skill registry
   ↓
7. Run ./arsenal/install.sh again
   ↓
8. Commit to arsenal
```

### Update Cycle

```
1. Edit skill in arsenal/dot-claude/skills/
   ↓
2. Run ./arsenal/install.sh
   ↓
3. Test changes
   ↓
4. Commit to arsenal
```

---

## Environment Configuration

Some skills need environment variables. Handle them properly:

### Create .env.example in Skill Directory

```bash
cat > arsenal/dot-claude/skills/YOUR_SKILL_NAME/.env.example << 'EOF'
# Environment variables for YOUR_SKILL_NAME skill
API_KEY=your-api-key-here
API_ENDPOINT=https://api.example.com
EOF
```

### Document in SKILL.md

```markdown
## Setup

### Environment Variables

Create a `.env` file in the skill directory:

```bash
cp .claude/skills/YOUR_SKILL_NAME/.env.example .claude/skills/YOUR_SKILL_NAME/.env
```

Edit `.env` and add your credentials:
```
API_KEY=sk-your-real-key
API_ENDPOINT=https://api.example.com
```

**Security:** Never commit real API keys to git!
```

### Load Environment in Scripts

```bash
#!/bin/bash
set -e

# Load environment variables
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$SKILL_DIR/.env" ]; then
    set -a
    source "$SKILL_DIR/.env"
    set +a
fi

# Your script logic here
```

---

## Self-Improvement Loop: Learning from Experience

**Core Principle:** Skills should evolve based on real-world usage. You can improve yourself by reading, thinking, and writing down what you learned.

### When to Improve Skills

Improve a skill when you observe:
1. **Repeated violations** - You or other agents keep making the same mistake
2. **New edge cases** - A scenario the skill doesn't cover
3. **Unclear instructions** - You had to guess or ask for clarification
4. **Missing automation** - You ran the same commands manually multiple times
5. **User confusion** - User asks "why did you do X?" and the skill doesn't explain it

### The Self-Improvement Workflow

```
1. Observe a pattern or problem
   ↓
2. Read the relevant skill
   ↓
3. Think about what's missing or unclear
   ↓
4. Write down the improvement
   ↓
5. Test the improved skill
   ↓
6. Commit the improvement to arsenal
```

### Pattern 1: Learning from Violations

**When you catch yourself (or observe another agent) violating a skill:**

```bash
# 1. Document what happened
# Create a file or note describing the violation
cat > /tmp/violation_note.md << 'EOF'
## Violation Observed
- **Skill:** test-writer
- **What happened:** Started writing tests without reading the skill
- **Why:** User said "write tests" and I jumped straight to code
- **Consequence:** Wrote brittle tests with hardcoded outputs
EOF

# 2. Read the skill to understand what should have happened
cat .claude/skills/test-writer/SKILL.md

# 3. Think: What would have prevented this?
# - Clearer trigger conditions?
# - Stronger "BANNED" language?
# - More examples of when to use?

# 4. Improve the skill in arsenal
vim arsenal/dot-claude/skills/test-writer/SKILL.md
# Add: "❌ BANNED: Writing tests without reading test-writer skill first"
# Add: More trigger examples

# 5. Sync and test
./arsenal/install.sh
cat .claude/skills/test-writer/SKILL.md | grep -A 5 "BANNED"

# 6. Commit
git add arsenal/dot-claude/skills/test-writer/SKILL.md
git commit -m "Strengthen test-writer: add explicit trigger for 'write tests' query"
```

### Pattern 2: Extracting Lessons from Past Conversations

**When you notice recurring patterns or learn something new:**

```markdown
## Example: Learning from a Debug Session

**Observation:**
User asked "Why didn't this intervention fire?" I read code and explained the logic,
but was wrong. The actual reason (found later in Langfuse traces) was different.

**Lesson:**
Production debugging requires actual data, not code reading.

**Action:**
1. Read langfuse-prompt-and-trace-debugger skill
2. Identify gap: No guidance on "when code reading is insufficient"
3. Add pressure test: "Production Debugging Without Data"
4. Add to skill: "Code shows what SHOULD happen. Traces show what DID happen."
```

**Implementation:**

```bash
# Edit the skill in arsenal
vim arsenal/dot-claude/skills/langfuse-prompt-and-trace-debugger/SKILL.md

# Add new section
cat >> arsenal/dot-claude/skills/langfuse-prompt-and-trace-debugger/SKILL.md << 'EOF'

## When Code Reading Is Insufficient

❌ **WRONG:** "Let me read the intervention logic to explain why it didn't fire..."
✅ **RIGHT:** "Let me fetch the actual trace to see what happened in production..."

**Why:**
- Code shows intent (what should happen)
- Traces show reality (what did happen)
- Reality often differs due to: null values, timing, errors, config mismatches
EOF

# Sync and commit
./arsenal/install.sh
git add arsenal/dot-claude/skills/langfuse-prompt-and-trace-debugger/
git commit -m "Add guidance: code vs traces for production debugging"
```

### Pattern 3: Creating New Skills from Discovered Patterns

**When you notice you're doing the same task repeatedly without a skill:**

```markdown
## Example: Repeated Database Migration Pattern

**Observation:**
Over 5 conversations, you ran similar commands:
1. Check current migration: `alembic current`
2. Generate migration: `alembic revision --autogenerate -m "..."`
3. Review migration: `cat alembic/versions/XXXX_*.py`
4. Apply migration: `alembic upgrade head`
5. Verify: `alembic current`

**Pattern Recognition:**
This is a repeated workflow that could be a skill.

**Action:**
Create database-migration-runner skill.
```

**Implementation:**

```bash
# 1. Create skill directory
mkdir -p arsenal/dot-claude/skills/database-migration-runner

# 2. Create SKILL.md
cat > arsenal/dot-claude/skills/database-migration-runner/SKILL.md << 'EOF'
---
name: database-migration-runner
description: Safe workflow for generating and applying Alembic database migrations
---

# database-migration-runner Skill

## Purpose
Provides a safe, tested workflow for database schema changes.

## When to Use
- User asks to "create migration" or "update database schema"
- Models in `api/src/models/` have changed
- New tables or columns needed

## Workflow

### Step 1: Check Current State
```bash
cd api
alembic current
```

### Step 2: Generate Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Step 3: Review Generated Migration
```bash
# Find the newest migration file
ls -t alembic/versions/ | head -1
cat alembic/versions/XXXX_*.py

# Check for:
- Correct table/column changes
- No accidental drops
- Proper indexes
```

### Step 4: Apply Migration
```bash
alembic upgrade head
```

### Step 5: Verify
```bash
alembic current  # Should show new migration
```

## Violations
- ❌ Applying migrations without reviewing
- ❌ Not checking current state first
- ❌ Assuming autogenerate is always correct
EOF

# 3. Create automation script
mkdir -p arsenal/dot-claude/skills/database-migration-runner/scripts
cat > arsenal/dot-claude/skills/database-migration-runner/scripts/safe_migrate.sh << 'EOF'
#!/bin/bash
set -e

echo "Step 1: Current state"
alembic current

echo -e "\nStep 2: Generating migration"
alembic revision --autogenerate -m "$1"

LATEST=$(ls -t alembic/versions/*.py | head -1)
echo -e "\nStep 3: Review generated migration"
echo "File: $LATEST"
cat "$LATEST"

read -p "Apply this migration? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\nStep 4: Applying migration"
    alembic upgrade head

    echo -e "\nStep 5: Verification"
    alembic current
    echo "✓ Migration applied successfully"
else
    echo "Migration not applied. Review and apply manually."
fi
EOF
chmod +x arsenal/dot-claude/skills/database-migration-runner/scripts/safe_migrate.sh

# 4. Sync to .claude
./arsenal/install.sh

# 5. Update CLAUDE.md skill registry
vim arsenal/system-prompts/CLAUDE.md
# Add database-migration-runner to skill list

# 6. Commit
git add arsenal/dot-claude/skills/database-migration-runner/
git add arsenal/system-prompts/CLAUDE.md
git commit -m "Add database-migration-runner skill from repeated pattern"
```

### Pattern 4: Mining Past Conversations

**When user provides conversation history or logs:**

```bash
# User says: "Here are my last 50 Claude conversations. Find patterns we should codify."

# 1. Analyze for repeated questions
grep -h "^user:" conversations/*.md | sort | uniq -c | sort -rn | head -20

# 2. Analyze for repeated commands
grep -h "```bash" conversations/*.md | sed 's/```bash//' | sort | uniq -c | sort -rn

# 3. Identify skill gaps
# Look for:
# - Questions you answered multiple times (→ skill or documentation)
# - Commands run repeatedly (→ automation script)
# - Mistakes made multiple times (→ stronger BANNED section)
# - Edge cases not covered (→ add to existing skill)

# 4. Extract top 5 lessons
cat > /tmp/lessons_learned.md << 'EOF'
## Lessons from Past 50 Conversations

1. **Repeatedly forgot to run install.sh after editing arsenal**
   → Add to skill-writer: explicit reminder in workflow

2. **Multiple times: edited .claude/ directly when urgent**
   → Add pressure test: "Direct Edit Temptation"

3. **Often guessed at Langfuse schemas instead of fetching**
   → Strengthen langfuse skill: make fetching mandatory

4. **Several times: said "tests pass" without running full suite**
   → Already covered in test-runner, but needs emphasis

5. **Pattern: database migrations done manually 10+ times**
   → Create database-migration-runner skill
EOF

# 5. Implement top improvements
# Process each lesson using the patterns above
```

### Pattern 5: Iterative Skill Improvement

**Skills should evolve through multiple iterations:**

```markdown
## Example: test-writer Skill Evolution

### Version 1 (Initial)
- Basic structure: "Follow these steps when writing tests"
- Problem: Agents still wrote brittle tests

### Version 2 (After violations observed)
- Added: "❌ BANNED: Hardcoding library outputs"
- Added: Examples of brittle vs robust tests
- Result: Fewer brittle tests, but fixture misuse increased

### Version 3 (After fixture problems)
- Added: "Fixture Decision Tree: When to use vs when to inline"
- Added: Factory pattern examples
- Result: Better fixtures, but still testing library behavior

### Version 4 (After contract confusion)
- Added: "The Golden Rule: What business requirement does this test protect?"
- Added: Contract vs implementation testing examples
- Result: Tests now focus on contracts

### Version 5 (After modification issues)
- Added: "TEST CONTRACT CHANGED:" mandatory format
- Added: Guidance on code broke vs contract changed
- Result: Test modifications are now explicit and justified
```

**Implementation of iterative improvement:**

```bash
# After each violation or learning, update the skill
vim arsenal/dot-claude/skills/test-writer/SKILL.md
# Add learned lesson to appropriate section

./arsenal/install.sh

# Document what changed
git add arsenal/dot-claude/skills/test-writer/SKILL.md
git commit -m "test-writer v5: add TEST CONTRACT CHANGED format

Observed agents modifying test assertions to make broken code pass.
Added mandatory format that forces explicit justification.
Prevents the #1 cardinal sin: weakening tests to hide bugs."
```

### Success Metrics for Self-Improvement

**You're successfully self-improving when:**

1. **Violations decrease** - Same mistake isn't repeated across conversations
2. **Skills get more specific** - Vague "be careful" becomes specific "❌ BANNED: X"
3. **Automation increases** - Manual commands become scripts
4. **Coverage expands** - Edge cases get documented after you encounter them
5. **Clarity improves** - Users ask fewer clarifying questions about what to do

### Anti-Patterns in Self-Improvement

**❌ DON'T:**
- Add improvements to `.claude/` (use arsenal)
- Make skills longer without making them clearer
- Add every edge case (focus on common patterns)
- Improve based on one incident (wait for patterns)
- Skip testing improved skills

**✅ DO:**
- Edit arsenal, sync with install.sh
- Make skills more specific and actionable
- Focus on violations that repeat 3+ times
- Extract generalizable lessons from specific incidents
- Test improved skills on realistic scenarios

---

## Success Criteria

You've mastered skill development when:

- [ ] You understand that arsenal/dot-claude is the source of truth
- [ ] You know how to create a new skill directory
- [ ] You can write a clear SKILL.md with steps and examples
- [ ] You know when to add scripts vs inline commands
- [ ] You run ./arsenal/install.sh after every change
- [ ] You test skills before committing
- [ ] You document skills in CLAUDE.md
- [ ] You commit changes to arsenal, not .claude

---

## Quick Reference

```bash
# Create new skill
mkdir -p arsenal/dot-claude/skills/SKILL_NAME
vim arsenal/dot-claude/skills/SKILL_NAME/SKILL.md

# Edit existing skill
vim arsenal/dot-claude/skills/EXISTING_SKILL/SKILL.md

# Sync to .claude
./arsenal/install.sh

# Test skill
cat .claude/skills/SKILL_NAME/SKILL.md
ls .claude/skills/

# Commit to arsenal
git add arsenal/dot-claude/skills/SKILL_NAME/
git commit -m "Add/Update SKILL_NAME skill"
```

---

## Related Skills

- **getting-started**: Learn how to discover and use skills
- **test-writer**: Example of a well-structured mandatory skill
- **test-runner**: Example of a skill with automation scripts

---

## Troubleshooting

### Skill doesn't appear after install.sh

**Cause:** Skill directory or SKILL.md missing
**Solution:**
```bash
# Check skill exists in arsenal
ls arsenal/dot-claude/skills/YOUR_SKILL_NAME/

# Check SKILL.md exists
ls arsenal/dot-claude/skills/YOUR_SKILL_NAME/SKILL.md

# Re-run install
./arsenal/install.sh

# Verify in .claude
ls .claude/skills/YOUR_SKILL_NAME/
```

### Changes not appearing in .claude

**Cause:** Edited .claude directly instead of arsenal
**Solution:**
```bash
# Discard .claude changes (it's a copy)
rm -rf .claude/skills/YOUR_SKILL_NAME

# Re-run install to restore from arsenal
./arsenal/install.sh
```

### npm install fails during install.sh

**Cause:** Invalid package.json or missing npm
**Solution:**
```bash
# Check package.json syntax
cat arsenal/dot-claude/skills/YOUR_SKILL_NAME/package.json | jq .

# Install dependencies manually
cd arsenal/dot-claude/skills/YOUR_SKILL_NAME
npm install

# Re-run install.sh
cd /path/to/project
./arsenal/install.sh
```
