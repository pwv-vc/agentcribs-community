#!/usr/bin/env python3
"""
Search Langfuse traces for specific error messages in trace content.

Usage:
    python search_trace_errors.py "error message" --hours 48
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_superpowers_env, select_langfuse_environment

from langfuse import Langfuse


def search_traces_for_error(
    langfuse: Langfuse,
    search_term: str,
    hours: int = 48,
    limit: int = 200,
) -> None:
    """Search traces for specific error messages."""

    now = datetime.now(timezone.utc)
    from_timestamp = now - timedelta(hours=hours)

    print(f"\nSearching traces from last {hours} hours for: '{search_term}'")
    print(f"Time range: {from_timestamp.strftime('%Y-%m-%d %H:%M:%S')} to {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")

    # Fetch traces
    traces = langfuse.fetch_traces(limit=min(limit, 100))

    print(f"Checking {len(traces.data)} traces...")

    matches = []

    for trace in traces.data:
        trace_dict = trace.dict() if hasattr(trace, "dict") else trace
        trace_id = trace_dict.get("id", "unknown")

        # Search in trace output
        output = trace_dict.get("output")
        if output:
            output_str = json.dumps(output) if isinstance(output, dict) else str(output)
            if search_term.lower() in output_str.lower():
                matches.append((trace_dict, "trace_output", output_str[:500]))
                continue

        # Search in observations
        try:
            observations = langfuse.fetch_observations(trace_id=trace_id)
            for obs in observations.data:
                obs_dict = obs.dict() if hasattr(obs, "dict") else obs

                # Check status message
                status_msg = obs_dict.get("statusMessage", "")
                if search_term.lower() in str(status_msg).lower():
                    matches.append((trace_dict, "status_message", status_msg))
                    break

                # Check output
                obs_output = obs_dict.get("output")
                if obs_output:
                    output_str = json.dumps(obs_output) if isinstance(obs_output, dict) else str(obs_output)
                    if search_term.lower() in output_str.lower():
                        matches.append((trace_dict, "observation_output", output_str[:500]))
                        break
        except Exception:
            # Skip traces where we can't fetch observations
            continue

    if matches:
        print(f"\n✅ Found {len(matches)} matching traces:\n")
        langfuse_host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

        for trace_dict, location, content in matches:
            trace_id = trace_dict.get("id")
            name = trace_dict.get("name", "unnamed")
            timestamp = trace_dict.get("timestamp", "")

            print(f"🔍 {name}")
            print(f"   ID: {trace_id}")
            print(f"   Time: {timestamp}")
            print(f"   Location: {location}")
            print(f"   Content: {content[:200]}...")
            print(f"   URL: {langfuse_host}/trace/{trace_id}")
            print()
    else:
        print(f"\n❌ No traces found containing: '{search_term}'")


def main():
    parser = argparse.ArgumentParser(description="Search traces for error messages")
    parser.add_argument("search_term", help="Error message to search for")
    parser.add_argument("--hours", type=int, default=48, help="Hours to look back")
    parser.add_argument("--limit", type=int, default=200, help="Max traces to check")
    parser.add_argument("--env", choices=["staging", "production", "prod"], help="Langfuse environment")

    args = parser.parse_args()

    if not load_superpowers_env():
        sys.exit(1)

    if args.env:
        select_langfuse_environment(args.env)

    langfuse = Langfuse(
        public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
        secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    )

    search_traces_for_error(langfuse, args.search_term, args.hours, args.limit)


if __name__ == "__main__":
    main()
