#!/usr/bin/env bash
set -euo pipefail

# Get issues assigned to the current user

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment from arsenal/.env
if [ -f "$SCRIPT_DIR/../../../../.env" ]; then
    set -a
    source "$SCRIPT_DIR/../../../../.env"
    set +a
fi

# Parse arguments
STATUS=""
INCLUDE_ARCHIVED=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --status)
      STATUS="$2"
      shift 2
      ;;
    --include-archived)
      INCLUDE_ARCHIVED="--include-archived"
      shift
      ;;
    *)
      echo "Unknown parameter: $1"
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --status 'in_progress'"
      echo "  --include-archived"
      exit 1
      ;;
  esac
done

# Build command arguments
CMD_ARGS=("get-user-issues")

if [ -n "$STATUS" ]; then
    CMD_ARGS+=("--status" "$STATUS")
fi

if [ -n "$INCLUDE_ARCHIVED" ]; then
    CMD_ARGS+=("$INCLUDE_ARCHIVED")
fi

# Call Python wrapper
python3 "$SCRIPT_DIR/linear_api.py" "${CMD_ARGS[@]}"
