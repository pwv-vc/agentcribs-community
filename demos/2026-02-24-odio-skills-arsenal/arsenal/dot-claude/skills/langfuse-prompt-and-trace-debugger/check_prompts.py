#!/usr/bin/env python3
"""
CLI script to check status of all prompts in Langfuse.

INSTRUCTIONS FOR CLAUDE/AI AGENTS:
- This script is READ-ONLY - it only verifies prompt existence in Langfuse
- DO NOT use this script to modify or push changes to Langfuse prompts
- DO NOT create or update prompts
- This is strictly a verification tool for local development

This script lists all prompts from Langfuse and shows their status
in the current environment with colored indicators.

Environment:
    Requires LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables.
    Optional: ENVIRONMENT (defaults to "production")
    Load with: set -a; source superpowers/.env; set +a
"""

import os
import sys
from pathlib import Path

# Add current directory to path to import env_loader
sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_superpowers_env

from langfuse import Langfuse
from langfuse.api.resources.commons.errors.not_found_error import NotFoundError


# Color codes for terminal output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


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
        except Exception as e:
            print(f"Warning: Pagination failed on page {page}: {e}")
            if page == 1:
                # Try fallback to simple list on first page
                try:
                    response = langfuse.api.prompts.list()
                    return [p.name for p in response.data]
                except Exception as fallback_e:
                    print(f"ERROR: Fallback also failed: {fallback_e}")
                    return []
            break

    return all_prompts


def check_prompt_exists(langfuse: Langfuse, prompt_type: str, environment: str) -> tuple[bool, str]:
    """
    Check if a prompt exists in Langfuse for the current environment only.

    Args:
        langfuse: Langfuse client
        prompt_type: The prompt type to check
        environment: Label to check (e.g., "production", "staging")

    Returns:
        Tuple of (exists, environment) where environment is the label where it was found
    """
    try:
        langfuse.get_prompt(prompt_type, label=environment, cache_ttl_seconds=0)
        return True, environment
    except NotFoundError:
        return False, "none"


def print_prompt_status(prompt_type: str, exists: bool, environment: str = "") -> None:
    """Print the status of a prompt with colored indicators."""
    if exists:
        indicator = f"{Colors.GREEN}✓{Colors.RESET}"
        env_info = f" ({environment})" if environment else ""
        print(f"{indicator} {Colors.WHITE}{prompt_type}{Colors.RESET}{env_info}")
    else:
        indicator = f"{Colors.RED}✗{Colors.RESET}"
        print(f"{indicator} {Colors.WHITE}{prompt_type}{Colors.RESET} - {Colors.RED}NOT FOUND{Colors.RESET}")


def main() -> None:
    """Main function to check all prompts."""
    # Auto-load environment from superpowers/.env
    if not load_superpowers_env():
        sys.exit(1)

    langfuse = get_langfuse()
    if not langfuse:
        sys.exit(1)

    env = os.environ.get("ENVIRONMENT", "production").lower()

    print(f"{Colors.BOLD}Checking All Langfuse Prompts{Colors.RESET}")
    print(f"Environment: {Colors.WHITE}{env}{Colors.RESET}")
    print("=" * 50)

    # Get all prompts from Langfuse
    try:
        all_prompts = get_all_prompts(langfuse)
        print(f"Found {len(all_prompts)} total prompts in Langfuse\n")
    except Exception as e:
        print(f"{Colors.RED}Failed to fetch prompts from Langfuse: {e}{Colors.RESET}")
        sys.exit(1)

    # Track statistics
    total_prompts = len(all_prompts)
    found_prompts = 0

    # Check each prompt's availability in current environment
    print(f"{Colors.BOLD}All Prompts in Langfuse ({total_prompts} total):{Colors.RESET}")
    for prompt_name in sorted(all_prompts):
        exists, environment = check_prompt_exists(langfuse, prompt_name, env)
        print_prompt_status(prompt_name, exists, environment)
        if exists:
            found_prompts += 1

    # Print summary
    print("\n" + "=" * 50)
    print(f"{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"Total prompts in Langfuse: {Colors.WHITE}{total_prompts}{Colors.RESET}")
    print(f"Available in {env}: {Colors.GREEN}{found_prompts}{Colors.RESET}")
    print(f"Missing from {env}: {Colors.RED}{total_prompts - found_prompts}{Colors.RESET}")

    if found_prompts == total_prompts:
        print(f"\n{Colors.GREEN}✓ All prompts available in {env}!{Colors.RESET}")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}✗ {total_prompts - found_prompts} prompts missing from {env}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
