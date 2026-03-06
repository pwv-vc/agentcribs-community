---
name: assess-relationship-health
description: Clinical assessment of couple's relationship health using affect ratios and repair rates. Supports 28-day period and weekly rolling granularity. Identifies conflict patterns, inflection points, and causal conversations.
allowed-tools:
  - Bash
  - Read
  - Write
  - Grep
  - Glob
---

# Assess Relationship Health Skill

**Clinical workflow for assessing couple relationship health through affect ratios, repair rates, conflict patterns, and diagnostic investigation.**

---

## When to Use This Skill

Use this skill when:
- "Assess [couple's] relationship/conflict/communication health"
- "How is [couple's] relationship doing?"
- "Show me [couple's] affect ratio/repair rate trends"
- "What's causing [couple's] health to decline?"
- "When did [couple's] relationship health change?"
- "What conflict pattern does [couple] have?"

**This is a CLINICAL skill** - prescriptive SQL, health thresholds, diagnostic workflow.

---

## Health Thresholds (Gottman Research-Based)

### Affect Ratio (Positive:Negative)
- **Healthy:** 5:1 to 30:1 (Gottman's sustainable range)
- **At-Risk:** <5:1 (below Gottman "magic ratio")
- **Context-Dependent:** >30:1 or 100:1
  - During external stress (medical, moving, election) → Likely **conflict avoidance** (dysfunctional)
  - Sustained with genuine connection → May be **stable conflict avoiders** (functional Gottman type)
  - If "affectless and devitalized" → **High neutral affect** (Gottman divorce predictor)
  - **Diagnostic**: Check intimacy topics, playful affects, genuine engagement

### Repair Rate (De-escalation Success %)
- **Healthy:** >75%
- **At-Risk:** 50-75%
- **Concerning:** <50% (highly defensive, poor conflict management)

### NULL/Special Values
- **Affect Ratio = 0:** No affect data (no emotional messages)
- **Affect Ratio = 100:** Zero negative affects — context matters (see above)
- **Repair Rate = NULL:** No responses to partner's conflicts (stonewalling/avoidance)

---

## SPAFF Affect Reference

**Defined once. All SQL templates below use these exact affect names.**

**Positive affects (5):**
```sql
'Partner-Affection', 'Partner-Validation', 'Partner-Enthusiasm', 'Humor', 'Partner-Interest'
```

**Negative affects (13):**
```sql
'Partner-Criticism', 'Partner-Contempt', 'Partner-Defensiveness', 'Partner-Complaint',
'Partner-Sadness', 'Partner-Anger', 'Partner-Belligerence', 'Partner-Domineering',
'Partner-Fear / Tension', 'Partner-Threats', 'Partner-Disgust', 'Partner-Whining', 'Stonewalling'
```

Note: `Partner-Complaint` is product-specific (not canonical Gottman SPAFF). `Other-*` affects are excluded from ratios.

---

## EFT Conflict Patterns

### Distressed Patterns (Sue Johnson's EFT)

#### 1. Pursue-Withdraw (Most Common)
One partner chases/demands connection, the other pulls away. The more one pushes, the more the other retreats.

**Markers:** Asymmetric conflict initiation, pursuit affects (Criticism, Complaint) from one partner, Stonewalling/NULL repair rates from the other.

**Diagnostic query:**
```sql
-- Pursue-Withdraw detection: look for asymmetric conflict patterns
SELECT p.id,
  COUNT(*) FILTER (WHERE me.conflict_state IN ('New Conflict', 'New conflict')) as conflicts_started,
  COUNT(*) FILTER (WHERE me.affect = 'Stonewalling') as stonewalling_count,
  COUNT(*) FILTER (WHERE me.affect IN ('Partner-Criticism', 'Partner-Complaint')) as pursuit_affects,
  COUNT(*) as total_messages
FROM message m
JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
JOIN persons p ON pc.person_id = p.id
LEFT JOIN message_enrichment me ON me.message_id = m.id
WHERE m.provider_timestamp >= CURRENT_DATE - INTERVAL '28 days'
GROUP BY p.id;
```

**Interpretation:** Partner A starts 80%+ conflicts = pursuer. Partner B has stonewalling but A doesn't = withdrawer. Check repair rates: withdrawer often has NULL (no response to partner's conflicts).

#### 2. Attack-Attack (Escalating)
Both partners get reactive and blame-focused. Balanced high negative affects from both.

**Markers:** Balanced criticism/contempt from both, escalation rate >40%, belligerence from both.

**Diagnostic query:**
```sql
-- Attack-Attack detection: balanced criticism from both partners
WITH couple_affects AS (
  SELECT p.id,
    COUNT(*) FILTER (WHERE me.affect IN ('Partner-Criticism', 'Partner-Contempt', 'Partner-Defensiveness', 'Partner-Belligerence')) as attack_affects,
    COUNT(*) FILTER (WHERE me.conflict_state = 'Escalation') as escalations,
    COUNT(*) FILTER (WHERE me.conflict_state IN ('New Conflict', 'New conflict')) as conflicts,
    COUNT(*) as total_messages
  FROM message m
  JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
  JOIN persons p ON pc.person_id = p.id
  LEFT JOIN message_enrichment me ON me.message_id = m.id
  WHERE m.provider_timestamp >= CURRENT_DATE - INTERVAL '28 days'
  GROUP BY p.id
)
SELECT id, attack_affects, escalations, conflicts,
  ROUND((attack_affects::numeric / NULLIF(total_messages, 0)::numeric) * 100, 1) as attack_pct,
  CASE WHEN conflicts > 0 THEN ROUND((escalations::numeric / conflicts::numeric) * 100, 1) ELSE 0 END as escalation_rate
FROM couple_affects;
```

**Interpretation:** Both partners have similar attack_pct (within 5%) + escalation rate >40% = Attack-Attack.

#### 3. Withdraw-Withdraw (Avoidant)
Both partners avoid conflict. Relationship feels distant, "affectless." Often develops when pursuer gives up.

**Markers:** Very high affect ratios (>30:1, especially 100:1) during stress, low conflict initiation from both (<2/month), surface-level topics, NULL repair rates.

**Diagnostic query:**
```sql
-- Withdraw-Withdraw detection: low conflict + low emotional engagement
WITH conflict_counts AS (
  SELECT p.id,
    COUNT(*) FILTER (WHERE me.conflict_state IN ('New Conflict', 'New conflict')) as conflicts_started,
    COUNT(*) FILTER (WHERE me.affect IS NOT NULL AND me.affect <> 'Neutral') as emotional_messages,
    COUNT(*) as total_messages
  FROM message m
  JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
  JOIN persons p ON pc.person_id = p.id
  LEFT JOIN message_enrichment me ON me.message_id = m.id
  WHERE m.provider_timestamp >= CURRENT_DATE - INTERVAL '28 days'
  GROUP BY p.id
)
SELECT id, conflicts_started, emotional_messages, total_messages,
  ROUND((conflicts_started::numeric / NULLIF(total_messages, 0)::numeric) * 100, 1) as conflict_pct,
  ROUND((emotional_messages::numeric / NULLIF(total_messages, 0)::numeric) * 100, 1) as emotional_pct
FROM conflict_counts;
```

