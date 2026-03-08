#!/usr/bin/env python3
"""Debug script to see what fields are in traces."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_superpowers_env, select_langfuse_environment

from langfuse import Langfuse

if not load_superpowers_env():
    sys.exit(1)

select_langfuse_environment("production")

langfuse = Langfuse(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    host=os.environ.get("LANGFUSE_HOST"),
)

traces = langfuse.fetch_traces(limit=5)

print(f"Fetched {len(traces.data)} traces\n")

for i, trace in enumerate(traces.data[:2]):
    trace_dict = trace.dict() if hasattr(trace, "dict") else trace
    print(f"=== Trace {i+1} ===")
    print(f"Available fields: {list(trace_dict.keys())}")
    print(f"\nFull trace dict:")
    print(json.dumps(trace_dict, indent=2, default=str))
    print("\n" + "="*80 + "\n")
