#!/usr/bin/env bash
set -euo pipefail

# Search for Linear issues

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment from arsenal/.env
if [ -f "$SCRIPT_DIR/../../../../.env" ]; then
    set -a
    source "$SCRIPT_DIR/../../../../.env"
    set +a
fi

# Parse arguments
QUERY=""
TEAM_ID=""
ASSIGNEE_ID=""
LIMIT="10"

while [[ $# -gt 0 ]]; do
  case $1 in
    --query)
      QUERY="$2"
      shift 2
      ;;
    --team-id)
      TEAM_ID="$2"
      shift 2
      ;;
    --assignee-id)
      ASSIGNEE_ID="$2"
      shift 2
      ;;
    --limit)
      LIMIT="$2"
      shift 2
      ;;
    *)
      echo "Unknown parameter: $1"
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --query 'search text'"
      echo "  --team-id 'team-uuid'"
      echo "  --assignee-id 'user-uuid'"
      echo "  --limit 10"
      exit 1
      ;;
  esac
done

# Build command arguments
CMD_ARGS=(
    "search-issues"
    "--limit" "$LIMIT"
)

if [ -n "$QUERY" ]; then
    CMD_ARGS+=("--query" "$QUERY")
fi

if [ -n "$TEAM_ID" ]; then
    CMD_ARGS+=("--team-id" "$TEAM_ID")
fi

if [ -n "$ASSIGNEE_ID" ]; then
    CMD_ARGS+=("--assignee-id" "$ASSIGNEE_ID")
fi

# Call Python wrapper
python3 "$SCRIPT_DIR/linear_api.py" "${CMD_ARGS[@]}"
