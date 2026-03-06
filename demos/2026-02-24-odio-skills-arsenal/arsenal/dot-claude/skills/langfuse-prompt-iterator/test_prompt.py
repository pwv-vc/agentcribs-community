#!/usr/bin/env python3
"""
Execute a prompt with test case data for iteration workflow.

This script loads a test case, executes the prompt, and returns formatted results.

Usage:
    python test_prompt.py PROMPT_NAME test_case.json [--version V] [--baseline]

Examples:
    # Run baseline test with latest version
    python test_prompt.py message_enricher test_case.json --baseline

    # Run with specific version
    python test_prompt.py message_enricher test_case.json --version 5

Environment:
    Requires LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST, OPENAI_API_KEY
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add current directory to path to import env_loader
sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_arsenal_env, find_project_root

from langfuse import Langfuse
from langfuse.decorators import langfuse_context, observe


def load_test_case(test_case_path: Path) -> dict:
    """Load test case from JSON file."""
    with open(test_case_path) as f:
        return json.load(f)


@observe()
def execute_prompt_test(
    prompt_name: str,
    context_params: dict,
    version: int | None = None,
    label: str = "production"
) -> dict:
    """
    Execute the prompt with given parameters.

    Args:
        prompt_name: Name of the prompt in Langfuse
        context_params: Parameters to pass to prompt template
        version: Specific version to use (None = latest with label)
        label: Label to fetch (default: production)

    Returns:
        Dict with output, trace_id, and metadata
    """
    # Get Langfuse client
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
    host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

    langfuse = Langfuse(public_key=public_key, secret_key=secret_key, host=host)

    # Fetch prompt
    if version:
        prompt = langfuse.get_prompt(prompt_name, version=version)
    else:
        prompt = langfuse.get_prompt(prompt_name, label=label)

    print(f"📝 Using prompt: {prompt_name}")
    print(f"   Version: {prompt.version}")
    print(f"   Label: {label if not version else f'(specific version {version})'}")

    # Compile prompt with context_params
    compiled_prompt = prompt.compile(**context_params)

    # Get model config
    config = prompt.config if hasattr(prompt, 'config') and prompt.config else {}
    model_config = config.get("model_config", {})
    model = model_config.get("model", "gpt-4o-mini")
    temperature = model_config.get("temperature", 0.7)

    print(f"   Model: {model}")
    print(f"   Temperature: {temperature}")

    # Call OpenAI via langfuse wrapper for tracing
    from openai import OpenAI

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Make the call
    print(f"\n🔄 Executing prompt...")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": compiled_prompt}],
        temperature=temperature,
        **{k: v for k, v in model_config.items() if k not in ["model", "temperature"]}
    )

    output = response.choices[0].message.content

    # Get trace ID from langfuse context
    trace_id = langfuse_context.get_current_trace_id()

    return {
        "output": output,
        "trace_id": trace_id,
        "prompt_version": prompt.version,
        "model": model,
        "timestamp": datetime.now().isoformat(),
    }


def save_test_result(result: dict, test_case_path: Path, is_baseline: bool = False):
    """Save test result to file."""
    project_root = find_project_root()
    results_dir = project_root / "docs" / "prompt_test_results"
    results_dir.mkdir(parents=True, exist_ok=True)

    test_case_name = test_case_path.stem
    suffix = "_baseline" if is_baseline else f"_v{result['prompt_version']}"
    filename = f"{test_case_name}{suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    filepath = results_dir / filename

    with open(filepath, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n💾 Saved result to: {filepath.relative_to(project_root)}")
    return filepath


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    prompt_name = sys.argv[1]
    test_case_path = Path(sys.argv[2])

    if not test_case_path.exists():
        print(f"❌ Test case file not found: {test_case_path}")
        sys.exit(1)

    # Parse flags
    is_baseline = "--baseline" in sys.argv
    version = None
    if "--version" in sys.argv:
        idx = sys.argv.index("--version")
        if idx + 1 < len(sys.argv):
            version = int(sys.argv[idx + 1])

    # Load environment
    print("🔒 Loading credentials...")
    if not load_arsenal_env():
        sys.exit(1)

    # Verify required env vars
    required = ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "OPENAI_API_KEY"]
    missing = [var for var in required if not os.environ.get(var)]
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    # Load test case
    print(f"\n📂 Loading test case: {test_case_path.name}")
    test_case = load_test_case(test_case_path)

    # Verify test case structure
    if "context_params" not in test_case:
        print("❌ Test case missing 'context_params' field")
        sys.exit(1)

    context_params = test_case["context_params"]

    # Execute test
    try:
        result = execute_prompt_test(
            prompt_name=prompt_name,
            context_params=context_params,
            version=version,
        )

        # Add test case metadata to result
        result["test_case"] = test_case_path.name
        result["is_baseline"] = is_baseline
        result["context_params"] = context_params

        # Save result
        save_test_result(result, test_case_path, is_baseline)

        # Display output
        print(f"\n{'='*60}")
        print("OUTPUT:")
        print('='*60)
        print(result["output"])
        print('='*60)

        print(f"\n✅ Test completed successfully")
        print(f"   Trace ID: {result['trace_id']}")
        print(f"   Prompt Version: {result['prompt_version']}")
        print(f"\n🔗 View trace in Langfuse:")
        host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
        print(f"   {host}/traces/{result['trace_id']}")

    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
