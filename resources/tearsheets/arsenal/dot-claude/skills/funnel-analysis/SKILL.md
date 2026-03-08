---
name: funnel-analysis
description: Analyze user conversion funnels and identify drop-off points. Use when investigating where users get stuck or churn in multi-step flows.
allowed-tools:
  - Bash
  - Read
  - Write
  - Grep
  - Glob
---

# Funnel Analysis Skill

Two funnels available:
- **"the funnel"** → Standard funnel (all users 28+ days old)
- **"the onboarding funnel"** → Onboarding funnel (onboarding users 7+ days old)

---

## Standard Funnel (28+ days old)

```sql
WITH user_first_messages AS (
  SELECT p.id as person_id, MIN(m.provider_timestamp) as first_message_date
  FROM persons p
  JOIN person_contacts pc ON pc.person_id = p.id
  JOIN message m ON m.sender_person_contact_id = pc.id
  GROUP BY p.id
  HAVING MIN(m.provider_timestamp) <= NOW() - INTERVAL '28 days'
),
user_complete_behavior AS (
  SELECT
    ufm.person_id,
    COUNT(DISTINCT CASE WHEN m.provider_timestamp >= ufm.first_message_date AND m.provider_timestamp < ufm.first_message_date + INTERVAL '7 days' THEN m.id END) as week1_messages,
    COUNT(DISTINCT CASE WHEN m.provider_timestamp >= ufm.first_message_date AND m.provider_timestamp < ufm.first_message_date + INTERVAL '7 days' THEN DATE(m.provider_timestamp) END) as days_active_week1,
    COUNT(DISTINCT CASE WHEN m.provider_timestamp >= NOW() - INTERVAL '28 days' THEN m.id END) as messages_last_28d,
    COUNT(DISTINCT CASE WHEN m.provider_timestamp >= NOW() - INTERVAL '28 days' THEN DATE(m.provider_timestamp) END) as days_active_last_28d,
    COUNT(DISTINCT CASE WHEN m.provider_timestamp >= ufm.first_message_date + INTERVAL '7 days' AND m.provider_timestamp < ufm.first_message_date + INTERVAL '14 days' THEN m.id END) as week2_messages,
    COUNT(DISTINCT CASE WHEN m.provider_timestamp >= ufm.first_message_date AND m.provider_timestamp < ufm.first_message_date + INTERVAL '28 days' THEN m.id END) as month1_messages
  FROM user_first_messages ufm
  JOIN person_contacts pc ON pc.person_id = ufm.person_id
  JOIN message m ON m.sender_person_contact_id = pc.id
  GROUP BY ufm.person_id, ufm.first_message_date
)
SELECT funnel_step, users,
  ROUND(100.0 * users::numeric / (SELECT COUNT(*) FROM user_first_messages), 1) as pct_of_start,
  ROUND(100.0 * users::numeric / LAG(users) OVER (ORDER BY step_num), 1) as conversion,
  ROUND(100.0 * (LAG(users) OVER (ORDER BY step_num) - users)::numeric / LAG(users) OVER (ORDER BY step_num), 1) as drop_off
FROM (
  SELECT 1 as step_num, 'Step 1: First Message Sent' as funnel_step, COUNT(*) as users FROM user_first_messages
  UNION ALL SELECT 2, 'Step 2: 5+ Messages Week 1', COUNT(CASE WHEN week1_messages >= 5 THEN 1 END) FROM user_complete_behavior
  UNION ALL SELECT 3, 'Step 3: Active 6+ Days Week 1', COUNT(CASE WHEN days_active_week1 >= 6 THEN 1 END) FROM user_complete_behavior
  UNION ALL SELECT 4, 'Step 4: 3+ Messages Week 2', COUNT(CASE WHEN week2_messages >= 3 THEN 1 END) FROM user_complete_behavior
  UNION ALL SELECT 5, 'Step 5: 100+ Messages Month 1 (28d)', COUNT(CASE WHEN month1_messages >= 100 THEN 1 END) FROM user_complete_behavior
  UNION ALL SELECT 6, 'Step 6: Power User (100+ msgs AND 24+ days active last 28d)', COUNT(CASE WHEN messages_last_28d >= 100 AND days_active_last_28d >= 24 THEN 1 END) FROM user_complete_behavior
) funnel_data ORDER BY step_num;
```

