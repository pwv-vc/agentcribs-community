---
name: onboarding-funnel-analyzer
description: Deep analysis of new user onboarding funnel - from form submission through partner invitation, including message content analysis, nudge effectiveness, and user segmentation
---

# onboarding-funnel-analyzer Skill

## 🎯 Purpose

Provides a comprehensive analysis framework for understanding the new user onboarding funnel, with special focus on:
- **Why users stall** at partner invitation
- **Semantic analysis** of actual message content (not just metrics)
- **Nudge effectiveness** by content type
- **Geographic distribution** of users
- **Engagement depth** beyond surface-level metrics
- **User segmentation** into actionable categories (likely to invite, engaging solo, unlikely to convert)

**Use this skill when:**
- User asks about "new user funnel" or "onboarding analysis"
- User wants to understand why users aren't completing onboarding
- User asks about "stalled users" or "incomplete onboardings"
- User wants to analyze nudge effectiveness
- Combining insights from `incomplete-onboarding-assessor` and `nux-first-week-analyzer`

---

## 🚀 Quick Start: Automation Scripts

**For quick analysis, use the automation scripts instead of running queries manually:**

```bash
# Full analysis (default: 7 days)
.claude/skills/onboarding-funnel-analyzer/scripts/run_funnel_analysis.sh

# Full analysis with custom time window
.claude/skills/onboarding-funnel-analyzer/scripts/run_funnel_analysis.sh 5    # Last 5 days
.claude/skills/onboarding-funnel-analyzer/scripts/run_funnel_analysis.sh 14   # Last 14 days

# Quick quantitative funnel only
.claude/skills/onboarding-funnel-analyzer/scripts/run_quantitative_only.sh
.claude/skills/onboarding-funnel-analyzer/scripts/run_quantitative_only.sh 5  # Last 5 days
```

**Scripts output to:** `.claude/skills/onboarding-funnel-analyzer/output/`

**To finalize report:**
```bash
cp .claude/skills/onboarding-funnel-analyzer/output/funnel_analysis_*.md docs/onboarding_funnel_analysis_$(date +%Y-%m-%d).md
```

---

## ⚙️ Time Window Configuration

**All queries in this skill use a configurable time window.**

When running queries manually, replace `'7 days'` with your desired window:

| User Request | Interval |
|--------------|----------|
| "Last 5 days" / "since Friday" | `'5 days'` |
| "Last week" | `'7 days'` |
| "Last 2 weeks" | `'14 days'` |
| "Last month" | `'30 days'` |

**Example adjustment:**
```sql
-- Original (7 days)
WHERE created_at >= NOW() - INTERVAL '7 days'

-- Adjusted for 5 days
WHERE created_at >= NOW() - INTERVAL '5 days'
```

---

## 🚨 CRITICAL: Always Exclude TEST Accounts

**TEST accounts WILL corrupt your funnel metrics if not filtered.**

```sql
-- ALWAYS join to persons and filter by type for any user-level analysis
JOIN persons p ON pc.person_id = p.id
WHERE p.type != 'TEST'
```

**Why this matters:** TEST accounts (e.g., "Buzz + Woody") complete onboarding during automated testing. If you count them as COMPLETED, your conversion rates will be wrong.

---

## Prerequisites

- **sql-reader skill** - You MUST read `docs/sql/DATA_QUIRKS.md` first
- **Admin links** - All person IDs must include clickable links to `https://admin.prod.cncorp.io/persons/{id}`
- **Person Type awareness** - Always include `persons.type` to distinguish USER vs USER_RESEARCH vs EMPLOYEE

### Person Types

| Type | Description | Include in Analysis? |
|------|-------------|---------------------|
| `USER` | Real paying/trial users | ✅ Yes - primary focus |
| `USER_RESEARCH` | Research participants | ✅ Yes - but flag separately |
| `EMPLOYEE` | Internal team members | ⚠️ Maybe - often testing |
| `TEST` | Automated test accounts | ❌ **NEVER** - always exclude |

**Always filter:** `WHERE p.type != 'TEST'`

**Always display:** Person type in output tables so USER_RESEARCH can be identified

---

## Step 1: Quantitative Funnel Summary

**Start with the numbers.** This gives you conversion rates and drop-off percentages at each step.

