#!/usr/bin/env python3
"""
Run multiple test iterations and collect results for bulk analysis.

Usage:
    python bulk_test_runner.py PROMPT_NAME test_case.json --runs N
    python bulk_test_runner.py PROMPT_NAME test_cases/*.json

Examples:
    # Run same test 5 times to check consistency
    python bulk_test_runner.py message_enricher test_case.json --runs 5

    # Run against multiple test cases
    python bulk_test_runner.py message_enricher test_cases/case1.json test_cases/case2.json
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List

# Add current directory to path to import env_loader
sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_arsenal_env, find_project_root

# Import test_prompt functions
from test_prompt import execute_prompt_test, load_test_case


def run_bulk_tests(
    prompt_name: str,
    test_case_paths: List[Path],
    runs_per_case: int = 1
) -> dict:
    """
    Run multiple test iterations.

    Args:
        prompt_name: Name of the prompt
        test_case_paths: List of test case files
        runs_per_case: How many times to run each test case

    Returns:
        Dict with all results and summary
    """
    all_results = []

    for test_case_path in test_case_paths:
        print(f"\n{'='*60}")
        print(f"Test Case: {test_case_path.name}")
        print('='*60)

        test_case = load_test_case(test_case_path)
        context_params = test_case.get("context_params", {})

        for run_num in range(runs_per_case):
            if runs_per_case > 1:
                print(f"\n🔄 Run {run_num + 1}/{runs_per_case}")

            try:
                result = execute_prompt_test(
                    prompt_name=prompt_name,
                    context_params=context_params,
                )

                result["test_case"] = test_case_path.name
                result["run_number"] = run_num + 1
                all_results.append(result)

                print(f"✅ Completed (trace: {result['trace_id'][:8]}...)")

            except Exception as e:
                print(f"❌ Failed: {e}")
                all_results.append({
                    "test_case": test_case_path.name,
                    "run_number": run_num + 1,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })

    return {
        "prompt_name": prompt_name,
        "total_runs": len(all_results),
        "successful_runs": len([r for r in all_results if "output" in r]),
        "failed_runs": len([r for r in all_results if "error" in r]),
        "results": all_results,
        "completed_at": datetime.now().isoformat()
    }


def generate_results_document(bulk_results: dict, output_path: Path):
    """Generate markdown document with all results."""
    md_lines = []

    md_lines.append(f"# Bulk Test Results: {bulk_results['prompt_name']}")
    md_lines.append(f"\n**Generated:** {bulk_results['completed_at']}")
    md_lines.append(f"\n## Summary\n")
    md_lines.append(f"- Total runs: {bulk_results['total_runs']}")
    md_lines.append(f"- Successful: {bulk_results['successful_runs']}")
    md_lines.append(f"- Failed: {bulk_results['failed_runs']}")

    # Group by test case
    by_test_case = {}
    for result in bulk_results['results']:
        test_case = result.get('test_case', 'unknown')
        if test_case not in by_test_case:
            by_test_case[test_case] = []
        by_test_case[test_case].append(result)

    md_lines.append(f"\n## Results by Test Case\n")

    for test_case, results in by_test_case.items():
        md_lines.append(f"\n### Test Case: {test_case}\n")

        for i, result in enumerate(results, 1):
            md_lines.append(f"\n#### Run {i}\n")

            if "error" in result:
                md_lines.append(f"**❌ Error:** {result['error']}\n")
            else:
                md_lines.append(f"**Trace ID:** `{result.get('trace_id', 'N/A')}`")
                md_lines.append(f"**Version:** {result.get('prompt_version', 'N/A')}")
                md_lines.append(f"**Model:** {result.get('model', 'N/A')}")
                md_lines.append(f"\n**Output:**")
                md_lines.append("```")
                md_lines.append(result.get('output', 'N/A'))
                md_lines.append("```\n")

    # Write to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(md_lines))

    print(f"\n📄 Results document: {output_path}")


def main():
    """Main function."""
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    prompt_name = sys.argv[1]

    # Parse arguments
    runs_per_case = 1
    test_case_paths = []

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--runs":
            if i + 1 < len(sys.argv):
                runs_per_case = int(sys.argv[i + 1])
                i += 2
            else:
                print("❌ --runs requires a number")
                sys.exit(1)
        else:
            # Treat as test case file
            path = Path(arg)
            if path.exists():
                test_case_paths.append(path)
            else:
                print(f"⚠️  Test case not found: {path}")
            i += 1

    if not test_case_paths:
        print("❌ No valid test case files provided")
        sys.exit(1)

    print(f"🧪 Bulk Test Configuration:")
    print(f"   Prompt: {prompt_name}")
    print(f"   Test cases: {len(test_case_paths)}")
    print(f"   Runs per case: {runs_per_case}")
    print(f"   Total runs: {len(test_case_paths) * runs_per_case}")

    # Load environment
    print("\n🔒 Loading credentials...")
    if not load_arsenal_env():
        sys.exit(1)

    # Run bulk tests
    print("\n🚀 Starting bulk test run...\n")
    bulk_results = run_bulk_tests(prompt_name, test_case_paths, runs_per_case)

    # Save results
    project_root = find_project_root()
    results_dir = project_root / "docs" / "prompt_test_results"
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = results_dir / f"bulk_results_{prompt_name}_{timestamp}.json"
    md_path = results_dir / f"bulk_results_{prompt_name}_{timestamp}.md"

    # Save JSON
    with open(json_path, 'w') as f:
        json.dump(bulk_results, f, indent=2)
    print(f"\n💾 Saved JSON results: {json_path.relative_to(project_root)}")

    # Generate and save markdown
    generate_results_document(bulk_results, md_path)
    print(f"💾 Saved markdown report: {md_path.relative_to(project_root)}")

    # Print summary
    print(f"\n{'='*60}")
    print("BULK TEST SUMMARY")
    print('='*60)
    print(f"Total runs: {bulk_results['total_runs']}")
    print(f"Successful: {bulk_results['successful_runs']}")
    print(f"Failed: {bulk_results['failed_runs']}")

    if bulk_results['failed_runs'] > 0:
        print("\n⚠️  Some tests failed - review the results document")
        sys.exit(1)
    else:
        print("\n✅ All tests completed successfully")


if __name__ == "__main__":
    main()
