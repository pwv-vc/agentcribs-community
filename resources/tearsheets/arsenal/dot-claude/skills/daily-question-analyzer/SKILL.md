---
name: daily-question-analyzer
description: Analyze daily question response rates, pair completion, and post-reveal engagement. Supports flexible time ranges.
---

# daily-question-analyzer Skill

Analyze daily question feature engagement including response rates, pair completion, and post-reveal feedback.

## When to Use

Use this skill when:
- "Show me daily question stats"
- "How are daily questions performing?"
- "What's the response rate for daily questions?"
- "Are couples responding to daily questions?"
- "Check daily question engagement"
- "Daily question analysis for last [X days/hours]"

---

## 🔒 Privacy: Default to Aggregates

**CRITICAL:** Do NOT reveal raw response text or message content unless the user explicitly asks.

**Default behavior:**
- ✅ Show counts, percentages, user IDs
- ✅ Show response status (responded/pending/expired)
- ✅ Show timestamps
- ❌ Do NOT show `response_text` content
- ❌ Do NOT show `question_text` content
- ❌ Do NOT show message `content` from conversations

**When user explicitly asks for content:**
- "Show me what they responded"
- "What did they say?"
- "Show the actual responses"
- Then you MAY include `response_text` and message content

---

## Duration Parameter

This skill supports flexible time ranges. Default is **24 hours**.

| User says | Interval to use |
|-----------|-----------------|
| "last 24 hours" / "today" | `INTERVAL '24 hours'` |
| "last 3 days" | `INTERVAL '3 days'` |
| "last week" / "last 7 days" | `INTERVAL '7 days'` |
| "last 2 weeks" | `INTERVAL '14 days'` |
| "last month" / "last 30 days" | `INTERVAL '30 days'` |
| (no duration specified) | `INTERVAL '24 hours'` (default) |

Replace `{{INTERVAL}}` in queries below with the appropriate interval.

---

## Step 1: Response Rate Overview

Run this query to get high-level stats.

**⚠️ NOTE:** Each question day creates 2 records (one per partner). Group by `(group_conversation_id, question_day)` to count question-days correctly.

```sql
-- Daily Question Response Stats (replace {{INTERVAL}})
WITH period_data AS (
  SELECT *
  FROM daily_question_response
  WHERE created_at >= NOW() - {{INTERVAL}}
),
question_day_stats AS (
  SELECT
    group_conversation_id,
    question_day,
    COUNT(*) as records_for_day,
    COUNT(responded_at) as responded_for_day
  FROM period_data
  GROUP BY group_conversation_id, question_day
)
SELECT
  (SELECT COUNT(*) FROM period_data) as total_records,
  (SELECT COUNT(*) FROM period_data WHERE responded_at IS NOT NULL) as total_responded,
  (SELECT COUNT(*) FROM period_data WHERE responded_at IS NULL AND NOW() < expires_at) as pending,
  (SELECT COUNT(*) FROM period_data WHERE responded_at IS NULL AND NOW() >= expires_at) as expired,
  (SELECT COUNT(*) FROM question_day_stats WHERE records_for_day = 2) as total_question_days,
  (SELECT COUNT(*) FROM question_day_stats WHERE records_for_day = 2 AND responded_for_day = 2) as question_days_both_responded,
  ROUND(100.0 * (SELECT COUNT(*) FROM period_data WHERE responded_at IS NOT NULL) /
    NULLIF((SELECT COUNT(*) FROM period_data), 0), 1) as individual_response_rate_pct,
  ROUND(100.0 * (SELECT COUNT(*) FROM question_day_stats WHERE records_for_day = 2 AND responded_for_day = 2) /
    NULLIF((SELECT COUNT(*) FROM question_day_stats WHERE records_for_day = 2), 0), 1) as pair_completion_rate_pct;
```

**Example output:**
```
 total_records | total_responded | pending | expired | total_question_days | question_days_both_responded | individual_response_rate_pct | pair_completion_rate_pct
---------------+-----------------+---------+---------+---------------------+------------------------------+------------------------------+--------------------------
           334 |              95 |      27 |     212 |                 167 |                           35 |                         28.4 |                     21.0
```

**Column meanings:**
- `total_records`: Individual response records (2 per question-day)
- `total_question_days`: Unique (couple, day) combinations where both partners received the question
- `question_days_both_responded`: Question-days where BOTH partners answered
- `pair_completion_rate_pct`: % of question-days with both partners responding

---

## Step 2: Response Status Breakdown

Get breakdown by status with user IDs:

