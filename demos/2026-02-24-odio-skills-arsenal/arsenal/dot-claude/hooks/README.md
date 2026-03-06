# Superpowers Hooks

This directory contains hook scripts that are automatically installed by the superpowers install script.

## SessionStart Hook

The `session_start.py` hook mechanically injects the getting-started skill into every Claude Code session.

### How It Works

1. **Hook Installation**: The `install.sh` script copies this hook to `.claude/hooks/session_start.py`
2. **Hook Configuration**: The hook is registered in `.claude/settings.json`:
   ```json
   {
     "hooks": {
       "SessionStart": [
         {
           "type": "command",
           "command": "python3 .claude/hooks/session_start.py"
         }
       ]
     }
   }
   ```
3. **Automatic Execution**: When a new Claude Code session starts, the hook runs automatically
4. **Content Injection**: The hook reads `.claude/skills/getting-started/SKILL.md` and prints it to stdout
5. **Context Loading**: Claude Code captures the output and includes it in the session context

### Why This Matters

**Problem**: Relying on LLM choice for bootstrap compliance is unreliable (~70% adherence)

**Solution**: Mechanical injection removes the decision point entirely (~95%+ adherence)

The getting-started skill content is automatically loaded into every session, ensuring agents:
- Know about available skills from the start
- Understand the three foundational rules
- Have the mandatory workflow documented
- Cannot "forget" to read the bootstrap documentation

### Defense-in-Depth Architecture

The SessionStart hook is part of a multi-layer compliance system:

1. **Layer 1: Mechanical Injection (This Hook)**
   - Ensures content is in context (cannot be skipped)
   - Token-efficient (only 230 lines)
   - Runs automatically before agent responds

2. **Layer 2: Validation Requirements (session-start-hook in CLAUDE.md/AGENTS.md)**
   - Requires proof-of-processing (list the three rules)
   - Forces tool use (`ls .claude/skills/`)
   - Exact format priming

3. **Layer 3: Persuasion Principles**
   - Safety-critical system framing
   - Visual anchors (ASCII boxes)
   - Negative priming (anti-patterns)
   - Semantic anchoring (pre-flight checklist)

### Testing the Hook

```bash
# Run the hook manually to see output
python3 .claude/hooks/session_start.py

# Expected output:
# ╔══════════════════════════════════════════════════════════╗
# ║   📋 SESSION BOOTSTRAP: getting-started skill loaded     ║
# ║   File size: 229 lines                                   ║
# ╚══════════════════════════════════════════════════════════╝
#
# [Full content of getting-started/SKILL.md]
#
# --- End of getting-started skill (229 lines) ---
```

### Maintenance

When updating the hook:
1. Edit `superpowers/hooks/session_start.py`
2. Run `./superpowers/install.sh` to copy to `.claude/hooks/`
3. Test with a new Claude Code session

### Design Principles

1. **Token Efficiency**: Only inject getting-started (not all docs)
2. **Fail Visible**: Exit with error if skill file not found
3. **Clear Feedback**: Visual formatting shows injection happened
4. **Zero Configuration**: Automatically set up by install script
5. **No Dependencies**: Pure Python 3 with stdlib only

## Adding New Hooks

To add additional hooks:

1. Create hook script in `superpowers/hooks/your_hook.py`
2. Make it executable: `chmod +x superpowers/hooks/your_hook.py`
3. Add installation logic to `superpowers/install.sh`
4. Update `.claude/settings.json` to register the hook
5. Document in this README

Available hook types in Claude Code:
- `SessionStart`: Runs when a new session starts
- `UserPromptSubmit`: Runs before user input is processed
- More types may be added in future Claude Code versions
