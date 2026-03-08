---
name: product-data-analyst
description: MANDATORY for ALL product/business questions. Analyzes usage data, funnels, metrics, and relationship insights. Use BEFORE sql-reader for product questions.
---

# Product Data Analyst Skill

**Unified framework for analyzing product data, user behavior, conversion funnels, and relationship coaching insights.**

---

## MANDATORY TRIGGERS - When to Use This Skill

**You MUST use this skill if user asks about:**

### Category 1: User Feedback & Reactions (100% of these questions)
- "Do we have user feedback from the last [time period]?"
- "What messages are getting thumbs up/down?"
- "Show me user reactions to [message type]"
- "What are users reacting positively/negatively to?"
- "Pattern analysis of intervention reactions"
- "Which interventions resonate with users?"

**Note:** Reactions are stored as messages with `provider_data->>'reaction_id' IS NOT NULL`, not in a separate table. Content format: `"Loved 'original text'"`. Use `CASE WHEN content LIKE 'Loved %' THEN 'Loved' ...` to extract type.

### Category 2: Behavioral Patterns & Anomalies (100% of these questions)
- "Are power users behaving in surprising ways?"
- "What patterns exist in [user behavior]?"
- "Who are our most engaged users and what do they do?"
- "What's different about users who [succeed/fail/churn]?"
- "Unusual activity in [feature/metric]?"

### Category 3: Trend Analysis & Causation (100% of these questions)
- "What's causing [drop/increase] in [metric]?"
- "Why did [metric] change in [time period]?"
- "What changed after we [launched/modified] [feature]?"
- "Compare [time period A] vs [time period B]"
- "What's the trend for [metric] over time?"

### Category 4: Conversion Funnels (100% of these questions)
- "Conversion funnel for [process]"
- "Where are users dropping off in [flow]?"
- "Drop-off analysis for [feature adoption]"
- "Where do users get stuck in [journey]?"
- "What's blocking users from [goal]?"

### Category 5: Relationship Data - Codel Specific (100% of these questions)
- "SPAFF ratio for [user/couple]"
- "Gottman analysis"
- "Affect distribution"
- "Four Horsemen patterns"
- "Communication patterns over time"
- "Relationship health for [couple]"

### Category 6: Content & Message Analysis (100% of these questions)
- "What topics are couples talking about?"
- "Show me examples of [effective/ineffective] interventions"
- "What message types work best for [segment]?"
- "Content analysis of [message category]"

**When NOT to use this skill:**
- Simple counts: "How many interventions yesterday?" → Use sql-reader
- Direct lookups: "Show me user ID 123" → Use sql-reader
- Schema exploration: "What tables exist?" → Use sql-reader
- Raw data export: "Give me all messages" → Use sql-reader

**The distinction:** sql-reader returns **data**. product-data-analyst provides **insights**.

---

## Decision Tree: Which Analysis Type?

**After user asks a product question, classify it:**

```
User asks product question
  ↓
┌─────────────────────────────────────┐
│ What type of analysis is needed?   │
└─────────────────────────────────────┘
  ↓
  ├─→ Funnel / Multi-Step Flow
  │   Examples: "Onboarding conversion funnel"
  │   Examples: "Where do users drop off?"
  │   → Use Section: Funnel Analysis
  │
  ├─→ Relationship Data / SPAFF
  │   Examples: "Calculate affect ratio for user 123"
  │   Examples: "Four Horsemen patterns"
  │   → Use the `relationship-analyst` skill (canonical SPAFF queries)
  │
  ├─→ Behavioral Patterns / Anomalies
  │   Examples: "Are power users behaving surprisingly?"
  │   Examples: "What patterns in user behavior?"
  │   → Use Section: Product Analytics Framework
  │
  └─→ Trend Analysis / Causation
      Examples: "What's causing drop in engagement?"
      Examples: "Why did metric X change?"
      → Use Section: Product Analytics Framework
```

**Choose the appropriate section below based on classification.**

---

## Prerequisites: Understand the Data Model

**BEFORE any analysis, you MUST:**

