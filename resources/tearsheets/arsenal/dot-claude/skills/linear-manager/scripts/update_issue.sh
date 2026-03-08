#!/usr/bin/env bash
set -euo pipefail

# Update an existing Linear issue

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment from arsenal/.env
if [ -f "$SCRIPT_DIR/../../../../.env" ]; then
    set -a
    source "$SCRIPT_DIR/../../../../.env"
    set +a
fi

# Parse arguments
ISSUE_ID=""
TITLE=""
DESCRIPTION=""
PRIORITY=""
STATUS=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --issue-id)
      ISSUE_ID="$2"
      shift 2
      ;;
    --title)
      TITLE="$2"
      shift 2
      ;;
    --description)
      DESCRIPTION="$2"
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
    *)
      echo "Unknown parameter: $1"
      echo "Usage: $0 --issue-id 'ENG-123' [options]"
      echo "Options:"
      echo "  --title 'New title'"
      echo "  --description 'New description'"
      echo "  --priority urgent|high|medium|low"
      echo "  --status backlog|todo|in_progress|done"
      exit 1
      ;;
  esac
done

# Validate required arguments
if [ -z "$ISSUE_ID" ]; then
    echo "❌ Error: --issue-id is required"
    exit 1
fi

# Build command arguments
CMD_ARGS=(
    "update-issue"
    "--issue-id" "$ISSUE_ID"
)

if [ -n "$TITLE" ]; then
    CMD_ARGS+=("--title" "$TITLE")
fi

if [ -n "$DESCRIPTION" ]; then
    CMD_ARGS+=("--description" "$DESCRIPTION")
fi

if [ -n "$PRIORITY" ]; then
    CMD_ARGS+=("--priority" "$PRIORITY")
fi

if [ -n "$STATUS" ]; then
    CMD_ARGS+=("--status" "$STATUS")
fi

# Call Python wrapper
python3 "$SCRIPT_DIR/linear_api.py" "${CMD_ARGS[@]}"
