---
description: Select best engineering spec, improve it, and distribute as FINAL_SPEC.md everywhere (project)
---

# Engineering Prioritize Command

**Purpose:** Review specs across multiple project directories, select the best one based on engineering criteria, improve it, and distribute a final version everywhere.

**Workflow:** Run AFTER `/eng-spec-review` adds engineering reviews to all specs.

## Usage

```bash
# Prioritize specs across multiple projects
/eng-prioritize ~/Hacking/codel/ct{5,6,7,8}/docs/temp/specs

# Prioritize specs in current project only
/eng-prioritize docs/temp/specs

# Filter by date
/eng-prioritize docs/temp/specs --date 2025-11-18
```

## Workflow

**🚨 CRITICAL: Work completely autonomously. DO NOT ask questions. DO NOT explain the workflow. Just execute it.**

### Step 1: Parse Directories

**Execute immediately (DO NOT ASK):**

Accept directory paths from user's command argument:
- If relative paths: resolve from current working directory
- If absolute paths: use as-is
- Validate each directory exists using Bash
- If directory doesn't exist: Report error "Directory not found: {path}" and skip it
- Proceed immediately to Step 2 with valid directories

### Step 2: Discover Specs

**Execute immediately (DO NOT ASK):**

For each valid directory, find all spec markdown files:
```bash
find {directory} -name "*.md" -not -name "README.md" -not -name "FINAL_SPEC.md"
```

Announce what you found:
```
Found 5 specs:
- ct6/docs/temp/specs/user-retention-2025-11-18.md
- ct6/docs/temp/specs/onboarding-flow-2025-11-17.md
- ct5/docs/temp/specs/user-retention-2025-11-18.md
- ct7/docs/temp/specs/user-retention-2025-11-18.md
- ct8/docs/temp/specs/message-templates-2025-11-15.md
```

If no specs found: Report "No specs found in provided directories" and exit.

Proceed immediately to Step 3.

### Step 3: Review Each Spec

For each spec, extract and analyze:

**1. Core content:**
- Overview and problem statement
- Requirements (functional and non-functional)
- Architecture design
- API and database changes
- Implementation plan
- Testing strategy
- Risk assessment
- Rollout plan
- Priority (P0/P1/P2/P3)
- Effort estimate (XS/S/M/L/XL)

**2. Engineering Review (if present):**
- Feasibility (High/Medium/Low)
- Complexity (Low/Medium/High/Very High with X/20 score)
- Risk Level (High/Medium/Low)
- Effort Validation
- Recommendation

**3. Score the spec:**

```
Score = (Feasibility × 4) + (Simplicity × 3) + (Safety × 3) + (Code Quality × 3)

Feasibility (from review):
- High = 4 points
- Medium = 3 points
- Low = 2 points
- No review = 2 points (assume medium)

Simplicity (inverse of complexity):
- Low complexity (5-8/20) = 4 points
- Medium complexity (9-12/20) = 3 points
- High complexity (13-16/20) = 2 points
- Very high complexity (17-20/20) = 1 point
- No review = 2 points (assume medium)

Safety (inverse of risk):
- Low risk = 4 points
- Medium risk = 3 points
- High risk = 2 points
- No review = 2 points (assume medium)

Code Quality (implementation considerations):
- Excellent = 4 points (all criteria met)
- Good = 3 points (most criteria met)
- Fair = 2 points (some criteria met)
- Poor = 1 point (few criteria met)
- No review = 2 points (assume fair)

Max score: 15/13 (4+4+4+4-1 when adjusted for priority)
```

**Code Quality Criteria (in priority order):**

Evaluate the spec's proposed implementation against:

1. **LOC (Lines of Code):**
   - ✅ Concise & elegant approach vs overly verbose
   - ✅ Clean & readable without unnecessary code
   - ✅ Prefers "cutting corners" to simplify code and align user experiences
   - ✅ Interprets spec in ways that simplify implementation

