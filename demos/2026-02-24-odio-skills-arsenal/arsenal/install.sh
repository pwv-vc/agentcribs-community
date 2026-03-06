#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Non-interactive mode (for Docker builds, CI, etc.)
# Usage: ./install.sh --non-interactive or ./install.sh -y
NONINTERACTIVE=false
for arg in "$@"; do
    case $arg in
        -y|--yes|--non-interactive)
            NONINTERACTIVE=true
            shift
            ;;
    esac
done

if [[ "$NONINTERACTIVE" == "true" ]]; then
    echo -e "${YELLOW}Running in non-interactive mode (skipping all prompts)${NC}"
fi

# Cross-platform sed in-place function (macOS requires -i '', Linux requires -i)
sed_inplace() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "$@"
    else
        sed -i "$@"
    fi
}

echo -e "${GREEN}Installing/Updating Arsenal...${NC}\n"

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUPERPOWERS_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Arsenal directory: $SUPERPOWERS_DIR"
echo "Project root directory: $PROJECT_ROOT"
echo ""

# 1. Copy .claude directory to project root (Claude Code expects it there)
# Note: We copy instead of symlink because Claude Code doesn't reliably respect symlinked directories
echo -e "${YELLOW}Step 1: Setting up .claude directory...${NC}"
CLAUDE_DIR="$PROJECT_ROOT/.claude"
SOURCE_CLAUDE="$SUPERPOWERS_DIR/dot-claude"

if [ -L "$CLAUDE_DIR" ]; then
    echo "  ! Removing old .claude symlink (switching to copy for reliability)"
    rm "$CLAUDE_DIR"
    cp -r "$SOURCE_CLAUDE" "$CLAUDE_DIR"
    echo -e "${GREEN}  ✓ Converted .claude from symlink to copy${NC}"
elif [ -d "$CLAUDE_DIR" ]; then
    echo "  Updating existing .claude directory from arsenal..."
    # Use rsync to sync, preserving newer files in destination if any
    rsync -a --update "$SOURCE_CLAUDE/" "$CLAUDE_DIR/"
    echo -e "${GREEN}  ✓ Updated .claude directory${NC}"
else
    cp -r "$SOURCE_CLAUDE" "$CLAUDE_DIR"
    echo -e "${GREEN}  ✓ Created .claude directory${NC}"
fi

# Make hook scripts executable
chmod +x "$CLAUDE_DIR/hooks/"*.py 2>/dev/null || true

# 2. Copy AGENTS.md files
# Note: We copy instead of symlink because Claude Code doesn't reliably respect symlinks
echo -e "\n${YELLOW}Step 2: Copying AGENTS.md files...${NC}"

# Root AGENTS.md
ROOT_AGENTS="$PROJECT_ROOT/AGENTS.md"
SOURCE_ROOT_AGENTS="$SUPERPOWERS_DIR/system-prompts/AGENTS.md"
if [ -L "$ROOT_AGENTS" ]; then
    echo "  ! Removing old AGENTS.md symlink (switching to copy for reliability)"
    rm "$ROOT_AGENTS"
    cp "$SOURCE_ROOT_AGENTS" "$ROOT_AGENTS"
    echo -e "${GREEN}  ✓ Converted root AGENTS.md from symlink to copy${NC}"
elif [ -f "$ROOT_AGENTS" ]; then
    # Backup existing file if it differs from source
    if ! cmp -s "$ROOT_AGENTS" "$SOURCE_ROOT_AGENTS"; then
        BACKUP_FILE="$ROOT_AGENTS.backup-$(date +%Y%m%d-%H%M%S)"
        cp "$ROOT_AGENTS" "$BACKUP_FILE"
        echo -e "${YELLOW}  ! Created backup: $BACKUP_FILE${NC}"
    fi
    echo "  Updating existing AGENTS.md from arsenal..."
    cp "$SOURCE_ROOT_AGENTS" "$ROOT_AGENTS"
    echo -e "${GREEN}  ✓ Updated root AGENTS.md${NC}"
else
    cp "$SOURCE_ROOT_AGENTS" "$ROOT_AGENTS"
    echo -e "${GREEN}  ✓ Created root AGENTS.md${NC}"
fi

# Testing AGENTS.md
TESTING_AGENTS="$PROJECT_ROOT/api/tests/AGENTS.md"
SOURCE_TESTING_AGENTS="$SUPERPOWERS_DIR/system-prompts/testing/AGENTS.md"
if [ -L "$TESTING_AGENTS" ]; then
    echo "  ! Removing old testing AGENTS.md symlink (switching to copy for reliability)"
    rm "$TESTING_AGENTS"
    cp "$SOURCE_TESTING_AGENTS" "$TESTING_AGENTS"
    echo -e "${GREEN}  ✓ Converted testing AGENTS.md from symlink to copy${NC}"