**🚨 CRITICAL:** TEST accounts are filtered out. Always use this query, not raw counts.

```sql
-- Quantitative funnel with conversion rates and drop-off (TEST accounts excluded)
WITH funnel_data AS (
  -- Step 1: Form submissions
  SELECT 1 as step_num, 'Form Submitted' as funnel_step,
    COUNT(DISTINCT id) as users
  FROM conversation_onboarding
  WHERE created_at >= NOW() - INTERVAL '7 days'
    AND form_data->>'name' IS NOT NULL
    AND LENGTH(form_data->>'name') > 1

  UNION ALL

  -- Step 2: Messaged Wren (INITIATOR_JOINED or COMPLETED, excluding TEST)
  SELECT 2, 'Messaged Wren',
    COUNT(DISTINCT co.id)
  FROM conversation_onboarding co
  JOIN conversation_participant_onboarding cpo
    ON cpo.conversation_onboarding_id = co.id AND cpo.is_initiator = true
  JOIN person_contacts pc ON cpo.person_contact_id = pc.id
  JOIN persons p ON pc.person_id = p.id
  WHERE co.created_at >= NOW() - INTERVAL '7 days'
    AND co.state IN ('INITIATOR_JOINED', 'COMPLETED')
    AND p.type != 'TEST'

  UNION ALL

  -- Step 3: Had real exchange (sent messages beyond access code)
  SELECT 3, 'Real Exchange',
    COUNT(DISTINCT uc.person_id)
  FROM (
    SELECT DISTINCT co.id as onboarding_id, pc.person_id, c.id as conv_id
    FROM conversation_onboarding co
    JOIN conversation_participant_onboarding cpo
      ON cpo.conversation_onboarding_id = co.id AND cpo.is_initiator = true
    JOIN person_contacts pc ON cpo.person_contact_id = pc.id
    JOIN persons p ON pc.person_id = p.id
    JOIN conversation_participant cp ON cp.person_id = pc.person_id
    JOIN conversation c ON c.id = cp.conversation_id AND c.type = 'ONE_ON_ONE'
    WHERE co.created_at >= NOW() - INTERVAL '7 days'
      AND co.state IN ('INITIATOR_JOINED', 'COMPLETED')
      AND p.type != 'TEST'
  ) uc
  JOIN message m ON m.conversation_id = uc.conv_id
  JOIN person_contacts mpc ON m.sender_person_contact_id = mpc.id AND mpc.person_id = uc.person_id
  WHERE m.provider_data->>'source' IS DISTINCT FROM 'onboarding_form'
    AND m.content NOT LIKE '%WREN-%'
    AND m.content NOT LIKE 'My birthday%'
    AND m.content NOT LIKE 'Our relationship%'
    AND m.content NOT LIKE 'We''re in a%'

  UNION ALL

  -- Step 4: Partner joined (COMPLETED, excluding TEST)
  SELECT 4, 'Partner Joined',
    COUNT(DISTINCT co.id)
  FROM conversation_onboarding co
  JOIN conversation_participant_onboarding cpo
    ON cpo.conversation_onboarding_id = co.id AND cpo.is_initiator = true
  JOIN person_contacts pc ON cpo.person_contact_id = pc.id
  JOIN persons p ON pc.person_id = p.id
  WHERE co.created_at >= NOW() - INTERVAL '7 days'
    AND co.state = 'COMPLETED'
    AND p.type != 'TEST'
)
SELECT
  funnel_step,
  users,
  ROUND(100.0 * users / FIRST_VALUE(users) OVER (ORDER BY step_num), 1) as pct_of_start,
  ROUND(100.0 * users / NULLIF(LAG(users) OVER (ORDER BY step_num), 0), 1) as conversion,
  ROUND(100.0 * (LAG(users) OVER (ORDER BY step_num) - users) /
        NULLIF(LAG(users) OVER (ORDER BY step_num), 0), 1) as drop_off
FROM funnel_data
ORDER BY step_num;
```

**Expected output format:**

| Step | Users | % of Start | Conversion | Drop-off |
|------|-------|------------|------------|----------|
| Form Submitted | 28 | 100% | - | - |
| Messaged Wren | 7 | 25% | 25% | 75% |
| Real Exchange | 5 | 18% | 71% | 29% |
| Partner Joined | 0 | 0% | 0% | 100% |

