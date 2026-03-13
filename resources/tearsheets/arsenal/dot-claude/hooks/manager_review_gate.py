#!/usr/bin/env python3
"""
Stop hook that enforces manager-review approval token.

Reads the transcript, extracts the last assistant response,
and checks for the approval token from manager-review skill.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

# Resolve paths relative to this script's location
HOOKS_DIR = Path(__file__).parent.resolve()
CLAUDE_DIR = HOOKS_DIR.parent
LOG_FILE = HOOKS_DIR / "manager_review_gate.log"
SKILL_PATH = CLAUDE_DIR / "skills" / "manager-review" / "SKILL.md"

# The approval token pattern to look for
# This should match the token in the manager-review skill
APPROVAL_TOKEN = "approve_7f3d8a2e9c1b4f6e"


def log_event(status: str, message: str) -> None:
    """Log event with timestamp, status, and message."""
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} | {status:7} | {message}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)


def get_last_assistant_response(transcript_path: str) -> str | None:
    """Extract the last assistant response from the transcript."""
    transcript_file = Path(transcript_path)
    if not transcript_file.exists():
        return None

    last_response = None
    with open(transcript_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            # Look for assistant messages
            if entry.get("type") == "assistant":
                message = entry.get("message", {})
                content = message.get("content", [])
                # Extract text from content blocks
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                if text_parts:
                    last_response = "\n".join(text_parts)

    return last_response


def main() -> None:
    # Read hook input from stdin
    input_data = json.load(sys.stdin)

    session_id = input_data.get("session_id", "unknown")
    transcript_path = input_data.get("transcript_path", "")
    stop_hook_active = input_data.get("stop_hook_active", False)

    log_event("START", f"session={session_id}, stop_hook_active={stop_hook_active}")

    # Prevent infinite loops - if stop hook already ran once, approve
    if stop_hook_active:
        log_event("SKIP", "stop_hook_active=True, allowing to prevent loop")
        output = {"decision": "approve", "reason": "Stop hook already active"}
        print(json.dumps(output))
        sys.exit(0)

    # Get the last assistant response
    last_response = get_last_assistant_response(transcript_path)

    if last_response is None:
        log_event("ERROR", f"Could not read transcript: {transcript_path}")
        output = {"decision": "approve", "reason": "Could not read transcript"}
        print(json.dumps(output))
        sys.exit(0)

    # Check for approval token
    if APPROVAL_TOKEN in last_response:
        log_event("APPROVE", "Token found in response")
        output = {"decision": "approve", "reason": "Manager review token found"}
        print(json.dumps(output))
        sys.exit(0)

    # Token not found - block and require manager review
    log_event("BLOCK", "Token not found, requiring manager review")
    output = {
        "decision": "block",
        "reason": (
            "MANAGER REVIEW REQUIRED: Before responding to the user, you must:\n"
            "1. Read .claude/skills/manager-review/SKILL.md\n"
            "2. Verify your response against the checklist\n"
            "3. Include the approval token from that skill in your response\n"
            "The token format is: approve_XXXXXXXX (find the exact token in the skill file)"
        ),
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