elif [ -f "$TESTING_AGENTS" ]; then
    # Backup existing file if it differs from source
    if ! cmp -s "$TESTING_AGENTS" "$SOURCE_TESTING_AGENTS"; then
        BACKUP_FILE="$TESTING_AGENTS.backup-$(date +%Y%m%d-%H%M%S)"
        cp "$TESTING_AGENTS" "$BACKUP_FILE"
        echo -e "${YELLOW}  ! Created backup: $BACKUP_FILE${NC}"
    fi
    echo "  Updating existing testing AGENTS.md from arsenal..."
    cp "$SOURCE_TESTING_AGENTS" "$TESTING_AGENTS"
    echo -e "${GREEN}  ✓ Updated testing AGENTS.md${NC}"
else
    cp "$SOURCE_TESTING_AGENTS" "$TESTING_AGENTS"
    echo -e "${GREEN}  ✓ Created testing AGENTS.md${NC}"
fi

# 3. Link pre-commit scripts
echo -e "\n${YELLOW}Step 3: Linking pre-commit scripts...${NC}"
PRE_COMMIT_LINK="$PROJECT_ROOT/.pre-commit-scripts"

if [ -d "$PRE_COMMIT_LINK" ] && [ ! -L "$PRE_COMMIT_LINK" ]; then
    echo -e "${RED}  ✗ .pre-commit-scripts exists as a directory (not a symlink)${NC}"
    echo "    Move it first: mv $PRE_COMMIT_LINK ${PRE_COMMIT_LINK}.backup"
    exit 1
fi

# Remove existing symlink if present, then create relative symlink
[ -L "$PRE_COMMIT_LINK" ] && rm "$PRE_COMMIT_LINK"
ln -s "arsenal/pre-commit-scripts" "$PRE_COMMIT_LINK"
echo -e "${GREEN}  ✓ Created .pre-commit-scripts symlink${NC}"

# 4. Install Node dependencies for skills
echo -e "\n${YELLOW}Step 4: Installing Node dependencies for skills...${NC}"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo -e "${YELLOW}  ! npm not found - skipping skill dependency installation${NC}"
    echo "    Skills requiring Node.js will need manual 'npm install' in their directories"
else
    # Find all package.json files in skills directories (excluding node_modules)
    SKILL_DIRS=$(find "$SUPERPOWERS_DIR/dot-claude/skills" -path "*/node_modules" -prune -o -name "package.json" -type f -print | xargs -n1 dirname)

    if [ -z "$SKILL_DIRS" ]; then
        echo "  ✓ No Node.js skills require installation"
    else
        for SKILL_DIR in $SKILL_DIRS; do
            SKILL_NAME=$(basename "$SKILL_DIR")

            # Check if node_modules already exists and is not empty
            if [ -d "$SKILL_DIR/node_modules" ] && [ "$(ls -A "$SKILL_DIR/node_modules" 2>/dev/null)" ]; then
                echo -e "${GREEN}  ✓ $SKILL_NAME dependencies already installed${NC}"
            else
                echo "  Installing dependencies for skill: $SKILL_NAME"
                # Install dependencies quietly
                (cd "$SKILL_DIR" && npm install --silent) && \
                    echo -e "${GREEN}    ✓ Installed $SKILL_NAME dependencies${NC}" || \
                    echo -e "${RED}    ✗ Failed to install $SKILL_NAME dependencies${NC}"
            fi
        done
    fi
fi

# 5. Setup arsenal environment configuration
echo -e "\n${YELLOW}Step 5: Setting up arsenal environment configuration...${NC}"

SUPERPOWERS_ENV="$SUPERPOWERS_DIR/.env"
SUPERPOWERS_ENV_EXAMPLE="$SUPERPOWERS_DIR/.env.example"

