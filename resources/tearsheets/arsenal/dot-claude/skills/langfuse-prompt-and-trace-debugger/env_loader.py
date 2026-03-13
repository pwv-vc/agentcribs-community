#!/usr/bin/env python3
"""
Automatic environment loader for langfuse-prompt-and-trace-debugger skill.
Finds and loads arsenal/.env automatically.
"""

import os
from pathlib import Path


def find_arsenal_dir() -> Path | None:
    """
    Find the arsenal directory by searching up from current directory.

    Returns:
        Path to arsenal directory, or None if not found
    """
    current = Path.cwd()

    # First check if we're already in arsenal or its subdirectories
    if current.name == "arsenal":
        return current

    # Check if arsenal is a sibling or parent
    for parent in [current, *current.parents]:
        arsenal = parent / "arsenal"
        if arsenal.is_dir() and (arsenal / ".env").exists():
            return arsenal

    return None


def load_arsenal_env() -> bool:
    """
    Automatically find and load arsenal/.env file, or use existing environment variables.

    Returns:
        True if environment is available (either loaded or already set), False otherwise
    """
    # Check if required variables are already set in environment
    required_vars = ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
    already_set = all(os.environ.get(var) for var in required_vars)

    if already_set:
        print("✓ Using existing environment variables")
        return True

    # Try to find and load arsenal/.env
    arsenal = find_arsenal_dir()

    if not arsenal:
        print("⚠ Could not find arsenal/.env")
        print(f"\nSearched from: {Path.cwd()}")
        print("\nTo use this skill, either:")
        print("  1. Create arsenal/.env with Langfuse credentials:")
        print("     LANGFUSE_PUBLIC_KEY=pk-lf-...")
        print("     LANGFUSE_SECRET_KEY=sk-lf-...")
        print("     LANGFUSE_HOST=https://your-instance.com")
        print("\n  2. Or set environment variables manually:")
        print("     export LANGFUSE_PUBLIC_KEY=pk-lf-...")
        print("     export LANGFUSE_SECRET_KEY=sk-lf-...")
        print("     export LANGFUSE_HOST=https://your-instance.com")
        return False

    env_file = arsenal / ".env"

    if not env_file.exists():
        print(f"⚠ {env_file} not found")
        print("\nCreate it with:")
        print(f"  cp {arsenal}/.env.example {env_file}")
        print("  # Then edit with your Langfuse credentials")
        print("\nOr set environment variables manually (see above)")
        return False

    # Load environment variables from file
    try:
        loaded_count = 0
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                # Parse key=value
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove inline comments (anything after #)
                    if "#" in value:
                        value = value.split("#")[0].strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Only set if not empty
                    if value:
                        os.environ[key] = value
                        loaded_count += 1

        # Select the right Langfuse environment based on LANGFUSE_ENVIRONMENT
        select_langfuse_environment()

        print(f"✓ Loaded {loaded_count} variables from: {env_file}")
        return True

    except Exception as e:
        print(f"ERROR: Failed to load {env_file}: {e}")
        return False


def select_langfuse_environment(env: str | None = None) -> None:
    """
    Select Langfuse credentials based on LANGFUSE_ENVIRONMENT variable.

    Args:
        env: Override environment (staging or production). If None, uses LANGFUSE_ENVIRONMENT variable.
    """
    # Determine which environment to use
    target_env = env or os.environ.get("LANGFUSE_ENVIRONMENT", "staging")
    target_env = target_env.lower()

    # Map to correct suffix
    if target_env in ["prod", "production"]:
        suffix = "PROD"
        env_name = "production"
    else:
        suffix = "STAGING"
        env_name = "staging"

    # Set the base Langfuse variables from environment-specific ones
    for key in ["PUBLIC_KEY", "SECRET_KEY", "HOST"]:
        env_var = f"LANGFUSE_{key}_{suffix}"
        if env_var in os.environ:
            os.environ[f"LANGFUSE_{key}"] = os.environ[env_var]

    # Print which environment is being used
    if os.environ.get("LANGFUSE_HOST"):
        print(f"  Using Langfuse {env_name} environment: {os.environ['LANGFUSE_HOST']}")


def find_project_root() -> Path:
    """
    Find the project root directory (parent of arsenal).

    Returns:
        Path to project root
    """
    arsenal = find_arsenal_dir()
    if arsenal:
        return arsenal.parent
    return Path.cwd()


# Legacy aliases for backward compatibility
find_superpowers_dir = find_arsenal_dir
load_superpowers_env = load_arsenal_env
