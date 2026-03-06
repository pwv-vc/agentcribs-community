---
description: Review engineering spec with feasibility, complexity, and risk analysis (project)
---

# Engineering Spec Review Command

**Purpose:** Add critical engineering review to specifications, validating feasibility, assessing complexity, and identifying risks.

**Workflow:** Run AFTER `/proposal-to-spec` creates specs in each directory.

## Usage

```bash
# Review a specific spec
/eng-spec-review user-retention-2025-11-18

# Search and review
/eng-spec-review "personalized check-ins"
```

## Workflow

### Step 1: Find Specification

**🚨 IMPORTANT: Work autonomously. Do NOT ask the user which option they prefer.**

Search `docs/temp/specs/` for the spec file:

**If no arguments provided by user:**
- Automatically find and select the most recent spec (DO NOT ASK):
  ```bash
  ls -t docs/temp/specs/*.md | head -1
  ```
- Announce what you found: "Found most recent spec: {filename}"
- Proceed immediately to Step 2

**If exact filename provided:**
- Use `{topic}-YYYY-MM-DD.md`
- Example: `user-retention-2025-11-18.md`

**If search term provided:**
- Find matching spec by content/title using grep
- If multiple matches: Show list and ask user to clarify
- If single match: Proceed with that spec

### Step 2: Read Specification

Read the spec to understand:
- **Overview:** What's being built
- **Requirements:** Functional and non-functional requirements
- **Architecture:** System design and components
- **API Changes:** New/modified endpoints
- **Database Changes:** Schema modifications
- **Implementation Plan:** Phased rollout approach
- **Testing Strategy:** Test coverage plans
- **Risks:** Already-identified risks
- **Rollout Plan:** Deployment strategy

### Step 3: Feasibility Analysis

**Question 1: Can we actually build this?**

Assess technical feasibility across multiple dimensions:

#### Technology Stack Feasibility

**Check if proposed technologies are viable:**
- Are the libraries/frameworks compatible with our stack?
- Do we have experience with these technologies?
- Are there known issues or limitations?
- Is the technology mature/production-ready?

**Use code search to verify:**
```bash
# Check if we're already using similar patterns
grep -r "similar_pattern" api/src/

# Check existing dependencies
cat api/pyproject.toml | grep -i "proposed_library"
```

**Feasibility indicators:**
- ✅ **High:** Uses existing stack, proven patterns, no new dependencies
- ⚠️ **Medium:** Requires new library but well-documented, team has similar experience
- ❌ **Low:** Requires unfamiliar tech, experimental libraries, significant learning curve

#### AI/LLM Architecture Feasibility

**For specs involving LLM-based features, assess:**

**Prompt Engineering Approach:**
- ✅ **High:** Uses structured outputs, few-shot examples, chain-of-thought
- ⚠️ **Medium:** Uses basic prompts with Langfuse versioning
- ❌ **Low:** Hard-codes prompts in code, no versioning

**Intent Detection Method:**
- ✅ **High:** LLM-based classification with confidence scoring
- ⚠️ **Medium:** Embeddings similarity or simple LLM classification
- ❌ **Low:** Regex patterns, keyword matching (brittle!)

**Error Handling:**
- ✅ **High:** Confidence thresholds, fallback prompts, graceful degradation
- ⚠️ **Medium:** Basic error catching, logs failures
- ❌ **Low:** No error handling, assumes LLM always succeeds

**Context Management:**
- ✅ **High:** Sliding window, semantic compression, retrieval-augmented
- ⚠️ **Medium:** Simple truncation, recent N messages
- ❌ **Low:** No context limits (will hit token limits)

**Observability:**
- ✅ **High:** Langfuse tracing, confidence metrics, failure analysis
- ⚠️ **Medium:** Basic logging of LLM calls
- ❌ **Low:** No visibility into LLM decision-making

**Red flags for AI/LLM specs:**
- ❌ Spec says "use regex to detect X" for semantic tasks
- ❌ No mention of confidence scoring or uncertainty handling
- ❌ No prompt versioning strategy (hard-coded in code)
- ❌ No fallback behavior when LLM fails
- ❌ No A/B testing infrastructure for prompt iterations

#### Infrastructure Feasibility

**Can our infrastructure support this?**
- Database capacity: Can Postgres handle the data volume?
- API throughput: Can we handle the request rate?
- Queue capacity: Can Redis handle the job volume?
- Storage: Do we have sufficient disk/memory?
- Network: Are external API rate limits acceptable?

**Check current capacity:**
```bash
# Example checks (conceptual)
# - Current database size and growth rate
# - Current API request volume
# - Current queue depth and processing rate
```

