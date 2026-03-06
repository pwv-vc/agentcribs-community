---
description: Answer any product/data question and create a spec if actionable insights are found
---

# Question to Spec Command

**Purpose:** Universal workflow for turning product questions into actionable specs.

## When to Use

Use this command for ANY product/data question:
- **User feedback:** "Was there any user feedback in the last 24 hours?"
- **Funnel analysis:** "Is our funnel broken?"
- **Retention:** "Did retention drop this week?"
- **Feature impact:** "Is the new feature working?"
- **Churn:** "Why are users churning in week 2?"

**Target cron usage:**
```bash
# Daily user feedback check
0 9 * * * claude -p "/question-to-spec 'Was there any user feedback in the last 24 hours?'"

# Weekly funnel health check
0 9 * * 1 claude -p "/question-to-spec 'Is our funnel broken?'"

# Ad-hoc questions
claude -p "/question-to-spec 'What features are users requesting?'"
```

## Workflow

**CRITICAL: This is a data-driven workflow. Let the data guide the analysis.**

### Step 0: Parse the Question

Understand what the user is asking:
- **Data sources:** What data is needed? (messages, reactions, funnel metrics, retention cohorts)
- **Time range:** Last 24 hours, last week, last month, all time?
- **Analysis type:** User feedback, funnel, retention, feature usage, churn?
- **Expected output:** Insights only, or insights + actionable spec?

**Examples:**

| Question | Data Source | Analysis Type | Time Range |
|----------|-------------|---------------|------------|
| "Was there any user feedback in the last 24 hours?" | messages, reactions | User feedback | 24 hours |
| "Is our funnel broken?" | onboarding, messages | Funnel | All time |
| "Did retention drop this week?" | messages, users | Retention cohort | This week vs. last week |
| "What features are users requesting?" | messages | User feedback | Last 30 days |

### Step 1: Gather Data

**MANDATORY: Use the appropriate skills based on question type**

#### User Feedback Questions
Use `codel-1on1-reactions-analysis` skill:
1. Announce: "I'm using the codel-1on1-reactions-analysis skill to analyze user feedback..."
2. Follow the skill workflow:
   - Run Data Model Quickstart (6 commands from sql-reader)
   - Query reactions to Codel 1:1 messages
   - Query feature requests in user messages
   - Calculate summary statistics
3. Create analysis file: `analysis_user_feedback_{YYYY-MM-DD}.md`

#### Funnel Questions
Use `funnel-analysis` skill:
1. Announce: "I'm using the funnel-analysis skill to analyze the user journey..."
2. Follow the skill workflow:
   - Define the funnel (start event → success event)
   - Query funnel data with sql-reader
   - Calculate conversion rates and drop-offs
   - Identify bottlenecks
3. Create analysis file: `analysis_funnel_{YYYY-MM-DD}.md`

#### Product Analytics Questions
Use `product-analytics` skill:
1. Announce: "I'm using the product-analytics skill for deep analysis..."
2. Follow the skill workflow:
   - Query production data with sql-reader
   - Create structured analysis with metrics
   - Identify patterns and insights
3. Create analysis file: `analysis_{topic}_{YYYY-MM-DD}.md`

#### Custom Questions
Use `sql-reader` directly:
1. Announce: "I'm querying production data to answer your question..."
2. Run appropriate SQL queries
3. Create analysis file: `analysis_custom_{YYYY-MM-DD}.md`

### Step 2: Analyze and Summarize

Create a markdown analysis file with:

```markdown
# Analysis: {Question}

**Date:** {YYYY-MM-DD}
**Time Range:** {e.g., "Last 24 hours"}
**Data Sources:** {Tables queried}

## Question
{Original question}

## Executive Summary
- {Key finding 1}
- {Key finding 2}
- {Key finding 3}

## Data Overview
{Metrics, counts, percentages}

## Detailed Analysis
{Tables, patterns, insights}

## Key Insights
{Numbered insights with "why this matters"}

## Actionable Items
{List of potential actions, if any}
```

**Save to:** `analysis_{topic}_{YYYY-MM-DD}.md`

### Step 3: Determine Highest-Value Opportunity

**Philosophy:** ALWAYS create a spec for the highest-value thing to build right now.

**Decision criteria:**
- ✅ What problem has the biggest user impact?
- ✅ What data is most compelling (new feedback, funnel drops, affect ratios, segment patterns)?
- ✅ What's the highest ROI opportunity identified in the analysis?
- ✅ Even if there's limited new data, what's the most important ongoing issue to address?

**Example prioritization:**

| Question | Finding | Spec Created For | Rationale |
|----------|---------|------------------|-----------|
| "User feedback last 24h?" | 2 items: 1 dislike (quote fabrication) + 1 feature request (7-day streak) | **Fix quote fabrication** (P0) OR **7-day streak** (P1) | Even with 2 items, quote fabrication is a trust violation (highest priority) |
| "User feedback last 24h?" | 0 new items, but analysis shows funnel at 42% (was 75%) | **Fix partner invite flow** (P0) | No new feedback, but funnel data is critical |
| "Which segment has best affect ratios?" | Power users: 7:1 positive-to-negative, Churned users: 2:1 | **Improve conflict coaching for at-risk users** (P1) | Segment data shows opportunity to prevent churn |
| "Is our funnel broken?" | 42% partner join rate, was 75% last week | **Fix partner invitation email** (P0) | Major drop, critical fix needed |