if [ -f "$SUPERPOWERS_ENV" ]; then
    echo -e "${GREEN}  ✓ .env file already exists${NC}"

    # Check for keys in parent project (.env or api/.env)
    PARENT_API_KEY=""
    PARENT_LANGFUSE_PUBLIC_KEY=""
    PARENT_LANGFUSE_SECRET_KEY=""
    PARENT_LANGFUSE_HOST=""

    # Check api/.env first, then .env
    for parent_env in "$PROJECT_ROOT/api/.env" "$PROJECT_ROOT/.env"; do
        if [ -f "$parent_env" ]; then
            if [ -z "$PARENT_API_KEY" ]; then
                PARENT_API_KEY=$(grep "^OPENAI_API_KEY=" "$parent_env" | head -1 | cut -d'=' -f2 | tr -d ' ')
            fi
            if [ -z "$PARENT_LANGFUSE_PUBLIC_KEY" ]; then
                PARENT_LANGFUSE_PUBLIC_KEY=$(grep "^LANGFUSE_PUBLIC_KEY=" "$parent_env" | head -1 | cut -d'=' -f2 | tr -d ' ')
            fi
            if [ -z "$PARENT_LANGFUSE_SECRET_KEY" ]; then
                PARENT_LANGFUSE_SECRET_KEY=$(grep "^LANGFUSE_SECRET_KEY=" "$parent_env" | head -1 | cut -d'=' -f2 | tr -d ' ')
            fi
            if [ -z "$PARENT_LANGFUSE_HOST" ]; then
                PARENT_LANGFUSE_HOST=$(grep "^LANGFUSE_HOST=" "$parent_env" | head -1 | cut -d'=' -f2 | tr -d ' ')
            fi
        fi
    done

    # Check and offer to update OPENAI_API_KEY
    # Exclude placeholder values like "sk-proj-your-key-here"
    if grep -q "^OPENAI_API_KEY=sk-" "$SUPERPOWERS_ENV" && \
       ! grep -q "^OPENAI_API_KEY=sk-proj-your-key-here" "$SUPERPOWERS_ENV"; then
        echo "  ✓ OPENAI_API_KEY configured"
    else
        if [ -n "$PARENT_API_KEY" ]; then
            echo -e "${YELLOW}  ! OPENAI_API_KEY not configured${NC}"
            if [[ "$NONINTERACTIVE" == "true" ]]; then
                REPLY="n"
            else
                read -p "  Copy OPENAI_API_KEY from parent project? [y/N]: " -n 1 -r
                echo
            fi
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                sed_inplace "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$PARENT_API_KEY|" "$SUPERPOWERS_ENV"
                echo -e "${GREEN}    ✓ Copied OPENAI_API_KEY${NC}"
            fi
        else
            echo -e "${YELLOW}  ! OPENAI_API_KEY not configured - edit arsenal/.env to add it${NC}"
        fi
    fi

    # Check and offer to update LANGFUSE keys
    # Check if both staging and production credentials are configured
    HAS_STAGING=$(grep -q "^LANGFUSE_PUBLIC_KEY_STAGING=pk-lf-" "$SUPERPOWERS_ENV" && \
                  ! grep -q "^LANGFUSE_PUBLIC_KEY_STAGING=pk-lf-your-public-key-here" "$SUPERPOWERS_ENV" && echo "yes" || echo "no")
    HAS_PROD=$(grep -q "^LANGFUSE_PUBLIC_KEY_PROD=pk-lf-" "$SUPERPOWERS_ENV" && \
               ! grep -q "^LANGFUSE_PUBLIC_KEY_PROD=pk-lf-your-prod-public-key" "$SUPERPOWERS_ENV" && echo "yes" || echo "no")

    if [ "$HAS_STAGING" == "yes" ] && [ "$HAS_PROD" == "yes" ]; then
        echo "  ✓ LANGFUSE credentials configured (both staging and production)"
    elif [ "$HAS_STAGING" == "yes" ]; then
        echo "  ✓ LANGFUSE staging credentials configured"
        echo -e "${YELLOW}  ! LANGFUSE production credentials not configured${NC}"
    elif [ "$HAS_PROD" == "yes" ]; then
        echo "  ✓ LANGFUSE production credentials configured"
        echo -e "${YELLOW}  ! LANGFUSE staging credentials not configured${NC}"
    else
        # Neither staging nor production configured - offer to copy from parent
        if [ -n "$PARENT_LANGFUSE_PUBLIC_KEY" ] && [ -n "$PARENT_LANGFUSE_SECRET_KEY" ]; then
            echo -e "${YELLOW}  ! LANGFUSE credentials not configured${NC}"
            echo ""
            echo "  Found Langfuse credentials in parent project:"
            echo "    Host: ${PARENT_LANGFUSE_HOST:-'not specified'}"
            echo "    Public Key: ${PARENT_LANGFUSE_PUBLIC_KEY:0:15}..."
            echo "    Secret Key: ${PARENT_LANGFUSE_SECRET_KEY:0:15}..."
            echo ""
            if [[ "$NONINTERACTIVE" == "true" ]]; then
                REPLY="x"  # skip
            else
                read -p "  Are these STAGING or PRODUCTION credentials? [s/p/skip]: " -n 1 -r
                echo
            fi

            if [[ $REPLY =~ ^[Ss]$ ]]; then
                # Save as staging credentials
                sed_inplace "s|LANGFUSE_PUBLIC_KEY_STAGING=.*|LANGFUSE_PUBLIC_KEY_STAGING=$PARENT_LANGFUSE_PUBLIC_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
                sed_inplace "s|LANGFUSE_SECRET_KEY_STAGING=.*|LANGFUSE_SECRET_KEY_STAGING=$PARENT_LANGFUSE_SECRET_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
                if [ -n "$PARENT_LANGFUSE_HOST" ]; then
                    sed_inplace "s|LANGFUSE_HOST_STAGING=.*|LANGFUSE_HOST_STAGING=$PARENT_LANGFUSE_HOST|" "$SUPERPOWERS_ENV"
                fi
                # Also update legacy variables to point to staging
                sed_inplace "s|LANGFUSE_PUBLIC_KEY=.*|LANGFUSE_PUBLIC_KEY=$PARENT_LANGFUSE_PUBLIC_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
                sed_inplace "s|LANGFUSE_SECRET_KEY=.*|LANGFUSE_SECRET_KEY=$PARENT_LANGFUSE_SECRET_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
                if [ -n "$PARENT_LANGFUSE_HOST" ]; then
                    sed_inplace "s|LANGFUSE_HOST=.*|LANGFUSE_HOST=$PARENT_LANGFUSE_HOST|" "$SUPERPOWERS_ENV"
                fi
                sed_inplace "s|LANGFUSE_ENVIRONMENT=.*|LANGFUSE_ENVIRONMENT=staging|" "$SUPERPOWERS_ENV"
                echo -e "${GREEN}    ✓ Saved as STAGING credentials${NC}"
            elif [[ $REPLY =~ ^[Pp]$ ]]; then
                # Save as production credentials
                sed_inplace "s|LANGFUSE_PUBLIC_KEY_PROD=.*|LANGFUSE_PUBLIC_KEY_PROD=$PARENT_LANGFUSE_PUBLIC_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
                sed_inplace "s|LANGFUSE_SECRET_KEY_PROD=.*|LANGFUSE_SECRET_KEY_PROD=$PARENT_LANGFUSE_SECRET_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
                if [ -n "$PARENT_LANGFUSE_HOST" ]; then
                    sed_inplace "s|LANGFUSE_HOST_PROD=.*|LANGFUSE_HOST_PROD=$PARENT_LANGFUSE_HOST|" "$SUPERPOWERS_ENV"
                fi
                # Also update legacy variables to point to production
                sed_inplace "s|LANGFUSE_PUBLIC_KEY=.*|LANGFUSE_PUBLIC_KEY=$PARENT_LANGFUSE_PUBLIC_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
                sed_inplace "s|LANGFUSE_SECRET_KEY=.*|LANGFUSE_SECRET_KEY=$PARENT_LANGFUSE_SECRET_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
                if [ -n "$PARENT_LANGFUSE_HOST" ]; then
                    sed_inplace "s|LANGFUSE_HOST=.*|LANGFUSE_HOST=$PARENT_LANGFUSE_HOST|" "$SUPERPOWERS_ENV"
                fi
                sed_inplace "s|LANGFUSE_ENVIRONMENT=.*|LANGFUSE_ENVIRONMENT=production|" "$SUPERPOWERS_ENV"
                echo -e "${GREEN}    ✓ Saved as PRODUCTION credentials${NC}"
            else
                echo "  Skipped Langfuse credential configuration"
            fi
        else
            echo -e "${YELLOW}  ! LANGFUSE credentials not configured - edit arsenal/.env to add them if needed${NC}"
        fi
    fi
