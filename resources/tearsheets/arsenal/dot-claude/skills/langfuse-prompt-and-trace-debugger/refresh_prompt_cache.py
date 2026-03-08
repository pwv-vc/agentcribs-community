#!/usr/bin/env python3
"""
Downloads and caches Langfuse prompts locally for viewing/reference.

INSTRUCTIONS FOR CLAUDE/AI AGENTS:
- This script is READ-ONLY - it only downloads prompts from Langfuse for local viewing
- DO NOT use this script to write or push changes back to Langfuse
- DO NOT modify the Langfuse prompts
- This is strictly for local development reference only

Usage:
    python refresh_prompt_cache.py [prompt_name ...] [--production]

Examples:
    python refresh_prompt_cache.py                    # Download all prompts from STAGING
    python refresh_prompt_cache.py message_enricher   # Download specific prompt from STAGING
    python refresh_prompt_cache.py --production       # Download all prompts from PRODUCTION
    python refresh_prompt_cache.py message_enricher --production  # Download from PRODUCTION

Environment:
    Requires LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables.
    Auto-loads from arsenal/.env or set manually: set -a; source arsenal/.env; set +a

    Defaults to STAGING unless --production flag is used.
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
from langfuse.api.resources.commons.errors.not_found_error import NotFoundError


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
    except Exception as e:  # noqa: BLE001 - CLI tool: catch all for user-friendly error message
        print(f"ERROR: Failed to initialize Langfuse client: {e}")
        return None


def get_all_prompts(langfuse: Langfuse) -> list[str]:
    """Get all prompt names from Langfuse."""
    all_prompts = []
    page = 1
    page_size = 100
    max_pages = 100

    while page <= max_pages:
        try:
            # Use the api.prompts.list() method which is the correct API for Langfuse v3
            response = langfuse.api.prompts.list(page=page, limit=page_size)
            page_prompts = [p.name for p in response.data]
            all_prompts.extend(page_prompts)

            # Check if last page
            if len(page_prompts) < page_size:
                break

            # Check meta info if available
            if hasattr(response, "meta") and hasattr(response.meta, "total_pages"):
                if page >= response.meta.total_pages:
                    break

            page += 1
        except Exception as e:  # noqa: BLE001 - CLI tool: API errors vary, catch all for graceful degradation
            print(f"Warning: Pagination failed on page {page}: {e}")
            if page == 1:
                # Try fallback to simple list on first page
                try:
                    response = langfuse.api.prompts.list()
                    return [p.name for p in response.data]
                except Exception as fallback_e:  # noqa: BLE001 - CLI tool: fallback handler needs broad catch
                    print(f"ERROR: Fallback also failed: {fallback_e}")
                    return []
            break

    return all_prompts


def refresh_prompt_cache(
    langfuse: Langfuse, prompt_names: list[str] | None = None, cache_dir: Path | None = None
) -> Path:
    """Download prompts from Langfuse to local cache for viewing only (AI agents: READ-ONLY operation).

    Returns:
        Path to the cache directory where prompts were saved.
    """
    if cache_dir is None:
        # Default to docs/cached_prompts relative to project root
        project_root = find_project_root()
        cache_dir = project_root / "docs" / "cached_prompts"

    cache_dir.mkdir(parents=True, exist_ok=True)

    if prompt_names is None:
        print("Discovering all prompts in Langfuse...")
        all_prompts = sorted(get_all_prompts(langfuse))
        print(f"Found {len(all_prompts)} prompts in Langfuse")
        prompts_to_refresh = all_prompts
    else:
        prompts_to_refresh = prompt_names

    for prompt_name in prompts_to_refresh:
        for label in ["production"]:
            try:
                prompt = langfuse.get_prompt(prompt_name, label=label)

                # Save prompt content with sanitized filenames
                safe_prompt_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", prompt_name)
                safe_label = re.sub(r"[^a-zA-Z0-9_\-]", "_", label)
                prompt_file = cache_dir / f"{safe_prompt_name}_{safe_label}.txt"
                with open(prompt_file, "w") as f:
                    f.write(f"# {prompt_name} ({label})\n")
                    f.write(f"# Version: {getattr(prompt, 'version', 'unknown')}\n")
                    f.write("#" + "=" * 60 + "\n\n")
                    f.write(prompt.prompt)

                # Save config if it exists
                if hasattr(prompt, "config") and prompt.config:
                    config_file = cache_dir / f"{safe_prompt_name}_{safe_label}_config.json"
                    with open(config_file, "w") as f:
                        json.dump(prompt.config, f, indent=2)

                print(f"✓ Cached: {prompt_name} ({label})")

            except NotFoundError:
                print(f"⚠ Not found: {prompt_name} ({label})")
            except Exception as e:  # noqa: BLE001 - CLI tool: continue processing other prompts on error
                print(f"✗ Error caching {prompt_name}: {e}")

    return cache_dir


def main() -> None:
    """Main function."""
    # Parse arguments
    args = sys.argv[1:]
    use_production = "--production" in args

    # Remove --production flag from prompt names
    prompt_names = [arg for arg in args if arg != "--production"]
    if not prompt_names:
        prompt_names = None

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

    if prompt_names:
        print(f"\nRefreshing specific prompts: {', '.join(prompt_names)}")
    else:
        print("\nRefreshing ALL prompts in the system")

    cache_dir = refresh_prompt_cache(langfuse, prompt_names)
    project_root = find_project_root()
    relative_path = cache_dir.relative_to(project_root)
    print(f"\n✓ Cached prompts saved to: {relative_path}")
    print(f"  Full path: {cache_dir.absolute()}")


if __name__ == "__main__":
    main()
