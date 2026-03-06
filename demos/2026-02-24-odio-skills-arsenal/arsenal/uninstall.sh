#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Uninstalling Arsenal symlinks...${NC}\n"

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Remove .claude symlink
if [ -L "$PROJECT_ROOT/.claude" ]; then
    rm "$PROJECT_ROOT/.claude"
    echo -e "${GREEN}✓ Removed .claude symlink${NC}"
else
    echo "  ! No .claude symlink found"
fi

# Remove .pre-commit-scripts symlink
if [ -L "$PROJECT_ROOT/.pre-commit-scripts" ]; then
    rm "$PROJECT_ROOT/.pre-commit-scripts"
    echo -e "${GREEN}✓ Removed .pre-commit-scripts symlink${NC}"
else
    echo "  ! No .pre-commit-scripts symlink found"
fi

# Remove CLAUDE.md symlink
if [ -L "$PROJECT_ROOT/CLAUDE.md" ]; then
    rm "$PROJECT_ROOT/CLAUDE.md"
    echo -e "${GREEN}✓ Removed CLAUDE.md symlink${NC}"

    # Restore backup if it exists
    if [ -f "$PROJECT_ROOT/CLAUDE.md.bak" ]; then
        mv "$PROJECT_ROOT/CLAUDE.md.bak" "$PROJECT_ROOT/CLAUDE.md"
        echo -e "${GREEN}✓ Restored CLAUDE.md from backup${NC}"
    fi
else
    echo "  ! No CLAUDE.md symlink found"
fi

# Remove AGENTS.md symlinks
if [ -L "$PROJECT_ROOT/AGENTS.md" ]; then
    rm "$PROJECT_ROOT/AGENTS.md"
    echo -e "${GREEN}✓ Removed root AGENTS.md symlink${NC}"

    # Restore backup if it exists
    if [ -f "$PROJECT_ROOT/AGENTS.md.backup" ]; then
        mv "$PROJECT_ROOT/AGENTS.md.backup" "$PROJECT_ROOT/AGENTS.md"
        echo -e "${GREEN}✓ Restored AGENTS.md from backup${NC}"
    fi
else
    echo "  ! No root AGENTS.md symlink found"
fi

if [ -L "$PROJECT_ROOT/api/tests/AGENTS.md" ]; then
    rm "$PROJECT_ROOT/api/tests/AGENTS.md"
    echo -e "${GREEN}✓ Removed testing AGENTS.md symlink${NC}"

    # Restore backup if it exists
    if [ -f "$PROJECT_ROOT/api/tests/AGENTS.md.backup" ]; then
        mv "$PROJECT_ROOT/api/tests/AGENTS.md.backup" "$PROJECT_ROOT/api/tests/AGENTS.md"
        echo -e "${GREEN}✓ Restored testing AGENTS.md from backup${NC}"
    fi
else
    echo "  ! No testing AGENTS.md symlink found"
fi

echo -e "\n${GREEN}✓ Uninstallation complete!${NC}"
echo ""
echo "Note: This only removes symlinks. The arsenal submodule remains."
echo "To fully remove arsenal, run: git submodule deinit arsenal && git rm arsenal"