else
    echo "  Creating .env file from template..."
    cp "$SUPERPOWERS_ENV_EXAMPLE" "$SUPERPOWERS_ENV"
    echo -e "${GREEN}  ✓ Created .env file${NC}"

    # Check for keys in parent project (.env or api/.env)
    PARENT_API_KEY=""
    PARENT_LANGFUSE_PUBLIC_KEY=""
    PARENT_LANGFUSE_SECRET_KEY=""
    PARENT_LANGFUSE_HOST=""

    # Check api/.env first, then .env
    for parent_env in "$PROJECT_ROOT/api/.env" "$PROJECT_ROOT/.env"; do
        if [ -f "$parent_env" ]; then
            if [ -z "$PARENT_API_KEY" ]; then
                PARENT_API_KEY=$(grep "^OPENAI_API_KEY=" "$parent_env" | head -1 | cut -d'=' -f2 | tr -d ' ')
            fi
            if [ -z "$PARENT_LANGFUSE_PUBLIC_KEY" ]; then
                PARENT_LANGFUSE_PUBLIC_KEY=$(grep "^LANGFUSE_PUBLIC_KEY=" "$parent_env" | head -1 | cut -d'=' -f2 | tr -d ' ')
            fi
            if [ -z "$PARENT_LANGFUSE_SECRET_KEY" ]; then
                PARENT_LANGFUSE_SECRET_KEY=$(grep "^LANGFUSE_SECRET_KEY=" "$parent_env" | head -1 | cut -d'=' -f2 | tr -d ' ')
            fi
            if [ -z "$PARENT_LANGFUSE_HOST" ]; then
                PARENT_LANGFUSE_HOST=$(grep "^LANGFUSE_HOST=" "$parent_env" | head -1 | cut -d'=' -f2 | tr -d ' ')
            fi
        fi
    done

    # Offer to configure OpenAI API key
    if [ -n "$OPENAI_API_KEY" ]; then
        echo "  Using OPENAI_API_KEY from environment"
        sed_inplace "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$OPENAI_API_KEY|" "$SUPERPOWERS_ENV"
        echo -e "${GREEN}  ✓ Set OPENAI_API_KEY${NC}"
    elif [ -n "$PARENT_API_KEY" ]; then
        if [[ "$NONINTERACTIVE" == "true" ]]; then
            REPLY="n"
        else
            read -p "  Copy OPENAI_API_KEY from parent project? [y/N]: " -n 1 -r
            echo
        fi
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sed_inplace "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$PARENT_API_KEY|" "$SUPERPOWERS_ENV"
            echo -e "${GREEN}  ✓ Copied OPENAI_API_KEY${NC}"
        else
            echo -e "${YELLOW}  ! OPENAI_API_KEY not set - edit arsenal/.env to add it${NC}"
        fi
    else
        echo -e "${YELLOW}  ! OPENAI_API_KEY not found - edit arsenal/.env to add it${NC}"
    fi

    # Offer to configure Langfuse keys
    if [ -n "$PARENT_LANGFUSE_PUBLIC_KEY" ] && [ -n "$PARENT_LANGFUSE_SECRET_KEY" ]; then
        echo ""
        echo "  Found Langfuse credentials in parent project:"
        echo "    Host: ${PARENT_LANGFUSE_HOST:-'not specified'}"
        echo "    Public Key: ${PARENT_LANGFUSE_PUBLIC_KEY:0:15}..."
        echo "    Secret Key: ${PARENT_LANGFUSE_SECRET_KEY:0:15}..."
        echo ""
        if [[ "$NONINTERACTIVE" == "true" ]]; then
            REPLY="x"  # skip
        else
            read -p "  Are these STAGING or PRODUCTION credentials? [s/p/skip]: " -n 1 -r
            echo
        fi

        if [[ $REPLY =~ ^[Ss]$ ]]; then
            # Save as staging credentials
            sed_inplace "s|LANGFUSE_PUBLIC_KEY_STAGING=.*|LANGFUSE_PUBLIC_KEY_STAGING=$PARENT_LANGFUSE_PUBLIC_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
            sed_inplace "s|LANGFUSE_SECRET_KEY_STAGING=.*|LANGFUSE_SECRET_KEY_STAGING=$PARENT_LANGFUSE_SECRET_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
            if [ -n "$PARENT_LANGFUSE_HOST" ]; then
                sed_inplace "s|LANGFUSE_HOST_STAGING=.*|LANGFUSE_HOST_STAGING=$PARENT_LANGFUSE_HOST|" "$SUPERPOWERS_ENV"
            fi
            # Also update legacy variables to point to staging
            sed_inplace "s|LANGFUSE_PUBLIC_KEY=.*|LANGFUSE_PUBLIC_KEY=$PARENT_LANGFUSE_PUBLIC_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
            sed_inplace "s|LANGFUSE_SECRET_KEY=.*|LANGFUSE_SECRET_KEY=$PARENT_LANGFUSE_SECRET_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
            if [ -n "$PARENT_LANGFUSE_HOST" ]; then
                sed_inplace "s|LANGFUSE_HOST=.*|LANGFUSE_HOST=$PARENT_LANGFUSE_HOST|" "$SUPERPOWERS_ENV"
            fi
            sed_inplace "s|LANGFUSE_ENVIRONMENT=.*|LANGFUSE_ENVIRONMENT=staging|" "$SUPERPOWERS_ENV"
            echo -e "${GREEN}  ✓ Saved as STAGING credentials${NC}"
        elif [[ $REPLY =~ ^[Pp]$ ]]; then
            # Save as production credentials
            sed_inplace "s|LANGFUSE_PUBLIC_KEY_PROD=.*|LANGFUSE_PUBLIC_KEY_PROD=$PARENT_LANGFUSE_PUBLIC_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
            sed_inplace "s|LANGFUSE_SECRET_KEY_PROD=.*|LANGFUSE_SECRET_KEY_PROD=$PARENT_LANGFUSE_SECRET_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
            if [ -n "$PARENT_LANGFUSE_HOST" ]; then
                sed_inplace "s|LANGFUSE_HOST_PROD=.*|LANGFUSE_HOST_PROD=$PARENT_LANGFUSE_HOST|" "$SUPERPOWERS_ENV"
            fi
            # Also update legacy variables to point to production
            sed_inplace "s|LANGFUSE_PUBLIC_KEY=.*|LANGFUSE_PUBLIC_KEY=$PARENT_LANGFUSE_PUBLIC_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
            sed_inplace "s|LANGFUSE_SECRET_KEY=.*|LANGFUSE_SECRET_KEY=$PARENT_LANGFUSE_SECRET_KEY  # pragma: allowlist-secret|" "$SUPERPOWERS_ENV"
            if [ -n "$PARENT_LANGFUSE_HOST" ]; then
                sed_inplace "s|LANGFUSE_HOST=.*|LANGFUSE_HOST=$PARENT_LANGFUSE_HOST|" "$SUPERPOWERS_ENV"
            fi
            sed_inplace "s|LANGFUSE_ENVIRONMENT=.*|LANGFUSE_ENVIRONMENT=production|" "$SUPERPOWERS_ENV"
            echo -e "${GREEN}  ✓ Saved as PRODUCTION credentials${NC}"
        else
            echo "  Skipped Langfuse credential configuration"
        fi
    else
        echo -e "${YELLOW}  ! LANGFUSE keys not found - edit arsenal/.env to add them if needed${NC}"
    fi
