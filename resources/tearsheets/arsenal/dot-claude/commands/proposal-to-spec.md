---
description: Convert FINAL.md proposal to engineering specification (project)
---

# Proposal to Spec Command

**Purpose:** Transform the prioritized product proposal into a detailed engineering specification ready for implementation.

**Workflow:** Run AFTER `/pm-prioritize` creates FINAL.md in all directories.

## Usage

```bash
# Run in each project directory (ct5, ct6, ct7, ct8)
/proposal-to-spec

# Or with explicit paths
/proposal-to-spec --proposal docs/temp/proposals/FINAL.md
```

## Workflow

### Step 1: Locate FINAL.md

Find the prioritized proposal:
```bash
# Default location
docs/temp/proposals/FINAL.md
```

If FINAL.md doesn't exist:
- Error: "No FINAL.md found. Run /pm-prioritize first."
- Exit without creating spec

### Step 2: Read and Parse Proposal

Read FINAL.md to extract:

**From the proposal:**
- **User Insight** - The problem being solved
- **Infrastructure** - Existing infrastructure mentioned
- **The Change** - What will be built
- **User Outcome** - Expected impact
- **Priority** - P0/P1/P2/P3
- **Effort** - XS/S/M/L/XL
- **PM Review** - Data support, brittleness, extensibility scores

**Key information:**
- Topic name (from filename or title)
- Date (from FINAL.md or current date)
- Data supporting the feature
- Technical constraints mentioned

### Step 3: Generate Engineering Specification

Transform the proposal into a technical specification with these sections:

#### Section 1: Overview

```markdown
# Engineering Specification: {Feature Name}

**Date:** {YYYY-MM-DD}
**Priority:** {P0/P1/P2/P3}
**Effort:** {Updated based on technical analysis}
**Source:** Converted from docs/temp/proposals/FINAL.md

## Executive Summary

{1-2 sentence technical summary of what's being built}

## Problem Statement

{Reframe "User Insight" in technical terms}
- Current system limitation
- Technical debt being addressed
- Performance/scalability issue
```

#### Section 2: Requirements

```markdown
## Functional Requirements

Based on the proposal's "The Change" section, enumerate specific technical requirements:

1. **Requirement 1:** {Specific capability the system must have}
   - Acceptance criteria: {How we know it's done}
   - Test scenario: {How we test it}

2. **Requirement 2:** {Another capability}
   - Acceptance criteria: {Measurable outcome}
   - Test scenario: {Verification method}

{Continue for all requirements...}

## Non-Functional Requirements

- **Performance:** {Response time, throughput targets}
- **Scalability:** {Load handling expectations}
- **Reliability:** {Uptime, error rate targets}
- **Security:** {Authentication, authorization, data protection}
```

#### Section 3: Architecture

```markdown
## System Architecture

### Components Affected

List all system components that will be modified:
- **Component 1:** {Name} - {What changes}
- **Component 2:** {Name} - {What changes}
- **Component 3:** {Name} - {What changes}

### Architecture Diagram

```
{Draw ASCII diagram showing:}
- Existing components
- New components (marked with *)
- Data flow
- Integration points

Example:
┌─────────────┐      ┌──────────────┐
│   FastAPI   │─────>│  Message     │
│   Webhook   │      │  Processor*  │ (new)
└─────────────┘      └──────────────┘
                            │
                            v
                     ┌──────────────┐
                     │  PostgreSQL  │
                     │  Database    │
                     └──────────────┘
```

### Design Decisions

**Decision 1: {Technology/Pattern Choice}**
- **Options considered:** {A, B, C}
- **Choice:** {Selected option}
- **Rationale:** {Why this choice}
- **Trade-offs:** {What we're giving up}

**Decision 2: {Another key decision}**
- **Options considered:** {X, Y, Z}
- **Choice:** {Selected option}
- **Rationale:** {Technical reasoning}
- **Trade-offs:** {Acknowledged downsides}
```

#### Section 4: API Changes

```markdown
## API Changes

### New Endpoints

**POST /api/v1/{resource}**
```json
Request:
{
  "field1": "string",
  "field2": 123
}