**Key metrics to highlight:**
- **Form → Messaged Wren:** Primary drop-off point (typically 70-80% drop)
- **Messaged → Real Exchange:** Engagement quality
- **Real Exchange → Partner Joined:** The partner invite barrier

---

## Step 2: State Distribution Breakdown

Get the detailed state distribution for context:

```sql
-- State distribution (for context)
SELECT
  state,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM conversation_onboarding
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY state
ORDER BY count DESC;
```

| State | Count | % |
|-------|-------|---|
| AWAITING_PARTICIPANTS | X | X% |
| INITIATOR_JOINED | X | X% |
| COMPLETED | X | X% |

**Why the join is needed for user-level queries:** `conversation_onboarding` doesn't have person type. You must join through `conversation_participant_onboarding` → `person_contacts` → `persons` to check `p.type != 'TEST'`.

---

## Step 3: Segment by Form Data

**Break down funnel metrics by form submission values** to identify which user types convert better.

### Step 3.1: Conversion by Relationship Type

```sql
-- Funnel by relationship_type
SELECT
  co.form_data->>'relationship_type' as relationship_type,
  COUNT(*) as form_submissions,
  COUNT(*) FILTER (WHERE co.state IN ('INITIATOR_JOINED', 'COMPLETED')) as messaged_wren,
  COUNT(*) FILTER (WHERE co.state = 'COMPLETED') as completed,
  ROUND(100.0 * COUNT(*) FILTER (WHERE co.state IN ('INITIATOR_JOINED', 'COMPLETED')) / NULLIF(COUNT(*), 0), 1) as msg_rate,
  ROUND(100.0 * COUNT(*) FILTER (WHERE co.state = 'COMPLETED') / NULLIF(COUNT(*), 0), 1) as complete_rate
FROM conversation_onboarding co
WHERE co.created_at >= NOW() - INTERVAL '7 days'
  AND co.form_data->>'name' IS NOT NULL
GROUP BY co.form_data->>'relationship_type'
ORDER BY form_submissions DESC;
```

**Expected output:**

| relationship_type | Forms | Messaged | Completed | Msg Rate | Complete Rate |
|-------------------|-------|----------|-----------|----------|---------------|
| romantic | 20 | 5 | 1 | 25% | 5% |
| family | 5 | 2 | 0 | 40% | 0% |
| friends | 3 | 0 | 0 | 0% | 0% |
| separated | 2 | 1 | 0 | 50% | 0% |

**Key questions to answer:**
- Do `separated` users convert at different rates? (Often seeking solo support)
- Are `family` users more likely to complete? (Different dynamic than romantic)
- Do `friends` users engage at all? (May not understand the product)

### Step 3.2: Conversion by Relationship Dynamic

```sql
-- Funnel by relationship_dynamic (can have multiple values)
SELECT
  jsonb_array_elements_text(co.form_data->'relationship_dynamic') as dynamic,
  COUNT(*) as form_submissions,
  COUNT(*) FILTER (WHERE co.state IN ('INITIATOR_JOINED', 'COMPLETED')) as messaged_wren,
  ROUND(100.0 * COUNT(*) FILTER (WHERE co.state IN ('INITIATOR_JOINED', 'COMPLETED')) / NULLIF(COUNT(*), 0), 1) as msg_rate
FROM conversation_onboarding co
WHERE co.created_at >= NOW() - INTERVAL '7 days'
  AND co.form_data->>'name' IS NOT NULL
  AND co.form_data->'relationship_dynamic' IS NOT NULL
GROUP BY jsonb_array_elements_text(co.form_data->'relationship_dynamic')
ORDER BY form_submissions DESC;
```

**Expected output:**

| dynamic | Forms | Messaged | Msg Rate |
|---------|-------|----------|----------|
| distant_or_disconnected | 12 | 4 | 33% |
| conflicts_or_tension | 8 | 2 | 25% |
| stable_and_connected | 6 | 3 | 50% |
| parenting_conflict | 3 | 1 | 33% |
| rupture_of_trust | 2 | 1 | 50% |

**Key insight:** Users with `rupture_of_trust` or `stable_and_connected` may convert better - they have clear motivation.