1. **Run sql-reader skill bootstrap** (if you haven't already this session)
   - Read: `.claude/skills/sql-reader/SKILL.md`
   - Understand table structures and relationships

2. **Know the key tables:**
   - `message` - All messages (1:1 and group)
   - `message_enrichment` - AI classifications (SPAFF affects, topics)
   - `intervention` - Coaching messages sent by Codel
   - `conversation` - Conversations (couples)
   - `conversation_participant` - Who's in each conversation
   - `persons` - Users and their metadata
   - `person_contacts` - Phone numbers

3. **Understand product instrumentation:**
   - What events are tracked?
   - What's in `message_enrichment`?
   - How are interventions triggered?
   - What's the lifecycle of a conversation?

**If you don't know the schema, STOP and use sql-reader bootstrap first.**

---

## Schema Quirks & Key Learnings

**Critical quirks that affect how you query and interpret data:**

### 1. Reactions Are Messages (Not a Separate Table)
- **Quirk:** Reactions stored as full message records with `provider_data->>'reaction_id' IS NOT NULL`
- **Content format:** `"Loved 'original message text'"` or `"Liked 'text'"`
- **No direct FK:** Can't easily link reaction to original message (must parse content)
- **Extract type:** `CASE WHEN content LIKE 'Loved %' THEN 'Loved' ...`
- **Impact:** Reactions inflate message count (883 reactions among 76,397 messages)

### 2. ONE_ON_ONE vs GROUP Conversations
- **ONE_ON_ONE** (245 convos) = User texting with Codel **COACH** (1:1 coaching)
- **GROUP** (113 convos) = Couple's shared conversation (partners text **EACH OTHER**)
- **No couple 1:1 feature exists** - all couple communication is in GROUP
- **Conflicts only in GROUP** - ONE_ON_ONE is supportive coaching (no conflicts)
- **Identify couples:** `WHERE c.type = 'GROUP' AND cp.role = 'MEMBER'`

### 3. SPAFF Affect Coding System (Gottman Research)

**Only 16 canonical SPAFF affects exist (from Gottman's research).**

Our message_enricher uses **Partner-** and **Other-** prefixes:
- **Partner-[Affect]**: Affect directed at romantic partner (e.g., Partner-Affection, Partner-Anger)
- **Other-[Affect]**: Affect directed at other person (e.g., Other-Affection, Other-Anger)
- **Standalone affects**: Humor, Stonewalling, Neutral (no prefix)

**Affect Ratio Uses Only Partner-Directed Affects:**
- **Includes**: Only `Partner-*` affects + `Humor` + `Stonewalling`
- **Excludes**: All `Other-*` affects (not counted in ratio)
- `Partner-Complaint`: Product-specific (not in canonical Gottman SPAFF, but IS used in production as negative)

**Positive affects (5):**
```sql
affect IN ('Partner-Affection', 'Partner-Validation', 'Partner-Enthusiasm', 'Humor', 'Partner-Interest')
```

**Negative affects (13):**
```sql
affect IN (
  'Partner-Criticism', 'Partner-Contempt', 'Partner-Defensiveness', 'Partner-Complaint',
  'Partner-Sadness', 'Partner-Anger', 'Partner-Belligerence', 'Partner-Domineering',
  'Partner-Fear / Tension', 'Partner-Threats', 'Partner-Disgust', 'Partner-Whining', 'Stonewalling'
)
```

**Special case logic:**
```sql
CASE
  WHEN negative_count = 0 AND positive_count > 0 THEN 100
  WHEN negative_count = 0 AND positive_count = 0 THEN 0
  ELSE ROUND(positive_count::numeric / negative_count::numeric, 2)
END
```

**Four Horsemen:** Partner-Criticism, Partner-Contempt, Partner-Defensiveness, Stonewalling

**For SPAFF calculations and affect ratio SQL, use the `relationship-analyst` skill** — it has the canonical queries.

### 4. Topics Are Free Text (Not Structured Taxonomy)
- **Format:** Free-text strings like "Holiday plans", "Childcare", "Debt repayment"
- **No standardization:** "Holiday plans" vs "Holiday planning" vs "Holiday schedule"
- **Analysis:** Use `GROUP BY topic HAVING COUNT(*) >= 2` for recurring topics

### 5. Message Enrichment Coverage: 71%
- **Total messages:** 76,397
- **Enriched messages:** 54,374 (71.2%)
- **Always use:** `LEFT JOIN message_enrichment` (not all messages enriched)

### 6. Key Product Insights from Analysis

**Power Users (100+ msgs/28d, active 24+/28d):**
- **2.8x better affect ratios** than casual users (13.96 vs 5.01)
- **Conflict FASTER** (2.7 days vs 4.1 for casual) - sign of engagement!
- **100% retention** - all first-month power users remain active
- **Conflict topics:** Planning, childcare, finances (healthy relationship maintenance)

**Churn is NOT about communication health:**
- **Churned users:** 7.75 affect ratio (above 5:1 "magic ratio")
- **At-risk users:** 0% show Four Horsemen patterns
- **Hypothesis:** External factors (life changes), not product fit

**Month 2 decline is normal (honeymoon effect):**
- **37% decline** in affect ratio from Month 1 (12.88) to Month 2 (8.12)
- **Still healthy** (8.12 > 5:1 threshold)

**Communication health vs engagement volume:**
- **43% achieve 5:1 affect ratio** in first month
- **Only 12% become power users**
- **Product succeeds** at improving quality even for moderate users

---

## Historical Insights & Data Gotchas

1. **`conversation_onboarding` introduced 2025-09-10** — Only ~36% of messaging users went through this flow. Use BOTH funnels: Onboarding flow + Activation funnel.

2. **Intervention tracking migrated Aug 27-28, 2025** — Pre-Aug 27: `codel_conversations` | Post-Aug 28: `intervention_message`. Trend analysis spanning migration requires `UNION ALL`.

3. **Person facts migrated Aug 28, 2025** — Pre-Aug 28: `person_facts` (plural) | Post-Aug 28: `person_fact` (singular).

4. **Intervention flow & data (started Aug 28, 2025)** — Trigger: Group message enriched via `message_enricher` → conditions evaluated → intervention sent 1:1. Query pattern:
   ```sql
   SELECT i.type, COUNT(*) as count
   FROM intervention i
   JOIN intervention_message im ON im.intervention_id = i.id
   WHERE im.created_at >= NOW() - INTERVAL '24 hours'
   GROUP BY i.type ORDER BY count DESC;
   ```

5. **Affect ratio uses Partner-directed affects only** — Including Other-* affects dramatically changes ratios (e.g., 23:1 correct vs 16.5:1 incorrect). Always filter `conversation.type = 'GROUP'`.

6. **Repair rate is directional, based on absence of escalation** — Formula: `(responses_without_escalation / total_responses) * 100`. NOT based on positive affects (common mistake leads to ~0.2% vs realistic 20-30%). Each partner has own rate.

7. **Add your insights here:** When you discover a product data quirk, add it to this list in `arsenal/dot-claude/skills/product-data-analyst/SKILL.md`

**Always validate your denominator:**
```sql
SELECT 'conversation_onboarding' as cohort, COUNT(*) FROM conversation_onboarding
UNION ALL
SELECT 'All messaging users', COUNT(DISTINCT pc.person_id)
FROM person_contacts pc JOIN message m ON m.sender_person_contact_id = pc.id;
```

---

## When to Use sql-reader vs product-data-analyst

**Use sql-reader when user asks:**
- **Simple count/sum/avg:** "How many interventions yesterday?" → Returns: 147
- **Direct lookup:** "Show me user ID 123's messages" → Returns: List of messages
- **Schema exploration:** "What columns are in the message table?" → Returns: Column list
- **Raw data export:** "Give me all messages from yesterday" → Returns: Raw data dump

**Use product-data-analyst when user asks:**
- **Pattern discovery:** "What patterns in user reactions?" → Returns: Analysis with examples
- **Behavioral questions:** "Are power users doing X?" → Returns: Comparison, insights
- **Anomaly detection:** "Unusual activity in metric Y?" → Returns: Investigation, context
- **Causation:** "What's causing drop in Z?" → Returns: Hypotheses, evidence
- **Trend explanation:** "Why did engagement change?" → Returns: Before/after analysis

**The key difference:** sql-reader returns **data**. product-data-analyst returns **insights**.

---

## Analysis Type 1: Funnel Analysis

**Use for:** Multi-step user journeys, conversion analysis, drop-off identification.

**Examples:**
- "Onboarding funnel: access code → first message → power user"
- "Activation funnel: first message → power user"
- "Retention funnel: Week 1 → Week 2 → Week 4"

### What is a Funnel?

A **funnel** is a sequence of steps where users progressively drop off:

```
Step 1: 100 users start
  ↓ 60% convert
Step 2: 60 users continue
  ↓ 50% convert
Step 3: 30 users complete
  ↓ 80% convert
Step 4: 24 users retained
```

**Key metrics:**
- **Conversion rate**: % who move from step N to step N+1
- **Drop-off rate**: % who abandon at each step (1 - conversion rate)
- **Time to convert**: How long users take between steps
- **Bottleneck**: Step with lowest conversion rate

---

### Canonical Funnels for Codel

**We have TWO primary funnels that should be used for all activation analysis:**

1. **Funnel A: Onboarding Flow** - Measures recent onboarding improvements (access code → power user)
2. **Funnel B: Activation Funnel** - Measures platform-wide activation (all users → power user)

**Both funnels use identical steps after "Sent first message" for direct comparison.**

---

### Funnel A: Onboarding Flow (Access Code → Power User)

**Purpose:** Measures effectiveness of recent onboarding improvements for users who went through access code signup.

**Cohort:** Users who created access codes >=28 days ago (to ensure 28-day completion window)

**First Month Power User Definition:** 100+ messages in first 28 days + active 24+ of 28 days

#### SQL Query - Funnel A

```sql
WITH onboarding_data AS (
  SELECT
    co.id as onboarding_id,
    co.created_at as access_code_created,
    co.conversation_id,
    MAX(CASE WHEN cpo.is_initiator = false THEN 1 ELSE 0 END) as has_partner,
    MAX(CASE WHEN c.state = 'ACTIVE' THEN 1 ELSE 0 END) as is_activated,
    MIN(m.provider_timestamp) as first_message_at
  FROM conversation_onboarding co
  LEFT JOIN conversation_participant_onboarding cpo ON cpo.conversation_onboarding_id = co.id
  LEFT JOIN conversation c ON c.id = co.conversation_id
  LEFT JOIN message m ON m.conversation_id = co.conversation_id AND c.type = 'GROUP'
  WHERE co.created_at <= NOW() - INTERVAL '28 days'
  GROUP BY co.id, co.created_at, co.conversation_id
),
user_stats AS (
  SELECT
    od.onboarding_id,
    od.first_message_at,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= od.first_message_at
      AND m.provider_timestamp < od.first_message_at + INTERVAL '7 days'
      THEN m.id
    END) as week1_messages,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= od.first_message_at
      AND m.provider_timestamp < od.first_message_at + INTERVAL '7 days'
      THEN DATE(m.provider_timestamp)
    END) as days_active_week1,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= od.first_message_at
      AND m.provider_timestamp < od.first_message_at + INTERVAL '28 days'
      THEN m.id
    END) as month_messages,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= od.first_message_at
      AND m.provider_timestamp < od.first_message_at + INTERVAL '28 days'
      THEN DATE(m.provider_timestamp)
    END) as days_active_month,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= od.first_message_at + INTERVAL '14 days'
      AND m.provider_timestamp < od.first_message_at + INTERVAL '28 days'
      THEN DATE(m.provider_timestamp)
    END) as days_active_15_28,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= NOW() - INTERVAL '28 days'
      THEN m.id
    END) as recent_28_days_messages,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= NOW() - INTERVAL '28 days'
      THEN DATE(m.provider_timestamp)
    END) as recent_28_days_active
  FROM onboarding_data od
  LEFT JOIN message m ON m.conversation_id = od.conversation_id
  WHERE od.first_message_at IS NOT NULL
  GROUP BY od.onboarding_id, od.first_message_at
)
SELECT
  '1. Access codes created (>=28 days ago)' as step,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM onboarding_data), 1) as pct
FROM onboarding_data

UNION ALL

SELECT '2. Partner joined', COUNT(*),
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM onboarding_data), 1)
FROM onboarding_data WHERE has_partner = 1

UNION ALL

SELECT '3. Conversation activated', COUNT(*),
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM onboarding_data), 1)
FROM onboarding_data WHERE is_activated = 1

UNION ALL

SELECT '4. Sent first message', COUNT(*),
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM onboarding_data), 1)
FROM onboarding_data WHERE first_message_at IS NOT NULL

UNION ALL

SELECT '5. Sent 10+ messages first week', COUNT(*),
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM onboarding_data), 1)
FROM user_stats WHERE week1_messages >= 10

UNION ALL

SELECT '6. Active 6+/7 days first week', COUNT(*),
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM onboarding_data), 1)
FROM user_stats WHERE days_active_week1 >= 6

UNION ALL

SELECT '7. Days 15-28 Retained (1+ message)', COUNT(*),
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM onboarding_data), 1)
FROM user_stats WHERE days_active_15_28 >= 1

UNION ALL

SELECT '8. First month power users (100+ msgs, 24+/28 days)', COUNT(*),
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM onboarding_data), 1)
FROM user_stats WHERE month_messages >= 100 AND days_active_month >= 24

UNION ALL

SELECT '9. Active in last 28 days (100+ msgs, 24+ days)', COUNT(*),
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM onboarding_data), 1)
FROM user_stats
WHERE first_message_at <= NOW() - INTERVAL '28 days'
  AND recent_28_days_messages >= 100
  AND recent_28_days_active >= 24

ORDER BY step;
```

#### Expected Format - Funnel A

```markdown
## Funnel A: Onboarding Flow (Access Code → Power User)

**Cohort:** Users who created access codes >=28 days ago
**Power User Definition:** 100+ messages in first 28 days + active 24+ of 28 days

| Step | Metric | Count | Conversion | Notes & Insights |
|------|--------|-------|------------|------------------|
| 1 | Access codes created | 70 | 100.0% | Measures recent onboarding improvements |
| 2 | Partner joined | 18 | 25.7% | Major drop-off: 74% don't get partner to join |
| 3 | Conversation activated | 16 | 22.9% | System reliability good once partner joins |
| 4 | **Sent first message** | **20** | **28.6%** | **Alignment point with Funnel B** |
| 5 | 10+ messages first week | 10 | 14.3% | 50% who message don't reach 10+ in week 1 |
| 6 | Active 6+/7 days first week | 2 | 2.9% | High-frequency early use is rare |
| 7 | Days 15-28 Retained | 2 | 2.9% | Retention to week 3-4 is challenging |
| 8 | **First month power users** | **2** | **2.9%** | 10.0% from first message → power user |
| 9 | **Active in last 28 days** | **2** | **2.9%** | Same 2 users still active |
```

---

### Funnel B: Activation Funnel (First Message → Power User)

**Purpose:** Measures platform-wide activation across all users (not just onboarding flow).

**Cohort:** All users who sent first message >=28 days ago (regardless of signup method)

**First Month Power User Definition:** 100+ messages in first 28 days + active 24+ of 28 days

#### SQL Query - Funnel B

```sql
WITH user_first_messages AS (
  SELECT
    pc.person_id,
    MIN(m.provider_timestamp) as first_message_date
  FROM message m
  JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
  GROUP BY pc.person_id
  HAVING MIN(m.provider_timestamp) <= NOW() - INTERVAL '28 days'
),
user_stats AS (
  SELECT
    ufm.person_id,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= ufm.first_message_date
      AND m.provider_timestamp < ufm.first_message_date + INTERVAL '7 days'
      THEN m.id
    END) as week1_messages,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= ufm.first_message_date
      AND m.provider_timestamp < ufm.first_message_date + INTERVAL '7 days'
      THEN DATE(m.provider_timestamp)
    END) as days_active_week1,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= ufm.first_message_date
      AND m.provider_timestamp < ufm.first_message_date + INTERVAL '28 days'
      THEN m.id
    END) as month_messages,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= ufm.first_message_date
      AND m.provider_timestamp < ufm.first_message_date + INTERVAL '28 days'
      THEN DATE(m.provider_timestamp)
    END) as days_active_month,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= ufm.first_message_date + INTERVAL '14 days'
      AND m.provider_timestamp < ufm.first_message_date + INTERVAL '28 days'
      THEN DATE(m.provider_timestamp)
    END) as days_active_15_28,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= NOW() - INTERVAL '28 days'
      THEN m.id
    END) as recent_28_days_messages,
    COUNT(DISTINCT CASE
      WHEN m.provider_timestamp >= NOW() - INTERVAL '28 days'
      THEN DATE(m.provider_timestamp)
    END) as recent_28_days_active
  FROM user_first_messages ufm
  JOIN person_contacts pc ON pc.person_id = ufm.person_id
  LEFT JOIN message m ON m.sender_person_contact_id = pc.id
  GROUP BY ufm.person_id, ufm.first_message_date
)
SELECT
  '1. Sent first message (>=28 days ago)' as step,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM user_first_messages), 1) as pct
FROM user_first_messages

UNION ALL

SELECT '2. Sent 10+ messages first week', COUNT(*),
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM user_first_messages), 1)
FROM user_stats WHERE week1_messages >= 10

UNION ALL

SELECT '3. Active 6+/7 days first week', COUNT(*),
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM user_first_messages), 1)
FROM user_stats WHERE days_active_week1 >= 6

UNION ALL

SELECT '4. Days 15-28 Retained (1+ message)', COUNT(*),
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM user_first_messages), 1)
FROM user_stats WHERE days_active_15_28 >= 1

UNION ALL

SELECT '5. First month power users (100+ msgs, 24+/28 days)', COUNT(*),
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM user_first_messages), 1)
FROM user_stats WHERE month_messages >= 100 AND days_active_month >= 24

UNION ALL

SELECT '6. Active in last 28 days (100+ msgs, 24+ days)', COUNT(*),
  ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM user_first_messages), 1)
FROM user_stats
WHERE first_message_date <= NOW() - INTERVAL '28 days'
  AND recent_28_days_messages >= 100
  AND recent_28_days_active >= 24

ORDER BY step;
```

#### Expected Format - Funnel B

```markdown
## Funnel B: Activation Funnel (First Message → Power User)

**Cohort:** All users who sent first message >=28 days ago
**Power User Definition:** 100+ messages in first 28 days + active 24+ of 28 days

| Step | Metric | Count | Conversion | Notes & Insights |
|------|--------|-------|------------|------------------|
| 1 | **Sent first message** | **146** | **100.0%** | **Alignment point with Funnel A** |
| 2 | 10+ messages first week | 84 | 57.5% | Strong early engagement signal |
| 3 | Active 6+/7 days first week | 37 | 25.3% | High-frequency users |
| 4 | Days 15-28 Retained | 68 | 46.6% | Better retention than onboarding flow |
| 5 | **First month power users** | **17** | **11.6%** | 11.6% activate to power user |
| 6 | **Active in last 28 days** | **17** | **11.6%** | 100% retention from first month |
```

---

### Comparing the Two Funnels

| Question | Use This Funnel | Why |
|----------|-----------------|-----|
| "How's our recent onboarding working?" | Funnel A | Measures recent product changes |
| "What's our overall activation rate?" | Funnel B | Platform-wide PMF signal |
| "Did the access code flow improve things?" | Compare A vs B | Shows impact of onboarding |
| "Where do users drop off?" | Both | Different bottlenecks in each |
| "What's blocking partner acquisition?" | Funnel A | Partner join is step 2 |
| "Do messaging users activate?" | Funnel B | Shows messaging → power user |

**Key insight:** Funnel A 10.0% conversion (first message → power user) vs Funnel B 11.6%. Overall users convert at slightly higher rate than onboarding-only.

---

### Presentation Format (MANDATORY)

**When presenting either funnel, ALWAYS use this table format:**

| Step | Metric | Count | Conversion | Notes & Insights |
|------|--------|-------|------------|------------------|
| N | Step name | Number | Percentage | Why this matters / what it tells us |

**The "Notes & Insights" column must include:**
- What this step measures
- Why drop-offs happen at this stage
- How this compares to benchmarks or other funnels
- What action could improve this step

---

## Analysis Type 2: Relationship Insights (SPAFF Ratios)

**For SPAFF calculations, use the `relationship-analyst` skill.** It has the canonical affect ratio queries with correct column names (`me.affect`, `m.provider_timestamp`, `m.sender_person_contact_id`).

**For clinical assessment of relationship health trends**, use the `assess-relationship-health` skill. It provides 28-day period and weekly rolling affect ratios, repair rates, conflict pattern identification, and diagnostic investigation.

**This skill provides the SPAFF reference data** (see Schema Quirks section 3 above) and the product context for interpreting results. The actual SQL queries live in the specialized skills to avoid duplication and drift.

**Affect Ratio Thresholds:**
- **>=20:1** - Upper target (exceptional)
- **>=5:1** - Lower target (healthy, "magic ratio")
- **1:1-5:1** - At-risk
- **<1:1** - Distress

---

## Analysis Type 3: Product Analytics Framework

**Use for:** Deep dives, pattern discovery, trend analysis, engagement studies.

**Examples:**
- "What types of interventions get the best reactions?"
- "What are usage patterns for power users vs casual users?"
- "How has engagement changed over the last 3 months?"

### Product Analytics Workflow

#### Step 1: Define the Question

Start with a clear, specific question:
- Bad: "How are users doing?"
- Good: "What types of 1:1 messages from Codel get the most positive reactions from users?"

**Write down:** Primary question, success metric, time range, user segment (if applicable).

#### Step 2: Collect Comprehensive Data

**Use sql-reader skill to query production data.**

Collect:
- **Quantitative data:** Counts, rates, distributions, trends
- **Qualitative data:** Actual message content, user names, specific examples
- **Context data:** Time of day, user characteristics, conversation state

**Best practices:**
- Query at different granularities (daily, weekly, monthly)
- Get both aggregates AND individual examples
- Include negative cases (what DIDN'T work)
- Gather enough data to see patterns (not just outliers)

#### Step 3: Create Structured Analysis

**MANDATORY:** Create a markdown file with these sections:

```markdown
# {Topic} Analysis

**Analysis Date:** {YYYY-MM-DD}
**Time Range:** {e.g., "Last 30 days" or "All time"}
**Total Records Analyzed:** {number}

## Key Findings
1. {Most important insight}
2. {Second most important insight}
3. {Third most important insight}

## Metrics Overview

| Metric | Value | Benchmark | Status |
|--------|-------|-----------|--------|
| Total X | 1,234 | - | - |
| Conversion Rate | 12.5% | 10% | Above target |

## Patterns Identified

### What Works
1. **{Pattern}** ({count} instances) - {why it works}

### What Doesn't Work
1. **{Pattern}** ({count} instances) - {why it fails}

## Concrete Examples (3-5 actual examples with analysis)

## Recommendations

### Immediate Actions
1. {Action with data support}

### Further Investigation
1. {Question to answer next}
```

#### Step 4: Share Insights

Save markdown file with descriptive name including date: `{topic}_analysis_{YYYY_MM_DD}.md`

---

## Common Product Questions & Routing

| User Question | Analysis Type | Key Section |
|---------------|---------------|-------------|
| "How many interventions yesterday?" | Quick Metric | Use sql-reader |
| "Onboarding completion rate?" | Funnel | Funnel Analysis |
| "SPAFF ratio for couple X?" | SPAFF | relationship-analyst skill |
| "What interventions work best?" | Product Analytics | Analytics Framework |
| "User retention over time?" | Product Analytics | Analytics Framework |
| "Where do users drop off?" | Funnel | Funnel Analysis |
| "Communication patterns for user Y?" | SPAFF | relationship-analyst skill |
| "Feature adoption funnel?" | Funnel | Funnel Analysis |
| "What are power users doing?" | Product Analytics | Analytics Framework |

---

## Success Criteria

You've successfully used this skill when:

- [ ] You identified the question type (funnel/SPAFF/analytics)
- [ ] You used sql-reader to query production data with proper context
- [ ] You provided structured output (tables, examples, insights)
- [ ] You included actionable recommendations
- [ ] You used product terminology correctly (not just raw SQL)
- [ ] You contextualized numbers with benchmarks or trends

---

## Violations

**BANNED:**
- Using sql-reader without this skill for product questions
- Returning raw SQL results without context or interpretation
- Providing numbers without examples or patterns
- Making recommendations without data support
- Analyzing data without understanding product instrumentation
- Calculating SPAFF ratios without checking sample size warnings
- Using nonexistent columns (`sent_at`, `direction`, `primary_spaff_affect`, `primary_message_type`, `message_topic`)

**CORRECT:**
- Always use this skill for product/business questions
- Provide context, patterns, and examples
- Structure output with markdown tables
- Include concrete recommendations
- Reference the data model and instrumentation
- Check data quality before drawing conclusions
- Use correct column names: `provider_timestamp`, `affect`, `topic`, `sender_person_contact_id`
