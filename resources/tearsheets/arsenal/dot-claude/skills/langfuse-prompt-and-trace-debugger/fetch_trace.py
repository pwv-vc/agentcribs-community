#!/usr/bin/env python3
"""
Fetch and display Langfuse traces for debugging and analysis.

INSTRUCTIONS FOR CLAUDE/AI AGENTS:
- This script is READ-ONLY - it only fetches trace data from Langfuse for viewing
- DO NOT use this script to modify or delete traces in Langfuse
- DO NOT push any changes to Langfuse
- This is strictly a debugging tool for understanding trace flow

Usage:
    python fetch_trace.py <trace_id>
    python fetch_trace.py <langfuse_url>
    python fetch_trace.py --list [--limit 10]

Examples:
    python fetch_trace.py db29520b-9acb-4af9-a7a0-1aa005eb7b24
    python fetch_trace.py "https://langfuse.prod.example.com/project/.../traces?peek=db29520b..."
    python fetch_trace.py --list --limit 5

Environment:
    Requires LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables.
    Load with: set -a; source superpowers/.env; set +a
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import TypeAlias
from urllib.parse import parse_qs, urlparse

# Add current directory to path to import env_loader
sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_superpowers_env, select_langfuse_environment

from langfuse import Langfuse
from langfuse.api.resources.commons.errors.not_found_error import NotFoundError

# Type alias for observation data from Langfuse API
ObservationDict: TypeAlias = dict[str, object]


def get_langfuse() -> Langfuse | None:
    """Get Langfuse client from environment variables."""
    try:
        public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
        secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
        host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

        if not public_key or not secret_key:
            print("ERROR: Missing required environment variables:")
            print("  - LANGFUSE_PUBLIC_KEY")
            print("  - LANGFUSE_SECRET_KEY")
            print("\nLoad them with: set -a; source superpowers/.env; set +a")
            return None

        return Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )
    except Exception as e:
        print(f"ERROR: Failed to initialize Langfuse client: {e}")
        return None


def extract_trace_id_from_url(url: str) -> str | None:
    """Extract trace ID from a Langfuse URL."""
    # Try to extract from peek parameter first
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)

    if "peek" in query_params:
        return query_params["peek"][0]

    # Try to extract from path (e.g., /traces/abc-def-123)
    path_match = re.search(r"/traces/([a-f0-9\-]+)", parsed.path)
    if path_match:
        return path_match.group(1)

    return None


def format_observation(obs: ObservationDict, indent: int = 0) -> str:
    """Format an observation for display."""
    indent_str = "  " * indent
    lines = []

    # Header with type and name
    obs_type = str(obs.get("type", "unknown"))
    name = str(obs.get("name", "unnamed"))
    start_time = str(obs.get("startTime", ""))

    lines.append(f"{indent_str}📍 {obs_type.upper()}: {name}")
    lines.append(f"{indent_str}   Time: {start_time}")

    # Input parameters
    if input_data := obs.get("input"):
        lines.append(f"{indent_str}   Input:")
        if isinstance(input_data, dict):
            for key, value in input_data.items():
                # Handle special parameters we care about for intervention debugging
                if key in [
                    "intervention_needed",
                    "other_codes",
                    "sender_has_upcoming_facts",
                    "has_sender_interventions_last_6_hours",
                    "has_recipient_interventions_last_6_hours",
                    "condition_key",
                    "sql_query",
                    "params_subset",
                    "key_params",
                ]:
                    value_str = json.dumps(value, indent=2) if isinstance(value, (dict, list)) else str(value)
                    lines.append(f"{indent_str}     • {key}: {value_str}")
        else:
            lines.append(f"{indent_str}     {str(input_data)[:200]}")

    # Output
    if output_data := obs.get("output"):
        lines.append(f"{indent_str}   Output:")
        if isinstance(output_data, dict):
            output_str = json.dumps(output_data, indent=2).replace("\n", f"\n{indent_str}     ")
            lines.append(f"{indent_str}     {output_str}")
        elif isinstance(output_data, str) and len(output_data) > 200:
            # For long YAML content, just show first part
            lines.append(f"{indent_str}     {output_data[:200]}...")
            lines.append(f"{indent_str}     [Truncated - {len(output_data)} total characters]")
        else:
            lines.append(f"{indent_str}     {output_data}")

    # Status and errors
    if status := obs.get("status"):
        lines.append(f"{indent_str}   Status: {status}")

    if error := obs.get("statusMessage"):
        lines.append(f"{indent_str}   ⚠️  Error: {error}")

    return "\n".join(lines)


def display_trace(langfuse: Langfuse, trace_id: str) -> None:
    """Fetch and display a trace with all its observations."""
    try:
        # Fetch the trace
        trace_response = langfuse.fetch_trace(trace_id)
        if not trace_response:
            print(f"ERROR: Trace not found: {trace_id}")
            return

        # Extract the actual trace data
        trace = trace_response.data if hasattr(trace_response, "data") else trace_response

        print("\n" + "=" * 80)
        print(f"TRACE: {trace.id}")
        print("=" * 80)

        # Display trace metadata
        print(f"Name: {trace.name}")
        print(f"User ID: {getattr(trace, 'user_id', None) or getattr(trace, 'userId', None) or 'N/A'}")
        print(f"Session ID: {getattr(trace, 'session_id', None) or getattr(trace, 'sessionId', None) or 'N/A'}")
        print(f"Timestamp: {trace.timestamp}")

        if trace.input:
            print(f"\nTrace Input: {json.dumps(trace.input, indent=2)}")

        if trace.output:
            print(f"\nTrace Output: {json.dumps(trace.output, indent=2)}")

        # Fetch and display observations
        print("\n" + "-" * 80)
        print("OBSERVATIONS:")
        print("-" * 80)

        observations = langfuse.fetch_observations(trace_id=trace_id)

        # Group observations by parent
        root_observations = []
        child_observations: dict[str, list[ObservationDict]] = {}

        for obs in observations.data:
            obs_dict = obs.dict() if hasattr(obs, "dict") else obs
            parent_id_obj = obs_dict.get("parentObservationId")

            if not parent_id_obj:
                root_observations.append(obs_dict)
            else:
                parent_id = str(parent_id_obj)
                if parent_id not in child_observations:
                    child_observations[parent_id] = []
                child_observations[parent_id].append(obs_dict)

        # Sort observations by startTime
        root_observations.sort(key=lambda x: str(x.get("startTime", "")))

        # Display observations hierarchically
        def display_observation_tree(obs: ObservationDict, indent: int = 0) -> None:
            print(format_observation(obs, indent))

            # Display children
            obs_id = str(obs["id"])
            if obs_id in child_observations:
                for child in sorted(child_observations[obs_id], key=lambda x: str(x.get("startTime", ""))):
                    display_observation_tree(child, indent + 1)
            print()

        for obs in root_observations:
            display_observation_tree(obs)

        # Look for SQL query spans specifically
        print("\n" + "-" * 80)
        print("SQL QUERY ANALYSIS:")
        print("-" * 80)

        sql_spans = [obs for obs in observations.data if hasattr(obs, "name") and obs.name == "sql_query"]

        if sql_spans:
            for span in sql_spans:
                span_dict = span.dict() if hasattr(span, "dict") else span
                condition_key = "unknown"
                if input_data := span_dict.get("input"):
                    if isinstance(input_data, dict):
                        condition_key = input_data.get("condition_key", "unknown")

                output = span_dict.get("output", "")
                matched = "matched" in str(output).lower() and "not matched" not in str(output).lower()

                print(f"  • {condition_key}: {'✅ MATCHED' if matched else '❌ NOT MATCHED'}")

                # Show key parameters that affected the decision
                if input_data and isinstance(input_data, dict):
                    if params := input_data.get("params_subset"):
                        print(f"    Parameters: {json.dumps(params, indent=6)}")
        else:
            print("  No SQL query spans found in trace")

        # Check for intervention conditions summary
        summary_spans = [
            obs for obs in observations.data if hasattr(obs, "name") and obs.name == "sql_conditions_summary"
        ]

        if summary_spans:
            print("\n" + "-" * 80)
            print("INTERVENTION CONDITIONS SUMMARY:")
            print("-" * 80)
            for span in summary_spans:
                span_dict = span.dict() if hasattr(span, "dict") else span
                if input_data := span_dict.get("input"):
                    if isinstance(input_data, dict):
                        if evaluated := input_data.get("conditions_evaluated"):
                            for condition in evaluated:
                                status = "✅" if condition.get("matched") else "❌"
                                print(f"  {status} {condition.get('condition_key', 'unknown')}")

                        if key_params := input_data.get("key_params"):
                            print("\n  Key Parameters:")
                            print(f"    • intervention_needed: {key_params.get('intervention_needed')}")
                            print(f"    • other_codes: {key_params.get('other_codes')}")
                            print(f"    • sender_has_upcoming_facts: {key_params.get('sender_has_upcoming_facts')}")

        print("\n" + "=" * 80)

    except NotFoundError:
        print(f"\nERROR: Trace with ID '{trace_id}' not found in Langfuse")
    except (ConnectionError, TimeoutError) as e:
        print(f"\nERROR: Failed to connect to Langfuse: {e}")
        print("\nMake sure you have the correct environment variables set:")
        print("  LANGFUSE_PUBLIC_KEY")
        print("  LANGFUSE_SECRET_KEY")
        print("  LANGFUSE_HOST")


def list_recent_traces(langfuse: Langfuse, limit: int = 10) -> None:
    """List recent traces."""
    try:
        traces = langfuse.fetch_traces(limit=limit)

        print("\n" + "=" * 80)
        print(f"RECENT TRACES (showing {limit})")
        print("=" * 80)

        for trace in traces.data:
            trace_dict = trace.dict() if hasattr(trace, "dict") else trace
            trace_id = trace_dict.get("id", "unknown")
            name = trace_dict.get("name", "unnamed")
            timestamp = trace_dict.get("timestamp", "")
            user_id = trace_dict.get("userId", "")

            print(f"\n📊 {name}")
            print(f"   ID: {trace_id}")
            print(f"   Time: {timestamp}")
            print(f"   User: {user_id or 'N/A'}")

            # Show trace URL
            langfuse_host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
            print(f"   URL: {langfuse_host}/traces/{trace_id}")

        print("\n" + "=" * 80)

    except NotFoundError as e:
        print(f"\nERROR: Could not fetch traces from Langfuse: {e}")
    except (ConnectionError, TimeoutError) as e:
        print(f"\nERROR: Failed to connect to Langfuse: {e}")


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description="Fetch and display Langfuse traces")
    parser.add_argument("trace_input", nargs="?", help="Trace ID or Langfuse URL")
    parser.add_argument("--list", action="store_true", help="List recent traces")
    parser.add_argument("--limit", type=int, default=10, help="Number of traces to list (default: 10)")
    parser.add_argument(
        "--env",
        choices=["staging", "production", "prod"],
        help="Langfuse environment to use (default: from LANGFUSE_ENVIRONMENT or staging)",
    )

    args = parser.parse_args()

    # Auto-load environment from arsenal/.env
    if not load_superpowers_env():
        sys.exit(1)

    # Override environment if --env flag provided
    if args.env:
        select_langfuse_environment(args.env)

    langfuse = get_langfuse()
    if not langfuse:
        sys.exit(1)

    if args.list:
        list_recent_traces(langfuse, args.limit)
    elif args.trace_input:
        # Check if it's a URL or direct trace ID
        if args.trace_input.startswith("http"):
            trace_id = extract_trace_id_from_url(args.trace_input)
            if not trace_id:
                print(f"ERROR: Could not extract trace ID from URL: {args.trace_input}")
                sys.exit(1)
            print(f"Extracted trace ID from URL: {trace_id}")
            display_trace(langfuse, trace_id)
        else:
            display_trace(langfuse, args.trace_input)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