**Interpretation:** Both partners <3% conflict_pct AND <30% emotional_pct = Withdraw-Withdraw. Compare to couple's OWN baseline — sudden drop during stress = stress-triggered avoidance.

### Healthy Patterns (Gottman's Stable Types)

#### 4. Validators
Calm conflict, collaborative problem-solving, mutual validation. Ratios 5-20:1, repair >75% both partners.

#### 5. Volatile
Lots of conflict AND passion. High negative AND positive affects, but ratio still 5-20:1, repair >75%. Quick de-escalation after intense conflicts.

#### 6. Stable Conflict Avoiders
Low conflict (<2/month) BUT high connection/intimacy topics and playful affects. Key difference from Withdraw-Withdraw: emotional vitality present, not devitalized.

**Distinguishing query (Stable Avoiders vs Withdraw-Withdraw):**
```sql
-- Distinguish stable avoiders from withdraw-withdraw
WITH engagement_metrics AS (
  SELECT COUNT(*) as total_messages,
    COUNT(*) FILTER (WHERE me.conflict_state IN ('New Conflict', 'New conflict')) as conflicts,
    COUNT(*) FILTER (WHERE me.topic ILIKE '%intimacy%' OR me.topic ILIKE '%appreciation%' OR me.topic ILIKE '%gratitude%') as connection_topics,
    COUNT(*) FILTER (WHERE me.affect IN ('Humor', 'Partner-Affection', 'Partner-Enthusiasm', 'Partner-Interest')) as playful_affects
  FROM message m
  LEFT JOIN message_enrichment me ON me.message_id = m.id
  WHERE m.provider_timestamp >= CURRENT_DATE - INTERVAL '28 days'
)
SELECT total_messages, conflicts, connection_topics, playful_affects,
  ROUND((conflicts::numeric / NULLIF(total_messages, 0)::numeric) * 100, 1) as conflict_pct,
  ROUND((connection_topics::numeric / NULLIF(total_messages, 0)::numeric) * 100, 1) as connection_pct,
  ROUND((playful_affects::numeric / NULLIF(total_messages, 0)::numeric) * 100, 1) as playful_pct,
  CASE
    WHEN (conflicts::numeric / NULLIF(total_messages, 0)::numeric) < 0.03
         AND (connection_topics::numeric / NULLIF(total_messages, 0)::numeric) < 0.02
         AND (playful_affects::numeric / NULLIF(total_messages, 0)::numeric) < 0.03
    THEN 'Withdraw-Withdraw (concerning)'
    WHEN (conflicts::numeric / NULLIF(total_messages, 0)::numeric) < 0.03
         AND ((connection_topics::numeric / NULLIF(total_messages, 0)::numeric) >= 0.03
              OR (playful_affects::numeric / NULLIF(total_messages, 0)::numeric) >= 0.03)
    THEN 'Stable Conflict Avoiders (healthy)'
    ELSE 'Engaged pattern (normal conflict rate)'
  END as pattern_diagnosis
FROM engagement_metrics;
```

**Calibration:** Thresholds (3% conflict, 2-3% connection) are starting points. Adjust for messaging volume and couple's historical baseline. Low-volume (<100 msgs/month): use absolute counts. High-volume (>500 msgs/month): lower percentage thresholds.

---

## Workflow: Clinical Assessment

### Choose Granularity

| Granularity | When to use | SQL Templates |
|---|---|---|
| **28-Day Periods** | Month-over-month trends, 4-period comparison | 28-Day Period Snapshots |
| **Weekly Rolling** | Detailed weekly trends, 12-week view with 56-day trailing averages | Weekly Rolling Templates |
| **Single Value** | Quick current health check (last 56 days) | Single Value Queries |

### Step 1: Run Health Metrics (BOTH REQUIRED)

**MANDATORY: Run BOTH affect ratios AND repair rates** from your chosen granularity.

A couple can have perfect affect ratios but poor repair (or vice versa) — you need BOTH.

### Step 2: Analyze Trends & Identify Conflict Pattern

1. **Current Health Status:**
   - Affect ratios: Healthy (5-30)? At-risk (<5)? Concerning (>30 or 0)?
   - Repair rates: Healthy (>75%)? At-risk (50-75%)? Concerning (<50% or NULL)?

2. **Trend Pattern:** Improving / Declining / Stable / Volatile / Recovering / Degrading

3. **Identify Inflection Points:**
   - Periods/weeks where ratio changed >20% or repair changed >15pp
   - Where metrics crossed health thresholds (5:1, 30:1, 75%)

4. **Identify Conflict Pattern** (run diagnostic queries from EFT section above):
   - If ratios >30:1: must distinguish Withdraw-Withdraw vs Stable Avoiders

### Step 3: Diagnose Inflection Points

For each inflection point, run ALL 5 diagnostic queries (see Diagnostic Queries section below).

### Step 4: Investigate Causal Conversations

For each inflection point with declining trends, query messages +/-3 days (see Causal Investigation section below).

### Assessment Document Format

```markdown
# Relationship Health Assessment: {{Person1}} & {{Person2}}
**Date:** {{date}} | **Period:** {{data_range}} | **Granularity:** {{28-day/weekly}}

## Current Health
- Affect Ratios: {{Person1}} {{ratio}}:1 ({{status}}), {{Person2}} {{ratio}}:1 ({{status}}), Couple {{ratio}}:1 ({{status}})
- Repair Rates: {{Person1}} {{rate}}% ({{status}}), {{Person2}} {{rate}}% ({{status}})

## Conflict Pattern: {{Pattern}} ({{EFT/Gottman}})
Evidence: {{metrics and diagnostic query results}}
Clinical Significance: {{attachment needs, recommended interventions}}

## Trends
- Affect ratios: {{pattern}} | Repair rates: {{pattern}}

## Inflection Points
1. {{date}}: {{metric}} changed from {{X}} to {{Y}} ({{Z}}% change)

## Diagnostic Analysis (per inflection point)
Root cause: {{synthesis of 5 diagnostic queries}}
Likely trigger: {{specific event/topic}}
Sample messages: {{2-3 representative messages}}

## Causal Analysis (if declining)
{{Topics discussed, conflict patterns observed, Four Horsemen detected}}
```

---

## SQL Templates: 28-Day Period Snapshots

### Affect Ratios by 28-Day Period

