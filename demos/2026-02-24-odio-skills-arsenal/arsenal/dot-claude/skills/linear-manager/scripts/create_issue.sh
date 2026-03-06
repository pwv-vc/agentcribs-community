#!/usr/bin/env bash
set -euo pipefail

# Create a new Linear issue

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment from arsenal/.env
if [ -f "$SCRIPT_DIR/../../../../.env" ]; then
    set -a
    source "$SCRIPT_DIR/../../../../.env"
    set +a
fi

# Parse arguments
TITLE=""
DESCRIPTION=""
TEAM_ID="${LINEAR_TEAM_ID:-}"
PRIORITY=""
STATUS=""
ASSIGNEE_ID=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --title)
      TITLE="$2"
      shift 2
      ;;
    --description)
      DESCRIPTION="$2"
      shift 2
      ;;
    --team-id)
      TEAM_ID="$2"
      shift 2
      ;;
    --priority)
      PRIORITY="$2"
      shift 2
      ;;
    --status)
      STATUS="$2"
      shift 2
      ;;
    --assignee-id)
      ASSIGNEE_ID="$2"
      shift 2
      ;;
    *)
      echo "Unknown parameter: $1"
      echo "Usage: $0 --title 'Issue title' --team-id 'team-uuid' [options]"
      echo "Options:"
      echo "  --description 'Description text'"
      echo "  --priority urgent|high|medium|low"
      echo "  --status backlog|todo|in_progress|done"
      echo "  --assignee-id 'user-uuid'"
      exit 1
      ;;
  esac
done

# Validate required arguments
if [ -z "$TITLE" ]; then
    echo "❌ Error: --title is required"
    exit 1
fi

if [ -z "$TEAM_ID" ]; then
    echo "❌ Error: --team-id is required (or set LINEAR_TEAM_ID in arsenal/.env)"
    echo "Run: .claude/skills/linear-manager/scripts/get_teams.sh"
    exit 1
fi

# Build command arguments
CMD_ARGS=(
    "create-issue"
    "--title" "$TITLE"
    "--team-id" "$TEAM_ID"
)

if [ -n "$DESCRIPTION" ]; then
    CMD_ARGS+=("--description" "$DESCRIPTION")
fi

if [ -n "$PRIORITY" ]; then
    CMD_ARGS+=("--priority" "$PRIORITY")
fi

if [ -n "$STATUS" ]; then
    CMD_ARGS+=("--status" "$STATUS")
fi

if [ -n "$ASSIGNEE_ID" ]; then
    CMD_ARGS+=("--assignee-id" "$ASSIGNEE_ID")
fi

# Call Python wrapper
python3 "$SCRIPT_DIR/linear_api.py" "${CMD_ARGS[@]}"