Response:
{
  "id": "uuid",
  "created_at": "timestamp",
  "status": "success"
}
```

### Modified Endpoints

**GET /api/v1/{existing-resource}**
- **Change:** Add new query parameter `filter`
- **Backward compatible:** Yes
- **Migration needed:** No

### Deprecated Endpoints

**GET /api/v1/{old-resource}** *(if applicable)*
- **Deprecation date:** {YYYY-MM-DD}
- **Removal date:** {YYYY-MM-DD + 90 days}
- **Migration path:** Use `/api/v1/{new-resource}` instead
```

#### Section 5: Database Changes

```markdown
## Database Schema Changes

### New Tables

**Table: `{table_name}`**
```sql
CREATE TABLE {table_name} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    field1 VARCHAR(255) NOT NULL,
    field2 INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_{table_name}_field1 ON {table_name}(field1);
```

### Modified Tables

**Table: `{existing_table}`**
```sql
-- Add new columns
ALTER TABLE {existing_table}
ADD COLUMN new_field VARCHAR(100);

-- Add constraints
ALTER TABLE {existing_table}
ADD CONSTRAINT check_new_field CHECK (new_field IN ('value1', 'value2'));
```

### Data Migration

```python
# Migration script (alembic)
def upgrade():
    # Step 1: Add column
    op.add_column('existing_table', sa.Column('new_field', sa.String(100)))

    # Step 2: Backfill data
    op.execute("""
        UPDATE existing_table
        SET new_field = 'default_value'
        WHERE new_field IS NULL
    """)

    # Step 3: Add constraint
    op.create_check_constraint(
        'check_new_field',
        'existing_table',
        "new_field IN ('value1', 'value2')"
    )

def downgrade():
    # Rollback steps
    op.drop_constraint('check_new_field', 'existing_table')
    op.drop_column('existing_table', 'new_field')
```
```

#### Section 6: Implementation Plan

```markdown
## Implementation Plan

### Phase 1: Foundation (Effort: {XS/S/M})

**Goal:** Set up core infrastructure

**Tasks:**
1. Create database schema
2. Write migration scripts
3. Set up new service/module structure

**Acceptance:**
- Migrations run successfully
- Tests for schema changes pass
- No breaking changes to existing functionality

**Estimated time:** {X days/weeks}

### Phase 2: Core Logic (Effort: {S/M/L})

**Goal:** Implement main business logic

**Tasks:**
1. Implement core algorithms
2. Add API endpoints
3. Integrate with existing services

**Acceptance:**
- All functional requirements met
- Integration tests pass
- Performance benchmarks met

**Estimated time:** {X days/weeks}

### Phase 3: Polish & Deploy (Effort: {XS/S})

**Goal:** Production readiness

**Tasks:**
1. Add monitoring/observability
2. Write documentation
3. Deploy to staging
4. Run load tests
5. Deploy to production

**Acceptance:**
- All tests pass (unit + integration + e2e)
- Monitoring dashboards created
- Runbook documented
- Staged rollout successful

**Estimated time:** {X days/weeks}
```

#### Section 7: Testing Strategy

```markdown
## Testing Strategy

### Unit Tests

**Coverage target:** 80%+

**Key test cases:**
1. **Test: `test_{function}_with_valid_input`**
   - Input: {Valid data}
   - Expected: {Correct output}
   - Validates: Core logic works correctly

2. **Test: `test_{function}_with_invalid_input`**
   - Input: {Invalid data}
   - Expected: {Proper error}
   - Validates: Error handling

3. **Test: `test_{function}_edge_cases`**
   - Input: {Edge case data}
   - Expected: {Graceful handling}
   - Validates: Robustness

### Integration Tests

**Test: End-to-end flow**
```python
@pytest.mark.integration
async def test_full_workflow():
    # Setup: Create test data
    user = await create_test_user()

    # Execute: Trigger the feature
    response = await client.post("/api/v1/resource", json={...})

    # Verify: Check all side effects
    assert response.status_code == 200
    db_record = await fetch_from_db(response.json()["id"])
    assert db_record.field1 == expected_value

    # Verify: External systems updated
    external_data = await fetch_from_external_service()
    assert external_data.synced == True