### Step 3.3: Conversion by Communication Goals

```sql
-- Funnel by communication_goals (can have multiple values)
SELECT
  jsonb_array_elements_text(co.form_data->'communication_goals') as goal,
  COUNT(*) as form_submissions,
  COUNT(*) FILTER (WHERE co.state IN ('INITIATOR_JOINED', 'COMPLETED')) as messaged_wren,
  ROUND(100.0 * COUNT(*) FILTER (WHERE co.state IN ('INITIATOR_JOINED', 'COMPLETED')) / NULLIF(COUNT(*), 0), 1) as msg_rate
FROM conversation_onboarding co
WHERE co.created_at >= NOW() - INTERVAL '7 days'
  AND co.form_data->>'name' IS NOT NULL
  AND co.form_data->'communication_goals' IS NOT NULL
GROUP BY jsonb_array_elements_text(co.form_data->'communication_goals')
ORDER BY form_submissions DESC;
```

### Step 3.4: Conversion by Platform (Provider)

```sql
-- Funnel by messaging platform
SELECT
  co.form_data->>'provider' as platform,
  COUNT(*) as form_submissions,
  COUNT(*) FILTER (WHERE co.state IN ('INITIATOR_JOINED', 'COMPLETED')) as messaged_wren,
  COUNT(*) FILTER (WHERE co.state = 'COMPLETED') as completed,
  ROUND(100.0 * COUNT(*) FILTER (WHERE co.state IN ('INITIATOR_JOINED', 'COMPLETED')) / NULLIF(COUNT(*), 0), 1) as msg_rate
FROM conversation_onboarding co
WHERE co.created_at >= NOW() - INTERVAL '7 days'
  AND co.form_data->>'name' IS NOT NULL
GROUP BY co.form_data->>'provider'
ORDER BY form_submissions DESC;
```

**Expected output:**

| platform | Forms | Messaged | Completed | Msg Rate |
|----------|-------|----------|-----------|----------|
| iMessage | 15 | 4 | 1 | 27% |
| WhatsApp | 13 | 3 | 0 | 23% |

**Key questions:**
- Does iMessage vs WhatsApp affect conversion?
- Are there regional patterns? (WhatsApp dominant outside US)

### Step 3.5: Form Data Summary Table

For the output report, include a summary of form data patterns:

```sql
-- Comprehensive form data summary for all users in period
SELECT
  co.id,
  co.form_data->>'name' as name,
  co.form_data->>'relationship_type' as rel_type,
  co.form_data->'relationship_dynamic' as dynamics,
  co.form_data->'communication_goals' as goals,
  co.form_data->>'provider' as platform,
  co.state
FROM conversation_onboarding co
WHERE co.created_at >= NOW() - INTERVAL '7 days'
  AND co.form_data->>'name' IS NOT NULL
ORDER BY co.created_at DESC;
```

---

## Step 4: Analyze Engagement Depth (Beyond Access Code)

**CRITICAL:** Don't just count messages. Categorize them semantically.

### Step 4.1: Exclude System Messages

**Use `provider_data->>'source'` to reliably identify auto-generated messages:**

```sql
-- Exclude auto-generated onboarding form messages
WHERE (m.provider_data->>'source' != 'onboarding_form'
       OR m.provider_data->>'source' IS NULL)
```

Auto-generated messages include:
- `My birthday is%` - Auto-submitted birthday
- `Our relationship dynamic:%` - Auto-submitted form data
- `We're in a romantic%` - Auto-submitted relationship type
- `Things that apply to us:%` - Auto-submitted situation
- `What we want to tackle:%` - Auto-submitted goals

**Also exclude:**
- `[Contact]%` - Contact card messages
- `%WREN-%` - Access code messages (sent by user, but not real engagement)

See `docs/sql/DATA_QUIRKS.md` for full details on this pattern.

### Step 4.2: Categorize User Messages

