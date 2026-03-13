---
description: Review proposals across directories, select best, improve, and save FINAL.md everywhere (project)
---

# PM Prioritize Command

**Purpose:** Review proposals from multiple project directories, select the best, improve it, and distribute a final version.

**Workflow:** Run AFTER `/pm-proposal-review` to prioritize across all reviewed proposals.

## Usage

```bash
# Review proposals across multiple projects
/pm-prioritize ~/Hacking/codel/ct6/docs/temp/proposals ~/Hacking/codel/ct5/docs/temp/proposals ~/Hacking/codel/ct7/docs/temp/proposals

# Review proposals in current project only
/pm-prioritize docs/temp/proposals

# Review with specific date filter
/pm-prioritize docs/temp/proposals --date 2025-11-18
```

## Workflow

### Step 1: Parse Directories

Accept 1 or more directory paths:
- If relative paths: resolve from current working directory
- If absolute paths: use as-is
- Validate each directory exists

### Step 2: Discover Proposals

For each directory:
```bash
# Find all proposal markdown files
find {directory} -name "*.md" -not -name "README.md" -not -name "FINAL.md"
```

List all proposals found:
```
Found 5 proposals:
- ct6/docs/temp/proposals/user-feedback-2025-11-18.md
- ct6/docs/temp/proposals/funnel-2025-11-17.md
- ct5/docs/temp/proposals/retention-2025-11-16.md
- ct7/docs/temp/proposals/user-feedback-2025-11-18.md
- ct7/docs/temp/proposals/onboarding-2025-11-15.md
```

### Step 3: Review Each Proposal

For each proposal, extract and analyze:

**1. Core content:**
- User Insight
- Infrastructure changes
- The Change
- User Outcome
- Priority (P0/P1/P2/P3)
- Effort (XS/S/M/L/XL)

**2. Existing PM Review (if present):**
- Data Support (Strong/Okay/Weak/Very Weak)
- Brittleness (Strong/Okay/Weak/Very Weak)
- Extensibility (Strong/Okay/Weak/Very Weak)

**3. Data validation using sql-reader:**
- Re-query database to verify data claims
- Check if metrics cited are still accurate
- Identify outdated or incorrect information

**4. Score proposal:**
```
Score = (Data Support × 4) + (Implementation Strength × 3) + (User Impact × 3)

Data Support:
- Strong = 4 points
- Okay = 3 points
- Weak = 2 points
- Very Weak = 1 point

Implementation Strength (brittleness inverted):
- Strong (non-brittle) = 4 points
- Okay = 3 points
- Weak (brittle) = 2 points
- Very Weak (very brittle) = 1 point

User Impact (from Priority + Effort):
- P0 + XS/S = 4 points
- P0 + M/L = 3 points
- P1 + XS/S/M = 3 points
- P1 + L/XL = 2 points
- P2+ = 1 point
```

### Step 4: Select Best Proposal

Rank proposals by score (highest first):
```
1. ct6/user-feedback-2025-11-18.md - Score: 11/10 (Strong data, Weak brittleness, P0/M)
2. ct7/user-feedback-2025-11-18.md - Score: 10/10 (Strong data, Weak brittleness, P0/M)
3. ct5/retention-2025-11-16.md - Score: 8/10 (Okay data, Okay brittleness, P1/S)
...
```

Select the highest-scoring proposal as the **base**.

If multiple proposals have the same score:
- Prefer the most recent (by date in filename)
- Prefer proposals with PM reviews already

### Step 5: Improve the Best Proposal

Take the best proposal and enhance it:

**1. Strengthen data support:**
- Add missing data validations
- Update metrics with latest numbers
- Clarify assumptions

**2. Address brittleness:**
- Add mitigation strategies from PM review
- Suggest graceful fallbacks
- Identify edge cases to handle

**3. Enhance extensibility:**
- Note future features this enables
- Suggest abstractions for flexibility

**4. Synthesize from other proposals:**
- If multiple proposals address same topic (e.g., "user-feedback"):
  - Merge unique insights
  - Combine data points
  - Take best implementation approach from each

**5. Update word count:**
- Keep ≤250 words for proposal body
- PM Review stays ≤75 words

### Step 6: Create FINAL.md