fi

# 6. Setup semantic search skill
echo -e "\n${YELLOW}Step 6: Setting up semantic search skill...${NC}"

CODE_SEARCH_DIR="$SUPERPOWERS_DIR/dot-claude/skills/semantic-search"
if [ -d "$CODE_SEARCH_DIR" ]; then
    echo "  Found semantic-search skill"

    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}  ! Docker not found - skipping semantic search setup${NC}"
        echo "    To use semantic search later, install Docker and run:"
        echo "    cd arsenal && docker-compose up -d"
    else
        # Check if containers are already running
        if docker ps | grep -q arsenal-semantic-search-cli; then
            echo -e "${GREEN}  ✓ Semantic search containers already running${NC}"
        else
            # Check if OpenAI API key is configured
            if [ ! -f "$SUPERPOWERS_ENV" ] || ! grep -q "^OPENAI_API_KEY=sk-" "$SUPERPOWERS_ENV"; then
                echo -e "${YELLOW}  ! OPENAI_API_KEY not configured in $SUPERPOWERS_ENV${NC}"
                echo "    Edit arsenal/.env to add your key, then run:"
                echo "    cd arsenal && docker-compose up -d"
            else
                if [[ "$NONINTERACTIVE" == "true" ]]; then
                    REPLY="n"
                else
                    read -p "  Start semantic search containers? [y/N]: " -n 1 -r
                    echo
                fi
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    echo "  Starting semantic search containers..."
                    cd "$SUPERPOWERS_DIR"

                    # Start containers
                    docker-compose up -d --build 2>&1 | grep -v "Pulling" | grep -v "Waiting"

                    if [ $? -eq 0 ]; then
                        echo -e "${GREEN}    ✓ Started semantic search containers${NC}"

                        # Wait for postgres to be healthy
                        echo "    Waiting for database to be ready..."
                        for i in {1..30}; do
                            if docker exec arsenal-semantic-search-cli psql postgresql://codesearch:codesearch@semantic-search-db:5432/codesearch -c "SELECT 1" &> /dev/null; then
                                break
                            fi
                            sleep 1
                        done

                        # Index the project root
                        echo "    Indexing codebase (this may take a minute)..."
                        docker exec arsenal-semantic-search-cli code-search index /project --clear 2>&1 | tail -5

                        if [ $? -eq 0 ]; then
                            echo -e "${GREEN}    ✓ Indexed codebase${NC}"

                            # Show stats
                            echo ""
                            docker exec arsenal-semantic-search-cli code-search stats
                        else
                            echo -e "${RED}    ✗ Failed to index codebase${NC}"
                            echo "    Try manually: docker exec arsenal-semantic-search-cli code-search index /project --clear"
                        fi
                    else
                        echo -e "${RED}    ✗ Failed to start semantic search containers${NC}"
                    fi

                    cd "$PROJECT_ROOT"
                else
                    echo "  Skipped semantic search startup"
                    echo "  To start later: cd arsenal && docker-compose up -d"
                fi
            fi
        fi
    fi