```sql
-- 28-day period snapshots for affect ratios (4 periods = 112 days)
-- Replace {{person_id}} with actual person_id
WITH
  target_conversation AS (
    SELECT c.id AS conversation_id
    FROM conversation c
    JOIN conversation_participant cp ON cp.conversation_id = c.id
    WHERE cp.person_id = CAST({{person_id}} AS int)
      AND c.type = 'GROUP'
    LIMIT 1
  ),
  couple AS (
    SELECT
      tc.conversation_id,
      p.id AS person_id
    FROM target_conversation tc
    JOIN conversation_participant cp ON cp.conversation_id = tc.conversation_id
    JOIN persons p ON cp.person_id = p.id
    WHERE cp.role = 'MEMBER'
    LIMIT 2
  ),
  periods AS (
    SELECT 1 AS period_num, 'Period 1 (Days 1-28)' AS period_name,
      CURRENT_DATE - INTERVAL '28 days' AS start_date, CURRENT_DATE AS end_date
    UNION ALL SELECT 2, 'Period 2 (Days 29-56)',
      CURRENT_DATE - INTERVAL '56 days', CURRENT_DATE - INTERVAL '28 days'
    UNION ALL SELECT 3, 'Period 3 (Days 57-84)',
      CURRENT_DATE - INTERVAL '84 days', CURRENT_DATE - INTERVAL '56 days'
    UNION ALL SELECT 4, 'Period 4 (Days 85-112)',
      CURRENT_DATE - INTERVAL '112 days', CURRENT_DATE - INTERVAL '84 days'
  ),
  period_affects AS (
    SELECT
      p.period_num, p.period_name, cp.person_id,
      SUM(CASE WHEN me.affect IN (
        'Partner-Affection','Partner-Validation','Partner-Enthusiasm','Humor','Partner-Interest'
      ) THEN 1 ELSE 0 END) AS positive_count,
      SUM(CASE WHEN me.affect IN (
        'Partner-Criticism','Partner-Contempt','Partner-Defensiveness','Partner-Complaint',
        'Partner-Sadness','Partner-Anger','Partner-Belligerence','Partner-Domineering',
        'Partner-Fear / Tension','Partner-Threats','Partner-Disgust','Partner-Whining','Stonewalling'
      ) THEN 1 ELSE 0 END) AS negative_count
    FROM couple cp
    CROSS JOIN periods p
    JOIN message m ON m.conversation_id = cp.conversation_id
    JOIN person_contacts pc ON m.sender_person_contact_id = pc.id AND pc.person_id = cp.person_id
    JOIN message_enrichment me ON me.message_id = m.id
    WHERE m.provider_timestamp >= p.start_date AND m.provider_timestamp < p.end_date
    GROUP BY p.period_num, p.period_name, cp.person_id
  ),
  period_ratios AS (
    SELECT period_num, period_name,
      MAX(CASE WHEN person_id = (SELECT MIN(person_id) FROM couple) THEN person_id END) AS person1_id,
      MAX(CASE WHEN person_id = (SELECT MAX(person_id) FROM couple) THEN person_id END) AS person2_id,
      SUM(CASE WHEN person_id = (SELECT MIN(person_id) FROM couple) THEN positive_count ELSE 0 END) AS p1_positive,
      SUM(CASE WHEN person_id = (SELECT MIN(person_id) FROM couple) THEN negative_count ELSE 0 END) AS p1_negative,
      SUM(CASE WHEN person_id = (SELECT MAX(person_id) FROM couple) THEN positive_count ELSE 0 END) AS p2_positive,
      SUM(CASE WHEN person_id = (SELECT MAX(person_id) FROM couple) THEN negative_count ELSE 0 END) AS p2_negative
    FROM period_affects
    GROUP BY period_num, period_name
  )
SELECT period_num, period_name, person1_id, person2_id,
  p1_positive, p1_negative,
  CASE WHEN p1_negative = 0 AND p1_positive > 0 THEN 100
       WHEN p1_negative = 0 THEN 0
       ELSE ROUND(p1_positive::numeric / p1_negative::numeric, 2) END AS person1_affect_ratio,
  p2_positive, p2_negative,
  CASE WHEN p2_negative = 0 AND p2_positive > 0 THEN 100
       WHEN p2_negative = 0 THEN 0
       ELSE ROUND(p2_positive::numeric / p2_negative::numeric, 2) END AS person2_affect_ratio,
  p1_positive + p2_positive AS couple_positive, p1_negative + p2_negative AS couple_negative,
  CASE WHEN (p1_negative + p2_negative) = 0 AND (p1_positive + p2_positive) > 0 THEN 100
       WHEN (p1_negative + p2_negative) = 0 THEN 0
       ELSE ROUND((p1_positive + p2_positive)::numeric / (p1_negative + p2_negative)::numeric, 2) END AS couple_affect_ratio
FROM period_ratios
ORDER BY period_num;
```

### Repair Rates by 28-Day Period