```sql
-- Categorize user messages semantically
WITH user_messages AS (
  SELECT
    p.id as person_id,
    m.content,
    CASE
      -- System/onboarding auto-messages (exclude these)
      WHEN m.content LIKE 'My birthday is%' THEN 'system_birthday'
      WHEN m.content LIKE 'Our relationship dynamic:%' THEN 'system_dynamic'
      WHEN m.content LIKE 'We''re in a romantic%' THEN 'system_relationship'
      WHEN m.content LIKE '[Contact]%' THEN 'system_contact'
      WHEN m.content LIKE '%WREN-%' THEN 'access_code'
      -- Engagement categories
      WHEN LOWER(m.content) LIKE '%how do%' OR LOWER(m.content) LIKE '%how does%' THEN 'question_how'
      WHEN LOWER(m.content) LIKE '%what%' THEN 'question_what'
      WHEN LOWER(m.content) = 'yes' OR LOWER(m.content) LIKE 'yeah%' THEN 'affirmative'
      WHEN LOWER(m.content) = 'no' OR LOWER(m.content) LIKE '%not interested%' THEN 'negative'
      WHEN LENGTH(m.content) > 100 THEN 'substantive_response'
      WHEN LENGTH(m.content) > 30 THEN 'brief_response'
      ELSE 'minimal_response'
    END as msg_category
  FROM persons p
  JOIN person_contacts pc ON pc.person_id = p.id
  JOIN message m ON m.sender_person_contact_id = pc.id
  -- ... join to incomplete onboardings
)
SELECT msg_category, COUNT(*), COUNT(DISTINCT person_id)
FROM user_messages
GROUP BY msg_category;
```

### Step 4.3: Assign Engagement Levels

| Level | Criteria |
|-------|----------|
| **DEEP** | 1+ substantive messages (>100 chars), asked questions |
| **CURIOUS** | Asked "how" or "what" questions |
| **SURFACE** | Short responses, no questions |
| **MINIMAL** | ≤2 messages, very brief |

---

## Step 5: Analyze Response to Partner Invitation

The key conversion point is when Wren sends: "Next step is to get [Partner] in..."

### Step 5.1: Identify Coach Messages

Coach messages come from conversation participants with `role = 'THERAPIST'`:

```sql
-- Get coach person_contact_ids
SELECT DISTINCT cp.person_contact_id
FROM conversation_participant cp
WHERE cp.role = 'THERAPIST';
```

### Step 5.2: Find Initial Partner Invite and User Response

```sql
-- Find initial invite message and user's next response
WITH initial_invite AS (
  SELECT DISTINCT ON (person_id)
    person_id, provider_timestamp, conv_id
  FROM ... -- join to get Wren messages
  WHERE LOWER(content) LIKE '%next step is to get%'
  ORDER BY person_id, provider_timestamp
)
SELECT
  person_id,
  (SELECT content FROM message WHERE ... > initial_invite.provider_timestamp LIMIT 1) as response
FROM initial_invite;
```

### Step 5.3: Categorize Responses

| Category | Pattern | Example |
|----------|---------|---------|
| **NO_RESPONSE** | NULL response | User went silent |
| **RESENT_ACCESS_CODE** | `%WREN-%` | "Hey Wren. Here's my access code: WREN-XXXXX" |
| **ASKED_HOW_IT_WORKS** | `%how do%`, `%curious%` | "Curious how you work" |
| **SAID_YES_DIDNT_ACT** | `yes`, `ok`, `sure` | "OK" (then silence) |
| **REQUESTED_SOLO** | `%without%`, `%just me%`, `%on my own%` | "Can we exclude her for now?" |
| **TOPIC_CHANGE** | Other content | Changed subject to avoid invitation |
| **CLAIMED_SENT** | `%sent%`, `%link shared%` | "Link shared" |

---

## Step 6: Analyze Onboarding Nudges

### Step 6.1: Identify Nudge Messages

Nudges are identified by `sender_context`:

```sql
WHERE m.data->'sender_context'->>'sender_type' = 'onboarding_nudge'
```

### Step 6.2: Categorize Nudge Content

| Type | Pattern | Description |
|------|---------|-------------|
| **OFFER_SOLO_EXERCISE** | `%1:1%`, `%exercise%` | "Want to try a quick 1:1 exercise?" |
| **MENTION_INVITE** | `%invite%`, `%bring%` | Soft mention of partner invite |
| **ASK_IF_INVITED** | `%invite%yet%` | "Have you had a chance to invite...?" |
| **OTHER** | Default | General check-ins |

### Step 6.3: Calculate Response Rates by Type