```sql
-- Response status breakdown (replace {{INTERVAL}})
WITH period_data AS (
  SELECT
    dqr.*,
    CASE
      WHEN responded_at IS NOT NULL THEN 'responded'
      WHEN NOW() >= expires_at THEN 'expired'
      ELSE 'pending'
    END as status
  FROM daily_question_response dqr
  WHERE dqr.created_at >= NOW() - {{INTERVAL}}
)
SELECT
  status,
  COUNT(*) as count,
  STRING_AGG(user_id::text, ', ' ORDER BY user_id) as users
FROM period_data
GROUP BY status
ORDER BY
  CASE status
    WHEN 'responded' THEN 1
    WHEN 'pending' THEN 2
    WHEN 'expired' THEN 3
  END;
```

---

## Step 3: Identify Pairs Where Both Responded

Find completed pairs for post-reveal analysis.

**⚠️ NOTE:** Each question day creates new records. Group by `(group_conversation_id, question_day)` to count question-days, not unique couples.

```sql
-- Question-days where both partners responded (replace {{INTERVAL}})
-- NOTE: Returns IDs and names only, NOT response content (privacy)
WITH period_data AS (
  SELECT * FROM daily_question_response
  WHERE created_at >= NOW() - {{INTERVAL}}
),
both_responded_days AS (
  SELECT group_conversation_id, question_day
  FROM period_data
  GROUP BY group_conversation_id, question_day
  HAVING COUNT(responded_at) = 2 AND COUNT(*) = 2
)
SELECT
  dqr.group_conversation_id,
  dqr.question_day,
  dqr.user_id,
  dqr.responded_at,
  dqr.created_at
FROM daily_question_response dqr
JOIN both_responded_days brd ON dqr.group_conversation_id = brd.group_conversation_id
  AND dqr.question_day = brd.question_day
WHERE dqr.created_at >= NOW() - {{INTERVAL}}
ORDER BY dqr.group_conversation_id, dqr.question_day, dqr.responded_at;
```

**Output includes:** conversation IDs, user IDs, question day, timestamps
**Output excludes:** response_text, question_text (privacy)

---

## Step 4: Post-Reveal Engagement Analysis

After both partners respond, the coach sends a "Daily Question Reveal" message ~30 minutes later.

**⚠️ CRITICAL:** The reveal happens ~30 min AFTER `responded_at`. You must find the actual reveal message, not use `responded_at` as the reveal time.

### 4a: Find the Actual Reveal Messages

```sql
-- Find actual reveal messages from coach (replace {{INTERVAL}})
WITH period_data AS (
  SELECT * FROM daily_question_response
  WHERE created_at >= NOW() - {{INTERVAL}}
),
both_responded_days AS (
  SELECT
    group_conversation_id,
    question_day,
    MAX(responded_at) as last_response_time
  FROM period_data
  GROUP BY group_conversation_id, question_day
  HAVING COUNT(responded_at) = 2 AND COUNT(*) = 2
),
reveal_messages AS (
  SELECT DISTINCT ON (br.group_conversation_id, br.question_day)
    br.group_conversation_id,
    br.question_day,
    m.id as reveal_message_id,
    m.provider_timestamp as actual_reveal_time
  FROM both_responded_days br
  JOIN message m ON m.conversation_id = br.group_conversation_id
    AND m.provider_timestamp > br.last_response_time
    AND m.content LIKE 'Daily Question Reveal%'
  JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
  JOIN conversation_participant cp ON cp.conversation_id = br.group_conversation_id
    AND cp.person_id = pc.person_id
    AND cp.role = 'THERAPIST'
  ORDER BY br.group_conversation_id, br.question_day, m.provider_timestamp
)
SELECT * FROM reveal_messages ORDER BY group_conversation_id, question_day;
```

### 4b: Find Member Messages After Reveal (within 15 min)

