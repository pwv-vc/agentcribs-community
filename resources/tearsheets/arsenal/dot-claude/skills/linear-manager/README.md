# Linear Manager Skill

Direct Linear API integration for Claude Code - create, update, search, and manage Linear issues without an MCP server.

## Quick Start

1. **Get Linear API key**: https://linear.app/settings/api

2. **Add to arsenal/.env**:
   ```bash
   echo "LINEAR_API_KEY=lin_api_your_key_here" >> arsenal/.env
   ```

3. **Install dependencies**:
   ```bash
   cd .claude/skills/linear-manager
   pip install -r requirements.txt
   ```

4. **Get your team ID**:
   ```bash
   .claude/skills/linear-manager/scripts/get_teams.sh
   ```

5. **Create your first issue**:
   ```bash
   .claude/skills/linear-manager/scripts/create_issue.sh \
     --title "Test issue from Claude Code" \
     --team-id "your-team-uuid" \
     --description "Testing the linear-manager skill"
   ```

## Architecture

This skill uses **direct GraphQL API calls** instead of the MCP protocol:

- **Python wrapper** (`scripts/linear_api.py`) handles GraphQL queries/mutations
- **Bash helper scripts** provide user-friendly CLI interface
- **Environment variables** from `arsenal/.env` for authentication
- **No server process** required - just direct HTTPS requests

## Commands

See `SKILL.md` for full documentation and usage examples.

### Core Commands

```bash
# Get issue details
.claude/skills/linear-manager/scripts/get_issue.sh ENG-123

# Create issue
.claude/skills/linear-manager/scripts/create_issue.sh \
  --title "Your title" \
  --team-id "team-uuid"

# Search issues
.claude/skills/linear-manager/scripts/search_issues.sh --query "bug"

# Update issue
.claude/skills/linear-manager/scripts/update_issue.sh \
  --issue-id "ENG-123" \
  --status "done"

# Add comment
.claude/skills/linear-manager/scripts/add_comment.sh \
  --issue-id "ENG-123" \
  --body "Comment text"

# Get my issues
.claude/skills/linear-manager/scripts/get_user_issues.sh

# List teams
.claude/skills/linear-manager/scripts/get_teams.sh
```

## Integration with Arsenal Commands

This skill makes the following arsenal commands functional:

- `/create-linear-ticket` - Now can actually create Linear issues
- `/linear-agent` - Can fetch and work on Linear issues

The skill provides the backend implementation that the arsenal commands expect.

## Development

### Testing

```bash
# Verify API key is set
grep LINEAR_API_KEY arsenal/.env

# Test team listing
.claude/skills/linear-manager/scripts/get_teams.sh

# Test creating an issue (safe - creates real issue)
.claude/skills/linear-manager/scripts/create_issue.sh \
  --title "Test from skill" \
  --team-id "your-team-uuid"
```

### Debugging

```bash
# Run Python wrapper directly for more detailed errors
cd .claude/skills/linear-manager/scripts
python3 linear_api.py get-teams

# Check environment variables
set -a && source ../../../arsenal/.env && set +a
echo $LINEAR_API_KEY
```

## Comparison to MCP Server

| Feature | This Skill | Linear MCP Server |
|---------|-----------|-------------------|
| Installation | `pip install requests` | MCP server + config |
| Authentication | Env var in arsenal/.env | Env var in Claude config |
| Invocation | Direct bash scripts | MCP protocol |
| Debugging | Standard Python/bash | MCP protocol layer |
| Maintenance | Update Python scripts | Update MCP server |
| Portability | Works anywhere | Claude Code only |

## Future Enhancements

Potential additions:

- [ ] State/status management (requires state ID lookups)
- [ ] Label management
- [ ] Project assignment
- [ ] Attachment upload
- [ ] Bulk operations
- [ ] Issue templates
- [ ] Webhook integration

## License

Part of the arsenal skill collection. Same license as parent repository.