else
    echo -e "${YELLOW}  ! Semantic search skill not found - skipping${NC}"
fi

# 7. Check for optional tool dependencies
echo -e "\n${YELLOW}Step 7: Checking optional tool dependencies...${NC}"

# Detect OS for platform-specific instructions
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PKG_MANAGER="apt-get"
    OS_NAME="Ubuntu/Debian"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PKG_MANAGER="brew"
    OS_NAME="macOS"
else
    PKG_MANAGER="unknown"
    OS_NAME="$OSTYPE"
fi

# Track missing packages
MISSING_PACKAGES=()

# Check for psql (PostgreSQL client) - needed for db-query skill
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}  ! psql (PostgreSQL client) not found${NC}"
    echo "    The db-query skill requires psql to query the production database"
    if [[ "$PKG_MANAGER" == "apt-get" ]]; then
        MISSING_PACKAGES+=("postgresql-client")
    elif [[ "$PKG_MANAGER" == "brew" ]]; then
        MISSING_PACKAGES+=("postgresql")
    fi
else
    echo -e "${GREEN}  ✓ psql found${NC}"
fi

# Check for jq (JSON processor) - needed for parsing AWS secrets
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}  ! jq (JSON processor) not found${NC}"
    echo "    jq is useful for parsing JSON output from AWS CLI and other tools"
    MISSING_PACKAGES+=("jq")
else
    echo -e "${GREEN}  ✓ jq found${NC}"
fi

# Check for aws CLI - useful for AWS operations (optional)
# Note: AWS CLI installation is platform-specific and not included in auto-install
if ! command -v aws &> /dev/null; then
    echo -e "${YELLOW}  ! aws CLI not found (optional)${NC}"
    echo "    The AWS CLI is useful for refreshing credentials and managing AWS resources"
    if [[ "$PKG_MANAGER" == "apt-get" ]]; then
        echo "    Install on Ubuntu: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    elif [[ "$PKG_MANAGER" == "brew" ]]; then
        echo "    Install on macOS: brew install awscli"
    fi