### Step 4: Create Spec (ALWAYS)

**MANDATORY: Always launch the feature-opportunity-creator agent**

1. Announce: "Launching feature-opportunity-creator agent to create spec..."
2. Use the Task tool:
   ```
   Task(
     subagent_type="feature-opportunity-creator",
     description="Create spec from analysis",
     prompt="""
     Create a feature spec from this analysis:

     analysis_file: analysis_{topic}_{YYYY-MM-DD}.md
     topic: {topic}
     output_dir: specs/
     always_create_spec: true

     Where {topic} is the analysis type slug (e.g., "user-feedback", "funnel", "retention", "affect-ratios", "power-users", "segments")

     IMPORTANT: Always create a spec for the highest-value opportunity identified in the analysis, even if there's limited new data.
     """
   )
   ```
3. The agent will:
   - Read the analysis
   - Identify the highest-value opportunity (could be from new data OR broader patterns)
   - ALWAYS create spec in `specs/{topic}-YYYY-MM-DD.md` (deterministic filename)
   - Return spec details and priority

### Step 5: Output Summary

**For cron job logs (spec ALWAYS created):**

```
✅ Analysis complete - Spec created

📊 Question: {question}
📈 Data analyzed: {summary}

🎯 Top priority opportunity: {title}
- Priority: {P0/P1/P2/P3}
- Effort: {XS/S/M/L/XL}
- Impact: {description}
- Rationale: {why this is the highest-value thing to build now}

📄 Analysis: analysis_{topic}_{YYYY-MM-DD}.md
📋 Spec: specs/{topic}-YYYY-MM-DD.md

---
Next step: Run /spec-to-pr specs/{topic}-YYYY-MM-DD.md to create PR
```

## Example Flows

### Example 1: User Feedback (Actionable)

```bash
$ claude -p "/question-to-spec 'Was there any user feedback in the last 24 hours?'"

Analyzing the question...
- Data source: messages, reactions
- Analysis type: User feedback
- Time range: Last 24 hours

I'm using the codel-1on1-reactions-analysis skill...
[Queries reactions and feature requests]

📊 Data collected:
- 8 reactions (6 loved, 2 disliked)
- 3 feature requests
- 11 total items

Creating analysis file: analysis_user_feedback_2025-11-14.md

Launching feature-opportunity-creator agent...
[Agent creates spec]

✅ Analysis complete - Spec created

📊 Question: Was there any user feedback in the last 24 hours?
📈 Data analyzed: 8 reactions, 3 feature requests, 5 unique users

🎯 Top actionable item: Build 7-day streak for new users
- Priority: P1 (High)
- Impact: Increase Week 1 retention 31% → 50%

📄 Analysis: analysis_user_feedback_2025-11-14.md
📋 Spec: specs/user-feedback-2025-11-14.md

---
Next step: Run /spec-to-pr to create PR
```

### Example 2: User Feedback (Limited Data, Still Creates Spec)

```bash
$ claude -p "/question-to-spec 'Was there any user feedback in the last 24 hours?'"

Analyzing the question...
- Data source: messages, reactions
- Analysis type: User feedback
- Time range: Last 24 hours

I'm using the codel-1on1-reactions-analysis skill...
[Queries reactions and feature requests]

📊 Data collected:
- 1 reaction (👎 Disliked - quote fabrication issue)
- 1 feature request (7-day streak)
- 2 total items

Creating analysis file: analysis_user_feedback_2025-11-14.md

Launching feature-opportunity-creator agent...
[Agent identifies highest-value opportunity from analysis]

✅ Analysis complete - Spec created

📊 Question: Was there any user feedback in the last 24 hours?
📈 Data analyzed: 1 reaction (dislike), 1 feature request

🎯 Top priority opportunity: Fix quote fabrication in AI responses
- Priority: P0 (Critical)
- Effort: S (1-2 days)
- Impact: Prevent trust violations; affects all users
- Rationale: Quote fabrication is a critical trust issue that must be fixed immediately

📄 Analysis: analysis_user_feedback_2025-11-14.md
📋 Spec: specs/user-feedback-2025-11-14.md

---
Next step: Run /spec-to-pr specs/user-feedback-2025-11-14.md to create PR
```

### Example 3: Funnel Question (Actionable)