```sql
SELECT
  nudge_type,
  COUNT(*) as total,
  SUM(CASE WHEN response IS NOT NULL THEN 1 ELSE 0 END) as got_response,
  ROUND(100.0 * SUM(...) / COUNT(*), 1) as response_rate
FROM nudges_with_responses
GROUP BY nudge_type;
```

**Expected finding:** `OFFER_SOLO_EXERCISE` nudges get ~33% response vs ~12% for generic nudges.

---

## Step 7: Get Timing and Location Data

### Step 7.1: Calculate Time Since Key Events

```sql
SELECT
  person_id,
  ROUND(EXTRACT(EPOCH FROM (NOW() - access_code_time)) / 3600, 1) as hours_since_access_code,
  ROUND(EXTRACT(EPOCH FROM (NOW() - last_wren_time)) / 3600, 1) as hours_since_last_wren
FROM ...
```

### Step 7.2: Extract Location from Form Data

Timezone is stored in `conversation_onboarding.form_data->>'timezone'`

```sql
SELECT
  form_data->>'timezone' as timezone,
  CASE
    WHEN handle LIKE '+1%' THEN 'US/Canada'
    WHEN handle LIKE '+27%' THEN 'South Africa'
    WHEN handle LIKE '+44%' THEN 'UK'
    WHEN handle LIKE '+91%' THEN 'India'
    WHEN handle LIKE '+61%' THEN 'Australia'
    WHEN handle LIKE '%@s.whatsapp.net' THEN 'WhatsApp'
    WHEN handle LIKE '%@lid' THEN 'WhatsApp (LID)'
    ELSE 'Unknown'
  END as country_from_phone
FROM ...
```

---

## Step 8: Identify Key Patterns

### Pattern 1: Access Code Confusion

Users who resend their access code after the partner invite message:
- They think they need to do something else
- They didn't understand the transition from "save contact" to "share link"
- **UX problem, not disinterest**

### Pattern 2: Intention-Action Gap

Users who say "Yes" or "OK" but never send the invite:
- Wren moves on to offer exercises
- Partner invitation never revisited
- Need immediate, frictionless action after "Yes"

### Pattern 3: Topic Deflection

Users who change subject to avoid partner invitation:
- Ask unrelated questions
- Share personal content
- Ask "how does it work" instead of inviting

### Pattern 4: Explicit Solo Requests

Users who explicitly say partner won't join:
- "She won't be onboard with this"
- "Thought I could use it on my own"
- **These users want solo mode but it's not offered**

---

## Step 9: Segment Users by Conversion Likelihood

After analyzing behavior patterns, segment users into three categories:

### Segment 1: LIKELY TO INVITE PARTNER

**Criteria:**
- Claimed they sent the invite (`%link shared%`, `%sent%`)
- Said "Yes" to invite AND still recently active (<48h)
- High engagement + responded to nudges

**Signals to look for:**
```sql
-- Users who claimed to send invite or said yes and are still active
CASE
  WHEN claimed_sent_invite THEN 'LIKELY_PARTNER'
  WHEN invite_response = 'SAID_YES' AND hours_silent < 48 AND nudge_responses > 0 THEN 'LIKELY_PARTNER'
  ...
END
```

**Action:** Follow up to verify partner received link. Offer troubleshooting.

### Segment 2: ENGAGING SOLO

**Criteria (Explicit):**
- Said `%without%`, `%just me%`, `%on my own%`, `%exclude%`
- Said `%won't be onboard%`, `%she won't%`, `%he won't%`

**Criteria (Implicit):**
- High engagement (DEEP) but systematically avoiding partner topic
- Topic changes every time partner is mentioned
- Using Wren to process relationship issues (e.g., considering divorce)

**Signals to look for:**
```sql
-- Explicit solo requests
bool_or(LOWER(content) LIKE '%without%' OR LOWER(content) LIKE '%just me%'
  OR LOWER(content) LIKE '%on my own%' OR LOWER(content) LIKE '%exclude%'
  OR LOWER(content) LIKE '%won''t%onboard%') as requested_solo

-- Implicit: high engagement + topic deflection on invite
WHEN real_msgs > 5 AND substantive_msgs > 2 AND invite_response = 'TOPIC_CHANGE' THEN 'ENGAGING_SOLO'
```