```sql
-- 28-day period snapshots for repair rates
-- Replace {{person_id}} with actual person_id
WITH couple_info AS (
  SELECT
    c.id AS conversation_id,
    MIN(cp.person_id) AS person1_id, MAX(cp.person_id) AS person2_id
  FROM conversation c
  JOIN conversation_participant cp ON cp.conversation_id = c.id
  JOIN persons p ON cp.person_id = p.id
  WHERE c.type = 'GROUP' AND cp.role = 'MEMBER'
    AND CAST({{person_id}} AS int) IN (SELECT person_id FROM conversation_participant WHERE conversation_id = c.id)
  GROUP BY c.id
  HAVING COUNT(DISTINCT cp.person_id) = 2
  LIMIT 1
),
periods AS (
  SELECT 1 AS period_num, 'Period 1 (Days 1-28)' AS period_name,
    CURRENT_DATE - INTERVAL '28 days' AS start_date, CURRENT_DATE AS end_date
  UNION ALL SELECT 2, 'Period 2 (Days 29-56)',
    CURRENT_DATE - INTERVAL '56 days', CURRENT_DATE - INTERVAL '28 days'
  UNION ALL SELECT 3, 'Period 3 (Days 57-84)',
    CURRENT_DATE - INTERVAL '84 days', CURRENT_DATE - INTERVAL '56 days'
  UNION ALL SELECT 4, 'Period 4 (Days 85-112)',
    CURRENT_DATE - INTERVAL '112 days', CURRENT_DATE - INTERVAL '84 days'
),
conflict_responses AS (
  SELECT
    m1.id as conflict_id, pc1.person_id as conflict_starter_id,
    m1.provider_timestamp as conflict_time, m1.conversation_id,
    MAX(CASE WHEN m2.id IS NOT NULL THEN 1 ELSE 0 END) as has_response,
    MAX(CASE
      WHEN m2.provider_timestamp <= (
        SELECT MAX(provider_timestamp) FROM (
          SELECT m3.provider_timestamp FROM message m3
          WHERE m3.conversation_id = m1.conversation_id
            AND m3.provider_timestamp > m1.provider_timestamp
          ORDER BY m3.provider_timestamp LIMIT 5
        ) AS next_5
      )
      AND pc2.person_id <> pc1.person_id
      AND me2.conflict_state IN ('Escalation', 'New Conflict', 'New conflict', 'De-escalation Failed')
      THEN 1 ELSE 0
    END) as has_escalation
  FROM couple_info ci
  JOIN message m1 ON m1.conversation_id = ci.conversation_id
  JOIN person_contacts pc1 ON m1.sender_person_contact_id = pc1.id
  JOIN message_enrichment me1 ON me1.message_id = m1.id
  LEFT JOIN message m2 ON m2.conversation_id = m1.conversation_id AND m2.provider_timestamp > m1.provider_timestamp
  LEFT JOIN person_contacts pc2 ON m2.sender_person_contact_id = pc2.id
  LEFT JOIN message_enrichment me2 ON me2.message_id = m2.id
  WHERE me1.conflict_state IN ('New Conflict', 'New conflict', 'Escalation')
    AND m1.provider_timestamp >= CURRENT_DATE - INTERVAL '112 days'
    AND m1.provider_timestamp < CURRENT_DATE
  GROUP BY m1.id, pc1.person_id, m1.provider_timestamp, m1.conversation_id
),
period_repair AS (
  SELECT p.period_num, p.period_name, ci.person1_id, ci.person2_id,
    COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person1_id AND cr.conflict_time >= p.start_date AND cr.conflict_time < p.end_date) AS person1_conflicts,
    CASE
      WHEN COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person1_id AND cr.has_response = 1 AND cr.conflict_time >= p.start_date AND cr.conflict_time < p.end_date) = 0 THEN NULL
      ELSE ROUND(
        COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person1_id AND cr.has_response = 1 AND cr.has_escalation = 0 AND cr.conflict_time >= p.start_date AND cr.conflict_time < p.end_date)::numeric * 100.0 /
        COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person1_id AND cr.has_response = 1 AND cr.conflict_time >= p.start_date AND cr.conflict_time < p.end_date)::numeric, 1)
    END AS person2_repair_rate,
    COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person2_id AND cr.conflict_time >= p.start_date AND cr.conflict_time < p.end_date) AS person2_conflicts,
    CASE
      WHEN COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person2_id AND cr.has_response = 1 AND cr.conflict_time >= p.start_date AND cr.conflict_time < p.end_date) = 0 THEN NULL
      ELSE ROUND(
        COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person2_id AND cr.has_response = 1 AND cr.has_escalation = 0 AND cr.conflict_time >= p.start_date AND cr.conflict_time < p.end_date)::numeric * 100.0 /
        COUNT(*) FILTER (WHERE cr.conflict_starter_id = ci.person2_id AND cr.has_response = 1 AND cr.conflict_time >= p.start_date AND cr.conflict_time < p.end_date)::numeric, 1)
    END AS person1_repair_rate
  FROM periods p
  CROSS JOIN couple_info ci
  LEFT JOIN conflict_responses cr ON cr.conversation_id = ci.conversation_id
  GROUP BY p.period_num, p.period_name, ci.person1_id, ci.person2_id
)
SELECT * FROM period_repair ORDER BY period_num;
```

---

## SQL Templates: Weekly Rolling (8-Week Trailing)

### Weekly Affect Ratios

```sql
-- Weekly affect ratios with 56-day (8-week) trailing averages, 12 weeks
-- Replace {{person_id}} with actual person_id
WITH
  target_conversation AS (
    SELECT c.id AS conversation_id
    FROM conversation c
    JOIN conversation_participant cp ON cp.conversation_id = c.id
    WHERE cp.person_id = CAST({{person_id}} AS int) AND c.type = 'GROUP'
    LIMIT 1
  ),
  couple AS (
    SELECT tc.conversation_id, p.id AS person_id
    FROM target_conversation tc
    JOIN conversation_participant cp ON cp.conversation_id = tc.conversation_id
    JOIN persons p ON cp.person_id = p.id
    WHERE cp.role = 'MEMBER'
    LIMIT 2
  ),
  calendar_weeks AS (
    SELECT generate_series(
      date_trunc('week', CURRENT_DATE) - INTERVAL '11 weeks',
      date_trunc('week', CURRENT_DATE),
      '1 week'::interval
    )::date + 3 AS week_end_date
  ),
  weekly_affects AS (
    SELECT cw.week_end_date, cp.person_id,
      SUM(CASE WHEN me.affect IN (
        'Partner-Affection','Partner-Validation','Partner-Enthusiasm','Humor','Partner-Interest'
      ) THEN 1 ELSE 0 END) AS positive_count,
      SUM(CASE WHEN me.affect IN (
        'Partner-Criticism','Partner-Contempt','Partner-Defensiveness','Partner-Complaint',
        'Partner-Sadness','Partner-Anger','Partner-Belligerence','Partner-Domineering',
        'Partner-Fear / Tension','Partner-Threats','Partner-Disgust','Partner-Whining','Stonewalling'
      ) THEN 1 ELSE 0 END) AS negative_count
    FROM calendar_weeks cw
    CROSS JOIN couple cp
    JOIN message m ON m.conversation_id = cp.conversation_id
    JOIN person_contacts pc ON m.sender_person_contact_id = pc.id AND pc.person_id = cp.person_id
    JOIN message_enrichment me ON me.message_id = m.id
    WHERE m.provider_timestamp >= cw.week_end_date - INTERVAL '56 days'
      AND m.provider_timestamp < cw.week_end_date
    GROUP BY cw.week_end_date, cp.person_id
  ),
  weekly_ratios AS (
    SELECT week_end_date,
      MAX(CASE WHEN person_id = (SELECT MIN(person_id) FROM couple) THEN person_id END) AS person1_id,
      MAX(CASE WHEN person_id = (SELECT MAX(person_id) FROM couple) THEN person_id END) AS person2_id,
      SUM(CASE WHEN person_id = (SELECT MIN(person_id) FROM couple) THEN positive_count ELSE 0 END) AS p1_positive,
      SUM(CASE WHEN person_id = (SELECT MIN(person_id) FROM couple) THEN negative_count ELSE 0 END) AS p1_negative,
      SUM(CASE WHEN person_id = (SELECT MAX(person_id) FROM couple) THEN positive_count ELSE 0 END) AS p2_positive,
      SUM(CASE WHEN person_id = (SELECT MAX(person_id) FROM couple) THEN negative_count ELSE 0 END) AS p2_negative
    FROM weekly_affects
    GROUP BY week_end_date
  )
SELECT week_end_date, person1_id, person2_id,
  p1_positive, p1_negative,
  CASE WHEN p1_negative = 0 AND p1_positive > 0 THEN 100
       WHEN p1_negative = 0 THEN 0
       ELSE ROUND(p1_positive::numeric / p1_negative::numeric, 2) END AS person1_affect_ratio,
  p2_positive, p2_negative,
  CASE WHEN p2_negative = 0 AND p2_positive > 0 THEN 100
       WHEN p2_negative = 0 THEN 0
       ELSE ROUND(p2_positive::numeric / p2_negative::numeric, 2) END AS person2_affect_ratio,
  p1_positive + p2_positive AS couple_positive, p1_negative + p2_negative AS couple_negative,
  CASE WHEN (p1_negative + p2_negative) = 0 AND (p1_positive + p2_positive) > 0 THEN 100
       WHEN (p1_negative + p2_negative) = 0 THEN 0
       ELSE ROUND((p1_positive + p2_positive)::numeric / (p1_negative + p2_negative)::numeric, 2) END AS couple_affect_ratio,
  5 AS healthy_lower_bound, 30 AS healthy_upper_bound
FROM weekly_ratios
ORDER BY week_end_date;
```