**Feasibility indicators:**
- ✅ **High:** Well within current capacity, no scaling needed
- ⚠️ **Medium:** Near capacity limits, may need optimization
- ❌ **Low:** Exceeds capacity, requires infrastructure scaling

#### Team Feasibility

**Do we have the skills to build this?**
- Does the team have experience with these technologies?
- Are there knowledge gaps that need training?
- Do we need to hire specialists?
- Can we learn what we need in reasonable time?

**Feasibility indicators:**
- ✅ **High:** Team has done this before, no skill gaps
- ⚠️ **Medium:** Team can learn with documentation, similar past experience
- ❌ **Low:** Requires expertise we don't have, steep learning curve

#### External Dependencies Feasibility

**Are external services reliable?**
- Review each external dependency mentioned in spec
- Check SLA, uptime history, rate limits
- Assess risk if service goes down
- Verify API stability and versioning

**For each external dependency:**
```markdown
**Service: {External Service Name}**
- SLA: {Uptime guarantee}
- Rate limits: {Requests/sec}
- Our usage: {Expected load}
- Risk: High/Medium/Low
- Mitigation: {Fallback strategy}
```

**Feasibility indicators:**
- ✅ **High:** Reliable services with generous limits, good SLAs
- ⚠️ **Medium:** Some concerns but mitigations exist
- ❌ **Low:** Unreliable services, tight rate limits, no fallbacks

#### Time Feasibility

**Can we build this in the estimated timeframe?**
- Review the effort estimate from spec
- Consider: tech complexity, unknowns, dependencies, team velocity
- Check if estimate is realistic

**Feasibility indicators:**
- ✅ **High:** Estimate matches complexity, similar past projects
- ⚠️ **Medium:** Tight but achievable with focus
- ❌ **Low:** Estimate way too optimistic, needs adjustment

### Output for Question 1: Feasibility

```markdown
**Feasibility Assessment:**

**Technology Stack:** High/Medium/Low
- {Key finding about technology choices}
- {Any blockers or concerns}

**Infrastructure:** High/Medium/Low
- {Assessment of capacity and scaling needs}
- {Any infrastructure changes required}

**Team Capability:** High/Medium/Low
- {Assessment of team skills and experience}
- {Any training or hiring needs}

**External Dependencies:** High/Medium/Low
- {Risk assessment for external services}
- {Mitigation strategies}

**Timeline:** High/Medium/Low
- {Reality check on effort estimate}
- {Recommended adjustments if needed}

**Overall Feasibility:** High/Medium/Low
**Blockers:** {List any blocking issues, or "None"}
**Recommendations:** {Suggestions to improve feasibility}
```

### Step 4: Complexity Analysis

**Question 2: How complex is this implementation?**

Analyze complexity across multiple dimensions:

#### Code Complexity

**Algorithmic complexity:**
- Are there complex algorithms or data structures?
- Is there significant business logic?
- Are there edge cases that require careful handling?

**Scoring:**
- **Simple (1):** Straightforward CRUD, no complex logic
- **Moderate (2):** Some business logic, standard algorithms
- **Complex (3):** Intricate algorithms, many edge cases
- **Very Complex (4):** Novel algorithms, high cognitive load

#### Integration Complexity

**How many systems need to integrate?**
- Count: Database, external APIs, internal services, queues, etc.
- Assess: Data flow complexity, error handling across boundaries

**Scoring:**
- **Simple (1):** Single system, no external integrations
- **Moderate (2):** 2-3 systems, straightforward integration
- **Complex (3):** 4-5 systems, complex data flow
- **Very Complex (4):** 6+ systems, distributed transactions

#### Data Complexity

**How complex are the data transformations?**
- Schema changes: Simple column add vs. complex restructuring
- Data migrations: Straightforward vs. lossy transformations
- Data volume: Small dataset vs. millions of rows

**Scoring:**
- **Simple (1):** Add columns, small data volume
- **Moderate (2):** Modify columns, moderate volume
- **Complex (3):** Restructure tables, large volume
- **Very Complex (4):** Multi-step migrations, data loss risk

#### Testing Complexity

**How difficult will testing be?**
- Number of test scenarios
- Need for mocks/fixtures
- E2E test complexity
- Performance testing requirements

**Scoring:**
- **Simple (1):** Straightforward unit tests, no mocks
- **Moderate (2):** Some integration tests, few mocks
- **Complex (3):** Many integration tests, complex mocking
- **Very Complex (4):** Full E2E pipeline, performance testing

#### Deployment Complexity