**Action:** Formalize solo mode offering. These users want help - just not couples coaching right now.

### Segment 3: UNLIKELY TO CONVERT

**Tier 3A: Confused and Lost**
- Resent access code after partner invite
- Didn't understand the flow
- May recover with clearer UX

**Tier 3B: Asked How But Went Silent**
- Initial curiosity ("how does it work?")
- No follow-through after explanation
- 3+ days silent

**Tier 3C: Said Yes But Ghosted**
- Agreed to invite but never did
- Wren moved on to exercises
- Partner invitation never revisited

**Tier 3D: Never Responded**
- No response to initial partner invite
- Minimal or no engagement
- Not responding to nudges

**Action:** Low priority. Final "We noticed you didn't finish..." email might recover <5%.

### Segmentation Query

```sql
-- Comprehensive user segmentation with person type
SELECT
  person_id,
  person_type,  -- USER, USER_RESEARCH, or EMPLOYEE
  real_msgs,
  substantive_msgs,
  hours_silent,
  requested_solo,
  claimed_sent_invite,
  invite_response,
  nudges_received,
  nudges_responded,
  CASE
    -- Segment 1: Likely to invite partner
    WHEN claimed_sent_invite THEN 'LIKELY_PARTNER'
    WHEN invite_response = 'SAID_YES' AND hours_silent < 48 AND nudges_responded > 0 THEN 'LIKELY_PARTNER'

    -- Segment 2: Engaging solo
    WHEN requested_solo THEN 'ENGAGING_SOLO'
    WHEN real_msgs > 5 AND substantive_msgs > 2 AND invite_response IN ('TOPIC_CHANGE', 'ASKED_HOW') THEN 'ENGAGING_SOLO'

    -- Segment 3: Unlikely to convert
    WHEN invite_response = 'CONFUSED' THEN 'UNLIKELY_CONFUSED'
    WHEN invite_response = 'ASKED_HOW' AND hours_silent > 72 THEN 'UNLIKELY_CURIOUS_GHOSTED'
    WHEN invite_response = 'SAID_YES' AND hours_silent > 72 THEN 'UNLIKELY_YES_GHOSTED'
    WHEN invite_response = 'NO_RESPONSE' THEN 'UNLIKELY_NEVER_RESPONDED'

    ELSE 'UNCLEAR'
  END as segment
FROM user_behavior_summary
WHERE person_type != 'TEST';  -- Always exclude TEST accounts
```

### Person Type Distribution

Always include a summary of person types in your analysis:

```sql
SELECT
  p.type as person_type,
  COUNT(*) as count,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as pct
FROM persons p
JOIN conversation_onboarding co ON ...
WHERE co.state = 'INITIATOR_JOINED'
  AND p.type IN ('USER', 'USER_RESEARCH', 'EMPLOYEE')
GROUP BY p.type
ORDER BY count DESC;
```

**Why this matters:**
- USER_RESEARCH participants may behave differently (recruited, incentivized)
- EMPLOYEE accounts are often testing
- Conversion rates should be calculated for USER only, with USER_RESEARCH noted separately

---

## Step 10: Generate Recommendations

Based on analysis, typical recommendations include:

### 1. Fix Access Code Confusion
- Explicitly say "You're all done on your side! ✅"
- Make clear the next step is THEM sending a link

### 2. Make Solo Mode Explicit
- Offer proactively: "Not ready to invite [Partner]? We can start with just you."
- Solo exercise nudges get higher response rates

### 3. Address Intention-Action Gap
- Don't move on after "Yes" - provide immediate one-tap action
- "Great! Tap here to send the link: [BUTTON]"

### 4. Prioritize Solo Exercise Nudges
- All nudges should offer concrete solo value
- Frame as "While we wait for [Partner]..."

### 5. Don't Ask "Have you invited yet?"
- Guilt-trip nudges get 0% response
- Instead offer value: "Want to try something helpful?"

---

## Output Format

**🚨 MANDATORY: Write analysis to a markdown file**

After completing the analysis, you MUST write the full report to:
```
docs/onboarding_funnel_analysis_YYYY-MM-DD.md
```

**File naming convention:**
- Use current date in ISO format: `2026-01-20`
- Example: `docs/onboarding_funnel_analysis_2026-01-20.md`

