#!/usr/bin/env python3
"""
SessionStart hook that injects the getting-started skill into every session.

This ensures agents have the skill content in their context from the start,
making compliance mechanical rather than relying on LLM choice.
"""
import sys
from datetime import datetime
from pathlib import Path

# Resolve paths relative to this script's location
HOOKS_DIR = Path(__file__).parent.resolve()
CLAUDE_DIR = HOOKS_DIR.parent
LOG_FILE = HOOKS_DIR / "session_start.log"
SKILL_PATH = CLAUDE_DIR / "skills" / "getting-started" / "SKILL.md"


def log_event(status: str, message: str) -> None:
    """Log event with timestamp, status, and message."""
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} | {status:7} | {message}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)


def main() -> None:
    log_event("START", f"Hook executed, cwd={Path.cwd()}")

    if not SKILL_PATH.exists():
        error_msg = f"Skill not found at {SKILL_PATH}"
        log_event("ERROR", error_msg)
        print(f"WARNING: getting-started skill not found at: {SKILL_PATH}")
        print(f"Expected location: {SKILL_PATH}")
        print("The agent will not have skill context loaded.")
        sys.exit(1)

    content = SKILL_PATH.read_text(encoding="utf-8")
    line_count = content.count("\n") + 1

    log_event("SUCCESS", f"Skill loaded, {line_count} lines")

    print("╔══════════════════════════════════════════════════════════╗")
    print("║   SESSION BOOTSTRAP: getting-started skill loaded        ║")
    print(f"║   File size: {line_count} lines                                   ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(content)
    print()
    print(f"--- End of getting-started skill ({line_count} lines) ---")
    print()


if __name__ == "__main__":
    main()