### Weekly Repair Rates

```sql
-- Weekly repair rates with 56-day (8-week) trailing averages, 12 weeks
-- Replace {{person_id}} with actual person_id
WITH couple_info AS (
  SELECT
    c.id AS conversation_id,
    MIN(cp.person_id) AS person1_id, MAX(cp.person_id) AS person2_id
  FROM conversation c
  JOIN conversation_participant cp ON cp.conversation_id = c.id
  JOIN persons p ON cp.person_id = p.id
  WHERE c.type = 'GROUP' AND cp.role = 'MEMBER'
    AND CAST({{person_id}} AS int) IN (SELECT person_id FROM conversation_participant WHERE conversation_id = c.id)
  GROUP BY c.id
  HAVING COUNT(DISTINCT cp.person_id) = 2
  LIMIT 1
),
calendar_weeks AS (
  SELECT generate_series(
    date_trunc('week', CURRENT_DATE) - INTERVAL '11 weeks',
    date_trunc('week', CURRENT_DATE),
    '1 week'::interval
  )::date + 3 AS week_end_date
),
conflict_responses AS (
  SELECT
    m1.id as conflict_id, pc1.person_id as conflict_starter_id,
    m1.provider_timestamp as conflict_time, m1.conversation_id,
    ROW_NUMBER() OVER (PARTITION BY m1.id ORDER BY m2.provider_timestamp) as response_num,
    pc2.person_id as responder_id, me2.conflict_state as response_state
  FROM couple_info ci
  JOIN message m1 ON m1.conversation_id = ci.conversation_id
  JOIN person_contacts pc1 ON m1.sender_person_contact_id = pc1.id
  JOIN message_enrichment me1 ON me1.message_id = m1.id
  LEFT JOIN message m2 ON m2.conversation_id = m1.conversation_id AND m2.provider_timestamp > m1.provider_timestamp
  LEFT JOIN person_contacts pc2 ON m2.sender_person_contact_id = pc2.id
  LEFT JOIN message_enrichment me2 ON me2.message_id = m2.id
  WHERE me1.conflict_state IN ('New Conflict', 'New conflict', 'Escalation')
    AND m1.provider_timestamp >= (SELECT MIN(week_end_date) FROM calendar_weeks) - INTERVAL '56 days'
    AND m1.provider_timestamp < CURRENT_DATE
),
conflicts_with_status AS (
  SELECT
    cr.conflict_id, cr.conflict_starter_id, cr.conflict_time, ci.conversation_id,
    ci.person1_id, ci.person2_id,
    MAX(CASE WHEN cr.response_num IS NOT NULL THEN 1 ELSE 0 END) as has_response,
    MAX(CASE
      WHEN cr.response_num <= 5
        AND cr.responder_id <> cr.conflict_starter_id
        AND cr.response_state IN ('Escalation', 'New Conflict', 'New conflict', 'De-escalation Failed')
      THEN 1 ELSE 0
    END) as has_escalation
  FROM couple_info ci
  JOIN conflict_responses cr ON cr.conversation_id = ci.conversation_id
  WHERE cr.response_num <= 5 OR cr.response_num IS NULL
  GROUP BY cr.conflict_id, cr.conflict_starter_id, cr.conflict_time, ci.conversation_id, ci.person1_id, ci.person2_id
)
SELECT cw.week_end_date, ci.person1_id, ci.person2_id,
  COUNT(*) FILTER (WHERE cs.conflict_starter_id = ci.person1_id
    AND cs.conflict_time >= cw.week_end_date - INTERVAL '56 days' AND cs.conflict_time < cw.week_end_date
  ) AS person1_conflicts,
  CASE
    WHEN COUNT(*) FILTER (WHERE cs.conflict_starter_id = ci.person1_id AND cs.has_response = 1
      AND cs.conflict_time >= cw.week_end_date - INTERVAL '56 days' AND cs.conflict_time < cw.week_end_date) = 0 THEN NULL
    ELSE ROUND(
      COUNT(*) FILTER (WHERE cs.conflict_starter_id = ci.person1_id AND cs.has_response = 1 AND cs.has_escalation = 0
        AND cs.conflict_time >= cw.week_end_date - INTERVAL '56 days' AND cs.conflict_time < cw.week_end_date)::numeric * 100.0 /
      COUNT(*) FILTER (WHERE cs.conflict_starter_id = ci.person1_id AND cs.has_response = 1
        AND cs.conflict_time >= cw.week_end_date - INTERVAL '56 days' AND cs.conflict_time < cw.week_end_date)::numeric, 1)
  END AS person2_repair_rate,
  COUNT(*) FILTER (WHERE cs.conflict_starter_id = ci.person2_id
    AND cs.conflict_time >= cw.week_end_date - INTERVAL '56 days' AND cs.conflict_time < cw.week_end_date
  ) AS person2_conflicts,
  CASE
    WHEN COUNT(*) FILTER (WHERE cs.conflict_starter_id = ci.person2_id AND cs.has_response = 1
      AND cs.conflict_time >= cw.week_end_date - INTERVAL '56 days' AND cs.conflict_time < cw.week_end_date) = 0 THEN NULL
    ELSE ROUND(
      COUNT(*) FILTER (WHERE cs.conflict_starter_id = ci.person2_id AND cs.has_response = 1 AND cs.has_escalation = 0
        AND cs.conflict_time >= cw.week_end_date - INTERVAL '56 days' AND cs.conflict_time < cw.week_end_date)::numeric * 100.0 /
      COUNT(*) FILTER (WHERE cs.conflict_starter_id = ci.person2_id AND cs.has_response = 1
        AND cs.conflict_time >= cw.week_end_date - INTERVAL '56 days' AND cs.conflict_time < cw.week_end_date)::numeric, 1)
  END AS person1_repair_rate,
  75 AS healthy_repair_threshold
FROM calendar_weeks cw
CROSS JOIN couple_info ci
LEFT JOIN conflicts_with_status cs ON cs.conversation_id = ci.conversation_id
GROUP BY cw.week_end_date, ci.person1_id, ci.person2_id
ORDER BY cw.week_end_date;
```

