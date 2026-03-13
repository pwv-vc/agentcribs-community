#!/usr/bin/env python3
"""
Push prompts to Langfuse (staging or production).

SAFETY FEATURES:
- Defaults to STAGING (safe default)
- Production requires explicit --production flag
- Production requires confirmation prompt
- NEVER assigns labels (human-in-the-loop safety)
- Rejects placeholder credentials
- Provides URL to view result in Langfuse UI

Usage:
    python push_to_staging.py PROMPT_NAME [PROMPT_NAME2 ...] [--production] [-m "message"]

Examples:
    # Push to STAGING (default - safe):
    python push_to_staging.py message_enricher -m "Reorder conditions: timeout first, bot response second"
    python push_to_staging.py prompt1 prompt2 prompt3 -m "Add new detection rules"

    # Push with a commit message:
    python push_to_staging.py message_enricher -m "Reorder conditions: timeout first, bot response second"

    # Push to PRODUCTION (requires --production flag + confirmation):
    python push_to_staging.py message_enricher --production -m "Fix: prioritize timeout over bot response"

Environment:
    Staging: LANGFUSE_PUBLIC_KEY_STAGING, LANGFUSE_SECRET_KEY_STAGING, LANGFUSE_HOST_STAGING
    Production: LANGFUSE_PUBLIC_KEY_PROD, LANGFUSE_SECRET_KEY_PROD, LANGFUSE_HOST_PROD
    Auto-loads from arsenal/.env
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests

# Add current directory to path to import env_loader
sys.path.insert(0, str(Path(__file__).parent))
from env_loader import load_arsenal_env, find_project_root


def validate_credentials(environment: str = "staging") -> tuple[str, str, str] | None:
    """
    Validate that we have proper credentials for the specified environment.

    Args:
        environment: Either "staging" or "production"

    Returns:
        Tuple of (public_key, secret_key, host) if valid, None otherwise
    """
    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")
    host = os.environ.get("LANGFUSE_HOST")

    # Check all are present
    if not all([public_key, secret_key, host]):
        print(f"❌ ERROR: Missing required {environment} environment variables")
        if environment == "staging":
            print("  Required: LANGFUSE_PUBLIC_KEY_STAGING, LANGFUSE_SECRET_KEY_STAGING, LANGFUSE_HOST_STAGING")
        else:
            print("  Required: LANGFUSE_PUBLIC_KEY_PROD, LANGFUSE_SECRET_KEY_PROD, LANGFUSE_HOST_PROD")
        print("  Add them to arsenal/.env")
        return None

    # Check for placeholder values
    placeholder_patterns = [
        "your-key-here",
        "your-public-key",
        "your-secret-key",
        "your-staging-public-key",
        "your-staging-secret-key",
        "your-prod-public-key",
        "your-prod-secret-key",
        "your-instance.com",
    ]

    for pattern in placeholder_patterns:
        if pattern in public_key.lower() or pattern in secret_key.lower() or pattern in host.lower():
            print(f"❌ ERROR: Credentials contain placeholder value: {pattern}")
            print(f"  Replace placeholders in arsenal/.env with real {environment} credentials")
            return None

    # Validate host matches expected environment
    if environment == "staging" and "staging" not in host.lower():
        print(f"❌ ERROR: Host URL does not contain 'staging': {host}")
        print("  Expected format: https://langfuse.staging.your-instance.com")
        return None
    elif environment == "production" and "prod" not in host.lower():
        print(f"❌ ERROR: Host URL does not contain 'prod': {host}")
        print("  Expected format: https://langfuse.prod.your-instance.com")
        return None

    # Validate key formats
    if not public_key.startswith("pk-lf-"):
        print(f"❌ ERROR: Invalid public key format: {public_key}")
        print("  Expected format: pk-lf-...")
        return None

    if not secret_key.startswith("sk-lf-"):
        print(f"❌ ERROR: Invalid secret key format: {secret_key}")
        print("  Expected format: sk-lf-...")
        return None

    print(f"✓ Validated {environment} credentials for: {host}")
    return public_key, secret_key, host


def fetch_existing_tags(prompt_name: str, public_key: str, secret_key: str, host: str) -> list[str]:
    """
    Fetch existing tags for a prompt from Langfuse.

    Returns:
        List of existing tags, or empty list if prompt doesn't exist
    """
    url = f"{host}/api/public/v2/prompts"
    response = requests.get(
        url,
        params={"name": prompt_name},
        auth=(public_key, secret_key),
        headers={"Content-Type": "application/json"},
        timeout=30,
    )

    if response.status_code == 200:
        data = response.json()
        prompts = data.get("data", [])
        for prompt in prompts:
            if prompt.get("name") == prompt_name:
                tags = prompt.get("tags", [])
                if tags:
                    print(f"  Found existing tags: {tags}")
                return tags
    return []


def read_prompt_from_cache(prompt_name: str, cache_dir: Path) -> dict | None:
    """
    Read prompt content and config from cached files.

    Returns:
        Dict with 'prompt' and optional 'config', or None if files not found
    """
    # Sanitize filename
    safe_prompt_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", prompt_name)

    # Read prompt text
    prompt_file = cache_dir / f"{safe_prompt_name}_production.txt"
    if not prompt_file.exists():
        print(f"❌ ERROR: Prompt file not found: {prompt_file}")
        print(f"  Expected: {prompt_file.relative_to(find_project_root())}")
        print("\nCreate it manually or fetch from Langfuse using:")
        print("  cd .claude/skills/langfuse-prompt-and-trace-debugger")
        print(f"  uv run python refresh_prompt_cache.py {prompt_name}")
        return None

    with open(prompt_file) as f:
        lines = f.readlines()

    # Skip ONLY the file header comments at the top (e.g., "# prompt_name (production)", "# Version: X")
    # But PRESERVE markdown headers like "### RULES" or "#### 1. **fact**"
    prompt_lines = []
    in_header = True
    for line in lines:
        stripped = line.strip()
        # File header comments start with "# " (single #) and are at the top
        # Markdown headers start with "##" or more
        if in_header and stripped.startswith("#") and not stripped.startswith("##"):
            # Skip file header comments (single # at start of file)
            continue
        else:
            in_header = False
            prompt_lines.append(line)
    prompt_text = "".join(prompt_lines).strip()

    result = {"prompt": prompt_text}

    # Read config if exists
    config_file = cache_dir / f"{safe_prompt_name}_production_config.json"
    if config_file.exists():
        with open(config_file) as f:
            result["config"] = json.load(f)

    return result


def push_prompt(
    prompt_name: str, prompt_data: dict, public_key: str, secret_key: str, host: str, environment: str = "staging", commit_message: str | None = None, existing_tags: list[str] | None = None
) -> dict | None:
    """
    Push prompt to Langfuse via API.

    Args:
        prompt_name: Name of the prompt
        prompt_data: Dict containing 'prompt' text and optional 'config'
        public_key: Langfuse public key
        secret_key: Langfuse secret key
        host: Langfuse host URL
        environment: "staging" or "production" (for logging only)
        commit_message: Optional commit message for the version
        existing_tags: Existing tags to preserve (merged with 'pushed-from-cli')

    Returns:
        Response data if successful, None otherwise
    """
    url = f"{host}/api/public/v2/prompts"

    # Determine prompt type from content
    prompt_content = prompt_data["prompt"]
    prompt_type = "text"  # Default to text

    # Build request payload
    # CRITICAL SAFETY: DO NOT assign ANY labels!
    # Without a label, the prompt won't be selected by the system (which looks for "production" label)
    # This acts as a human-in-the-loop safety control - humans must manually add labels in Langfuse UI
    payload = {
        "name": prompt_name,
        "type": prompt_type,
        "prompt": prompt_content,
        # "labels": [],  # NEVER set labels - human must assign in Langfuse UI
        "tags": list(set((existing_tags or []) + ["pushed-from-cli"])),
        "commitMessage": commit_message if commit_message else f"Updated from CLI at {datetime.now().isoformat()}",
    }

    # Add config if present
    if "config" in prompt_data:
        payload["config"] = prompt_data["config"]

    env_emoji = "🚨" if environment == "production" else "📤"
    print(f"\n{env_emoji} Pushing '{prompt_name}' to {environment.upper()}...")
    print(f"  Host: {host}")
    print(f"  Type: {prompt_type}")
    if "config" in payload:
        print(f"  Config: {json.dumps(payload['config'], indent=2)}")

    # Make API request
    try:
        response = requests.post(
            url,
            json=payload,
            auth=(public_key, secret_key),
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code in [200, 201]:
            result = response.json()
            env_indicator = "🚨 PRODUCTION" if environment == "production" else "STAGING"
            print(f"\n✅ Successfully pushed prompt to {env_indicator}!")
            print(f"  Prompt Name: {result.get('name')}")
            print(f"  Version: {result.get('version')}")
            print(f"  Labels: {result.get('labels', [])} (NO LABELS - human must assign in UI)")
            print(f"  Prompt ID: {result.get('id')}")
            print("\n⚠️  IMPORTANT: This prompt has NO LABEL and will NOT be used by the system")
            print("  A human must manually add a label in the Langfuse UI to activate it")

            # Extract project ID from response to build URL
            project_id = result.get("projectId")
            if project_id:
                langfuse_url = f"{host}/project/{project_id}/prompts/{prompt_name}"
                print(f"\n🔗 View in Langfuse: {langfuse_url}")

            return result
        else:
            print(f"\n❌ Failed to push prompt")
            print(f"  Status: {response.status_code}")
            print(f"  Error: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return None


def main() -> None:
    """Main function."""
    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    # Check for production flag
    use_production = "--production" in sys.argv

    # Parse -m/--message flag
    commit_message = None
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg in ("-m", "--message") and i + 1 < len(args):
            commit_message = args[i + 1]
            break

    # Remove flags and their values from arguments to get prompt names
    prompt_names = []
    skip_next = False
    for arg in args:
        if skip_next:
            skip_next = False
            continue
        if arg in ("-m", "--message"):
            skip_next = True
            continue
        if not arg.startswith("--"):
            prompt_names.append(arg)

    if not prompt_names:
        print("❌ ERROR: No prompt names provided")
        print(__doc__)
        sys.exit(1)

    # Determine environment
    environment = "production" if use_production else "staging"

    # Show what we're doing
    if use_production:
        print("\n" + "=" * 60)
        print("⚠️  PRODUCTION MODE - PUSHING TO PRODUCTION SERVER")
        print("=" * 60)
        print(f"\n🚨 You are about to push {len(prompt_names)} prompt(s) to PRODUCTION:")
        for name in prompt_names:
            print(f"  • {name}")
        print("\n⚠️  These prompts will be created WITHOUT LABELS")
        print("  → A human must manually add labels in Langfuse UI to activate them")
        print("\nAre you ABSOLUTELY SURE you want to push to PRODUCTION?")

        response = input("Type 'yes' to confirm, anything else to abort: ").strip().lower()
        if response != "yes":
            print("\n❌ Aborted - not pushing to production")
            sys.exit(0)
        print("\n✓ Confirmed - proceeding with production push...")
    else:
        print("\n🔒 STAGING MODE (default - safe)")
        print(f"  Pushing {len(prompt_names)} prompt(s) to staging server")

    # Load environment
    print(f"\n🔒 Loading {environment.upper()} credentials...")
    if not load_arsenal_env():
        sys.exit(1)

    # Override with environment-specific credentials
    if environment == "staging":
        os.environ["LANGFUSE_PUBLIC_KEY"] = os.environ.get("LANGFUSE_PUBLIC_KEY_STAGING", "")
        os.environ["LANGFUSE_SECRET_KEY"] = os.environ.get("LANGFUSE_SECRET_KEY_STAGING", "")
        os.environ["LANGFUSE_HOST"] = os.environ.get("LANGFUSE_HOST_STAGING", "")
    else:  # production
        os.environ["LANGFUSE_PUBLIC_KEY"] = os.environ.get("LANGFUSE_PUBLIC_KEY_PROD", "")
        os.environ["LANGFUSE_SECRET_KEY"] = os.environ.get("LANGFUSE_SECRET_KEY_PROD", "")
        os.environ["LANGFUSE_HOST"] = os.environ.get("LANGFUSE_HOST_PROD", "")

    # Validate credentials
    credentials = validate_credentials(environment)
    if not credentials:
        sys.exit(1)

    public_key, secret_key, host = credentials

    print(f"\n📋 Prompts to push: {', '.join(prompt_names)}")

    # Find cache directory
    project_root = find_project_root()
    cache_dir = project_root / "docs" / "cached_prompts"

    if not cache_dir.exists():
        print(f"\n❌ ERROR: Cache directory not found: {cache_dir}")
        print("\nCreate it with:")
        print("  mkdir -p docs/cached_prompts")
        sys.exit(1)

    print(f"\n📁 Reading prompts from: {cache_dir.relative_to(project_root)}")

    # Process each prompt
    success_count = 0
    for prompt_name in prompt_names:
        print(f"\n{'='*60}")
        print(f"Processing: {prompt_name}")
        print('='*60)

        # Read prompt data
        prompt_data = read_prompt_from_cache(prompt_name, cache_dir)
        if not prompt_data:
            continue

        # Fetch existing tags to preserve them
        existing_tags = fetch_existing_tags(prompt_name, public_key, secret_key, host)

        # Push to environment (staging or production)
        result = push_prompt(prompt_name, prompt_data, public_key, secret_key, host, environment, commit_message, existing_tags)
        if result:
            success_count += 1

    # Summary
    print(f"\n{'='*60}")
    env_indicator = "🚨 PRODUCTION" if environment == "production" else "STAGING"
    print(f"Summary: {success_count}/{len(prompt_names)} prompts pushed to {env_indicator} successfully")
    print('='*60)

    if success_count < len(prompt_names):
        sys.exit(1)


if __name__ == "__main__":
    main()
