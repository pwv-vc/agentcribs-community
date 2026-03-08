#!/usr/bin/env python3
"""
Create a test case template for prompt iteration.

Usage:
    python setup_test_case.py PROMPT_NAME [--from-trace TRACE_ID]

Examples:
    python setup_test_case.py message_enricher
    python setup_test_case.py journal_agent --from-trace abc123
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path to import env_loader
sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_arsenal_env, find_project_root

from langfuse import Langfuse


def fetch_trace_data(trace_id: str, langfuse: Langfuse) -> dict | None:
    """Fetch trace data from Langfuse."""
    try:
        trace = langfuse.api.trace.get(trace_id)

        # Extract input parameters from the trace
        # This will vary based on your trace structure
        observations = trace.observations if hasattr(trace, 'observations') else []

        # Find the generation observation (LLM call)
        generation = None
        for obs in observations:
            if hasattr(obs, 'type') and obs.type == 'GENERATION':
                generation = obs
                break

        if not generation:
            print(f"⚠️  No generation found in trace {trace_id}")
            return None

        return {
            "trace_id": trace_id,
            "input": generation.input if hasattr(generation, 'input') else {},
            "output": generation.output if hasattr(generation, 'output') else {},
            "metadata": generation.metadata if hasattr(generation, 'metadata') else {},
        }
    except Exception as e:
        print(f"❌ Failed to fetch trace: {e}")
        return None


def create_test_case_from_trace(prompt_name: str, trace_data: dict, output_dir: Path) -> Path:
    """Create test case from trace data."""
    test_case = {
        "prompt_name": prompt_name,
        "created_from": "trace",
        "source_trace_id": trace_data["trace_id"],
        "created_at": datetime.now().isoformat(),
        "context_params": trace_data["input"],
        "expected_behavior": "# TODO: Describe what the prompt SHOULD do",
        "actual_output": trace_data["output"],
        "issues": "# TODO: Describe what's wrong with the actual output",
    }

    filename = f"test_case_trace_{trace_data['trace_id'][:8]}.json"
    filepath = output_dir / filename

    with open(filepath, 'w') as f:
        json.dump(test_case, f, indent=2)

    return filepath


def create_manual_test_case(prompt_name: str, output_dir: Path) -> Path:
    """Create empty test case template for manual filling."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    test_case = {
        "prompt_name": prompt_name,
        "created_from": "manual",
        "created_at": datetime.now().isoformat(),
        "context_params": {
            "# TODO": "Add the context_params required by this prompt",
            "# Example for router_context_1on1": {
                "has_recent_journal_prompt": "true",
                "journal_prompt_theme": "gratitude",
                "hours_since_journal_prompt": "2",
                "current_flow": "null",
                "flow_confidence": "0.0"
            },
            "# IMPORTANT": "Check the codebase to see what params are actually passed"
        },
        "test_input": {
            "# TODO": "Add the actual input data (message, conversation, etc.)",
            "message_content": "Example message text here",
            "sender_name": "Test User",
            "recipient_name": "Codel"
        },
        "expected_behavior": "# TODO: Describe what the prompt SHOULD output for this input",
        "notes": "# TODO: Add any notes about this test case"
    }

    filename = f"test_case_manual_{timestamp}.json"
    filepath = output_dir / filename

    with open(filepath, 'w') as f:
        json.dump(test_case, f, indent=2)

    return filepath


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    prompt_name = sys.argv[1]

    # Check for --from-trace flag
    trace_id = None
    if "--from-trace" in sys.argv:
        idx = sys.argv.index("--from-trace")
        if idx + 1 < len(sys.argv):
            trace_id = sys.argv[idx + 1]

    # Create output directory
    project_root = find_project_root()
    output_dir = project_root / "docs" / "prompt_test_cases"
    output_dir.mkdir(parents=True, exist_ok=True)

    if trace_id:
        print(f"📥 Fetching trace {trace_id} from Langfuse...")

        # Load environment
        if not load_arsenal_env():
            sys.exit(1)

        # Initialize Langfuse
        import os
        public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
        secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
        host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if not public_key or not secret_key:
            print("❌ Missing LANGFUSE credentials")
            sys.exit(1)

        langfuse = Langfuse(public_key=public_key, secret_key=secret_key, host=host)

        # Fetch trace
        trace_data = fetch_trace_data(trace_id, langfuse)
        if not trace_data:
            sys.exit(1)

        # Create test case
        filepath = create_test_case_from_trace(prompt_name, trace_data, output_dir)
        print(f"✅ Created test case from trace: {filepath.relative_to(project_root)}")
        print(f"\n📝 Next steps:")
        print(f"   1. Review the test case file")
        print(f"   2. Fill in 'expected_behavior' and 'issues' fields")
        print(f"   3. Run: uv run python test_prompt.py {prompt_name} {filepath.relative_to(project_root)}")
    else:
        # Create manual test case
        filepath = create_manual_test_case(prompt_name, output_dir)
        print(f"✅ Created manual test case template: {filepath.relative_to(project_root)}")
        print(f"\n📝 Next steps:")
        print(f"   1. Edit the test case file and fill in TODOs")
        print(f"   2. Check codebase for actual context_params needed")
        print(f"   3. Run: uv run python test_prompt.py {prompt_name} {filepath.relative_to(project_root)}")


if __name__ == "__main__":
    main()