---

## Single Value Queries (Quick Checks)

### Current Affect Ratio (Last 56 Days)

```sql
-- Quick-check: current couple affect ratio (last 56 days)
-- Replace {{person_id}} with actual person_id
WITH couple AS (
  SELECT c.id AS conversation_id
  FROM conversation c
  JOIN conversation_participant cp ON cp.conversation_id = c.id
  WHERE cp.person_id = {{person_id}}::int AND c.type = 'GROUP'
  LIMIT 1
)
SELECT
  CASE
    WHEN COUNT(*) FILTER (WHERE me.affect IN (
      'Partner-Criticism','Partner-Contempt','Partner-Defensiveness','Partner-Complaint',
      'Partner-Sadness','Partner-Anger','Partner-Belligerence','Partner-Domineering',
      'Partner-Fear / Tension','Partner-Threats','Partner-Disgust','Partner-Whining','Stonewalling'
    )) = 0 AND COUNT(*) FILTER (WHERE me.affect IN (
      'Partner-Affection','Partner-Validation','Partner-Enthusiasm','Humor','Partner-Interest'
    )) > 0 THEN 100
    WHEN COUNT(*) FILTER (WHERE me.affect IN (
      'Partner-Criticism','Partner-Contempt','Partner-Defensiveness','Partner-Complaint',
      'Partner-Sadness','Partner-Anger','Partner-Belligerence','Partner-Domineering',
      'Partner-Fear / Tension','Partner-Threats','Partner-Disgust','Partner-Whining','Stonewalling'
    )) = 0 THEN 0
    ELSE ROUND(
      COUNT(*) FILTER (WHERE me.affect IN (
        'Partner-Affection','Partner-Validation','Partner-Enthusiasm','Humor','Partner-Interest'
      ))::numeric /
      COUNT(*) FILTER (WHERE me.affect IN (
        'Partner-Criticism','Partner-Contempt','Partner-Defensiveness','Partner-Complaint',
        'Partner-Sadness','Partner-Anger','Partner-Belligerence','Partner-Domineering',
        'Partner-Fear / Tension','Partner-Threats','Partner-Disgust','Partner-Whining','Stonewalling'
      ))::numeric, 2)
  END AS affect_ratio
FROM couple cp
JOIN message m ON m.conversation_id = cp.conversation_id
JOIN message_enrichment me ON me.message_id = m.id
WHERE m.provider_timestamp >= CURRENT_DATE - INTERVAL '56 days'
  AND m.provider_timestamp < CURRENT_DATE;
```

### Current Repair Rate (Last 56 Days)

```sql
-- Quick-check: current repair rate (last 56 days)
-- Replace {{person_id}} with actual person_id
WITH couple_info AS (
  SELECT c.id AS conversation_id,
    MIN(cp.person_id) AS person1_id, MAX(cp.person_id) AS person2_id
  FROM conversation c
  JOIN conversation_participant cp ON cp.conversation_id = c.id
  WHERE c.type = 'GROUP' AND cp.role = 'MEMBER'
    AND {{person_id}}::int IN (SELECT person_id FROM conversation_participant WHERE conversation_id = c.id)
  GROUP BY c.id
  HAVING COUNT(DISTINCT cp.person_id) = 2
  LIMIT 1
),
conflicts_by_person2 AS (
  SELECT m.id AS conflict_message_id, m.provider_timestamp AS conflict_timestamp, ci.conversation_id,
    EXISTS (
      SELECT 1 FROM message m2
      WHERE m2.conversation_id = ci.conversation_id AND m2.provider_timestamp > m.provider_timestamp
      LIMIT 1
    ) AS has_response,
    EXISTS (
      SELECT 1 FROM message m2
      JOIN person_contacts pc2 ON m2.sender_person_contact_id = pc2.id
      JOIN message_enrichment me2 ON me2.message_id = m2.id
      WHERE m2.conversation_id = ci.conversation_id
        AND m2.provider_timestamp > m.provider_timestamp
        AND pc2.person_id = ci.person1_id
        AND m2.provider_timestamp <= (
          SELECT MAX(provider_timestamp) FROM (
            SELECT m3.provider_timestamp FROM message m3
            WHERE m3.conversation_id = ci.conversation_id AND m3.provider_timestamp > m.provider_timestamp
            ORDER BY m3.provider_timestamp LIMIT 5
          ) AS next_5
        )
        AND me2.conflict_state IN ('Escalation', 'New Conflict', 'New conflict', 'De-escalation Failed')
    ) AS has_escalation
  FROM couple_info ci
  JOIN message m ON m.conversation_id = ci.conversation_id
  JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
  JOIN message_enrichment me ON me.message_id = m.id
  WHERE me.conflict_state IN ('New Conflict', 'New conflict', 'Escalation')
    AND pc.person_id = ci.person2_id
    AND m.provider_timestamp >= CURRENT_DATE - INTERVAL '56 days'
    AND m.provider_timestamp < CURRENT_DATE
)
SELECT
  CASE
    WHEN COUNT(*) FILTER (WHERE has_response) = 0 THEN NULL
    ELSE ROUND(
      COUNT(*) FILTER (WHERE has_response AND NOT has_escalation)::numeric * 100.0 /
      COUNT(*) FILTER (WHERE has_response)::numeric, 1)
  END AS repair_rate
FROM conflicts_by_person2;
```

---

## Diagnostic Queries (Run for Each Inflection Point)

**For each inflection point, run ALL 5 queries. Replace `{{inflection_start_date}}`, `{{inflection_end_date}}`, `{{person_id}}`.**

### 1. Affect Pattern Changes