```

### E2E Tests

**Test: Real user workflow**
```python
@pytest.mark.e2e
async def test_user_completes_workflow():
    # Simulate actual user journey
    # Uses real database, real queue, real services
    # Validates entire stack works together
```

### Performance Tests

**Load test:** {X requests/second}
**Response time target:** {Y milliseconds at p95}
**Test tool:** {locust/k6/etc}
```

#### Section 8: Risk Assessment

```markdown
## Risk Assessment

### Technical Risks

**Risk 1: {Specific technical risk}**
- **Likelihood:** High/Medium/Low
- **Impact:** Critical/High/Medium/Low
- **Mitigation:** {How to reduce risk}
- **Contingency:** {What if it happens}

**Risk 2: {Another risk}**
- **Likelihood:** High/Medium/Low
- **Impact:** Critical/High/Medium/Low
- **Mitigation:** {Prevention strategy}
- **Contingency:** {Backup plan}

### Dependencies

**External dependencies:**
1. **Dependency: {Library/Service}**
   - **Version:** {X.Y.Z}
   - **Risk:** {What could go wrong}
   - **Mitigation:** {How to handle}

2. **Dependency: {Another service}**
   - **SLA:** {Uptime guarantee}
   - **Risk:** {Service downtime impact}
   - **Mitigation:** {Fallback strategy}

### Breaking Changes

**Impact analysis:**
- **Breaking change:** {What will break}
- **Affected users:** {Who is impacted}
- **Migration path:** {How to upgrade}
- **Communication plan:** {How to notify users}
```

#### Section 9: Monitoring & Observability

```markdown
## Monitoring & Observability

### Metrics

**Key metrics to track:**
1. **{Metric name}** - {What it measures}
   - **Target:** {Expected value}
   - **Alert threshold:** {When to alert}

2. **{Another metric}** - {What it measures}
   - **Target:** {Expected value}
   - **Alert threshold:** {When to alert}

### Logging

**Log events:**
- `feature.started` - User initiates feature
- `feature.processing` - Processing in progress
- `feature.completed` - Successfully completed
- `feature.failed` - Failure with error details

**Log format:**
```json
{
  "timestamp": "2025-11-18T10:00:00Z",
  "level": "INFO",
  "event": "feature.started",
  "user_id": "uuid",
  "trace_id": "uuid",
  "context": {...}
}
```

### Alerts

**Alert 1: High error rate**
- **Trigger:** Error rate > 5% for 5 minutes
- **Severity:** Critical
- **Action:** Page on-call engineer

**Alert 2: Slow response time**
- **Trigger:** p95 latency > 500ms for 10 minutes
- **Severity:** Warning
- **Action:** Notify team channel
```

#### Section 10: Rollout Plan

```markdown
## Rollout Plan

### Feature Flag

**Flag name:** `enable_{feature_name}`
**Default:** `false`
**Rollout strategy:** Gradual percentage rollout

### Rollout Stages

**Stage 1: Internal testing (0.1%)**
- **Duration:** 1 day
- **Audience:** Internal users only
- **Success criteria:** No errors, metrics look good

**Stage 2: Beta users (5%)**
- **Duration:** 3 days
- **Audience:** Opt-in beta testers
- **Success criteria:** Positive feedback, no critical bugs

**Stage 3: Gradual rollout (5% → 25% → 50% → 100%)**
- **Duration:** 1 week
- **Monitoring:** Watch error rates, performance metrics
- **Rollback trigger:** Error rate > 2% OR critical bug

### Rollback Plan

**Immediate rollback if:**
- Error rate exceeds 5%
- Data corruption detected
- Critical security vulnerability found

**Rollback procedure:**
1. Disable feature flag
2. Verify system returns to normal
3. Investigate root cause
4. Fix and re-test before next attempt
```

### Step 4: Assess Complexity & Update Effort

Based on technical analysis, re-evaluate effort estimate:

**Complexity factors:**
- **Database migrations:** Simple column add (low) vs. complex data transformation (high)
- **External integrations:** None (low) vs. multiple APIs (high)
- **Testing scope:** Straightforward (low) vs. edge cases galore (high)
- **Breaking changes:** None (low) vs. major API changes (high)