else
    echo -e "${GREEN}  ✓ aws CLI found${NC}"
fi

# Check for Twilio CLI - useful for managing Twilio resources
if ! command -v twilio &> /dev/null; then
    echo -e "${YELLOW}  ! Twilio CLI not found (optional)${NC}"
    echo "    The Twilio CLI is useful for listing phone numbers and managing Twilio resources"

    # Twilio CLI requires Node.js/npm
    if command -v npm &> /dev/null; then
        if [[ "$NONINTERACTIVE" == "true" ]]; then
            REPLY="n"
        else
            read -p "  Install Twilio CLI globally with npm? [y/N]: " -n 1 -r
            echo
        fi
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "  Installing Twilio CLI..."
            npm install -g twilio-cli
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}  ✓ Successfully installed Twilio CLI${NC}"

                # Auto-configure if credentials are available
                TWILIO_ACCOUNT_SID=""
                TWILIO_AUTH_TOKEN=""

                # Check for Twilio credentials in api/.env
                if [ -f "$PROJECT_ROOT/api/.env" ]; then
                    TWILIO_ACCOUNT_SID=$(grep "^TWILIO_ACCOUNT_SID=" "$PROJECT_ROOT/api/.env" | head -1 | cut -d'=' -f2 | tr -d ' "'"'"'')
                    TWILIO_AUTH_TOKEN=$(grep "^TWILIO_AUTH_TOKEN=" "$PROJECT_ROOT/api/.env" | head -1 | cut -d'=' -f2 | tr -d ' "'"'"'')
                fi

                if [ -n "$TWILIO_ACCOUNT_SID" ] && [ -n "$TWILIO_AUTH_TOKEN" ]; then
                    echo "  Configuring Twilio CLI with credentials from api/.env..."
                    twilio profiles:create default --account-sid "$TWILIO_ACCOUNT_SID" --auth-token "$TWILIO_AUTH_TOKEN" 2>/dev/null || \
                    twilio login --account-sid "$TWILIO_ACCOUNT_SID" --auth-token "$TWILIO_AUTH_TOKEN" 2>/dev/null

                    if [ $? -eq 0 ]; then
                        echo -e "${GREEN}    ✓ Configured Twilio CLI with project credentials${NC}"
                        echo "    Usage: twilio phone-numbers:list"
                    else
                        echo -e "${YELLOW}    ! Could not auto-configure Twilio CLI${NC}"
                        echo "    Run manually: twilio login"
                    fi
                else
                    echo "    Usage: twilio phone-numbers:list"
                    echo "    Login: twilio login (will prompt for Account SID and Auth Token)"
                fi
            else
                echo -e "${RED}  ✗ Failed to install Twilio CLI${NC}"
            fi
        else
            echo "  Skipped Twilio CLI installation"
            echo "  To install manually: npm install -g twilio-cli"
        fi
    else
        echo "    npm not found - Twilio CLI requires Node.js/npm"
        echo "    Install Node.js first, then run: npm install -g twilio-cli"
    fi
else
    echo -e "${GREEN}  ✓ Twilio CLI found${NC}"

    # Check if already logged in
    if twilio profiles:list 2>/dev/null | grep -q "default"; then
        echo "    Already configured with default profile"
    else
        # Try to auto-configure if credentials are available
        TWILIO_ACCOUNT_SID=""
        TWILIO_AUTH_TOKEN=""

        if [ -f "$PROJECT_ROOT/api/.env" ]; then
            TWILIO_ACCOUNT_SID=$(grep "^TWILIO_ACCOUNT_SID=" "$PROJECT_ROOT/api/.env" | head -1 | cut -d'=' -f2 | tr -d ' "'"'"'')
            TWILIO_AUTH_TOKEN=$(grep "^TWILIO_AUTH_TOKEN=" "$PROJECT_ROOT/api/.env" | head -1 | cut -d'=' -f2 | tr -d ' "'"'"'')
        fi

        if [ -n "$TWILIO_ACCOUNT_SID" ] && [ -n "$TWILIO_AUTH_TOKEN" ]; then
            if [[ "$NONINTERACTIVE" == "true" ]]; then
                REPLY="n"
            else
                read -p "  Configure Twilio CLI with credentials from api/.env? [y/N]: " -n 1 -r
                echo
            fi
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                twilio profiles:create default --account-sid "$TWILIO_ACCOUNT_SID" --auth-token "$TWILIO_AUTH_TOKEN" 2>/dev/null || \
                twilio login --account-sid "$TWILIO_ACCOUNT_SID" --auth-token "$TWILIO_AUTH_TOKEN" 2>/dev/null

                if [ $? -eq 0 ]; then
                    echo -e "${GREEN}  ✓ Configured Twilio CLI${NC}"
                else
                    echo -e "${YELLOW}  ! Could not configure Twilio CLI${NC}"
                fi
            fi
        fi
    fi
fi