```sql
-- Compare affects before (14d) vs during inflection period
WITH inflection_period AS (
  SELECT '{{inflection_start_date}}'::date AS start_date, '{{inflection_end_date}}'::date AS end_date
),
before_period AS (
  SELECT (SELECT start_date FROM inflection_period) - INTERVAL '14 days' AS start_date,
         (SELECT start_date FROM inflection_period) AS end_date
),
couple_conv AS (
  SELECT c.id AS conversation_id FROM conversation c
  JOIN conversation_participant cp ON cp.conversation_id = c.id
  WHERE cp.person_id = {{person_id}}::int AND c.type = 'GROUP' LIMIT 1
),
before_affects AS (
  SELECT me.affect, COUNT(*) as count
  FROM couple_conv cc JOIN message m ON m.conversation_id = cc.conversation_id
  JOIN message_enrichment me ON me.message_id = m.id CROSS JOIN before_period bp
  WHERE m.provider_timestamp >= bp.start_date AND m.provider_timestamp < bp.end_date
    AND me.affect IS NOT NULL AND me.affect <> 'Neutral'
  GROUP BY me.affect
),
during_affects AS (
  SELECT me.affect, COUNT(*) as count
  FROM couple_conv cc JOIN message m ON m.conversation_id = cc.conversation_id
  JOIN message_enrichment me ON me.message_id = m.id CROSS JOIN inflection_period ip
  WHERE m.provider_timestamp >= ip.start_date AND m.provider_timestamp < ip.end_date
    AND me.affect IS NOT NULL AND me.affect <> 'Neutral'
  GROUP BY me.affect
)
SELECT COALESCE(b.affect, d.affect) as affect,
  COALESCE(b.count, 0) as before_count, COALESCE(d.count, 0) as during_count,
  COALESCE(d.count, 0) - COALESCE(b.count, 0) as change,
  CASE WHEN COALESCE(b.count, 0) = 0 THEN 'NEW'
       WHEN COALESCE(d.count, 0) = 0 THEN 'DISAPPEARED'
       ELSE ROUND(((COALESCE(d.count, 0) - COALESCE(b.count, 0))::numeric / b.count::numeric) * 100, 1)::text || '%'
  END as percent_change
FROM before_affects b FULL OUTER JOIN during_affects d ON b.affect = d.affect
ORDER BY ABS(COALESCE(d.count, 0) - COALESCE(b.count, 0)) DESC;
```

### 2. Topic Changes

```sql
-- Compare topics before (14d) vs during inflection period
WITH inflection_period AS (
  SELECT '{{inflection_start_date}}'::date AS start_date, '{{inflection_end_date}}'::date AS end_date
),
before_period AS (
  SELECT (SELECT start_date FROM inflection_period) - INTERVAL '14 days' AS start_date,
         (SELECT start_date FROM inflection_period) AS end_date
),
couple_conv AS (
  SELECT c.id AS conversation_id FROM conversation c
  JOIN conversation_participant cp ON cp.conversation_id = c.id
  WHERE cp.person_id = {{person_id}}::int AND c.type = 'GROUP' LIMIT 1
),
before_topics AS (
  SELECT me.topic, COUNT(*) as count
  FROM couple_conv cc JOIN message m ON m.conversation_id = cc.conversation_id
  JOIN message_enrichment me ON me.message_id = m.id CROSS JOIN before_period bp
  WHERE m.provider_timestamp >= bp.start_date AND m.provider_timestamp < bp.end_date
    AND me.topic IS NOT NULL AND me.topic <> ''
  GROUP BY me.topic
),
during_topics AS (
  SELECT me.topic, COUNT(*) as count
  FROM couple_conv cc JOIN message m ON m.conversation_id = cc.conversation_id
  JOIN message_enrichment me ON me.message_id = m.id CROSS JOIN inflection_period ip
  WHERE m.provider_timestamp >= ip.start_date AND m.provider_timestamp < ip.end_date
    AND me.topic IS NOT NULL AND me.topic <> ''
  GROUP BY me.topic
)
SELECT COALESCE(b.topic, d.topic) as topic,
  COALESCE(b.count, 0) as before_count, COALESCE(d.count, 0) as during_count,
  COALESCE(d.count, 0) - COALESCE(b.count, 0) as change,
  CASE WHEN COALESCE(b.count, 0) = 0 THEN 'NEW TOPIC'
       WHEN COALESCE(d.count, 0) = 0 THEN 'DROPPED'
       ELSE ROUND(((COALESCE(d.count, 0) - COALESCE(b.count, 0))::numeric / b.count::numeric) * 100, 1)::text || '%'
  END as percent_change
FROM before_topics b FULL OUTER JOIN during_topics d ON b.topic = d.topic
WHERE COALESCE(b.count, 0) + COALESCE(d.count, 0) >= 2
ORDER BY ABS(COALESCE(d.count, 0) - COALESCE(b.count, 0)) DESC LIMIT 20;
```

### 3. Conflict State Changes

```sql
-- Compare conflict introduction/escalation before vs during inflection
WITH inflection_period AS (
  SELECT '{{inflection_start_date}}'::date AS start_date, '{{inflection_end_date}}'::date AS end_date
),
before_period AS (
  SELECT (SELECT start_date FROM inflection_period) - INTERVAL '14 days' AS start_date,
         (SELECT start_date FROM inflection_period) AS end_date
),
couple_conv AS (
  SELECT c.id AS conversation_id FROM conversation c
  JOIN conversation_participant cp ON cp.conversation_id = c.id
  WHERE cp.person_id = {{person_id}}::int AND c.type = 'GROUP' LIMIT 1
)
SELECT period,
  SUM(new_conflicts) as new_conflicts, SUM(escalations) as escalations,
  SUM(deescalation_success) as deescalation_success, SUM(deescalation_failed) as deescalation_failed,
  CASE WHEN SUM(new_conflicts) > 0
    THEN ROUND((SUM(escalations)::numeric / SUM(new_conflicts)::numeric) * 100, 1) ELSE 0
  END as escalation_rate
FROM (
  SELECT 'Before' as period,
    COUNT(*) FILTER (WHERE me.conflict_state IN ('New Conflict', 'New conflict')) as new_conflicts,
    COUNT(*) FILTER (WHERE me.conflict_state = 'Escalation') as escalations,
    COUNT(*) FILTER (WHERE me.conflict_state = 'De-escalation Successful') as deescalation_success,
    COUNT(*) FILTER (WHERE me.conflict_state = 'De-escalation Failed') as deescalation_failed
  FROM couple_conv cc JOIN message m ON m.conversation_id = cc.conversation_id
  JOIN message_enrichment me ON me.message_id = m.id CROSS JOIN before_period bp
  WHERE m.provider_timestamp >= bp.start_date AND m.provider_timestamp < bp.end_date
  UNION ALL
  SELECT 'During' as period,
    COUNT(*) FILTER (WHERE me.conflict_state IN ('New Conflict', 'New conflict')) as new_conflicts,
    COUNT(*) FILTER (WHERE me.conflict_state = 'Escalation') as escalations,
    COUNT(*) FILTER (WHERE me.conflict_state = 'De-escalation Successful') as deescalation_success,
    COUNT(*) FILTER (WHERE me.conflict_state = 'De-escalation Failed') as deescalation_failed
  FROM couple_conv cc JOIN message m ON m.conversation_id = cc.conversation_id
  JOIN message_enrichment me ON me.message_id = m.id CROSS JOIN inflection_period ip
  WHERE m.provider_timestamp >= ip.start_date AND m.provider_timestamp < ip.end_date
) subq
GROUP BY period ORDER BY period;
```

