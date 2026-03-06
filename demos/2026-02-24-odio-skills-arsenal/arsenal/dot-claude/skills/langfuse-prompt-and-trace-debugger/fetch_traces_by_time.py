#!/usr/bin/env python3
"""
Fetch Langfuse traces from a specific time window.
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_superpowers_env, select_langfuse_environment

from langfuse import Langfuse


def fetch_traces_by_time(langfuse: Langfuse, start_time_str: str, end_time_str: str, limit: int = 100):
    """Fetch traces from a specific time window."""

    # Parse time strings
    start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
    end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))

    print(f"\nSearching for traces between:")
    print(f"  Start: {start_time}")
    print(f"  End:   {end_time}")
    print(f"  Host:  {os.environ.get('LANGFUSE_HOST')}")

    traces = langfuse.fetch_traces(limit=limit)

    matching_traces = []
    for trace in traces.data:
        trace_dict = trace.dict() if hasattr(trace, "dict") else trace
        timestamp = trace_dict.get("timestamp")

        if timestamp:
            if isinstance(timestamp, str):
                trace_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                trace_time = timestamp

            if start_time <= trace_time <= end_time:
                matching_traces.append(trace_dict)

    print(f"\nFound {len(matching_traces)} traces in time window:\n")

    for trace_dict in matching_traces:
        trace_id = trace_dict.get("id")
        name = trace_dict.get("name", "unnamed")
        timestamp = trace_dict.get("timestamp", "")
        user_id = trace_dict.get("userId", "")

        print(f"📊 {name}")
        print(f"   ID: {trace_id}")
        print(f"   Time: {timestamp}")
        print(f"   User: {user_id or 'N/A'}")
        print(f"   URL: {os.environ.get('LANGFUSE_HOST')}/trace/{trace_id}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Fetch traces from specific time window")
    parser.add_argument("start_time", help="Start time (ISO format: 2025-11-14T02:00:00Z)")
    parser.add_argument("end_time", help="End time (ISO format: 2025-11-14T03:00:00Z)")
    parser.add_argument("--limit", type=int, default=100, help="Max traces to fetch")
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

    fetch_traces_by_time(langfuse, args.start_time, args.end_time, args.limit)


if __name__ == "__main__":
    main()