# Offer to install missing packages
if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Missing packages: ${MISSING_PACKAGES[*]}${NC}"

    if [[ "$PKG_MANAGER" == "apt-get" ]]; then
        if [[ "$NONINTERACTIVE" == "true" ]]; then
            REPLY="n"
        else
            read -p "  Install missing packages with apt-get? (requires sudo) [y/N]: " -n 1 -r
            echo
        fi
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "  Installing packages..."
            sudo apt-get update -qq
            sudo apt-get install -y "${MISSING_PACKAGES[@]}"
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}  ✓ Successfully installed packages${NC}"
            else
                echo -e "${RED}  ✗ Failed to install some packages${NC}"
            fi
        else
            echo "  Skipped package installation"
            echo "  To install manually: sudo apt-get install ${MISSING_PACKAGES[*]}"
        fi
    elif [[ "$PKG_MANAGER" == "brew" ]]; then
        if [[ "$NONINTERACTIVE" == "true" ]]; then
            REPLY="n"
        else
            read -p "  Install missing packages with Homebrew? [y/N]: " -n 1 -r
            echo
        fi
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "  Installing packages..."
            brew install "${MISSING_PACKAGES[@]}"
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}  ✓ Successfully installed packages${NC}"
            else
                echo -e "${RED}  ✗ Failed to install some packages${NC}"
            fi
        else
            echo "  Skipped package installation"
            echo "  To install manually: brew install ${MISSING_PACKAGES[*]}"
        fi
    else
        echo "  Unknown package manager - please install manually:"
        echo "    ${MISSING_PACKAGES[*]}"
    fi
fi

# 8. Copy CLAUDE.md
# Note: We copy instead of symlink because Claude Code doesn't reliably respect symlinks
echo -e "\n${YELLOW}Step 8: Copying CLAUDE.md...${NC}"
CLAUDE_MD="$PROJECT_ROOT/CLAUDE.md"
SOURCE_CLAUDE_MD="$SUPERPOWERS_DIR/system-prompts/CLAUDE.md"

if [ -L "$CLAUDE_MD" ]; then
    echo "  ! Removing old CLAUDE.md symlink (switching to copy for reliability)"
    rm "$CLAUDE_MD"
    cp "$SOURCE_CLAUDE_MD" "$CLAUDE_MD"
    echo -e "${GREEN}  ✓ Converted CLAUDE.md from symlink to copy${NC}"
elif [ -f "$CLAUDE_MD" ]; then
    # Backup existing file if it differs from source
    if ! cmp -s "$CLAUDE_MD" "$SOURCE_CLAUDE_MD"; then
        BACKUP_FILE="$CLAUDE_MD.backup-$(date +%Y%m%d-%H%M%S)"
        cp "$CLAUDE_MD" "$BACKUP_FILE"
        echo -e "${YELLOW}  ! Created backup: $BACKUP_FILE${NC}"
    fi
    echo "  Updating existing CLAUDE.md from arsenal..."
    cp "$SOURCE_CLAUDE_MD" "$CLAUDE_MD"
    echo -e "${GREEN}  ✓ Updated CLAUDE.md${NC}"
else
    cp "$SOURCE_CLAUDE_MD" "$CLAUDE_MD"
    echo -e "${GREEN}  ✓ Created CLAUDE.md${NC}"
fi

echo -e "\n${GREEN}✓ Installation complete!${NC}"
echo ""
echo "Arsenal setup:"
echo "  - $PROJECT_ROOT/.claude (agents, commands, skills, hooks, settings)"
echo "  - $PROJECT_ROOT/.pre-commit-scripts -> $SUPERPOWERS_DIR/pre-commit-scripts (symlink)"
echo "  - $PROJECT_ROOT/CLAUDE.md (copied from arsenal/system-prompts/CLAUDE.md)"
echo "  - $PROJECT_ROOT/AGENTS.md (copied from arsenal/system-prompts/AGENTS.md)"
echo "  - $PROJECT_ROOT/api/tests/AGENTS.md (copied from arsenal/system-prompts/testing/AGENTS.md)"
echo ""

# Check if .env was created
if [ -f "$SUPERPOWERS_ENV" ]; then
    echo -e "${GREEN}Environment configuration:${NC}"
    echo "  - arsenal/.env (edit this file to configure API keys)"
    echo ""
fi

# Check if semantic search was set up
if docker ps | grep -q arsenal-semantic-search-cli; then
    echo -e "${GREEN}Semantic search is ready!${NC}"
    echo "  Usage: docker exec arsenal-semantic-search-cli code-search find \"your search query\""
    echo "  Stats: docker exec arsenal-semantic-search-cli code-search stats"
    echo "  Reindex: docker exec arsenal-semantic-search-cli code-search index /project --clear"
    echo ""
fi

echo "To update from arsenal (CLAUDE.md/AGENTS.md/.claude/.pre-commit-scripts): re-run ./arsenal/install.sh"
echo "To edit patterns: modify files in arsenal/system-prompts/ then re-run install.sh to sync"
echo "To manage arsenal services: cd arsenal && docker-compose up -d"
