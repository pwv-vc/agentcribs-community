# Relationship Analyst Skill

Calculate relationship affect metrics and health insights from production data.

**This skill provides helper scripts for common metrics AND supports flexible SQL exploration for ad-hoc questions.**

## Quick Start

All scripts require a `person_id` (from either partner in a couple). Optional `days` parameter defaults to 56 (8 weeks).

### 1. Affect Ratio (Positive/Negative Balance)

**Research-based "Magic Ratio"**: Healthy relationships have ≥5:1 positive to negative interactions.

```bash
# Calculate affect ratio for person_id 123
arsenal/dot-claude/skills/relationship-analyst/affect_ratio.sh 123

# Or for different time periods
arsenal/dot-claude/skills/relationship-analyst/affect_ratio.sh 123 28   # 4 weeks
arsenal/dot-claude/skills/relationship-analyst/affect_ratio.sh 123 84   # 12 weeks
```

**Output:**
- Positive/negative message counts
- Affect ratio (e.g., 7.2 = 7.2:1 ratio)
- Health assessment (Exceptional, Healthy, At-Risk, Distress)

### 2. Repair Rate (Conflict De-escalation)

**Repair Rate**: % of conflicts where partner responds without escalating. ≥75% is healthy.

```bash
# Calculate repair rate for a couple
arsenal/dot-claude/skills/relationship-analyst/repair_rate.sh 123

# Different time periods
arsenal/dot-claude/skills/relationship-analyst/repair_rate.sh 123 28
```

**Output:**
- Conflicts introduced by each partner
- Each partner's repair rate when the other starts conflict
- Shows who is defensive vs. who can de-escalate

### 3. Affect Distribution (Detailed Breakdown)

**Affect Distribution**: See exactly which affects appear most frequently.

```bash
# Show all affects for a couple
arsenal/dot-claude/skills/relationship-analyst/affect_distribution.sh 123

# Different time periods
arsenal/dot-claude/skills/relationship-analyst/affect_distribution.sh 123 28
```

**Output:**
- Count of each specific affect (Partner-Affection, Humor, Partner-Criticism, etc.)
- Per-person and partnership totals
- Sorted by frequency (most common first)

## Research-Based Framework Summary

### Affect Ratio Thresholds
- **≥20:1** - Upper target (exceptional)
- **≥5:1** - Lower target (research "magic ratio", healthy)
- **1:1-5:1** - At-risk, needs improvement
- **<1:1** - Distress, high-priority intervention

### Repair Rate Thresholds
- **≥75%** - Healthy (good emotional regulation)
- **<75%** - Highly defensive (poor conflict management)

### Destructive Communication Patterns (Most Toxic)
1. **Criticism** - Attacking partner's character
2. **Contempt** - Mockery, sarcasm, disrespect (strongest predictor of relationship breakdown)
3. **Defensiveness** - Making excuses, counter-attacking
4. **Stonewalling** - Withdrawal, silent treatment

## Affect Categories

Our system uses AI-classified affects:

### Positive Affects
- `Partner-Affection` - warmth, caring expressions
- `Partner-Validation` - acknowledgment, understanding
- `Partner-Enthusiasm` - joy, interest, excitement
- `Humor` - playfulness, jokes
- `Partner-Interest` - engaged listening, curiosity

### Negative Affects
- `Partner-Criticism` - attacking character (destructive pattern #1)
- `Partner-Contempt` - mockery, disrespect (destructive pattern #2)
- `Partner-Defensiveness` - excuses, counter-attacking (destructive pattern #3)
- `Stonewalling` - withdrawal, silent treatment (destructive pattern #4)
- `Partner-Complaint` - expressing displeasure (milder than criticism)
- `Partner-Anger` - frustration, irritation
- `Partner-Sadness` - hurt, disappointment
- `Partner-Belligerence` - provocative behavior
- `Partner-Domineering` - controlling behavior
- `Partner-Fear / Tension` - anxiety, nervousness
- `Partner-Threats` - ultimatums, intimidation
- `Partner-Disgust` - revulsion, disdain
- `Partner-Whining` - complaining tone

## Example Workflow

```bash
# 1. Find a person_id (e.g., Craig = 123, Amy = 456)
arsenal/dot-claude/skills/sql-reader/connect.sh "SELECT id, name FROM persons WHERE name ILIKE '%craig%';"

# 2. Calculate affect ratio
arsenal/dot-claude/skills/relationship-analyst/affect_ratio.sh 123

# 3. Check repair rate
arsenal/dot-claude/skills/relationship-analyst/repair_rate.sh 123

# 4. See detailed affect breakdown
arsenal/dot-claude/skills/relationship-analyst/affect_distribution.sh 123
```

## Ad-Hoc SQL Queries

For exploratory questions beyond standard metrics, write custom SQL. See `SKILL.md` for examples:

**Standard Metrics (use helper scripts above):**
- Single person affect ratio
- Couple combined affect ratio
- Repair rate calculation
- Affect distribution

**Common Ad-Hoc Questions (write custom SQL):**
- "What did they fight about?" - Query conflict messages with content
- "Message volume analysis" - Check classification rates and activity levels
- Any other affect-related exploratory questions

**For schema-related queries:**
- "Find couple by name" - See sql-reader skill "Relationship Coaching Schema Patterns"
- Understanding table relationships - Run sql-reader bootstrap commands
- Join patterns and schema gotchas - See sql-reader documentation

## Data Requirements

These scripts require:
- `message` table with `provider_timestamp`
- `message_enrichment` table with `affect` and `conflict_state` columns
- `persons` and `conversation_participant` tables for couple identification
- `person_contacts` table linking messages to persons

## Troubleshooting

### "No rows returned"
- Verify person_id exists: `arsenal/dot-claude/skills/sql-reader/connect.sh "SELECT * FROM persons WHERE id = 123;"`
- Check if person has messages in time window
- Ensure message_enrichment table has affect classifications

### "affect_ratio is NULL"
- No negative messages in time window (cannot calculate ratio)
- Check message_enrichment.affect column for classifications

### "repair_rate is NULL"
- No conflicts with partner responses in time window
- Either couple had no conflicts, or conflicts had no responses

## References

- **Affect Ratio Research**: Published studies on positive-to-negative interaction ratios in relationships
- **Relationship Communication Patterns**: Research on constructive vs destructive communication styles
