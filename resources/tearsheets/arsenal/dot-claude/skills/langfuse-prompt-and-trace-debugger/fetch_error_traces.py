#!/usr/bin/env python3
"""
Fetch Langfuse traces with errors from a specified time range.

INSTRUCTIONS FOR CLAUDE/AI AGENTS:
- This script is READ-ONLY - it only fetches trace data from Langfuse for viewing
- DO NOT use this script to modify or delete traces in Langfuse
- DO NOT push any changes to Langfuse
- This is strictly a debugging tool for understanding error patterns

Usage:
    python fetch_error_traces.py
    python fetch_error_traces.py --hours 48
    python fetch_error_traces.py --days 7
    python fetch_error_traces.py --limit 20

Examples:
    # Fetch error traces from last 24 hours (default)
    python fetch_error_traces.py

    # Fetch error traces from last 48 hours
    python fetch_error_traces.py --hours 48

    # Fetch error traces from last 7 days
    python fetch_error_traces.py --days 7

    # Limit to 5 results
    python fetch_error_traces.py --limit 5

Environment:
    Requires LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, and LANGFUSE_HOST environment variables.
    These are automatically loaded from arsenal/.env
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Add current directory to path to import env_loader
sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_superpowers_env, select_langfuse_environment

from langfuse import Langfuse


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
            print("\nThese are automatically loaded from arsenal/.env")
            return None

        return Langfuse(public_key=public_key, secret_key=secret_key, host=host)
    except Exception as e:
        print(f"ERROR: Failed to initialize Langfuse client: {e}")
        return None


def has_error_observations(langfuse: Langfuse, trace_dict: dict) -> tuple[bool, list[str]]:
    """
    Check if a trace has any errors (either trace-level or observation-level).

    Returns:
        Tuple of (has_errors, error_messages)
    """
    trace_id = trace_dict.get("id")
    error_messages = []

    # First check trace-level error count
    error_count = trace_dict.get("errorCount", 0)
    if error_count and error_count > 0:
        error_messages.append(f"Trace has {error_count} error(s)")

    # Then check observations for ERROR level or error status
    try:
        observations = langfuse.fetch_observations(trace_id=trace_id)

        for obs in observations.data:
            obs_dict = obs.dict() if hasattr(obs, "dict") else obs
            level = obs_dict.get("level")
            status_message = obs_dict.get("statusMessage")

            # Check if observation has ERROR level or error status
            if level == "ERROR" or (status_message and "error" in status_message.lower()):
                obs_name = obs_dict.get("name", "unknown")
                if status_message:
                    error_messages.append(f"{obs_name}: {status_message}")
                else:
                    error_messages.append(f"{obs_name} (ERROR level)")

        return len(error_messages) > 0, error_messages
    except Exception as e:
        # If we can't fetch observations but trace has error count, still report it
        if error_count and error_count > 0:
            return True, error_messages
        print(f"  Warning: Could not fetch observations for trace {trace_id}: {e}")
        return False, []


def fetch_error_traces(
    langfuse: Langfuse,
    hours: int | None = None,
    days: int | None = None,
    limit: int = 50,
) -> None:
    """
    Fetch traces with errors from the specified time range.

    Args:
        langfuse: Langfuse client
        hours: Number of hours to look back (mutually exclusive with days)
        days: Number of days to look back (mutually exclusive with hours)
        limit: Maximum number of traces to fetch
    """
    # Calculate time range
    now = datetime.now(timezone.utc)
    if days:
        time_delta = timedelta(days=days)
        time_desc = f"last {days} day(s)"
    else:
        hours = hours or 24
        time_delta = timedelta(hours=hours)
        time_desc = f"last {hours} hour(s)"

    from_timestamp = now - time_delta

    print("\n" + "=" * 80)
    print(f"SEARCHING FOR ERROR TRACES ({time_desc})")
    print("=" * 80)
    print(f"Time range: {from_timestamp.strftime('%Y-%m-%d %H:%M:%S')} to {now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"Langfuse host: {os.environ.get('LANGFUSE_HOST', 'unknown')}")
    print("=" * 80)

    try:
        # Fetch traces from the time range
        # Note: The Langfuse SDK supports various filters, but we need to check all traces
        # and then filter for errors by examining their observations
        print(f"\nFetching up to {limit} traces from {time_desc}...")

        # Langfuse API has a max limit of 100 per request
        fetch_limit = min(limit * 3, 100)

        # Try to use from_timestamp parameter if supported by the SDK
        try:
            traces = langfuse.fetch_traces(
                limit=fetch_limit,  # Fetch more since we'll filter for errors
                from_timestamp=from_timestamp,
            )
        except TypeError:
            # If from_timestamp not supported, fall back to fetching recent traces
            print("  Note: Time filtering not supported by SDK, checking recent traces...")
            traces = langfuse.fetch_traces(limit=fetch_limit)

        if not traces or not traces.data:
            print("\n❌ No traces found in the specified time range")
            return

        print(f"  Found {len(traces.data)} total traces, checking for errors...")

        # Filter traces that have error observations
        error_traces: list[tuple[Any, list[str]]] = []

        for trace in traces.data:
            trace_dict = trace.dict() if hasattr(trace, "dict") else trace
            trace_id = trace_dict.get("id", "unknown")
            timestamp = trace_dict.get("timestamp")

            # Skip traces outside our time range (if we couldn't filter in the query)
            if timestamp:
                if isinstance(timestamp, str):
                    trace_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                else:
                    trace_time = timestamp

                if trace_time < from_timestamp:
                    continue

            # Check if trace has error observations
            has_errors, error_messages = has_error_observations(langfuse, trace_dict)

            if has_errors:
                error_traces.append((trace_dict, error_messages))

                # Stop if we've found enough error traces
                if len(error_traces) >= limit:
                    break

        # Display results
        if not error_traces:
            print(f"\n✅ No traces with errors found in {time_desc}")
            return

        print(f"\n❌ Found {len(error_traces)} trace(s) with errors:\n")
        print("=" * 80)

        langfuse_host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")

        for trace_dict, error_messages in error_traces:
            trace_id = trace_dict.get("id", "unknown")
            name = trace_dict.get("name", "unnamed")
            timestamp = trace_dict.get("timestamp", "")
            user_id = trace_dict.get("userId", "")

            print(f"\n🔴 {name}")
            print(f"   ID: {trace_id}")
            print(f"   Time: {timestamp}")
            print(f"   User: {user_id or 'N/A'}")
            print(f"   URL: {langfuse_host}/trace/{trace_id}")
            print(f"   Errors:")
            for error_msg in error_messages:
                print(f"     • {error_msg}")

        print("\n" + "=" * 80)
        print(f"\nTo view detailed trace information, run:")
        print(f"  cd .claude/skills/langfuse-prompt-and-trace-debugger")
        print(f"  uv run python fetch_trace.py <trace_id>")

    except Exception as e:
        print(f"\nERROR: Failed to fetch traces: {e}")
        import traceback

        traceback.print_exc()


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Fetch Langfuse traces with errors from a specified time range",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch error traces from last 24 hours (default)
  python fetch_error_traces.py

  # Fetch error traces from last 48 hours
  python fetch_error_traces.py --hours 48

  # Fetch error traces from last 7 days
  python fetch_error_traces.py --days 7

  # Limit to 5 results
  python fetch_error_traces.py --limit 5

  # Use production Langfuse server
  python fetch_error_traces.py --env production
        """,
    )

    parser.add_argument(
        "--hours",
        type=int,
        help="Number of hours to look back (default: 24, mutually exclusive with --days)",
    )
    parser.add_argument(
        "--days",
        type=int,
        help="Number of days to look back (mutually exclusive with --hours)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of error traces to display (default: 50)",
    )
    parser.add_argument(
        "--env",
        choices=["staging", "production", "prod"],
        help="Langfuse environment to use (default: from LANGFUSE_ENVIRONMENT or staging)",
    )

    args = parser.parse_args()

    # Validate mutually exclusive options
    if args.hours and args.days:
        print("ERROR: --hours and --days are mutually exclusive")
        parser.print_help()
        sys.exit(1)

    # Auto-load environment from arsenal/.env
    if not load_superpowers_env():
        sys.exit(1)

    # Override environment if --env flag provided
    if args.env:
        select_langfuse_environment(args.env)

    langfuse = get_langfuse()
    if not langfuse:
        sys.exit(1)

    fetch_error_traces(
        langfuse,
        hours=args.hours,
        days=args.days,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
