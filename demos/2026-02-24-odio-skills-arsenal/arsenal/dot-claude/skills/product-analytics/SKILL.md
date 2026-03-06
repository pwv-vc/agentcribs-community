---
name: product-analytics
description: Framework for analyzing product usage data and identifying patterns. Use when performing deep analysis of user behavior and engagement metrics.
allowed-tools:
  - Bash
  - Read
  - Write
  - Grep
  - Glob
---

# Product Analytics Skill

Framework for transforming raw product data into actionable insights.

## When to Use

Use this skill when you need to:
- Analyze user behavior patterns
- Identify engagement trends
- Investigate feature usage
- Understand user segments
- Find opportunities for improvement
- Support product decisions with data

## Analysis Framework

### 1. Define the Question

Start with a clear, specific question:
- ❌ Bad: "How are users doing?"
- ✅ Good: "What types of 1:1 messages from Codel get the most positive reactions from users?"

**Write down:**
- Primary question
- Success metric
- Time range
- User segment (if applicable)

### 2. Collect Comprehensive Data

**IMPORTANT:** Use the sql-reader skill to query production data.

Collect:
- **Quantitative data:** Counts, rates, distributions, trends
- **Qualitative data:** Actual message content, user names, specific examples
- **Context data:** Time of day, user characteristics, conversation state