Format:
```markdown
# FINAL PROPOSAL: {Title}

**Date:** {YYYY-MM-DD}
**Priority:** {P0/P1/P2/P3}
**Effort:** {XS/S/M/L/XL}
**Source:** Synthesized from {list of source proposals}

## 1. User Insight

{Enhanced insight with data from all sources}

## 2. Infrastructure

{Refined infrastructure design addressing brittleness}

## 3. The Change

{Improved implementation description with mitigations}

## 4. User Outcome

{Enhanced outcome with realistic impact projections}

---

**Word count:** {N} words ✅

---

## PM REVIEW ({YYYY-MM-DD})

**Data Support:** {Strong/Okay/Weak/Very Weak} - {validation summary}

**Brittleness:** {Strong/Okay/Weak/Very Weak} - {key mitigations}

**Extensibility:** {Strong/Okay/Weak/Very Weak} - {future capabilities}

---

## IMPROVEMENTS MADE

**Strengths carried forward:**
- {Strength 1 from best proposal}
- {Strength 2 from another proposal}

**Weaknesses addressed:**
- {Weakness 1}: Added {mitigation}
- {Weakness 2}: Clarified {aspect}

**Synthesis notes:**
- Combined insights from {N} proposals
- Updated data as of {date}
- Addressed brittleness concerns from reviews
```

### Step 7: Distribute FINAL.md

Copy the exact same FINAL.md to all target directories:
```bash
cp FINAL.md {dir1}/FINAL.md
cp FINAL.md {dir2}/FINAL.md
cp FINAL.md {dir3}/FINAL.md
```

### Step 8: Output Summary

```
✅ Proposal review complete

📊 Reviewed: 5 proposals across 3 directories
🏆 Best: ct6/user-feedback-2025-11-18.md (Score: 11/10)

💡 Improvements made:
- Strengthened data support (added validation for 3 claims)
- Addressed brittleness (added fallback logic, ML-based detection)
- Enhanced extensibility (noted 4 future features enabled)
- Synthesized insights from 2 user-feedback proposals

📄 FINAL.md distributed to:
- ~/Hacking/codel/ct6/docs/temp/proposals/FINAL.md
- ~/Hacking/codel/ct5/docs/temp/proposals/FINAL.md
- ~/Hacking/codel/ct7/docs/temp/proposals/FINAL.md
```

## Example Usage

### Example 1: Review Across Multiple Projects

```bash
$ /pm-prioritize ~/Hacking/codel/ct{5,6,7}/docs/temp/proposals

Discovering proposals...
✓ Found 5 proposals across 3 directories

Reviewing proposals...
[1/5] ct6/user-feedback-2025-11-18.md
  - Data: Strong (validated with sql-reader)
  - Brittleness: Weak (pattern matching issues)
  - Score: 11/10

[2/5] ct7/user-feedback-2025-11-18.md
  - Data: Strong (similar to ct6)
  - Brittleness: Weak (same issues)
  - Score: 10/10

[3/5] ct5/retention-2025-11-16.md
  - Data: Okay (some assumptions not validated)
  - Brittleness: Okay (moderate risks)
  - Score: 8/10

Best proposal: ct6/user-feedback-2025-11-18.md

Improving proposal...
- Strengthened data: Added baseline metrics
- Addressed brittleness: Added ML-based detection
- Synthesized from: ct6 + ct7 user-feedback proposals

Creating FINAL.md...
Distributing to 3 directories...

✅ FINAL.md created and distributed
```

### Example 2: Review Single Directory

```bash
$ /pm-prioritize docs/temp/proposals

Discovering proposals...
✓ Found 2 proposals in docs/temp/proposals

Reviewing proposals...
[1/2] user-feedback-2025-11-18.md - Score: 11/10
[2/2] funnel-2025-11-17.md - Score: 7/10

Best proposal: user-feedback-2025-11-18.md

Improving proposal...
- Strengthened data support
- Addressed brittleness concerns

Creating FINAL.md...
Distributing to 1 directory...

✅ FINAL.md created at docs/temp/proposals/FINAL.md
```

## Configuration

### Options

- `--date YYYY-MM-DD`: Only review proposals from specific date
- `--topic TOPIC`: Only review proposals matching topic (e.g., "user-feedback")
- `--min-score N`: Only consider proposals with score ≥ N
- `--no-improve`: Just select best, don't improve
- `--dry-run`: Show what would be selected, don't create FINAL.md

### Environment Variables

```bash
export PROPOSAL_REVIEW_AUTO_VALIDATE=true  # Auto-validate data with sql-reader
export PROPOSAL_REVIEW_VERBOSE=true        # Show detailed scoring
```

## Skills Used

1. **sql-reader** - Validate data claims in proposals
2. **File operations** - Read proposals, write FINAL.md

## Notes

- FINAL.md is identical in all directories (exact copy)
- Original proposals are preserved (not modified)
- If FINAL.md exists, it will be overwritten
- Proposals are compared objectively based on data, implementation, and impact
- Improvement focuses on addressing weaknesses while preserving strengths
- Synthesis combines unique insights from multiple proposals on same topic
