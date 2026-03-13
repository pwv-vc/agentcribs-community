#!/usr/bin/env python3
"""
Compare outputs from two different test runs (side-by-side comparison).

Usage:
    python compare_outputs.py result1.json result2.json
    python compare_outputs.py --trace-ids TRACE_ID_1 TRACE_ID_2

Examples:
    # Compare two saved result files
    python compare_outputs.py docs/prompt_test_results/test_baseline.json docs/prompt_test_results/test_v2.json

    # Compare two traces directly from Langfuse
    python compare_outputs.py --trace-ids abc123 def456
"""

import json
import sys
from pathlib import Path

# Add current directory to path to import env_loader
sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_arsenal_env, find_project_root


def load_result(result_path: Path) -> dict:
    """Load result from JSON file."""
    with open(result_path) as f:
        return json.load(f)


def fetch_trace_output(trace_id: str) -> dict:
    """Fetch trace and extract output from Langfuse."""
    from langfuse import Langfuse
    import os

    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
    host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

    langfuse = Langfuse(public_key=public_key, secret_key=secret_key, host=host)

    try:
        trace = langfuse.api.trace.get(trace_id)

        # Extract generation output
        observations = trace.observations if hasattr(trace, 'observations') else []
        for obs in observations:
            if hasattr(obs, 'type') and obs.type == 'GENERATION':
                return {
                    "trace_id": trace_id,
                    "output": obs.output if hasattr(obs, 'output') else "N/A",
                    "prompt_version": obs.metadata.get("prompt_version") if hasattr(obs, 'metadata') else "N/A"
                }

        return {"trace_id": trace_id, "output": "No generation found", "prompt_version": "N/A"}

    except Exception as e:
        return {"trace_id": trace_id, "error": str(e)}


def generate_comparison(result1: dict, result2: dict, output_path: Path):
    """Generate side-by-side comparison markdown."""
    md_lines = []

    md_lines.append("# Prompt Output Comparison\n")
    md_lines.append(f"**Generated:** {Path(__file__).stem}\n")

    # Metadata table
    md_lines.append("## Metadata\n")
    md_lines.append("| Field | Result 1 | Result 2 |")
    md_lines.append("|-------|----------|----------|")

    fields = ["trace_id", "prompt_version", "model", "timestamp", "test_case"]
    for field in fields:
        val1 = result1.get(field, "N/A")
        val2 = result2.get(field, "N/A")
        md_lines.append(f"| {field} | {val1} | {val2} |")

    # Side-by-side outputs
    md_lines.append("\n## Output Comparison\n")
    md_lines.append("### Result 1\n")
    md_lines.append("```")
    md_lines.append(str(result1.get("output", "N/A")))
    md_lines.append("```\n")

    md_lines.append("### Result 2\n")
    md_lines.append("```")
    md_lines.append(str(result2.get("output", "N/A")))
    md_lines.append("```\n")

    # Analysis section (for user to fill in)
    md_lines.append("## Analysis\n")
    md_lines.append("### Key Differences\n")
    md_lines.append("- [ ] TODO: Note important differences\n")
    md_lines.append("### Which is Better?\n")
    md_lines.append("- [ ] Result 1")
    md_lines.append("- [ ] Result 2")
    md_lines.append("- [ ] Neither - needs more work\n")
    md_lines.append("### Next Steps\n")
    md_lines.append("TODO: What changes should we try next?\n")

    # Write to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(md_lines))

    print(f"\n📄 Comparison saved to: {output_path}")


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    # Check if comparing traces or files
    if "--trace-ids" in sys.argv:
        # Load environment
        if not load_arsenal_env():
            sys.exit(1)

        trace_id_1 = sys.argv[2]
        trace_id_2 = sys.argv[3]

        print(f"📥 Fetching traces from Langfuse...")
        result1 = fetch_trace_output(trace_id_1)
        result2 = fetch_trace_output(trace_id_2)

        if "error" in result1 or "error" in result2:
            print(f"❌ Failed to fetch traces")
            if "error" in result1:
                print(f"   Trace 1: {result1['error']}")
            if "error" in result2:
                print(f"   Trace 2: {result2['error']}")
            sys.exit(1)
    else:
        # Load from files
        result1_path = Path(sys.argv[1])
        result2_path = Path(sys.argv[2])

        if not result1_path.exists():
            print(f"❌ Result 1 not found: {result1_path}")
            sys.exit(1)
        if not result2_path.exists():
            print(f"❌ Result 2 not found: {result2_path}")
            sys.exit(1)

        print(f"📂 Loading results...")
        result1 = load_result(result1_path)
        result2 = load_result(result2_path)

    # Generate comparison
    project_root = find_project_root()
    output_dir = project_root / "docs" / "prompt_comparisons"
    output_dir.mkdir(parents=True, exist_ok=True)

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"comparison_{timestamp}.md"

    generate_comparison(result1, result2, output_path)

    print(f"\n✅ Comparison complete")
    print(f"   Review: {output_path.relative_to(project_root)}")


if __name__ == "__main__":
    main()
