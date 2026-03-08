#!/usr/bin/env bash
set -euo pipefail

# Add a comment to a Linear issue

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment from arsenal/.env
if [ -f "$SCRIPT_DIR/../../../../.env" ]; then
    set -a
    source "$SCRIPT_DIR/../../../../.env"
    set +a
fi

# Parse arguments
ISSUE_ID=""
BODY=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --issue-id)
      ISSUE_ID="$2"
      shift 2
      ;;
    --body)
      BODY="$2"
      shift 2
      ;;
    *)
      echo "Unknown parameter: $1"
      echo "Usage: $0 --issue-id 'ENG-123' --body 'Comment text'"
      exit 1
      ;;
  esac
done

# Validate required arguments
if [ -z "$ISSUE_ID" ]; then
    echo "❌ Error: --issue-id is required"
    exit 1
fi

if [ -z "$BODY" ]; then
    echo "❌ Error: --body is required"
    exit 1
fi

# Call Python wrapper
python3 "$SCRIPT_DIR/linear_api.py" add-comment \
    --issue-id "$ISSUE_ID" \
    --body "$BODY"