| Step | Users | % of Start | Conversion | Drop-off | Notes |
|------|-------|-----------|-----------|----------|-------|
| **Step 1: First Message Sent** | X | 100.0% | - | - | Baseline (28+ days old) |
| **Step 2: 5+ Messages Week 1** | X | X% | X% | X% | Initial engagement |
| **Step 3: Active 6+ Days Week 1** | X | X% | X% | X% | Daily habit |
| **Step 4: 3+ Messages Week 2** | X | X% | X% | X% | Week 2 retention |
| **Step 5: 100+ Messages Month 1 (28d)** | X | X% | X% | X% | Volume threshold |
| **Step 6: Power User (100+ msgs AND 24+ days active last 28d)** | X | X% | X% | X% | Sustained engagement |

**Power User = 100+ messages in last 28 days AND active 24+ days in last 28 days**

---

## Onboarding Funnel (7+ days old)

```sql
WITH onboarding_stats AS (
  SELECT
    COUNT(*) as total_created,
    COUNT(CASE WHEN state IN ('INITIATOR_JOINED', 'COMPLETED') THEN 1 END) as initiator_joined,
    COUNT(CASE WHEN state = 'COMPLETED' THEN 1 END) as completed
  FROM conversation_onboarding
  WHERE created_at >= '2025-09-10'
),
onboarded_users AS (
  SELECT DISTINCT cp.person_id
  FROM conversation_participant cp
  JOIN conversation c ON c.id = cp.conversation_id AND c.type = 'GROUP'
  JOIN conversation_onboarding co ON co.conversation_id = c.id
  WHERE co.state = 'COMPLETED' AND co.created_at >= '2025-09-10'
),
user_first_messages AS (
  SELECT p.id as person_id, MIN(m.provider_timestamp) as first_message_date
  FROM persons p
  JOIN onboarded_users ou ON ou.person_id = p.id
  JOIN person_contacts pc ON pc.person_id = p.id
  JOIN message m ON m.sender_person_contact_id = pc.id
  GROUP BY p.id
  HAVING MIN(m.provider_timestamp) <= NOW() - INTERVAL '7 days'
),
user_week1_behavior AS (
  SELECT
    ufm.person_id,
    COUNT(DISTINCT CASE WHEN m.provider_timestamp >= ufm.first_message_date AND m.provider_timestamp < ufm.first_message_date + INTERVAL '7 days' THEN m.id END) as week1_messages,
    COUNT(DISTINCT CASE WHEN m.provider_timestamp >= ufm.first_message_date AND m.provider_timestamp < ufm.first_message_date + INTERVAL '7 days' THEN DATE(m.provider_timestamp) END) as days_active_week1
  FROM user_first_messages ufm
  JOIN person_contacts pc ON pc.person_id = ufm.person_id
  JOIN message m ON m.sender_person_contact_id = pc.id
  GROUP BY ufm.person_id, ufm.first_message_date
)
SELECT funnel_step, users,
  ROUND(100.0 * users::numeric / (SELECT total_created FROM onboarding_stats), 1) as pct_of_start,
  ROUND(100.0 * users::numeric / LAG(users) OVER (ORDER BY step_num), 1) as conversion,
  ROUND(100.0 * (LAG(users) OVER (ORDER BY step_num) - users)::numeric / LAG(users) OVER (ORDER BY step_num), 1) as drop_off
FROM (
  SELECT 0 as step_num, 'Step 0: Onboarding Created' as funnel_step, (SELECT total_created FROM onboarding_stats) as users
  UNION ALL SELECT 1, 'Step 1: Initiator Joined', (SELECT initiator_joined FROM onboarding_stats)
  UNION ALL SELECT 2, 'Step 2: Onboarding Completed', (SELECT completed FROM onboarding_stats)
  UNION ALL SELECT 3, 'Step 3: First Message Sent (7d+)', (SELECT COUNT(*) FROM user_first_messages)
  UNION ALL SELECT 4, 'Step 4: 5+ Messages Week 1', COUNT(CASE WHEN week1_messages >= 5 THEN 1 END) FROM user_week1_behavior
  UNION ALL SELECT 5, 'Step 5: Active 6+ Days Week 1', COUNT(CASE WHEN days_active_week1 >= 6 THEN 1 END) FROM user_week1_behavior
) funnel_data ORDER BY step_num;
```

| Step | Users | % of Start | Conversion | Drop-off | Notes |
|------|-------|-----------|-----------|----------|-------|
| **Step 0: Onboarding Created** | X | 100.0% | - | - | Baseline |
| **Step 1: Initiator Joined** | X | X% | X% | X% | First person joins |
| **Step 2: Onboarding Completed** | X | X% | X% | X% | Both partners complete |
| **Step 3: First Message Sent (7d+)** | X | X% | X% | X% | Started messaging |
| **Step 4: 5+ Messages Week 1** | X | X% | X% | X% | Initial engagement |
| **Step 5: Active 6+ Days Week 1** | X | X% | X% | X% | Daily habit |
