#!/bin/bash
# SQL Reader - Connect to production database with read-only credentials

set -e

# Determine the script directory and arsenal location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Try to find arsenal/.env
# First try: script is in arsenal/dot-claude/skills/sql-reader/
ENV_FILE="$SCRIPT_DIR/../../../.env"

# Second try: script was copied to .claude/skills/sql-reader/
if [ ! -f "$ENV_FILE" ]; then
    ENV_FILE="$SCRIPT_DIR/../../../../arsenal/.env"
fi

# Third try: look for arsenal in parent directories
if [ ! -f "$ENV_FILE" ]; then
    CURRENT="$SCRIPT_DIR"
    while [ "$CURRENT" != "/" ]; do
        if [ -f "$CURRENT/arsenal/.env" ]; then
            ENV_FILE="$CURRENT/arsenal/.env"
            break
        fi
        CURRENT="$(dirname "$CURRENT")"
    done
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Could not find arsenal/.env"
    echo "Searched locations:"
    echo "  - $SCRIPT_DIR/../../../.env"
    echo "  - $SCRIPT_DIR/../../../../arsenal/.env"
    echo "  - Parent directories for arsenal/.env"
    echo ""
    echo "Please ensure arsenal/.env exists with database credentials:"
    echo "  PGHOST=your-database-host"
    echo "  PGPORT=5432"
    echo "  PGDATABASE=your_database"
    echo "  PGUSER=readonly_user"
    echo "  PGPASSWORD=your_password"
    echo "  PGSSLMODE=require"
    exit 1
fi

echo "Loading database credentials from arsenal/.env..."

# Source the .env file to load PG* variables
set -a  # automatically export all variables
source "$ENV_FILE"
set +a

# Verify required variables are set
if [ -z "$PGHOST" ] || [ -z "$PGUSER" ] || [ -z "$PGDATABASE" ]; then
    echo "Error: Missing required database credentials in arsenal/.env"
    echo "Required variables: PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD, PGSSLMODE"
    exit 1
fi

echo "✓ Connecting to: $PGHOST:$PGPORT/$PGDATABASE as $PGUSER"
echo ""

# Run query if provided as argument, otherwise open interactive session
if [ $# -eq 0 ]; then
    echo "Opening interactive psql session (read-only)..."
    echo "Tip: Use \? for help, \dt to list tables, \d tablename to describe a table"
    echo ""
    psql
else
    # Run the query passed as argument
    psql -c "$1"
fi