```sql
-- Post-reveal messages from members within 15 minutes (replace {{INTERVAL}})
-- Use tight window to capture reveal-RELATED engagement, not regular conversation
WITH period_data AS (
  SELECT * FROM daily_question_response
  WHERE created_at >= NOW() - {{INTERVAL}}
),
both_responded_days AS (
  SELECT
    group_conversation_id,
    question_day,
    MAX(responded_at) as last_response_time
  FROM period_data
  GROUP BY group_conversation_id, question_day
  HAVING COUNT(responded_at) = 2 AND COUNT(*) = 2
),
reveal_messages AS (
  SELECT DISTINCT ON (br.group_conversation_id, br.question_day)
    br.group_conversation_id,
    br.question_day,
    m.provider_timestamp as actual_reveal_time
  FROM both_responded_days br
  JOIN message m ON m.conversation_id = br.group_conversation_id
    AND m.provider_timestamp > br.last_response_time
    AND m.content LIKE 'Daily Question Reveal%'
  JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
  JOIN conversation_participant cp ON cp.conversation_id = br.group_conversation_id
    AND cp.person_id = pc.person_id
    AND cp.role = 'THERAPIST'
  ORDER BY br.group_conversation_id, br.question_day, m.provider_timestamp
)
SELECT
  rm.group_conversation_id,
  rm.question_day,
  p.id as sender_id,
  CASE WHEN m.provider_data->>'reaction_id' IS NOT NULL THEN 'REACTION' ELSE 'MESSAGE' END as type,
  LENGTH(m.content) as message_length,
  ROUND(EXTRACT(EPOCH FROM (m.provider_timestamp - rm.actual_reveal_time))/60) as minutes_after_reveal
FROM reveal_messages rm
JOIN message m ON m.conversation_id = rm.group_conversation_id
  AND m.provider_timestamp > rm.actual_reveal_time
  AND m.provider_timestamp < rm.actual_reveal_time + INTERVAL '15 minutes'
JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
JOIN persons p ON pc.person_id = p.id
JOIN conversation_participant cp ON cp.conversation_id = rm.group_conversation_id
  AND cp.person_id = pc.person_id
  AND cp.role = 'MEMBER'
ORDER BY rm.group_conversation_id, rm.question_day, m.provider_timestamp;
```

---

## Step 5: Aggregate Post-Reveal Engagement

Summarize engagement across all completed pairs using the **actual reveal message timestamp**:

```sql
-- Aggregate post-reveal engagement (replace {{INTERVAL}})
-- Uses actual reveal message time, not responded_at
WITH period_data AS (
  SELECT * FROM daily_question_response
  WHERE created_at >= NOW() - {{INTERVAL}}
),
both_responded_days AS (
  SELECT
    group_conversation_id,
    question_day,
    MAX(responded_at) as last_response_time
  FROM period_data
  GROUP BY group_conversation_id, question_day
  HAVING COUNT(responded_at) = 2 AND COUNT(*) = 2
),
reveal_messages AS (
  SELECT DISTINCT ON (br.group_conversation_id, br.question_day)
    br.group_conversation_id,
    br.question_day,
    m.provider_timestamp as actual_reveal_time
  FROM both_responded_days br
  JOIN message m ON m.conversation_id = br.group_conversation_id
    AND m.provider_timestamp > br.last_response_time
    AND m.content LIKE 'Daily Question Reveal%'
  JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
  JOIN conversation_participant cp ON cp.conversation_id = br.group_conversation_id
    AND cp.person_id = pc.person_id
    AND cp.role = 'THERAPIST'
  ORDER BY br.group_conversation_id, br.question_day, m.provider_timestamp
),
-- Count reactions within 15 min of reveal
reveal_reactions AS (
  SELECT
    rm.group_conversation_id,
    rm.question_day,
    COUNT(*) as reaction_count
  FROM reveal_messages rm
  JOIN message m ON m.conversation_id = rm.group_conversation_id
    AND m.provider_timestamp > rm.actual_reveal_time
    AND m.provider_timestamp < rm.actual_reveal_time + INTERVAL '15 minutes'
    AND m.provider_data->>'reaction_id' IS NOT NULL
  JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
  JOIN conversation_participant cp ON cp.conversation_id = rm.group_conversation_id
    AND cp.person_id = pc.person_id
    AND cp.role = 'MEMBER'
  GROUP BY rm.group_conversation_id, rm.question_day
),
-- Count messages within 10 min of reveal (likely reveal-related)
quick_messages AS (
  SELECT
    rm.group_conversation_id,
    rm.question_day,
    COUNT(*) as message_count
  FROM reveal_messages rm
  JOIN message m ON m.conversation_id = rm.group_conversation_id
    AND m.provider_timestamp > rm.actual_reveal_time
    AND m.provider_timestamp < rm.actual_reveal_time + INTERVAL '10 minutes'
    AND m.provider_data->>'reaction_id' IS NULL
  JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
  JOIN conversation_participant cp ON cp.conversation_id = rm.group_conversation_id
    AND cp.person_id = pc.person_id
    AND cp.role = 'MEMBER'
  GROUP BY rm.group_conversation_id, rm.question_day
)
SELECT
  (SELECT COUNT(*) FROM reveal_messages) as total_reveals,
  (SELECT COUNT(*) FROM reveal_reactions) as reveals_with_reactions,
  (SELECT COUNT(*) FROM quick_messages) as reveals_with_quick_messages,
  (SELECT COUNT(DISTINCT (rm.group_conversation_id, rm.question_day))
   FROM reveal_messages rm
   LEFT JOIN reveal_reactions rr ON rm.group_conversation_id = rr.group_conversation_id
     AND rm.question_day = rr.question_day
   LEFT JOIN quick_messages qm ON rm.group_conversation_id = qm.group_conversation_id
     AND rm.question_day = qm.question_day
   WHERE COALESCE(rr.reaction_count, 0) > 0 OR COALESCE(qm.message_count, 0) > 0
  ) as reveals_with_any_engagement;
```