2. **DRY (Don't Repeat Yourself):**
   - ✅ Reuses existing functions from codebase
   - ✅ Avoids duplicating logic that already exists
   - ✅ References specific existing code to reuse

3. **Non-defensive coding:**
   - ✅ Avoids try/except patterns unless truly necessary
   - ✅ Doesn't catch edge cases that never actually happen in logic
   - ✅ Lets errors surface instead of hiding them

4. **Regression analysis:**
   - ✅ Clear understanding of business logic changes
   - ✅ Documents how existing behavior will change
   - ✅ Identifies potential breaking changes

5. **Spec alignment:**
   - ✅ Implementation matches requirements exactly
   - ✅ No unnecessary features added beyond spec
   - ✅ All requirements addressed

6. **Test quality:**
   - ✅ Tests aligned with `docs/TEST_PATTERNS.md`
   - ✅ Tests follow patterns in `./tests/README.md`
   - ✅ Tests focus on business logic, not library behavior
   - ✅ Uses factory-style fixtures appropriately

**Scoring code quality:**
- **Excellent (4):** Meets all 6 criteria, exemplary code practices
- **Good (3):** Meets 4-5 criteria, minor improvements possible
- **Fair (2):** Meets 2-3 criteria, significant improvements needed
- **Poor (1):** Meets 0-1 criteria, major refactoring required

**Priority bonus:**
- P0: +1 point to final score
- P1: +0 points
- P2: -1 point
- P3: -2 points

### Step 4: Select Best Spec

Rank specs by score (highest first):

```
1. ct6/user-retention-2025-11-18.md - Score: 11/10
   Feasibility: High (4), Simplicity: Medium (3), Safety: High (4), Priority: P0 (+1)

2. ct7/user-retention-2025-11-18.md - Score: 10/10
   Feasibility: High (4), Simplicity: Medium (3), Safety: High (4), Priority: P1 (+0)

3. ct5/onboarding-flow-2025-11-17.md - Score: 8/10
   Feasibility: Medium (3), Simplicity: High (4), Safety: Medium (3), Priority: P1 (+0)
```

Select the highest-scoring spec as the **base**.

**Tie-breaking rules:**
If multiple specs have the same score:
1. Prefer higher feasibility (more likely to succeed)
2. Prefer lower complexity (easier to implement)
3. Prefer lower risk (safer deployment)
4. Prefer more recent date (latest thinking)
5. Prefer spec with engineering review (validated)

### Step 5: Improve the Best Spec

Take the best spec and enhance it by addressing weaknesses:

#### 5.1: Improve Code Quality

**If code quality is Fair or Poor:**
- Simplify the implementation approach
- Remove unnecessary abstraction layers
- Identify existing code to reuse (DRY)
- Eliminate defensive try/except patterns
- Clarify regression impacts
- Align tests with test patterns

**Example improvements:**
```markdown
## CODE QUALITY IMPROVEMENTS

**LOC Reduction:**
- Original: 5 new utility functions
- Simplified: Reuse existing `format_phone_number()` from `src/utils/phone.py`
- Original: Custom date parser (200 LOC)
- Simplified: Use built-in `datetime.fromisoformat()` (1 LOC)

**DRY Improvements:**
- Original: New timezone validation logic
- Improved: Reuse `validate_timezone()` from `src/utils/time.py:45`
- Original: Custom error handling for API calls
- Improved: Use existing `@retry_on_failure` decorator from `src/decorators.py`

**Non-defensive Coding:**
- Removed: `try/except` around database queries (let errors surface to monitoring)
- Removed: Edge case handling for "user has 1000+ facts" (never happens in prod)
- Kept: `try/except` for external Twilio API only (genuinely unreliable)

**Regression Analysis Added:**
- ✅ Change: Phone formatting now strips +1 prefix for US numbers
- ✅ Impact: Existing users with +1 stored will see different display format
- ✅ Breaking: API response format changes from "phoneNumber" to "phone"

**Test Improvements:**
- Removed: Tests for `phonenumbers` library behavior (not our code)
- Added: Tests for our `format_for_display()` contract
- Updated: Use `person_factory()` instead of hardcoded test data
- Aligned: All tests follow patterns in `tests/README.md`
```

#### 5.2: Address Feasibility Concerns

**If feasibility is Medium or Low:**
- Review feasibility assessment from engineering review
- Identify blocking issues
- Add mitigation strategies
- Consider alternative approaches
- Update architecture to address concerns

**Example improvements:**
```markdown
## FEASIBILITY IMPROVEMENTS

**Original concern:** Team lacks experience with Redis Streams
**Improvement:**
- Phase 1: Use simpler Redis lists first (team knows this)
- Phase 2: Migrate to Streams after proof-of-concept (2 weeks learning)
- Fallback: Stick with lists if Streams prove difficult

**Original concern:** External API rate limits too restrictive
**Improvement:**
- Add request batching (10 requests → 1 batch)
- Implement caching layer (reduces calls by 70%)
- Add fallback to degraded mode if rate limited
```

#### 5.3: Reduce Complexity

**If complexity is High or Very High:**
- Simplify the architecture
- Break into smaller phases
- Remove non-essential features from MVP
- Use simpler technologies
- Reduce number of integrations

**Example improvements:**
```markdown
## COMPLEXITY REDUCTIONS

**Original plan:** 5 new tables with complex relationships
**Simplified:**
- Phase 1: 2 core tables only
- Phase 2: Add 3 additional tables after core stabilizes
- Reduces initial complexity from 15/20 → 9/20

**Original plan:** Integrate 4 external services simultaneously
**Simplified:**
- Phase 1: Integrate 1 critical service only
- Phase 2: Add remaining services incrementally
- Reduces integration complexity, easier debugging
```

#### 5.4: Mitigate Risks

**If risk level is High or Medium:**
- Add mitigation strategies for top risks
- Implement circuit breakers
- Add comprehensive monitoring
- Create detailed rollback plan
- Add safety mechanisms

**Example improvements:**
```markdown
## RISK MITIGATIONS ADDED

**Risk:** Database migration could corrupt data
**Mitigation:**
- Add dry-run mode to test migration on copy of production DB
- Implement migration in reversible steps
- Add data validation after each step
- Maintain backup for 30 days

**Risk:** New cron jobs conflict with existing schedules
**Mitigation:**
- Use distributed locks (Redis) to prevent double-execution
- Stagger execution times (15-minute offset from existing jobs)
- Add monitoring for job conflicts
- Implement graceful degradation if lock acquisition fails
```

#### 5.5: Validate Effort Estimate

**Review the effort estimate:**
- Compare with complexity score
- Check against feasibility concerns
- Factor in risks and mitigations
- Adjust if improvements changed scope

**Effort calibration:**
- Very High complexity (17-20) + Low feasibility = XL (1+ month)
- High complexity (13-16) + Medium feasibility = L (2-4 weeks)
- Medium complexity (9-12) + High feasibility = M (1-2 weeks)
- Low complexity (5-8) + High feasibility = S (3-5 days)

Update effort if needed based on improvements.

#### 5.6: Synthesize from Other Specs

**If multiple specs address the same feature:**
- Compare approaches across specs
- Take best technical solutions from each
- Merge unique insights
- Combine risk mitigations
- Select most robust architecture

**Example synthesis:**
```markdown
## SYNTHESIS FROM MULTIPLE SPECS

**Best approach from ct6:** Redis-based queue for job distribution
**Best approach from ct7:** Distributed lock mechanism
**Best approach from ct5:** Comprehensive monitoring setup

**Combined approach:** Use ct7's lock mechanism + ct6's queue + ct5's monitoring
```

### Step 6: Create FINAL_SPEC.md

Format:

```markdown
# FINAL ENGINEERING SPECIFICATION: {Feature Name}

**Date:** {YYYY-MM-DD}
**Priority:** {P0/P1/P2/P3}
**Effort:** {Updated based on improvements}
**Source:** Selected from {N} specs, primary: {best spec file}

## Executive Summary

{1-2 sentence technical summary}

## Problem Statement

{What's being solved}

## Requirements

### Functional Requirements

1. **Requirement 1**
   - Acceptance criteria: {...}
   - Test scenario: {...}

### Non-Functional Requirements

- Performance: {...}
- Scalability: {...}
- Reliability: {...}
- Security: {...}

## Architecture

### Components

- Component 1: {Description}
- Component 2: {Description}

### Architecture Diagram

```
{ASCII diagram of system design}
```

### Design Decisions

**Decision 1: {Choice}**
- Options: {A, B, C}
- Selected: {X}
- Rationale: {Why}
- Trade-offs: {What we're giving up}

## API Changes

### New Endpoints

**POST /api/v1/{resource}**
```json
{Request/Response format}
```

### Modified Endpoints

{Changes to existing endpoints}

## Database Changes

### New Tables

```sql
CREATE TABLE ...
```

### Modified Tables

```sql
ALTER TABLE ...
```

### Data Migration

```python
def upgrade():
    # Migration steps
```

## Implementation Plan

### Phase 1: Foundation (Effort: {X})

**Tasks:**
1. Task 1
2. Task 2

**Acceptance:** {...}

### Phase 2: Core Logic (Effort: {Y})

**Tasks:**
1. Task 1
2. Task 2

**Acceptance:** {...}

### Phase 3: Polish & Deploy (Effort: {Z})

**Tasks:**
1. Task 1
2. Task 2

**Acceptance:** {...}

## Testing Strategy

### Unit Tests
{Key test cases}

### Integration Tests
{E2E workflows}

### Performance Tests
{Load testing approach}

## Risk Assessment

### High-Priority Risks

1. **Risk:** {Description}
   - Mitigation: {Strategy}

### Medium-Priority Risks

{List}

## Monitoring & Observability

### Metrics
- Metric 1: {Target}
- Metric 2: {Target}

### Alerts
- Alert 1: {Trigger and action}

## Rollout Plan

### Feature Flag
**Flag:** `enable_{feature}`

### Stages
1. Internal (0.1%)
2. Beta (5%)
3. Gradual (25% → 50% → 100%)

### Rollback Plan
{How to revert if needed}

---

## ENGINEERING REVIEW ({YYYY-MM-DD})

**Feasibility:** {High/Medium/Low} - {Summary}
**Complexity:** {Low/Medium/High/Very High} ({X}/20) - {Summary}
**Risk Level:** {High/Medium/Low} - {Summary}
**Effort Validation:** {Original} → {Final} - {Justification}
**Recommendation:** {Approve/Approve with Conditions}

---

## IMPROVEMENTS MADE

**Strengths Preserved:**
- {Strength 1 from best spec}
- {Strength 2 from another spec}

**Weaknesses Addressed:**
- {Weakness 1}: {How it was fixed}
- {Weakness 2}: {How it was fixed}

**Feasibility Improvements:**
- {Improvement 1}
- {Improvement 2}

**Complexity Reductions:**
- {Simplification 1}
- {Simplification 2}

**Risk Mitigations Added:**
- {Mitigation 1}
- {Mitigation 2}

**Synthesis Notes:**
- Combined best approaches from {N} specs
- Selected most feasible architecture
- Reduced complexity while preserving functionality
- Added comprehensive risk mitigations
```

### Step 7: Distribute FINAL_SPEC.md

Copy the exact same FINAL_SPEC.md to all target directories:

```bash
cp FINAL_SPEC.md {dir1}/FINAL_SPEC.md
cp FINAL_SPEC.md {dir2}/FINAL_SPEC.md
cp FINAL_SPEC.md {dir3}/FINAL_SPEC.md
cp FINAL_SPEC.md {dir4}/FINAL_SPEC.md
```

### Step 8: Output Summary

```
✅ Engineering prioritization complete

📊 Reviewed: {N} specs across {M} directories
🏆 Best: {spec file} (Score: {X}/10)

💡 Improvements made:
- Feasibility: {Key improvement}
- Complexity: {Key simplification}
- Risk: {Key mitigation}
- Synthesized insights from {N} specs

📄 FINAL_SPEC.md distributed to:
- ~/Hacking/codel/ct5/docs/temp/specs/FINAL_SPEC.md
- ~/Hacking/codel/ct6/docs/temp/specs/FINAL_SPEC.md
- ~/Hacking/codel/ct7/docs/temp/specs/FINAL_SPEC.md
- ~/Hacking/codel/ct8/docs/temp/specs/FINAL_SPEC.md

Next step: Run /spec-to-pr in each directory to generate PRs
```

## Example Usage

### Example: Prioritizing User Retention Specs

```bash
$ /eng-prioritize ~/Hacking/codel/ct{5,6,7,8}/docs/temp/specs

Discovering specs...
✓ Found 5 specs across 4 directories

Reviewing specs...

[1/5] ct6/user-retention-personalized-checkins-2025-11-18.md
  Engineering Review:
    - Feasibility: High (4 points)
    - Complexity: 12/20 (Medium) → Simplicity: 3 points
    - Risk: Medium (3 points)
    - Priority: P0 (+1 bonus)
  Score: 11/10 (4+3+3+1)

[2/5] ct7/user-retention-personalized-checkins-2025-11-18.md
  Engineering Review:
    - Feasibility: High (4 points)
    - Complexity: 14/20 (High) → Simplicity: 2 points
    - Risk: Medium (3 points)
    - Priority: P1 (+0 bonus)
  Score: 9/10 (4+2+3+0)

[3/5] ct5/user-retention-gamification-2025-11-17.md
  Engineering Review:
    - Feasibility: Medium (3 points)
    - Complexity: 8/20 (Low) → Simplicity: 4 points
    - Risk: Low (4 points)
    - Priority: P1 (+0 bonus)
  Score: 11/10 (3+4+4+0)

[4/5] ct8/user-retention-push-notifications-2025-11-16.md
  No engineering review found
    - Feasibility: Medium (2 points, default)
    - Complexity: Unknown → Simplicity: 2 points (default)
    - Risk: Medium (2 points, default)
    - Priority: P2 (-1 penalty)
  Score: 5/10 (2+2+2-1)

[5/5] ct6/onboarding-flow-improvements-2025-11-15.md
  Engineering Review:
    - Feasibility: High (4 points)
    - Complexity: 9/20 (Medium) → Simplicity: 3 points
    - Risk: Low (4 points)
    - Priority: P2 (-1 penalty)
  Score: 10/10 (4+3+4-1)

---

Ranking by score:

1. 🥇 ct6/user-retention-personalized-checkins-2025-11-18.md - 11/10
   (High feasibility, Medium complexity, Medium risk, P0)

2. 🥇 ct5/user-retention-gamification-2025-11-17.md - 11/10
   (Medium feasibility, Low complexity, Low risk, P1)

Tie-breaker: ct6 has higher feasibility (4 vs 3) → ct6 wins

Best spec: ct6/user-retention-personalized-checkins-2025-11-18.md

---

Improving best spec...

Addressing feasibility concerns:
✓ No major concerns (already High)

Reducing complexity:
✓ Breaking cron job implementation into 2 phases:
  - Phase 1: Manual trigger only (simpler, faster)
  - Phase 2: Automated cron scheduling (after validation)
✓ Complexity reduced: 12/20 → 9/20 (High-Medium → Medium)

Mitigating risks:
✓ Adding distributed lock for cron jobs (prevent double-sends)
✓ Adding Twilio rate limit handling with queue throttling
✓ Adding comprehensive monitoring for all new components

Validating effort:
  Original: L (3 weeks)
  Complexity: 9/20 (Medium) suggests 2 weeks
  Risk mitigations add: +3 days
  Phase 1 (manual): 1 week
  Phase 2 (cron): 1 week
  Polish: 3 days
  Total: ~2.5 weeks → M (2 weeks) for Phase 1, +1 week for Phase 2
  Updated: M (2 weeks) for initial launch

Synthesizing from other specs:
✓ Taking gamification insights from ct5 (reward users for engagement)
✓ Taking monitoring setup from ct6 (comprehensive metrics)
✓ Combined approach: Personalized check-ins + gamification elements

---

Creating FINAL_SPEC.md...

Writing improved spec with:
- Phased implementation (reduced complexity)
- Enhanced risk mitigations
- Validated effort estimate
- Synthesized best approaches

Distributing to 4 directories...

✅ Engineering prioritization complete

📊 Reviewed: 5 specs across 4 directories
🏆 Best: ct6/user-retention-personalized-checkins-2025-11-18.md (11/10)

💡 Improvements made:
- Feasibility: No changes needed (already High)
- Complexity: Reduced from 12/20 to 9/20 via phased approach
- Risk: Added 3 key mitigations (locks, rate limiting, monitoring)
- Synthesized gamification insights from ct5 spec

📄 FINAL_SPEC.md distributed to:
- ~/Hacking/codel/ct5/docs/temp/specs/FINAL_SPEC.md
- ~/Hacking/codel/ct6/docs/temp/specs/FINAL_SPEC.md
- ~/Hacking/codel/ct7/docs/temp/specs/FINAL_SPEC.md
- ~/Hacking/codel/ct8/docs/temp/specs/FINAL_SPEC.md

Next step: Run /spec-to-pr in each directory to generate PRs
```

## Scoring Reference

### Feasibility Points
- **High (4):** No blockers, can build now
- **Medium (3):** Minor concerns, mitigations exist
- **Low (2):** Major concerns, significant work needed

### Simplicity Points (Inverse of Complexity)
- **Low complexity (4):** 5-8/20 points
- **Medium complexity (3):** 9-12/20 points
- **High complexity (2):** 13-16/20 points
- **Very high complexity (1):** 17-20/20 points

### Safety Points (Inverse of Risk)
- **Low risk (4):** Well-understood, safe to deploy
- **Medium risk (3):** Some concerns, mitigations exist
- **High risk (2):** Significant risks, careful execution needed

### Priority Modifier
- **P0:** +1 point (critical)
- **P1:** +0 points (important)
- **P2:** -1 point (nice to have)
- **P3:** -2 points (wishlist)

## Skills Used

1. **File operations** - Read specs, write FINAL_SPEC.md
2. **Technical analysis** - Score specs, identify improvements
3. **Synthesis** - Combine best approaches from multiple specs

## Notes

- FINAL_SPEC.md is identical in all directories (exact copy)
- Original specs are preserved (not modified)
- If FINAL_SPEC.md exists, it will be overwritten
- Specs are compared objectively based on engineering criteria
- Improvement focuses on feasibility, simplicity, and safety
- Synthesis combines best technical approaches from multiple specs
- Each project instance may produce different specs, but best one wins
- Engineering prioritization complements PM prioritization (different criteria)
