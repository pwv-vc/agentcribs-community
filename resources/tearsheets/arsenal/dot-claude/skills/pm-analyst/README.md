# PM Analyst Skill - Usage Guide

## Quick Start

The PM Analyst skill is a **complete workflow** from data analysis to shipping, with built-in pragmatism to avoid over-engineering.

### The 5-Step Workflow

```
User Question → Analysis → Opportunity → Spec → Linear Ticket → Audit → Ship
```

---

## Example: Real Usage

### User asks:
> "How did users react to our 1:1 messages? What should we build next?"

### Step 1: Analyze the Data

**Using relationship-analyst skill:**

```
I'm using the relationship-analyst skill to analyze message reactions...

[Skill runs SQL queries, calculates metrics, identifies patterns]

Output: codel_1on1_reactions_analysis.md
```

**Analysis includes:**
- 71 reactions total (0.7% rate)
- 85.9% loved, 14.1% liked, 4.2% disliked
- Meta-Commentary (MC) highest-performing (craig's 35 reactions = 80% MC)
- Positive Reinforcement (🌟) most loved type
- Suggested Responses polarizing (craig loves, joe/Mary dislike)

---

### Step 2: Identify #1 Opportunity

**PM thinking:**

1. **What's working best?**
   - Positive Reinforcement (🌟) - 85.9% love rate
   - Already our differentiation

2. **What's the gap?**
   - Only triggering ~5-10% of positive moments
   - 6-hour cooldown too restrictive

3. **What's the 80/20 solution?**
   - Reduce cooldown 6h → 1h
   - HIGH IMPACT: 2-3x more of what users love
   - LOW EFFORT: Change one SQL condition

**Priority:** 🔥 SHIP NOW (high impact, low effort)

---

### Step 3: Spec the Feature (MVP)

```markdown
## Problem
Positive Reinforcement (🌟) is highest-performing message type,
but 6-hour cooldown limits coverage to ~5-10% of positive moments.

## Proposed Solution (MVP)
Reduce cooldown from 6 hours to 1 hour.

## Success Metrics
- PR volume: 2-3x increase
- Love rate: Maintain >80%
- No spam complaints

## Implementation
1. Update group_message_intervention_conditions_dsl:
   - Change: sender_interventions_last_6_hours → last_1_hour
   - Change: recipient_interventions_last_6_hours → last_1_hour
2. Deploy to staging (3 days)
3. Deploy to prod gradual rollout (25%→50%→100%)
4. Measure for 4 weeks

## Non-Goals (For Now)
- ❌ Expanding to Medium emotional depth (Phase 2 - after we measure)
- ❌ Variety tracking infrastructure (Phase 3 - only if repetition complaints)
- ❌ Additional affect categories (Phase 4 - no evidence needed)

## Decision Gate (Week 4)
After 4 weeks, answer:
- Did PR volume increase 2-3x?
- Did quality stay high (>80% love rate)?
- Are users asking for MORE or LESS?
- Any repetition complaints?

Then decide: Ship and move on, OR consider Phase 2
```

---

### Step 4: Create Linear Ticket

```bash
# Export API key (get from arsenal/.env)
export LINEAR_API_KEY=your_linear_api_key_here

# Get team ID
.claude/skills/linear-manager/scripts/get_teams.sh
# Output: Codel (CODEL) - cf35cf6c-5d97-4123-a8d3-0f257364a795

# Create ticket
.claude/skills/linear-manager/scripts/create_issue.sh \
  --title "Reduce PR cooldown from 6h to 1h (ship & measure)" \
  --team-id "cf35cf6c-5d97-4123-a8d3-0f257364a795" \
  --priority "high" \
  --description "$(cat <<'DESC'
{Paste feature spec from Step 3}
DESC
)"
```

**Output:** ✅ Created CODEL-804

---

### Step 5: AUDIT THE TICKET 🔍

**This is the critical step most PMs skip.**

#### Review the ticket as "PM's boss"

**Questions:**

1. **Scope creep check:**
   - ✅ Only 1 phase (Phase 1 alone)
   - ✅ Independently valuable
   - ✅ Can ship and stop there

2. **Premature optimization check:**
   - ✅ No infrastructure for hypothetical problems
   - ✅ No edge cases before core value validated
   - ✅ No variety tracking before volume increase

3. **Power user bias check:**
   - ✅ Benefits ALL users (not just craig)
   - ✅ Normal users get 0.8 PR/day (vs 0.3 current)
   - ✅ Power users get 3 PR/day (vs 1 current)

4. **Evidence-based check:**
   - ✅ Reaction data shows PR is highest-performing
   - ✅ Cooldown is documented constraint
   - ✅ No assumptions - solving real problem

5. **Complexity cost check:**
   - ✅ 1 week to ship (not 4-6 sprints)
   - ✅ Minimal risk (trivial rollback)
   - ✅ ROI: 80% value at 5% cost

#### Audit Result: ✅ APPROVED

**No cuts needed** - This ticket is ALREADY the 80/20 solution.

**Why:**
- Single phase only
- No premature optimization
- Benefits all users
- Evidence-based
- Minimal complexity
- Clear decision gate

**Compare to original PM proposal:**
- **Original:** 4-6 sprints (variety tracking, Medium depth, affects expansion)
- **This ticket:** 1 week (cooldown change only)
- **Same core value:** 2-3x more PR

---

## When the Audit WOULD Cut Scope

### Example: If PM had proposed this:

```markdown
## Title
Increase Positive Reinforcement: Reduce cooldown, expand triggers, add variety tracking

## Scope
- Phase 1: Reduce cooldown 6h→1h (1 sprint)
- Phase 2: Expand depth High→Medium (1 sprint + A/B test)
- Phase 3: Variety tracking database (2 sprints)
- Phase 4: Expand affect categories (1 sprint)

Total: 4-6 sprints
```

### Audit would say:

```markdown
## 🚨 TICKET AUDIT

### Critical Questions
1. **Do we need Phase 2-4 before measuring Phase 1?** NO
2. **Is variety tracking for craig (1 user)?** YES
3. **Do we have evidence Medium depth maintains quality?** NO

### What to Cut
❌ Phase 2: Premature - A/B test before simple change
❌ Phase 3: Solving problem that doesn't exist (no repetition complaints)
❌ Phase 4: Speculative - no user evidence

### 80/20 Solution
✅ Ship ONLY Phase 1
✅ Effort: 1 week (vs 4-6 sprints)
✅ Value: 80% of original (2-3x increase)
✅ ROI: 20x better

### Revised Scope
{Ship Phase 1 only, measure 4 weeks, decide on Phase 2 based on DATA}
```

---

## Common Patterns

### Pattern 1: "Big Design Up Front"

**PM proposes:** Multi-phase plan with infrastructure

**Audit catches:**
- Building for hypothetical future
- Phases 2-4 depend on Phase 1 success
- Should ship Phase 1, measure, THEN decide

**Fix:** Cut to Phase 1 only, add decision gate

---

### Pattern 2: "Optimizing for Power Users"

**PM proposes:** Variety tracking for users who send 10+ msgs/day

**Audit catches:**
- craig is 1 user (not 49% of users)
- Normal users (3 msgs/day) don't need variety
- Building infrastructure for <5% of userbase

**Fix:** Ship without variety, add only if complaints emerge

---

### Pattern 3: "Solving Theoretical Problems"

**PM proposes:** A/B testing framework for Medium depth expansion

**Audit catches:**
- No evidence Medium depth dilutes quality
- Premature optimization
- A/B test adds weeks of delay

**Fix:** Ship Phase 1 first, gather data, THEN test if needed

---

## Workflow Checklist

Use this checklist for every PM Analyst run:

### ✅ Analysis Complete
- [ ] Queried production database
- [ ] Sample size documented (n > 30)
- [ ] Patterns identified with clear names
- [ ] Qualitative examples included
- [ ] Failure modes analyzed
- [ ] Statistical context provided
- [ ] File saved: `{topic}_analysis.md`

### ✅ Opportunity Identified
- [ ] #1 insight clearly stated
- [ ] Impact vs. Effort assessed (high/medium/low)
- [ ] User segment size known (% of userbase)
- [ ] Competitive differentiation noted
- [ ] Success metric defined with target

### ✅ Feature Spec Complete
- [ ] Problem statement (1-2 sentences)
- [ ] MVP solution (simplest version)
- [ ] Success metrics with current → target
- [ ] Implementation steps (3-5 bullets, not 10)
- [ ] Non-goals explicitly stated
- [ ] Decision gate at 4 weeks

### ✅ Linear Ticket Created
- [ ] Title: Concise with key metrics
- [ ] Priority: high/medium/low (justified)
- [ ] Description: Feature spec pasted
- [ ] Team ID correct
- [ ] URL tested (CODEL-XXX loads)

### ✅ Audit Completed
- [ ] Challenged scope creep (>1 sprint?)
- [ ] Identified premature optimization
- [ ] Checked power user bias (<5% of users?)
- [ ] Verified evidence-based (or assumptions?)
- [ ] Calculated complexity cost (weeks of eng)
- [ ] Proposed 80/20 solution (if cuts needed)
- [ ] Reduced effort by >50% (if bloated)
- [ ] Maintained >70% of value

---

## Files Generated

A complete pm-analyst workflow produces:

```
codel_1on1_reactions_analysis.md          # Step 1: Analysis
meta_commentary_products_analysis.md       # Step 1: Deep dive (optional)
linear_ticket_spec.md                      # Step 3: Spec (optional, for complex tickets)
CODEL-XXX (Linear)                         # Step 4: Ticket created
{topic}_audit.md                           # Step 5: Audit notes (optional)
```

---

## Tips for Success

### DO
- ✅ Start with real user data
- ✅ Identify patterns, don't just report numbers
- ✅ Pick #1 opportunity (not top 5)
- ✅ Spec the MVP (simplest version)
- ✅ Add decision gates ("measure 4 weeks, then decide")
- ✅ Audit ruthlessly (cut 50%+ of scope)
- ✅ Ship small and learn

### DON'T
- ❌ Skip the audit step (most critical!)
- ❌ Build multi-phase plans without gates
- ❌ Optimize for power users (<5%)
- ❌ Solve theoretical problems
- ❌ Add infrastructure before validating need
- ❌ A/B test before simple change
- ❌ Build everything at once

---

## Philosophy

**The PM Analyst Mindset:**

> "Perfect is the enemy of shipped. Ship 80% of value at 20% of complexity. Measure. Iterate based on DATA, not assumptions. Avoid big design up front. The best PMs ship small and learn fast."

**Why this matters:**

Most PM tickets fail because:
- They're over-scoped (4-6 sprints when 1 week would work)
- They optimize for edge cases (power users)
- They solve hypothetical problems (variety tracking before volume increase)
- They lack decision gates ("if this works, then...")

**This skill enforces:**
- Ship Phase 1 alone
- Measure for 4 weeks
- THEN decide on Phase 2
- Based on real user behavior

---

## Integration

**Before using pm-analyst:**
```bash
# Ensure you have these skills installed:
ls .claude/skills/ | grep -E "(sql-reader|relationship-analyst|product-analytics|linear-manager)"
```

**After using pm-analyst:**
- Linear ticket created and ready for engineering
- Audit completed (scope reduced to 80/20)
- Decision gate at 4 weeks
- Clear success metrics defined

---

## Questions?

**"When should I use pm-analyst vs. just creating a ticket?"**

Use pm-analyst when:
- You need data to inform the decision
- The opportunity isn't obvious
- Risk of over-scoping (multi-phase plans)
- Need to justify priority

Skip pm-analyst when:
- Bug fixes (obvious what to do)
- User explicitly requested feature
- Trivial changes (<1 day of work)

**"Can I skip the audit step?"**

NO. The audit is the most valuable part. It catches:
- Scope creep (4-6 sprints → 1 week)
- Premature optimization (variety tracking)
- Power user bias (craig-specific features)
- Theoretical problems (no evidence needed)

**"What if the audit doesn't find cuts?"**

Great! That means the ticket is already pragmatic. But in practice, 80% of PM tickets have scope that can be cut.

**"How do I know if I'm a good PM?"**

Good PMs:
- Ship Phase 1 alone and measure
- Cut scope ruthlessly
- Avoid big design up front
- Use decision gates

Bad PMs:
- Plan all phases upfront
- Build for hypothetical futures
- Optimize for edge cases
- Skip measurement phases

---

Ready to ship smarter? Use the pm-analyst skill.
