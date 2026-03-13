#!/usr/bin/env bash
set -euo pipefail

# List all teams in the Linear workspace

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment from arsenal/.env
if [ -f "$SCRIPT_DIR/../../../../.env" ]; then
    set -a
    source "$SCRIPT_DIR/../../../../.env"
    set +a
fi

# Call Python wrapper
python3 "$SCRIPT_DIR/linear_api.py" get-teams