**Interpretation:**
- `reveals_with_reactions`: Couples who reacted (Loved, Laughed at, etc.) to the reveal
- `reveals_with_quick_messages`: Couples who messaged within 10 min (likely reveal-related)
- `reveals_with_any_engagement`: Union of above (best measure of reveal engagement)

---

## Step 6: Verify Engagement is Reveal-Related (CRITICAL)

**⚠️ IMPORTANT:** A tight time window (10-15 min) reduces noise but does NOT guarantee messages are reveal-related. You MUST inspect actual message content before claiming "post-reveal engagement."

### 6a: Inspect Message Content

When reporting engagement stats, **always verify a sample** by looking at actual content:

```sql
-- Inspect actual post-reveal message content (replace {{INTERVAL}})
-- Use this to VERIFY messages are reveal-related, not coincidental
WITH period_data AS (
  SELECT * FROM daily_question_response
  WHERE created_at >= NOW() - {{INTERVAL}}
),
both_responded_days AS (
  SELECT
    group_conversation_id,
    question_day,
    MAX(responded_at) as last_response_time
  FROM period_data
  GROUP BY group_conversation_id, question_day
  HAVING COUNT(responded_at) = 2 AND COUNT(*) = 2
),
reveal_messages AS (
  SELECT DISTINCT ON (br.group_conversation_id, br.question_day)
    br.group_conversation_id,
    br.question_day,
    m.provider_timestamp as actual_reveal_time
  FROM both_responded_days br
  JOIN message m ON m.conversation_id = br.group_conversation_id
    AND m.provider_timestamp > br.last_response_time
    AND m.content LIKE 'Daily Question Reveal%'
  JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
  JOIN conversation_participant cp ON cp.conversation_id = br.group_conversation_id
    AND cp.person_id = pc.person_id
    AND cp.role = 'THERAPIST'
  ORDER BY br.group_conversation_id, br.question_day, m.provider_timestamp
)
SELECT
  rm.group_conversation_id,
  rm.question_day,
  p.id as sender_id,
  CASE WHEN m.provider_data->>'reaction_id' IS NOT NULL THEN 'REACTION' ELSE 'MESSAGE' END as type,
  LEFT(m.content, 150) as content_preview,
  ROUND(EXTRACT(EPOCH FROM (m.provider_timestamp - rm.actual_reveal_time))/60) as minutes_after_reveal
FROM reveal_messages rm
JOIN message m ON m.conversation_id = rm.group_conversation_id
  AND m.provider_timestamp > rm.actual_reveal_time
  AND m.provider_timestamp < rm.actual_reveal_time + INTERVAL '15 minutes'
JOIN person_contacts pc ON m.sender_person_contact_id = pc.id
JOIN persons p ON pc.person_id = p.id
JOIN conversation_participant cp ON cp.conversation_id = rm.group_conversation_id
  AND cp.person_id = pc.person_id
  AND cp.role = 'MEMBER'
ORDER BY rm.group_conversation_id, rm.question_day, m.provider_timestamp;
```

### 6b: Classify Messages as Reveal-Related or Not

**Reveal-related messages (count these):**
- ✅ Reactions to reveal message ("Loved", "Laughed at" the reveal)
- ✅ Comments on partner's answer ("That's so funny", "lol that was tonkatsu")
- ✅ Discussion sparked by question topic (if question was about "favorite dinner", discussing dinner plans)
- ✅ Feedback about the reveal ("Wrong response", "Codel, this is an old answer")
- ✅ Meta-discussion ("I think I might have won for quickest answer")

**NOT reveal-related (do NOT count):**
- ❌ Regular logistics ("I'm leaving work now", "Do we have any meat?")
- ❌ Child-related ("Why is Kai not in bed?")
- ❌ Unrelated life events ("Board presentation went well")
- ❌ Location updates ("About 7 mins away")
- ❌ General conversation that happened to occur after reveal

### 6c: Report Verified Engagement

After inspecting content, report BOTH the raw count and verified count:

```markdown
### Post-Reveal Engagement (Verified)

| Metric | Value |
|--------|-------|
| Total reveals sent | 34 |
| Reveals with activity (raw, within 15 min) | 10 |
| **Reveals with verified reveal-related activity** | **7** |

**Verified engagement examples:**
- Conversation 184: Kristi reflected on their partnership
- Conversation 1060: Esty commented "That's so funny almog"

**False positives excluded:**
- Conversation 43: "Board presentation went well" (unrelated)
- Conversation 536: "About 7 mins away" (logistics)
```

**⚠️ CRITICAL:** Never report "X% post-reveal engagement" based solely on message counts. Always verify content.

---

## Report Format

When presenting results, use this structure:

```markdown
## Daily Question Analysis ({duration})

### Response Statistics

| Metric | Value |
|--------|-------|
| Total created | X |
| Responded | X (Y%) |
| Pending | X |
| Expired | X |
| Total pairs | X |
| Pairs both responded | X (Y%) |

### Response Breakdown

| Status | Count | Users |
|--------|-------|-------|
| Responded | X | id1, id2, ... |
| Pending | X | id1, id2, ... |
| Expired | X | id1, id2, ... |

### Completed Pairs (Both Responded)

| Conversation | Partners | Question Day | Last Response |
|--------------|----------|--------------|---------------|
| [123](link) | ID1 & ID2 | Day X | timestamp |

### Post-Reveal Engagement

| Metric | Value |
|--------|-------|
| Pairs with post-reveal activity | X of Y |
| Total messages after reveal | X |
| Total reactions after reveal | X |
| Avg messages per active pair | X |

**Summary:** [1-2 sentence interpretation]
```

---

## Citations

**MANDATORY:** Include clickable links for all entity IDs.

| Entity | URL Pattern |
|--------|-------------|
| Person | `https://admin.prod.cncorp.io/persons/{id}` |
| Conversation | `https://admin.prod.cncorp.io/conversations/{id}` |
| Messages (time range) | `https://admin.prod.cncorp.io/conversations/{id}/messages?start={iso}&end={iso}` |

**Example:**
```markdown
Conversation [184](https://admin.prod.cncorp.io/conversations/184): Kristi ([view](https://admin.prod.cncorp.io/persons/146)) & Tobin ([view](https://admin.prod.cncorp.io/persons/147))
```

---

## Privacy Escalation

If user asks to see actual content:

```sql
-- ONLY USE WHEN USER EXPLICITLY ASKS FOR CONTENT
-- Shows response text for completed pairs (replace {{INTERVAL}})
SELECT
  dqr.group_conversation_id,
  dqr.user_id,
  dqr.question_text,
  dqr.response_text,
  dqr.responded_at
FROM daily_question_response dqr
WHERE dqr.responded_at IS NOT NULL
  AND dqr.created_at >= NOW() - {{INTERVAL}}
ORDER BY dqr.group_conversation_id, dqr.responded_at;
```

**Announce:** "Showing response content as requested (contains personal data)."

---

## Common Violations

- ❌ **BANNED:** Using `responded_at` as reveal time (reveal happens ~30 min AFTER second response)
- ❌ **BANNED:** Using 24-hour window for "post-reveal engagement" (captures unrelated conversation)
- ❌ **BANNED:** Counting messages as "engagement" without verifying content is reveal-related
- ❌ **BANNED:** Reporting "X% engagement" based on raw counts without content inspection
- ❌ **BANNED:** Showing `response_text` or message `content` without explicit user request
- ❌ **BANNED:** Forgetting to include citations for conversation/person IDs
- ❌ **BANNED:** Using hardcoded 24h interval when user specified different duration
- ❌ **BANNED:** Grouping only by `group_conversation_id` (must also group by `question_day`)
- ✅ **CORRECT:** Find actual "Daily Question Reveal" message and use that timestamp
- ✅ **CORRECT:** Use 10-15 min window for reveal-related engagement
- ✅ **CORRECT:** Inspect message content to verify it's reveal-related before reporting
- ✅ **CORRECT:** Report both raw counts AND verified counts
- ✅ **CORRECT:** Default to aggregates and metadata, escalate to content only when asked

---

## Success Criteria

Analysis is complete when:
- [ ] Response rate overview provided
- [ ] Status breakdown with user IDs shown
- [ ] Completed pairs identified (if any)
- [ ] Post-reveal engagement analyzed using actual reveal message timestamp
- [ ] Message content inspected to verify engagement is reveal-related
- [ ] Verified engagement count reported (not just raw counts)
- [ ] All entity IDs have clickable citations
- [ ] No raw content shown unless explicitly requested
- [ ] Correct time interval used per user request
