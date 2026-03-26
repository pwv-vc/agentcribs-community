---
name: multi-model-review
description: "INVOKE when reviewing PRs, designs, or architecture decisions where a single perspective isn't enough. Orchestrates Claude + Codex CLI for adversarial multi-model review with structured synthesis."
---

# Multi-Model Review

Get two AI models to review the same artifact independently, then synthesize their findings. Two models from different providers catch what one model alone misses - they have different training data, different blind spots, and different instincts about what matters.

## When to Use

- PR with significant scope, security implications, or tricky logic
- Design doc or spec before committing to implementation
- Architecture decision with real tradeoffs
- Any artifact where "one model said it looks good" isn't enough confidence
- Post-mortem analysis where you want multiple perspectives on root cause

**When NOT to use:** Typo fixes, dependency bumps, trivial config changes. Don't burn tokens on ceremony.

## Prerequisites

- **Claude Code** (you're already here)
- **Codex CLI** installed and configured (`codex` command available)
  - Install: `npm install -g @openai/codex`
  - Or substitute any second model CLI (Gemini CLI, etc.)

## Workflow

### Step 1: Prepare the Artifact

Identify what's being reviewed and capture it as a diffable artifact:

```bash
# For a PR or staged changes:
git diff main > /tmp/review-diff.txt

# For a design doc:
# Just reference the file path directly

# For architecture decisions:
# Reference the ADR or design doc path
```

### Step 2: Run Claude Review (You)

You ARE Claude. Perform your review first. Assess across these dimensions - skip any that don't apply:

| Dimension | What to look for |
|-----------|-----------------|
| **Correctness** | Logic errors, off-by-ones, race conditions, wrong assumptions |
| **Completeness** | Missing error handling, untested paths, undocumented behavior |
| **Edge cases** | Unusual inputs, empty states, concurrent access, boundary values |
| **Security** | Injection, auth gaps, secret exposure, unsafe deserialization |
| **Performance** | N+1 queries, unnecessary allocations, missing indexes, blocking I/O |
| **Maintainability** | Unclear naming, hidden coupling, missing abstractions, future footguns |

Write your findings as a structured list with severity ratings:

- **Critical** - must fix before merge, causes data loss/security hole/crash
- **High** - should fix before merge, causes incorrect behavior or significant tech debt
- **Medium** - fix soon, quality/maintainability concern
- **Low** - nice to have, style or minor improvement

Save your review:

```bash
cat > /tmp/claude-review.md << 'EOF'
## Claude Review

### Findings
- **[severity]** finding description
  - Concrete scenario: what goes wrong and when
  - Suggestion: how to fix it

### What Looks Good
- (genuinely good patterns worth calling out)
EOF
```

### Step 3: Run Codex Review (Background Agent)

Spawn Codex CLI to review the same artifact independently. The key is that Codex hasn't seen your review - it brings fresh eyes.

```bash
# For code changes:
codex -q --full-auto "Review this diff for bugs, security issues, edge cases, and maintainability concerns. Be specific - every finding needs a concrete scenario showing what goes wrong. Rate each finding as critical/high/medium/low severity. Also note what looks good. Diff: $(cat /tmp/review-diff.txt)" > /tmp/codex-review.md

# For a design doc:
codex -q --full-auto "Review this design doc for completeness, edge cases, and feasibility. Be specific about what could go wrong. Rate findings by severity. File: $(cat path/to/design.md)" > /tmp/codex-review.md
```

**If Codex CLI isn't available**, you can substitute:
- Gemini CLI: `gemini -p "..." > /tmp/gemini-review.md`
- Any other model CLI
- Or skip to single-model review (still follow the structured format above)

### Step 4: Synthesize

Read both reviews and produce a single synthesis. This is where the value compounds - you're looking for:

**Consensus** - Both models flagged the same issue. High confidence it's real.

**Divergence** - One model found something the other missed. Investigate - these are often the most valuable findings because they represent blind spots.

**Contradiction** - Models disagree about whether something is a problem. Document both positions with reasoning. Don't pick a winner - surface it for human decision.

**False positives** - Either model flagged something that isn't actually an issue. Note why it's not a real concern (prevents future reviewers from re-flagging).

### Step 5: Write the Synthesis Report

```markdown
## Multi-Model Review Synthesis

**Artifact:** <what was reviewed>
**Models:** Claude (Anthropic) + Codex (OpenAI)
**Date:** <date>

### Consensus (both models agree)
- **[severity]** <finding> - <concrete scenario>

### Unique to Claude
- **[severity]** <finding> - <why Codex may have missed this>

### Unique to Codex
- **[severity]** <finding> - <why Claude may have missed this>

### Contradictions
- <topic>: Claude says X, Codex says Y. <context for human to decide>

### False Positives Dismissed
- <finding that was flagged but isn't real> - <why>

### Summary
- Total findings: N (X critical, Y high, Z medium, W low)
- Consensus findings: N (highest confidence)
- Needs human decision: N contradictions
- Verdict: ready to merge / address criticals first / needs rework
```

## Tips

- **Independence matters.** Don't show Claude's review to Codex or vice versa. The value is in independent perspectives. If they converge independently, you have high confidence.
- **Concrete scenarios or it didn't happen.** "This could be a problem" is noise. "If two requests hit this endpoint simultaneously and neither has acquired the lock, rows X and Y can diverge" is signal.
- **Severity is about blast radius, not likelihood.** A rare event that corrupts the database is critical. A common annoyance users can work around is low.
- **Accepted risk is a valid outcome.** Not every finding needs a fix. Some risks are acknowledged. The value is making them explicit rather than invisible.
- **Don't review too early.** Running this on a half-finished PR just produces noise about things you already know are incomplete. Wait until the author thinks it's ready.
- **Track patterns across reviews.** If the same finding keeps appearing (e.g., "missing error handling on external API calls"), that's a systemic issue worth a codebase-wide fix, not a per-PR nit.

## Failure Modes to Avoid

- ❌ Running both reviews but ignoring the divergences (defeats the purpose)
- ❌ Treating consensus as "definitely correct" without thinking (both models can share blind spots)
- ❌ Spending 30 minutes reviewing a 3-line config change (match effort to risk)
- ❌ Using this as a gate on every PR (reserve for significant changes)
- ❌ Letting the synthesis be longer than both reviews combined (it should be shorter and sharper)
