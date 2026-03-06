#!/usr/bin/env python3
"""
Fetch specific version of a Langfuse prompt.

Usage:
    python fetch_prompt_version.py PROMPT_NAME VERSION [--production]

Examples:
    python fetch_prompt_version.py cronjobs_yaml 22
    python fetch_prompt_version.py cronjobs_yaml 26 --production
"""

import json
import os
import re
import sys
from pathlib import Path

# Add current directory to path to import env_loader
sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_superpowers_env, find_project_root, select_langfuse_environment

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
            print("\nLoad them with: set -a; source arsenal/.env; set +a")
            return None

        return Langfuse(public_key=public_key, secret_key=secret_key, host=host)
    except Exception as e:
        print(f"ERROR: Failed to initialize Langfuse client: {e}")
        return None


def fetch_prompt_version(langfuse: Langfuse, prompt_name: str, version: int, cache_dir: Path | None = None) -> None:
    """Fetch a specific version of a prompt from Langfuse."""
    if cache_dir is None:
        project_root = find_project_root()
        cache_dir = project_root / "docs" / "cached_prompts"

    cache_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Fetch the specific version
        prompt = langfuse.get_prompt(prompt_name, version=version)

        # Save prompt content
        safe_prompt_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", prompt_name)
        prompt_file = cache_dir / f"{safe_prompt_name}_v{version}.txt"

        with open(prompt_file, "w") as f:
            f.write(f"# {prompt_name} (version {version})\n")
            f.write(f"# Version: {getattr(prompt, 'version', 'unknown')}\n")
            if hasattr(prompt, 'labels') and prompt.labels:
                f.write(f"# Labels: {', '.join(prompt.labels)}\n")
            f.write("#" + "=" * 60 + "\n\n")
            f.write(prompt.prompt)

        # Save config if it exists
        if hasattr(prompt, "config") and prompt.config:
            config_file = cache_dir / f"{safe_prompt_name}_v{version}_config.json"
            with open(config_file, "w") as f:
                json.dump(prompt.config, f, indent=2)

        print(f"✓ Cached: {prompt_name} (version {version})")
        print(f"  Saved to: {prompt_file}")
        if hasattr(prompt, 'labels') and prompt.labels:
            print(f"  Labels: {', '.join(prompt.labels)}")

    except Exception as e:
        print(f"✗ Error fetching {prompt_name} v{version}: {e}")
        sys.exit(1)


def main() -> None:
    """Main function."""
    args = sys.argv[1:]

    if len(args) < 2 or "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    use_production = "--production" in args
    args = [arg for arg in args if arg != "--production"]

    if len(args) < 2:
        print("ERROR: Missing required arguments")
        print(__doc__)
        sys.exit(1)

    prompt_name = args[0]
    try:
        version = int(args[1])
    except ValueError:
        print(f"ERROR: Version must be an integer, got: {args[1]}")
        sys.exit(1)

    # Auto-load environment from arsenal/.env
    if not load_superpowers_env():
        sys.exit(1)

    # Override environment selection if --production flag is used
    if use_production:
        print("=" * 60)
        print("📍 PRODUCTION MODE - Fetching from PRODUCTION server")
        print("=" * 60)
        select_langfuse_environment("production")
    else:
        print("=" * 60)
        print("📍 STAGING MODE - Fetching from STAGING server (default)")
        print("=" * 60)
        select_langfuse_environment("staging")

    langfuse = get_langfuse()
    if not langfuse:
        sys.exit(1)

    print(f"\nFetching {prompt_name} version {version}...")
    fetch_prompt_version(langfuse, prompt_name, version)


if __name__ == "__main__":
    main()
