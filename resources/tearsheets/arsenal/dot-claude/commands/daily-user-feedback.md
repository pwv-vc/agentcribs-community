---
description: Automated daily analysis of user feedback with Linear ticket creation (for cron jobs)
---

# Daily User Feedback Analysis (Automated)

**Purpose:** Run as a daily cron job to analyze user feedback, prioritize opportunities, and create Linear tickets automatically.

**Target cron usage:**
```bash
0 9 * * * cd /path/to/ct3 && claude -p "Run /daily-user-feedback"
```

## Workflow

**CRITICAL: This is a fully automated workflow. No user interaction required.**

### Step 0: Configuration
- **Time range:** Last 24 hours (fixed)
- **Assignee:** cursor (default, can be overridden)
- **Min items:** 3 (default - won't create tickets for <3 feedback items)
- **Output:** Ticket URL for cron logs

### Step 1: Analyze User Feedback
**MANDATORY: Use the codel-1on1-reactions-analysis skill**

1. Announce: "Analyzing user feedback from last 24 hours..."
2. Follow the skill workflow:
   - Run Data Model Quickstart (6 commands from sql-reader)
   - Query reactions to Codel 1:1 messages
   - Query feature requests in user messages
   - Query power reactors
   - Calculate reaction summary statistics
3. Create markdown analysis file: `codel_1on1_feedback_YYYY-MM-DD.md`
4. Include:
   - Executive summary
   - Top 3 feedback items
   - Reaction analysis tables
   - Feature request analysis
   - Key insights and recommendations

### Step 2: Create Feature Spec and Linear Ticket
**MANDATORY: Launch the feature-opportunity-creator agent**

1. Announce: "Launching feature-opportunity-creator agent..."
2. Use the Task tool to launch the agent:
   ```
   Task(
     subagent_type="feature-opportunity-creator",
     description="Create spec and ticket from feedback",
     prompt="""
     Create a feature spec and Linear ticket from this analysis:

     analysis_file: codel_1on1_feedback_{YYYY-MM-DD}.md
     assignee: cursor
     min_items: 3
     """
   )
   ```
3. The agent will autonomously:
   - Read the analysis file
   - Check if data is sufficient (3+ items)
   - If insufficient: Save summary, skip ticket creation
   - If sufficient:
     - Prioritize top feedback item
     - Create feature spec in markdown
     - Create Linear ticket assigned to cursor
     - Return ticket URL

### Step 3: Output Summary
**For cron job logs:**

**Success case (ticket created):**
```
✅ Daily user feedback analysis complete (YYYY-MM-DD)

📊 Data analyzed:
- {n} reactions ({%} positive)
- {m} feature requests
- {k} unique users

🎯 Top feedback item:
"{Title}"
- Priority: {P0/P1/P2/P3}
- Impact: {brief description}

🎫 Linear ticket created:
{TEAM-123}: {URL}
Assigned to: @cursor

📄 Full report:
{path}/codel_1on1_feedback_{YYYY-MM-DD}.md

---
Next run: Tomorrow at 9am UTC
```

**Insufficient data case (no ticket):**
```
⚠️ Daily user feedback analysis complete (YYYY-MM-DD)

📊 Data analyzed:
- {n} reactions
- {m} feature requests
Total: {n+m} items

❌ No Linear ticket created - insufficient data (need 3+ items)

📄 Summary saved:
{path}/codel_1on1_feedback_{YYYY-MM-DD}.md

---
Next run: Tomorrow at 9am UTC
```

## Example Run

**Scenario 1: Insufficient data**
```bash
$ claude -p "Run /daily-user-feedback"

Analyzing user feedback from last 24 hours...
[Runs codel-1on1-reactions-analysis skill]

Launching feature-opportunity-creator agent...
[Agent evaluates: only 2 items, skips ticket creation]

⚠️ Daily user feedback analysis complete (2025-11-14)

📊 Data analyzed:
- 1 reaction (👎 Disliked)
- 1 feature request
Total: 2 items

❌ No Linear ticket created - insufficient data (need 3+ items)

📄 Summary saved:
/home/odio/Hacking/codel/ct3/codel_1on1_feedback_2025-11-14.md

---
Next run: Tomorrow at 9am UTC
```

**Scenario 2: Sufficient data**
```bash
$ claude -p "Run /daily-user-feedback"

Analyzing user feedback from last 24 hours...
[Runs codel-1on1-reactions-analysis skill]

Launching feature-opportunity-creator agent...
[Agent creates spec and ticket]

✅ Daily user feedback analysis complete (2025-11-14)

📊 Data analyzed:
- 8 reactions (75% positive)
- 3 feature requests
- 5 unique users

🎯 Top feedback item:
"Build 7-day streak for new users"
- Priority: P1 (High)
- Impact: Increase Week 1 retention from 31% to 50%

🎫 Linear ticket created:
CODEL-789: https://linear.app/codel/issue/CODEL-789
Assigned to: @cursor

📄 Full report:
/home/odio/Hacking/codel/ct3/codel_1on1_feedback_2025-11-14.md

---
Next run: Tomorrow at 9am UTC
```

## Configuration Options

### Override via Prompt
```bash
# Custom assignee
claude -p "/daily-user-feedback assignee=samuel"

# Custom time range (not recommended - breaks 24h cadence)
claude -p "/daily-user-feedback time-range=48-hours"

# Skip ticket creation (analysis only)
claude -p "/daily-user-feedback --no-ticket"
```

## Skills and Agents Used

1. **codel-1on1-reactions-analysis** (skill) - Query and analyze feedback data
2. **sql-reader** (skill) - Query production database
3. **feature-opportunity-creator** (agent) - Creates specs and Linear tickets

## Cron Job Setup

### Add to crontab:
```bash
crontab -e
```

### Example entries:
```bash
# Daily at 9am UTC
0 9 * * * cd /home/odio/Hacking/codel/ct3 && /usr/local/bin/claude -p "Run /daily-user-feedback" >> /var/log/daily-feedback.log 2>&1

# Monday-Friday at 9am UTC (skip weekends)
0 9 * * 1-5 cd /home/odio/Hacking/codel/ct3 && /usr/local/bin/claude -p "Run /daily-user-feedback" >> /var/log/daily-feedback.log 2>&1

# Twice daily: 9am and 5pm UTC
0 9,17 * * * cd /home/odio/Hacking/codel/ct3 && /usr/local/bin/claude -p "Run /daily-user-feedback" >> /var/log/daily-feedback.log 2>&1
```

### Log rotation:
```bash
# /etc/logrotate.d/daily-feedback
/var/log/daily-feedback.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
}
```

## Monitoring

### Check cron is running:
```bash
tail -f /var/log/daily-feedback.log
```

### Verify tickets are created:
```bash
grep "Linear ticket created" /var/log/daily-feedback.log | tail -10
```

## Troubleshooting

### "No Linear ticket created - insufficient data"
- **Expected:** Some days have <3 feedback items (normal)
- **Action:** None needed - wait for more data

### "Database connection failed"
- **Cause:** arsenal/.env credentials expired or network issue
- **Action:** Check `arsenal/.env` has valid production credentials

### "linear-manager: Team not found"
- **Cause:** Team ID changed or not cached
- **Action:** Run linear-manager skill manually to refresh team ID

### Cron job not running
- **Check cron daemon:** `sudo service cron status`
- **Check cron logs:** `grep CRON /var/log/syslog`
- **Verify path:** Use absolute paths in crontab

## Notes

- **Fully automated:** No user interaction required (designed for cron)
- **Smart thresholding:** Won't create tickets for <3 items (noise filtering)
- **Agent handles PM work:** feature-opportunity-creator prioritizes and creates specs
- **Logs everything:** Output suitable for cron log files
- **Graceful failures:** Reports issues, doesn't crash cron
- **Idempotent:** Safe to run multiple times per day

---

Remember: This command is designed for **unattended automation**. The agent runs autonomously to create tickets.
