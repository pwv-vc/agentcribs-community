#!/usr/bin/env python3
"""
Skill Router Hook for UserPromptSubmit

Injects reasoning instructions that let Claude decide which skill to use
based on the skills index. Runs on every user message.

Complements SessionStart hook (which loads bootstrap rules and tokens).
"""

import json
import sys
import os
import re
from pathlib import Path


def get_project_dir() -> str:
    """Get project directory from env or fallback to cwd."""
    return os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())


def should_skip_message(message: str) -> bool:
    """Check if message should skip skill checking."""
    message = message.strip().lower()

    # Skip very short messages
    if len(message) < 5:
        return True

    # Skip confirmations
    skip_patterns = [
        r'^(yes|no|ok|okay|sure|thanks|thank you|y|n)\.?$',
        r'^(continue|proceed|go ahead|do it)\.?$',
        r'^(looks good|lgtm|approved)\.?$',
    ]

    for pattern in skip_patterns:
        if re.match(pattern, message):
            return True

    return False


def main() -> None:
    """
    Hook that injects skill-checking instructions to Claude.
    Let Claude's reasoning decide which skill to use.
    """
    # A/B test toggle: set SKILL_ROUTER_ENABLED=0 to disable
    if os.environ.get("SKILL_ROUTER_ENABLED") == "0":
        print(json.dumps({}))
        return

    project_dir = get_project_dir()
    log_file = Path(project_dir) / ".claude" / "hooks" / "skill-router.log"
    skills_index = ".claude/skills/SKILLS-INDEX.md"

    # Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({}))
        return

    user_message = hook_input.get("prompt", "")

    # Log for debugging
    with open(log_file, "a") as f:
        f.write(f"[{__import__('datetime').datetime.now()}] Message: {user_message[:50]}...\n")

    # Skip empty or confirmation messages
    if not user_message or should_skip_message(user_message):
        print(json.dumps({}))
        return

    # Skip if user already explicitly invoked a skill
    if user_message.strip().startswith('/'):
        print(json.dumps({}))
        return

    # Inject reasoning instructions - let Claude decide
    output = {
        "reason": f"""Before responding, analyze the user's request:

1. Did they mention a skill path (like /skill-name)? If so, use that skill.
2. Does their request relate to any available skill? Check {skills_index} for the list.
3. If a skill matches their intent, invoke it using the Skill tool BEFORE responding.
4. Only if NO skill matches, respond normally without invoking any skill.

Read {skills_index} to see all available skills and their descriptions.""",
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": f"Skills index available at {skills_index}"
        }
    }

    with open(log_file, "a") as f:
        f.write("  -> Injected skill-checking instructions\n")

    print(json.dumps(output))


if __name__ == "__main__":
    main()