```bash
$ claude -p "/question-to-spec 'Is our funnel broken?'"

Analyzing the question...
- Data source: onboarding, messages
- Analysis type: Funnel
- Time range: All time (compare recent vs. historical)

I'm using the funnel-analysis skill...
[Queries onboarding funnel data]

📊 Data collected:
- Access codes: 89
- Partner joined: 37 (42%)
- Conversations: 30 (34%)
- Historical partner join rate: 75%

Creating analysis file: analysis_funnel_2025-11-14.md

Key finding: Partner join rate dropped from 75% to 42% (33 percentage points)

Launching feature-opportunity-creator agent...
[Agent creates spec]

✅ Analysis complete - Spec created

📊 Question: Is our funnel broken?
📈 Data analyzed: 89 access codes, 42% partner join rate (down from 75%)

🎯 Top actionable item: Fix partner invitation email delivery
- Priority: P0 (Critical)
- Impact: Restore partner join rate to 75% (2x current rate)

📄 Analysis: analysis_funnel_2025-11-14.md
📋 Spec: specs/funnel-2025-11-14.md

---
Next step: Run /spec-to-pr to create PR
```

### Example 4: Affect Ratio / Segment Analysis

```bash
$ claude -p "/question-to-spec 'Which user segment has the best affect ratios - are power users healthier in their communication?'"

Analyzing the question...
- Data source: messages, affect coding
- Analysis type: User segmentation + affect ratios
- Segments: Power users vs. casual users vs. churned users

I'm using the relationship-analyst skill...
[Calculates affect ratios for each segment]

📊 Data collected:
- Power users (10+ weeks active): 7:1 positive-to-negative ratio
- Casual users (2-9 weeks): 4:1 ratio
- Churned users (1 week only): 2:1 ratio

Creating analysis file: analysis_affect-ratios_2025-11-14.md

Launching feature-opportunity-creator agent...
[Agent identifies opportunity to help at-risk users]

✅ Analysis complete - Spec created

📊 Question: Which user segment has the best affect ratios?
📈 Data analyzed: 150 users across 3 segments, 10,000+ messages

🎯 Top priority opportunity: Add proactive conflict coaching for at-risk users
- Priority: P1 (High)
- Effort: M (1 sprint)
- Impact: Improve affect ratios for casual users from 4:1 → 6:1, reduce churn
- Rationale: Churned users have 2:1 ratio (unhealthy); early intervention could prevent churn

📄 Analysis: analysis_affect-ratios_2025-11-14.md
📋 Spec: specs/affect-ratios-2025-11-14.md

---
Next step: Run /spec-to-pr specs/affect-ratios-2025-11-14.md to create PR
```

## Question Type Mapping

| Question Pattern | Skill to Use | Example |
|------------------|--------------|---------|
| "feedback", "reactions", "requested" | codel-1on1-reactions-analysis | "What feedback did we get?" |
| "funnel", "conversion", "drop-off" | funnel-analysis | "Where are users dropping off?" |
| "retention", "churn", "cohort" | funnel-analysis (retention funnel) | "Is retention improving?" |
| "engagement", "usage", "activity" | product-analytics | "How engaged are users?" |
| "affect ratio", "communication health" | relationship-analyst | "Are power users healthier?" |
| "segment", "power users", "who" | user-segmentation + product-analytics | "Which segment churns most?" |
| "topics", "conflict", "what do users discuss" | product-analytics + SQL | "What topics cause conflict?" |
| Custom SQL needed | sql-reader directly | "How many messages sent on Sundays?" |

## Configuration

### Environment Variables
```bash
export QUESTION_TO_SPEC_MIN_ITEMS=3  # Minimum data points for spec creation
```

### Override in Prompt
```bash
# Require more data
claude -p "/question-to-spec 'User feedback?' min-items=5"

# Force spec creation even with low data
claude -p "/question-to-spec 'User feedback?' --force-spec"
```

## Cron Job Setup

```bash
# Daily user feedback at 9am
0 9 * * * cd /path/to/ct3 && claude -p "/question-to-spec 'Was there any user feedback in the last 24 hours?'" >> /var/log/question-to-spec.log 2>&1

# Weekly funnel check on Mondays at 10am
0 10 * * 1 cd /path/to/ct3 && claude -p "/question-to-spec 'Is our funnel broken?'" >> /var/log/question-to-spec.log 2>&1

# Ad-hoc: Check retention every day at 11am
0 11 * * * cd /path/to/ct3 && claude -p "/question-to-spec 'Did retention drop this week?'" >> /var/log/question-to-spec.log 2>&1
```

## Skills and Agents Used

1. **codel-1on1-reactions-analysis** (skill) - User feedback analysis
2. **funnel-analysis** (skill) - Funnel and retention analysis
3. **product-analytics** (skill) - Deep product analysis
4. **sql-reader** (skill) - Direct database queries
5. **feature-opportunity-creator** (agent) - Creates specs from analysis

## Notes

- **Flexible routing:** Command chooses the right skill based on question type
- **Always creates specs:** Every analysis yields a spec for the highest-value opportunity
- **Daily product discovery:** Spec might be based on new data OR broader patterns (funnels, segments, affect ratios)
- **Sophisticated questions supported:** Affect ratios, user segments, conflict topics, funnel drops, etc.
- **Consistent output:** All analysis files follow same format
- **Cron-friendly:** Clean logs with summary for monitoring
- **Composable:** Pairs with /spec-to-pr for full automation
- **Deterministic filenames:** `specs/{topic}-YYYY-MM-DD.md` format enables predictable cron workflows

Remember: The goal is to turn **any product question** into **actionable specs** by identifying the highest-value thing to build right now.
