#!/usr/bin/env bash
set -euo pipefail

# Get issue details by identifier (e.g., "ENG-123")

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment from arsenal/.env
if [ -f "$SCRIPT_DIR/../../../../.env" ]; then
    set -a
    source "$SCRIPT_DIR/../../../../.env"
    set +a
fi

# Check for issue identifier argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <issue-identifier>"
    echo "Example: $0 ENG-123"
    exit 1
fi

ISSUE_ID="$1"

# Call Python wrapper
python3 "$SCRIPT_DIR/linear_api.py" get-issue "$ISSUE_ID"