**Best practices:**
- Query at different granularities (daily, weekly, monthly)
- Get both aggregates AND individual examples
- Include negative cases (what DIDN'T work)
- Gather enough data to see patterns (not just outliers)

### 3. Create Structured Analysis

**MANDATORY:** Create a markdown file with the following sections:

#### Executive Summary
```markdown
# {Topic} Analysis

**Analysis Date:** {YYYY-MM-DD}
**Time Range:** {e.g., "Last 30 days" or "All time"}
**Total Records Analyzed:** {number}

## Key Findings
1. {Most important insight}
2. {Second most important insight}
3. {Third most important insight}

## Top Recommendation
{One-sentence actionable recommendation}
```

#### Metrics Overview
```markdown
## Metrics Overview

| Metric | Value | Benchmark | Status |
|--------|-------|-----------|--------|
| Total X | 1,234 | - | - |
| Conversion Rate | 12.5% | 10% | ✅ Above target |
| Engagement Rate | 0.7% | - | ⚠️ Low |
```

#### Detailed Analysis Tables

**CRITICAL:** Use tables to organize data.

**Example: Reaction Analysis**
```markdown
| Reaction Type | Count | % of Total | Top User | Pattern |
|---------------|-------|------------|----------|---------|
| Loved | 61 | 85.9% | craig (35) | Meta-commentary |
| Liked | 10 | 14.1% | Varied | Practical info |
| Disliked | 3 | 4.2% | samuel, Mary, joe | Suggested responses |
```

**For each data point, ask:**
- What does this number mean?
- Is this good or bad?
- What's the trend?
- Who are the outliers?

#### Pattern Analysis

Identify and name patterns:

```markdown
## Pattern 1: The "Power User Effect"
**Observation:** craig provides 49% of all reactions (35 out of 71)

**Analysis:**
- One user drives nearly half of all engagement
- This user is highly engaged with coaching
- Uses reactions as a feedback mechanism
- May not represent typical user behavior

**Implication:** Engagement metrics may be skewed by power users
```

**Pattern Template:**
```markdown
## Pattern {N}: {Name}
**Observation:** {What you see in the data}
**Analysis:** {Why this matters, what it means}
**Implication:** {So what? What does this mean for the product?}
```

#### User Segmentation

If applicable, segment users:
```markdown
## User Segments

### High Engagers (n=3)
- **Who:** craig, karen, Mallory
- **Behavior:** Regular reactions, loves meta-commentary
- **Need:** Growth-oriented coaching

### Low Engagers (n=10)
- **Who:** Most users
- **Behavior:** Rarely react, passive consumption
- **Need:** Unknown - may be satisfied, may not see value in reactions

### Negative Reactors (n=3)
- **Who:** samuel, Mary, joe
- **Behavior:** Used dislike button
- **Need:** Different message types, less presumption
```

#### Qualitative Analysis

**CRITICAL:** Don't just show numbers. Explain WHY.

```markdown
## Why These Patterns Exist

### Hypothesis 1: Meta-commentary resonates because...
- Provides immediate positive reinforcement
- Uses specific examples from user's own behavior
- Celebrates growth (motivating)
- Emoji usage (🌟 💞) conveys warmth

**Evidence:**
- 85% of craig's loved reactions are meta-commentary
- Common phrases: "Notice the shift", "Let yourself feel"

### Hypothesis 2: Suggested responses are polarizing because...
- Some users want help (craig)
- Others feel it's presumptuous (joe, Mary)
- Depends on user preference and communication style

**Evidence:**
- craig loved 5+ suggested responses
- joe and Mary both disliked suggested responses
- No middle ground - either love or hate
```

#### Failure Modes

**IMPORTANT:** Always include what went wrong.

```markdown
## What Didn't Work

### Disliked Message Analysis

| Date | User | Message Type | Why Disliked | Fix |
|------|------|--------------|--------------|-----|
| 2025-11-14 | samuel | Direct Reply | Fabricated quote | Never use quotes unless verbatim |
| 2025-10-16 | Mary | Suggested Response | Felt inauthentic | Personalize feature to user preference |
| 2025-09-14 | joe | Suggested Response | Presumptuous | Ask first if user wants drafts |

**Pattern:** 2 of 3 dislikes are suggested responses
**Root cause:** One-size-fits-all approach to a preference-based feature
**Recommended fix:** Add user setting for suggested responses
```

### 4. Data Visualization Recommendations

While you can't create charts directly, recommend visualizations:

```markdown
## Recommended Visualizations

1. **Time series:** Reactions per week (identify trends)
2. **Distribution:** Histogram of reaction types
3. **Funnel:** Messages sent → reactions received
4. **Heatmap:** Reaction type by user segment
5. **Comparative:** Loved vs. Disliked message characteristics
```

### 5. Statistical Context

Provide context for numbers:

```markdown
## Statistical Context

- **Sample size:** 71 reactions out of 10,000+ messages
- **Confidence:** 0.7% reaction rate (low but consistent)
- **Bias:** Power user skew (49% from one user)
- **Significance:** 96% positive rate is statistically meaningful
- **Trend:** Need historical data to identify trends
```

### 6. Insights and Recommendations

**Format:**
```markdown
## Key Insights

### Insight 1: Meta-commentary drives engagement
**What we learned:** Messages with 🌟 celebrating user growth get most love (85%)

**Why it matters:** Users value affirmation and progress tracking

**What to do:**
1. Increase frequency of meta-commentary
2. Train AI to identify more growth moments
3. A/B test different affirmation styles

**Success metric:** Increase reaction rate from 0.7% to 1.5%

### Insight 2: Suggested responses are divisive
**What we learned:** Some users love drafts (craig: 5+ loved), others hate them (2 dislikes)

**Why it matters:** One-size-fits-all approach fails for preference-based features

**What to do:**
1. Add user preference: "Do you want message drafts?"
2. Default to OFF, let users opt-in
3. Track adoption and satisfaction by preference

**Success metric:** 0% dislikes for suggested responses among opted-in users
```

## Analysis Quality Checklist

Before finishing your analysis, verify:

### Data Quality
- ✅ Queried production database (not dev/test)
- ✅ Sample size is meaningful (n > 30 for stats)
- ✅ Time range is specified
- ✅ Data source is documented
- ✅ Limitations are acknowledged

### Analysis Depth
- ✅ Quantitative data in tables
- ✅ Patterns identified and named
- ✅ Qualitative examples included
- ✅ Hypotheses for WHY patterns exist
- ✅ Failure modes analyzed
- ✅ User segmentation (if applicable)

### Actionability
- ✅ Clear insights stated
- ✅ Recommendations are specific
- ✅ Success metrics defined
- ✅ Next steps provided
- ✅ Prioritization guidance (impact/effort)

### Presentation
- ✅ Executive summary at top
- ✅ Tables for all data
- ✅ Consistent formatting
- ✅ Spell-checked and proofread
- ✅ File saved with descriptive name

## Common Patterns to Look For

### Engagement Patterns
- **Power users:** Small % driving most activity
- **Activation:** When do users first engage?
- **Retention:** Do users come back?
- **Frequency:** Daily, weekly, monthly usage?

### Behavioral Patterns
- **Feature adoption:** What % use each feature?
- **Success paths:** What do successful users do?
- **Drop-off points:** Where do users stop?
- **Preference clusters:** Do user types emerge?

### Quality Patterns
- **Satisfaction signals:** Likes, completion rates
- **Dissatisfaction signals:** Dislikes, churn, support tickets
- **Value moments:** When do users express gratitude?
- **Friction points:** Where do users get stuck?

### Temporal Patterns
- **Time of day:** When are users most active?
- **Day of week:** Weekday vs. weekend usage
- **Seasonality:** Monthly/quarterly trends
- **Cohorts:** New vs. old users

## Output Format

Your final analysis file should follow this structure:

```
1. Title and metadata
2. Executive Summary (1-3 bullet points)
3. Key Findings (numbered list)
4. Top Recommendation (one sentence)
5. Metrics Overview (table)
6. Detailed Analysis (multiple sections with tables)
7. Pattern Analysis (named patterns with implications)
8. User Segmentation (if applicable)
9. Qualitative Analysis (why these patterns exist)
10. What Didn't Work (failure modes)
11. Insights and Recommendations (actionable)
12. Recommended Visualizations
13. Statistical Context
14. Next Steps
```

## Example File Structure

```markdown
# Message Reactions Analysis

**Analysis Date:** 2025-11-14
**Time Range:** All time
**Total Reactions:** 71

## Executive Summary
- 96% positive reaction rate (61 loved, 10 liked, 3 disliked)
- One power user (craig) drives 49% of all reactions
- Meta-commentary messages get most love; suggested responses are polarizing

## Top Recommendation
Add user preference setting for suggested responses to reduce dislikes and increase satisfaction.

[... rest of analysis follows framework above ...]
```

## Integration with Other Skills

**Data skills:**
- `sql-reader` - Query production data
- `funnel-analysis` - User activation funnel (use for retention/activation questions)

**Output skills:**
- `feature-spec-writer` - Create PM specs
- `linear-manager` - Create tickets

## Notes

- **Be thorough:** Surface-level analysis isn't useful
- **Show your work:** Include query examples and data samples
- **Think like a PM:** Ask "so what?" for every finding
- **Be honest:** Include limitations and uncertainties
- **Make it actionable:** Every insight should lead to a decision

Remember: Good analysis tells a story. What did we learn? Why does it matter? What should we do?