**Why:** This creates a permanent record for tracking trends over time and sharing with stakeholders.

---

Generate a markdown report with:

1. **Executive Summary** - Key metrics and insights
2. **Funnel Overview** - State distribution table
3. **All Stalled Users Table** - With admin links, timing, location
4. **Engagement Depth Analysis** - DEEP/CURIOUS/SURFACE/MINIMAL breakdown
5. **Partner Invite Response Analysis** - Categorized responses
6. **Nudge Effectiveness** - Response rates by nudge type
7. **Key Patterns** - Named patterns with user lists
8. **User Segmentation** - Three segments with user lists:
   - LIKELY TO INVITE PARTNER (with next actions)
   - ENGAGING SOLO (explicit + implicit)
   - UNLIKELY TO CONVERT (by tier: confused, ghosted, never responded)
9. **Priority Actions** - Immediate, this week, product changes
10. **Recommendations** - Actionable next steps
11. **Methodology** - Data sources and filters applied

### Required Elements

- ✅ All person IDs as clickable admin links: `[{id}](https://admin.prod.cncorp.io/persons/{id})`
- ✅ **Person type** (USER, USER_RESEARCH, EMPLOYEE) in all user tables
- ✅ Hours since access code and last Wren message
- ✅ Timezone and country from phone number
- ✅ Last Wren message content (truncated)
- ✅ Geographic distribution summary
- ✅ **Person type distribution** (how many USER vs USER_RESEARCH)
- ✅ **Analysis date and period** in header

---

## Common Violations

- ❌ **CRITICAL:** Including TEST accounts in funnel counts (join to persons, filter `p.type != 'TEST'`)
- ❌ **CRITICAL:** Counting COMPLETED without checking person type (TEST accounts complete onboarding in automated tests)
- ❌ **BANNED:** Not writing analysis to `docs/onboarding_funnel_analysis_YYYY-MM-DD.md`
- ❌ **BANNED:** Analyzing message count without semantic categorization
- ❌ **BANNED:** Treating all "engaged" users the same (must distinguish DEEP vs MINIMAL)
- ❌ **BANNED:** Missing admin links for person IDs
- ❌ **BANNED:** Not filtering out system-generated onboarding messages
- ❌ **BANNED:** Assuming all nudges are equal (must categorize by content type)
- ❌ **BANNED:** Treating all stalled users the same (must segment into 3 categories)
- ❌ **BANNED:** Missing "ENGAGING SOLO" segment (these users want help, just not couples)
- ❌ **BANNED:** Not distinguishing explicit vs implicit solo requests
- ❌ **BANNED:** Not including person type (USER/USER_RESEARCH/EMPLOYEE) in output
- ❌ **BANNED:** Mixing USER and USER_RESEARCH in conversion rate calculations without noting

---

## Success Criteria

You've completed this analysis when:

- [ ] **Report written to `docs/onboarding_funnel_analysis_YYYY-MM-DD.md`**
- [ ] Funnel overview shows all states (AWAITING, INITIATOR_JOINED, COMPLETED)
- [ ] **Person type distribution** shown (USER vs USER_RESEARCH vs EMPLOYEE)
- [ ] Engagement depth categorized (DEEP/CURIOUS/SURFACE/MINIMAL)
- [ ] Partner invite responses categorized with user lists
- [ ] Nudge response rates calculated by content type
- [ ] All person IDs have admin links
- [ ] **Person type column** included in all user tables
- [ ] Timing data (hours since access code, last Wren)
- [ ] Location data (timezone + country from phone)
- [ ] Key patterns identified with affected user counts
- [ ] **Users segmented into 3 categories:**
  - LIKELY TO INVITE PARTNER (count + user list)
  - ENGAGING SOLO (explicit + implicit, with user list)
  - UNLIKELY TO CONVERT (by tier, with user list)
- [ ] **Priority actions identified** (immediate, this week, product)
- [ ] Actionable recommendations provided
- [ ] **Methodology section** documenting data sources and filters

---

## Related Skills

- **incomplete-onboarding-assessor** - Temperature model (COLD/WARM/HOT) with time decay
- **nux-first-week-analyzer** - First week analysis for completed onboardings
- **sql-reader** - Database query patterns and DATA_QUIRKS.md
