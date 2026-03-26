# Multi-Agent Workflows in Pi - A Primer

> **Context:** This doc shows how [Pi](https://github.com/mariozechner/pi-coding-agent), an open-source coding agent harness, approaches multi-model review and agentic workflows. Written by Gilman (Rho Impact, PWV portco) based on months of daily production use in [GalexC](https://github.com/callsen/galexc-net), a personal AI lab for infrastructure and agentic workflows. The `multi-model-review` skill in this repo is a Claude Code-native distillation of these patterns. If there's interest, we can flesh out any section into a full tearsheet.

## The Core Idea

Arsenal gives Claude Code superpowers through skills and commands. Pi takes a similar philosophy but adds a runtime layer that can **cast ephemeral agents** from different model providers and run **structured debates** between them. Instead of Claude orchestrating a Codex CLI subprocess, Pi's forge tools let you spin up multiple models as first-class participants in a shared workflow.

Three primitives, one foundation:

| Primitive | What it does | Arsenal equivalent |
|-----------|-------------|-------------------|
| **Skills** | Reusable methodology (WHAT to do) | Skills (`.claude/skills/`) |
| **Agents** | Persona definitions (WHO does it) | Agents (`.claude/agents/`) |
| **Prompts** | One-shot compositions (WHEN/HOW to trigger) | Commands (`.claude/commands/`) |
| **Foundation** | Always-loaded context (CLAUDE.md, docs) | AGENTS.md, CLAUDE.md |

The key difference: Pi skills can invoke `cast` and `debate` tools that spin up models from Anthropic, OpenAI, Google, and others as independent agents with their own personas, tools, and timeouts.

## How Multi-Model Review Works in Pi

### Single Reviewer (quick check)

```
1. Call models(role="reviewer") - get available models ranked for review tasks
2. Pick a model from a different provider than the one running the session
3. Cast it with a domain-specific persona and the artifact to review
4. Read the output, incorporate findings
```

This is roughly equivalent to Arsenal's `multi-model-review` skill (Claude + Codex), but the model selection is dynamic - Pi queries available models at runtime rather than hardcoding "use Codex."

### Adversarial Debate (stress test)

For high-stakes artifacts, Pi runs a **round-table debate**:

```
1. Call models(role="reviewer") - pick 2-3 models from different providers
2. Create a debate with:
   - Each agent gets a skeptical reviewer persona tailored to the domain
   - Agents can see each other's findings (builds on prior rounds)
   - Max 3 rounds, with a convergence keyword ("LGTM")
   - Timeout per round (prevents hung agents from blocking)
3. Read round files to assess quality
4. Synthesize into consensus / divergence / blockers
```

The multi-round structure is the key upgrade over single-pass review. In round 1, each model independently identifies issues. In round 2, they respond to each other's findings - confirming, refuting, or building on them. By round 3, what remains is either genuine consensus or genuine disagreement (both are valuable signal).

### Iterative Design Review (shaping work)

For artifacts that aren't ready for adversarial review yet, Pi uses a three-mode lifecycle:

| Mode | When | What happens |
|------|------|-------------|
| **Explore** | Idea is rough | Creative sparring - what's the biggest version? What's the MVP? What's the kill criterion? |
| **Converge** | Has shape, not yet tight | Free-form shaping toward a clear objective and acceptance criteria |
| **Refine** | Ready for structured review | Multi-model review cycles with synthesis after each round |

This prevents the common failure mode of running rigorous review on half-baked ideas (which just produces noise).

## What We've Learned

### Different providers have correlated blind spots

Models from the same provider tend to agree on the same things AND miss the same things. Anthropic models are generally strong on security reasoning; OpenAI models tend to catch performance concerns; Google models sometimes flag completeness gaps the others miss. Running two Claude instances is less valuable than running Claude + a model from another provider.

### Non-convergence is signal, not failure

If reviewers can't agree after 3 rounds, the artifact has genuine ambiguity that more review won't resolve. This is valuable information - it means a human needs to make a judgment call. We surface divergences explicitly rather than forcing artificial consensus.

### Stability matters more than iteration count

A design that's converging (findings getting smaller each cycle) after 2 rounds is healthier than one that's oscillating (different major issues each round) after 5. Oscillation usually means the scope is too broad and should be split.

### Match effort to risk

We calibrate review depth to estimated effort (LOE):
- **LOE 1** (trivial): skip or glance, no multi-model
- **LOE 2** (a few hours): single-model quick review
- **LOE 3+** (days/weeks): full multi-model iterative review

Arsenal's instinct here is right - the `multi-model-review` skill says "don't review typo fixes." We've made the same mistake and corrected for it.

### Concrete scenarios or it didn't happen

The single most impactful rule across all our review workflows: every finding must include a concrete failure scenario. "This could be a problem" gets filtered out. "If two users submit simultaneously and the lock isn't held, rows X and Y diverge" gets acted on.

## Arsenal vs Pi - Honest Comparison

| Aspect | Arsenal | Pi |
|--------|---------|-----|
| **Runtime** | Claude Code native | Pi agent harness (wraps Claude, adds forge tools) |
| **Multi-model** | Manual orchestration (spawn Codex via CLI) | Built-in `cast` and `debate` primitives |
| **Skill distribution** | Git submodule + symlinks + install.sh | Library catalog (`/library use <name>`) |
| **Agent execution** | Background Claude instances via `claude --dangerously-skip-permissions` | Ephemeral agents via `cast` (model, persona, tools, timeout) |
| **Debate** | Not built-in (could be built as a skill) | First-class `debate` tool (round-table or adversarial, convergence detection) |
| **Model selection** | Hardcoded (Claude + Codex) | Dynamic (`models(role=X)` queries available models at runtime) |
| **Enforcement** | Bootstrap tokens, manager-review gate | Convention-based (CLAUDE.md, skills loaded on demand) |
| **Maturity** | Battle-tested on a production product | Battle-tested on infrastructure + dispatch system |

Neither is strictly better. Arsenal's strength is enforcement discipline (bootstrap tokens, mandatory manager-review). Pi's strength is multi-model orchestration as a first-class primitive. The `multi-model-review` skill in this repo bridges them by bringing multi-model review patterns into Arsenal's Claude Code-native world.

## Want to Go Deeper?

If any of these topics would be useful as a full tearsheet, let us know:

- **Adversarial review methodology** - detailed playbook for stress-testing designs with skeptical multi-model panels
- **Iterative design convergence** - the explore/converge/refine lifecycle with real examples
- **Background agent dispatch** - fire-and-forget agent jobs with git worktree isolation, auto-commit, and PR creation
- **Skill portability** - how to write skills that work across repos and agent harnesses
- **Agent sandboxing** - macOS sandbox-exec for safe local agent execution (deny-first, per-project overrides)

Reach out to [Gilman](https://github.com/callsen) or open an issue on this repo.
