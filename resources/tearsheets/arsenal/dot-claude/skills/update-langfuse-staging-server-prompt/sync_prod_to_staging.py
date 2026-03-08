#!/usr/bin/env python3
"""
Sync production Langfuse server prompts to staging Langfuse server.

This script:
1. Connects to PRODUCTION Langfuse server (READ-ONLY)
2. Fetches all prompts with "production" label
3. Pushes them to STAGING Langfuse server
4. Tags them appropriately on staging

SAFETY FEATURES:
- READ-ONLY access to production server
- Validates both server credentials separately
- Requires confirmation before syncing
- Shows diff of what will be synced

Usage:
    python sync_prod_to_staging.py [--prompt PROMPT_NAME] [--yes]

Examples:
    python sync_prod_to_staging.py                    # Sync all production prompts (with confirmation)
    python sync_prod_to_staging.py --prompt message_enricher  # Sync specific prompt
    python sync_prod_to_staging.py --yes              # Skip confirmation (automation)

Environment:
    Requires both production and staging credentials in arsenal/.env:
    - LANGFUSE_PUBLIC_KEY_PROD / LANGFUSE_SECRET_KEY_PROD / LANGFUSE_HOST_PROD
    - LANGFUSE_PUBLIC_KEY_STAGING / LANGFUSE_SECRET_KEY_STAGING / LANGFUSE_HOST_STAGING
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

# Add current directory to path to import env_loader
sys.path.insert(0, str(Path(__file__).parent))
from env_loader import find_arsenal_dir, find_project_root


def load_env_file(env_file: Path) -> dict[str, str]:
    """Load environment variables from file into a dict."""
    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Remove inline comments
                if "#" in value:
                    value = value.split("#")[0].strip()

                # Remove quotes
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                if value:
                    env_vars[key] = value
    return env_vars


def validate_credentials(env_vars: dict, server_type: str) -> tuple[str, str, str] | None:
    """
    Validate credentials for a specific server type (PROD or STAGING).

    Returns:
        Tuple of (public_key, secret_key, host) if valid, None otherwise
    """
    public_key = env_vars.get(f"LANGFUSE_PUBLIC_KEY_{server_type}")
    secret_key = env_vars.get(f"LANGFUSE_SECRET_KEY_{server_type}")
    host = env_vars.get(f"LANGFUSE_HOST_{server_type}")

    if not all([public_key, secret_key, host]):
        print(f"❌ ERROR: Missing {server_type} credentials")
        print(f"  Required: LANGFUSE_PUBLIC_KEY_{server_type}, LANGFUSE_SECRET_KEY_{server_type}, LANGFUSE_HOST_{server_type}")
        return None

    # Check for placeholder values
    placeholder_patterns = ["your-key-here", "your-public-key", "your-secret-key", "your-instance.com"]
    for pattern in placeholder_patterns:
        if pattern in public_key.lower() or pattern in secret_key.lower() or pattern in host.lower():
            print(f"❌ ERROR: {server_type} credentials contain placeholder: {pattern}")
            return None

    # Validate key formats
    if not public_key.startswith("pk-lf-"):
        print(f"❌ ERROR: Invalid {server_type} public key format: {public_key}")
        return None

    if not secret_key.startswith("sk-lf-"):
        print(f"❌ ERROR: Invalid {server_type} secret key format: {secret_key}")
        return None

    # Validate server type in host
    expected_in_host = server_type.lower()
    if expected_in_host not in host.lower():
        print(f"❌ ERROR: {server_type} host URL doesn't contain '{expected_in_host}': {host}")
        return None

    print(f"✓ Validated {server_type} credentials: {host}")
    return public_key, secret_key, host


def get_all_prompts(public_key: str, secret_key: str, host: str, label: str = "production") -> list[dict]:
    """
    Fetch all prompts with a specific label from Langfuse server.

    Returns:
        List of prompt dictionaries
    """
    url = f"{host}/api/public/v2/prompts"
    all_prompts = []
    page = 1
    page_size = 100

    print(f"\n📥 Fetching prompts from {host}...")

    while True:
        try:
            response = requests.get(
                url,
                params={"page": page, "limit": page_size},
                auth=(public_key, secret_key),
                timeout=30,
            )

            if response.status_code != 200:
                print(f"❌ Failed to fetch prompts: {response.status_code} {response.text}")
                break

            data = response.json()
            prompts = data.get("data", [])

            if not prompts:
                break

            # Filter by label
            for prompt in prompts:
                if label in prompt.get("labels", []):
                    all_prompts.append(prompt)

            # Check if more pages
            if len(prompts) < page_size:
                break

            page += 1

        except Exception as e:
            print(f"❌ Error fetching prompts: {e}")
            break

    print(f"  Found {len(all_prompts)} prompts with '{label}' label")
    return all_prompts


def push_prompt_to_server(
    prompt_name: str, prompt_content: str, config: dict | None, public_key: str, secret_key: str, host: str
) -> dict | None:
    """
    Push a prompt to a Langfuse server.

    Returns:
        Response data if successful, None otherwise
    """
    url = f"{host}/api/public/v2/prompts"

    # CRITICAL SAFETY: DO NOT assign ANY labels!
    # Without a label, the prompt won't be selected by the system (which looks for "production" label)
    # This acts as a human-in-the-loop safety control - humans must manually add labels in Langfuse UI
    payload = {
        "name": prompt_name,
        "type": "text",  # Default to text, could be enhanced to detect chat type
        "prompt": prompt_content,
        # "labels": [],  # NEVER set labels - human must assign in Langfuse UI
        "tags": ["auto-synced", "synced-from-prod"],
        "commitMessage": f"Synced from production server at {datetime.now().isoformat()}",
    }

    if config:
        payload["config"] = config

    try:
        response = requests.post(
            url, json=payload, auth=(public_key, secret_key), headers={"Content-Type": "application/json"}, timeout=30
        )

        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"  ❌ Failed: {response.status_code} {response.text}")
            return None

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def sync_prompts(
    prod_creds: tuple, staging_creds: tuple, prompt_filter: str | None = None, auto_confirm: bool = False
) -> None:
    """
    Main sync function.

    Args:
        prod_creds: (public_key, secret_key, host) for production
        staging_creds: (public_key, secret_key, host) for staging
        prompt_filter: Optional specific prompt name to sync
        auto_confirm: Skip confirmation prompts
    """
    prod_public, prod_secret, prod_host = prod_creds
    staging_public, staging_secret, staging_host = staging_creds

    # Fetch production prompts
    print("\n" + "=" * 60)
    print("STEP 1: Fetching production prompts")
    print("=" * 60)

    prod_prompts = get_all_prompts(prod_public, prod_secret, prod_host, label="production")

    if not prod_prompts:
        print("\n❌ No production prompts found to sync")
        return

    # Filter if specific prompt requested
    if prompt_filter:
        prod_prompts = [p for p in prod_prompts if p["name"] == prompt_filter]
        if not prod_prompts:
            print(f"\n❌ Prompt '{prompt_filter}' not found in production")
            return

    # Show what will be synced
    print("\n" + "=" * 60)
    print("STEP 2: Preview changes")
    print("=" * 60)
    print(f"\nWill sync {len(prod_prompts)} prompt(s) from production → staging:\n")

    for prompt in prod_prompts:
        print(f"  • {prompt['name']}")
        print(f"    Version: {prompt.get('version', 'unknown')}")
        print(f"    Labels: {prompt.get('labels', [])}")
        print()

    # Confirm unless auto-confirm
    if not auto_confirm:
        print("=" * 60)
        response = input("Proceed with sync? [y/N]: ")
        if response.lower() != "y":
            print("❌ Sync cancelled")
            return

    # Sync each prompt
    print("\n" + "=" * 60)
    print("STEP 3: Syncing prompts to staging")
    print("=" * 60)

    success_count = 0
    for prompt in prod_prompts:
        print(f"\n📤 Syncing: {prompt['name']}")

        result = push_prompt_to_server(
            prompt["name"],
            prompt["prompt"],
            prompt.get("config"),
            staging_public,
            staging_secret,
            staging_host,
        )

        if result:
            print(f"  ✅ Success! Version {result.get('version')} created on staging")
            print(f"  ⚠️  NO LABEL ASSIGNED - human must add label in UI to activate")
            # Extract project ID to build URL
            project_id = result.get("projectId")
            if project_id:
                url = f"{staging_host}/project/{project_id}/prompts/{prompt['name']}"
                print(f"  🔗 View: {url}")
            success_count += 1
        else:
            print(f"  ❌ Failed to sync {prompt['name']}")

    # Summary
    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"✅ Successfully synced: {success_count}/{len(prod_prompts)} prompts")
    print("\n⚠️  IMPORTANT: All prompts were created WITHOUT LABELS")
    print("  → These prompts will NOT be used by the system until labeled")
    print("  → A human must manually add labels in the Langfuse UI")
    print("  → This is a safety control to prevent untested prompts from being used")
    print("=" * 60)


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Sync production Langfuse prompts to staging server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--prompt", help="Sync specific prompt by name (default: sync all)")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompts")

    args = parser.parse_args()

    print("🔄 Langfuse Production → Staging Sync")
    print("=" * 60)

    # Load environment
    arsenal = find_arsenal_dir()
    if not arsenal:
        print("❌ Could not find arsenal/.env")
        sys.exit(1)

    env_file = arsenal / ".env"
    if not env_file.exists():
        print(f"❌ {env_file} not found")
        sys.exit(1)

    env_vars = load_env_file(env_file)

    # Validate credentials for both servers
    print("\n📋 Validating credentials...")
    prod_creds = validate_credentials(env_vars, "PROD")
    staging_creds = validate_credentials(env_vars, "STAGING")

    if not prod_creds or not staging_creds:
        print("\n❌ Credential validation failed")
        print("\nEnsure arsenal/.env has both production and staging credentials:")
        print("  LANGFUSE_PUBLIC_KEY_PROD=pk-lf-...")
        print("  LANGFUSE_SECRET_KEY_PROD=sk-lf-...")
        print("  LANGFUSE_HOST_PROD=https://langfuse.prod.cncorp.io")
        print("")
        print("  LANGFUSE_PUBLIC_KEY_STAGING=pk-lf-...")
        print("  LANGFUSE_SECRET_KEY_STAGING=sk-lf-...")
        print("  LANGFUSE_HOST_STAGING=https://langfuse.staging.cncorp.io")
        sys.exit(1)

    # Perform sync
    sync_prompts(prod_creds, staging_creds, prompt_filter=args.prompt, auto_confirm=args.yes)


if __name__ == "__main__":
    main()