**Effort mapping:**
- **XS (1-2 days):** Simple config changes, minor tweaks
- **S (3-5 days):** Single API endpoint, straightforward logic
- **M (1-2 weeks):** Multiple endpoints, moderate complexity
- **L (2-4 weeks):** Significant architecture changes
- **XL (1+ months):** Major system redesign

Update effort if technical complexity differs from PM estimate.

### Step 5: Generate Spec Filename

Create filename from topic and date:
```bash
# Extract topic from FINAL.md title or content
TOPIC=$(grep "^# " docs/temp/proposals/FINAL.md | head -1 | sed 's/^# //' | tr ' ' '-' | tr '[:upper:]' '[:lower:]')

# Use current date
DATE=$(date +%Y-%m-%d)

# Generate filename
SPEC_FILE="docs/temp/specs/${TOPIC}-${DATE}.md"
```

### Step 6: Write Specification File

Write the complete specification to:
```
docs/temp/specs/{topic}-YYYY-MM-DD.md
```

**Validation:**
- File created successfully
- All sections present
- No placeholder text (all {...} filled in)
- Markdown formatting correct

### Step 7: Output Summary

```
✅ Engineering spec created

📄 Input:  docs/temp/proposals/FINAL.md
📄 Output: docs/temp/specs/{topic}-2025-11-18.md

📊 Specification Summary:
- Priority: P0
- Updated Effort: M (2 weeks)
- Complexity: Medium
- Breaking Changes: No
- External Dependencies: 2

🔍 Key Technical Details:
- New tables: 1
- Modified tables: 2
- New API endpoints: 3
- Modified endpoints: 1

⚠️ Risks Identified: 2
- Risk 1: {Brief description}
- Risk 2: {Brief description}

📈 Rollout Plan: 4 stages over 1 week

Next step: Run /eng-spec-review {topic}-2025-11-18
```

## Example Usage

### Example: Converting User Retention Proposal

```bash
$ /proposal-to-spec

Reading proposal: docs/temp/proposals/FINAL.md

Found proposal: "Improve User Retention with Personalized Check-ins"
- Priority: P0
- PM Effort: M
- Data Support: Strong
- Brittleness: Okay
- Extensibility: High

Generating engineering specification...

✅ Technical Analysis Complete

Complexity Assessment:
- Database changes: 2 new tables, 1 modified table (Medium)
- API changes: 4 new endpoints (Medium)
- External integrations: Twilio API, Langfuse prompts (Medium)
- Testing scope: E2E with cron jobs and webhooks (High)
- Breaking changes: None (Low)

Updated Effort: L (3 weeks) ← Increased from M due to complexity

Writing specification to: docs/temp/specs/user-retention-personalized-checkins-2025-11-18.md

✅ Engineering spec created

📄 Output: docs/temp/specs/user-retention-personalized-checkins-2025-11-18.md

📊 Specification Summary:
- Priority: P0
- Updated Effort: L (3 weeks)
- Complexity: Medium-High
- Breaking Changes: No
- External Dependencies: 2 (Twilio, Langfuse)

🔍 Key Technical Details:
- New tables: 2 (checkin_schedule, checkin_history)
- Modified tables: 1 (user_preferences)
- New API endpoints: 4
- Modified endpoints: 1

⚠️ Risks Identified: 3
- Risk 1: Cron job scheduling conflicts with existing jobs
- Risk 2: Twilio rate limits during bulk send
- Risk 3: Langfuse prompt versioning during rollout

📈 Rollout Plan: 4 stages over 2 weeks (gradual due to cron jobs)

Next step: Run /eng-spec-review user-retention-personalized-checkins-2025-11-18
```

## Skills Used

1. **Read** - Read FINAL.md proposal
2. **Technical analysis** - Assess complexity, identify risks
3. **Architecture design** - Design system components and interactions

## Notes

- This command translates product language to engineering language
- Adds technical details not present in the proposal
- Updates effort estimate based on technical complexity
- Identifies risks and mitigation strategies
- Creates actionable implementation plan
- Each project instance (ct5, ct6, ct7, ct8) may produce different specs due to different technical contexts