### 4. Message Content Patterns

```sql
-- Search for defensive/problematic language during inflection period
WITH couple_conv AS (
  SELECT c.id AS conversation_id FROM conversation c
  JOIN conversation_participant cp ON cp.conversation_id = c.id
  WHERE cp.person_id = {{person_id}}::int AND c.type = 'GROUP' LIMIT 1
)
SELECT m.provider_timestamp, p.id as sender_id, m.content,
  me.affect, me.conflict_state, me.topic, me.communication_pattern,
  CASE
    WHEN m.content ILIKE '%but you%' OR m.content ILIKE '%your fault%' THEN 'Defensive'
    WHEN m.content ILIKE '%always%' OR m.content ILIKE '%never%' THEN 'Overgeneralization'
    WHEN m.content ILIKE '%whatever%' OR m.content ILIKE '%seriously%' THEN 'Contempt'
    WHEN m.content ILIKE '%don''t want to talk%' OR m.content ILIKE '%not discussing%' THEN 'Stonewalling'
  END as pattern_detected
FROM couple_conv cc
JOIN message m ON m.conversation_id = cc.conversation_id
JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
JOIN persons p ON pc.person_id = p.id
LEFT JOIN message_enrichment me ON me.message_id = m.id
WHERE m.provider_timestamp >= '{{inflection_start_date}}'::date
  AND m.provider_timestamp < '{{inflection_end_date}}'::date
  AND (m.content ILIKE '%but you%' OR m.content ILIKE '%your fault%'
    OR m.content ILIKE '%always%' OR m.content ILIKE '%never%'
    OR m.content ILIKE '%whatever%' OR m.content ILIKE '%seriously%'
    OR m.content ILIKE '%don''t want to talk%' OR m.content ILIKE '%not discussing%')
ORDER BY m.provider_timestamp;
```

### 5. Communication Pattern Changes

```sql
-- Compare communication patterns before vs during inflection
WITH inflection_period AS (
  SELECT '{{inflection_start_date}}'::date AS start_date, '{{inflection_end_date}}'::date AS end_date
),
before_period AS (
  SELECT (SELECT start_date FROM inflection_period) - INTERVAL '14 days' AS start_date,
         (SELECT start_date FROM inflection_period) AS end_date
),
couple_conv AS (
  SELECT c.id AS conversation_id FROM conversation c
  JOIN conversation_participant cp ON cp.conversation_id = c.id
  WHERE cp.person_id = {{person_id}}::int AND c.type = 'GROUP' LIMIT 1
),
before_patterns AS (
  SELECT me.communication_pattern, COUNT(*) as count
  FROM couple_conv cc JOIN message m ON m.conversation_id = cc.conversation_id
  JOIN message_enrichment me ON me.message_id = m.id CROSS JOIN before_period bp
  WHERE m.provider_timestamp >= bp.start_date AND m.provider_timestamp < bp.end_date
    AND me.communication_pattern IS NOT NULL
  GROUP BY me.communication_pattern
),
during_patterns AS (
  SELECT me.communication_pattern, COUNT(*) as count
  FROM couple_conv cc JOIN message m ON m.conversation_id = cc.conversation_id
  JOIN message_enrichment me ON me.message_id = m.id CROSS JOIN inflection_period ip
  WHERE m.provider_timestamp >= ip.start_date AND m.provider_timestamp < ip.end_date
    AND me.communication_pattern IS NOT NULL
  GROUP BY me.communication_pattern
)
SELECT COALESCE(b.communication_pattern, d.communication_pattern) as pattern,
  COALESCE(b.count, 0) as before_count, COALESCE(d.count, 0) as during_count,
  COALESCE(d.count, 0) - COALESCE(b.count, 0) as change,
  CASE WHEN COALESCE(b.count, 0) = 0 THEN 'NEW PATTERN'
       WHEN COALESCE(d.count, 0) = 0 THEN 'DISAPPEARED'
       ELSE ROUND(((COALESCE(d.count, 0) - COALESCE(b.count, 0))::numeric / b.count::numeric) * 100, 1)::text || '%'
  END as percent_change
FROM before_patterns b FULL OUTER JOIN during_patterns d ON b.communication_pattern = d.communication_pattern
ORDER BY ABS(COALESCE(d.count, 0) - COALESCE(b.count, 0)) DESC;
```

---

## Causal Investigation (Messages Around Inflection Points)

**For each inflection point date, query messages +/-3 days:**

```sql
-- Messages around inflection point for causal analysis
WITH couple_info AS (
  SELECT c.id AS conversation_id
  FROM conversation c
  JOIN conversation_participant cp ON cp.conversation_id = c.id
  WHERE c.type = 'GROUP' AND cp.role = 'MEMBER'
    AND {{person_id}}::int IN (
      SELECT person_id FROM conversation_participant WHERE conversation_id = c.id
    )
  LIMIT 1
)
SELECT m.provider_timestamp, p.id AS sender_id, m.content,
  me.affect, me.conflict_state, me.topic, me.communication_pattern
FROM couple_info ci
JOIN message m ON m.conversation_id = ci.conversation_id
JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
JOIN persons p ON pc.person_id = p.id
LEFT JOIN message_enrichment me ON me.message_id = m.id
WHERE m.provider_timestamp >= '{{inflection_date}}'::date - INTERVAL '3 days'
  AND m.provider_timestamp < '{{inflection_date}}'::date + INTERVAL '3 days'
ORDER BY m.provider_timestamp;
```

**Analyze:** Topics during decline (me.topic), conflict states (New Conflict, Escalation, De-escalation Failed), communication patterns (Four Horsemen, Repair Attempts), affects (Partner-Criticism, Partner-Contempt, etc.).

---

## Violations

- Running only affect ratios OR only repair rates (must run BOTH)
- Not calculating trends / month-over-month changes
- Identifying inflection points but skipping diagnostic queries
- Running fewer than 5 diagnostic queries per inflection point
- Incomplete assessment (missing either metric in any section)
- Not identifying conflict pattern when ratios >30:1

---

## Clinical Tips

1. **Always run both metrics** - affect ratio + repair rate measure different aspects
2. **Look for divergence** - one partner may have healthy affect but poor repair
3. **NULL repair rates are concerning** - indicates stonewalling/avoidance
4. **Very high ratios (>30) need investigation** - may indicate avoidance, not health
5. **Inflection points matter more than absolutes** - sudden changes = triggering events
6. **Investigate +/-3 days around inflection** - causal conversations usually nearby
7. **Four Horsemen = red flags** - Criticism, Contempt, Defensiveness, Stonewalling
8. **Compare to couple's OWN baseline** - generic thresholds are starting points