**How risky is the deployment?**
- Breaking changes
- Data migrations
- Feature flag strategy
- Rollback plan

**Scoring:**
- **Simple (1):** No breaking changes, instant rollback
- **Moderate (2):** Minor breaking changes, feature flagged
- **Complex (3):** Significant changes, careful rollout needed
- **Very Complex (4):** Major breaking changes, complex rollback

### Calculate Complexity Score

```
Total Complexity = Code + Integration + Data + Testing + Deployment
Max score: 20

Complexity Rating:
- Low: 5-8 points
- Medium: 9-12 points
- High: 13-16 points
- Very High: 17-20 points
```

### Output for Question 2: Complexity

```markdown
**Complexity Assessment:**

**Code Complexity:** {1-4} - {Brief explanation}
**Integration Complexity:** {1-4} - {Brief explanation}
**Data Complexity:** {1-4} - {Brief explanation}
**Testing Complexity:** {1-4} - {Brief explanation}
**Deployment Complexity:** {1-4} - {Brief explanation}

**Total Complexity Score:** {5-20} / 20
**Complexity Rating:** Low/Medium/High/Very High

**Key Complexity Drivers:**
- {Most complex aspect 1}
- {Most complex aspect 2}

**Simplification Opportunities:**
- {How to reduce complexity 1}
- {How to reduce complexity 2}
```

### Step 5: Risk Analysis

**Question 3: What could go wrong?**

Identify and assess all implementation risks:

#### Technical Risks

**Categorize risks:**

**Performance Risks:**
- Will this handle the expected load?
- Are there N+1 queries or other performance pitfalls?
- Will response times meet SLAs?

**Data Risks:**
- Could data be corrupted?
- Are migrations reversible?
- Is there risk of data loss?

**Security Risks:**
- Are there new attack vectors?
- Is sensitive data exposed?
- Are permissions/auth correct?

**Reliability Risks:**
- Single points of failure?
- Error handling gaps?
- Monitoring blind spots?

**For each risk, assess:**
```markdown
**Risk: {Risk description}**
- **Likelihood:** High/Medium/Low
- **Impact:** Critical/High/Medium/Low
- **Risk Score:** {Likelihood × Impact}
- **Mitigation:** {How to prevent}
- **Detection:** {How we'll know if it happens}
- **Response:** {What we'll do if it happens}
```

#### Schedule Risks

**What could delay delivery?**
- Unknown unknowns
- Dependency delays
- Scope creep
- Resource constraints

#### Quality Risks

**What could compromise quality?**
- Insufficient testing
- Cutting corners under time pressure
- Skipping code review
- Poor documentation

### Output for Question 3: Risk Analysis

```markdown
**Risk Assessment:**

**High-Priority Risks:**
1. **{Risk name}**
   - Likelihood: {High/Medium/Low}
   - Impact: {Critical/High/Medium/Low}
   - Mitigation: {Strategy}

2. **{Risk name}**
   - Likelihood: {High/Medium/Low}
   - Impact: {Critical/High/Medium/Low}
   - Mitigation: {Strategy}

**Medium-Priority Risks:**
{List 2-3 medium risks}

**Low-Priority Risks:**
{List low risks}

**Overall Risk Level:** High/Medium/Low
**Show-stoppers:** {Any critical unmitigated risks, or "None"}
```

### Step 6: Effort Validation

**Does the effort estimate match the complexity?**

Compare spec's effort estimate with complexity analysis:

```markdown
**Effort Validation:**

**Spec Estimate:** {XS/S/M/L/XL from spec}
**Complexity Rating:** {Low/Medium/High/Very High}
**Feasibility Rating:** {High/Medium/Low}

**Recommended Effort:** {Updated estimate}

**Justification:**
- Complexity score: {X/20} suggests {Y weeks}
- Feasibility concerns add: {+Z days for unknowns}
- Risk mitigation adds: {+W days for safety}
- Total: {Final estimate}

**Confidence:** High/Medium/Low
```

### Step 7: Add Review to Spec

Append concise review (≤150 words) to the bottom of the spec file:

```markdown
{original spec content}

---

## ENGINEERING REVIEW ({YYYY-MM-DD})

**Feasibility:** High/Medium/Low - {1 sentence on key feasibility concern}

**Complexity:** Low/Medium/High/Very High ({X}/20) - {1 sentence on complexity drivers}

**Risk Level:** High/Medium/Low - {1 sentence on top risks}

**Effort Validation:** {Original estimate} → {Recommended estimate} - {1 sentence justification}

**Recommendation:** Approve/Approve with Conditions/Needs Revision/Reject
- {Key condition or concern, if any}

**Reviewer:** {Your name/AI}
```

