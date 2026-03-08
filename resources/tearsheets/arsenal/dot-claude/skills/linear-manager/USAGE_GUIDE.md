# Linear Manager Skill - Quick Setup & Usage Guide

## Installation (5 minutes)

### Step 1: Get Your Linear API Key

1. Go to https://linear.app/settings/api
2. Click "Create new API key"
3. Give it a name (e.g., "Claude Code")
4. Copy the key (starts with `lin_api_`)

### Step 2: Configure Environment

```bash
# Add your Linear API key to arsenal/.env
echo "LINEAR_API_KEY=lin_api_paste_your_key_here" >> arsenal/.env

# Verify it was added
grep LINEAR_API_KEY arsenal/.env
```

### Step 3: Install Dependencies

```bash
# Option 1: System Python
pip install requests

# Option 2: Python venv
python3 -m pip install requests

# Verify installation
python3 -c "import requests; print('✅ requests installed')"
```

### Step 4: Test the Installation

```bash
# This should list all teams in your Linear workspace
.claude/skills/linear-manager/scripts/get_teams.sh
```

**Expected output:**
```
📋 Teams in workspace (X total)

Engineering (ENG)
  ID: a1b2c3d4-uuid-here

Product (PROD)
  ID: e5f6g7h8-uuid-here
```

### Step 5: Set Default Team (Optional)

```bash
# Copy the team ID from the output above
echo "LINEAR_TEAM_ID=a1b2c3d4-uuid-here" >> arsenal/.env
```

## Common Usage Patterns

### Pattern 1: Creating an Issue from a Bug Discovery

```bash
# Scenario: You found a bug while coding
.claude/skills/linear-manager/scripts/create_issue.sh \
  --title "Fix Redis timeout in worker process" \
  --description "Workers fail to reconnect after Redis restarts" \
  --team-id "your-team-uuid" \
  --priority "urgent"

# Output:
# ✅ Created issue ENG-789: Fix Redis timeout in worker process
# 🔗 https://linear.app/team/issue/ENG-789
```

### Pattern 2: Working on a Linear Ticket

```bash
# Fetch issue details to understand what to work on
.claude/skills/linear-manager/scripts/get_issue.sh ENG-456

# Output shows:
# - Title and description
# - Current status
# - Priority
# - Assignee
# - Comments
# - URL to view in Linear

# Update status to "in_progress" when you start
.claude/skills/linear-manager/scripts/update_issue.sh \
  --issue-id "ENG-456" \
  --status "in_progress"
```

### Pattern 3: Checking Your Assigned Work

```bash
# See all your assigned issues
.claude/skills/linear-manager/scripts/get_user_issues.sh

# Filter by status
.claude/skills/linear-manager/scripts/get_user_issues.sh --status "in_progress"

# Output:
# 📋 Your Name's issues (3 total)
#
# ENG-123: Implement user authentication
#   Status: In Progress | Priority: High
#   🔗 https://linear.app/...
```

### Pattern 4: Searching for Related Issues

```bash
# Search by keyword
.claude/skills/linear-manager/scripts/search_issues.sh --query "authentication"

# Search within a specific team
.claude/skills/linear-manager/scripts/search_issues.sh \
  --team-id "your-team-uuid" \
  --query "bug"
```

### Pattern 5: Completing Work

```bash
# Add a comment with implementation details
.claude/skills/linear-manager/scripts/add_comment.sh \
  --issue-id "ENG-456" \
  --body "Implementation complete. Tests passing. PR #123 ready for review."

# Update status to done
.claude/skills/linear-manager/scripts/update_issue.sh \
  --issue-id "ENG-456" \
  --status "done"
```

## Integration with Claude Code Workflow

When using Claude Code, announce you're using the skill:

```
User: "Create a Linear issue for this authentication bug"

You: "I'm using the linear-manager skill to create a Linear issue...

First, let me verify your team:
.claude/skills/linear-manager/scripts/get_teams.sh

Creating issue:
.claude/skills/linear-manager/scripts/create_issue.sh \
  --title "Fix OAuth authentication timeout" \
  --description "Users report timeout after 30s during OAuth flow" \
  --team-id "abc123" \
  --priority "urgent"

✅ Created issue ENG-789: https://linear.app/team/issue/ENG-789"
```

## Troubleshooting

### "LINEAR_API_KEY not set"

```bash
# Check if key exists
grep LINEAR_API_KEY arsenal/.env

# If not found, add it
echo "LINEAR_API_KEY=your-key-here" >> arsenal/.env
```

### "requests library not installed"

```bash
# Install it
pip install requests

# Or with python3
python3 -m pip install requests
```

### "Team ID required"

```bash
# Get team IDs
.claude/skills/linear-manager/scripts/get_teams.sh

# Set default team (optional)
echo "LINEAR_TEAM_ID=your-team-uuid" >> arsenal/.env

# Or provide --team-id flag each time
```

### "Issue not found"

- Check the issue ID format (e.g., "ENG-123", not "eng-123")
- Verify you have access to the issue's team
- Make sure the issue exists in Linear

### Permission Errors on Scripts

```bash
# Make scripts executable
chmod +x .claude/skills/linear-manager/scripts/*.sh
```

## Command Reference

```bash
# Get issue details
.claude/skills/linear-manager/scripts/get_issue.sh <issue-id>

# Create issue
.claude/skills/linear-manager/scripts/create_issue.sh \
  --title "Title" \
  --team-id "uuid" \
  [--description "..."] \
  [--priority urgent|high|medium|low] \
  [--assignee-id "uuid"]

# Update issue
.claude/skills/linear-manager/scripts/update_issue.sh \
  --issue-id "ENG-123" \
  [--title "New title"] \
  [--description "..."] \
  [--priority urgent|high|medium|low] \
  [--status backlog|todo|in_progress|done]

# Search issues
.claude/skills/linear-manager/scripts/search_issues.sh \
  [--query "search text"] \
  [--team-id "uuid"] \
  [--assignee-id "uuid"] \
  [--limit 10]

# Add comment
.claude/skills/linear-manager/scripts/add_comment.sh \
  --issue-id "ENG-123" \
  --body "Comment text"

# Get user's issues
.claude/skills/linear-manager/scripts/get_user_issues.sh \
  [--status "in_progress"] \
  [--include-archived]

# List teams
.claude/skills/linear-manager/scripts/get_teams.sh
```

## Tips

1. **Always start with get_teams.sh** to find your team IDs
2. **Set LINEAR_TEAM_ID** in arsenal/.env to avoid typing team ID every time
3. **Use issue identifiers** (e.g., "ENG-123") instead of UUIDs when possible
4. **Include priority** when creating issues for better triage
5. **Add comments** during development to track progress
6. **Update status** to keep the team informed

## What's Next?

- Read `SKILL.md` for detailed documentation
- Check `README.md` for architecture details
- Look at `scripts/linear_api.py` for implementation details
- Integrate with arsenal commands like `/create-linear-ticket`

## Getting Help

If you encounter issues:

1. Verify API key is correct: https://linear.app/settings/api
2. Check Python and requests are installed
3. Test with get_teams.sh first (simplest command)
4. Review error messages - they include troubleshooting hints
5. Check Linear's API documentation: https://developers.linear.app
