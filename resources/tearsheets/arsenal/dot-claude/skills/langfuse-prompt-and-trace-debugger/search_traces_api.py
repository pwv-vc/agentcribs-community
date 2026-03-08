#!/usr/bin/env python3
"""
Search traces using the Langfuse REST API directly with query parameter.
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_superpowers_env, select_langfuse_environment

import httpx


def search_traces(search_term: str, limit: int = 100):
    """Search traces using REST API."""

    host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com")
    public_key = os.environ["LANGFUSE_PUBLIC_KEY"]
    secret_key = os.environ["LANGFUSE_SECRET_KEY"]

    print(f"\nSearching traces for: '{search_term}'")
    print(f"Host: {host}")
    print(f"Limit: {limit} traces\n")

    # Try different API endpoints and parameters
    endpoints_to_try = [
        (f"{host}/api/public/traces", {"query": search_term, "limit": limit}),
        (f"{host}/api/public/traces", {"search": search_term, "limit": limit}),
        (f"{host}/api/public/traces", {"q": search_term, "limit": limit}),
        (f"{host}/api/public/traces", {"filter": json.dumps({"query": search_term}), "limit": limit}),
    ]

    for endpoint, params in endpoints_to_try:
        print(f"Trying: {endpoint} with params {params}")

        try:
            response = httpx.get(
                endpoint,
                params=params,
                auth=(public_key, secret_key),
                timeout=30.0,
            )

            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                traces = data.get("data", [])

                print(f"  ✅ Found {len(traces)} traces\n")

                if traces:
                    for trace in traces[:5]:  # Show first 5
                        trace_id = trace.get("id")
                        name = trace.get("name", "unnamed")
                        timestamp = trace.get("timestamp", "")

                        print(f"📊 {name}")
                        print(f"   ID: {trace_id}")
                        print(f"   Time: {timestamp}")
                        print(f"   URL: {host}/trace/{trace_id}")
                        print()

                    if len(traces) > 5:
                        print(f"... and {len(traces) - 5} more")

                    return
            elif response.status_code == 400:
                error_detail = response.json()
                print(f"  ❌ Bad request: {error_detail.get('message', 'Unknown error')}")
            else:
                print(f"  ❌ Error: {response.text[:200]}")

        except Exception as e:
            print(f"  ❌ Exception: {e}")

        print()

    print("\n❌ None of the attempted query parameters worked.")
    print("\nThe Langfuse SDK/API may not support text search via these parameters.")
    print("Full text search might only be available through the UI.")
    print("\nAlternative: Use the UI filter at:")
    print(f"  {host}/project/YOUR_PROJECT_ID/traces?filter=...")


def main():
    parser = argparse.ArgumentParser(description="Search traces using REST API")
    parser.add_argument("search_term", help="Text to search for in traces")
    parser.add_argument("--limit", type=int, default=100, help="Max traces to return")
    parser.add_argument("--env", choices=["staging", "production", "prod"], help="Langfuse environment")

    args = parser.parse_args()

    if not load_superpowers_env():
        sys.exit(1)

    if args.env:
        select_langfuse_environment(args.env)

    search_traces(args.search_term, args.limit)


if __name__ == "__main__":
    main()