**Keep it ≤150 words. Be specific and actionable.**

### Step 8: Output Summary

```
✅ Engineering review complete: {spec file}

🔍 Feasibility: {High/Medium/Low}
🧩 Complexity: {Low/Medium/High/Very High} ({X}/20)
⚠️ Risk Level: {High/Medium/Low}
⏱️ Effort: {Original} → {Recommended}

💡 Recommendation: {Approve/Approve with Conditions/Needs Revision/Reject}

📄 Updated: docs/temp/specs/{filename}
```

## Example Usage

### Example: Reviewing User Retention Spec

```bash
$ /eng-spec-review user-retention-personalized-checkins-2025-11-18

Reading spec: docs/temp/specs/user-retention-personalized-checkins-2025-11-18.md

Analyzing feasibility...

✓ Technology Stack: High
  - Uses existing Python/FastAPI/Postgres stack
  - Twilio integration similar to existing SMS features
  - Langfuse prompt management already in place

✓ Infrastructure: High
  - New tables add ~10MB, well within capacity
  - Cron jobs: 4/day per user, ~100 users = 400 jobs/day (manageable)
  - Twilio limit: 200 SMS/day, usage ~100/day (50% headroom)

✓ Team Capability: High
  - Team has built similar cron-based features
  - Twilio integration exists, just extending it
  - No new tech required

⚠️ External Dependencies: Medium
  - Twilio: 99.9% SLA but no fallback for SMS delivery failures
  - Langfuse: Critical for prompts, 99.95% SLA

✓ Timeline: High
  - Spec estimates L (3 weeks), matches similar past projects
  - Clear implementation plan

**Overall Feasibility: High**

---

Analyzing complexity...

Code Complexity: 2/4
  - Moderate business logic for scheduling and personalization
  - Cron job coordination needs careful testing

Integration Complexity: 3/4
  - Integrates: Database, Twilio, Langfuse, Cron scheduler
  - 4 systems with complex error handling

Data Complexity: 2/4
  - 2 new tables, straightforward schema
  - No complex migrations

Testing Complexity: 3/4
  - Need E2E tests for cron → queue → Twilio pipeline
  - Time-sensitive logic requires careful mocking

Deployment Complexity: 2/4
  - Feature flag rollout
  - No breaking changes

**Total Complexity: 12/20 (Medium)**

---

Analyzing risks...

**High-Priority Risks:**

1. **Cron Job Timing Conflicts**
   - Likelihood: Medium
   - Impact: High
   - Mitigation: Distributed lock mechanism, prevent double-sends

2. **Twilio Rate Limit During Bulk Send**
   - Likelihood: Medium
   - Impact: Medium
   - Mitigation: Queue throttling, retry logic

**Medium Risks:**
- Langfuse prompt versioning during gradual rollout
- User timezone calculations for check-in scheduling

**Low Risks:**
- Database table growth (minimal)

**Overall Risk Level: Medium**

---

Validating effort estimate...

Spec Estimate: L (3 weeks)
Complexity: 12/20 (Medium)
Feasibility: High

**Recommended Effort: L (3 weeks)** ✓

Justification:
- Medium complexity (12/20) = ~2-3 weeks baseline
- Cron testing adds +3 days for E2E validation
- Twilio integration refactor adds +2 days
- Total: ~3 weeks matches spec estimate

**Confidence: High**

---

Writing review to spec...

✅ Engineering review complete: user-retention-personalized-checkins-2025-11-18.md

🔍 Feasibility: High
🧩 Complexity: Medium (12/20)
⚠️ Risk Level: Medium
⏱️ Effort: L (3 weeks) → L (3 weeks) ✓

💡 Recommendation: Approve with Conditions
   - Add distributed lock for cron jobs
   - Implement Twilio rate limit handling

📄 Updated: docs/temp/specs/user-retention-personalized-checkins-2025-11-18.md
```

## Skills Used

1. **Code search** - Verify existing patterns and technologies in codebase
2. **Technical analysis** - Assess feasibility, complexity, and risk
3. **Critical thinking** - Identify potential issues and mitigations

## Notes

- Engineering review focuses on **how** to build (feasibility, complexity, risk)
- Complements PM review which focused on **what** to build (data support, user value)
- Review is appended to spec (preserves original content)
- Multiple reviews accumulate (shows evolution of thinking)
- Be objective - approve good specs, reject infeasible ones
- Complexity scoring helps calibrate effort estimates
- Risk analysis identifies issues before they become problems
- Each project instance (ct5, ct6, ct7, ct8) may have different engineering contexts
