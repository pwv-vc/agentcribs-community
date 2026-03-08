# Langfuse Prompt & Trace Debugger - Standalone Skill

Fully standalone scripts for debugging Langfuse prompts and traces with automatic environment loading.

## ✅ Features

- **Fully Portable**: Works in ANY project with Langfuse - not tied to this repository
- **Standalone**: Own virtual environment with pinned dependencies (langfuse==2.60.3, httpx==0.27.2)
- **Flexible Configuration**:
  - Auto-loads from `arsenal/.env` if present
  - Falls back to standard environment variables
  - Works with manual `export` commands
- **No manual setup needed**: Just configure credentials once and run
- **Six powerful tools**:
  - `check_prompts.py` - List all prompts
  - `refresh_prompt_cache.py` - Download prompts locally
  - `fetch_trace.py` - View and debug individual traces
  - `fetch_error_traces.py` - Find traces with errors from time range
  - `search_trace_errors.py` - Search traces for specific error messages
  - `fetch_filtered_prompts.py` - Fetch prompts with filters

## 🚀 Quick Start

### 1. One-time setup

**Option A: Using `arsenal/.env` (recommended if using with arsenal)**
```bash
# Add to arsenal/.env:
LANGFUSE_PUBLIC_KEY=pk-lf-your-key  # pragma: allowlist-secret
LANGFUSE_SECRET_KEY=sk-lf-your-key  # pragma: allowlist-secret
LANGFUSE_HOST=https://your-langfuse-host.com
ENVIRONMENT=production
```

**Option B: Using environment variables (works anywhere)**
```bash
export LANGFUSE_PUBLIC_KEY=pk-lf-your-key
export LANGFUSE_SECRET_KEY=sk-lf-your-key
export LANGFUSE_HOST=https://your-langfuse-host.com
export ENVIRONMENT=production
```

**Option C: Using shell config (permanent)**
```bash
# Add to ~/.bashrc or ~/.zshrc:
export LANGFUSE_PUBLIC_KEY=pk-lf-your-key
export LANGFUSE_SECRET_KEY=sk-lf-your-key
export LANGFUSE_HOST=https://your-langfuse-host.com
```

### 2. Use the scripts

```bash
cd .claude/skills/langfuse-prompt-and-trace-debugger

# List all prompts
uv run python check_prompts.py

# Download a specific prompt
uv run python refresh_prompt_cache.py voice_message_enricher

# List recent traces
uv run python fetch_trace.py --list --limit 5

# View specific trace
uv run python fetch_trace.py <trace-id>
```

## 🔧 How It Works

The scripts use `env_loader.py` to automatically:
1. Find the `arsenal/` directory by searching up from the current location
2. Load `arsenal/.env` and parse environment variables
3. Strip inline comments (like `# pragma: allowlist-secret`)
4. Make credentials available to the Langfuse SDK

No manual `source` commands needed!

## 📝 Full Documentation

See [SKILL.md](./SKILL.md) for complete documentation including:
- Detailed usage examples
- Debugging workflows
- Understanding prompt configurations
- All available options

## ✨ Fixed Issues

- **Inline comment parsing**: Correctly strips `# pragma: allowlist-secret` from values
- **Version compatibility**: Uses exact versions (langfuse 2.60.3, httpx 0.27.2) that work with the API
- **Automatic path resolution**: Finds project root and `arsenal/.env` from any directory
